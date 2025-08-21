"""Callbacks and wrappers for async message service calls."""

from __future__ import annotations

import asyncio
from asyncio.futures import Future as AsyncFuture
import atexit
from collections.abc import (
    Callable,
    Collection,
    Coroutine,
    Generator,
    Iterable,
)
from concurrent.futures import Future as ConcurrentFuture, ThreadPoolExecutor
from dataclasses import dataclass
from functools import wraps
import inspect
import threading
from threading import Lock as ThreadingLock
from typing import TYPE_CHECKING, Any, Final, Generic, Optional, TypeVar, Union, cast
import uuid
import warnings
import weakref

from bitfount.encryption.exceptions import DecryptError
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.transport.message_service import (
    _BitfountMessage,
    _BitfountMessageType,
)
from bitfount.utils.concurrency_utils import await_event_with_stop

if TYPE_CHECKING:
    from bitfount.federated.transport.base_transport import Handler, _BaseMailbox

logger = _get_federated_logger(__name__)

_PRIORITY_HANDLER_MAX_WORKERS: Final = 5

# Return type placeholder
_R = TypeVar("_R")


class _AsyncCallback(Generic[_R]):
    """Async wrapper around a callback function.

    Allows us to `await` on the result of this callback. By overriding __call__
    the fact that we've wrapped the callback is transparent to the calling code.
    """

    def __init__(self, fn: Callable[[_BitfountMessage], _R]):
        """Create a new AsyncCallback.

        Args:
            fn: the callback function to be wrapped.
        """
        self._fn = fn
        self._result_exists = asyncio.Event()
        self._result: _R

    def __call__(self, message: _BitfountMessage) -> None:
        """Call the underlying (synchronous) callback function."""
        # Overriding __call__ allows us to transparently wrap the underlying
        # function call so that the call to the async callback looks just like
        # a normal call to the function itself.
        self._result = self._fn(message)
        self._result_exists.set()

    async def result(self, timeout: Optional[int] = None) -> _R:
        """Asynchronously retrieve the result of the callback.

        Will (non-blockingly) wait on the callback to be called.

        Args:
            timeout: Timeout in seconds to await on the result. If not
                provided, will wait indefinitely. Optional.

        Returns:
            The return value of the callback.

        Raises:
            asyncio.TimeoutError: If timeout provided and result is not set within
                timeout seconds.
        """
        if timeout:
            await asyncio.wait_for(self._result_exists.wait(), timeout)
        else:
            await self._result_exists.wait()
        return self._result

    def reset(self) -> None:
        """Clears the result of the callback, allowing it to be re-used."""
        # We don't need to clear the actual result here as that's set before the
        # _result_exists is set.
        self._result_exists.clear()


def _simple_message_returner(x: _BitfountMessage) -> _BitfountMessage:
    """Simple callback that simply returns the message."""
    return x


def _get_message_awaitable() -> _AsyncCallback[_BitfountMessage]:
    """Returns an awaitable wrapper around message retrieval."""
    return _AsyncCallback(_simple_message_returner)


