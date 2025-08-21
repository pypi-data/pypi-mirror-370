"""Handles Modeller sending training requests and receiving pod responses."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable, Mapping, MutableMapping, MutableSequence
from dataclasses import dataclass
import logging
from typing import Any, Final, Optional, Union, cast

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from grpc import RpcError

from bitfount import config
from bitfount.encryption.encryption import _AESEncryption
from bitfount.federated.exceptions import BitfountTaskStartError, TaskAbortError
from bitfount.federated.logging import _federate_logger, _get_federated_logger
from bitfount.federated.transport.base_transport import (
    Handler,
    MessageRetrievalError,
    SyncHandler,
    _BaseMailbox,
    _send_aes_encrypted_message,
)
from bitfount.federated.transport.handlers import _AsyncMultipleResponsesHandler
from bitfount.federated.transport.message_service import (
    _BitfountMessage,
    _BitfountMessageType,
    _DecryptedBitfountMessage,
    _MessageService,
)
from bitfount.federated.transport.protos.messages_pb2 import TaskMetadata
from bitfount.federated.transport.types import (
    Reason,
    ReasonString,
    TaskAbortBody,
    _OIDCAuthFlowResponse,
    _OIDCClientID,
    _PodDeviceCodeDetails,
)
from bitfount.federated.transport.utils import _average_training_metrics
from bitfount.federated.types import (
    _RESPONSE_MESSAGES,
    SerializedProtocol,
    _PodResponseType,
    _TaskRequestMessageGenerator,
)
from bitfount.hooks import HookType, get_hooks
from bitfount.types import _JSONDict, _SerializedWeights, _StrAnyDict

logger = _get_federated_logger(__name__)

_DEFAULT_TASK_RESPONSE_TIMEOUT: Final[int] = 5 * 60  # 5 minutes
_DEFAULT_OIDC_CLIENT_IDS_TIMEOUT: Final[int] = 5 * 60  # 5 minutes
_SOFT_LIMIT_MESSAGE_TIMEOUT: Final[int] = config.settings.online_check_soft_limit


@dataclass
class _WorkerMailboxDetails:
    """Mailbox details for a specific task/worker on a pod.

    Used by the modeller to encapsulate details of worker mailboxes.

    Attributes:
        pod_identifier: The parent pod's identifier.
        public_key: The parent pod's public key.
        mailbox_id: The mailbox ID for this specific task/worker.
        aes_encryption_key: The encryption key to use for this specific task/worker.
    """

    pod_identifier: str
    public_key: RSAPublicKey
    mailbox_id: str
    aes_encryption_key: bytes


class _ModellerMailbox(_BaseMailbox):
    """Handles message interactions with pods."""

    def __init__(
        self,
        mailbox_id: str,
        worker_mailboxes: Mapping[str, _WorkerMailboxDetails],
        task_id: str,
        message_service: _MessageService,
        handlers: Optional[
            Mapping[_BitfountMessageType, Union[Handler, Iterable[Handler]]]
        ] = None,
    ):
        """Creates a new ModellerMailbox.

        Note that the preferred way to get a new ModellerMailbox is by calling
        ModellerMailbox.send_task_requests() which will instantiate the correct
        ModellerMailbox for you.

        Args:
            mailbox_id: The mailbox ID for this modeller mailbox.
            worker_mailboxes: A mapping of pod identifiers to worker mailbox details
                              for the pods/workers that will be involved in this task.
            task_id: The ID for the task this mailbox belongs to.
            message_service: The underlying message service.
            handlers: Optional. A set of handlers to initialise with.
        """
        super().__init__(
            mailbox_id=mailbox_id, message_service=message_service, handlers=handlers
        )
        self.worker_mailboxes: dict[str, _WorkerMailboxDetails] = dict(worker_mailboxes)
        self._pod_identifiers: set[str] = set(worker_mailboxes.keys())
        self._task_id = task_id

        self.accepted_worker_mailboxes: dict[str, _WorkerMailboxDetails] = {}
        self.pods_ready: bool = False
        self._num_pods_ready: int = 0
        self.batches_complete_received: bool = False
        self.completed_workers: set[str] = set()

        self._current_total_batches: Optional[int] = None
        # self._lock = threading.Lock()

        self._setup_federated_logging()
        self._setup_online_status_handler()
        self._setup_task_abort_handler()
        self._setup_task_start_handler()
        self._setup_batches_complete_handler()
        self._setup_batch_count_update_handler()
        self.abort: Optional[tuple[str, Optional[Reason]]] = None

        self.workers_in_resilience: set[str] = (
            set()
        )  # Track which workers are in resilience
        self.workers_batch_complete: set[str] = (
            set()
        )  # Track which workers finished batches

    @property
    def task_id(self) -> str:
        """The task ID of the task associated with this mailbox."""
        return self._task_id

    @property
    def any_worker_in_resilience(self) -> bool:
        """Check if any worker is currently in resilience phase."""
        return len(self.workers_in_resilience) > 0

    @property
    def all_workers_batch_complete(self) -> bool:
        """Check if all workers have completed their regular batches."""
        return len(self.workers_batch_complete) == len(self.accepted_worker_mailboxes)

    ############################
    # Task Setup Phase Methods #
    ############################
    @classmethod
    async def send_task_requests(
        cls,
        serialized_protocol: SerializedProtocol,
        pod_public_keys: Mapping[str, RSAPublicKey],
        task_request_msg_gen: _TaskRequestMessageGenerator,
        message_service: _MessageService,
        project_id: Optional[str] = None,
        run_on_new_data_only: bool = False,
        batched_execution: Optional[bool] = None,
        test_run: bool = False,
        force_rerun_failed_files: bool = True,
    ) -> _ModellerMailbox:
        """Sends task requests, such as training requests, to pods.

        Appropriate mailboxes will be created for the modeller and worker mailboxes
        for the pods.

        Args:
            serialized_protocol: The serialized protocol to use for the task.
            pod_public_keys: A mapping of pod identifiers to their public keys for all
                the pods involved in this task request.
            task_request_msg_gen: A callable which will generate a task request message
                appropriate to the chosen verification method.
            message_service: The underlying message service to use.
            project_id: The project ID the task belongs to. Defaults to None.
            run_on_new_data_only: Whether to run the task on new datapoints only.
                Defaults to False.
            batched_execution: Whether to run the task in batched execution mode.
                Defaults to False.
            test_run: Whether this is a test run. Defaults to False.
            force_rerun_failed_files: If True, forces a rerun on files that
                the task previously failed on. If False, the task will skip
                files that have previously failed. Note: This option can only be
                enabled if both enable_batch_resilience and
                individual_file_retry_enabled are True. Defaults to True.

        Returns:
            The created modeller mailbox for this task.
        """
        if batched_execution is None:
            batched_execution = config.settings.default_batched_execution

        modeller_mailbox_id, worker_mailboxes, task_id = await cls._send_task_requests(
            serialized_protocol,
            pod_public_keys,
            task_request_msg_gen=task_request_msg_gen,
            message_service=message_service,
            project_id=project_id,
            run_on_new_data_only=run_on_new_data_only,
            batched_execution=batched_execution,
            test_run=test_run,
            force_rerun_failed_files=force_rerun_failed_files,
        )
        modeller_mailbox = cls(
            mailbox_id=modeller_mailbox_id,
            worker_mailboxes=worker_mailboxes,
            task_id=task_id,
            message_service=message_service,
        )
        return modeller_mailbox

    @classmethod
    async def _send_task_requests(
        cls,
        serialized_protocol: SerializedProtocol,
        pod_public_keys: Mapping[str, RSAPublicKey],
        task_request_msg_gen: _TaskRequestMessageGenerator,
        message_service: _MessageService,
        project_id: Optional[str],
        run_on_new_data_only: bool = False,
        batched_execution: Optional[bool] = None,
        test_run: bool = False,
        force_rerun_failed_files: bool = True,
    ) -> tuple[str, dict[str, _WorkerMailboxDetails], str]:
        """Manage sending of task requests, such as training requests, to pods.

        Args:
            serialized_protocol: The serialized protocol to use for the task.
            pod_public_keys: A mapping of pod identifiers to their public keys for all
                the pods involved in this task request.
            task_request_msg_gen: A callable which will generate a task request message
                appropriate to the chosen verification method.
            message_service: The underlying message service to use.
            project_id: The project Id the task belongs to.
            run_on_new_data_only: Whether to run the task on new datapoints only.
                Defaults to False.
            batched_execution: Whether to run the task in batched execution mode.
                Defaults to False.
            test_run: Whether this is a test run. Defaults to False.
            force_rerun_failed_files: If True, forces a rerun on files that
                the task previously failed on. If False, the task will skip
                files that have previously failed. Note: This option can only be
                enabled if both enable_batch_resilience and
                individual_file_retry_enabled are True. Defaults to True.

        Returns:
            tuple of:
                - (str) modeller mailbox ID
                - (dict) of pod identifier to worker mailbox details
                - (str) the task ID
        """
        # Shorthand the pod identifiers for ease of use
        pod_identifiers: list[str] = list(pod_public_keys)
        if batched_execution is None:
            batched_execution = config.settings.default_batched_execution
        # Generate encryption keys and then task request messages for each pod.
        aes_key_per_pod = {
            pod_identifier: _AESEncryption.generate_key()
            for pod_identifier in pod_identifiers
        }
        task_request_per_pod: dict[str, bytes] = {
            pod_identifier: task_request_msg_gen(
                serialized_protocol,
                pod_identifiers,
                aes_key_per_pod[pod_identifier],
                pod_public_key,
                project_id,
                run_on_new_data_only,
                batched_execution,
                test_run,
                force_rerun_failed_files,
            )
            for pod_identifier, pod_public_key in pod_public_keys.items()
        }

        # Send this message to each pod and receive the modeller's mailbox ID
        # and the mailbox IDs of all the pods in the task.
        try:
            (
                modeller_mailbox_id,
                worker_mailbox_ids,
                task_id,
            ) = await message_service.setup_task(
                task_request_per_pod,
                TaskMetadata(protocol=serialized_protocol["class_name"]),
                project_id,
            )
            logger.info(f"Sent task requests to {pod_identifiers}")
        except RpcError as err:
            logger.error(
                f"Failed to start task with pods: {pod_identifiers}. Error: {err}"
            )
            raise BitfountTaskStartError(
                f"Failed to start task with pods: {pod_identifiers}"
            ) from err

        return (
            modeller_mailbox_id,
            {
                pod_identifier: _WorkerMailboxDetails(
                    pod_identifier,
                    pod_public_keys[pod_identifier],
                    worker_mailbox_id,
                    aes_key_per_pod[pod_identifier],
                )
                for pod_identifier, worker_mailbox_id in worker_mailbox_ids.items()
            },
            task_id,
        )

    async def get_oidc_client_ids(
        self, timeout: Optional[int] = _DEFAULT_OIDC_CLIENT_IDS_TIMEOUT
    ) -> dict[str, _OIDCClientID]:
        """Receive OIDC client ID responses from pods.

        These will be the first step in OIDC-related auth flows, showing the modeller
        that the pods have received their request and are ready to start the flow.

        Returns:
            A mapping of pod identifier to their client ID as a dataclass.
        """
        oidc_client_ids: dict[str, _OIDCClientID] = {}

        def _oidc_client_id_message_handler(message: _BitfountMessage) -> None:
            logger.info(f"Received OIDC Client ID from {message.sender}")
            decrypted_msg = self._decrypt_message(message)
            oidc_client_ids[decrypted_msg.sender] = _OIDCClientID.deserialize(
                decrypted_msg.body
            )

        # Create handler for processing the group of expected responses. Using it
        # as a context manager guarantees that the handlers are correctly applied
        # and removed.
        with _AsyncMultipleResponsesHandler(
            handler=_oidc_client_id_message_handler,
            message_types=_BitfountMessageType.OIDC_CHALLENGE,
            mailbox=self,
            responders=self._pod_identifiers,
        ) as multi_response:
            try:
                # Wait for all responses to have been received or until the
                # timeout expires.
                await multi_response.wait_for_responses(timeout=timeout)
            except MessageRetrievalError as err:
                logger.error(
                    f"Error receiving responses from all pods to the OIDC phase "
                    f"of the task request: {err}"
                )
                raise BitfountTaskStartError(
                    "Failed to start task with all pods."
                ) from err

        if not oidc_client_ids:
            logger.error("No OIDC client id retrieved from message handler")
            raise ValueError("No OIDC client id retrieved from message handler")

        return oidc_client_ids

    async def send_oidc_auth_flow_responses(
        self,
        oidc_responses: dict[str, _OIDCAuthFlowResponse],
    ) -> None:
        """Send response for OIDC Authorization Code Flow."""
        for pod_id, response in oidc_responses.items():
            pod_mailbox = self.worker_mailboxes[pod_id]
            await _send_aes_encrypted_message(
                response.serialize(),
                pod_mailbox.aes_encryption_key,
                self.message_service,
                message_type=_BitfountMessageType.OIDC_AFC_PKCE_RESPONSE,
                recipient=pod_mailbox.pod_identifier,
                recipient_mailbox_id=pod_mailbox.mailbox_id,
                sender=self.message_service.username,
                sender_mailbox_id=self.mailbox_id,
                task_id=self._task_id,
            )

    async def send_oidc_device_code_responses(
        self, device_code_details: dict[str, _PodDeviceCodeDetails]
    ) -> None:
        """Send response for OIDC Device Code Flow."""
        for pod_id, details in device_code_details.items():
            pod_mailbox = self.worker_mailboxes[pod_id]
            await _send_aes_encrypted_message(
                details.serialize(),
                pod_mailbox.aes_encryption_key,
                self.message_service,
                message_type=_BitfountMessageType.OIDC_DEVICE_CODE_RESPONSE,
                recipient=pod_mailbox.pod_identifier,
                recipient_mailbox_id=pod_mailbox.mailbox_id,
                sender=self.message_service.username,
                sender_mailbox_id=self.mailbox_id,
                task_id=self._task_id,
            )

    async def process_task_request_responses(
        self, timeout: int = _DEFAULT_TASK_RESPONSE_TIMEOUT
    ) -> dict[str, _WorkerMailboxDetails]:
        """Process incoming responses to a task request.

        Incoming responses are awaited as a group until all are received or timeout
        is reached. Responses are expected from all pods assigned at mailbox init.

        Returns:
            The subdict of this mailbox's worker mailboxes that corresponds to
            pods that accepted the task.
        """
        # Set the responses all to None to begin with and replace them with
        # messages as we receive them.
        response_messages: dict[str, Optional[_DecryptedBitfountMessage]] = {
            pod_identifier: None for pod_identifier in self._pod_identifiers
        }
        # This duplicates behaviour in task_abort_handler - review if this is necessary
        # Since the task_abort_handler raise doesn't interrupt anything (any more?)
        # and it's up to the protocol to raise an "impactful" error, I guess this
        # covers the case where the task is aborted but the protocol doesn't exist?
        task_abort: Optional[tuple[str, Optional[Reason]]] = None

        def _response_message_handler(message: _BitfountMessage) -> None:
            """Simple handler that saves messages to closured dict."""
            nonlocal task_abort
            logger.info(
                f"Received message with type: {message.message_type} "
                f"from sender: {message.sender}"
            )
            if message.message_type == _BitfountMessageType.TASK_ABORT:
                task_abort = self._process_task_abort(message)
                logger.error(
                    f"Task aborted by pod {message.sender}: {task_abort[0]}"  # noqa: E501
                )
            else:
                response_messages[message.sender] = self._decrypt_message(message)

        # Create handler for processing the group of expected responses. Using it
        # as a context manager guarantees that the handlers are correctly applied
        # and removed.
        with _AsyncMultipleResponsesHandler(
            handler=_response_message_handler,
            message_types=[
                _BitfountMessageType.JOB_ACCEPT,
                _BitfountMessageType.JOB_REJECT,
                _BitfountMessageType.TASK_ABORT,
            ],
            mailbox=self,
            responders=self._pod_identifiers,
        ) as multi_response:
            try:
                # Wait for all responses to have been received or until the
                # timeout expires.
                await multi_response.wait_for_responses(timeout=timeout)
                if task_abort is not None:
                    error_message, reason = task_abort
                    raise TaskAbortError(
                        error_message,
                        reason,
                    )
            except MessageRetrievalError as err:
                logger.error(
                    f"Error receiving responses from all pods to the task request: "
                    f"{err}"
                )
                raise BitfountTaskStartError(
                    "Failed to start task with all pods."
                ) from err

        accepted_mailbox_details = await self._handle_task_responses(response_messages)

        # Set on the attribute and return as well
        self.accepted_worker_mailboxes = accepted_mailbox_details
        return accepted_mailbox_details

    async def _handle_task_responses(
        self,
        response_messages: MutableMapping[str, Optional[_DecryptedBitfountMessage]],
    ) -> dict[str, _WorkerMailboxDetails]:
        # Want to track the various responses separately, but only care about
        # the details of the accepted ones.
        accepted_task_worker_mailboxes: dict[str, _WorkerMailboxDetails] = {}
        # These are effectively only used for counting,
        # so could be replaced with counters.
        # The only reason for creating a list of messages here
        # was in case we wanted to log these errors in future
        rejected_tasks: list[_DecryptedBitfountMessage] = []
        ignored_tasks: list[None] = []

        # Check through each of the responses
        for pod_identifier, response in response_messages.items():
            if response:
                pod_identifier = response.sender

                # Handle ACCEPT response
                if _PodResponseType.ACCEPT.name in response.body:
                    logger.info(f"Pod '{pod_identifier}' accepted request")

                    mailbox_details = self.worker_mailboxes[pod_identifier]
                    accepted_task_worker_mailboxes[pod_identifier] = mailbox_details

                    logger.debug(
                        f"Pod {pod_identifier} mailbox id is: {mailbox_details}"
                    )

                # Handle REJECT response (regardless of what form that reject takes)
                else:
                    rejected_tasks.append(response)

                    # Process different forms of rejection
                    for response_type in response.body:
                        logger.error(
                            f"Received rejection from {pod_identifier}. "
                            f"{_RESPONSE_MESSAGES[_PodResponseType[response_type]]}"  # noqa: E501
                        )

            # Handle cases where response didn't arrive
            else:
                response = cast(None, response)
                ignored_tasks.append(response)

        logger.info(
            f"{len(accepted_task_worker_mailboxes)} task(s) accepted, "
            f"{len(rejected_tasks)} rejection(s), "
            f"{len(ignored_tasks)} pod(s) did not respond in time."
        )

        return accepted_task_worker_mailboxes

    ################################
    # End Task Setup Phase Methods #
    ################################

    ##############################
    # Task Running Phase Methods #
    ##############################
    async def _send_to_all_pods_aes_encrypt(
        self, object_to_send: Any, message_type: _BitfountMessageType
    ) -> None:
        """Send message to all pods involved in a training task, AES encrypted.

        Args:
            object_to_send: Body of the message (not encrypted)
            message_type: The type of message to send
        """
        for mailbox in self.accepted_worker_mailboxes.values():
            await _send_aes_encrypted_message(
                object_to_send,
                mailbox.aes_encryption_key,
                self.message_service,
                message_type=message_type,
                recipient=mailbox.pod_identifier,
                recipient_mailbox_id=mailbox.mailbox_id,
                sender_mailbox_id=self.mailbox_id,
                sender=self.message_service.username,
                task_id=self._task_id,
            )

    async def send_training_iteration_complete_update(
        self, training_complete: bool
    ) -> None:
        """Sends whether training is complete or not to the workers."""
        logger.debug(f"Sending TRAINING_COMPLETE from {self.mailbox_id}")
        await self._send_to_all_pods_aes_encrypt(
            training_complete, _BitfountMessageType.TRAINING_COMPLETE
        )

    async def send_task_start_message(self) -> None:
        """Sends task start message to the workers.

        Note: The message is not important here, the message type is.
        """
        await self._send_to_all_pods_aes_encrypt(None, _BitfountMessageType.TASK_START)

    async def send_task_complete_message(self) -> None:
        """Sends task complete message to the workers.

        Note: The message is not important here, the message type is.
        """
        logger.info(f"Sending TASK_COMPLETE message to workers from {self.mailbox_id}")
        await self._send_to_all_pods_aes_encrypt(
            None, _BitfountMessageType.TASK_COMPLETE
        )

    def _decrypt_message(self, message: _BitfountMessage) -> _DecryptedBitfountMessage:
        """Decrypt received message using this mailbox's AES keys.

        Args:
            message: Received message to decrypt.

        Returns:
            The decrypted message body.
        """
        return message.decrypt(self.worker_mailboxes[message.sender].aes_encryption_key)

    async def get_evaluation_results_from_workers(
        self, timeout: Optional[int] = None
    ) -> _StrAnyDict:
        """Get evaluation results from workers.

        Args:
            timeout: Optional timeout for waiting for results. Defaults to None,

        Returns:
            A dictionary mapping worker identifiers to their evaluation results.

        Raises:
            TaskAbortError: If the task is aborted while waiting for results.
        """
        logger.info("Waiting to receive results from Pods...")
        # Check if batches are complete - if so, don't wait for results
        if self.batches_complete_received:
            logger.debug(
                "BATCHES_COMPLETE received - not waiting for evaluation results"
            )
            return {}

        all_eval_results: _StrAnyDict = {}

        # Create light-weight handler to append to shared list
        def evaluation_results_handler(message: _BitfountMessage) -> None:
            """Handler for evaluation results messages."""
            logger.debug(f"Receiving evaluation results from worker {message.sender}")
            eval_results = self._decrypt_message(message).body
            all_eval_results[message.sender] = eval_results

        # We use `self` rather than `self.modeller_mailbox` as the mailbox below
        # because this ensures things are correctly delegated.
        with _AsyncMultipleResponsesHandler(
            handler=evaluation_results_handler,
            message_types=_BitfountMessageType.EVALUATION_RESULTS,
            mailbox=self,
            responders=self.accepted_worker_mailboxes.keys(),
        ) as response_handler:
            await self._wait_with_abort_check(response_handler, timeout)
        return all_eval_results

    async def log(self, message: Mapping[str, object]) -> None:
        """Log message to all pods involved in task."""
        await self._send_to_all_pods_aes_encrypt(
            message, _BitfountMessageType.LOG_MESSAGE
        )

    def _setup_federated_logging(self) -> None:
        """Set up federated logging."""
        _federate_logger(self)
        self.register_handler(
            _BitfountMessageType.LOG_MESSAGE, self._get_log_message_handler()
        )

    def _get_log_message_handler(self) -> SyncHandler:
        """Create the appropriate handler for LOG_MESSAGE messages."""

        def log_message_handler(message: _BitfountMessage) -> None:
            """Locally logs the log message that has been received from a pod."""
            log_message_wrapper: _DecryptedBitfountMessage = self._decrypt_message(
                message
            )
            log_message: _JSONDict = log_message_wrapper.body

            # We prepend the name of the pod to the log message
            log_message["msg"] = f"<FROM POD {message.sender}>: {log_message['msg']}"

            # Modify processName and threadName to indicate these are non-local
            try:
                log_message["processName"] = f"<{log_message['processName']}>"
            except KeyError:
                pass
            try:
                log_message["threadName"] = f"<{log_message['threadName']}>"
            except KeyError:
                pass

            for hook in get_hooks(HookType.MODELLER):
                hook.on_log_message(message=log_message, task_id=self._task_id)
            # We remove the `federated` key to avoid recursively sending a federated
            # log message on both the Modeller and Worker sides
            log_message.pop("federated")
            logger.handle(logging.makeLogRecord(log_message))

        return log_message_handler

    def _setup_online_status_handler(self) -> None:
        """Respond to online status requests from Pods."""

        async def status_request_handler(message: _BitfountMessage) -> None:
            """Responds to an ONLINE_CHECK request with an ONLINE_RESPONSE."""
            logger.info(f"Informing {message.sender} that we are still online.")

            # We use the message service sending directly as we don't want to
            # re-encrypt the already encrypted body, we just want to send it back
            # to the worker.
            await self.message_service.send_message(
                _BitfountMessage(
                    message_type=_BitfountMessageType.ONLINE_RESPONSE,
                    body=message.body,
                    recipient=message.sender,
                    recipient_mailbox_id=message.sender_mailbox_id,
                    sender=self.message_service.username,
                    sender_mailbox_id=self.mailbox_id,
                    task_id=self._task_id,
                ),
                already_packed=True,
            )

        self.register_handler(
            _BitfountMessageType.ONLINE_CHECK,
            status_request_handler,
            high_priority=True,
        )

    def _setup_task_abort_handler(self) -> None:
        """Process TASK_ABORT message from Pods."""

        async def task_abort_handler(message: _BitfountMessage) -> None:
            """Abort the task."""
            error_message, reason = self._process_task_abort(message)
            self.abort = (error_message, reason)
            logger.info(error_message)
            raise TaskAbortError(
                error_message,
                reason,
            )

        self.register_handler(
            _BitfountMessageType.TASK_ABORT,
            task_abort_handler,
        )

    def _setup_task_start_handler(self) -> None:
        """Wait for TASK_START message from all Pods."""

        def task_start_handler(message: _BitfountMessage) -> None:
            """Simply keep track of how many Pods have sent a TASK_START message."""
            self._num_pods_ready += 1
            if self._num_pods_ready == len(self.accepted_worker_mailboxes):
                logger.info("All Pods are ready to start the task.")
                self.pods_ready = True

        self.register_handler(
            _BitfountMessageType.TASK_START,
            task_start_handler,
        )

    def _setup_batches_complete_handler(self) -> None:
        """Set up handler for BATCHES_COMPLETE messages."""

        def batches_complete_handler(message: _BitfountMessage) -> None:
            """Handle BATCHES_COMPLETE message."""
            completion_state = self._decrypt_message(message).body
            if completion_state is None:
                completion_state = "TASK_COMPLETE"

            worker_id = message.sender
            logger.debug(f"Received BATCHES_COMPLETE from worker {message.sender}")

            if completion_state == "BATCHES_ONLY":
                # Worker finished batches, starting resilience
                logger.info(
                    f"Worker {worker_id} completed batches, starting resilience phase"
                )
                self.workers_batch_complete.add(worker_id)
                self.workers_in_resilience.add(worker_id)
                return

            elif completion_state == "TASK_COMPLETE":
                # Worker finished everything including resilience
                logger.info(f"Worker {worker_id} completed task including resilience")
                self.workers_batch_complete.add(
                    worker_id
                )  # In case it wasn't added before
                self.workers_in_resilience.discard(worker_id)  # Remove from resilience
                self.completed_workers.add(worker_id)

                # Only mark as complete when ALL workers have completed
                if len(self.completed_workers) == len(self.accepted_worker_mailboxes):
                    logger.info("All workers have completed tasks including resilience")
                    self.batches_complete_received = True

        self.register_handler(
            _BitfountMessageType.BATCHES_COMPLETE,
            batches_complete_handler,
        )

    def _setup_batch_count_update_handler(self) -> None:
        """Set up handler for ongoing NUMBER_OF_BATCHES updates during streaming."""

        def batch_count_update_handler(message: _BitfountMessage) -> None:
            """Handle updated batch count messages during streaming execution."""
            logger.debug(f"Received batch count update from worker {message.sender}")
            # Deliberate access to private method here as that method shouldn't be used
            # in any other context than transport layer access.
            # noinspection PyProtectedMember
            updated_batch_count: int = self._decrypt_message(message).body

            # Only accept positive batch counts (not the initial -1)
            if updated_batch_count > 0:
                self._current_total_batches = updated_batch_count
                logger.info(
                    f"Updated total batch estimate: {updated_batch_count} batches"
                )

        self.register_handler(
            _BitfountMessageType.NUMBER_OF_BATCHES,
            batch_count_update_handler,
        )

    async def _check_abort_and_batches_complete(self) -> None:
        """Check for task abort and batches complete in a loop."""
        while True:
            if self.abort is not None:
                error_message, reason = self.abort
                raise TaskAbortError(error_message, reason)
            # Also check BATCHES_COMPLETE to stop waiting if received
            # as this is sent when the pod has finished processing all
            # the batches and finished running on the last batch
            if self.batches_complete_received:
                logger.debug(
                    "BATCHES_COMPLETE received during wait. Stopping operation wait"
                )
                return
            await asyncio.sleep(0.1)

    async def _wait_with_abort_check(
        self,
        response_handler: _AsyncMultipleResponsesHandler,
        timeout: Optional[int] = None,
        check_batches_complete: bool = True,
    ) -> None:
        """Wait for responses while checking for abort conditions.

        Args:
            response_handler: The response handler to wait for
            timeout: Optional timeout for the wait
            check_batches_complete: Whether to check for batches complete condition
        """
        # Create tasks for both waiting for responses and checking for abort
        wait_task = asyncio.create_task(
            response_handler.wait_for_responses(timeout=timeout)
        )

        if check_batches_complete:
            abort_check_task = asyncio.create_task(
                self._check_abort_and_batches_complete()
            )
        else:
            # Simple abort check without batches complete
            async def simple_abort_check() -> None:
                while True:
                    if self.abort is not None:
                        error_message, reason = self.abort
                        raise TaskAbortError(error_message, reason)
                    await asyncio.sleep(0.1)

            abort_check_task = asyncio.create_task(simple_abort_check())

        try:
            # Wait for either task to complete
            done, pending = await asyncio.wait(
                [wait_task, abort_check_task], return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel the pending task
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            # Re-raise any exceptions
            for task in done:
                await task

        except asyncio.CancelledError:
            raise
        except Exception:
            raise

    async def get_num_batches_message(self, timeout: Optional[int] = None) -> int:
        """Get number of batches from worker for batched execution.

        This is intended to be used for batched execution, where the number of batches
        is not known in advance by the modeller so the modeller must get it from the
        worker. Batched execution is only supported in cases where there is only one
        worker.

        Args:
            modeller_mailbox: The modeller mailbox.
            timeout: The timeout for the request.

        Returns:
            A number of batches.

        Raises:
            ValueError: If the number of responses is not 1.
            TaskAbortError: If the task is aborted while waiting.
        """
        num_batches_list: list[int] = []

        def batched_execution_handler(message: _BitfountMessage) -> None:
            """Handler for number of batches update messages."""
            logger.debug(
                f"Receiving number of batches update from worker {message.sender}"
            )
            # Deliberate access to private method here as that method shouldn't be used
            # in any other context than transport layer access.
            # noinspection PyProtectedMember
            num_batches: int = self._decrypt_message(message).body
            num_batches_list.append(num_batches)

        with _AsyncMultipleResponsesHandler(
            handler=batched_execution_handler,
            message_types=_BitfountMessageType.NUMBER_OF_BATCHES,
            mailbox=self,
            responders=self.accepted_worker_mailboxes.keys(),
        ) as response_handler:
            await self._wait_with_abort_check(
                response_handler, timeout, check_batches_complete=False
            )

        if len(num_batches_list) != len(self._pod_identifiers):
            raise ValueError(
                f"Expected {len(self._pod_identifiers)} response from worker "
                f"for number of batches, got {len(num_batches_list)}"
            )
        return max(num_batches_list)

    async def get_current_batch_id_message(
        self, timeout: Optional[int] = None
    ) -> Optional[int]:
        """Get the current batch id from worker for batched execution.

        This is intended to be used for batched execution, where the number of batches
        is not known in advance by the modeller so the modeller must get it from the
        worker. Batched execution is only supported in cases where there is only one
        worker.

        Args:
            timeout: The timeout for the request.

        Returns:
            The current batch ID from the worker(s).

        Raises:
            ValueError: If no responses are received or if there's
                a communication issue.
            TaskAbortError: If the task is aborted while waiting.
        """
        # Only expect batch IDs from workers that haven't completed yet
        active_workers = (
            set(self.accepted_worker_mailboxes.keys()) - self.completed_workers
        )

        if not active_workers:
            # All workers have completed
            logger.debug("All workers have completed, no active workers remaining")
            return -1
        logger.debug(
            f"Waiting for batch IDs from {len(active_workers)} "
            f"active workers: {active_workers}"
        )
        max_retries = 3
        backoff = 5
        current_batch_id_list: list[int] = []

        for attempt in range(max_retries):
            logger.debug(
                f"Attempting to get batch ID (attempt {attempt + 1}/{max_retries})"
            )

            # Define a handler to process the responses
            def batched_execution_handler(message: _BitfountMessage) -> None:
                """Handler for current batch ID update messages."""
                logger.debug(
                    f"Receiving the current batch id update from worker "
                    f"{message.sender}"
                )
                # Deliberate access to private method here as that method
                # shouldn't be used in any other context than transport
                # layer access.
                # noinspection PyProtectedMember
                current_batch: int = self._decrypt_message(message).body
                current_batch_id_list.append(current_batch)

            try:
                with _AsyncMultipleResponsesHandler(
                    handler=batched_execution_handler,
                    message_types=_BitfountMessageType.CURRENT_BATCH_ID,
                    mailbox=self,
                    responders=active_workers,
                ) as response_handler:
                    await self._wait_with_abort_check(response_handler, timeout)
                if current_batch_id_list:
                    if len(current_batch_id_list) != len(active_workers):
                        received_count = len(current_batch_id_list)
                        expected_count = len(active_workers)
                        logger.warning(
                            f"Expected batch IDs from {expected_count} active workers, "
                            f"but only received {received_count}"
                        )
                    min_batch_id = min(current_batch_id_list)
                    if len(active_workers) > 1:
                        logger.debug(
                            f"Multiple workers active. Received batch IDs: "
                            f"{current_batch_id_list}. Using minimum (slowest worker): "
                            f"{min_batch_id}"
                        )
                    return min_batch_id
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1}")
            except TaskAbortError:
                # Don't retry on abort
                raise

            except Exception as e:
                logger.warning(f"Error on attempt {attempt + 1}: {e}")

            # Check if batches completed during this attempt
            if self.batches_complete_received:
                return -1
            if not current_batch_id_list and attempt < max_retries - 1:
                logger.warning(
                    f"No batch ID received, retrying... ({attempt + 1}/{max_retries})"
                )
                await asyncio.sleep(backoff)
        if not self.batches_complete_received:
            logger.error(
                "No batch ID received after maximum retries. "
                "Workers might be unresponsive."
            )
            return None
        else:
            logger.warning("No current batch ID received, but batches are complete")
            return -1

    def _process_task_abort(
        self, message: _BitfountMessage
    ) -> tuple[str, Optional[Reason]]:
        """Process TASK_ABORT message."""
        # Parse body
        task_abort_message_body: Union[str, TaskAbortBody, None] = (
            self._decrypt_message(message).body
        )
        maybe_message: Optional[str] = None
        maybe_reason: Optional[ReasonString] = None
        if isinstance(task_abort_message_body, str):
            # Backward compatibility with pods running an old SDK
            maybe_message = task_abort_message_body
        elif task_abort_message_body is not None:
            maybe_message = task_abort_message_body.get("message")
            maybe_reason = task_abort_message_body.get("reason")

        error_message = f"Received TASK_ABORT message from {message.sender}"
        if maybe_message is not None:
            error_message = f"{error_message}: {maybe_message}"

        return (
            error_message,
            Reason[maybe_reason] if maybe_reason is not None else None,
        )

    ##################################
    # End Task Running Phase Methods #
    ##################################


async def _send_model_parameters(
    model_parameters: _SerializedWeights, modeller_mailbox: _ModellerMailbox
) -> None:
    """Sends model parameters to the workers."""
    # Deliberate access to private method here as that method shouldn't be used in
    # any other context than transport layer access.
    # noinspection PyProtectedMember
    await modeller_mailbox._send_to_all_pods_aes_encrypt(
        model_parameters, _BitfountMessageType.MODEL_PARAMETERS
    )


async def _send_prompt(prompt: str, modeller_mailbox: _ModellerMailbox) -> None:
    """Sends model parameters to the workers."""
    # Deliberate access to private method here as that method shouldn't be used in
    # any other context than transport layer access.
    # noinspection PyProtectedMember
    await modeller_mailbox._send_to_all_pods_aes_encrypt(
        prompt, _BitfountMessageType.MODEL_PROMPT
    )


def _training_metrics_handler(
    modeller_mailbox: _ModellerMailbox,
    training_metrics: MutableSequence[Mapping[str, str]],
) -> SyncHandler:
    """Training metrics handler.

    Will mutate the passed in sequence by appending responses to it.

    Note that there is no notion of "worker order" in this list, the elements are
    in the order they are received.
    """

    def training_metrics_handler(message: _BitfountMessage) -> None:
        """Training metrics handler."""
        logger.debug(f"Receiving training metrics update from worker {message.sender}")
        # Deliberate access to private method here as that method shouldn't be used in
        # any other context than transport layer access.
        # noinspection PyProtectedMember
        single_training_metrics: Mapping[str, str] = modeller_mailbox._decrypt_message(
            message
        ).body
        training_metrics.append(single_training_metrics)

    return training_metrics_handler


async def _get_training_metrics_from_workers(
    modeller_mailbox: _ModellerMailbox,
    timeout: Optional[int] = None,
) -> dict[str, float]:
    """Get average training metrics from workers."""
    training_metrics: list[Mapping[str, str]] = []
    training_metrics_handler = _training_metrics_handler(
        modeller_mailbox, training_metrics
    )
    with _AsyncMultipleResponsesHandler(
        handler=training_metrics_handler,
        message_types=_BitfountMessageType.TRAINING_METRICS,
        mailbox=modeller_mailbox,
        responders=modeller_mailbox.accepted_worker_mailboxes.keys(),
    ) as response_handler:
        non_responders = await response_handler.wait_for_responses(timeout=timeout)
        if non_responders:
            logger.info(
                f"The following did not send training metrics in time: {non_responders}"
            )

    # Find the average metrics for those who responded and return
    averaged_training_metrics = _average_training_metrics(training_metrics)
    return averaged_training_metrics


def _parameter_updates_handler(
    modeller_mailbox: _ModellerMailbox,
    weight_updates: MutableMapping[str, _SerializedWeights],
) -> SyncHandler:
    """Parameter update handler.

    Will mutate the passed in mapping by appending responses to it.
    """

    def parameter_update_handler(message: _BitfountMessage) -> None:
        """Parameter update handler."""
        logger.debug(f"Receiving parameter update from worker {message.sender}")
        # Deliberate access to private method here as that method shouldn't be used in
        # any other context than transport layer access.
        # noinspection PyProtectedMember
        weight_update = modeller_mailbox._decrypt_message(message).body
        sender = message.sender
        weight_updates[sender] = weight_update

    return parameter_update_handler


async def _get_parameter_updates_from_workers(
    modeller_mailbox: _ModellerMailbox, timeout: Optional[int] = None
) -> dict[str, _SerializedWeights]:
    """Get model parameter updates from workers.

    Args:
        modeller_mailbox: The modeller mailbox.
        timeout: The timeout for the request.

    Returns:
        A dictionary of the form {worker_name: weight_update}.
    """
    weight_updates: dict[str, _SerializedWeights] = {}
    parameter_updates_handler = _parameter_updates_handler(
        modeller_mailbox, weight_updates
    )

    with _AsyncMultipleResponsesHandler(
        handler=parameter_updates_handler,
        message_types=_BitfountMessageType.TRAINING_UPDATE,
        mailbox=modeller_mailbox,
        responders=modeller_mailbox.accepted_worker_mailboxes.keys(),
    ) as response_handler:
        await response_handler.wait_for_responses(timeout=timeout)

    return weight_updates


def _model_responses_handler(
    modeller_mailbox: _ModellerMailbox,
    model_responses: MutableMapping[str, list[dict[str, str]]],
) -> SyncHandler:
    """Model response handler.

    Will mutate the passed in mapping by appending responses to it.
    """

    def model_responses_handler(message: _BitfountMessage) -> None:
        """Handler for model response messages."""
        logger.debug(f"Receiving model response from worker {message.sender}")
        # Deliberate access to private method here as that method shouldn't be used in
        # any other context than transport layer access.
        # noinspection PyProtectedMember
        model_response = modeller_mailbox._decrypt_message(message).body
        sender = message.sender
        model_responses[sender] = model_response

    return model_responses_handler


async def _get_model_responses_from_workers(
    modeller_mailbox: _ModellerMailbox, timeout: Optional[int] = None
) -> dict[str, list[dict[str, str]]]:
    """Get model responses from workers.

    Args:
        modeller_mailbox: The modeller mailbox.
        timeout: The timeout for the request.

    Returns:
        A dictionary of the form {worker_name: model_response}.
    """
    model_responses: dict[str, list[dict[str, str]]] = {}
    model_responses_handler = _model_responses_handler(
        modeller_mailbox, model_responses
    )
    with _AsyncMultipleResponsesHandler(
        handler=model_responses_handler,
        message_types=_BitfountMessageType.MODEL_RESPONSE,
        mailbox=modeller_mailbox,
        responders=modeller_mailbox.accepted_worker_mailboxes.keys(),
    ) as response_handler:
        await response_handler.wait_for_responses(timeout=timeout)

    return model_responses
