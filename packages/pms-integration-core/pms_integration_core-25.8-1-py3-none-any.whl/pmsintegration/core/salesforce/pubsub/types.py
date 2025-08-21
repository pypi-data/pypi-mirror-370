import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import cached_property
from typing import Any, Tuple

import pmsintegration.core.salesforce.pubsub.gen.pubsub_api_pb2 as pb2
from pmsintegration.platform.utils import trim_dict_keys

CommitReplayRequest: Any = pb2.CommitReplayRequest  # noqa
CommitReplayResponse: Any = pb2.CommitReplayResponse  # noqa
ConsumerEvent: Any = pb2.ConsumerEvent  # noqa
Error: Any = pb2.Error  # noqa
ErrorCode: Any = pb2.ErrorCode  # noqa
EventHeader: Any = pb2.EventHeader  # noqa
FetchRequest: Any = pb2.FetchRequest  # noqa
FetchResponse: Any = pb2.FetchResponse  # noqa
ManagedFetchRequest: Any = pb2.ManagedFetchRequest  # noqa
ManagedFetchResponse: Any = pb2.ManagedFetchResponse  # noqa
ProducerEvent: Any = pb2.ProducerEvent  # noqa
PublishRequest: Any = pb2.PublishRequest  # noqa
PublishResponse: Any = pb2.PublishResponse  # noqa
PublishResult: Any = pb2.PublishResult  # noqa
ReplayPreset: Any = pb2.ReplayPreset  # noqa
SchemaInfo: Any = pb2.SchemaInfo  # noqa
SchemaRequest: Any = pb2.SchemaRequest  # noqa
TopicInfo: Any = pb2.TopicInfo  # noqa
TopicRequest: Any = pb2.TopicRequest  # noqa


@dataclass
class SfEvent:
    event_id: str
    replay_id: str
    schema_id: str
    payload: dict[str, Any]
    headers: list[Tuple[str, Any]] | None = None

    def get_created_date(self):
        millis = self.payload.get("CreatedDate", time.time() * 1000)
        return datetime.fromtimestamp(millis / 1000.0, timezone.utc)

    @cached_property
    def data(self) -> dict[str, Any]:
        return trim_dict_keys(json.loads(self.payload.get("Data__c", "{}")))

    def get_entity_id(self):
        return self.data.get("recordId") or self.payload.get("recordId__c") or ""

    @classmethod
    def create(cls, e: ConsumerEvent, payload: dict[str, Any]) -> 'SfEvent':
        return cls(
            event_id=e.event.id,
            replay_id=e.replay_id.hex(),
            schema_id=e.event.schema_id,
            payload=payload,
        )
