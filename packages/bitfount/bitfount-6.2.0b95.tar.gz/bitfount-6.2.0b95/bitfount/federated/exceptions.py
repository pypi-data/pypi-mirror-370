"""Custom exceptions for the federated package."""

from __future__ import annotations

from concurrent.futures import Future as ConcurrentFuture
from typing import TYPE_CHECKING, Optional, Union

# Compatibility shims for encryption exceptions moved to bitfount.encryption.exceptions
# These are re-exported for backward compatibility with external code
from bitfount.encryption.exceptions import (  # noqa: F401
    DecryptError,
    EncryptionError,
    RSAKeyError,
)
from bitfount.exceptions import BitfountError
from bitfount.federated.transport.types import Reason

if TYPE_CHECKING:
    from bitfount.federated.transport.handlers import _PriorityHandler


class BitfountTaskStartError(BitfountError, RuntimeError):
    """Raised when an issue occurs whilst trying to start a task with pods."""

    pass


class AlgorithmError(BitfountError):
    """Error raised during a worker-side algorithm run."""

    pass


class ProtocolError(BitfountError):
    """Error raised during protocol run."""

    pass


class TaskAbortError(BitfountError):
    """Error raised when a TASK_ABORT is received from a pod."""

    def __init__(
        self,
        error_message: str,
        reason: Optional[Reason] = None,
        message_already_sent: bool = False,
    ):
        """Initialises TaskAbortError.

        Args:
            error_message: Describes the reason for the task being aborted.
            reason: Machine-reasable reason for the task being aborted.
            message_already_sent: Whether a message has already been sent to the
                "other side" (i.e. modeller or pod) of the task run, or whether
                a TASK_ABORT message still needs to be sent.
        """
        super().__init__(error_message)
        self.reason = reason
        self.message_already_sent = message_already_sent


class PodSchemaMismatchError(BitfountError):
    """Error raised when a pod schema does not match the task schema."""

    pass


class MessageHandlerDispatchError(BitfountError):
    """Error raised when there is a problem dispatching messages to handlers."""

    pass


class MessageHandlerNotFoundError(MessageHandlerDispatchError):
    """Error raised when no registered message handler can be found."""

    pass


class MessageTypeSpecificHandlerNotFoundError(MessageHandlerDispatchError):
    """Error raised when no non-universal registered message handler can be found."""

    universal_dispatches: list[Union[ConcurrentFuture, _PriorityHandler]]


class MessageRetrievalError(BitfountError, RuntimeError):
    """Raised when an error occurs whilst retrieving a message from message service."""

    pass


class PodConnectFailedError(BitfountError, TypeError):
    """The message service has not correctly connected the pod."""

    pass


class PodRegistrationError(BitfountError):
    """Error related to registering a Pod with BitfountHub."""

    pass


class PodResponseError(BitfountError):
    """Pod rejected or failed to respond to a task request."""

    pass


class PodNameError(BitfountError):
    """Error related to given Pod name."""

    pass


class PrivateSqlError(BitfountError):
    """An exception for any issues relating to the PrivateSQL algorithm."""

    pass


class AggregatorError(BitfountError, ValueError):
    """Error related to Aggregator classes."""

    pass


class DPParameterError(BitfountError):
    """Error if any of given dp params are not allowed."""

    pass


class DPNotAppliedError(BitfountError):
    """Error if DP could not be applied to a model."""

    pass


class NoNewDataError(BitfountError):
    """Error when run_on_new_data_only is True but no new records are found."""

    pass


class NoDataError(BitfountError):
    """Error when no data is found."""

    pass


class DataProcessingError(BitfountError):
    """Error related to data processing.

    This is distinct from DataSourceError, as it is related to later processing
    of the data. Raised by the ophthalmology algorithms.
    """

    pass


class BatchResilienceAbortError(BitfountError):
    """Error raised when batch resilience system aborts due to consecutive failures.

    Args:
        error_message: Description of why the task was aborted.
        consecutive_failures: Number of consecutive failures that triggered abort.
        failed_batches: Dictionary mapping batch numbers to their exceptions.
    """

    def __init__(
        self,
        error_message: str,
        consecutive_failures: Optional[int] = None,
        failed_batches: Optional[dict[int, Exception]] = None,
    ):
        super().__init__(error_message)
        self.consecutive_failures = consecutive_failures
        self.failed_batches = failed_batches or {}
