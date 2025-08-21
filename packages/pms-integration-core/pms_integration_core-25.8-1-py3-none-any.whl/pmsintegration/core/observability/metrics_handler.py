from prometheus_client import Counter, Histogram

_get_event_msg_counter = Counter(
    name="events_messages",
    documentation="Total events processed",
    labelnames=["source", "method", "end_point", "status_code"],
)

_get_event_processing_latency = Histogram(
    name="event_processing_latency",
    documentation="Time taken to process events",
    labelnames=["source", "method", "end_point", "status_code"],
    buckets=[0.1, 0.5, 1, 2, 5, 10]
)


def increment_event_counter(source: str, method: str, end_point: str, status_code: str | int, count: int = 1) -> None:
    """Increment the API event counter with labels."""
    _get_event_msg_counter.labels(
        source=source,
        method=method,
        end_point=end_point,
        status_code=str(status_code)
    ).inc(count)


def track_event_latency(source: str, method: str, end_point: str, status_code: str | int):
    """Track latency for API calls."""
    return _get_event_processing_latency.labels(
        source=source,
        method=method,
        end_point=end_point,
        status_code=str(status_code)
    )
