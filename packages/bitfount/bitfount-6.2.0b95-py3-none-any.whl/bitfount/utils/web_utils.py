"""Utility functions for web interactions."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Collection, MutableMapping
from functools import wraps
import inspect
import logging
import re
import time
from typing import Any, Final, Optional, Protocol, Union, cast, overload

import httpx
from httpx._client import USE_CLIENT_DEFAULT, UseClientDefault
from httpx._types import (
    AuthTypes,
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    TimeoutTypes,
    URLTypes,
)
import requests
from requests import Response
from typing_extensions import ParamSpec

from bitfount import config
from bitfount.utils.retry_utils import DEFAULT_BACKOFF_FACTOR, compute_backoff

_logger = logging.getLogger(__name__)

_DEFAULT_RETRY_STATUS_CODES: Final[frozenset[int]] = frozenset(
    {
        # Not generally something that should be retried, but we often find there's a
        # delay between resource creation and GET returning correctly and so we want to
        # generally give it another try
        404,
        # General good retry codes; from https://stackoverflow.com/a/74627395
        # Client issues
        408,  # Request Timeout
        425,  # Too Early
        429,  # Too Many Requests
        # Server issues
        500,  # Internal Server Error
        502,  # Bad Gateway
        503,  # Service Unavailable
        504,  # Gateway Timeout
    }
)
_DEFAULT_TIMEOUT: Final = 20.0
_DEFAULT_MAX_RETRIES: Final[int] = config.settings.web_max_retries

_P = ParamSpec("_P")
_SYNC_F = Callable[_P, Response]
_ASYNC_F = Callable[_P, Awaitable[httpx.Response]]
_F = Union[_SYNC_F[_P], _ASYNC_F[_P]]


class _RETURN_SYNC_F(Protocol[_P]):
    def __call__(
        self,
        *args: _P.args,
        do_not_retry_codes: Optional[Collection[int]] = None,
        **kwargs: _P.kwargs,
    ) -> Response: ...


class _RETURN_ASYNC_F(Protocol[_P]):
    def __call__(
        self,
        *args: _P.args,
        do_not_retry_codes: Optional[Collection[int]] = None,
        **kwargs: _P.kwargs,
    ) -> Awaitable[httpx.Response]: ...


class _DecoratorCreator(Protocol[_P]):
    @overload
    def __call__(self, req_func: _SYNC_F[_P]) -> _RETURN_SYNC_F[_P]: ...

    @overload
    def __call__(self, req_func: _ASYNC_F[_P]) -> _RETURN_ASYNC_F[_P]: ...

    def __call__(self, req_func: _F[_P]) -> _RETURN_F: ...


_RETURN_F = Union[_RETURN_SYNC_F[_P], _RETURN_ASYNC_F[_P]]


def obfuscate_security_token(text: str) -> str:
    """Obfuscate a security token in a string.

    Replaces the value of a security token in a string with asterisks.

    Args:
        text: The string to obfuscate.

    Returns:
        The obfuscated string.
    """
    pattern = re.compile(r"(Security-Token=)([^&]*)", re.IGNORECASE)
    return pattern.sub(r"\1**********", text)


@overload
def _auto_retry_request(
    original_req_func: _SYNC_F[_P],
    *,
    max_retries: int = _DEFAULT_MAX_RETRIES,
    backoff_factor: int = DEFAULT_BACKOFF_FACTOR,
) -> _RETURN_SYNC_F[_P]:
    """Applies automatic retries to HTTP requests when encountering specific errors."""
    ...


@overload
def _auto_retry_request(
    original_req_func: _ASYNC_F[_P],
    *,
    max_retries: int = _DEFAULT_MAX_RETRIES,
    backoff_factor: int = DEFAULT_BACKOFF_FACTOR,
) -> _RETURN_ASYNC_F[_P]:
    """Applies automatic retries to HTTP requests when encountering specific errors."""
    ...


@overload
def _auto_retry_request(
    original_req_func: None = None,
    *,
    max_retries: int = _DEFAULT_MAX_RETRIES,
    backoff_factor: int = DEFAULT_BACKOFF_FACTOR,
) -> _DecoratorCreator[_P]:
    """Applies automatic retries to HTTP requests when encountering specific errors."""
    ...


def _auto_retry_request(
    original_req_func: Optional[_F[_P]] = None,
    *,
    max_retries: int = _DEFAULT_MAX_RETRIES,
    backoff_factor: int = DEFAULT_BACKOFF_FACTOR,
) -> _RETURN_F[_P] | _DecoratorCreator[_P]:
    """Applies automatic retries to HTTP requests when encountering specific errors.

    Wraps the target `requests` call in a retry mechanism which will reattempt
    the call if:
        - A connection error occurs
        - A retryable HTTP error response is received

    Utilises an exponential backoff to avoid flooding the request and to give
    time for the issue to resolve itself.

    Can be used as either an argumentless decorator (@_auto_retry_request) or a
    decorator with args (@_auto_retry_request(...)).
    """

    @overload
    def _decorate(req_func: _SYNC_F) -> _RETURN_SYNC_F: ...

    @overload
    def _decorate(req_func: _ASYNC_F) -> _RETURN_ASYNC_F: ...

    def _decorate(req_func: _F) -> _RETURN_F:
        """Apply decoration to target request function."""
        if inspect.iscoroutinefunction(req_func):
            return _get_async_wrapper(
                cast(_ASYNC_F, req_func), max_retries, backoff_factor
            )
        else:
            return _get_sync_wrapper(
                cast(_SYNC_F, req_func), max_retries, backoff_factor
            )

    if original_req_func:
        # Was used as @_auto_retry_dec (or called directly).
        # original_req_func was passed in through the decorator machinery so just
        # wrap and return.
        return _decorate(original_req_func)
    else:
        # Was used as @_auto_retry_dec(**kwargs).
        # original_req_func not yet passed in so need to return a decorator function
        # to allow the decorator machinery to pass it in.
        return _decorate


def _get_sync_wrapper(
    req_func: _SYNC_F[_P], max_retries: int, backoff_factor: int
) -> _RETURN_SYNC_F[_P]:
    @wraps(req_func)
    def _wrapped_sync_req_func(
        *args: _P.args,
        do_not_retry_codes: Optional[Collection[int]] = None,
        **kwargs: _P.kwargs,
    ) -> Response:
        """Wraps target request function in retry capability.

        Adds automatic retry, backoff, and logging.

        Args:
            *args: Args to pass to the underlying request.
            do_not_retry_codes: Collection of integer status codes that should not be
                auto-retried for this call.
            **kwargs: Keyword args to pass to the underlying request.
        """
        # Set default timeout if one not provided
        timeout = kwargs.get("timeout", None)
        if timeout is None:
            # [LOGGING-IMPROVEMENTS]
            if config.settings.logging.log_web_utils:
                _logger.debug(
                    f"No request timeout provided,"
                    f" setting to default timeout ({_DEFAULT_TIMEOUT}s)"
                )
            kwargs["timeout"] = _DEFAULT_TIMEOUT

        auto_retry_codes = set(_DEFAULT_RETRY_STATUS_CODES)
        if do_not_retry_codes:
            auto_retry_codes -= set(do_not_retry_codes)
        retry_count = 0

        while retry_count <= max_retries:
            final_retry = retry_count == max_retries

            # Attempt to make wrapped request and handle if it doesn't work
            # as expected
            try:
                resp: Response = req_func(*args, **kwargs)
                # Check, if response received but not successful, that it is a
                # status code we are willing to retry and we have retries left
                if resp.status_code not in auto_retry_codes or final_retry:
                    return resp
                else:
                    failure_cause_msg = (
                        f"Error ({resp.status_code}) for"
                        f" {resp.request.method}:{resp.url}"
                    )
            except (requests.ConnectionError, requests.Timeout) as ex:
                # If a connection error occurs, we can retry unless
                # this is our final attempt
                if final_retry:
                    raise
                else:
                    failure_title = "Connection error"
                    if isinstance(ex, requests.Timeout):
                        failure_title = "Timeout"
                    # If the exception contains request info, we can use it
                    if req := ex.request:
                        failure_cause_msg = (
                            f"{failure_title} ({str(ex)}) for {req.method}:{req.url}"
                        )
                    else:
                        failure_cause_msg = f"{failure_title} ({str(ex)})"

            # If we reach this point we must be attempting a retry
            retry_count += 1
            backoff = compute_backoff(retry_count, backoff_factor)

            # Log out failure information and retry information.
            _logger.debug(
                f"{failure_cause_msg}; "
                f"will retry in {backoff} seconds (attempt {retry_count})."
            )

            time.sleep(backoff)

        # We shouldn't reach this point due to how the loop can be exited,
        # but just in case
        raise requests.ConnectionError(
            "Unable to make connection, even after multiple attempts."
        )

    return _wrapped_sync_req_func


def _get_async_wrapper(
    req_func: _ASYNC_F[_P], max_retries: int, backoff_factor: int
) -> _RETURN_ASYNC_F[_P]:
    @wraps(req_func)
    async def _wrapped_async_req_func(
        *args: _P.args,
        do_not_retry_codes: Optional[Collection[int]] = None,
        **kwargs: _P.kwargs,
    ) -> httpx.Response:
        """Wraps target HTTPX request function in retry capability.

        Adds automatic retry, backoff, and logging.

        Args:
            *args: Args to pass to the underlying request.
            do_not_retry_codes: Collection of integer status codes that should not be
                auto-retried for this call.
            **kwargs: Keyword args to pass to the underlying request.
        """
        # Set default timeout if one not provided
        timeout = kwargs.get("timeout", None)
        if timeout is None or timeout is USE_CLIENT_DEFAULT:
            # [LOGGING-IMPROVEMENTS]
            if config.settings.logging.log_web_utils:
                _logger.debug(
                    f"No request timeout provided,"
                    f" setting to default timeout ({_DEFAULT_TIMEOUT}s)"
                )
            # Want to allow arbitrary time lengths for read and write as
            # upload/download may take a while
            kwargs["timeout"] = httpx.Timeout(
                connect=_DEFAULT_TIMEOUT,
                read=None,
                write=None,
                pool=_DEFAULT_TIMEOUT,
            )

        auto_retry_codes = set(_DEFAULT_RETRY_STATUS_CODES)
        if do_not_retry_codes:
            auto_retry_codes -= set(do_not_retry_codes)
        retry_count = 0

        while retry_count <= max_retries:
            final_retry = retry_count == max_retries

            # Attempt to make wrapped request and handle if it doesn't work
            # as expected
            try:
                resp: httpx.Response = await req_func(*args, **kwargs)

                # Check, if response received but not successful, that it is a
                # status code we are willing to retry and we have retries left
                if resp.status_code not in auto_retry_codes or final_retry:
                    return resp
                else:
                    failure_cause_msg = (
                        f"Error ({resp.status_code}) for"
                        f" {resp.request.method}:{resp.url}"
                    )
            except httpx.ConnectError as ex:
                # If a connection error occurs, we can retry unless
                # this is our final attempt
                if final_retry:
                    raise
                else:
                    # If the exception contains request info, we can use it
                    try:
                        req = ex.request
                    except RuntimeError:
                        failure_cause_msg = f"Connection error ({str(ex)})"
                    else:
                        failure_cause_msg = (
                            f"Connection error ({str(ex)}) for {req.method}:{req.url}"
                        )

            # If we reach this point we must be attempting a retry
            retry_count += 1
            backoff = compute_backoff(retry_count, backoff_factor)

            # Log out failure information and retry information.
            _logger.debug(
                f"{failure_cause_msg}; "
                f"will retry in {backoff} seconds (attempt {retry_count})."
            )

            await asyncio.sleep(backoff)

        # We shouldn't reach this point due to how the loop can be exited,
        # but just in case
        raise httpx.HTTPError(
            "Unable to make connection, even after multiple attempts."
        )

    return _wrapped_async_req_func


# Create patched versions of the `requests` methods
request = _auto_retry_request(  #: This is needed to get pdoc to pick these up
    requests.request
)
head = _auto_retry_request(  #: This is needed to get pdoc to pick these up
    requests.head
)
get = _auto_retry_request(requests.get)  #: This is needed to get pdoc to pick these up
post = _auto_retry_request(  #: This is needed to get pdoc to pick these up
    requests.post
)
put = _auto_retry_request(requests.put)  #: This is needed to get pdoc to pick these up
patch = _auto_retry_request(  #: This is needed to get pdoc to pick these up
    requests.patch
)
delete = _auto_retry_request(  #: This is needed to get pdoc to pick these up
    requests.delete
)

__pdoc__ = {
    "request": "See `requests.request()` for more details.",
    "head": "See `requests.head()` for more details.",
    "get": "See `requests.get()` for more details.",
    "post": "See `requests.post()` for more details.",
    "put": "See `requests.put()` for more details.",
    "patch": "See `requests.patch()` for more details.",
    "delete": "See `requests.delete()` for more details.",
}


# Create patched versions of the HTTPX methods
class _AsyncClient(httpx.AsyncClient):
    # We only wrap this method in _auto_retry_request as any calls to the others
    # (post, get, etc) will make use of this. Wrapping them all would result in
    # a double retry loop, but we can't _not_ wrap request as it is often used
    # directly.
    @_auto_retry_request
    async def request(  # type: ignore[override] # Reason: wrapped function adds a new kwarg, but this isn't passed through to the underlying super() call # noqa: E501
        self,
        method: str,
        url: URLTypes,
        *,
        content: Optional[RequestContent] = None,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        auth: Union[AuthTypes, UseClientDefault, None] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: Optional[MutableMapping[str, Any]] = None,
    ) -> httpx.Response:
        """See httpx.AsyncClient.request() for information."""  # noqa: D402
        return await super().request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )


async def async_request(
    method: str,
    url: URLTypes,
    *,
    content: Optional[RequestContent] = None,
    data: Optional[RequestData] = None,
    files: Optional[RequestFiles] = None,
    json: Optional[Any] = None,
    params: Optional[QueryParamTypes] = None,
    headers: Optional[HeaderTypes] = None,
    cookies: Optional[CookieTypes] = None,
    auth: Union[AuthTypes, UseClientDefault, None] = USE_CLIENT_DEFAULT,
    follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: Optional[dict] = None,
    do_not_retry_codes: Optional[Collection[int]] = None,
) -> httpx.Response:
    """See httpx.request() for more information."""
    async with _AsyncClient() as client:
        return await client.request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
            do_not_retry_codes=do_not_retry_codes,
        )


async def async_get(
    url: URLTypes,
    *,
    params: Optional[QueryParamTypes] = None,
    headers: Optional[HeaderTypes] = None,
    cookies: Optional[CookieTypes] = None,
    auth: Union[AuthTypes, UseClientDefault, None] = USE_CLIENT_DEFAULT,
    follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: Optional[dict] = None,
    do_not_retry_codes: Optional[Collection[int]] = None,
) -> httpx.Response:
    """See httpx.get() for more information."""
    async with _AsyncClient() as client:
        return await client.request(
            "GET",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
            do_not_retry_codes=do_not_retry_codes,
        )


async def async_options(
    url: URLTypes,
    *,
    params: Optional[QueryParamTypes] = None,
    headers: Optional[HeaderTypes] = None,
    cookies: Optional[CookieTypes] = None,
    auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: Optional[dict] = None,
    do_not_retry_codes: Optional[Collection[int]] = None,
) -> httpx.Response:
    """See httpx.options() for more information."""
    async with _AsyncClient() as client:
        return await client.request(
            "OPTIONS",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
            do_not_retry_codes=do_not_retry_codes,
        )


async def async_head(
    url: URLTypes,
    *,
    params: Optional[QueryParamTypes] = None,
    headers: Optional[HeaderTypes] = None,
    cookies: Optional[CookieTypes] = None,
    auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: Optional[dict] = None,
    do_not_retry_codes: Optional[Collection[int]] = None,
) -> httpx.Response:
    """See httpx.head() for more information."""
    async with _AsyncClient() as client:
        return await client.request(
            "HEAD",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
            do_not_retry_codes=do_not_retry_codes,
        )


async def async_post(
    url: URLTypes,
    *,
    content: Optional[RequestContent] = None,
    data: Optional[RequestData] = None,
    files: Optional[RequestFiles] = None,
    json: Optional[Any] = None,
    params: Optional[QueryParamTypes] = None,
    headers: Optional[HeaderTypes] = None,
    cookies: Optional[CookieTypes] = None,
    auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: Optional[dict] = None,
    do_not_retry_codes: Optional[Collection[int]] = None,
) -> httpx.Response:
    """See httpx.post() for more information."""
    async with _AsyncClient() as client:
        return await client.request(
            "POST",
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
            do_not_retry_codes=do_not_retry_codes,
        )


async def async_put(
    url: URLTypes,
    *,
    content: Optional[RequestContent] = None,
    data: Optional[RequestData] = None,
    files: Optional[RequestFiles] = None,
    json: Optional[Any] = None,
    params: Optional[QueryParamTypes] = None,
    headers: Optional[HeaderTypes] = None,
    cookies: Optional[CookieTypes] = None,
    auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: Optional[dict] = None,
    do_not_retry_codes: Optional[Collection[int]] = None,
) -> httpx.Response:
    """See httpx.put() for more information."""
    async with _AsyncClient() as client:
        return await client.request(
            "PUT",
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
            do_not_retry_codes=do_not_retry_codes,
        )


async def async_patch(
    url: URLTypes,
    *,
    content: Optional[RequestContent] = None,
    data: Optional[RequestData] = None,
    files: Optional[RequestFiles] = None,
    json: Optional[Any] = None,
    params: Optional[QueryParamTypes] = None,
    headers: Optional[HeaderTypes] = None,
    cookies: Optional[CookieTypes] = None,
    auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: Optional[dict] = None,
    do_not_retry_codes: Optional[Collection[int]] = None,
) -> httpx.Response:
    """See httpx.patch() for more information."""
    async with _AsyncClient() as client:
        return await client.request(
            "PATCH",
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
            do_not_retry_codes=do_not_retry_codes,
        )


async def async_delete(
    url: URLTypes,
    *,
    params: Optional[QueryParamTypes] = None,
    headers: Optional[HeaderTypes] = None,
    cookies: Optional[CookieTypes] = None,
    auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: Optional[dict] = None,
    do_not_retry_codes: Optional[Collection[int]] = None,
) -> httpx.Response:
    """See httpx.delete() for more information."""
    async with _AsyncClient() as client:
        return await client.request(
            "DELETE",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
            do_not_retry_codes=do_not_retry_codes,
        )
