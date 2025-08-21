"""Interface classes and methods for the message service.

Provides functionality to wrap generated GRPC code and python-friendly versions
of GRPC classes and methods.
"""

from __future__ import annotations

import asyncio
from asyncio import AbstractEventLoop
from collections.abc import AsyncGenerator, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from math import ceil
import os
import platform
import re
from re import Pattern
import tempfile
import threading
from typing import TYPE_CHECKING, Any, Final, List, Optional, Union, cast
from urllib.parse import urlparse, urlunparse

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from grpc import (
    RpcError,
    StatusCode,
)
import msgpack
import numpy as np
import pandas as pd
import psutil
import pyarrow as pa
from pyarrow import feather
from requests.exceptions import RequestException

from bitfount import config
from bitfount.config import get_gpu_metadata
from bitfount.encryption.encryption import _AESEncryption, _RSAEncryption
from bitfount.federated.exceptions import PodConnectFailedError
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.transport.exceptions import BitfountMessageServiceError
from bitfount.federated.transport.protos.messages_pb2 import (
    BitfountMessage as GrpcBitfountMessage,
    BitfountTask,
    BitfountTasks,
    CommunicationDetails as GrpcCommunicationDetails,
    DiagnosticsParameters,
    LargeStorageRequest,
    MessageMetadata as GrpcMessageMetadata,
    MultipartUploadMetadata as GrpcMultipartUploadMetadata,
    MultipartUploadPart as GrpcMultipartUploadPart,
    PodData,
    ResourcesConsumed as GrpcResourcesConsumed,
    SuccessResponse,
    TaskMetadata,
    TaskNotification as GrpcTaskNotification,
    TaskTransferMetadata,
    TaskTransferRequest,
    TaskTransferRequests,
)
from bitfount.federated.transport.types import CommunicationDetails, Reason
from bitfount.federated.transport.utils import (
    DEFAULT_MANY_RETRIES,
    MessageServiceStubWrapper,
    _auto_retry_grpc,
)
from bitfount.storage import (
    _async_download_data_from_s3,
    _async_upload_data_to_s3,
    _get_packed_data_object_size,
)
from bitfount.types import _S3PresignedPOSTFields, _S3PresignedPOSTURL, _S3PresignedURL
from bitfount.utils import _get_mb_from_bytes
from bitfount.utils.concurrency_utils import await_threading_event

if TYPE_CHECKING:
    from bitfount.federated.transport.config import MessageServiceConfig
    from bitfount.hub.authentication_flow import BitfountSession

_logger = _get_federated_logger(__name__)

# This is used for sanity checking/detecting when the message body is an S3 URL.
# However, it doesn't give us any security guarantees as this subdomain may not be
# unique to us.
_S3_NETLOC_REGEX: Final[Pattern[str]] = re.compile(
    r".*-message-service-external[0-9]*\.s3([.-][a-z0-9-]+)?\.amazonaws\.com"
)


def _is_s3_netloc(netloc: str) -> bool:
    """Checks if the given netloc URL segment matches expected S3 URL structure."""
    if _S3_NETLOC_REGEX.search(netloc):
        return True
    else:
        return False


# This limit is lower than the SQS message limit intentionally.
# When messages are packaged on the message service we attach some metadata,
# the metadata will make them larger, so the python code needs a lower limit.
# So this limit ensures that our message service will accept the raw messages.
_SMALL_MESSAGE_UPPER_LIMIT_SIZE_BYTES: int = 128 * 1024  # 128kb

# Maximum storage request size in message service: 3gb. This should match the value
# in bitfount/message-service:src/messaging/queue.service.ts
_MAX_STORAGE_SIZE_BYTES: Final[int] = 3 * 1024 * 1024 * 1024
_MAX_STORAGE_SIZE_MEGABYTES: Final[int] = _get_mb_from_bytes(
    _MAX_STORAGE_SIZE_BYTES
).whole

# Create fibonacci backoffs to avoid constant querying for messages. Will poll
# (60/1=60) times the first minute after the last message (i.e. 1s intervals),
# (60/2=30) times (i.e. 2s intervals) for the second minute, etc, up to a max of
# 8s polling intervals.
_POLLING_BACKOFFS: Final[tuple[int, ...]] = tuple(
    i for i in (1, 2, 3, 5, 8) for _ in range(ceil(60 / i))
)


def _current_time() -> str:
    """Gets current time as factory for dataclass timestamps."""
    return datetime.now().isoformat()


def msgpackext_encode(obj: Any) -> Any:
    """Serialises extension objects for DataFrames or np.ndarray using pyarrow.

    Args:
        obj: An object to be serialized
    Returns:
        A msgpack compatible extension form of the object.
    """
    if isinstance(obj, np.ndarray):
        tensor = pa.Tensor.from_numpy(obj)
        sink = pa.BufferOutputStream()
        pa.ipc.write_tensor(tensor, sink)
        buf = sink.getvalue().to_pybytes()
        return msgpack.ExtType(1, buf)

    if isinstance(obj, pd.DataFrame):
        sink = pa.BufferOutputStream()
        feather.write_feather(obj, sink)
        buf = sink.getvalue().to_pybytes()
        return msgpack.ExtType(2, buf)
    return obj


def msgpackext_decode(code: int, obj: Any) -> Any:
    """Extension to deserialise DataFrame and numpy using arrow.

    Args:
        code: An integer specifying whether the object is
            a numpy array (code=1) or Dataframe (code=2).
        obj: An encoded object, likely a dictionary.

    Returns:
        The decoded form of the object.
    """
    if code == 1:
        buf = pa.py_buffer(obj)
        tensor = pa.ipc.read_tensor(buf)
        return tensor.to_numpy()
    elif code == 2:
        return feather.read_feather(pa.py_buffer(obj))
    return obj


