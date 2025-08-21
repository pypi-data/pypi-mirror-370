import atexit
import logging
import time
from concurrent.futures import (
    Future,
    ThreadPoolExecutor,
)

from pmsintegration.core.addepar.connector import response_handler
from pmsintegration.core.app import AppContext
from pmsintegration.core.observability import telemetry_service, metrics_core
from pmsintegration.core.salesforce.events import SalesforceEventProcessor
from pmsintegration.core.salesforce.pubsub.types import SfEvent
from pmsintegration.core.salesforce.sf_utils import (
    expand_and_validate_listener_names,
    on_task_complete_logger,
    SalesforceListenerConfig,
)
from pmsintegration.platform.concurrent_utils import halt_requested, wait_for_futures

_log = logging.getLogger(__name__)


class DBEventPoller:
    def __init__(self, app_ctx: AppContext, config: SalesforceListenerConfig):
        self.app_ctx = app_ctx
        self.config = config
        self.processor = SalesforceEventProcessor.create(config.name)

    def poll(self):
        event_store = self.app_ctx.event_store
        subscription_key = self.config.name

        if self.config.disable:
            _log.info(f"Configuration '{subscription_key}' is disabled. Will not poll new events")
            return

        gen = event_store.poll_for_processing(subscription_key)
        try:
            events = gen.send(None)  # Start the generator
            while True:
                start_poll_time = time.monotonic()
                should_stop = self.process_events(events)
                metrics_core.track_sf_event_latency_histogram(subscription_key).observe(
                    time.monotonic() - start_poll_time)
                if should_stop or halt_requested():
                    wait_in_seconds = -1  # Stop signal
                else:
                    wait_in_seconds = None  # let's not wait and ask for more events
                events = gen.send(wait_in_seconds)  # Send value and get next events
        except StopIteration:
            ...

    def process_events(self, events: list[SfEvent]) -> bool | None:
        _log.info(f"({self.config.name}): {len(events)} new event(s) received")
        try:
            _log.info("Returning process_events object to update in SalesForce")
            return self.processor.process(events)
        except Exception as e:
            http_error_code = response_handler.http_error_code or None  # noqa
            if response_handler.http_error_text is None:  # noqa
                response_handler.set_http_error_text(error_string=f"{http_error_code}:SF: {e}")

            _log.error(f"Exception - Nothing to send to SalesForce - {e}")
            metrics_core.increment_sf_process_event_counter(self.config.name, "processing_failed")


def run(app_ctx: AppContext, names: set[str]):
    env = app_ctx.env
    telemetry_service.initialize(env)
    names = expand_and_validate_listener_names(env, names)
    listener_configs = [SalesforceListenerConfig.create(env, name) for name in names]
    if len(listener_configs) > 1:
        pool = ThreadPoolExecutor()
        atexit.register(pool.shutdown)
        tasks: set[Future] = {pool.submit(DBEventPoller(app_ctx, c).poll) for c in listener_configs}
        wait_for_futures(tasks, on_task_complete_logger)
        pool.shutdown()
    else:
        DBEventPoller(app_ctx, listener_configs[0]).poll()

    _log.info("SF Event Processor stopped")
