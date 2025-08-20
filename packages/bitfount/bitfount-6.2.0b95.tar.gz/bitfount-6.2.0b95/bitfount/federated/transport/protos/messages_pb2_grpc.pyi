# Manually created stub for generated gRPC code.
from typing import Any, Optional, Sequence, Tuple

import grpc.aio

from bitfount.federated.transport.protos.messages_pb2 import (
    Acknowledgement,
    BitfountMessage,
    BitfountTasks,
    BlobStorageData,
    CommunicationDetails,
    LargeStorageRequest,
    PodData,
    SuccessResponse,
    TaskTransferMetadata,
    TaskTransferRequests,
    DiagnosticsParameters,
    ServiceDiagnostics,
)

class MessageServiceStub:
    def __init__(self, channel: grpc.aio.Channel) -> None: ...
    async def PodConnect(
        self,
        data: PodData,
        /,
        *,
        metadata: Sequence[Tuple[str, Any]],
        timeout: Optional[float] = ...,
    ) -> SuccessResponse: ...
    async def SetupTaskMailboxes(
        self,
        data: BitfountTasks,
        /,
        *,
        metadata: Sequence[Tuple[str, Any]],
        timeout: Optional[float] = ...,
    ) -> CommunicationDetails: ...
    async def SetupTask(
        self,
        data: TaskTransferRequests,
        /,
        *,
        metadata: Sequence[Tuple[str, Any]],
        timeout: Optional[float] = ...,
    ) -> TaskTransferMetadata: ...
    async def InitiateTask(
        self,
        data: BitfountTasks,
        /,
        *,
        metadata: Sequence[Tuple[str, Any]],
        timeout: Optional[float] = ...,
    ) -> CommunicationDetails: ...
    async def AcknowledgeMessage(
        self,
        data: Acknowledgement,
        /,
        *,
        metadata: Sequence[Tuple[str, Any]],
        timeout: Optional[float] = ...,
    ) -> SuccessResponse: ...
    async def GetBitfountMessage(
        self,
        data: CommunicationDetails,
        /,
        *,
        metadata: Sequence[Tuple[str, Any]],
        timeout: Optional[float] = ...,
    ) -> BitfountMessage: ...
    async def SendBitfountMessage(
        self,
        data: BitfountMessage,
        /,
        *,
        metadata: Sequence[Tuple[str, Any]],
        timeout: Optional[float] = ...,
    ) -> SuccessResponse: ...
    async def GetLargeObjectStorage(
        self,
        data: LargeStorageRequest,
        /,
        *,
        metadata: Sequence[Tuple[str, Any]],
        timeout: Optional[float] = ...,
    ) -> BlobStorageData: ...
    async def Diagnostics(
            self,
            data: DiagnosticsParameters,
            /,
            *,
            metadata: Sequence[Tuple[str, Any]],
            timeout: Optional[float] = ...,
    ) -> ServiceDiagnostics: ...