class _BitfountMessageType(Enum):
    """Used for providing information on the expected shape of a Message.

    These can be used to quickly identify the expected type of an unstructured message
    body from the message service.

    These message types are defined in 4 locations and any changes need to be
    reflected in all locations:

    - the message service (whole proto file)
    - the python repo (whole proto file)
    - the _BitfountMessageType class (python repo)
    - the Hub/AM for audit logs
    """

    # DEPRECATED: SAML exchanges between modeller and worker
    SAML_REQUEST = GrpcBitfountMessage.SAML_REQUEST
    # DEPRECATED: SAML exchanges between modeller and worker
    SAML_RESPONSE = GrpcBitfountMessage.SAML_RESPONSE
    ALGORITHM_EXCHANGE = GrpcBitfountMessage.ALGORITHM_EXCHANGE
    # TODO: [BIT-1049] Should these be combined into JOB_RESPONSE?
    #       The message body itself indicates whether it was an accept or reject.
    JOB_ACCEPT = GrpcBitfountMessage.JOB_ACCEPT
    JOB_REJECT = GrpcBitfountMessage.JOB_REJECT
    JOB_REQUEST = GrpcBitfountMessage.JOB_REQUEST
    EVALUATION_RESULTS = GrpcBitfountMessage.EVALUATION_RESULTS
    KEY_EXCHANGE = GrpcBitfountMessage.KEY_EXCHANGE
    LOG_MESSAGE = GrpcBitfountMessage.LOG_MESSAGE
    # weight updates sent modeller->worker
    MODEL_PARAMETERS = GrpcBitfountMessage.MODEL_PARAMETERS
    SECURE_SHARE = GrpcBitfountMessage.SECURE_SHARE
    TRAINING_COMPLETE = GrpcBitfountMessage.TRAINING_COMPLETE
    # task complete message modeller->worker
    TASK_COMPLETE = GrpcBitfountMessage.TASK_COMPLETE
    # task abort message worker->modeller
    TASK_ABORT = GrpcBitfountMessage.TASK_ABORT
    # weight updates send worker->modeller
    TRAINING_UPDATE = GrpcBitfountMessage.TRAINING_UPDATE
    # validation metrics sent worker->modeller
    TRAINING_METRICS = GrpcBitfountMessage.TRAINING_METRICS
    # Default value for Proto
    UNDEFINED = GrpcBitfountMessage.UNDEFINED
    # OIDC identity verification related types
    OIDC_CHALLENGE = GrpcBitfountMessage.OIDC_CHALLENGE
    # Authorisation Flow Code with PKCE Response
    OIDC_AFC_PKCE_RESPONSE = GrpcBitfountMessage.OIDC_AFC_PKCE_RESPONSE
    # Device Code Response
    OIDC_DEVICE_CODE_RESPONSE = GrpcBitfountMessage.OIDC_DEVICE_CODE_RESPONSE
    # Online check from worker->modeller
    ONLINE_CHECK = GrpcBitfountMessage.ONLINE_CHECK
    # Online response from modeller->worker
    ONLINE_RESPONSE = GrpcBitfountMessage.ONLINE_RESPONSE
    # DEPRECATED: PSI Dataset exchanges between modeller and worker
    PSI_DATASET = GrpcBitfountMessage.PSI_DATASET
    # task start message modeller->worker
    TASK_START = GrpcBitfountMessage.TASK_START
    # Number of batches for batched execution worker->modeller
    NUMBER_OF_BATCHES = GrpcBitfountMessage.NUMBER_OF_BATCHES
    # Model prompt message modeller->worker
    MODEL_PROMPT = GrpcBitfountMessage.MODEL_PROMPT
    # Model response message worker->modeller
    MODEL_RESPONSE = GrpcBitfountMessage.MODEL_RESPONSE
    # Processing of data batches complete message worker->modeller
    BATCHES_COMPLETE = GrpcBitfountMessage.BATCHES_COMPLETE
    # Current batch id message worker->modeller
    CURRENT_BATCH_ID = GrpcBitfountMessage.CURRENT_BATCH_ID


class _LargeObjectRequestHandler:
    """Slim wrapper for handling requests to blob storage."""

    @staticmethod
    async def upload_large_object(
        upload_url: _S3PresignedPOSTURL,
        upload_fields: _S3PresignedPOSTFields,
        large_object: bytes,
    ) -> None:
        """Uploads the object to the upload URL.

        Args:
            upload_url: The URL to upload to.
            upload_fields: Additional data fields needed to upload the object.
            large_object: The object to upload as bytes.

        Raises:
            HTTPError: If the upload fails.
        """
        try:
            await _async_upload_data_to_s3(upload_url, upload_fields, large_object)
        except RequestException as ex:
            raise RequestException(
                f"Failed to upload message to large message storage. Cause: {str(ex)}."
            ) from ex

    @staticmethod
    async def get_large_object_from_url(url: _S3PresignedURL) -> bytes:
        """Retrieves a larger message from the provided download URL.

        Args:
            url: The URL provided on the message service.

        Returns:
            The message that was uploaded.

        Raises:
            HTTPError: If the download fails
        """
        try:
            # We can guarantee the return type is bytes as `upload_large_object`
            # takes in bytes.
            large_object: bytes = await _async_download_data_from_s3(url)
            return large_object
        except RequestException as ex:
            raise RequestException(
                f"Failed to retrieve message from large message storage."
                f" Cause: {str(ex)}."
            ) from ex


