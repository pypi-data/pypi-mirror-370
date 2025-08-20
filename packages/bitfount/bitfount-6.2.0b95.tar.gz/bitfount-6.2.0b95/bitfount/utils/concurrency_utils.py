"""Useful components related to asyncio, multithreading or multiprocessing."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
import enum
from enum import Enum
from functools import partial, wraps
import logging
import threading
from typing import Final, Literal, Optional, Protocol, TypeVar, Union, cast

from typing_extensions import Concatenate, ParamSpec

from bitfount import config
from bitfount.exceptions import BitfountError

_logger = logging.getLogger(__name__)

_R = TypeVar("_R")
_P = ParamSpec("_P")

_DEFAULT_POLLING_TIMEOUT: Final = 5  # seconds


# Workaround for type hinting sentinel values:
# https://github.com/python/typing/issues/689
class _NoPolling(Enum):
    """Sentinel type for indicating no polling should occur."""

    NO_POLLING = enum.auto()


NO_POLLING: Final = _NoPolling.NO_POLLING  # sentinel value


def _asyncify(
    func: Callable[_P, _R], *args: _P.args, **kwargs: _P.kwargs
) -> asyncio.Future[_R]:
    """Run sync function in separate thread to avoid blocking event loop.

    Uses the default ThreadPoolExecutor for whichever event loop is running this
    function and returns an asyncio.Future object to await the result of the
    execution on.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError as ex:
        raise BitfountError(
            "Tried to asyncify without running loop;"
            " _asyncify() should only be called from async functions."
        ) from ex

    # Use default executor for this loop (signified by `None`)
    if kwargs:
        p_func = partial(func, **kwargs)
        fut = loop.run_in_executor(None, p_func, *args)
    else:
        # Separate this call version out, so we don't unnecessarily wrap in a partial
        # which makes debugging harder
        fut = loop.run_in_executor(None, func, *args)
    return fut


async def await_threading_event(
    event: threading.Event,
    event_name: str,
    timeout: Optional[float] = None,
    polling_timeout: Union[
        float, Literal[_NoPolling.NO_POLLING]
    ] = _DEFAULT_POLLING_TIMEOUT,
) -> bool:
    """Event.wait() that doesn't block the event loop.

    Avoids saturation of the ThreadPoolExecutor by either limiting run time directly
    (via `timeout`) or by occassionally rescheduling the wait so other thread-based
    tasks get a chance to run (via `polling_timeout`).

    If both `timeout` and `polling_timeout` are supplied, `timeout` takes precedence
    and no polling/rescheduling will be performed.

    If `polling_timeout` is set to `NO_POLLING` then the thread will wait indefinitely.
    This should be used rarely and with caution as it may leave either hanging threads
    or saturate all threads of the ThreadPoolExecutor.

    Args:
        event: The event to wait on.
        event_name: The name of the event, used in debug logging.
        timeout: The timeout to wait for the event to be set.
        polling_timeout: How frequently to return control to this function from
            the thread execution. If the event is still not set, the thread execution
            is rescheduled. Useful for handling cancellation events as it places
            a bound on the time a thread can run.

    Returns:
        `True` if the event is set within any timeout constraints specified,
        `False` otherwise.
    """
    if (
        config.settings.logging.multithreading_debug
        and timeout is None
        and polling_timeout is NO_POLLING
    ):
        _logger.warning(
            f"await_threading_event({event_name}) called without timeout or"
            f" polling timeout for {event=};"
            f" this may cause hanging threads"
        )

    if config.settings.logging.multithreading_debug:
        _logger.debug(f"Going to wait in thread on event {event_name} {event=}")

    # Use timeout as priority timeout
    if timeout:
        return await _asyncify(event.wait, timeout=timeout)

    # Otherwise use polling approach
    else:
        event_set: bool = False
        try:
            while True:
                if polling_timeout is not NO_POLLING:
                    event_set = await _asyncify(event.wait, timeout=polling_timeout)
                else:
                    event_set = await _asyncify(event.wait)

                if event_set:
                    if config.settings.logging.multithreading_debug:
                        _logger.info(f"Event {event_name} was set {event=}")
                    break
                else:
                    if config.settings.logging.multithreading_debug:
                        _logger.debug(
                            f"Event {event_name} {event=} was not set in timeout,"
                            f" will try again"
                        )

            # This should be `True` at this point as in this path no `wait()` timeout
            # is possible.
            return event_set
        except asyncio.CancelledError:
            if config.settings.logging.multithreading_debug:
                _logger.warning(
                    f"Event waiting for {event_name} was cancelled"
                    f" {event_set=} {event=};"
                    f" this may leave threads hanging if no timeout was specified"
                )
            raise


async def await_event_with_stop(
    wait_event: threading.Event,
    stop_event: threading.Event,
    wait_event_name: str,
    polling_timeout: float = _DEFAULT_POLLING_TIMEOUT,
) -> bool:
    """Helper function that waits on a Threading Event but allows exiting early.

    Avoids blocking the async event loop.

    Monitors the wait_event but with a polling timeout, so it can periodically check
    if it should stop early.

    Args:
        wait_event: The event to wait to be set.
        stop_event: An event indicating we should stop early.
        wait_event_name: The name of the wait event, used for debugging.
        polling_timeout: The amount of time in seconds between checks for whether
            the stop_event has been set.

    Returns:
        `True` if the `wait_event` has been set, `False` if the `stop_event` is
         used to cancel waiting before the `wait_event` is set.
    """
    while not stop_event.is_set():
        # We explicitly use `timeout` rather than `polling_timeout` to ensure control
        # returns to us here rather than the while-loop in `await_threading_event()`.
        wait_event_is_set = await await_threading_event(
            wait_event, event_name=wait_event_name, timeout=polling_timeout
        )
        if wait_event_is_set:
            return True
    return False


