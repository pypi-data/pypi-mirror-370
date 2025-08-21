import json
from contextlib import contextmanager
from typing import Any, Dict, Optional, Type, Union

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from truefoundry.common.exceptions import BadRequestException, HttpRequestException


# TODO (chiragjn): Rename this to json_response_handling
def request_handling(response: Response) -> Optional[Any]:
    status_code = response.status_code
    if 200 <= status_code <= 299:
        if response.content == b"":
            # TODO (chiragjn): Do we really need this empty check?
            return None
        try:
            return response.json()
        except json.JSONDecodeError as je:
            raise ValueError(
                f"Failed to parse response as json. Response: {response.text}",
            ) from je

    try:
        message = str(response.json()["message"])
    except Exception:
        message = response.text

    if 400 <= status_code <= 499:
        raise BadRequestException(message=message, status_code=response.status_code)
    if 500 <= status_code <= 599:
        raise HttpRequestException(message=message, status_code=response.status_code)

    raise HttpRequestException("Unknown error occurred", status_code=status_code)


def urllib3_retry(
    retries: int = 2,
    backoff_factor: float = 0.3,
    status_forcelist=(408, 429, 500, 502, 503, 504, 524),
    method_whitelist=frozenset({"GET", "POST"}),
    raise_on_status: bool = False,
):
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        status=retries,
        backoff_factor=backoff_factor,
        allowed_methods=method_whitelist,
        status_forcelist=status_forcelist,
        respect_retry_after_header=True,
        raise_on_status=raise_on_status,
    )
    return retry


def requests_retry_session(
    retries: int = 2,
    backoff_factor: float = 0.3,
    status_forcelist=(408, 429, 417, 500, 502, 503, 504, 524),
    method_whitelist=frozenset({"GET", "POST"}),
    raise_on_status: bool = False,
    session: Optional[requests.Session] = None,
) -> requests.Session:
    """
    Returns a `requests` session with retry capabilities for certain HTTP status codes.

    Args:
        retries (int): The number of retries for HTTP requests.
        backoff_factor (float): The backoff factor for exponential backoff during retries.
        status_forcelist (tuple): A tuple of HTTP status codes that should trigger a retry.
        method_whitelist (frozenset): The set of HTTP methods that should be retried.
        session (requests.Session, optional): An optional existing requests session to use.

    Returns:
        requests.Session: A session with retry capabilities.
    """
    # Implementation taken from https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    session = session or requests.Session()
    retry = urllib3_retry(
        retries=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        method_whitelist=method_whitelist,
        raise_on_status=raise_on_status,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def http_request(
    *,
    method: str,
    url: str,
    token: Optional[str] = None,
    timeout=None,
    headers: Optional[Dict[str, str]] = None,
    session: Optional[requests.Session] = None,
    exception_class: Type[HttpRequestException] = HttpRequestException,
    **kwargs,
) -> requests.Response:
    session = session or requests.Session()
    headers = headers or {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = session.request(
            method=method, url=url, headers=headers, timeout=timeout, **kwargs
        )
        return response
    except requests.exceptions.ConnectionError as ce:
        raise exception_class("Failed to connect to TrueFoundry") from ce
    except requests.exceptions.Timeout as te:
        raise exception_class(f"Request to {url} timed out") from te
    except Exception as e:
        raise exception_class(f"Request to {url} failed with error {str(e)}") from e


@contextmanager
def cloud_storage_http_request(
    *,
    method: str,
    url: str,
    session: Optional[requests.Session] = None,
    timeout: Optional[Union[int, float]] = None,
    exception_class: Type[HttpRequestException] = HttpRequestException,
    **kwargs,
):
    """
    Performs an HTTP PUT/GET request using Python's `requests` module with automatic retry.
    """
    # Note: This does not support auth and is only meant to be used for pre-signed URLs.
    session = session or requests_retry_session(retries=5, backoff_factor=0.5)
    headers = kwargs.get("headers", {}) or {}
    if "blob.core.windows.net" in url:
        headers.update({"x-ms-blob-type": "BlockBlob"})
    if method.lower() not in ("put", "get"):
        raise ValueError(f"Illegal http method: {method}")
    yield http_request(
        method=method,
        url=url,
        session=session,
        timeout=timeout,
        headers=headers,
        exception_class=exception_class,
        **kwargs,
    )


# TODO: Try and eliminate this
def augmented_raise_for_status(
    response, exception_class: Type[HttpRequestException] = HttpRequestException
):
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as he:
        raise exception_class(
            message=f"Request failed with status code {he.response.status_code}. Response: {he.response.text}",
            status_code=he.response.status_code,
        ) from he
