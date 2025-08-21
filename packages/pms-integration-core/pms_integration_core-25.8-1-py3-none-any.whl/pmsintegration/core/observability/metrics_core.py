from prometheus_client import Counter, Histogram

_get_sf_msg_counter = Counter(
    name="events_messages",
    namespace="salesforce",
    documentation="Total Salesforce events processed",
    labelnames=["subscription", "event_type"],
)

_get_sf_processing_latency = Histogram(
    name="event_processing_latency",
    namespace="salesforce",
    documentation="Time taken to process salesforce events",
    labelnames=["subscription"],
    buckets=[0.1, 0.5, 1, 2, 5, 10]
)


def increment_sf_listener_event_counter(subscription_key: str, event_type: str, count: int = 1) -> None:
    """Increment the Salesforce Platform Event counter with labels.

   Args:
       subscription_key (str): The event subscription identifier (topic name).
       event_type (str): The type of event (e.g., received, processed, failed, duplicates).
       count (int, optional): The number of events to increment. Defaults to 1.
   """
    _get_sf_msg_counter.labels(subscription=subscription_key, event_type=f"events_{event_type}").inc(count)


def increment_sf_process_event_counter(subscription_key: str, event_type: str, count: int = 1) -> None:
    """Increment the Salesforce Platform Event counter with labels.

   Args:
       subscription_key (str): The event subscription identifier (topic name).
       event_type (str): The type of event (e.g., received, processed, failed, duplicates).
       count (int, optional): The number of events to increment. Defaults to 1.
   """
    _get_sf_msg_counter.labels(subscription=subscription_key, event_type=f"events_{event_type}").inc(count)


def track_sf_event_latency_histogram(subscription_key):
    """Add Histogram to your Salesforce Platform Event with labels

    Args:
       subscription_key (str): The event subscription identifier (topic name).
    """
    return _get_sf_processing_latency.labels(subscription=subscription_key)