@dataclass
class _MessageMetadata:
    """Bitfount-readable message metadata."""

    reason: Optional[Reason]
    task_notification: Optional[TaskNotification]
    resources_consumed: List[ResourceConsumed]


@dataclass
class _MultipartUploadMetadata:
    """Metadata for a multipart upload."""

    key: str
    upload_id: str
    multipart_upload_parts: List[_MultipartUploadPart]


@dataclass
class _MultipartUploadPart:
    """A part of a multipart upload."""

    etag: str
    part_number: int


@dataclass
class ResourceConsumed:
    """Resource consumed during the execution of an algorithm or task step."""

    resource_type: ResourceType
    resource_identifier: str
    amount: float


class ResourceType(Enum):
    """Type of resource consumed."""

    MODEL_INFERENCE = GrpcResourcesConsumed.ResourceType.MODEL_INFERENCE


@dataclass
class TaskNotification:
    """User-readable notification that should be triggered by this message."""

    message: str
    email: bool


def message_metadata_from_grpc_2_sdk(
    grpc_message_metadata: GrpcMessageMetadata,
) -> _MessageMetadata:
    """Deserialise message metadata."""
    reason: Optional[Reason] = None
    if grpc_message_metadata.HasField("reason"):
        try:
            reason = Reason(grpc_message_metadata.reason)
        except ValueError:
            _logger.warning(
                f"Could not parse MessageMetadata Reason {grpc_message_metadata.reason}"
            )

    task_notification: Optional[TaskNotification] = (
        TaskNotification(
            grpc_message_metadata.taskNotification.message,
            grpc_message_metadata.taskNotification.email,
        )
        if grpc_message_metadata.HasField("taskNotification")
        else None
    )

    resources_consumed: List[ResourceConsumed] = []
    for rc in grpc_message_metadata.resourcesConsumed:
        try:
            resource_type = ResourceType(rc.resourceType)
            resources_consumed.append(
                ResourceConsumed(resource_type, rc.resourceIdentifier, rc.amount)
            )
        except ValueError:
            _logger.warning(f"Could not parse resource consumed type {rc.resourceType}")

    return _MessageMetadata(
        reason=reason,
        task_notification=task_notification,
        resources_consumed=resources_consumed,
    )


def message_metadata_from_sdk_2_grpc(
    message_metadata: _MessageMetadata,
) -> GrpcMessageMetadata:
    """Serialise message metadata."""
    task_notification = None
    if message_metadata.task_notification is not None:
        task_notification = GrpcTaskNotification(
            message=message_metadata.task_notification.message,
            email=message_metadata.task_notification.email,
        )

    resources_consumed: Optional[List[GrpcResourcesConsumed]] = None
    if len(message_metadata.resources_consumed) > 0:
        resources_consumed = []
        for rc in message_metadata.resources_consumed:
            resources_consumed.append(
                GrpcResourcesConsumed(
                    resourceType=rc.resource_type.value,
                    resourceIdentifier=rc.resource_identifier,
                    amount=rc.amount,
                )
            )

    return GrpcMessageMetadata(
        reason=(
            None if message_metadata.reason is None else message_metadata.reason.value
        ),
        taskNotification=task_notification,
        resourcesConsumed=resources_consumed,
    )


def message_multipart_upload_metadata_from_grpc_2_sdk(
    grpc_multipart_upload_metadata: GrpcMultipartUploadMetadata,
) -> _MultipartUploadMetadata:
    """Deserialise multipart upload metadata."""
    multipart_upload_parts: List[_MultipartUploadPart] = []
    for part in grpc_multipart_upload_metadata.multipartUploadParts:
        multipart_upload_parts.append(
            _MultipartUploadPart(
                etag=part.ETag,
                part_number=part.PartNumber,
            )
        )

    return _MultipartUploadMetadata(
        key=grpc_multipart_upload_metadata.key,
        upload_id=grpc_multipart_upload_metadata.uploadId,
        multipart_upload_parts=multipart_upload_parts,
    )


def message_multipart_upload_metadata_from_sdk_2_grpc(
    multipart_upload_metadata: _MultipartUploadMetadata,
) -> GrpcMultipartUploadMetadata:
    """Serialise multipart upload metadata."""
    multipart_upload_parts: List[GrpcMultipartUploadPart] = []
    for part in multipart_upload_metadata.multipart_upload_parts:
        multipart_upload_parts.append(
            GrpcMultipartUploadPart(
                ETag=part.etag,
                PartNumber=part.part_number,
            )
        )

    return GrpcMultipartUploadMetadata(
        key=multipart_upload_metadata.key,
        uploadId=multipart_upload_metadata.upload_id,
        multipartUploadParts=multipart_upload_parts,
    )


