import os
from typing import Any, Literal, Optional
from warnings import warn

from oauthlib.oauth2 import OAuth2Error
from requests.adapters import HTTPAdapter
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    JSONDecodeError,
    RequestException,
    Timeout,
    TooManyRedirects,
)
from requests.models import Response
from requests_oauthlib import OAuth2Session
from urllib3.util.retry import Retry

DEFAULT_TIMEOUT = 10.0


def get_timeout() -> float:
    try:
        timeout = float(os.environ.get("APH_REQUESTS_TIMEOUT", DEFAULT_TIMEOUT))
    except ValueError:
        timeout = DEFAULT_TIMEOUT
        warn(
            "APH_REQUESTS_TIMEOUT has been set to an invalid, non-numeric value. We will "
            f"use the default value of {DEFAULT_TIMEOUT} instead."
        )
    return timeout


def request_timeout_is_set() -> bool:
    # Don't just check the key as the key could exist but the value set to None
    return os.environ.get("APH_REQUESTS_TIMEOUT", None) is not None


def override_request_timeout(seconds: float):
    os.environ["APH_REQUESTS_TIMEOUT"] = str(seconds)


def unset_request_timeout():
    del os.environ["APH_REQUESTS_TIMEOUT"]


class RequestError(Exception):
    def __init__(self, message: str = "", status_code: int = None):
        self.status_code = status_code
        self.message = message


def _error_message(msg: str, response: Optional[Response] = None) -> str:
    # It's important to explicitly check response is not None as a Response object with
    # non-ok status also resolves to boolean False.
    if response is not None and hasattr(response, "text"):
        try:
            data = response.json()
            if data and "error" in data:
                error_text = data["error"]
            else:
                error_text = response.text
        except JSONDecodeError:
            error_text = response.text

        return msg + f"\nError details: {error_text}"
    return msg


def exception_handled_request(
    session: OAuth2Session,
    uri: str,
    method: Literal["post", "get", "delete"],
    payload: Optional[Any] = None,
    json: Optional[Any] = None,
) -> Response:

    # ToDo: Reconsider the configuration
    retries = Retry(
        total=10,
        backoff_factor=0.2,
        backoff_max=2,
        status_forcelist=[425, 500, 502, 503, 504],
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.mount("http://", HTTPAdapter(max_retries=retries))

    response = None
    try:
        if method == "post":
            response = session.post(uri, data=payload, json=json, timeout=get_timeout())
        elif method == "delete":
            response = session.delete(uri, data=payload, timeout=get_timeout())
        elif method == "get":
            response = session.get(uri, params=payload, timeout=get_timeout())
        else:
            raise NotImplementedError("Only POST, GET and DELETE requests are supported.")
    except (
        OAuth2Error,
        HTTPError,
        ConnectionError,
        Timeout,
        TooManyRedirects,
        RequestException,
    ) as e:
        raise RequestError(_error_message(f"{type(e).__name__} occurred: {e}."))

    try:
        response.raise_for_status()
    except HTTPError as e:
        raise RequestError(
            _error_message(f"HTTP error occurred: {e}.", response),
            status_code=response.status_code,
        )

    return response


__all__ = [
    "RequestError",
    "exception_handled_request",
]