class _AsyncMultipleResponsesHandler:
    """Wraps multiple expected responses in a singular awaitable."""

    def __init__(
        self,
        handler: Handler,
        message_types: Union[_BitfountMessageType, Collection[_BitfountMessageType]],
        mailbox: _BaseMailbox,
        responders: Collection[str],
    ):
        """Creates a handler for multiple responses of a given type(s).

        When expecting multiple separate responses from a set of responders, this
        class will provide an awaitable that returns when either all expected responses
        have been received, or when a timeout is reached (in which case it returns
        the set of those who didn't respond).

        Each message is passed to the assigned handler and track is kept of those
        who have responded. The awaitable returned blocks asynchronously on all
        responses being received.

        Can be used as a context manager which ensures that all message type handlers
        are correctly attached and removed at the end of the usage.

        Args:
            handler: The async function to call for each received message.
            message_types: The message types to handle.
            mailbox: The mailbox where messages will be received.
            responders: The set of expected responders.
        """
        self._orig_handler = handler
        if not isinstance(message_types, Iterable):
            message_types = [message_types]
        self._message_types = message_types
        self._mailbox = mailbox
        self.responders = responders

        # Initialise to the full set of expected and remove them as they response.
        self._not_responded = set(responders)

        # Synchronization primitives for handling multiple responses coming in
        # simultaneously and for keeping track of when all responses have been received.
        self._lock = asyncio.Lock()
        self._responses_done = asyncio.Event()
        self._timeout_reached = False

    async def handler(self, message: _BitfountMessage) -> None:
        """An augmented handler for multiple responses.

        Wraps the supplied handler and tracks the expected responses.

        Args:
            message: The message to be processed.
        """
        # We want to wrap the supplied handler with additional logic to (a) avoid
        # multiple calls to the handler simultaneously which may mess with state,
        # and (b) to enable us to monitor when all responses have been received so
        # we can exit.

        # This lock prevents multiple calls to the handler at the same time
        async with self._lock:
            # This check prevents calls being processed after we have marked it
            # as done, for instance if timeout has occurred.
            if not self._responses_done.is_set():
                # We mark the responder as responded and handle cases where we
                # receive an unexpected response.
                try:
                    self._not_responded.remove(message.sender)
                except KeyError:
                    if message.sender in self.responders:
                        logger.error(
                            f"Received multiple responses from {message.sender}; "
                            f"only expecting one response per responder."
                        )
                    else:
                        logger.error(
                            f"Received unexpected response from {message.sender}; "
                            f"they were not in the list of expected responders."
                        )
                # Once marked as responded we can call the underlying handler and then
                # check whether all responses have been received.
                else:
                    # As this supports both sync and async handlers we need to
                    # process the result (which should be None, but could be a
                    # Coroutine returning None). As such, we comfortably call the
                    # handler and then simply await the result if needed.
                    handler_return = self._orig_handler(message)
                    if inspect.isawaitable(handler_return):
                        await handler_return

                    if len(self._not_responded) == 0:
                        self._responses_done.set()
            # Handle responses received after we're marked as done
            else:
                if self._timeout_reached:
                    logger.warning(
                        f"Message received after timeout reached; "
                        f"responder too slow, message will not be processed: {message}"
                    )
                else:
                    logger.warning(
                        f"Received message too early, storing for later "
                        f"processing: {message}"
                    )
                    # Requeue message for later processing
                    self._mailbox.requeue_message(message)

    def __enter__(self) -> _AsyncMultipleResponsesHandler:
        self.setup_handlers()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.remove_handlers()

    def setup_handlers(self) -> None:
        """Setup the augmented handler for the supplied message types."""
        for message_type in self._message_types:
            self._mailbox.register_handler(message_type, self.handler)

    def remove_handlers(self) -> None:
        """Remove the augmented handler for the supplied message types."""
        for message_type in self._message_types:
            self._mailbox.delete_handler(message_type, self.handler)

    async def wait_for_responses(self, timeout: Optional[int] = None) -> set[str]:
        """Waits for the set of responses to be handled.

        Each response is passed to the supplied (augmented) handler and this method
        will return once all responders have responded or until timeout is reached.

        Args:
            timeout: Optional. Timeout in seconds to wait for all responses to be
                received. If provided, any responders who failed to respond in time
                will be returned as a set.

        Returns:
            The set of responders who did not respond in time.
        """
        # Wait for all responses to have been received or
        # until the timeout expires (if provided).
        try:
            if timeout:
                await asyncio.wait_for(self._responses_done.wait(), timeout)
            else:
                await self._responses_done.wait()
        except asyncio.TimeoutError:
            self._timeout_reached = True
            # Acquiring the lock guarantees that no other responses are
            # _currently_ being processed (and hence we can set the event)
            async with self._lock:
                # Setting this stops other responses in the event loop from
                # being processed _later_.
                self._responses_done.set()

        # Will be empty if all responses received
        return self._not_responded


@dataclass(frozen=True)
class _TemporaryHandler:
    """A wrapper indicating that a handler is to be used only once."""

    handler: Handler


