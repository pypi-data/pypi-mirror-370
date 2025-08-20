"""Federated logging."""

from __future__ import annotations

import asyncio
from asyncio import Task
import logging
from typing import TYPE_CHECKING, Any

from bitfount.utils.concurrency_utils import ThreadWithException

if TYPE_CHECKING:
    from bitfount.federated.transport.base_transport import _BaseMailbox

# asyncio event loop only keeps weak references to tasks so need to keep strong
# references so they don't get garbage collected.
_background_logging_tasks: set[Task] = set()


# Dynamic base class error below ignored as this is the recommended way to subclass
# logging.Logger as specified in the documentation:
# https://docs.python.org/3/library/logging.html#logging.getLoggerClass
class _FederatedLogger(logging.getLoggerClass()):  # type: ignore[misc] # Reason: see comment # noqa: E501
    """Federated Logger with extra federated methods."""

    def __init__(self, name: str) -> None:
        super().__init__(name)

    def federated_debug(self, msg: object, *args: Any, **kwargs: Any) -> None:
        """Calls `self.debug` under the hood and sets the `federated` attribute."""
        self.debug(
            msg,
            *args,
            **kwargs,
            # Set stack level to 2 so the record is made from
            # the _caller_ of this method
            stacklevel=2,
            extra={"federated": True},
        )

    def federated_info(self, msg: object, *args: Any, **kwargs: Any) -> None:
        """Calls `self.info` under the hood and sets the `federated` attribute."""
        self.info(
            msg,
            *args,
            **kwargs,
            # Set stack level to 2 so the record is made from
            # the _caller_ of this method
            stacklevel=2,
            extra={"federated": True},
        )

    def federated_warning(self, msg: object, *args: Any, **kwargs: Any) -> None:
        """Calls `self.warning` under the hood and sets the `federated` attribute."""
        self.warning(
            msg,
            *args,
            **kwargs,
            # Set stack level to 2 so the record is made from
            # the _caller_ of this method
            stacklevel=2,
            extra={"federated": True},
        )

    def federated_error(self, msg: object, *args: Any, **kwargs: Any) -> None:
        """Calls `self.error` under the hood and sets the `federated` attribute."""
        self.error(
            msg,
            *args,
            **kwargs,
            # Set stack level to 2 so the record is made from
            # the _caller_ of this method
            stacklevel=2,
            extra={"federated": True},
        )

    def federated_critical(self, msg: object, *args: Any, **kwargs: Any) -> None:
        """Calls `self.critical` under the hood and sets the `federated` attribute."""
        self.critical(
            msg,
            *args,
            **kwargs,
            # Set stack level to 2 so the record is made from
            # the _caller_ of this method
            stacklevel=2,
            extra={"federated": True},
        )


class _MailboxHandler(logging.Handler):
    """A class which sends records to a GRPC mailbox.

    Args:
        mailbox (BaseMailbox): the recipient of emitted logs
    """

    def __init__(self, mailbox: _BaseMailbox):
        super().__init__()
        self.mailbox = mailbox

    def emit(self, record: logging.LogRecord) -> None:
        """Emits a record to the designated mailbox.

        Args:
            record (logging.LogRecord): the record to be emitted
        """
        try:
            # Because emit() is overriding an inherited method, it cannot be async
            # def itself. However, the call to BaseMailbox _has_ to be, due to the
            # underlying async gRPC interaction. So we have to wrap this in
            # create_task() to make it async.
            # We should have an event loop by this point, as this is only accessed at
            # runtime and we have the main event loop running everything else.
            # If we don't, Handler.handleError() will deal with the raised exception.

            # Replace msg object with str version to avoid serialization issues.
            record.msg = record.getMessage()

            # Drop exc_info as this is currently unsupported and will result in
            # an exception
            # TODO: [BIT-1619] [BIT-2260] Add support for federated exception logging.
            record.exc_info = None

            if record.levelno >= logging.ERROR:
                # Block flow until high priority messages have completed.
                # As can't run second event loop in the same thread we farm the
                # priority logging out to a second thread.
                message_send_thread = ThreadWithException(
                    target=asyncio.run,
                    args=(self.mailbox.log(record.__dict__),),
                    daemon=True,
                    name="message_send_thread",
                )
                message_send_thread.start()
                message_send_thread.join()
            else:
                # Ensure strong reference kept to task so doesn't get garbage
                # collected, but also that it's still "fire-and-forget".
                logging_task = asyncio.create_task(
                    self.mailbox.log(record.__dict__), name="Federated Log Sending"
                )
                _background_logging_tasks.add(logging_task)
                logging_task.add_done_callback(_background_logging_tasks.discard)
        except Exception:
            self.handleError(record)


class _FederatedLogFilter(logging.Filter):
    """Filters logs for Federated Logging."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Only logs with the `federated` attribute set to True are passed through.

        Args:
            record (logging.LogRecord): the record to be filtered

        Returns:
            bool: whether or not the record passses through the filter to the handler(s)
        """
        if hasattr(record, "federated"):
            # Ignoring type error since we have already checked for the presence of
            # `federated` attribute
            if record.federated:
                return True
        return False


def _federate_logger(mailbox: _BaseMailbox) -> None:
    """Adds a MailboxHandler to the `bitfount.federated` logger.

    Any existing mailbox handlers are first removed so that the handler and mailbox is
    updated prior to each task. This ensures that we don't attempt to log to a mailbox
    from an older task. The MailboxHandler is then attached with a filter which filters
    only for log messages that have the `federated` attribute set to True. We are
    federating the logger at the package level so that all loggers below it within the
    `bitfount.federated` package will also be federated.

    Args:
        mailbox (BaseMailbox): the mailbox used to create the mailbox handler
    """
    logger = _get_federated_logger("bitfount.federated")

    for handler in logger.handlers:
        if isinstance(handler, _MailboxHandler):
            logger.removeHandler(handler)

    mailbox_handler = _MailboxHandler(mailbox)
    mailbox_handler.setLevel(logging.DEBUG)
    log_filter = _FederatedLogFilter()
    mailbox_handler.addFilter(log_filter)
    logger.addHandler(mailbox_handler)


def _get_federated_logger(name: str) -> _FederatedLogger:
    """Returns logger with federated logging methods attached.

    This function should be used to retrieve the module level logger in any module in
    the `bitfount.federated` package where we want to send federated logs. We reset the
    logger class at the end of the function to ensure that subsequent calls to
    `logging.getLogger()` in other parts of the code don't return a federated logger.

    Returns:
        FederatedLogger: a regular logger but with extra methods for federated logging.
            It is important to note that these federated methods will not send messages
            in a federated way unless `federate_logger` has been called already.

    Raises:
        ValueError: if a federated logger is requested for a module/subpackage outside
            the `bitfount.federated` package
    """
    if not name.startswith("bitfount.federated"):
        raise ValueError("This can only be used from the federated package.")
    logging_class = logging.getLoggerClass()
    # Use the global logging lock for thread safety
    logging._acquireLock()  # type: ignore[attr-defined] # Reason: known private attribute, see comment # noqa: E501
    try:
        logging.setLoggerClass(_FederatedLogger)
        logger = logging.getLogger(name)
        if not isinstance(logger, _FederatedLogger):
            raise TypeError(
                f"logger for {name} is not federated; did a logger with this name"
                f" already exist?"
            )
        return logger
    finally:
        logging.setLoggerClass(logging_class)
        logging._releaseLock()  # type: ignore[attr-defined] # Reason: known private attribute # noqa: E501
