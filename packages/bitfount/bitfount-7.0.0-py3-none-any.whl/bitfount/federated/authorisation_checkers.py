"""Authorisation Checkers."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Mapping
import dataclasses
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Final,
    List,
    Optional,
    Protocol,
    TypeVar,
    Union,
)

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
import requests
from requests import HTTPError, RequestException, Response
from requests.exceptions import InvalidJSONError

from bitfount import config
from bitfount.encryption.encryption import _RSAEncryption
from bitfount.federated.helper import TaskContext
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.pod_response_message import _PodResponseMessage
from bitfount.federated.task_requests import (
    _EncryptedTaskRequest,
    _SignedEncryptedTaskRequest,
    _TaskRequest,
    _TaskRequestMessage,
)
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.federated.types import (
    AccessCheckResult,
    SerializedProtocol,
    _PodResponseType,
    _TaskRequestMessageGenerator,
)
from bitfount.hub.authentication_flow import _get_auth_environment
from bitfount.hub.authentication_handlers import (
    _AUTHORIZATION_PENDING_ERROR,
    _SLOW_DOWN_ERROR,
)
from bitfount.hub.types import (
    _AMResourceUsageAndLimitJSON,
    _DeviceAccessTokenFailResponseJSON,
    _DeviceAccessTokenRequestDict,
    _DeviceAccessTokenResponseJSON,
    _PKCEAccessTokenRequestDict,
    _PKCEAccessTokenResponseJSON,
)
from bitfount.types import _S3PresignedURL
from bitfount.utils import web_utils

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountAM
logger = _get_federated_logger(__name__)

# This forces `requests` to make IPv4 connections
# TODO: [BIT-1443] Remove this once Hub/AM support IPv6
requests.packages.urllib3.util.connection.HAS_IPV6 = False  # type: ignore[attr-defined] # Reason: see above # noqa: E501


class IdentityVerificationMethod(Enum):
    """Allowed types of identity verification."""

    KEYS = "key-based"
    OIDC_ACF_PKCE = "oidc-auth-code"
    OIDC_DEVICE_CODE = "oidc-device-code"

    DEFAULT = OIDC_DEVICE_CODE


#: Allowed types of identity verification as a tuple of strings
IDENTITY_VERIFICATION_METHODS: Final[tuple[str, ...]] = tuple(
    i.value for i in IdentityVerificationMethod
)
#: Default identity verification method
DEFAULT_IDENTITY_VERIFICATION_METHOD: Final[str] = (
    IdentityVerificationMethod.DEFAULT.value
)


def check_identity_verification_method(
    method: Union[str, IdentityVerificationMethod],
) -> IdentityVerificationMethod:
    """Checks that the verification method is supported."""
    try:
        return IdentityVerificationMethod(method)
    except ValueError as e:
        raise ValueError(f"Unsupported identity verification method: {method}") from e


_M_co = TypeVar("_M_co", covariant=True)


@dataclass
class InferenceLimits:
    """Container class for model inference usage limits.

    Attributes:
        limit: The total number of inferences that can be performed.
        total_usage: The total number of inferences performed so far.
    """

    limit: int
    total_usage: int
    _initial_total_usage: int = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self._initial_total_usage = self.total_usage

    @property
    def initial_total_usage(self) -> int:
        """Returns the total usage that was set when this instance was created."""
        return self._initial_total_usage

    @classmethod
    def from_access_check_result(
        cls, access_check_result: AccessCheckResult
    ) -> dict[str, InferenceLimits]:
        """Construct model name -> inference usage limits from access check results.

        If a model usage `limit` is `undefined` or not present, this indicates that
        there is no usage limit, and so we do not add this to the constructed dict.

        Returns:
            Dictionary of full model name (e.g. "some-model-owner/some-model:12"
            to the model inference usage limits for that model as detailed in
            `access_check_results`).
        """
        limits: Optional[list[_AMResourceUsageAndLimitJSON]] = access_check_result[
            "limits"
        ]
        if not limits:
            return {}
        else:
            limits_dict: dict[str, InferenceLimits] = {}
            for d in limits:
                if d["resourceType"] == "MODEL_INFERENCE":
                    # If a model usage `limit` is `undefined` or not present,
                    # this indicates that there is no usage limit, and so we do not
                    # add this to the constructed dict.
                    limit: Optional[int] = d.get("limit", None)
                    if limit is not None:
                        limits_dict[d["resourceName"]] = InferenceLimits(
                            limit=limit, total_usage=d["totalUsage"]
                        )
            return limits_dict


@dataclass
class ModelURLs:
    """Container class for model download URLs from the authorisation checker.

    Attributes:
        model_download_url: URL for downloading the model code.
        model_weights_url: URL for downloading the model weights.
    """

    model_download_url: _S3PresignedURL
    model_weights_url: _S3PresignedURL | None
    # TODO: [BIT-4857] Add model hash information here

    @classmethod
    def from_access_check_result(
        cls, access_check_result: AccessCheckResult
    ) -> dict[str, ModelURLs]:
        """Construct model name -> model download URLs from access check results.

        Returns:
            Dictionary of full model name/id (e.g. "some-model-owner/some-model:12"
            to the model download URL and/or model weights URL for that model as
            detailed in `access_check_results`).
        """
        limits: Optional[list[_AMResourceUsageAndLimitJSON]] = access_check_result[
            "limits"
        ]
        if not limits:
            return {}
        else:
            model_urls_dict: dict[str, ModelURLs] = {}
            for d in limits:
                if d["resourceType"] == "MODEL_INFERENCE":
                    # Only add the model URLs information to the dict if it has
                    # a download URL (it may optionally also have a weights URL)
                    model_download_url: Optional[_S3PresignedURL] = (
                        _S3PresignedURL(url)
                        if (url := d.get("modelDownloadUrl", None)) is not None
                        else None
                    )
                    if model_download_url:
                        model_weights_url: Optional[_S3PresignedURL] = (
                            _S3PresignedURL(url)
                            if (url := d.get("weightsDownloadUrl", None)) is not None
                            else None
                        )
                        model_urls_dict[d["resourceName"]] = ModelURLs(
                            model_download_url=model_download_url,
                            model_weights_url=model_weights_url,
                        )
            return model_urls_dict


@dataclass
class ProtocolContext:
    """Details needed for the protocol at runtime.

    Attributes:
        inference_limits: A mapping of model name (full name, including owner and
            version) to the inference limits information for that model.
            e.g. `{"some-model-owner/some-model:12": {"limit": 90, "total_usage": 10}}`
        task_context: Optional. Which context (modeller or worker) the task is running
            in.
    """

    inference_limits: dict[str, InferenceLimits] = dataclasses.field(
        default_factory=dict
    )
    model_urls: dict[str, ModelURLs] = dataclasses.field(default_factory=dict)
    task_context: Optional[TaskContext] = None


@dataclass
class AuthCheckResponse:
    """Response regarding an authentication check.

    Contains information on whether the task is allowed to run, as well as any other
    run-time details needed by the task that are provided by the access manager.

    Attributes:
        pod_response_message: The response of the pod to the task request. Contains
            information on the modeller, pod, and any messages related to why the task
            was rejected (if applicable).
        protocol_context: Details needed for the protocol at runtime, such as usage
            limits, etc.
    """

    pod_response_message: _PodResponseMessage
    protocol_context: ProtocolContext


class _AuthorisationChecker(Protocol[_M_co]):
    """Protocol for checking authorisation.

    This is a simple protocol for checking authorisation. It's used to inform a decision
    on whether a Pod accepts or rejects a job.
    """

    serialized_protocol: SerializedProtocol

    @classmethod
    def create_task_request_message_generator(
        cls,
    ) -> _TaskRequestMessageGenerator:
        """Creates a callable that can be used to generate task request messages."""
        ...

    @classmethod
    def extract_from_task_request_message(
        cls, task_request_message: Union[bytes, _TaskRequestMessage]
    ) -> _M_co:
        """Extract the packed task request details from the task request message.

        Args:
            task_request_message: The task request message, either packed as bytes
                or unpacked.

        Returns:
            The packed task request details, in the dataclass relevant for this
            authorisation checker.
        """
        ...

    @classmethod
    def unpack_task_request(
        cls, msg: Union[bytes, _TaskRequestMessage], pod_private_key: RSAPrivateKey
    ) -> _TaskRequest:
        """Unpacks/decrypts the task request details from the task request message.

        Args:
            msg: The task request message, either packed as bytes or unpacked.
            pod_private_key: The pod's RSA private key, for decryption.
        """
        ...

    async def check_authorisation(self) -> AuthCheckResponse:
        """Check if the task should be executed or not."""
        ...

    def _additional_messages_for_limits(
        self, access_check_result: AccessCheckResult
    ) -> Optional[List[str]]:
        limits = access_check_result.get("limits")
        if (
            limits is not None
            and access_check_result["response_type"] == _PodResponseType.NO_ACCESS
        ):
            additional_messages = []
            for resource in limits:
                try:
                    # If a model usage `limit` is `undefined` or not present,
                    # this indicates that there is no usage limit, and so we do not
                    # consider this for the messaging
                    limit: Optional[int] = resource.get("limit", None)
                    if limit is None:
                        continue

                    if resource["totalUsage"] >= limit:
                        # when we support other resources will need to read resourceType
                        model_slug = resource["resourceName"]
                        msg = f"Usage of model {model_slug} is above allowed limit"
                        additional_messages.append(msg)
                except KeyError:
                    logger.warning(
                        (
                            "Could not process resource limit response from AM: "
                            f"{resource}"
                        )
                    )
            if len(additional_messages) > 0:
                return additional_messages

        return None


def _make_encrypted_task_request_message(
    auth_type: IdentityVerificationMethod,
    serialized_protocol: SerializedProtocol,
    pod_identifiers: list[str],
    aes_key: bytes,
    pod_public_key: RSAPublicKey,
    project_id: Optional[str],
    run_on_new_data_only: bool = False,
    batched_execution: Optional[bool] = None,
    test_run: bool = False,
    force_rerun_failed_files: bool = True,
) -> bytes:
    """Common function for generating messages with _EncryptedTaskRequest contents."""
    # Create task request
    tr = _TaskRequest(serialized_protocol, pod_identifiers, aes_key)
    # Set batched execution based on env variable
    if batched_execution is None:
        batched_execution = config.settings.default_batched_execution
    # Encrypt and pack in class
    packed_tr = _EncryptedTaskRequest(
        _RSAEncryption.encrypt(tr.serialize(), pod_public_key)
    )

    # Create outer message
    message = _TaskRequestMessage(
        serialized_protocol,
        auth_type.value,
        packed_tr.serialize(),
        project_id,
        run_on_new_data_only,
        batched_execution,
        test_run=test_run,
        force_rerun_failed_files=force_rerun_failed_files,
    )
    return message.serialize()


def _extract_encrypted_task_request(
    task_request_message: Union[bytes, _TaskRequestMessage],
) -> _EncryptedTaskRequest:
    """Extract _EncryptedTaskRequest from _TaskRequestMessage."""
    # Deserialize outer message if provided as bytes
    if isinstance(task_request_message, bytes):
        task_request_message = _TaskRequestMessage.deserialize(task_request_message)

    # Deserialize inner _EncryptedTaskRequest
    packed_task_request = _EncryptedTaskRequest.deserialize(
        task_request_message.request
    )

    return packed_task_request


def _unpack_task_request(
    msg: Union[bytes, _TaskRequestMessage],
    pod_private_key: RSAPrivateKey,
    extract_from_task_request_message: Union[
        Callable[[Union[bytes, _TaskRequestMessage]], _EncryptedTaskRequest],
        Callable[[Union[bytes, _TaskRequestMessage]], _SignedEncryptedTaskRequest],
    ],
) -> _TaskRequest:
    """Function for common behaviour to fully unpack _TaskRequest message.

    Args:
        msg: The _TaskRequestMessage, maybe serialized as bytes.
        pod_private_key: The RSA private key of the pod.
        extract_from_task_request_message:
            Callable that will extract the packed task request from the
            _TaskRequestMessage.

    Returns:
        The unpacked task request.
    """
    if isinstance(msg, bytes):
        msg = _TaskRequestMessage.deserialize(msg)
    packed_task_request = extract_from_task_request_message(msg)
    task_request = _TaskRequest.deserialize(
        _RSAEncryption.decrypt(packed_task_request.encrypted_request, pod_private_key)
    )
    return task_request


@dataclass
class _SignatureBasedAuthorisation(_AuthorisationChecker[_SignedEncryptedTaskRequest]):
    """Task authorisation using Signatures.

    Checks whether the Modeller provided signature of the task
    can be verified against the modeller's public key.
    """

    pod_response_message: _PodResponseMessage
    access_manager: BitfountAM
    modeller_name: str
    encrypted_task_request: bytes
    signature: bytes
    serialized_protocol: SerializedProtocol
    project_id: Optional[str] = None
    key_id: Optional[str] = None

    @dataclass
    class _SignedMessageMaker:
        private_key: RSAPrivateKey
        key_id: str

        def generate_task_request_message(
            self,
            serialized_protocol: SerializedProtocol,
            pod_identifiers: list[str],
            aes_key: bytes,
            pod_public_key: RSAPublicKey,
            project_id: Optional[str] = None,
            run_on_new_data_only: bool = False,
            batched_execution: Optional[bool] = None,
            test_run: bool = False,
            force_rerun_failed_files: bool = True,
        ) -> bytes:
            tr = _TaskRequest(serialized_protocol, pod_identifiers, aes_key)
            if batched_execution is None:
                batched_execution = config.settings.default_batched_execution
            try:
                serialized_tr = tr.serialize()
            except Exception as e:
                logger.error(
                    f"Unable to serialize task request: {str(e)}", exc_info=True
                )
                logger.error(f"Serialized protocol was: {serialized_protocol}")
                raise
            encrypted_tr = _RSAEncryption.encrypt(serialized_tr, pod_public_key)
            signature = _RSAEncryption.sign_message(self.private_key, encrypted_tr)
            packed_tr = _SignedEncryptedTaskRequest(encrypted_tr, signature)

            message = _TaskRequestMessage(
                serialized_protocol,
                IdentityVerificationMethod.KEYS.value,
                packed_tr.serialize(),
                project_id,
                run_on_new_data_only,
                batched_execution,
                self.key_id,
                test_run=test_run,
                force_rerun_failed_files=force_rerun_failed_files,
            )
            return message.serialize()

    # This is an intentional LSP violation as this class is (currently) the only
    # one with a special create_task_request_message_generator method. As the base
    # class is a Protocol, it cannot be instantiated (so an end-user won't
    # accidentally end up with a different create_task_request_message_generator
    # signature) and for the cases where we need to call this version of the method
    # we can assuage static typing with an isinstance or cast against this class.
    #
    # If more classes appear with different create_task_request_message_generator
    # signatures then we should split the signatures out into their own protocols.
    @classmethod
    def create_task_request_message_generator(  # type: ignore[override] # Reason: see comment # noqa: E501
        cls, modeller_private_key: RSAPrivateKey, key_id: str
    ) -> _TaskRequestMessageGenerator:
        return cls._SignedMessageMaker(
            modeller_private_key, key_id
        ).generate_task_request_message

    @classmethod
    def extract_from_task_request_message(
        cls, task_request_message: Union[bytes, _TaskRequestMessage]
    ) -> _SignedEncryptedTaskRequest:
        if isinstance(task_request_message, bytes):
            task_request_message = _TaskRequestMessage.deserialize(task_request_message)
        packed_task_request = _SignedEncryptedTaskRequest.deserialize(
            task_request_message.request
        )
        return packed_task_request

    @classmethod
    def unpack_task_request(
        cls, msg: Union[bytes, _TaskRequestMessage], pod_private_key: RSAPrivateKey
    ) -> _TaskRequest:
        return _unpack_task_request(
            msg, pod_private_key, cls.extract_from_task_request_message
        )

    def _check_access(self) -> AccessCheckResult:
        """Check that access is allowed for the authorised user and request."""
        return self.access_manager.check_signature_based_access_request(
            unsigned_task=self.encrypted_task_request,
            task_signature=self.signature,
            pod_identifier=self.pod_response_message.pod_identifier,
            serialized_protocol=self.serialized_protocol,
            modeller_name=self.modeller_name,
            project_id=self.project_id,
            public_key_id=self.key_id,
        )

    async def check_authorisation(self) -> AuthCheckResponse:
        """Check signature matches modeller public key."""
        result = self._check_access()
        additional_messages = self._additional_messages_for_limits(result)

        self.pod_response_message.add(
            response_type=result["response_type"],
            additional_messages=additional_messages,
        )

        return AuthCheckResponse(
            pod_response_message=self.pod_response_message,
            protocol_context=ProtocolContext(
                inference_limits=InferenceLimits.from_access_check_result(result),
                model_urls=ModelURLs.from_access_check_result(result),
            ),
        )


@dataclass
class _OIDCAuthorisationCode(_AuthorisationChecker[_EncryptedTaskRequest]):
    """OIDC Authorisation Code Flow with PKCE.

    See: https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-proof-key-for-code-exchange-pkce
    """  # noqa: E501

    pod_response_message: _PodResponseMessage
    access_manager: BitfountAM
    mailbox: _WorkerMailbox
    serialized_protocol: SerializedProtocol
    project_id: Optional[str] = None

    # Auth-related params
    _auth_domain: str = None  # type: ignore[assignment] # Reason: filled in __post_init__ if not provided # noqa: E501
    _client_id: str = None  # type: ignore[assignment] # Reason: filled in __post_init__ if not provided # noqa: E501

    def __post_init__(self) -> None:
        # Fill auth-related attributes if not provided
        auth_env = _get_auth_environment()
        if not self._auth_domain:
            self._auth_domain = auth_env.auth_domain
        if not self._client_id:
            self._client_id = auth_env.client_id

        self._token_endpoint: str = f"https://{self._auth_domain}/oauth/token"

    @classmethod
    def _generate_task_request_message(
        cls,
        serialized_protocol: SerializedProtocol,
        pod_identifiers: list[str],
        aes_key: bytes,
        pod_public_key: RSAPublicKey,
        project_id: Optional[str],
        run_on_new_data_only: bool = False,
        batched_execution: Optional[bool] = None,
        test_run: bool = False,
        force_rerun_failed_files: bool = True,
    ) -> bytes:
        if batched_execution is None:
            batched_execution = config.settings.default_batched_execution
        return _make_encrypted_task_request_message(
            IdentityVerificationMethod.OIDC_ACF_PKCE,
            serialized_protocol,
            pod_identifiers,
            aes_key,
            pod_public_key,
            project_id,
            run_on_new_data_only,
            batched_execution,
            test_run=test_run,
            force_rerun_failed_files=force_rerun_failed_files,
        )

    @classmethod
    def create_task_request_message_generator(
        cls,
    ) -> _TaskRequestMessageGenerator:
        return cls._generate_task_request_message

    @classmethod
    def extract_from_task_request_message(
        cls, task_request_message: Union[bytes, _TaskRequestMessage]
    ) -> _EncryptedTaskRequest:
        return _extract_encrypted_task_request(task_request_message)

    @classmethod
    def unpack_task_request(
        cls, msg: Union[bytes, _TaskRequestMessage], pod_private_key: RSAPrivateKey
    ) -> _TaskRequest:
        return _unpack_task_request(
            msg, pod_private_key, cls.extract_from_task_request_message
        )

    async def check_authorisation(self) -> AuthCheckResponse:
        """Perform OIDC flow from the pod-side.

        This flow is based on:
        https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-proof-key-for-code-exchange-pkce
        """  # noqa: E501
        # Retrieve client ID for pod and send to modeller
        client_id = self._get_client_id()
        await self.mailbox.send_oidc_client_id(client_id)

        # Wait for authorization code and code verifier
        response = await self.mailbox.get_oidc_auth_flow_response()

        # Get access token
        modeller_access_token = self._get_access_token(
            response.auth_code, response.code_verifier, response.redirect_uri
        )

        # Check with Access Manager that user matches expected identity
        # and that the user has the correct permissions for the task
        # that they have requested.
        authentication_result: AccessCheckResult = self._check_access(
            modeller_access_token
        )
        response_type = authentication_result["response_type"]

        logger.info(
            "OIDC authorisation check complete. "
            f"Will inform modeller: {response_type.name}"
        )
        additional_messages = self._additional_messages_for_limits(
            authentication_result
        )
        self.pod_response_message.add(
            response_type=response_type,
            additional_messages=additional_messages,
        )
        return AuthCheckResponse(
            pod_response_message=self.pod_response_message,
            protocol_context=ProtocolContext(
                inference_limits=InferenceLimits.from_access_check_result(
                    authentication_result
                ),
                model_urls=ModelURLs.from_access_check_result(authentication_result),
            ),
        )

    def _get_client_id(self) -> str:
        """Retrieve client ID for pod."""
        # Note: Currently this just returns the static client ID used throughout.
        #       If we change to using Dynamic Client Registration (https://auth0.com/docs/api/authentication#dynamic-application-client-registration)  # noqa: E501
        #       we should change what is returned by this method
        return self._client_id

    def _get_access_token(
        self,
        auth_code: str,
        code_verifier: str,
        redirect_uri: str,
    ) -> str:
        """Request access token from oauth endpoint."""
        # POST to endpoint to exchange for access token.
        # See: https://auth0.com/docs/api/authentication?http#authorization-code-flow-with-pkce45  # noqa: E501
        request_data: _PKCEAccessTokenRequestDict = {
            "grant_type": "authorization_code",
            "client_id": self._client_id,
            "code": auth_code,
            "code_verifier": code_verifier,
            "redirect_uri": redirect_uri,
        }
        response: Response = web_utils.post(
            self._token_endpoint,
            data=request_data,
            timeout=20,
        )
        response.raise_for_status()

        # Handle good response
        response_json: _PKCEAccessTokenResponseJSON = response.json()
        return response_json["access_token"]

    def _check_access(self, modeller_access_token: str) -> AccessCheckResult:
        """Check that access is allowed for the authorised user and request."""
        return self.access_manager.check_oidc_access_request(
            self.pod_response_message.pod_identifier,
            self.serialized_protocol,
            self.mailbox.modeller_name,
            modeller_access_token,
            project_id=self.project_id,
        )


@dataclass
class _OIDCDeviceCode(_AuthorisationChecker[_EncryptedTaskRequest]):
    """OIDC Device Authorisation Flow from pod-side.

    See: https://auth0.com/docs/get-started/authentication-and-authorization-flow/device-authorization-flow
    """  # noqa: E501

    pod_response_message: _PodResponseMessage
    access_manager: BitfountAM
    mailbox: _WorkerMailbox
    serialized_protocol: SerializedProtocol
    project_id: Optional[str] = None

    # Auth-related params
    _auth_domain: str = None  # type: ignore[assignment] # Reason: filled in __post_init__ if not provided # noqa: E501
    _client_id: str = None  # type: ignore[assignment] # Reason: filled in __post_init__ if not provided # noqa: E501

    def __post_init__(self) -> None:
        # Fill auth-related attributes if not provided
        auth_env = _get_auth_environment()
        if not self._auth_domain:
            self._auth_domain = auth_env.auth_domain
        if not self._client_id:
            self._client_id = auth_env.client_id

        self._token_endpoint: str = f"https://{self._auth_domain}/oauth/token"

    @classmethod
    def _generate_task_request_message(
        cls,
        serialized_protocol: SerializedProtocol,
        pod_identifiers: list[str],
        aes_key: bytes,
        pod_public_key: RSAPublicKey,
        project_id: Optional[str],
        run_on_new_data_only: bool = False,
        batched_execution: Optional[bool] = None,
        test_run: bool = False,
        force_rerun_failed_files: bool = True,
    ) -> bytes:
        if batched_execution is None:
            batched_execution = config.settings.default_batched_execution
        return _make_encrypted_task_request_message(
            IdentityVerificationMethod.OIDC_DEVICE_CODE,
            serialized_protocol,
            pod_identifiers,
            aes_key,
            pod_public_key,
            project_id,
            run_on_new_data_only,
            batched_execution,
            test_run=test_run,
            force_rerun_failed_files=force_rerun_failed_files,
        )

    @classmethod
    def create_task_request_message_generator(
        cls,
    ) -> _TaskRequestMessageGenerator:
        """See parent class for more information."""
        return cls._generate_task_request_message

    @classmethod
    def extract_from_task_request_message(
        cls, task_request_message: Union[bytes, _TaskRequestMessage]
    ) -> _EncryptedTaskRequest:
        """See parent class for more information."""
        return _extract_encrypted_task_request(task_request_message)

    @classmethod
    def unpack_task_request(
        cls, msg: Union[bytes, _TaskRequestMessage], pod_private_key: RSAPrivateKey
    ) -> _TaskRequest:
        """See parent class for more information."""
        return _unpack_task_request(
            msg, pod_private_key, cls.extract_from_task_request_message
        )

    async def check_authorisation(self) -> AuthCheckResponse:
        """Perform OIDC flow from the pod-side.

        This flow is based on:
        https://auth0.com/docs/get-started/authentication-and-authorization-flow/device-authorization-flow
        """  # noqa: E501
        # Send client ID for pod to modeller
        logger.info("Sending client ID for pod to modeller")
        await self.mailbox.send_oidc_client_id(self._client_id)

        # Wait for device code from modeller
        logger.info("Awaiting identity verification details from modeller")
        device_code_details = await self.mailbox.get_oidc_device_code_response()

        # Poll for user approval/authentication
        logger.info("Awaiting modeller approval for identity verification access")
        modeller_access_token = await self._poll_for_access_token(
            device_code_details.device_code,
            device_code_details.expires_at,
            device_code_details.interval,
        )

        # Check with Access Manager that user matches expected identity
        # and that the user has the correct permissions for the task
        # that they have requested.
        logger.info("Verifying access permissions for modeller task")
        authentication_result: AccessCheckResult = self._check_access(
            modeller_access_token
        )
        response_type = authentication_result["response_type"]

        logger.info(
            f"OIDC authorisation check complete. "
            f"Will inform modeller: {response_type.name}"
        )
        additional_messages = self._additional_messages_for_limits(
            authentication_result
        )
        self.pod_response_message.add(
            response_type=response_type,
            additional_messages=additional_messages,
        )
        return AuthCheckResponse(
            pod_response_message=self.pod_response_message,
            protocol_context=ProtocolContext(
                inference_limits=InferenceLimits.from_access_check_result(
                    authentication_result
                ),
                model_urls=ModelURLs.from_access_check_result(authentication_result),
            ),
        )

    async def _poll_for_access_token(
        self, device_code: str, expires_at: datetime, interval: int
    ) -> str:
        """Polls the token endpoint waiting for the authenticated response.

        Polls at the interval specified (which comes from the modeller's
        """
        # Poll until the token has expired
        while self._has_not_expired(expires_at):
            # Make request
            request_data: _DeviceAccessTokenRequestDict = {
                "client_id": self._client_id,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            }
            response = web_utils.post(
                self._token_endpoint,
                data=request_data,
                timeout=10,
            )

            # If we get our access token, exit early
            if (status_code := response.status_code) == 200:
                try:
                    success_json: _DeviceAccessTokenResponseJSON = response.json()
                    return success_json["access_token"]
                except (InvalidJSONError, KeyError) as e:
                    raise RequestException(
                        f'Success response, but JSON was invalid: "{response.text}"'
                    ) from e

            # Otherwise, treat as a retry-able error until we know otherwise;
            # status code could be any 4XX value, so we instead just check for the
            # right format and error values.
            try:
                error_json: _DeviceAccessTokenFailResponseJSON = response.json()
            except InvalidJSONError as e:
                raise RequestException(
                    f'{status_code} response, but JSON was invalid: "{response.text}"'
                ) from e

            # See if just pending authorisation
            if (error := error_json.get("error")) == _AUTHORIZATION_PENDING_ERROR:
                logger.info(
                    "Waiting on modeller to approve identity verification request..."
                )
            # We're requesting too quickly, increase interval
            elif error == _SLOW_DOWN_ERROR:
                logger.warning(
                    f"Polling token endpoint too frequently. "
                    f"Increasing interval from {interval} to {interval + 1}"
                )
                interval += 1

            # Otherwise, it's an actual error, raise it
            else:
                # If we have an actual error message, raise that
                if error:
                    error_msg = f"Error in OAuth response ({status_code}) ({error})"
                    # Try to add error_description if present
                    try:
                        error_msg += f": {error_json['error_description']}"
                    except KeyError:
                        pass
                    raise HTTPError(error_msg, response=response)

                # Otherwise, raise an exception with as much detail as possible
                else:
                    raise HTTPError(
                        f"An unexpected error occurred: "
                        f'status code: {status_code}; "{response.text}"',
                        response=response,
                    )

            # Sleep for the interval
            await asyncio.sleep(interval)

        # If we're past the expiration, raise it
        raise TimeoutError("Device code has expired, unable to retrieve access token.")

    @staticmethod
    def _has_not_expired(expires_at: datetime) -> bool:
        return datetime.now(timezone.utc) < expires_at

    def _check_access(self, modeller_access_token: str) -> AccessCheckResult:
        """Check that access is allowed for the authorised user and request."""
        return self.access_manager.check_oidc_access_request(
            self.pod_response_message.pod_identifier,
            self.serialized_protocol,
            self.mailbox.modeller_name,
            modeller_access_token,
            project_id=self.project_id,
        )


_IDENTITY_VERIFICATION_METHODS_MAP: Final[
    Mapping[IdentityVerificationMethod, type[_AuthorisationChecker]]
] = {
    IdentityVerificationMethod.KEYS: _SignatureBasedAuthorisation,
    IdentityVerificationMethod.OIDC_ACF_PKCE: _OIDCAuthorisationCode,
    IdentityVerificationMethod.OIDC_DEVICE_CODE: _OIDCDeviceCode,
}