@dataclass
class _BitfountMessage:
    """A common message structure for all messages from the message service.

    This is a pythonic wrapper on the generated gRPC Proto,
    allowing us to pre-emptively build in support for upcoming features
    as well as backwards compatibility where needed.
    """

    message_type: _BitfountMessageType
    body: bytes
    recipient: str
    recipient_mailbox_id: str
    sender: str
    sender_mailbox_id: str
    # This is provided to pods for secure aggregation
    pod_mailbox_ids: dict[str, str] = field(default_factory=dict)
    # default_factory is used here to ensure current time is set for each instantiation
    timestamp: str = field(default_factory=_current_time)
    # Provided by the message service
    receipt_handle: Optional[str] = None
    # task_id is optional for older message formats but should be used for all
    # new ones when available.
    task_id: Optional[str] = None
    message_metadata: Optional[_MessageMetadata] = None
    multipart_upload_metadata: Optional[_MultipartUploadMetadata] = None

    @staticmethod
    async def from_rpc(message: GrpcBitfountMessage) -> _BitfountMessage:
        """Converts Proto messages into a BitfountMessage.

        Currently requires some additional logic due to the differing protos,
        FromModeller & FromPod, but hopefully those will soon be one proto.

        Args:
            message: A message from a pod or modeller.

        Returns: A BitfountMessage containing the data from the original message

        """
        message_body: bytes = message.body
        try:
            # We attempt to unpack this, as we need to know if it is:
            #   bytes  - Encrypted
            #   string - A URL to download the message body from
            unpacked_body_to_inspect: Union[str, bytes] = msgpack.loads(
                message.body, ext_hook=msgpackext_decode
            )

            # Checks if message body is an S3 file reference or local file reference
            if isinstance(unpacked_body_to_inspect, str):
                parsed_url = urlparse(unpacked_body_to_inspect)

                # If it is an S3 file reference, retrieve the actual message from S3
                if parsed_url.scheme == "https" and _is_s3_netloc(parsed_url.netloc):
                    # [LOGGING-IMPROVEMENTS]
                    if config.settings.logging.log_message_service:
                        _logger.debug(
                            "Large message, retrieving from large object storage"
                        )
                    storage_url = cast(_S3PresignedURL, unpacked_body_to_inspect)
                    message_body = (
                        await _LargeObjectRequestHandler.get_large_object_from_url(
                            storage_url
                        )
                    )

                # If it is a local file reference, retrieve the actual message and
                # re-parse the message with the file contents. For windows, the letter
                # corresponding to the local drive gets assigned to the scheme, so
                # we need an additional check.
                elif (
                    (
                        not parsed_url.scheme
                        or (
                            len(parsed_url.scheme) == 1
                            and platform.system() == "Windows"
                        )
                    )
                    and not parsed_url.netloc
                    and parsed_url.path
                ):
                    _logger.debug("Local message, retrieving from local storage")
                    with open(unpacked_body_to_inspect, "rb") as f:
                        message_body = f.read()
                    # deletes the tempfile after contents have been read
                    os.remove(unpacked_body_to_inspect)

                # If the parsed_url contains a netloc, but it's not a message service
                # S3 one, then raise an exception
                elif parsed_url.netloc:
                    domain_url = urlunparse(
                        (parsed_url.scheme, parsed_url.netloc, "", "", "", "")
                    )
                    raise ValueError(
                        f"Unexpected URL domain or scheme in retrieved message"
                        f" ({message.messageType}) body: {domain_url}"
                    )

                # Otherwise log that this is an unexpected message
                else:
                    _logger.warning(
                        f"Received message ({message.messageType}) from"
                        f" {message.sender} with unencrypted string body"
                        f" that was not a URL."
                    )
        except (msgpack.exceptions.UnpackException, ValueError):
            _logger.debug(
                "Couldn't unpack message - "
                "The message is most likely an encrypted message "
                "which is not on blob storage"
            )
        except OSError as error:  # can be thrown by msgpackext_decode
            _logger.warning(
                f"Couldn't unpack {message.messageType} message "
                f"with a body of {len(message.body)} bytes - "
                "This message could be an encrypted message "
                "which is not on blob storage",
                error,
            )

        message_metadata: Optional[_MessageMetadata] = None
        if message.HasField("messageMetadata"):
            message_metadata = message_metadata_from_grpc_2_sdk(message.messageMetadata)

        multipart_upload_metadata: Optional[_MultipartUploadMetadata] = None
        if message.HasField("multipartUploadMetadata"):
            multipart_upload_metadata = (
                message_multipart_upload_metadata_from_grpc_2_sdk(
                    message.multipartUploadMetadata
                )
            )

        return _BitfountMessage(
            message_type=_BitfountMessageType(message.messageType),
            body=message_body,
            recipient=message.recipient,
            recipient_mailbox_id=message.recipientMailboxId,
            sender=message.sender,
            sender_mailbox_id=message.senderMailboxId,
            pod_mailbox_ids=dict(message.podMailboxIds),
            receipt_handle=message.receiptHandle,
            timestamp=message.timestamp,
            # Older messages may not have task_id field (so will either not be
            # present or default to "")
            task_id=(
                message.taskId
                if hasattr(message, "taskId") and message.taskId
                else None
            ),
            message_metadata=message_metadata,
            multipart_upload_metadata=multipart_upload_metadata,
        )

    def decrypt(self, aes_key: bytes) -> _DecryptedBitfountMessage:
        """Decrypt message body using AES.

        Args:
            aes_key: AES Key to use for decryption
        """
        decrypted_message_body = msgpack.loads(
            _MessageEncryption.decrypt_incoming_message(self.body, aes_key),
            ext_hook=msgpackext_decode,
        )
        return _DecryptedBitfountMessage(
            message_type=self.message_type,
            body=decrypted_message_body,
            recipient=self.recipient,
            recipient_mailbox_id=self.recipient_mailbox_id,
            sender=self.sender,
            sender_mailbox_id=self.sender_mailbox_id,
            pod_mailbox_ids=self.pod_mailbox_ids,
            timestamp=self.timestamp,
            task_id=self.task_id,
        )

    def decrypt_rsa(self, private_key: RSAPrivateKey) -> _DecryptedBitfountMessage:
        """Decrypt message body using RSA.

        Args:
            private_key: RSA private key to use for decryption.
        """
        decrypted_message_body: Any = msgpack.loads(
            _RSAEncryption.decrypt(self.body, private_key)
        )
        return _DecryptedBitfountMessage(
            message_type=self.message_type,
            body=decrypted_message_body,
            recipient=self.recipient,
            recipient_mailbox_id=self.recipient_mailbox_id,
            sender=self.sender,
            sender_mailbox_id=self.sender_mailbox_id,
            pod_mailbox_ids=self.pod_mailbox_ids,
            timestamp=self.timestamp,
            task_id=self.task_id,
        )


