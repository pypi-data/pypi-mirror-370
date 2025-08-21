import logging
from concurrent.futures import Future, CancelledError

from pydantic import BaseModel


from pmsintegration.platform.config import ConfigEnvironment
from pmsintegration.platform.errors import IllegalArgumentException

_log = logging.getLogger(__name__)


class SalesforceListenerConfig(BaseModel):
    name: str
    topic_name: str
    app_name: str
    processor: str | None
    connector_name: str = "salesforce_pubsub_api"
    disable: bool = False

    @classmethod
    def create(cls, env: ConfigEnvironment, name: str) -> 'SalesforceListenerConfig':
        configs = env.find_matched(f"listeners.salesforce.{name}")
        return SalesforceListenerConfig(name=name, **configs)

    @classmethod
    def find_all(cls, env: ConfigEnvironment) -> set[str]:
        return set(env.find_matched("listeners.salesforce.").keys())


def expand_and_validate_listener_names(env: ConfigEnvironment, names: set[str]) -> set[str]:
    """Expands and validates a list of Salesforce listener names.

    If the input list contains only "ALL", it is expanded to include all
    available listener names. Otherwise, it checks if all provided names
    are valid and raises an exception if any unknown names are found.

    Args:
        env: The configuration environment.
        names: A list of Salesforce listener names.  May contain "ALL".

    Returns:
        A list of valid Salesforce listener names.

    Raises:
        IllegalArgumentException: If any unknown listener names are provided.
    """

    available_names = SalesforceListenerConfig.find_all(env)

    if "ALL" in names and len(names) == 1:
        # Only if names = {"ALL" }
        return available_names

    names = set(names)
    unknown_names = names - available_names
    if unknown_names:
        raise IllegalArgumentException(f"Unknown listener names: {unknown_names}")

    return names


def on_task_complete_logger(completed: set[Future], pending: set[Future]):
    """Callback function to log the completion of futures.

    Logs the result (or exception) of each completed future and the number of pending futures.
    """
    for future in completed:
        try:
            result = future.result()
            _log.info(f"Listener task completed successfully with result: {result}")
        except TimeoutError as e:
            _log.error(f"Listener task timed out: {e}", exc_info=True)
        except CancelledError as e:
            _log.error(f"Listener task was cancelled: {e}", exc_info=True)
        except Exception as e:
            _log.error(f"Listener task raised an unexpected exception: {e}", exc_info=True)

    _log.info(f"Number of pending tasks: {len(pending)}")
