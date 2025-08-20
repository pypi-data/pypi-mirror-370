"""Helper module for federated transport."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Collection, Mapping, Sequence
from functools import wraps
import logging
from statistics import mean
from types import MethodType
from typing import Any, Final, Optional, Set, Tuple, TypeVar, cast

from grpc import (
    ChannelConnectivity,
    RpcError,
    StatusCode,
    aio,
    ssl_channel_credentials,
)

from bitfount import config
from bitfount.federated.transport import _MESSAGE_SERVICE_GRPC_OPTIONS
from bitfount.federated.transport.config import MessageServiceConfig
from bitfount.federated.transport.exceptions import BitfountMessageServiceError
from bitfount.federated.transport.protos.messages_pb2 import (
    Acknowledgement,
    BitfountMessage,
    BitfountTasks,
    BlobStorageData,
    CommunicationDetails,
    DiagnosticsParameters,
    LargeStorageRequest,
    PodData,
    ServiceDiagnostics,
    SuccessResponse,
    TaskTransferMetadata,
    TaskTransferRequests,
)
from bitfount.federated.transport.protos.messages_pb2_grpc import MessageServiceStub
from bitfount.utils.retry_utils import DEFAULT_BACKOFF_FACTOR, compute_backoff

_logger = logging.getLogger(__name__)


def _average_training_metrics(
    validation_metrics: Sequence[Mapping[str, str]],
) -> dict[str, float]:
    """Average training metrics from each worker."""
    averaged_metrics = dict()
    if validation_metrics:
        # What should happen if one (or all) of the pods does not respond in time?
        for metric_key in validation_metrics[0]:
            averaged_metrics[metric_key] = mean(
                float(worker_metrics[metric_key])
                for worker_metrics in validation_metrics
            )
    return averaged_metrics


_RETRY_STATUS_CODES: Final[Set[StatusCode]] = {
    sc
    for sc in StatusCode
    if sc
    not in (
        # because this means it worked
        StatusCode.OK,
        # because this means it doesn't need to be done again
        StatusCode.ALREADY_EXISTS,
        # because this means it will never work
        StatusCode.UNIMPLEMENTED,
    )
}
_DEFAULT_TIMEOUT: Final = 20.0
_DEFAULT_MAX_RETRIES: Final[int] = config.settings.message_service_retries

_CONNECTIVITY_STATUS_CODES: Final[Set[StatusCode]] = {
    StatusCode.UNAVAILABLE,
    StatusCode.DEADLINE_EXCEEDED,
}
# Assuming a _DEFAULT_MAX_BACKOFF of 60 seconds and a _DEFAULT_TIMEOUT of 20,
# each retry after the 9th will take 1:20 minutes to complete.
# So this value (default 270) means about 6 hours of retries.
DEFAULT_MANY_RETRIES: Final[int] = config.settings.message_service_many_retries


class MessageServiceStubWrapper(MessageServiceStub):
    """Wrapper around the MessageServiceStub to allow channel updates.

    We need this to provide an indirection to the underlying MessageServiceStub
    that doesn't allow the channel to be mutated.
    """

    _actual: MessageServiceStub
    _channel: aio.Channel
    _config: MessageServiceConfig

    def __init__(self, config: MessageServiceConfig) -> None:
        self._config = config
        self.reset_channel()

    def reset_channel(self) -> None:
        """Reset the underlying GRPC channel."""
        self._channel = self._create_channel()
        self._actual = MessageServiceStub(self._channel)

    def get_channel_state(self) -> ChannelConnectivity:
        """Get the state of the underlying GRPC channel."""
        return self._channel.get_state()

    def _create_channel(self) -> aio.Channel:
        if self._config.tls:
            # This is an async secure_channel
            return aio.secure_channel(
                f"{self._config.url}:{self._config.port}",
                ssl_channel_credentials(),
                options=_MESSAGE_SERVICE_GRPC_OPTIONS,
            )
        else:
            # This is an async insecure_channel
            return aio.insecure_channel(
                f"{self._config.url}:{self._config.port}",
                options=_MESSAGE_SERVICE_GRPC_OPTIONS,
            )

    async def atomic_get_and_ack(
        self,
        metadata: list[tuple[str, str]],
        mailbox_id: str,
        timeout: Optional[float] = None,
    ) -> BitfountMessage:
        """Get and acknowledge gRPC message in one atomic operation.

        Will either return the retrieved and ACKed message or raise an RpcError
        if something goes wrong at either stage or if there is no message available.
        """
        # [LOGGING-IMPROVEMENTS]
        if config.settings.logging.log_message_service:
            _logger.debug(f"Attempting message retrieval from {mailbox_id}")
        message = await self.GetBitfountMessage(
            # Only mailboxId is needed here because that's all that's used on the
            # message service side. Despite the other args not being "optional"
            # we can let the default values be used.
            CommunicationDetails(mailboxId=mailbox_id),
            metadata=metadata,
            timeout=timeout,
        )
        # [LOGGING-IMPROVEMENTS]
        if config.settings.logging.log_message_service:
            _logger.debug(f"Message retrieved (id={id(message)})")

        delete_mailbox = False
        if message.messageType == BitfountMessage.TASK_COMPLETE:
            _logger.debug(
                "Received a TASK_COMPLETE message - asking message service to tidy up."
            )
            delete_mailbox = True

        # [LOGGING-IMPROVEMENTS]
        if config.settings.logging.log_message_service:
            _logger.debug(f"Attempting to ACK message (id={id(message)})")
        await self.AcknowledgeMessage(
            Acknowledgement(
                mailboxId=mailbox_id,
                receiptHandle=message.receiptHandle,
                deleteMailbox=delete_mailbox,
            ),
            metadata=metadata,
            timeout=timeout,
        )
        # [LOGGING-IMPROVEMENTS]
        if config.settings.logging.log_message_service:
            _logger.debug(f"ACKed message (id={id(message)})")

        return message

    async def PodConnect(
        self,
        data: PodData,
        /,
        *,
        metadata: Sequence[Tuple[str, Any]],
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> SuccessResponse:
        """PodConnect GRPC Endpoint."""
        return await self._actual.PodConnect(data, metadata=metadata, timeout=timeout)

    async def SetupTask(
        self,
        data: TaskTransferRequests,
        /,
        *,
        metadata: Sequence[Tuple[str, Any]],
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> TaskTransferMetadata:
        """SetupTask GRPC Endpoint."""
        return await self._actual.SetupTask(data, metadata=metadata, timeout=timeout)

    async def InitiateTask(
        self,
        data: BitfountTasks,
        /,
        *,
        metadata: Sequence[Tuple[str, Any]],
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> CommunicationDetails:
        """InitiateTask GRPC Endpoint."""
        return await self._actual.InitiateTask(data, metadata=metadata, timeout=timeout)

    async def AcknowledgeMessage(
        self,
        data: Acknowledgement,
        /,
        *,
        metadata: Sequence[Tuple[str, Any]],
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> SuccessResponse:
        """AcknowledgeMessage GRPC Endpoint."""
        return await self._actual.AcknowledgeMessage(
            data, metadata=metadata, timeout=timeout
        )

    async def GetBitfountMessage(
        self,
        data: CommunicationDetails,
        /,
        *,
        metadata: Sequence[Tuple[str, Any]],
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> BitfountMessage:
        """GetBitfountMessage GRPC Endpoint."""
        return await self._actual.GetBitfountMessage(
            data, metadata=metadata, timeout=timeout
        )

    async def SendBitfountMessage(
        self,
        data: BitfountMessage,
        /,
        *,
        metadata: Sequence[Tuple[str, Any]],
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> SuccessResponse:
        """SendBitfountMessage GRPC Endpoint."""
        return await self._actual.SendBitfountMessage(
            data, metadata=metadata, timeout=timeout
        )

    async def GetLargeObjectStorage(
        self,
        data: LargeStorageRequest,
        /,
        *,
        metadata: Sequence[Tuple[str, Any]],
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> BlobStorageData:
        """GetLargeObjectStorage GRPC Endpoint."""
        return await self._actual.GetLargeObjectStorage(
            data, metadata=metadata, timeout=timeout
        )

    async def Diagnostics(
        self,
        data: DiagnosticsParameters,
        /,
        *,
        metadata: Sequence[Tuple[str, Any]],
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> ServiceDiagnostics:
        """Diagnostics GRPC Endpoint."""
        return await self._actual.Diagnostics(data, metadata=metadata, timeout=timeout)


# These should be replaced with ParamSpec versions once
# https://github.com/python/mypy/issues/11855 is resolved
_F = TypeVar("_F", bound=Callable[..., Awaitable[Any]])


def _auto_retry_grpc(
    original_rpc_func: _F,
    *,
    max_retries: int = _DEFAULT_MAX_RETRIES,
    backoff_factor: int = DEFAULT_BACKOFF_FACTOR,
    additional_no_retry_status_codes: Optional[Collection[StatusCode]] = None,
    connectivity_retries: int = _DEFAULT_MAX_RETRIES,
) -> _F:
    """Applies automatic retries to gRPC calls when encountering specific errors.

    Wraps the target gRPC call in a retry mechanism which will reattempt
    the call if a retryable gRPC error response is received.

    Utilises an exponential backoff to avoid flooding the request and to give
    time for the issue to resolve itself.

    Is primarily meant to wrap methods of MessageServiceStubWrapper so that
    broken GRPC channels can be appropriately replaced.
    """
    if additional_no_retry_status_codes:
        _additional_no_retry_status_codes = set(additional_no_retry_status_codes)
    else:
        _additional_no_retry_status_codes = set()

    all_retry_status_codes = _RETRY_STATUS_CODES.union(_CONNECTIVITY_STATUS_CODES)

    if isinstance(original_rpc_func, MethodType) and isinstance(
        original_rpc_func.__self__, MessageServiceStubWrapper
    ):
        mutable_container = original_rpc_func.__self__
        name = original_rpc_func.__name__
    else:
        _logger.warning(
            (
                "_auto_retry_grpc used with function that is not a method of "
                "MessageServiceStubWrapper - won't be able to recover from a broken"
                "GRPC channel"
            )
        )
        mutable_container = None
        name = None

    def _decorate(grpc_func: _F) -> _F:
        """Apply decoration to target request function."""

        @wraps(grpc_func)
        async def _wrapped_async_grpc_func(*args: Any, **kwargs: Any) -> Any:
            """Wraps target gRPC function in retry capability.

            Adds automatic retry, backoff, and logging.
            """
            # Set default timeout if one not provided
            timeout = kwargs.get("timeout", None)
            if timeout is None:
                # [LOGGING-IMPROVEMENTS]
                if config.settings.logging.log_message_service:
                    _logger.debug(
                        f"No gRPC timeout provided,"
                        f" setting to default timeout ({_DEFAULT_TIMEOUT}s)"
                    )
                kwargs["timeout"] = _DEFAULT_TIMEOUT

            retry_count = 0
            local_max_retries = max_retries

            while retry_count <= local_max_retries:
                # Attempt to make wrapped call and handle if it doesn't work
                # as expected
                try:
                    return await grpc_func(*args, **kwargs)
                except RpcError as ex:
                    status_code: StatusCode = ex.code()

                    # If the status code indicates lack of internet connection,
                    # consider a specific number of retries
                    connectivity_message = ""
                    if status_code in _CONNECTIVITY_STATUS_CODES:
                        if local_max_retries != connectivity_retries:
                            _logger.warning(
                                f"Encountered a connectivity issue"
                                f" ({status_code.name});"
                                f" setting retries to {connectivity_retries}"
                            )
                            local_max_retries = connectivity_retries

                        if mutable_container is not None:
                            state = mutable_container.get_channel_state()
                            if (
                                state != ChannelConnectivity.READY
                                and state != ChannelConnectivity.CONNECTING
                            ):
                                connectivity = (
                                    mutable_container._config.test_connection()
                                )
                                if connectivity:
                                    connectivity_message = (
                                        f"GRPC channel state is {state} but "
                                        "Message Service is reacheable - "
                                        "re-initialising channel; "
                                    )
                                    mutable_container.reset_channel()
                                else:
                                    connectivity_message = (
                                        f"GRPC channel state is {state}"
                                        " and Message Service is unreacheable; "
                                    )
                        else:
                            connectivity_message = "cannot inspect GRPC channel state; "
                    else:
                        local_max_retries = max_retries

                    # If an error occurs, we can retry unless this is our final
                    # attempt, or the error code is a non-retryable one.
                    if (
                        retry_count >= local_max_retries
                        or status_code not in all_retry_status_codes
                        or status_code in _additional_no_retry_status_codes
                    ):
                        # Try to append retry count to exception
                        ex._retry_count = retry_count  # type: ignore[attr-defined] # Reason: explicitly setting a new attribute # noqa: E501
                        raise
                    else:
                        maybe_name = f" trying to {name}" if name is not None else ""
                        failure_cause_msg = (
                            f"gRPC error occurred{maybe_name}:"
                            f" (Status Code {status_code}) {ex.details()}"
                        )

                # If we reach this point we must be attempting a retry
                retry_count += 1
                backoff = compute_backoff(retry_count, backoff_factor)

                # Log out failure information and retry information.
                _logger.debug(
                    f"{failure_cause_msg}; {connectivity_message}"
                    f"will retry in {backoff} seconds (attempt {retry_count})."
                )

                await asyncio.sleep(backoff)

            # We shouldn't reach this point due to how the loop can be exited,
            # but just in case.
            raise BitfountMessageServiceError(
                "Unable to make connection, even after multiple attempts."
            )

        return cast(_F, _wrapped_async_grpc_func)

    return _decorate(original_rpc_func)
