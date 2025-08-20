"""Base mailbox classes for other mailbox classes to inherit from."""

from __future__ import annotations

import asyncio
from asyncio import FIRST_COMPLETED, AbstractEventLoop, Task
from asyncio.futures import Future as AsyncFuture
from collections import defaultdict
from collections.abc import (
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Generator,
    Iterable,
    Mapping,
)
from concurrent.futures import Future as ConcurrentFuture, ThreadPoolExecutor
from contextlib import AbstractAsyncContextManager, contextmanager
import inspect
from queue import Empty, Queue
import threading
import time
from typing import (
    Any,
    Final,
    Literal,
    NamedTuple,
    Optional,
    TypeVar,
    Union,
    cast,
    overload,
)
import warnings

import async_timeout
from grpc import RpcError, StatusCode
import msgpack

from bitfount import config
from bitfount.exceptions import BitfountError
from bitfount.federated.exceptions import (
    MessageHandlerNotFoundError,
    MessageRetrievalError,
    MessageTypeSpecificHandlerNotFoundError,
    TaskAbortError,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.transport.handlers import _PriorityHandler, _TemporaryHandler
from bitfount.federated.transport.message_service import (
    _BitfountMessage,
    _BitfountMessageType,
    _MessageEncryption,
    _MessageService,
    msgpackext_encode,
)
from bitfount.utils.concurrency_utils import (
    NO_POLLING,
    ThreadWithException,
    _synchronised,
    async_lock,
    asyncnullcontext,
    await_threading_event,
)

_logger = _get_federated_logger(__name__)

SyncHandler = Callable[[_BitfountMessage], None]
AsyncHandler = Callable[[_BitfountMessage], Awaitable[None]]
NonPriorityHandler = Union[SyncHandler, AsyncHandler]
Handler = Union[NonPriorityHandler, _PriorityHandler]

# Additional types for handler registration storage
ANY_MESSAGE: Final = "ANY_MESSAGE"
_ExtendedMessageTypes = Union[_BitfountMessageType, Literal["ANY_MESSAGE"]]
# Registered handlers can additionally be of type _TemporaryHandler
_RegisterHandler = Union[Handler, _TemporaryHandler]
_HandlersDict = dict[_RegisterHandler, Optional[asyncio.Lock]]


# Maximum queue size for early message queues
MAX_QUEUE_SIZE = 30


class _HandlerLockPair(NamedTuple):
    """Pair of handler and associated exclusivity lock."""

    handler: _RegisterHandler
    lock: Optional[asyncio.Lock]


class _HandlerRegistry:
    """Registry for message handlers.

    Thread-safe.
    """

    _registry: defaultdict[_ExtendedMessageTypes, _HandlersDict]
    _sync_lock: threading.RLock

    def __init__(
        self,
        handlers: Optional[
            Mapping[_BitfountMessageType, Union[Handler, Iterable[Handler]]]
        ] = None,
    ) -> None:
        self._registry: defaultdict[_ExtendedMessageTypes, _HandlersDict] = defaultdict(
            dict
        )
        if handlers:
            # Register supplied handlers
            for message_type, handlers_ in handlers.items():
                try:
                    # Assume iterable
                    for handler in cast(Iterable[Handler], handlers_):
                        # TODO: [BIT-1048] Revisit this and decide if _all_ messages
                        #       need to be exclusive in this way.
                        self.register_handler(message_type, handler, exclusive=True)
                except TypeError:
                    # Otherwise, register individual handler
                    self.register_handler(
                        message_type, cast(Handler, handlers_), exclusive=True
                    )

        # Lock for managing multithread operations
        self._sync_lock = threading.RLock()

    @_synchronised
    def register_handler(
        self,
        message_type: _ExtendedMessageTypes,
        handler: _RegisterHandler,
        exclusive: bool = True,
    ) -> None:
        """Registers a handler for a specific message type.

        Args:
            message_type: The message type to register the handler for.
            handler: The handler.
            exclusive: Whether only a single instance of the handler can be running
                at a given time.
        """
        if exclusive:
            if isinstance(handler, _PriorityHandler):
                # The exclusivity locking is handled within the priority handler
                # instead
                lock = None
                handler.set_exclusive()
            else:
                lock = asyncio.Lock()
        else:
            lock = None

        self._registry[message_type][handler] = lock

    @_synchronised
    def delete_handler(
        self,
        message_type: _ExtendedMessageTypes,
        handler: _RegisterHandler,
    ) -> None:
        """Deletes a handler associated with the message type."""
        self._registry[message_type].pop(handler, None)  # avoids KeyError

    @_synchronised
    def delete_all_handlers(self, message_type: _ExtendedMessageTypes) -> None:
        """Deletes all handlers for a specific message type."""
        self._registry[message_type].clear()

    @overload
    def get_handlers(
        self, message_type: _BitfountMessageType, with_locks: Literal[True]
    ) -> list[_HandlerLockPair]:
        """Gets all handlers for a specific message type."""
        ...

    @overload
    def get_handlers(
        self, message_type: _ExtendedMessageTypes, with_locks: Literal[False] = ...
    ) -> list[_RegisterHandler]:
        """Gets all handlers for a specific message type."""
        ...

    @_synchronised  # type: ignore[misc] # Reason: https://github.com/python/mypy/issues/12716 # noqa: E501
    def get_handlers(
        self, message_type: _ExtendedMessageTypes, with_locks: bool = False
    ) -> Union[list[_RegisterHandler], list[_HandlerLockPair]]:
        """Gets all handlers for a specific message type.

        If `with_locks` is True, returns a list of tuples of the handlers and their
        exclusivity locks if present.

        :::caution

        This does not retrieve the universal handlers. If you want to retrieve those
        as well you must call get_handlers(ANY_MESSAGE) and merge the two handler
        lists together.

        :::

        Args:
            message_type: The message type to retrieve the handlers for.
            with_locks: Whether to include handlers' exclusivity locks.

        Returns:
            Either a list of handlers or a list of handler-lock tuples.
        """
        handlers: Union[list[_RegisterHandler], list[_HandlerLockPair]]
        if not with_locks:
            handlers = list(self._registry[message_type].keys())
        else:
            handlers = [
                _HandlerLockPair(k, v) for k, v in self._registry[message_type].items()
            ]

        return handlers

    @_synchronised
    def get_lock(
        self,
        message_type: _ExtendedMessageTypes,
        handler: _RegisterHandler,
    ) -> Optional[asyncio.Lock]:
        """Returns the exclusivity lock for a given handler and message type.

        Returns:
            The exclusivity lock for the handler or None if no lock.

        Raises:
            KeyError: If handler is not associated with message type.
        """
        return self._registry[message_type][handler]


class _BaseMailbox:
    """The base mailbox class.

    Contains handlers and message service.

    Args:
        mailbox_id: the ID of the mailbox to monitor.
        message_service: underlying message service instance.
        handlers: an optional mapping of message types to handlers to initialise with.
    """

    def __init__(
        self,
        mailbox_id: str,
        message_service: _MessageService,
        handlers: Optional[
            Mapping[_BitfountMessageType, Union[Handler, Iterable[Handler]]]
        ] = None,
    ):
        self.mailbox_id = mailbox_id
        self.message_service = message_service

        self._handlers: _HandlerRegistry = _HandlerRegistry(handlers)

        # Only one call to _listen_for_messages() should be allowed at a time.
        # Otherwise we run the risk of messages being pulled off of the mailbox
        # by a listener that doesn't have the right handlers. Each mailbox should
        # only need one listener as it runs indefinitely.
        self._listening_lock = threading.Lock()

        # To enable a smart back-off when no handler is found before reattempting
        # we introduce an event that can monitor when new handlers are added. This
        # allows us to handle the situation where a response comes through faster
        # than the correct handler can be attached.
        self._new_handler_added_monitors_lock = threading.Lock()
        self._new_handler_added_monitors: set[threading.Event] = set()

        # Queue for each message type to store messages that arrive too early
        self._early_message_queues: dict[
            _BitfountMessageType, Queue[_BitfountMessage]
        ] = {}

    async def log(self, message: Mapping[str, object]) -> None:
        """Log message to remote task participant."""
        raise NotImplementedError

    def _setup_federated_logging(self) -> None:
        """Sets up federated logging."""
        raise NotImplementedError

    @contextmanager
    def listen(
        self, handler_dispatch_loop: Optional[AbstractEventLoop] = None
    ) -> Generator[threading.Thread, None, None]:
        """Starts the mailbox listening for messages in a separate thread.

        High-priority messages will be dispatched to a thread pool to be executed
        immediately. Low-priority messages will be dispatched to the event loop
        supplied to this method.

        Args:
            handler_dispatch_loop: The event loop to dispatch low-priority message
                handling to. If not supplied the running event loop from the calling
                thread is used.

        Yields:
            The thread that the mailbox listener is running in.

        Raises:
            BitfountError: If no handler_dispatch_loop is supplied and no event
                loop is running.
        """
        if not handler_dispatch_loop:
            try:
                handler_dispatch_loop = asyncio.get_running_loop()
            except RuntimeError as ex:
                raise BitfountError(
                    "Attempted to run mailbox listener without a running event loop."
                ) from ex

        # Create stop event, so we can notify the underlying thread to cease
        stop_event = threading.Event()

        mailbox_thread = ThreadWithException(
            target=self._start_in_own_thread,
            name=f"mailbox_listener_thread_{self.mailbox_id}",
            args=(handler_dispatch_loop, stop_event),
            daemon=True,
        )

        try:
            mailbox_thread.start()
            yield mailbox_thread
        finally:
            _logger.debug(f"Stopping mailbox listener ({self.mailbox_id})...")
            stop_event.set()

            if mailbox_thread.is_alive():
                stop_timeout = 15
                _logger.debug(
                    f"Waiting up to {stop_timeout} seconds"
                    f" for mailbox listener ({self.mailbox_id}) to stop..."
                )

                mailbox_thread.join(timeout=stop_timeout)

                if mailbox_thread.is_alive():
                    raise TimeoutError(
                        f"Mailbox listener ({self.mailbox_id}) did not stop in time."
                    )

            _logger.debug(f"Mailbox listener ({self.mailbox_id}) stopped.")

    def requeue_message(self, message: _BitfountMessage) -> None:
        """Requeue a message for later processing if it arrived prior to expectation."""
        # Create queue if it doesn't exist
        if message.message_type not in self._early_message_queues:
            self._early_message_queues[message.message_type] = Queue(
                maxsize=MAX_QUEUE_SIZE
            )

        message_queue = self._early_message_queues[message.message_type]

        # If queue is full, remove oldest message
        if message_queue.full():
            try:
                # queue.Queue retrieves messages in FIFO order, so calling
                # get_nowait will remove the oldest message first
                message_queue.get_nowait()
                _logger.warning(
                    f"Early message queue for {message.message_type} reached max size, "
                    f"discarding oldest message"
                )
            except Empty:
                # This shouldn't happen if queue is full, but handle it just in case
                _logger.error(
                    "Unexpected empty queue when trying to remove oldest message"
                )
                pass

        # Add the message to queue
        message_queue.put(message)

        _logger.debug(
            f"Requeueing {message.message_type} message from {message.sender}"
        )

    def _start_in_own_thread(
        self, handler_dispatch_loop: AbstractEventLoop, stop_event: threading.Event
    ) -> None:
        """Start listening for messages in new event loop.

        This is designed to be a thread target.
        """
        return asyncio.run(self._listen_for_messages(handler_dispatch_loop, stop_event))

    async def listen_indefinitely(
        self, handler_dispatch_loop: Optional[AbstractEventLoop] = None
    ) -> None:
        """Listen to a mailbox indefinitely without blocking the event loop.

        Does this by setting up a mailbox listener and dispatcher in a separate
        thread and then providing an async Future to await on. If the listener finishes
        or the caller of this function is cancelled then this will gracefully exit out,
        otherwise it allows the listener to run indefinitely.

        Args:
            handler_dispatch_loop: The event loop to dispatch low-priority message
                handling to. If not supplied the running event loop from the calling
                thread is used.

        Raises:
            BitfountError: If no handler_dispatch_loop is supplied and no event
                loop is running.
        """
        with self.listen(handler_dispatch_loop) as listen_thread:
            # We can't use the ThreadPoolExecutor context manager here because
            # of how the target thread functions and our intentions.
            #
            # If the process is cancelled then we want this function to exit out
            # which will cause the listen_thread to be gracefully shutdown as we
            # leave the self.listen() context manager. If we use the ThreadPoolExecutor
            # context manager it calls executor.shutdown(wait=True) which will cause
            # a deadlock as listen_thread.join() (and hence ThreadPoolExecutor)
            # won't finish until we're out of the self.listen() context manager,
            # but the self.listen() context manager won't finish until we leave
            # the ThreadPoolExecutor context manager.
            #
            # Instead, we need to manually call shutdown on the executor so that
            # it won't block, knowing that the thread in the executor will finish
            # soon because of the graceful shutdown mechanism in self.listen().
            executor = ThreadPoolExecutor(
                1, thread_name_prefix="listen_indefinitely_executor"
            )
            try:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(executor, listen_thread.join)
            finally:
                executor.shutdown(wait=False)
        return None

    async def _listen_for_messages(
        self,
        handler_dispatch_loop: AbstractEventLoop,
        stop_event: threading.Event,
    ) -> None:
        """Listens for messages on the target mailbox.

        Received messages are passed to the relevant handlers. If no relevant
        handlers are found, it will wait for up to
        `config.settings.handler_register_grace_period` for one to be registered.
        This avoids the situation of a response coming through faster than
        a handler can be registered. If not, it is passed to the default handler.
        """
        running_dispatch_tasks: set[
            Task[list[Union[ConcurrentFuture, _PriorityHandler]]]
        ] = set()
        done_dispatch_tasks: set[
            Task[list[Union[ConcurrentFuture, _PriorityHandler]]]
        ] = set()

        # Guarantee that only one listener is listening at a time.
        # We can set there to be NO_POLLING despite the dangers as
        # `_listen_for_messages()` should only be called once for each mailbox.
        async with async_lock(
            self._listening_lock,
            lock_name=f"listening_lock_{self.mailbox_id}",
            polling_timeout=NO_POLLING,
        ):
            try:
                async for message in self.message_service.poll_for_messages(
                    self.mailbox_id,
                    stop_event,
                ):
                    if stop_event.is_set():
                        _logger.info(
                            f"Stopping listening for messages"
                            f" in mailbox {self.mailbox_id}"
                        )
                        break

                    # Create dispatch task to run in background and handle
                    # maintaining a reference to it. Also add callbacks to
                    # move it between sets once it is done.
                    dispatch_task = asyncio.create_task(
                        self._dispatch_message_handlers(message, handler_dispatch_loop),
                        name=f"{message.message_type.name}_handler_dispatch_{self.mailbox_id}",
                    )
                    running_dispatch_tasks.add(dispatch_task)
                    dispatch_task.add_done_callback(running_dispatch_tasks.discard)
                    dispatch_task.add_done_callback(done_dispatch_tasks.add)

                    # Check on any "done" handler dispatch tasks
                    # TODO: [NO_TICKET: Idle thoughts rather than actionable]
                    #       What to do with the awaitables from the dispatch; do
                    #       they need weakref protection?
                    #       See: https://github.com/python/cpython/issues/88831
                    #       See: https://github.com/python/asyncio/issues/397#issuecomment-339014739  # noqa: E501
                    examined_tasks = set()
                    for task in done_dispatch_tasks:
                        _logger.debug(
                            f"Examining task in done_dispatch_tasks: {task.get_name()}"
                        )
                        # If there was an exception in the task dispatch,
                        # this will reraise it here.
                        try:
                            handler_results = task.result()
                        except Exception as e:
                            _logger.error(
                                f"Task dispatch exception in {task.get_name()}: {e}"
                            )
                            raise
                        for result in handler_results:
                            # If there was an exception in the actual handler,
                            # this will reraise it here
                            if isinstance(result, _PriorityHandler):
                                try:
                                    await result.result()
                                except Exception as e:
                                    _logger.error(
                                        f"Task handler exception in priority handler"
                                        f" {task.get_name()}: {e}"
                                    )
                                    raise
                            else:
                                try:
                                    result.result()
                                except Exception as e:
                                    _logger.error(
                                        f"Task handler exception in"
                                        f" low-priority handler {task.get_name()}: {e}"
                                    )
                                    raise

                        _logger.debug(
                            f"Dispatch task {task.get_name()} is done"
                            f" in mailbox {self.mailbox_id}"
                        )
                        examined_tasks.add(task)
                    # Remove examined tasks from the done set
                    done_dispatch_tasks -= examined_tasks

            # General message service issues to log out before failing.
            except RpcError as err:
                if err.code() == StatusCode.UNAVAILABLE:
                    _logger.warning("Message Service unavailable")
                if err.code() == StatusCode.UNAUTHENTICATED:
                    # This could be a temporary token expiry issue
                    _logger.info(
                        f"Authentication to read from '{self.mailbox_id}' failed"
                    )
                if err.code() == StatusCode.PERMISSION_DENIED:
                    _logger.warning(
                        f"You don't own a pod with the mailbox: {self.mailbox_id}. "
                        f"Ensure it exists on Bitfount Hub."
                    )
                if err.code() == StatusCode.FAILED_PRECONDITION:
                    _logger.debug(
                        f"No mailbox exists for '{self.mailbox_id}', "
                        f"ensure connect_pod() or send_task_requests() is called first."
                    )
                raise MessageRetrievalError(
                    f"An error occurred when trying to communicate"
                    f" with the messaging service: {err}"
                ) from err
            except TaskAbortError as tae:
                _logger.info(
                    f"Received TASK_ABORT request from handler. Aborting: {tae}"
                )
                raise
            except BaseException as e:
                # Want to ensure we log out whatever happened
                _logger.error(
                    f"Unexpected error in message retrieval: {e}", exc_info=True
                )
                raise
            finally:
                # Cancel outstanding dispatch tasks
                if len(running_dispatch_tasks) > 0:
                    cancelled_tasks: set[str] = set()

                    for task in running_dispatch_tasks:
                        task.cancel()
                        cancelled_tasks.add(task.get_name())

                    _logger.warning(
                        f"Message listener ended with running handler dispatches."
                        f" Cancelled: {', '.join(sorted(cancelled_tasks))}"
                    )

    async def _dispatch_message_handlers(
        self,
        message: _BitfountMessage,
        handler_dispatch_loop: AbstractEventLoop,
        timeout: int = config.settings.handler_register_grace_period,
    ) -> list[Union[ConcurrentFuture, _PriorityHandler]]:
        """Dispatch handlers for a message.

        Handles the retrieval and calling of handlers and the error state of no
        handlers being found.

        Returns:
            The created concurrent.futures.Futures in which the handler(s) are
            being run or, for high-priority handlers, the _PriorityHandler which
            the execution is tied to.
        """
        try:
            # [LOGGING-IMPROVEMENTS]
            if config.settings.logging.log_message_service:
                _logger.debug(
                    f"Attempting to dispatch handlers for"
                    f" {message.message_type} from {message.sender}"
                    f" in mailbox {self.mailbox_id}"
                )
            return await self._handle_message(message, handler_dispatch_loop, timeout)
        except MessageHandlerNotFoundError:
            self._default_handler(message)
            return []
        except MessageTypeSpecificHandlerNotFoundError as exc:
            _logger.warning(
                f"No specific handler could be found for message "
                f"("
                f"type: {message.message_type}; "
                f"sender {message.sender}; "
                f"recipient {message.recipient}"
                f"). "
                f"Message was passed to universal handlers only."
            )
            return exc.universal_dispatches

    async def _handle_message(
        self,
        message: _BitfountMessage,
        handler_dispatch_loop: AbstractEventLoop,
        timeout: int = config.settings.handler_register_grace_period,
    ) -> list[Union[ConcurrentFuture, _PriorityHandler]]:
        """Finds and runs handler(s) for the supplied message.

        The lower-priority handler(s) (whether async or not) are run within an
        asyncio event loop (the handler_dispatch_loop) to avoid blocking
        listen_for_messages().

        High-priority handlers are run directly (although in actuality in a thread)
        to avoid a blocking async task from stopping them being executed.

        Args:
            message: The message to handle.
            handler_dispatch_loop: The event loop to dispatch the handler execution
                to. Generally this will be the event loop in the main thread.
            timeout: The time to allow handlers to be registered for dispatch.

        Returns:
            The created concurrent.futures.Futures in which the handler(s) are
            being run or, for high-priority handlers, the _PriorityHandler which
            the execution is tied to.

        Raises:
            MessageHandlerNotFoundError: If no handler is registered for message
                type and one is not registered within the timeout.
            MessageTypeSpecificHandlerNotFoundError: If only universal handlers
                are found for the message type.
        """
        message_type: _BitfountMessageType = message.message_type
        awaitables: list[Union[ConcurrentFuture, _PriorityHandler]] = []
        handlers_specific_or_universal: list[bool] = []

        # We create an async wrapper around any low-priority handlers regardless
        # of if it's an async function or not to allow us to run it in the background
        # as a Task. This also allows us to access the asyncio.Locks.
        #
        # We need to use a separate method to return the wrapper (rather than defining
        # it in the for-loop) due to the late-binding of closures in Python.
        def _get_run_handler_wrapper(
            handler: NonPriorityHandler,
        ) -> Callable[[], Coroutine[None, None, None]]:
            async def _run_handler_wrapper() -> None:
                # Only a single handler instance (i.e. a call to a specific handler
                # function) should be running at a given time; this helps avoid
                # conflicting use of shared resources and ensures that tasks we
                # _want_ to block (such as worker running) do so.
                # TODO: [BIT-1048] Revisit this and decide if _all_ messages need to
                #       be exclusive in this way.
                message_lock: Optional[AbstractAsyncContextManager]
                try:
                    message_lock = self._handlers.get_lock(message_type, handler)
                except KeyError:
                    message_lock = None

                if message_lock is None:
                    message_lock = asyncnullcontext()

                async with message_lock:
                    # As this supports both sync and async handlers we need to
                    # process the result (which should be None, but could be a
                    # Coroutine returning None). As such, we comfortably call the
                    # handler and then simply await the result if needed.
                    # [LOGGING-IMPROVEMENTS]
                    if config.settings.logging.log_message_service:
                        _logger.debug(
                            f"Running low-priority handler"
                            f" for {message.message_type.name} message"
                            f" from {message.sender}"
                            f" in mailbox {self.mailbox_id}"
                        )
                    result = handler(message)
                    if inspect.isawaitable(result):
                        await result

            return _run_handler_wrapper

        # We retrieve and dispatch handlers up to the timeout limit from the async
        # generator. Any handlers already registered or that are registered in this
        # timeout window will be dispatched.
        async for handler, is_type_specific in self._retrieve_handlers(
            message_type, timeout
        ):
            _logger.debug(
                f"Handler retrieved for {message_type.name}"
                f" in mailbox {self.mailbox_id}"
            )
            handlers_specific_or_universal.append(is_type_specific)

            handler_callable: Handler
            if not isinstance(handler, _TemporaryHandler):
                handler_callable = handler
            else:
                handler_callable = handler.handler

            if not isinstance(handler_callable, _PriorityHandler):
                # For non-priority handlers we farm them out to the handler dispatch
                # event loop. We return the concurrent Future instance so the task
                # can be monitored later.
                wrapped_handler = _get_run_handler_wrapper(handler_callable)
                # [LOGGING-IMPROVEMENTS]
                if config.settings.logging.log_message_service:
                    _logger.debug(
                        f"Dispatching low priority handler for {message_type.name}"
                        f" to event loop (id={id(handler_dispatch_loop)})"
                        f" in mailbox {self.mailbox_id}"
                    )
                fut = asyncio.run_coroutine_threadsafe(
                    wrapped_handler(), handler_dispatch_loop
                )
                awaitables.append(fut)
            else:
                # The handler register locks aren't used for _PriorityHandler as
                # they get run in other threads and asyncio.Locks aren't thread
                # safe. The _PriorityHandler itself enforces locking.
                _logger.debug(
                    f"Dispatching high priority handler for {message_type.name}"
                    f" in mailbox {self.mailbox_id}"
                )
                handler_callable(message)
                awaitables.append(handler_callable)

            # As handler has been dispatched, we should delete it if it's a
            # temporary handler
            if isinstance(handler, _TemporaryHandler):
                _logger.debug(
                    f"Temporary handler {handler} has been dispatched for"
                    f" {message_type.name} in mailbox {self.mailbox_id}."
                    f" Deleting handler."
                )
                self._delete_handler(message_type, handler)

        # If no handlers were dispatched at all, raise exception
        if len(handlers_specific_or_universal) == 0:
            raise MessageHandlerNotFoundError(
                f"No handlers for message type {message_type.name}"
                f" were found in mailbox {self.mailbox_id}"
            )

        # If only universal handlers were found, raise exception
        if not any(handlers_specific_or_universal):
            exc = MessageTypeSpecificHandlerNotFoundError(
                f"Only universal handlers were found for message type"
                f" {message.message_type} in mailbox {self.mailbox_id}"
            )
            exc.universal_dispatches = awaitables
            raise exc

        return awaitables

    async def _retrieve_handlers(
        self,
        message_type: _BitfountMessageType,
        timeout: int = config.settings.handler_register_grace_period,
    ) -> AsyncIterator[tuple[_RegisterHandler, bool]]:
        """Yield the registered handler(s) for the given message type.

        Args:
            message_type: Message type to retrieve handler for.
            timeout: Number of seconds to wait before stopping handler retrieval.

        Yields:
            The handler(s) registered for the given message type within the timeout.
        """
        try:
            async with async_timeout.timeout(timeout):
                # We also pass the timeout through to
                # _retrieve_handlers_with_monitoring() as this allows us to put
                # bounds on how long the threads that wait on threading.Events can run.
                async for (
                    handler,
                    is_type_specific,
                ) in self._retrieve_handlers_with_monitoring(message_type, timeout):
                    yield handler, is_type_specific
        except asyncio.TimeoutError:
            # This is expected from the async_timeout.timeout() contextmanager
            return

    async def _retrieve_handlers_with_monitoring(
        self,
        message_type: _BitfountMessageType,
        timeout: float,
    ) -> AsyncIterator[tuple[_RegisterHandler, bool]]:
        """Yield handler(s) for message type as they become available.

        Stops yielding when a handler specific to that message type is available.

        Yields:
            A tuple of the handler and a boolean indicating whether the handler
            was specifically registered for that message type or was a universal
            handler.
        """
        # We give a small amount of buffer to ensure the Event waiting doesn't
        # finish before the async_timeout.timeout() in the parent method call.
        timeout *= 1.1
        start_time = time.time()

        # Allows us to avoid yielding a handler twice whilst allowing us to not
        # have to extract _only_ new handlers.
        yielded_handlers: set[_RegisterHandler] = set()

        # We create a monitor event before initial yielding to detect any handlers
        # that are added during that initial yielding.
        new_handler_added_monitor = threading.Event()
        # [LOGGING-IMPROVEMENTS]
        if config.settings.logging.log_message_service:
            _logger.debug(
                f"Trying to add new handler monitor for {message_type.name}"
                f" in mailbox {self.mailbox_id}"
            )
        async with async_lock(
            self._new_handler_added_monitors_lock, "new_handler_added_monitor_lock"
        ):
            # [LOGGING-IMPROVEMENTS]
            if config.settings.logging.log_message_service:
                _logger.debug(
                    f"Added new handler monitor for {message_type.name}"
                    f" in mailbox {self.mailbox_id}"
                )
            self._new_handler_added_monitors.add(new_handler_added_monitor)

        try:
            # Do an initial yield for any handlers that are already registered
            message_type_specific_handler_found = False
            handlers = self._get_relevant_handlers(message_type)
            if any([is_type_specific for handler, is_type_specific in handlers]):
                message_type_specific_handler_found = True

            for handler, is_type_specific in handlers:
                # [LOGGING-IMPROVEMENTS]
                if config.settings.logging.log_message_service:
                    _logger.debug(
                        f"Retrieved handler {handler} for {message_type.name}"
                        f" in mailbox {self.mailbox_id}"
                    )
                if handler not in yielded_handlers:
                    yielded_handlers.add(handler)
                    # [LOGGING-IMPROVEMENTS]
                    if config.settings.logging.log_message_service:
                        _logger.debug(
                            f"Yielding {'universal ' if not is_type_specific else ''}"
                            f"handler {handler} for {message_type.name}"
                            f" in mailbox {self.mailbox_id}"
                        )
                    yield handler, is_type_specific
                else:
                    # [LOGGING-IMPROVEMENTS]
                    if config.settings.logging.log_message_service:
                        _logger.debug(
                            f"Handler {handler} already dispatched for"
                            f" {message_type.name} in mailbox {self.mailbox_id}"
                        )

            # If we've already dispatched a message specific handler, return immediately
            if message_type_specific_handler_found:
                return

            # Now wait on any new handler registrations
            while True:
                # Get remaining timeout based on start time and current time
                remaining_timeout = timeout - (time.time() - start_time)

                # This condition should never happen due to timeout buffer
                if remaining_timeout < 0:
                    _logger.warning(
                        f"Timeout encountered whilst retrieving handlers"
                        f" for {message_type}."
                    )
                    return

                # Wait for a new handler to be registered. If one is already registered
                # since the last time this waiting was attempted, returns immediately.
                # As self._new_handler_added is a `threading.Event` we run the
                # waiting in a separate thread to not block the event loop.
                monitor_set: bool = await await_threading_event(
                    new_handler_added_monitor,
                    event_name=f"new_handler_added_monitor_{message_type}",
                    timeout=remaining_timeout,
                )

                # monitor_set should always be true at this point due to timeout
                # buffer and await_threading_event only returning when Event.wait()
                # is achieved.
                if monitor_set:
                    _logger.debug(
                        f"Detected new handler registration in {message_type.name}"
                        f" in mailbox {self.mailbox_id}"
                    )
                    # Reset monitor. No need to acquire lock here as even if
                    # _register_handler is mid-notify we'll either pick up the new
                    # handlers immediately or on the next loop.
                    new_handler_added_monitor.clear()

                    handlers = self._get_relevant_handlers(message_type)
                    if any(
                        [is_type_specific for handler, is_type_specific in handlers]
                    ):
                        message_type_specific_handler_found = True

                    for handler, is_type_specific in handlers:
                        _logger.debug(
                            f"Retrieved handler {handler} for {message_type.name}"
                            f" in mailbox {self.mailbox_id}"
                        )
                        if handler not in yielded_handlers:
                            yielded_handlers.add(handler)
                            _logger.debug(
                                f"Yielding "
                                f"{'universal ' if not is_type_specific else ''}"
                                f"handler {handler} for {message_type.name}"
                                f" in mailbox {self.mailbox_id}"
                            )
                            yield handler, is_type_specific
                        else:
                            _logger.debug(
                                f"Handler {handler} already dispatched "
                                f"for {message_type.name} in mailbox {self.mailbox_id}"
                            )

                    # If we've now dispatched a message specific handler,
                    # return immediately
                    if message_type_specific_handler_found:
                        return
                else:
                    _logger.warning(
                        f"Timeout encountered whilst waiting for notification"
                        f" of new handler registrations for {message_type}."
                    )
                    return
        finally:
            async with async_lock(
                self._new_handler_added_monitors_lock, "new_handler_added_monitor_lock"
            ):
                # [LOGGING-IMPROVEMENTS]
                if config.settings.logging.log_message_service:
                    _logger.debug(
                        f"Removing new handler monitor for {message_type.name}"
                        f" in mailbox {self.mailbox_id}"
                    )
                self._new_handler_added_monitors.remove(new_handler_added_monitor)

                # Set so any threads that are waiting on it are done; this is only
                # used in this method so doesn't matter that we've set it even if
                # it is not actually a "new handler added" event.
                new_handler_added_monitor.set()

    def _get_relevant_handlers(
        self, message_type: _BitfountMessageType
    ) -> list[tuple[_RegisterHandler, bool]]:
        """Retrieve all relevant handlers for a given message type.

        Includes both specific handlers and universal handlers.
        """
        handlers: list[tuple[_RegisterHandler, bool]] = []

        # Get any existing handlers for that specific message type
        handlers.extend(
            (handler, True) for handler in self._handlers.get_handlers(message_type)
        )

        # Get any existing universal handlers
        handlers.extend(
            (handler, False) for handler in self._handlers.get_handlers(ANY_MESSAGE)
        )

        return handlers

    def _register_handler(
        self, message_type: _ExtendedMessageTypes, handler: _RegisterHandler
    ) -> None:
        """Registers a handler for a specific message type."""
        self._handlers.register_handler(message_type, handler)

        # Note we've added a new handler, to allow backed off handler retrieval
        # to know.
        start_wait_time = time.time()
        with self._new_handler_added_monitors_lock:
            if config.settings.logging.multithreading_debug:
                _logger.debug(
                    f"Was waiting on _new_handler_added_monitors_lock in"
                    f" _register_handler() for {time.time() - start_wait_time:.4f}"
                    f" seconds."
                )

            if self._new_handler_added_monitors:
                message_type_name = (
                    message_type.name
                    if isinstance(message_type, _BitfountMessageType)
                    else message_type
                )
                for monitor in self._new_handler_added_monitors:
                    monitor.set()

                if config.settings.logging.multithreading_debug:
                    _logger.debug(
                        f"Notified {len(self._new_handler_added_monitors)} handlers"
                        f" in mailbox {self.mailbox_id}"
                        f" due to {message_type_name} handler {handler}"
                    )

        if config.settings.logging.multithreading_debug:
            _logger.debug(
                "Released _new_handler_added_monitors_lock in _register_handler()"
            )

    def register_handler(
        self,
        message_type: _BitfountMessageType,
        handler: Handler,
        high_priority: bool = False,
    ) -> Handler:
        """Registers a handler for a specific message type.

        If `high_priority` is true, the handler will be converted to a high priority
        handler. Note that only synchronous functions are compatible with
        `high_priority`.

        Returns:
            The registered handler, which may not be the same as the supplied handler.
        """
        handler = self._process_handler(handler, high_priority)

        # [LOGGING-IMPROVEMENTS]
        if config.settings.logging.log_message_service:
            _logger.debug(
                f"Registering handler {handler} for message type {message_type}"
                f" in mailbox {self.mailbox_id}"
            )
        self._register_handler(message_type, handler)

        # Process any early messages that were queued for this message type
        if (
            hasattr(self, "_early_message_queues")
            and message_type in self._early_message_queues
        ):
            self._process_early_messages(message_type, handler)

        # Notify any waiting monitors
        with self._new_handler_added_monitors_lock:
            for monitor in self._new_handler_added_monitors:
                monitor.set()

        return handler

    def _process_early_messages(
        self, message_type: _BitfountMessageType, handler: Handler
    ) -> None:
        """Process any early messages of the given type using the specified handler."""
        if message_type not in self._early_message_queues:
            _logger.debug(
                f"Message type {message_type} not found in early message queues."
            )
            return
        queue = self._early_message_queues[message_type]
        processed_count = 0
        # Process all messages currently in the queue
        while True:
            try:
                # Try to get a message from the queue without blocking
                # Queue.get_nowait() will raise Empty if the queue is empty
                # The messages are retrieved from get_nowait in FIFO order
                message = queue.get_nowait()
                processed_count += 1
                asyncio.create_task(self._process_message_async(message, handler))
            except Empty:
                break

        if processed_count > 0:
            _logger.debug(
                f"Processing {processed_count} queued message(s) for {message_type}"
            )

    async def _process_message_async(
        self, message: _BitfountMessage, handler: Handler
    ) -> None:
        """Process a single message asynchronously."""
        try:
            # Call the handler directly
            result = handler(message)
            if inspect.isawaitable(result):
                await result
        except Exception as e:
            _logger.error(f"Error processing early message: {e}", exc_info=True)

    def register_universal_handler(
        self, handler: Handler, high_priority: bool = False
    ) -> Handler:
        """Registers a universal handler, that will also be called for all messages.

        :::caution

        Universal handlers are run IN ADDITION to any other handlers for that message
        type. If no non-universal handlers are registered for that message type,
        the default handler will be used instead.

        :::

        If `high_priority` is true, the handler will be converted to a high priority
        handler. Note that only synchronous functions are compatible with
        `high_priority`.

        Returns:
            The registered handler, which may not be the same as the supplied handler.
        """
        handler = self._process_handler(handler, high_priority)

        _logger.debug(
            f"Registering universal handler {handler} in mailbox {self.mailbox_id}"
        )
        self._register_handler(ANY_MESSAGE, handler)

        return handler

    def register_temp_handler(
        self,
        message_type: _BitfountMessageType,
        handler: Handler,
        high_priority: bool = False,
    ) -> _TemporaryHandler:
        """Registers a handler that will be deleted after it is called.

        If `high_priority` is true, the handler will be converted to a high priority
        handler. Note that only synchronous functions are compatible with
        `high_priority`.

        Returns:
            The registered temporary handler.
        """
        handler = self._process_handler(handler, high_priority)
        temp_handler = self._make_temp_handler(handler)

        _logger.debug(
            f"Registering temporary handler {handler} for message type {message_type}"
            f" in mailbox {self.mailbox_id}"
        )
        self._register_handler(message_type, temp_handler)

        return temp_handler

    @staticmethod
    def _make_temp_handler(handler: Handler) -> _TemporaryHandler:
        """Wraps handler so that it will be deleted after it is called."""
        return _TemporaryHandler(handler)

    def _delete_handler(
        self, message_type: _BitfountMessageType, handler: _RegisterHandler
    ) -> None:
        """Delete a handler from the registry."""
        self._handlers.delete_handler(message_type, handler)

    def delete_handler(
        self,
        message_type: _BitfountMessageType,
        handler: Optional[_RegisterHandler] = None,
    ) -> None:
        """Deletes a handler associated with the message type.

        If a specific handler is not provided, deletes all handlers for that
        message type.
        """
        if not handler:
            warnings.warn(
                "In future versions, delete_handler will require a specific handler"
                " instance to be provided. Please switch to delete_all_handlers"
                " instead to maintain previous functionality.",
                DeprecationWarning,
            )
            self.delete_all_handlers(message_type)
        else:
            _logger.debug(
                f"Deleting handler for message type: {message_type}"
                f" in mailbox {self.mailbox_id}"
            )
            self._delete_handler(message_type, handler)

    def delete_all_handlers(self, message_type: _BitfountMessageType) -> None:
        """Deletes all handlers for a specific message type."""
        _logger.debug(
            f"Deleting all handlers for message type: {message_type}"
            f" in mailbox {self.mailbox_id}"
        )
        self._handlers.delete_all_handlers(message_type)

    @staticmethod
    def _default_handler(message: _BitfountMessage) -> None:
        """Simple default handler that logs the message details.

        If this is called it is because we have received a message type that we
        were not expecting and do not know how to handle. We log out pertinent
        (non-private) details.
        """
        _logger.error(
            f"Received unexpected message "
            f"("
            f"type: {message.message_type}; "
            f"sender {message.sender}; "
            f"recipient {message.recipient}"
            f"). "
            f"Message was not handled."
        )

    @staticmethod
    def _process_handler(handler: Handler, high_priority: bool) -> Handler:
        """Process the supplied handler given handler configuration.

        Handles conversion into high priority handlers as needed and also does
        type-checking for supported handler types.

        Return:
            The processed (and hence potentially changed) handler.
        """
        if high_priority:
            if isinstance(handler, _PriorityHandler):
                # Already correct, just return
                return handler
            else:
                # [LOGGING-IMPROVEMENTS]
                if config.settings.logging.log_message_service:
                    _logger.debug(
                        f"Converting handler {handler} to high priority handler."
                    )
                return _PriorityHandler(handler)
        else:
            if isinstance(handler, _PriorityHandler):
                _logger.warning(
                    "A priority handler has been provided but high_priority not set."
                    " Treating as though high_priority is True."
                )
                return handler
            else:
                return handler


async def _send_aes_encrypted_message(
    message: Any,
    aes_encryption_key: bytes,
    message_service: _MessageService,
    **kwargs: Any,
) -> None:
    """Packs message, encrypts it and sends it.

    Args:
        message: The message to be sent. Must support serialisation via msgpack.
        aes_encryption_key: Key used to encrypt message.
        message_service: The MessageService used to send the message.
        **kwargs: Keyword arguments passed to BitfountMessage constructor.
    """
    body = msgpack.dumps(message, default=msgpackext_encode)
    message_body = _MessageEncryption.encrypt_outgoing_message(body, aes_encryption_key)

    await message_service.send_message(
        _BitfountMessage(body=message_body, **kwargs),
        already_packed=True,
    )


# type variable for return type below.
_R = TypeVar("_R")


async def _run_func_and_listen_to_mailbox(
    run_func: Coroutine[None, None, _R],
    mailbox: _BaseMailbox,
) -> _R:
    """Runs an async function and listens for messages simultaneously.

    This function allows any exceptions that occur in the run function to be properly
    propagated to the calling code whilst ensuring that the listener or run function
    are correctly shutdown in such a situation.

    It also ensures that the mailbox listener is not run for longer than the lifetime
    of run_func.

    Args:
        run_func: The function to run that will be needing received messages.
        mailbox: The mailbox to use to listen for messages.

    Returns:
         The return value of run_func.
    """
    with mailbox.listen() as mailbox_listener:
        loop = asyncio.get_running_loop()
        executor = ThreadPoolExecutor(
            1, thread_name_prefix="run_func_and_listen_executor"
        )
        try:
            # Create a separate task for the wrapped function call
            run_task: Task[_R] = asyncio.create_task(run_func)

            # Create future to monitor mailbox listener
            fut: AsyncFuture[None] = loop.run_in_executor(
                executor, mailbox_listener.join
            )

            aws: list[Awaitable] = [run_task, fut]
            done, _ = await asyncio.wait(aws, return_when=FIRST_COMPLETED)

            if run_task in done:
                # Task has completed, return the result (or raise an exception)
                _logger.debug(f"Task {run_task} is done")
                return run_task.result()
            else:  # run_task not in done
                # The mailbox listener has finished prematurely (likely due to an
                # error).
                exc = fut.exception()
                error_msg = (
                    f"Mailbox has finished listening before the target task"
                    f" ({run_task}) finished running."
                )

                if exc:
                    # If an exception occurred in the mailbox listener, log information
                    # about it and then throw the exception into the run_task to handle
                    error_msg += (
                        f" Exception was: {exc}. This has been passed to the task"
                        f" to handle."
                    )
                    _logger.error(error_msg)
                    _logger.exception(exc)

                    # TODO: [BIT-3718] This approach to propagating the exception
                    #       from the mailbox to the task is not really supported
                    #       in Python; whilst it _will_ cause the task to raise
                    #       the exception it will likely cause RuntimeErrors related
                    #       to the coroutine being awaited multiple times.
                    #       The issue is that throwing an exception into the underlying
                    #       coroutine does nothing to mark the wrapping Task as
                    #       cancelled/done and so it can continue to attempt to
                    #       use the coroutine without knowing it has already had
                    #       an exception raised/been awaited.
                    # Pass to task to handle then await on task
                    cast(Coroutine, run_task.get_coro()).throw(exc)
                    return await run_task
                else:
                    # Otherwise, log that something went wrong and wait on the run_task
                    # to "finish"
                    _logger.error(error_msg)
                    return await run_task
        except TaskAbortError as e:
            _logger.error("Modeller task was aborted: %s", str(e))
            return await run_task
        finally:
            executor.shutdown(wait=False)
