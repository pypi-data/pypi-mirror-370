import json
import logging
import sys
from json import JSONDecodeError
from typing import Generator, Type, Any, Callable

from httpx import Response, HTTPError

from pmsintegration.core.addepar.connector.api_models import APIResponse, APIData, DataWrapper
from pmsintegration.core.core_models import LET, TypedLenientEntity

_log = logging.getLogger(__name__)

sys.modules[__name__].http_error_text = None
sys.modules[__name__].http_error_code = None


def _raise_for_status(response: Response):
    try:
        response.raise_for_status()
    except HTTPError:
        body = response.text
        _log.error(f"http error occurred. Response was:\nStatus Ccode: {response.status_code}\nBody: {body}")
        raise


def set_http_error_text(error_string: object) -> None:
    sys.modules[__name__].http_error_text = error_string if error_string else None
    # Suffix: error from Addepar


def set_http_error_code(error_code: object) -> None:
    sys.modules[__name__].http_error_code = error_code if error_code else None


def make_no_data_json_response_model(response: Response, _rt, data_as_list: bool = False):
    """Process API response into typed model."""
    raw_data = _handle_response_data(response)
    data = _process_response_data(raw_data, _rt, data_as_list)
    return _build_api_response(response, data, raw_data)


def _handle_response_data(response: Response) -> dict:
    """Extract and validate response data with error handling."""
    try:
        response.raise_for_status()
        data = response.json()
        set_http_error_text(error_string=None)
        _log.info(f"Response:\n{json.dumps(data, indent=2)}\n==============")
        return data
    except HTTPError as e:
        error_str = str(response.text)
        set_http_error_text(error_string=f"ADPR: {error_str}")
        _log.error(f"HTTP Error {e}\nResponse: {error_str}")
        raise
    except JSONDecodeError as e:
        if _is_empty_response_error(e):
            return {"data": []}
        raise
    except Exception as e:
        _log.error(f"Unexpected error: {e}\nRaw Response: {response.text}")
        raise


def _is_empty_response_error(e: JSONDecodeError) -> bool:
    """Check if decode error is for empty response."""
    return (hasattr(e, 'msg') and
            isinstance(e.msg, str) and
            e.msg.strip().lower() == "expecting value")


def _process_response_data(raw_data: dict, _rt, data_as_list: bool) -> list:
    """Convert raw data to properly typed model instances."""
    is_typed = _check_type_compatibility(_rt)
    converter = _create_data_converter(is_typed)

    if isinstance(raw_data, list):
        return [converter(item) for item in raw_data]

    result = converter(raw_data)
    return [result] if data_as_list else result


def _check_type_compatibility(_rt) -> bool:
    """Safely verify type compatibility."""
    if _rt is None or not isinstance(_rt, type):
        return False
    try:
        return issubclass(_rt, TypedLenientEntity)
    except TypeError:
        _log.warning(f"Invalid type provided: {_rt}")
        return False


def _create_data_converter(is_typed: bool):
    """Create converter function with frozen type flag."""

    def convert(raw: dict) -> APIData:
        return APIData(
            relationships={
                r: DataWrapper(
                    data=[APIData(**d) for d in w.get("data")]
                    if isinstance(w.get("data"), list)
                    else APIData(**w.get("data") or {})
                )
                for r, w in raw.get("relationships", {}).items()
            },
            id=raw.get("id"),
            type=raw.get("type"),
        )

    return convert


def _build_api_response(response: Response, data, raw_data: dict) -> APIResponse:
    """Construct final response without data duplication."""
    return APIResponse(
        raw=response,
        data=data,
        **{k: v for k, v in raw_data.items() if k != 'data'}
    )


def make_json_response_model(response: Response, _rt, data_as_list: bool = False):
    try:
        response.raise_for_status()
        raw_data = response.json()
        set_http_error_text(error_string=None)
        _log.info(f"Response from Addepar:\n{json.dumps(raw_data, indent=2)}\n======================")
    except HTTPError as e:
        _log.error(f"HTTP Error occurred: {e}")
        raw_data = response.text
        error_str = str(raw_data)
        error_code = str(response.status_code)
        set_http_error_text(error_string=error_code + " :ADPR: " + error_str)
        set_http_error_code(error_code=error_code)
        _log.info(f"HTTP Error Response: {raw_data}")
        raise
    except JSONDecodeError as e:
        if hasattr(e, 'msg') and isinstance(e.msg, str) and e.msg.strip().lower() == "expecting value":
            raw_data: dict[str, Any] = {"data": []}  # Not removing the check since it was already here
        else:
            raise
    except Exception as e:
        raw_data = response.text
        _log.error(f"Unknown exception: {e}\nRaw Response from Addepar: {raw_data}")

    data_or_list = raw_data.pop("data")

    def _new_rt(_raw: dict[str, Any], _is_typed: bool):
        _d = APIData(
            attributes=_rt(**_raw.get("attributes", {})),
            relationships={
                r: DataWrapper(
                    data=[APIData(**d) for d in w.get("data")] if isinstance(w.get("data"), list) else APIData(
                        **w.get("data") or {}))
                for r, w in _raw.get("relationships", {}).items()
            },
            id=_raw.get("id"),
            type=_raw.get("type"),
        )
        if _is_typed:
            _d.attributes.id = _d.id
        _d.attributes.type = _d.type
        return _d

    is_typed = issubclass(_rt, TypedLenientEntity)
    if isinstance(data_or_list, list):
        data = [_new_rt(e, is_typed) for e in data_or_list]
    else:
        data = _new_rt(data_or_list, is_typed)
        if data_as_list:
            # Addepar API does not return an array when the request payload is a list
            # so as a workaround, making it a list explicitly.
            data = [data]

    return APIResponse(raw=response, data=data, **raw_data)


def unwrap_json_payload(response: Response, _rt):
    return make_json_response_model(response, _rt).data.unwrap()


def paginate_and_unwrap_json_payload(
        response: Response,
        _rt: Type[LET],
        httpx,
        transform: Callable[[LET], Any] | None = None
) -> Generator[LET, str, None]:
    if transform is None:
        transform = unwrap_payload

    while True:
        api_response = make_json_response_model(response, _rt)
        for d in api_response.data:
            should_stop = yield transform(d)
            if should_stop:
                raise StopIteration("stopped explicitly")
        link_next = api_response.links.get("next")
        if link_next:
            response = httpx.get(link_next)
        else:
            break


def unwrap_payload(item):
    return item.unwrap()
