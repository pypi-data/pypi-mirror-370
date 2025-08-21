import functools
import re
import time
from typing import Optional

import httpx
import requests

from pmsintegration.core.observability.metrics_handler import track_event_latency, increment_event_counter

_SF_ENDPOINT_PATTERN = re.compile(
    r"/services/data/(v\d+(?:\.\d+)?)/sobjects/([A-Za-z_]+)/[a-zA-Z0-9]+"
)

_ADP_ENDPOINT_PATTERN = re.compile(
    r"/api/(v\d+(?:\.\d+)?)/([A-Za-z]+)"
)


class MetricsHook:
    def __init__(self, namespace: str):
        self.namespace = namespace

    def on_request(self, request: httpx.Request):
        request.extensions["start_time"] = time.time()

    def on_response(self, response: httpx.Response):
        method = response.request.method
        url = extract_addepar_object_path(response.request.url.__str__())
        status_code = str(response.status_code)
        start_time = response.request.extensions.get("start_time", time.time())
        url and record_metrics(start_time, self.namespace, method, url, status_code)

    def on_exception(self, request: httpx.Request, exception: Exception):
        method = request.method
        status_code = str(getattr(getattr(exception, "response", None), "status_code", 500))
        url = extract_addepar_object_path(request.url.__str__())
        start_time = request.extensions.get("start_time", time.time())
        url and record_metrics(start_time, self.namespace, method, url, status_code)


class SalesforceMetricsHook(requests.Session):
    def __init__(self, namespace: str = "salesforce"):
        super().__init__()
        self.namespace = namespace

    def request(self, method, url, **kwargs):
        start_time = time.time()
        status_code = "500"
        try:
            response = super().request(method, url, **kwargs)
            status_code = str(response.status_code)
            return response
        except requests.RequestException as e:
            if hasattr(e, "response") and e.response is not None:
                status_code = str(e.response.status_code)
            raise
        finally:
            url = extract_salesforce_object_path(url)
            url and record_metrics(start_time, self.namespace, method, url, status_code)


@functools.lru_cache()
def extract_salesforce_object_path(url: str) -> Optional[str]:
    """
    Extracts Salesforce endpoint path like 'v61.0/sobjects/Account' only if a Salesforce ID follows.
    Returns None if the pattern isn't matched.
    """
    match = _SF_ENDPOINT_PATTERN.search(url)
    if match:
        version, object_name = match.groups()
        return f"/{version}/sobjects/{object_name}"
    return None


@functools.lru_cache()
def extract_addepar_object_path(url: str) -> Optional[str]:
    """
    Extracts Addepar endpoint path like 'v1.0/entities'.
    Returns None if the pattern isn't matched.
    """
    match = _ADP_ENDPOINT_PATTERN.search(url)
    if match:
        version, entity_type = match.groups()
        return f"/{version}/{entity_type}"
    return None


def record_metrics(start_time, namespace, method, url, status_code):
    """
    Record metrics
    :param start_time: start_time sent for metric capture
    :param namespace: source: addepar/salesforce
    :param method: [GET, POST..etc]
    :param url: http-URL
    :param status_code: http status_code
    """
    latency = time.time() - start_time
    track_event_latency(namespace, method, url, status_code).observe(latency)
    increment_event_counter(namespace, method, url, status_code)