def _init_event_loop_in_thread() -> None:
    """Create and set a new event loop.

    Should be used as the initializer method in a ThreadPoolExecutor so that all
    threads have a persistent event loop that can be used.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    logger.debug(
        f"asyncio loop set to {loop} {id(loop)=} in {threading.current_thread().name}"
    )


# Create a thread pool for executing high-priority handlers and register its
# shutdown method to be run on program exit.
# Also create a container to store pending futures and to allow us to cancel them
# in the case of a shutdown.
_priority_handler_thread_pool = ThreadPoolExecutor(
    max_workers=_PRIORITY_HANDLER_MAX_WORKERS,
    thread_name_prefix="priority-handler",
    initializer=_init_event_loop_in_thread,
)
_priority_handler_futures: set[ConcurrentFuture] = set()
_priority_handler_futures_lock: Final = ThreadingLock()


def _shutdown_priority_handler_thread_pool() -> None:
    """Shutdown handler to ensure thread pool shutdown."""
    # Shutdown thread pool (any running tasks may run until completion)
    _priority_handler_thread_pool.shutdown(wait=False)

    # TODO: [Python 3.9]
    # Cancel all outstanding futures
    # NOTE: In Python 3.9+ we can use the built-in ThreadPoolExecutor.shutdown()
    #       method to also cancel futures.
    with _priority_handler_futures_lock:
        for f in _priority_handler_futures:
            f.cancel()


atexit.register(_shutdown_priority_handler_thread_pool)


def _concurrent_future_done(fut: ConcurrentFuture) -> None:
    """Callback function for removing futures from _priority_handler_futures."""
    # As the handler is finished we can remove it from the set of futures that we
    # need to consider for cancellation. We use `discard()` here as we don't care
    # if it's already been removed.
    with _priority_handler_futures_lock:
        _priority_handler_futures.discard(fut)


def _wrap_handler_with_lock(
    fn: Callable[[_BitfountMessage], _R], lock: ThreadingLock
) -> Callable[[_BitfountMessage], _R]:
    """Wraps the target callable in a lock acquisition."""

    @wraps(fn)
    def _wrapped(message: _BitfountMessage) -> _R:
        with lock:
            return fn(message)

    return _wrapped


def _wrap_async_func(
    fn: Callable[[_BitfountMessage], Coroutine[Any, Any, _R]],
) -> Callable[[_BitfountMessage], _R]:
    """Wraps the target async callable in a sync wrapper."""

    @wraps(fn)
    def _wrapped(message: _BitfountMessage) -> _R:
        loop = asyncio.get_event_loop()
        logger.debug(
            f"Retrieved asyncio loop {loop} {id(loop)=}"
            f" in {threading.current_thread().name}"
        )
        if loop.is_running():
            return asyncio.run_coroutine_threadsafe(fn(message), loop=loop).result()
        else:
            return loop.run_until_complete(fn(message))

    return _wrapped


class _PriorityHandler(Generic[_R]):
    """A handler that executes with priority by running in a separate thread."""

    def __init__(
        self,
        fn: Union[
            Callable[[_BitfountMessage], _R],
            Callable[[_BitfountMessage], Coroutine[Any, Any, _R]],
        ],
        set_exclusive: bool = True,
    ):
        """Create new priority handler.

        Args:
            fn: The underlying handler to wrap.
            set_exclusive: Whether the handler should only allow one running call
                at any given time.
        """
        self._orig_fn = fn

        self._fn: Callable[[_BitfountMessage], _R]
        if asyncio.iscoroutinefunction(self._orig_fn):
            self._fn = _wrap_async_func(
                cast(
                    Callable[[_BitfountMessage], Coroutine[Any, Any, _R]],
                    self._orig_fn,
                )
            )
        else:
            self._fn = cast(Callable[[_BitfountMessage], _R], self._orig_fn)

        # The lock is managed in here because it needs to be passed into the calling
        # thread and to ensure that only a single call to this handler can be being
        # run at a time. This precludes us from having the lock external to the
        # handler (i.e. in the _HandlerRegister) without having to have a different
        # call signature for the handler (to allow the lock to be passed in).
        self._lock: Optional[ThreadingLock] = None
        if set_exclusive:
            self.set_exclusive()

        # These are used to monitor for the event result and allow us to await on it.
        # NOTE: asyncio.Event() is not thread safe, and so this should only be
        #       accessed from the _calling_ thread. AsyncFuture is not _inherently_
        #       thread safe, but because we create it by wrapping a ConcurrentFuture
        #       it is (as the thread itself interacts with the ConcurrentFuture,
        #       not the AsyncFuture directly).
        self._called = asyncio.Event()
        self._fut: AsyncFuture[_R]

    def __call__(self, message: _BitfountMessage) -> None:
        """Call the underlying handler in a thread."""
        c_fut = _priority_handler_thread_pool.submit(self._fn, message)

        # Register the concurrent future for later shutdown cancellation if needed
        # and adds done_callback
        with _priority_handler_futures_lock:
            _priority_handler_futures.add(c_fut)
        c_fut.add_done_callback(_concurrent_future_done)

        self._fut = asyncio.wrap_future(c_fut)
        self._called.set()

    def set_exclusive(self) -> None:
        """Sets the handler so that only one instance can be running at a time.

        If handler is already marked as exclusive, does nothing.
        """
        if not self._lock:
            self._lock = ThreadingLock()
            self._fn = _wrap_handler_with_lock(self._fn, self._lock)

    @property
    def lock(self) -> Optional[ThreadingLock]:
        """Get the underlying threading.Lock if presented.

        If exclusivity is set, will return the threading.Lock used to ensure this,
        otherwise None.
        """
        return self._lock

    async def _result(self) -> _R:
        """Handles actual result retrieval."""
        # If handler not yet called, wait for that to occur
        await self._called.wait()

        # Then wait for handler to complete
        return await self._fut

    async def result(self, timeout: Optional[int] = None) -> _R:
        """Asynchronously retrieve the result of the callback.

        Will (non-blockingly) wait on the callback to be called.

        Args:
            timeout: Timeout in seconds to await on the result. If not
                provided, will wait indefinitely. Optional.

        Returns:
            The return value of the callback.

        Raises:
            asyncio.TimeoutError: If timeout provided and result is not set within
                timeout seconds.
        """
        return await asyncio.wait_for(self._result(), timeout)

    def __await__(self) -> Generator[Any, None, _R]:
        """Allows `await` functionality directly on the result of the handler."""
        return self.result().__await__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {repr(self._orig_fn)}"


class _OnlineResponseHandling:
    """A class for monitoring and handling of online checking and responses."""

    def __init__(self, modeller_name: str, aes_key: bytes) -> None:
        """Create a new instance.

        Args:
            modeller_name: The name of the modeller in this task. Used to determine
                which of the received messages should count as online responses.
            aes_key: The encryption key that message bodies will be encrypted with.
        """
        self._modeller_name = modeller_name
        self._aes_key = aes_key
        self._lock = threading.Lock()
        self._waiting: dict[str, threading.Event] = {}

        # Create a finalizer so that, when this _OnlineResponseHandling instance
        # goes out of scope, any remaining listeners for events are resolved.
        self._finalizer = weakref.finalize(
            self, _OnlineResponseHandling._clear_event_dict, self._waiting, self._lock
        )

    def get_online_check_id(self) -> str:
        """Generate a UUID to place in the message body.

        Also creates an event to mark that we are waiting for a response.
        """
        with self._lock:
            ident = uuid.uuid4().hex
            self._waiting[ident] = threading.Event()
            return ident

    def _mark_all_waiting(self) -> None:
        """Mark all pending events as set and clear them."""
        with self._lock:
            for event in self._waiting.values():
                event.set()
            self._waiting.clear()

    def remove_waiter(self, ident: str) -> None:
        """Remove a specific waiter and mark it as done."""
        with self._lock:
            try:
                event = self._waiting.pop(ident)
                event.set()
            except KeyError:
                # Potentially already removed
                return

    def response_handler(self, message: _BitfountMessage) -> None:
        """Handles messages for online responses.

        Will handle any message type from the intended modeller and use any being
        received to indicate that the modeller is still online.

        Args:
            message: The message to handle.
        """
        if message.sender != self._modeller_name:
            # This isn't relevant for our modeller online checking
            return

        if message.message_type != _BitfountMessageType.ONLINE_RESPONSE:
            # Not an explicit online response but shows modeller _is_ online.
            # Mark all waiting as done.
            self._mark_all_waiting()
        else:  # message.message_type == _BitfountMessageType.ONLINE_RESPONSE
            try:
                decrypted = message.decrypt(self._aes_key)
            except DecryptError:
                logger.warning(
                    "Unable to decrypt ONLINE_RESPONSE message for response checking;"
                    " likely this is not a modeller->pod message."
                )
                # Mark all done as cannot establish _which_ it was intended for
                # but know that modeller is online
                self._mark_all_waiting()
            else:
                if decrypted.body is None:
                    # Older ONLINE_RESPONSE messages will not have the ident
                    # in the body, and so we just have to treat it as though
                    # it is _any_ response
                    warnings.warn(
                        "Support for ID-less ONLINE_RESPONSE messages will be"
                        " removed in a future release, please update your"
                        " bitfount version.",
                        DeprecationWarning,
                    )
                    self._mark_all_waiting()
                else:
                    # Otherwise, try and mark only that specific response monitor
                    try:
                        with self._lock:
                            self._waiting[decrypted.body].set()
                    except KeyError:
                        logger.debug(
                            f"Not waiting on this response ident {decrypted.body}"
                        )

    async def wait_for_response(self, ident: str) -> None:
        """Provides an async interface to wait for modeller online checking."""
        with self._lock:
            try:
                wait_event = self._waiting[ident]
            except KeyError:
                logger.debug(f"Not waiting on this response ident {ident}")
                return None

        # Otherwise wait on the event to be set or for a request to stop waiting
        stop_event = threading.Event()
        try:
            await await_event_with_stop(
                wait_event,
                stop_event,
                wait_event_name=f"online_response_waiter_{ident}",
            )
        except asyncio.CancelledError:
            # If us waiting on this is cancelled, need to ensure the wait
            # thread finishes as well
            stop_event.set()
            raise
        return None

    @staticmethod
    def _clear_event_dict(
        event_dict: dict[str, threading.Event], lock: threading.Lock
    ) -> None:
        """Clear the event dictionary by setting all events to done.

        This is used by the finalizer to ensure no threads are left waiting. Due
        to this it must be @staticmethod to not have a reference to the
        _OnlineResponseHandling instance (which would block the finalizer from
        running).
        """
        acquired = lock.acquire(blocking=False)

        if not acquired:
            raise RuntimeError(
                "Could not acquire lock to finalise online response handling events"
            )
        else:
            try:
                for event in event_dict.values():
                    event.set()
                event_dict.clear()
            finally:
                lock.release()