@asynccontextmanager
async def asyncnullcontext() -> AsyncGenerator[None, None]:
    """Async version of contextlib.nullcontext()."""
    yield None


@asynccontextmanager
async def async_lock(
    lock: threading.Lock,
    lock_name: str,
    polling_timeout: Union[
        float, Literal[_NoPolling.NO_POLLING]
    ] = _DEFAULT_POLLING_TIMEOUT,
) -> AsyncGenerator[None, None]:
    """Context manager to acquire a threading.Lock from the async event loop.

    Avoids blocking the async event loop.

    Avoids saturation of the ThreadPoolExecutor by limiting thread run times (via
    `polling_timeout`) to enable to control to return to this function and to
    reschedule the wait so other thread-based tasks get a chance to run. Control
    is returned to here every `polling_timeout` seconds and allows asyncio cancellation
    to avoid hanging threads.

    If `polling_timeout` is `NO_POLLING`, then the thread will wait indefinitely.

    Handles releasing the lock at the end of the context.

    Args:
        lock: The threading.Lock to acquire.
        lock_name: The name of the lock to acquire, used for debugging.
        polling_timeout: How frequently to return control to this function from
            the thread execution. If the lock is still not acquired, the thread
            execution is rescheduled. Useful for handling cancellation events as
            it places a bound on the time a thread can run.

    Yields:
        A context in which the desired threading.Lock has been acquired.
    """
    if config.settings.logging.multithreading_debug and polling_timeout is NO_POLLING:
        _logger.warning(
            f"async_lock({lock_name}) called without polling timeout for {lock=};"
            f" this may cause hanging threads"
        )

    acquired: bool = False
    try:
        while True:
            if config.settings.logging.multithreading_debug:
                _logger.debug(f"Going to wait in thread on lock {lock_name} {lock=}")

            if polling_timeout is not NO_POLLING:
                acquired = await _asyncify(lock.acquire, timeout=polling_timeout)
            else:
                acquired = await _asyncify(lock.acquire)

            if acquired:
                if config.settings.logging.multithreading_debug:
                    _logger.info(f"Acquired lock {lock_name} {lock=}")
                break
            else:
                if config.settings.logging.multithreading_debug:
                    _logger.debug(
                        f"Didn't acquire lock {lock_name} {lock=} in timeout,"
                        f" will try again"
                    )

        yield  # the lock is held
    except asyncio.CancelledError:
        if config.settings.logging.multithreading_debug:
            _logger.warning(
                f"Async lock {lock_name} was cancelled {acquired=} {lock=};"
                f" this may leave threads hanging if no timeout was specified"
            )
        raise
    finally:
        # Reassure mypy that `acquired` can be True or False at this point (due
        # to exceptions occurring potentially); mypy complains this is redundant
        # but then _also_ complains that the `else` statement below is unreachable
        # without it.
        acquired = cast(bool, acquired)  # type: ignore[redundant-cast] # Reason: See comment # noqa: E501

        if acquired:
            if config.settings.logging.multithreading_debug:
                _logger.info(f"Releasing lock {lock_name} {lock=}")
            lock.release()
        else:
            if config.settings.logging.multithreading_debug:
                _logger.warning(
                    f"async_lock() finished without acquisition of"
                    f" {lock_name} {lock=} {acquired=}"
                )


class ThreadWithException(threading.Thread):
    """A thread subclass that captures exceptions to be reraised in the main thread."""

    def run(self) -> None:
        """See parent method for documentation.

        Captures exceptions raised during the run call and stores them as an attribute.
        """
        self._exc: Optional[Exception] = None
        try:
            super().run()
        except Exception as e:
            self._exc = e
            raise

    def join(self, timeout: Optional[float] = None) -> None:
        """See parent method for documentation.

        If an exception occurs in the joined thread it will be reraised in the calling
        thread.
        """
        super().join(timeout)
        if self._exc:
            raise self._exc


# #################################################### #
# Decorator for thread-safe synchronisation of methods #
# #################################################### #
_LOCK = TypeVar("_LOCK", bound=Union[threading.Lock, threading.RLock])


class _Synchronisable(Protocol[_LOCK]):
    """Represents a class that can be synchronised."""

    _sync_lock: _LOCK


SelfWithLock = TypeVar(
    "SelfWithLock",
    bound=Union[_Synchronisable[threading.Lock], _Synchronisable[threading.RLock]],
)


def _synchronised(
    meth: Callable[Concatenate[SelfWithLock, _P], _R],
) -> Callable[Concatenate[SelfWithLock, _P], _R]:
    """Wrap target method with instance's Lock."""
    if asyncio.iscoroutinefunction(meth):
        raise TypeError(
            "_synchronised cannot be used with async functions as it may block the"
            " event loop."
        )

    @wraps(meth)
    def _wrapper(self_: SelfWithLock, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        if config.settings.logging.multithreading_debug:
            _logger.debug(
                f"Waiting on {self_.__class__.__name__} lock ({id(self_._sync_lock)})"
                f" in {threading.current_thread().name}"
            )

        with self_._sync_lock:
            if config.settings.logging.multithreading_debug:
                _logger.debug(
                    f"Got {self_.__class__.__name__} lock ({id(self_._sync_lock)}) in"
                    f" {threading.current_thread().name}"
                )

            res = meth(self_, *args, **kwargs)

        if config.settings.logging.multithreading_debug:
            _logger.debug(
                f"Released {self_.__class__.__name__} lock ({id(self_._sync_lock)}) in"
                f" {threading.current_thread().name}"
            )
        return res

    return _wrapper
