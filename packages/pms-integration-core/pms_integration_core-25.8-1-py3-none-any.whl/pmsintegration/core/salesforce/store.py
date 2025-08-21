import json
import logging
import time
from typing import Tuple, Generator

from pydantic import BaseModel

from pmsintegration.core.addepar.connector import response_handler
from pmsintegration.core.observability import metrics_core
from pmsintegration.core.pmsdb.config import use_conn
from pmsintegration.core.salesforce.pubsub.types import SfEvent
from pmsintegration.platform.concurrent_utils import halt_requested

_log = logging.getLogger(__name__)


class SubscribeParams(BaseModel):
    __table__ = "sys_sf_topic_subscription"
    replay_type: str = "CUSTOM"
    replay_id: str


class EventProcessingError(Exception):
    def __init__(self, event_id: str, error: str):
        super().__init__(error)
        self.event_id: event_id


class EventProcessingRecoverableError(EventProcessingError):
    def __init__(self, event_id: str, error: str):
        super().__init__(event_id, error)


class EventBatchProcessingError(Exception):
    def __init__(self, errors: dict[str, EventProcessingError]):
        self.errors = errors


class SubscriptionStore:
    def __init__(self, pmdb):
        self.pmdb = pmdb

    def get_subscription_param(self, key: str) -> SubscribeParams:
        default = SubscribeParams(replay_type="EARLIEST", replay_id="")
        with use_conn(self.pmdb) as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT replay_id  "
                            f"FROM {SubscribeParams.__table__} "
                            f"WHERE last_updated_ts >= NOW() - INTERVAL '72 hours' "
                            f"AND subscription_key = %s", (key,))
                row = cur.fetchone()
                result = SubscribeParams(replay_id=row[0]) if row else default
        return result

    def get_latest_reply_id(self, key: str) -> SubscribeParams:
        with use_conn(self.pmdb) as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT replay_id  "
                            f"FROM {SubscribeParams.__table__} "
                            f"WHERE subscription_key = %s", (key,))
                row = cur.fetchone()
                result = SubscribeParams(replay_id=row[0])
            return result

    def update_replay_id(self, subscription_key: str, new_replay_id: str) -> None:
        with use_conn(self.pmdb) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE {SubscribeParams.__table__}
                    SET replay_id = %s, last_updated_ts = DEFAULT
                    WHERE subscription_key = %s
                    AND replay_id != %s
                    """,
                    (new_replay_id, subscription_key, new_replay_id)
                )
                if cur.rowcount == 0:
                    # If no rows were updated, insert a new row for the new subscription
                    cur.execute(
                        f"""
                        INSERT INTO {SubscribeParams.__table__} (subscription_key, replay_id)
                        VALUES (%s, %s)
                        """,
                        (subscription_key, new_replay_id)
                    )
                    _log.info(f"A new subscription key get created in the sf topic subscription: {subscription_key}")


class SfEventHelper:
    __tablename__ = "sys_sf_topic_event"

    @classmethod
    def map(cls, key: str, e: SfEvent) -> Tuple:
        return (
            e.event_id,
            key,
            e.get_created_date(),
            key[0:key.rfind("_")],  # Remove _create/_update suffix
            e.get_entity_id(),
            json.dumps(e.payload, indent=2),
            e.replay_id,
            e.schema_id,
        )

    @classmethod
    def polling_query(cls):
        return """
             WITH locked_rows AS (
                SELECT subscription_key, id, replay_id, schema_id, payload
                FROM pms_data.sys_sf_topic_event
                WHERE subscription_key = %s
                AND processed = FALSE
                AND processing = FALSE
                AND (processing_error IS NULL
                    OR processing_error = ''       -- pick up new events
                    OR (processing_error IS NOT NULL
                        AND processing_error NOT LIKE %s    -- omit SF failure retry
                        AND processing_error SIMILAR to %s  -- error codes to retry
                        AND processing_ts < NOW() - INTERVAL '10 minutes')
                    )
                ORDER BY created_date
                LIMIT 1     -- Limiting to avoid crash loops for failed batches
                FOR UPDATE SKIP LOCKED
            )
            UPDATE pms_data.sys_sf_topic_event AS t
            SET processing = TRUE, processing_ts = NOW()
            FROM locked_rows
            WHERE t.id = locked_rows.id and t.subscription_key = locked_rows.subscription_key
              RETURNING t.id, t.replay_id, t.schema_id, t.payload
            """.strip()

    @classmethod
    def update_processing_status_query(cls):
        return """
        UPDATE pms_data.sys_sf_topic_event AS t
        SET processed = %s,
            processing = FALSE,
            processing_error = %s
        WHERE 1 = 1
            AND subscription_key = %s
            AND id = %s
       """.strip()

    @classmethod
    def unmap(cls, rows: list[Tuple[...]]) -> list[SfEvent]:
        return [
            SfEvent(
                event_id=row[0],
                replay_id=row[1],
                schema_id=row[2],
                payload=json.loads(row[3]),
            )
            for row in rows
        ]


class EventStore:

    def __init__(self, pmdb):
        self.pmdb = pmdb
        self._insert_sql = f"""
               INSERT INTO {SfEventHelper.__tablename__}
                  (id, subscription_key, created_date, entity_type, entity_id, payload, replay_id, schema_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (subscription_key, id) DO NOTHING
               """.strip()
        self._load_sql = SfEventHelper.polling_query()

    def append(self, subscription_key: str, events: list[SfEvent]):
        mapped = [SfEventHelper.map(subscription_key, e) for e in events]
        with use_conn(self.pmdb) as conn:
            with conn.cursor() as cur:
                cur.executemany(self._insert_sql, mapped)
                appended = cur.rowcount
                total = len(events)
                metrics_core.increment_sf_listener_event_counter(subscription_key, "received_total", total)
                metrics_core.increment_sf_listener_event_counter(subscription_key, "received_appended", appended)
                dupes = total - appended
                msg = f"Consumed {total} events for subscription '{subscription_key}'"
                if dupes:
                    metrics_core.increment_sf_listener_event_counter(subscription_key, "received_duplicates", dupes)
                    msg += f"{appended} event(s) were appended, and {dupes} duplicate event(s) were discarded."
                _log.info(msg)

    def poll_for_processing(self, subscription_key: str) -> Generator[list[SfEvent], int | None, None]:
        _log.info(f"Start polling for new events: {subscription_key}")
        wait_interval = 0
        retryable_error_list = [408, 429, 500, 502, 503, 504]  # Common retryable HTTP error codes
        retry_regex = '|'.join(map(str, retryable_error_list))
        regex_str = f"({retry_regex})%"
        sf_exclude_regex = "%:SF:%"
        while not halt_requested():
            if wait_interval == -1:
                _log.info(f"Stopping event polling for subscription: {subscription_key}")
                break
            _log.info(f"WAIT_INTERVAL = {wait_interval}")
            if wait_interval:
                time.sleep(max(1, wait_interval))
            _log.info(f"Reading new batch of events: {subscription_key=}")
            with use_conn(self.pmdb) as conn:
                with conn.cursor() as cur:
                    sql = SfEventHelper.polling_query()
                    cur.execute(sql, (subscription_key, str(sf_exclude_regex), str(regex_str)))
                    events = SfEventHelper.unmap(cur.fetchall())
                    if not events:
                        _log.info("No new events arrived since last poll")
                        wait_interval = 10
                        continue

                    try:
                        wait_interval = yield events
                        http_error = str(response_handler.http_error_text) if response_handler.http_error_text else None
                        error_code = str(response_handler.http_error_code) if response_handler.http_error_code else None
                        arglist = [(
                            False if (
                                    error_code is not None
                                    and int(error_code) in retryable_error_list
                            ) else True,  # Marked as Processed
                            http_error if http_error else None,  # additional check to avoid 'None' string
                            subscription_key,
                            e.event_id,
                        ) for e in events]
                    except EventBatchProcessingError as e:
                        errors = e.errors
                        arglist = [(
                            not isinstance(ex := errors.get(e.event_id), EventProcessingRecoverableError),
                            str(ex.args[0]) if ex else None,
                            subscription_key,
                            e.event_id,
                        ) for e in events]
                    except Exception as ex:
                        msg = (
                            f"Unhandled exception occurred in the processor. Many events will be marked as processed;"
                            f" however, their actual status is unknown. This must be investigated via support."
                            f" For more information about the event, you can query the {SfEventHelper.__tablename__}"
                            f" table."
                            f" This can be a potential bug in the handler({subscription_key=})")
                        _log.warning(msg, ex)
                        arglist = [(
                            True,  # This is set to True; as if an unknown exception occurred
                            str(ex.args[0]) if ex.args else None,
                            subscription_key,
                            e.event_id,
                        ) for e in events]
                    # Mark processed
                    _log.info(f"Updating the processing status: {arglist}")
                    cur.executemany(
                        SfEventHelper.update_processing_status_query(),
                        arglist
                    )
                    # clear the global variables
                    response_handler.set_http_error_text(error_string=None)
                    response_handler.set_http_error_code(error_code=None)

                    failed_msg_cnt = sum(1 for e in arglist if e[1] is not None)
                    if failed_msg_cnt:
                        metrics_core.increment_sf_process_event_counter(
                            subscription_key,
                            "processing_failed",
                            failed_msg_cnt
                        )
                    else:
                        metrics_core.increment_sf_process_event_counter(
                            subscription_key,
                            "processed",
                            len(arglist) - failed_msg_cnt
                        )