@dataclass
class _DecryptedBitfountMessage:
    """BitfountMessage where the body has been decrypted.

    This gives us more confidence that we have a decrypted body,
    and allows us to pass around the decrypted message body and
    metadata together easily.
    """

    message_type: _BitfountMessageType
    body: Any
    recipient: str
    recipient_mailbox_id: str
    sender: str
    sender_mailbox_id: str
    # This is provided to pods for secure aggregation
    pod_mailbox_ids: dict[str, str] = field(default_factory=dict)
    # default_factory is used here to ensure current time is set for each instantiation
    timestamp: str = field(default_factory=_current_time)
    # task_id is optional for older message formats but should be used for all
    # new ones when available.
    task_id: Optional[str] = None


class _AutoRetryMessageServiceStub:
    """Wrapper class that manages an instance of MessageServiceStub.

    It manages the channel state and provides auto-retry.
    Not thread safe, needs to be accessed via a thread-safe environment.
    """

    # Don't mutate this reference because the retries will keep the old one
    _orig: Final[MessageServiceStubWrapper]

    def __init__(
        self,
        config: MessageServiceConfig,
    ) -> None:
        self._config = config
        self._orig = MessageServiceStubWrapper(config)

        self.PodConnect = _auto_retry_grpc(
            self._orig.PodConnect,
        )
        self.SetupTask = _auto_retry_grpc(
            self._orig.SetupTask,
        )
        self.InitiateTask = _auto_retry_grpc(
            self._orig.InitiateTask,
        )
        self.SendBitfountMessage = _auto_retry_grpc(
            self._orig.SendBitfountMessage,
            # If there's a connectivity issue retry a lot more times
            connectivity_retries=DEFAULT_MANY_RETRIES,
        )
        self.GetLargeObjectStorage = _auto_retry_grpc(
            self._orig.GetLargeObjectStorage,
        )
        self.Diagnostics = _auto_retry_grpc(
            self._orig.Diagnostics,
        )

        # NOTE: Auto retry for GetBitfountMessage and AcknowledgeMessage are
        #       handled separately to ensure that it is an atomic operation.
        #
        #       See _atomic_get_and_ack().
        self.GetBitfountMessage = self._orig.GetBitfountMessage
        self.AcknowledgeMessage = self._orig.AcknowledgeMessage
        self.atomic_get_and_ack_with_retry = _auto_retry_grpc(
            self._orig.atomic_get_and_ack,
            additional_no_retry_status_codes=[StatusCode.NOT_FOUND],
            connectivity_retries=DEFAULT_MANY_RETRIES,
        )


class _LocalGrpc(threading.local):
    """A thread-local container class for storing the gRPC stub.

    This ensures that the gRPC stub is unique per-thread as the async gRPC API is
    not thread-safe and wrapping it in synchronisation primitives would mean that
    it blocks gRPC interactions and potentially event loops.

    Because each thread will receive its own instance of this class, we want to
    set the stub to None in __init__ so that the stub instance isn't shared between
    threads.
    """

    stub: Optional[_AutoRetryMessageServiceStub]

    def __init__(self) -> None:
        self.stub = None


