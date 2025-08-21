import atexit
import logging
from concurrent.futures import (
    Future,
    ThreadPoolExecutor,
)

from pmsintegration.core.app import AppContext
from pmsintegration.core.observability import telemetry_service, metrics_core
from pmsintegration.core.salesforce.connector.pubsub_api_connector import SalesforcePubSubConnector
from pmsintegration.core.salesforce.events import SalesforceEventProcessor, ProcessorConfig
from pmsintegration.core.salesforce.pubsub.types import SfEvent
from pmsintegration.core.salesforce.sf_utils import (
    expand_and_validate_listener_names,
    on_task_complete_logger,
    SalesforceListenerConfig,
)
from pmsintegration.core.salesforce.store import SubscribeParams
from pmsintegration.platform.concurrent_utils import wait_for_futures
from pmsintegration.platform.retries import (
    retry,
    after_log,
    wait_exponential,
    before_sleep_log,
    retry_if_exception,
    stop_when_halt_requested,
    retryable_grpc_exception,
    RetryableGrpcException,
)

_log = logging.getLogger(__name__)


class SalesforceEventDBAppender(SalesforceEventProcessor):
    def __init__(self, config: ProcessorConfig, app_context: AppContext):
        super().__init__(config, app_context)
        self.replay_store = app_context.topic_subscription_store
        self.event_store = app_context.event_store

    def process(self, events: list[SfEvent]) -> bool | None:
        if len(events) == 0:
            return None
        subscription_key = self.config.name

        self.event_store.append(subscription_key, events)

        # Update the last replay id
        try:
            self.replay_store.update_replay_id(
                subscription_key,
                events[-1].replay_id
            )
        except Exception as e:
            _log.warning(f"Error updating last replay_id: {e}")

    def subscribe_parameters(self) -> SubscribeParams:
        return self.replay_store.get_subscription_param(self.config.name)


class SalesforceEventListener:
    def __init__(self, config: SalesforceListenerConfig, connector: SalesforcePubSubConnector):
        self.connector = connector
        self.config = config
        self.processor = SalesforceEventProcessor.create(config.name, impl=config.processor)

    @retry(
        reraise=True,
        stop=stop_when_halt_requested(),
        wait=wait_exponential(multiplier=1, min=5, max=30),
        retry=retry_if_exception(retryable_grpc_exception),
        after=after_log(_log, log_level=logging.ERROR),
        before_sleep=before_sleep_log(_log, logging.WARNING)
    )
    def listen(self):
        c = self.config
        retry_grpc_keywords = [
            'unavailable',
            'deadline_exceeded',
            'rst_stream',
            'resource_exhausted',
            'aborted']

        if c.disable or c.topic_name in ("None", None):
            _log.warning(
                f"Event Listener '{c.name}' is disabled explicitly (or no topic name) "
                f"in the configuration. Not starting..."
            )
            return

        try:
            # Attempt to subscribe to the topic
            subscription = self.connector.subscribe(
                c.topic_name,
                self.process_event,
                subscription_params_provider=self.processor.subscribe_parameters,
            )
            _log.info(f"Subscribed to topic: ==={c.topic_name}===")

            subscription.run_forever()
        except Exception as e:
            _log.error(f"Error occurred during subscription to topic ==={c.topic_name}===")
            metrics_core.increment_sf_listener_event_counter(c.topic_name, "subscription_failed")
            if 'grpc' in str(e).lower():
                _log.error(f"GRPC Error: {e}")
                if any(keyword in str(e).lower() for keyword in retry_grpc_keywords):
                    # Reraise to trigger retry, else just log
                    raise RetryableGrpcException("Treating as a retryable GRPC error...retrying") from e
                elif 'permission_denied' in str(e).lower():
                    _log.error("GRPC PERMISSION_DENIED Exception")
                else:
                    _log.error(f"Unhandled GRPC exception occurred: {e}")
            else:
                _log.error(f"Unknown, non-retryable exception occurred: {e}")

    def process_event(self, events: list[SfEvent]) -> bool:
        _log.info(f"({self.config.name}): New {len(events)} event(s) received")
        should_stop = self.processor.process(events)
        return should_stop


def run(app_ctx: AppContext, names: set[str]):
    env = app_ctx.env
    telemetry_service.initialize(env)
    names = expand_and_validate_listener_names(env, names)
    connector_name = "salesforce_pubsub_api"
    listener_configs = [SalesforceListenerConfig.create(env, name) for name in names]
    with SalesforcePubSubConnector.create(env, connector_name) as connector:
        if (max_workers := len(listener_configs)) > 1:
            pool = ThreadPoolExecutor(max_workers=max_workers)
            atexit.register(pool.shutdown)
            tasks: set[Future] = {pool.submit(SalesforceEventListener(c, connector).listen) for c in listener_configs}
            wait_for_futures(tasks, on_task_complete_logger)
            pool.shutdown()  # Let's shut it down explicitly
        else:
            SalesforceEventListener(listener_configs[0], connector).listen()

    _log.info("Listener stopped")