class _MessageService:
    """Slim wrapper around the GRPC Functions provided by the message service.

    It stops the GRPC objects which aren't very pleasant to use from being everywhere
    as well as making it easier to replace these in future if needed.

    Args:
        config: The configuration for the gRPC message service.
        session: Used for authentication.
    """

    def __init__(
        self, config: MessageServiceConfig, session: Optional[BitfountSession] = None
    ):
        self._config = config
        self._session = session
        self._use_local_storage: bool = config.use_local_storage

        self._grpc = _LocalGrpc()

    # @cached_property can't be used because it returns the _exact_ same Awaitable
    # which cannot be awaited more than once.
    @property
    async def stub(self) -> _AutoRetryMessageServiceStub:
        """The gRPC stub generated for this instance."""
        if self._grpc.stub is None:
            self._grpc.stub = _AutoRetryMessageServiceStub(self._config)

            def _custom_exception_handler(
                loop: AbstractEventLoop, context: dict[str, Any]
            ) -> None:
                """Custom exception handler to suppress superfluous gRPC exceptions.

                See https://github.com/grpc/grpc/issues/25364.
                """
                # TODO: [BIT-2236] Remove workaround when gRPC issue resolved
                # If it is the problematic "error", ignore
                if (
                    "Exception in callback PollerCompletionQueue._handle_events"
                    in context["message"]
                ):
                    pass
                # Otherwise, pass to the default exception handler to handle
                else:
                    return loop.default_exception_handler(context)

            loop_ = asyncio.get_running_loop()
            loop_.set_exception_handler(_custom_exception_handler)
        return self._grpc.stub

    @property
    def username(self) -> str:
        """Get the authenticated username."""
        if self._session:
            return self._session.username
        return ""

    @property
    def metadata(self) -> list[tuple[str, str]]:
        """Returns metadata required for sending a BitfountMessage."""
        if self._session:
            return self._session.message_service_metadata
        return []

    async def connect_pod(
        self, pod_name: str, dataset_names: Optional[list[str]] = None
    ) -> str:
        """Make the message service aware of the Pod.

        This ensures that the correct queue is set up for this pod,
        in future it may contain more metadata.

        Args:
            pod_name: The name of the pod (the part after 'username/')
            dataset_names: Optional. The name of the datasets, in case there is
                more than one (also the part after 'username/').

        Returns:
            The created mailbox ID for this pod.

        Raises:
            BitfountMessageServiceError: If an error occurs when communicating
                                         with the message service.
        """
        processor = platform.processor()
        pod_os = platform.system()
        logical_cpu_count = psutil.cpu_count() or 1
        total_physical_memory_bytes = psutil.virtual_memory().total
        gpu_name, available_gpus = get_gpu_metadata()

        try:
            _logger.debug("Accessing gRPC stub.")
            stub = await self.stub
            _logger.debug("Calling PodConnect on message service.")
            response = await stub.PodConnect(
                PodData(
                    podName=pod_name,
                    processor=processor,
                    podOS=pod_os,
                    cpuCount=logical_cpu_count,
                    totalMemoryBytes=total_physical_memory_bytes,
                    gpuCount=available_gpus,
                    gpuName=gpu_name,
                    datasetNames=dataset_names,
                ),
                metadata=self.metadata,
            )
            _logger.debug(f"PodConnect completed, response: {response}")
        except (RpcError, RequestException) as e:
            _logger.debug(e, exc_info=True)
            raise BitfountMessageServiceError(
                "Unable to connect pod to message service."
                " See debug logs for more details."
            ) from e

        # If we've not received a successful response (but no other RPC error
        # happened) then raise it here.
        if not isinstance(response, SuccessResponse):
            raise PodConnectFailedError("Unable to connect pod to message service.")

        # TODO: [BIT-960] Currently this is just hardcoded to return the pod_name
        #       (which is what the mailbox ID will actually be). [BIT-960] will have
        #       the PodConnect method actually return the generated mailbox ID so
        #       that if the approach changes in future it only needs to change on
        #       the message service side. At that point this should return the
        #       generated mailbox ID instead.
        return pod_name

    async def setup_task(
        self,
        tasks_per_pod: dict[str, bytes],
        task_metadata: TaskMetadata,
        project_id: Optional[str] = None,
    ) -> CommunicationDetails:
        """Called by the modeller to set up communication channels with specified pods.

        Args:
            tasks_per_pod: Mapping of pod identifiers to AES Encrypted messages.
            task_metadata: Metadata about the encrypted tasks
            project_id: ID of the project the task is associated with

        Returns:
            A tuple of mailbox IDs used for communications:
                - mailbox_id (str): The modeller's mailbox ID
                - worker_mailbox_ids (dict): Mapping from Pod ID to Worker Mailbox ID
                - task_id (str): The unique task ID for the task

        Raises:
            BitfountMessageServiceError: If an error occurs when communicating
                                         with the message service.
        """
        _logger.debug(f"Setting up task configuration with: '{tasks_per_pod.keys()}'")
        try:
            # All tasks are transferred via Blob storage,
            # so we need to request the appropriate amounts of storage.
            # This can differ per pod as the tasks are encrypted.
            task_sizes = []
            for pod_identifier, aes_encrypted_task in tasks_per_pod.items():
                task_sizes.append(
                    TaskTransferRequest(
                        podIdentifier=pod_identifier,
                        contentSize=_get_packed_data_object_size(aes_encrypted_task),
                    )
                )

            # Request the storage, and get a Task ID
            task_upload_metadata: TaskTransferMetadata = await (
                await self.stub
            ).SetupTask(
                TaskTransferRequests(podTasks=task_sizes, projectId=project_id),
                metadata=self.metadata,
            )

            # Upload each encrypted task to the appropriately sized location
            tasks = []
            for storage_metadata in task_upload_metadata.taskStorage:
                await _LargeObjectRequestHandler.upload_large_object(
                    cast(_S3PresignedPOSTURL, storage_metadata.uploadUrl),
                    cast(_S3PresignedPOSTFields, storage_metadata.uploadFields),
                    tasks_per_pod[storage_metadata.podIdentifier],
                )
                # Prepare the message that will be sent to each pod containing the task
                tasks.append(
                    BitfountTask(
                        podIdentifier=storage_metadata.podIdentifier,
                        taskURL=msgpack.dumps(
                            storage_metadata.downloadUrl, default=msgpackext_encode
                        ),
                    )
                )

            # Send the URL for each task on blob storage to each pod
            communication_details: GrpcCommunicationDetails = await (
                await self.stub
            ).InitiateTask(
                BitfountTasks(
                    tasks=tasks,
                    taskId=task_upload_metadata.taskId,
                    projectId=project_id,
                    taskMetadata=task_metadata,
                ),
                metadata=self.metadata,
            )
        except (RpcError, RequestException) as e:
            _logger.debug(e, exc_info=True)
            raise BitfountMessageServiceError(
                "Unable to start task with target pods."
                " See debug logs for more details."
            ) from e

        # communication_details.podMailboxIds is actually the _worker_ mailbox_ids
        return CommunicationDetails(
            communication_details.mailboxId,
            dict(communication_details.podMailboxIds),
            communication_details.taskId,
        )

    async def poll_for_messages(
        self,
        mailbox_id: str,
        stop_event: threading.Event,
    ) -> AsyncGenerator[_BitfountMessage, None]:
        """Polls target mailbox for message.

        Will keep retrying up to `self.minutes_before_timeout_no_messages`
        or until a message is received, whichever is sooner.

        Will attempt to workaround transient connection exceptions by retrying but
        if exceptions are repeatedly raised then it will throw the exception.

        Args:
            mailbox_id: The mailbox to poll for messages.
            stop_event: A threading Event that indicates to stop polling.

        Yields:
            BitfountMessage: the next message received
        """
        counter = 0

        # Create stop_event future to use for all retrievals.
        # Can set larger polling timeout as should only be a single instance of
        # this and should be `set()` in event of failure or polling end
        # (see `_BaseMailbox.listen()`).
        stop_event_wait_task = asyncio.create_task(
            await_threading_event(
                stop_event,
                event_name=f"stop_polling_event_in_{mailbox_id}",
                polling_timeout=30,
            )
        )

        while True:
            # Check stop event before trying to retrieve messages
            if stop_event.is_set():
                _logger.debug("Stopping polling for messages.")
                break

            # Wait for either a message or for the stop event to be set
            get_message_task = asyncio.create_task(
                self._get_message(mailbox_id), name="get_message"
            )
            awaitables: list[Awaitable] = [get_message_task, stop_event_wait_task]
            done, _ = await asyncio.wait(
                awaitables, return_when=asyncio.FIRST_COMPLETED
            )

            if get_message_task in done:
                message = get_message_task.result()

                if message:
                    # Reset counter
                    counter = 0
                    # Yield as soon as we've retrieved a message
                    yield message
                else:
                    counter += 1
                    # Cap counter at the maximum `backoffs` entry
                    counter = min(counter, len(_POLLING_BACKOFFS) - 1)

                # Check stop event again before trying to sleep
                if stop_event.is_set():
                    _logger.debug("Stopping polling for messages.")
                    break

                # Sleep for backoff time until trying again
                await asyncio.sleep(_POLLING_BACKOFFS[counter])
            else:
                # The stop event has been triggered
                _logger.debug("Stopping polling for messages.")
                get_message_task.cancel()
                break

    async def _get_message(self, mailbox_id: str) -> Optional[_BitfountMessage]:
        """Retrieve message from mailbox if available.

        If none are available then it returns None.

        Other errors are raised if they occur repeatedly.

        Args:
            mailbox_id: Mailbox to check for messages.

        Returns:
            An BitfountMessage if one is available, else None.

        Raises:
            BitfountMessageServiceError: If an error occurs when multiple times
                                         when communicating with the message service.
        """
        # Try to retrieve a message and acknowledge message in one atomic step if
        # there is one available

        try:
            message: GrpcBitfountMessage = await (
                await self.stub
            ).atomic_get_and_ack_with_retry(self.metadata, mailbox_id)
        except (RpcError, RequestException) as ex:
            if isinstance(ex, RpcError) and ex.code() == StatusCode.NOT_FOUND:
                # This indicates that no message was waiting and is an expected "error"
                # [LOGGING-IMPROVEMENTS]
                if config.settings.logging.log_message_service:
                    _logger.debug(f"No message available on {mailbox_id}")
                return None
            else:
                _logger.debug(ex, exc_info=True)
                retry_count: Optional[int] = getattr(ex, "_retry_count", None)
                if retry_count is not None:
                    retry_count_msg_str = f" ({retry_count} retries) "
                else:
                    retry_count_msg_str = " "
                _logger.error(
                    "Exceeded maximum attempts"
                    + retry_count_msg_str
                    + f"when retrieving message from {mailbox_id}"
                )
                raise BitfountMessageServiceError(
                    "Issue retrieving message from mailbox. See debug log for details."
                ) from ex

        b_message = await _BitfountMessage.from_rpc(message)
        _logger.debug(
            f"Retrieved {b_message.message_type} message"
            f" from {b_message.sender}"
            f" on mailbox {mailbox_id}"
        )
        return b_message

    async def send_message(
        self,
        message: _BitfountMessage,
        already_packed: bool = False,
    ) -> SuccessResponse:
        """Send a message.

        Args:
            message (BitfountMessage): The message to send
            already_packed (bool): Whether or not the message is already in required
                bytes format

        Returns:
            SuccessResponse if the message was successfully sent

        Raises:
            BitfountMessageServiceError: If an error occurs when communicating
                                         with the message service.
        """
        if not already_packed:
            message.body = msgpack.dumps(
                message.body,
                default=msgpackext_encode,
            )

        if self._use_local_storage:
            message.body = self._save_object_to_local_storage(message)
        else:
            message.body = await self._maybe_upload_to_large_object_storage(message)

        try:
            _logger.debug(
                f"Sending {message.message_type}"
                f" to {message.recipient} (id={id(message)})"
            )
            send_resp = await (await self.stub).SendBitfountMessage(
                GrpcBitfountMessage(
                    messageType=message.message_type.value,
                    body=message.body,
                    recipient=message.recipient,
                    recipientMailboxId=message.recipient_mailbox_id,
                    sender=message.sender,
                    senderMailboxId=message.sender_mailbox_id,
                    timestamp=message.timestamp,
                    podMailboxIds=message.pod_mailbox_ids,
                    taskId=message.task_id,
                    messageMetadata=(
                        None
                        if message.message_metadata is None
                        else message_metadata_from_sdk_2_grpc(message.message_metadata)
                    ),
                    multipartUploadMetadata=(
                        None
                        if message.multipart_upload_metadata is None
                        else message_multipart_upload_metadata_from_sdk_2_grpc(
                            message.multipart_upload_metadata
                        )
                    ),
                ),
                metadata=self.metadata,
            )
            # [LOGGING-IMPROVEMENTS]
            if config.settings.logging.log_message_service:
                _logger.debug(
                    f"Sent {message.message_type} to {message.recipient}"
                    f" (id={id(message)}): {send_resp}"
                )
            return send_resp
        except (RpcError, RequestException) as e:
            _logger.debug(
                f"Error sending {message.message_type}"
                f" to {message.recipient} (id={id(message)})"
            )
            _logger.debug(e, exc_info=True)
            raise BitfountMessageServiceError(
                "Encountered problem when sending message."
                " See debug logs for more details."
            ) from e

    async def _maybe_upload_to_large_object_storage(
        self, message: _BitfountMessage
    ) -> bytes:
        """Uploads the message body to large object storage if it's too big.

        Args:
            message: the message containing the body to upload

        Returns:
            Either the original message body, or a URL that can be used to download it
        """
        # Larger messages are sent as references to large object storage
        if len(message.body) > _SMALL_MESSAGE_UPPER_LIMIT_SIZE_BYTES:
            # Check that message body isn't above the maximum storage size
            message_body_size = _get_packed_data_object_size(message.body)
            if message_body_size > _MAX_STORAGE_SIZE_BYTES:
                raise ValueError(
                    f"Message body is too large to upload: "
                    f"expected max {_MAX_STORAGE_SIZE_MEGABYTES} megabytes, "
                    f"got {_get_mb_from_bytes(message_body_size).fractional} megabytes."
                )

            pod_name = None
            if message.sender and "/" in message.sender:
                pod_name = message.sender.split("/")[1]
            (
                (
                    upload_url,
                    upload_fields,
                ),
                download_url,
            ) = await self._get_large_object_storage_details(
                message.sender_mailbox_id, message_body_size, message.task_id, pod_name
            )
            _logger.debug(
                f"Uploading contents of {message.message_type} to object storage"
            )
            await _LargeObjectRequestHandler.upload_large_object(
                upload_url, upload_fields, message.body
            )

            # Currently necessary, as the message service is expecting bytes
            return msgpack.dumps(download_url, default=msgpackext_encode)
        # Small messages can just go on the message service directly
        return message.body

    async def _get_large_object_storage_details(
        self,
        mailbox_id: str,
        message_size: int,
        task_id: Union[str, None],
        pod_name: Optional[str] = None,
    ) -> tuple[tuple[_S3PresignedPOSTURL, _S3PresignedPOSTFields], _S3PresignedURL]:
        """Get an upload and download URL for larger message bodies.

        Args:
            mailbox_id: Your mailbox id for the current task.
            message_size: The size of the message to upload (an upper limit).
            task_id: The ID associated with the task. Must be supplied but can be None.
            pod_name: Name of the pod that you're acting as, if relevant.

        Returns:
            tuple of upload handler, download URL.

        Raises:
            BitfountMessageServiceError: If an error occurs when communicating
                with the message service.
        """
        try:
            blob_storage_data = await (await self.stub).GetLargeObjectStorage(
                LargeStorageRequest(
                    senderMailboxId=mailbox_id,
                    podName=pod_name,
                    contentSize=message_size,
                    taskId=task_id,
                ),
                metadata=self.metadata,
            )
            return (
                (
                    cast(_S3PresignedPOSTURL, blob_storage_data.uploadUrl),
                    cast(_S3PresignedPOSTFields, dict(blob_storage_data.uploadFields)),
                ),
                cast(_S3PresignedURL, blob_storage_data.downloadUrl),
            )
        except (RpcError, RequestException) as e:
            _logger.debug(e, exc_info=True)
            raise BitfountMessageServiceError(
                "Unable to acquire large object storage."
                " See debug logs for more details."
            ) from e

    async def diagnostics(self) -> _S3PresignedURL:
        try:
            diagnostics = await (await self.stub).Diagnostics(
                DiagnosticsParameters(), metadata=self.metadata
            )

            return cast(_S3PresignedURL, diagnostics.testDataDownloadUrl)
        except (RpcError, RequestException) as e:
            _logger.debug(e, exc_info=True)
            raise BitfountMessageServiceError(
                "Unable to get diagnostics data. See debug logs for more details."
            ) from e

    @staticmethod
    def _save_object_to_local_storage(message: _BitfountMessage) -> bytes:
        """Saves object to local storage and returns filename.

        Args:
            message: the message containing the body to upload

        Returns:
            A path to the file where the local object has been stored.
        """
        # we use mkstemp here to ensure we have complete control over when the file gets
        # deleted on every OS - unlike e.g. NamedTemporaryFile
        handle, local_tempfile = tempfile.mkstemp()
        # write to the open file handler rather than finding the file by name
        with os.fdopen(handle, "wb") as f:
            f.write(message.body)
        return msgpack.dumps(local_tempfile, default=msgpackext_encode)


class _MessageEncryption:
    """Shared functions for handling encryption/decryption of messages.

    These handle encrypting or decrypting a single or multiple messages
    at the same time using different keys (for different pods)
    """

    @staticmethod
    def encrypt_outgoing_message(body: bytes, encryption_key: bytes) -> bytes:
        """Encrypt `body` using `encryption_key`."""
        body, nonce = _AESEncryption.encrypt(encryption_key, body)
        body += nonce
        return body

    @staticmethod
    def decrypt_incoming_message(
        body: bytes,
        encryption_key: bytes,
    ) -> bytes:
        """Decrypt incoming message."""
        body, nonce = body[:-12], body[-12:]
        body = _AESEncryption.decrypt(encryption_key, nonce, body)

        return body
