"""Typed wrappers around the Bitfount REST apis."""

from __future__ import annotations

import base64
from collections.abc import Callable, Mapping
from dataclasses import dataclass
import logging
from pathlib import Path
import time
from typing import Any, Final, Optional, TypeVar, Union, overload
import warnings

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
import pydash
import requests
from requests import HTTPError, RequestException, Response
from requests.exceptions import InvalidJSONError
from typing_extensions import ParamSpec

from bitfount import config
from bitfount.config import (
    _DEVELOPMENT_ENVIRONMENT,
    _PRODUCTION_ENVIRONMENT,
    _SANDBOX_ENVIRONMENT,
    _STAGING_ENVIRONMENT,
    _get_environment,
)
from bitfount.data.schema import BitfountSchema
from bitfount.encryption.encryption import _RSAEncryption
from bitfount.federated.types import (
    AccessCheckResult,
    SerializedProtocol,
    _PodResponseType,
)
from bitfount.hub.authentication_flow import (
    BitfountSession,
)
from bitfount.hub.exceptions import (
    ModelTooLargeError,
    ModelUploadError,
    ModelValidationError,
    NoModelCodeError,
    SchemaUploadError,
    SMARTOnFHIRError,
)
from bitfount.hub.types import (
    _DEV_AM_URL,
    _SANDBOX_AM_URL,
    _STAGING_AM_URL,
    PRODUCTION_AM_URL,
    PRODUCTION_HUB_URL,
    SMARTOnFHIRAccessToken,
    _AccessManagerKeyResponseJSON,
    _ActivePublicKey,
    _AMAccessCheckResponseJSON,
    _CreatedResourceResponseJSON,
    _CreateProjectResponseJSON,
    _GetProjectsPagedResponseJSON,
    _InitialisedPairingJSON,
    _ModelDetailsResponseJSON,
    _ModelUploadResponseJSON,
    _MonitorPostJSON,
    _OIDCAccessCheckPostJSON,
    _PairedPairingJSON,
    _PodDetailsResponseJSON,
    _PodRegistrationResponseJSON,
    _ProjectLimitsJSON,
    _ProjectModelLimitsJSON,
    _PublicKeyJSON,
    _RegisterUserPublicKeyPOSTJSON,
    _SignatureBasedAccessCheckPostJSON,
    _SMARTOnFHIRSessionJSON,
)
from bitfount.hub.utils import hash_contents, hash_file_contents
from bitfount.models.bitfount_model import BitfountModel
from bitfount.storage import (
    _download_data_from_s3,
    _download_file_from_s3,
    _get_packed_data_object_size,
    _upload_data_to_s3,
    _upload_file_to_s3,
)
from bitfount.types import (
    _JSONDict,
    _S3PresignedPOSTFields,
    _S3PresignedPOSTURL,
    _S3PresignedURL,
)
from bitfount.utils import (
    _get_mb_from_bytes,
    _get_non_abstract_classes_from_module,
    model_id_from_elements,
    web_utils,
)

logger = logging.getLogger(__name__)

# This forces `requests` to make IPv4 connections
# TODO: [BIT-1443] Remove this once Hub/AM support IPv6
requests.packages.urllib3.util.connection.HAS_IPV6 = False  # type: ignore[attr-defined] # Reason: see above # noqa: E501


# This should match the corresponding value in
# bitfount/bitfount-web:bf-packages/bitfount-hub/pages/api/pods.api.js
_MAX_SCHEMA_SIZE_BYTES: Final[int] = 10 * 1024 * 1024  # 10 Megabytes
_MAX_SCHEMA_SIZE_MEGABYTES: Final[int] = _get_mb_from_bytes(
    _MAX_SCHEMA_SIZE_BYTES
).whole
# This should match the corresponding value in
# bitfount/bitfount-web:bf-packages/bitfount-hub/pages/api/models.api.js
_MAX_CUSTOM_MODEL_SIZE_BYTES: Final[int] = 3 * 1024 * 1024  # 3 Megabytes
_MAX_CUSTOM_MODEL_SIZE_MEGABYTES: Final[int] = _get_mb_from_bytes(
    _MAX_CUSTOM_MODEL_SIZE_BYTES
).whole
_MAX_WEIGHTS_SIZE_BYTES: Final[int] = 500 * 1024 * 1024  # 3 Megabytes
_MAX_WEIGHTS_SIZE_MEGABYTES: Final[int] = _get_mb_from_bytes(
    _MAX_CUSTOM_MODEL_SIZE_BYTES
).whole

_P = ParamSpec("_P")
_R = TypeVar("_R")


@dataclass
class PodPublicMetadata:
    """Data about the Pod which is publicly visible on BitfountHub."""

    name: str
    display_name: str
    description: str
    schema: _JSONDict  # This should be set to schema.to_json()
    number_of_records: Optional[int] = None


def _verify_signature(
    public_key: RSAPublicKey, signature: bytes, message: bytes
) -> bool:
    """Verifies that decrypting `signature` with `public_key` == `message`."""
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=20,  # padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
    except InvalidSignature:
        logger.warning("Signature invalid.")
        return False

    logger.info("Signature valid.")
    return True


def _handle_request_exception(
    exc: RequestException, response: Optional[Response], conn_type: str
) -> str:
    """Logs out the request exception and response details, if provided."""
    err_msg = f"Bitfount {conn_type} connection failed with: {exc}."
    # Explicit None check needed due to truthyness of Response objects
    if response is not None and response.text:
        err_msg += f" Response was: {response.text}"
    logger.error(err_msg)

    return err_msg


def _extract_response_json(response: Response) -> Any:
    """Extracts the JSON from the response, raising an HTTPError if there is none."""
    try:
        response_json = response.json()
    except ValueError as e:  # raised if JSON extraction fails
        raise InvalidJSONError(
            f"Invalid JSON response ({response.status_code}): {response.text}"
        ) from e
    return response_json


def _check_pod_id_details(
    pod_identifier: Optional[str] = None,
    pod_namespace: Optional[str] = None,
    pod_name: Optional[str] = None,
) -> str:
    """Checks that either pod_identifier OR pod_namespace and pod_name are provided.

    If both sets are provided, then makes sure that the constructed pod_identifier
    matches the supplied one.

    Args:
        pod_identifier: Full pod identifier (i.e. pod_namespace/pod_name).
        pod_namespace: Pod namespace name.
        pod_name: Pod name.

    Returns:
        The pod_identifier.

    Raises:
        ValueError:
            - If no args are provided.
            - If pod_namespace is provided but pod_name is not (or vice versa).
            - If all args are provided but the constructed pod_identifier doesn't
              match the provided one.
    """
    args = [pod_identifier, pod_namespace, pod_name]

    # At least one set of args must be provided.
    if not any(args):
        raise ValueError(
            "At least one of pod_identifier OR "
            "pod_namespace and pod_name must be provided"
        )

    # Either both pod_namespace and pod_name are provided or both aren't
    if bool(pod_namespace) != bool(pod_name):
        raise ValueError(
            "Both pod_namespace and pod_name must be provided, or neither must be."
        )

    # If all are provided, the constructed and provided pod_identifiers must match
    if all(args):
        if pod_identifier != f"{pod_namespace}/{pod_name}":
            raise ValueError(
                "pod_identifier, pod_namespace and pod_name all provided, "
                "but pod_identifier doesn't match pod_namespace/pod_name."
            )

    # If conditions are met, return as needed
    if pod_identifier:
        return pod_identifier
    else:
        warnings.warn(
            "pod_identifier should be used instead of pod_namespace and pod_name",
            DeprecationWarning,
            stacklevel=3,
        )
        return f"{pod_namespace}/{pod_name}"


class BitfountHub:
    """A typed API for interacting with BitfountHub.

    Args:
        session: Bitfount session for authentication.
        url: URL to Bitfount Hub. Defaults to PRODUCTION_HUB_URL.
    """

    def __init__(
        self,
        session: Optional[BitfountSession] = None,
        url: str = PRODUCTION_HUB_URL,
    ):
        self.session = session if session else BitfountSession()
        if not self.session.authenticated:
            self.session.authenticate()
        self.url = url.rstrip("/")  # to ensure no trailing slash
        self.user_storage_path = self.session.authentication_handler.user_storage_path
        self.username = self.session.username

    @staticmethod
    def _handle_hub_request_exception(
        err: RequestException, response: Optional[Response]
    ) -> str:
        """Logs out the request exception and response details, if provided."""
        return _handle_request_exception(err, response, "Hub")

    def get_pod(
        self,
        pod_identifier: Optional[str] = None,
        pod_namespace: Optional[str] = None,
        pod_name: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Optional[_PodDetailsResponseJSON]:
        """Gets the details of a pod.

        Either pod_identifier or pod_namespace and pod_name can be provided.

        Args:
            pod_identifier: Full pod identifier (i.e. pod_namespace/pod_name). Optional.
            pod_namespace: Pod namespace name. Optional.
            pod_name: Pod name. Optional.
            project_id: The project ID to search for the pod in. Optional.

        Returns:
            The pod details JSON or None if unable to retrieve them.
        """
        # We reuse the arg name here because we're guaranteeing it's set now
        pod_identifier: str = _check_pod_id_details(  # type: ignore[no-redef] # Reason: see comment # noqa: E501
            pod_identifier, pod_namespace, pod_name
        )
        # Delete the others to avoid incorrect usage
        del pod_namespace
        del pod_name

        # Retrieve pod details from hub
        try:
            # pod_identifier here is str but mypy thinks it's still Optional[str]
            if project_id is None or pod_identifier.startswith(f"{self.username}/"):  # type: ignore[union-attr] # Reason: see comment # noqa: E501
                # keep current behaviour for cases that work
                logger.debug(
                    f"Requesting pod information for '{pod_identifier}' from hub"
                )
                response = self.session.get(f"{self.url}/api/pods/{pod_identifier}")
            else:
                logger.debug(
                    f"Requesting pod information for '{pod_identifier}' "
                    f"from hub via project_id '{project_id}'"
                )
                response = self.session.get(
                    f"{self.url}/api/projects/{project_id}/pods/{pod_identifier}"
                )
            response.raise_for_status()
        except RequestException as err:
            try:
                # noinspection PyUnboundLocalVariable
                err_response: Optional[Response] = response
            except NameError:
                # response variable wasn't created yet
                err_response = None
            self._handle_hub_request_exception(err, err_response)
            return None

        # Extract the JSON from the response body
        response_json: _PodDetailsResponseJSON = _extract_response_json(response)
        return response_json

    def get_pod_key(
        self,
        pod_identifier: Optional[str] = None,
        pod_namespace: Optional[str] = None,
        pod_name: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Optional[str]:
        """Gets the public key of a pod.

        Either pod_identifier or pod_namespace and pod_name can be provided.

        Args:
            pod_identifier: Full pod identifier (i.e. pod_namespace/pod_name). Optional.
            pod_namespace: Pod namespace name. Optional.
            pod_name: Pod name. Optional.
            project_id: The project ID to search for the pod in. Optional.

        Returns:
            The pod key or None if no key can be found.

        Raises:
            HTTPError: If the response from the hub is malformed.
        """
        # Get pod details and check validity
        logger.debug(f"Requesting public key for '{pod_identifier}' from hub")
        pod_details: Optional[_PodDetailsResponseJSON] = self.get_pod(
            pod_identifier, pod_namespace, pod_name, project_id=project_id
        )

        if not pod_details:
            # Return None so that the caller is aware that
            # they aren't guaranteed a string key!
            return None

        # Extract key from response
        pod_key: Optional[str] = pod_details.get("podPublicKey")

        if not pod_key:
            logger.error(f"Response JSON contained no public key: {pod_details}")
            return None

        return pod_key

    def send_model(
        self,
        model_code_path: Path,
        private_model: bool = False,
        model_description: str = "",
    ) -> _ModelUploadResponseJSON:
        """Sends the provided `model_code` to Hub, associated to session username.

        The name of the model is taken from the name of the file.

        Args:
            model_code_path: The path to the file containing the model code.
            private_model: Whether the model is private or publically accessible.
            model_description: An optional description of the model being uploaded.

        Returns: The response JSON from the Hub.

        Raises:
            ModelUploadError: If the model upload fails. Specific subclasses of
                ModelUploadError are used to indicate different failure conditions.
        """
        # Check model is correctly formed
        try:
            self._verify_bitfount_model_format(model_code_path)
        except (ValueError, TypeError) as e:
            logger.error(f"Model incorrectly structured. Error: {e}")
            raise ModelValidationError("Model incorrectly structured.") from e
        except ImportError as ie:
            logger.error(ie)
            raise ModelValidationError("Unable to import model.") from ie

        model_name: str = model_code_path.stem
        model_code_text: bytes = model_code_path.read_text().encode("utf-8")
        model_size = len(model_code_text)
        model_hash = hash_file_contents(model_code_path)
        if model_size > _MAX_CUSTOM_MODEL_SIZE_BYTES:
            raise ModelTooLargeError(
                f"Model is too large to upload: "
                f"expected max {_MAX_CUSTOM_MODEL_SIZE_MEGABYTES} megabytes, "
                f"got {_get_mb_from_bytes(model_size).fractional} megabytes."
            )

        # Register model details with hub
        try:
            logger.info(f"Uploading model '{model_name}' to Hub")
            response = self.session.post(
                f"{self.url}/api/models",
                json={
                    "modelName": model_name,
                    "modelSize": model_size,
                    "modelHash": model_hash,
                    "privateModel": private_model,
                    "modelDescription": model_description,
                },
            )
            response.raise_for_status()
        except RequestException as err:
            try:
                # noinspection PyUnboundLocalVariable
                err_response: Optional[Response] = response
            except NameError:
                # response variable wasn't created yet
                err_response = None
            self._handle_hub_request_exception(err, err_response)
            raise ModelUploadError(
                "Request exception occurred when uploading model details to hub."
            ) from err

        # Extract response
        response_json: _ModelUploadResponseJSON = _extract_response_json(response)
        if not response_json["success"]:
            logger.error(
                f"Could not send model to Bitfount Hub. "
                f"Failed with message: {response_json['errorMessage']}"
            )
            raise ModelUploadError(
                f"Failed to upload model details to hub: "
                f"{response_json['errorMessage']}"
            )
        logger.info(
            "Model successfully registered to Bitfount Hub, "
            "uploading to object storage."
        )

        # Extract URL to upload model to and upload it
        upload_url: _S3PresignedPOSTURL = response_json["uploadUrl"]
        upload_fields: _S3PresignedPOSTFields = response_json["uploadFields"]
        try:
            _upload_file_to_s3(
                upload_url,
                upload_fields,
                file_contents=model_code_text,
                file_name=model_code_path.name,
            )
        except RequestException as re:
            logger.error(f"Failed to upload model to S3: {re}")
            raise ModelUploadError("Failed to upload model to S3") from re

        logger.info("Model successfully uploaded to object storage.")
        return response_json

    def send_weights(
        self, model_name: str, model_version: int, pretrained_file_path: Path
    ) -> None:
        """Sends the provided `model_weights` to Hub.

        Save trained model weights associated to session username,
        model_name and model_version.

        Args:
            model_name: The name of the model to associate the weights with.
            model_version: The version of the model to associate the weights with.
            pretrained_file_path: The path to the pretrained model file.

        Raises:
            ModelUploadError: If the model upload fails. Specific subclasses of
            ModelUploadError are used to indicate different failure conditions.
        """
        weights_text: bytes = pretrained_file_path.read_bytes()
        weights_size = len(weights_text)
        if weights_size > _MAX_WEIGHTS_SIZE_BYTES:
            raise ModelTooLargeError(
                f"Model weights are too large to upload: "
                f"expected max {_MAX_WEIGHTS_SIZE_MEGABYTES} megabytes, "
                f"got {_get_mb_from_bytes(weights_size).fractional} megabytes."
            )

        # Register model weight details with hub
        try:
            logger.info(
                f"Uploading model weights to '{model_name}:{model_version}' to Hub"
            )
            response = self.session.put(
                f"{self.url}/api/models",
                json={
                    "modelName": model_name,
                    "modelVersion": model_version,
                    "weightSize": weights_size,
                },
            )
            response.raise_for_status()
        except RequestException as err:
            try:
                # noinspection PyUnboundLocalVariable
                err_response: Optional[Response] = response
            except NameError:
                # response variable wasn't created yet
                err_response = None
            self._handle_hub_request_exception(err, err_response)
            raise ModelUploadError(
                "Request exception occurred when uploading model weights to hub."
            ) from err

        # Extract response
        response_json: _ModelUploadResponseJSON = _extract_response_json(response)
        logger.info(
            "Model weights successfully registered to Bitfount Hub, "
            "uploading to object storage."
        )

        # Extract URL to upload model to and upload it
        upload_url: _S3PresignedPOSTURL = response_json["uploadUrl"]
        upload_fields: _S3PresignedPOSTFields = response_json["uploadFields"]
        try:
            _upload_file_to_s3(
                upload_url,
                upload_fields,
                file_contents=weights_text,
                file_name=pretrained_file_path.name,
            )
        except RequestException as re:
            logger.error(f"Failed to upload model weights to S3: {re}")
            raise ModelUploadError("Failed to upload model weights to S3") from re

        logger.info("Model weights successfully uploaded to object storage.")
        return None

    @staticmethod
    def _verify_bitfount_model_format(
        model_source: Union[Path, str],
    ) -> type[BitfountModel]:
        """Verifies that the model file is correctly formatted.

        Args:
            model_source: Path to the model file.

        Returns:
            The parsed model class.

        Raises:
            ImportError: If the file could not be loaded.
            TypeError: If there is no BitfountModel subclass in the file, or it
                is still abstract.
            ValueError: If multiple model classes are contained in the file.
            ValueError: If the name of the class and the name of the file differ.
        """
        if not isinstance(model_source, (Path, str)):
            raise ValueError(f"Unsupported model source type: {type(model_source)}")

        models = _get_non_abstract_classes_from_module(model_source)
        models = {
            name: class_
            for name, class_ in models.items()
            if issubclass(class_, BitfountModel)
        }

        num_models = len(models)
        if num_models == 0:
            raise TypeError(
                "Subclass of `BitfountModel` not found in file or is still abstract."
            )
        elif num_models > 1:
            raise ValueError(
                f"Model file contains {num_models} models. Must be just 1."
            )

        model = models.popitem()
        if isinstance(model_source, Path):
            if model[0] != model_source.stem:
                raise ValueError(
                    f"{model[0]} != {model_source.stem}. "
                    "Model class name must be the same as the filename",
                )

        logger.debug("Model is formatted correctly")

        # [PyTorchBitfountModelv2] No conversion necessary as this is not the base
        # method
        return model[1]

    def _get_model_response(
        self,
        username: str,
        model_name: str,
        model_version: Optional[int] = None,
        project_id: Optional[str] = None,
    ) -> Optional[_ModelDetailsResponseJSON]:
        """Gets the response for the model from the hub."""
        # Retrieve model details from API endpoint
        try:
            params = {
                "modellerName": username,
                "modelName": model_name,
            }
            if model_version:
                params.update({"modelVersion": str(model_version)})
            if project_id:
                params.update({"projectId": project_id})
            response = self.session.get(
                f"{self.url}/api/models",
                params=params,
            )
            response.raise_for_status()
        except RequestException as err:
            try:
                # noinspection PyUnboundLocalVariable
                err_response: Optional[Response] = response
            except NameError:
                # response variable wasn't created yet
                err_response = None
            self._handle_hub_request_exception(err, err_response)
            return None

        # Check response contains model details
        response_json: _ModelDetailsResponseJSON = _extract_response_json(response)

        return response_json

    def _response_retry(
        self, request: Callable[_P, Optional[_R]], err_msg: str
    ) -> Callable[_P, Optional[_R]]:
        """Retry decorator for Hub requests."""

        def retried_request(*args: _P.args, **kwargs: _P.kwargs) -> Optional[_R]:
            attempts = 5
            response_json = request(*args, **kwargs)
            while response_json is None and attempts > 0:
                time.sleep(5)  # give an extra 5 seconds in between retries
                response_json = request(*args, **kwargs)
                attempts -= 1
            if not response_json:  # i.e. empty JSON response
                logger.warning(err_msg)
                return None

            return response_json

        return retried_request

    def get_weights(
        self,
        username: str,
        model_name: str,
        model_version: int,
        project_id: Optional[str] = None,
    ) -> Optional[bytes]:
        """Gets weights byte stream corresponding to `model_name` from user `username`.

        Args:
            username: The model's owner.
            model_name: The name of the model.
            model_version: The version of the model. Defaults to latest.
            project_id: The project ID to search for the model in. Optional.

        Returns:
            The loaded weights as a byte stream or None if one has not been uploaded.
        """
        retrying_get_model_response = self._response_retry(
            self._get_model_response,
            f"No models registered by the name of {model_name} from user {username}",
        )
        response_json = retrying_get_model_response(
            username=username,
            model_name=model_name,
            model_version=model_version,
            project_id=project_id,
        )
        if not response_json:
            return None

        if weights_url := response_json.get("weightsDownloadUrl"):
            return self.get_weights_from_url(weights_url)
        else:
            logger.warning(
                "No weight file associated with "
                f"{model_id_from_elements(username, model_name, model_version)}"
            )
            return None

    @staticmethod
    def get_weights_from_url(weights_url: _S3PresignedURL) -> bytes:
        """Retrieve model weights from a pre-defined S3 URL."""
        return _download_file_from_s3(weights_url)

    def get_model(
        self,
        username: str,
        model_name: str,
        model_version: Optional[int] = None,
        project_id: Optional[str] = None,
    ) -> Optional[type[BitfountModel]]:
        """Gets model code corresponding to `model_name` from user `username`.

        Args:
            username: The model's owner.
            model_name: The name of the model.
            model_version: The version of the model. Defaults to latest. Optional.
            project_id: The project ID to search for the model in. Optional.

        Returns:
            The loaded Bitfount model class or None if unable to retrieve it. If the
            loaded model class is a v1 PyTorchBitfount model it is _not_
            automatically converted. To convert, call
            convert_bitfount_model_class_to_v2().
        """
        logger.debug(
            f"Requesting model metadata for model "
            f"{model_id_from_elements(username, model_name, model_version)}"
        )
        retrying_get_model_response = self._response_retry(
            self._get_model_response,
            f"No models registered by the name of {model_name} from user {username}",
        )
        response_json: Optional[_ModelDetailsResponseJSON] = (
            retrying_get_model_response(
                username=username,
                model_name=model_name,
                model_version=model_version,
                project_id=project_id,
            )
        )
        if not response_json:
            return None

        # Download model code from S3
        try:
            model_url: _S3PresignedURL = response_json["modelDownloadUrl"]
        except (KeyError, TypeError) as e:
            if isinstance(e, KeyError):
                model_version = response_json.get("modelVersion")
                if model_version is not None and project_id is not None:
                    # model exists but user doesn't have access to the code,
                    # probably because they reached the project usage limits
                    raise NoModelCodeError(
                        f"Found model version {model_version} but not its contents, "
                        "probably because you have exceeded usage limit in the project"
                    ) from e

            # Either entry isn't in the dict, or it's not a dict (might be None)
            raise InvalidJSONError(
                f"Cannot retrieve model, no model URL in pod response: {response_json}"
            ) from e

        # Extract class from downloaded code. The code is not saved to a file
        # to avoid exposing the source code.
        # [PyTorchBitfountModelv2] Not converted here, as this is just used downstream
        return self.get_model_from_url(model_url, response_json["modelHash"])

    @staticmethod
    def get_model_from_url(
        model_url: _S3PresignedURL, model_hash: str
    ) -> Optional[type[BitfountModel]]:
        """Retrieve model code from a pre-defined S3 URL.

        Will compare the downloaded model code to the hash provided.

        Args:
            model_url: The URL to download the model from.
            model_hash: Hash of the model code to compare the downloaded model code to.

        Returns:
            The parsed model class of the downloaded code, or None if the model class
            could not be parsed.  If the loaded model class is a v1 PyTorchBitfount
            model it is _not_ automatically converted. To convert,
            call convert_bitfount_model_class_to_v2().

        Raises:
            ModelValidationError: if the provided hash does not match the hash of the
                downloaded model code.
        """
        model_code: str = _download_file_from_s3(model_url, encoding="utf-8")

        content_hash = hash_contents(model_code)
        if content_hash != model_hash:
            raise ModelValidationError(
                "Stored hash does not match hashed model file contents. "
                "Model must be re-uploaded to hub."
            )

        try:
            # TODO: [BIT-3564] Any benefits from saving source code locally?
            model_class = BitfountHub._verify_bitfount_model_format(model_code)
        except (ValueError, TypeError, ImportError) as e:
            logger.error(e)
            return None

        # [PyTorchBitfountModelv2] Not converted here, as this is just used downstream
        return model_class

    # TODO: [BIT-4857] Remove this method once model hashes are provided via the auth
    #       response
    def _get_model_hash(
        self,
        username: str,
        model_name: str,
        model_version: Optional[int] = None,
        project_id: Optional[str] = None,
    ) -> str:
        logger.debug(
            f"Requesting model metadata for model "
            f"{model_id_from_elements(username, model_name, model_version)}"
        )
        retrying_get_model_response = self._response_retry(
            self._get_model_response,
            f"No models registered by the name of {model_name} from user {username}",
        )
        response_json: Optional[_ModelDetailsResponseJSON] = (
            retrying_get_model_response(
                username=username,
                model_name=model_name,
                model_version=model_version,
                project_id=project_id,
            )
        )
        if not response_json:
            raise ModelValidationError(
                "Unable to extract model hash from hub model metadata response."
            )
        else:
            return response_json["modelHash"]

    def register_pod(
        self,
        public_metadata: PodPublicMetadata,
        pod_public_key: RSAPublicKey,
        access_manager_key: RSAPublicKey,
    ) -> None:
        """Registers a pod with the hub.

        The pod's schema will be uploaded to S3.

        Args:
            public_metadata: Details about the pod (name, etc) to register.
            pod_public_key: The public key to use for this pod.
            access_manager_key: The public key of the Access Manager.

        Raises:
            RequestException: If unable to connect to the hub.
            HTTPError: If the response is not successful.
        """
        # Need to determine how large it will be once packed and uploaded to S3
        schema_size = _get_packed_data_object_size(public_metadata.schema)
        if schema_size > _MAX_SCHEMA_SIZE_BYTES:
            raise SchemaUploadError(
                f"Schema is too large to upload: "
                f"expected max {_MAX_SCHEMA_SIZE_MEGABYTES} megabytes, "
                f"got {_get_mb_from_bytes(schema_size).fractional} megabytes."
            )

        json_post = {
            "name": public_metadata.name,
            "podDisplayName": public_metadata.display_name,
            "podPublicKey": _RSAEncryption.serialize_public_key(
                pod_public_key, form="SSH"
            ).decode("utf-8"),
            "accessManagerPublicKey": _RSAEncryption.serialize_public_key(
                access_manager_key, form="SSH"
            ).decode("utf-8"),
            "description": public_metadata.description,
            "schemaSize": schema_size,
            "numberOfRecords": public_metadata.number_of_records,
        }

        # Send pod registration request and get response from hub
        try:
            response = self.session.post(
                f"{self.url}/api/pods",
                json=json_post,
                timeout=10,
            )
            # We raise_for_status() here but also need to explicitly check that
            # it's a 200/201 status code later.
            response.raise_for_status()
        except RequestException as err:
            try:
                # noinspection PyUnboundLocalVariable
                err_response: Optional[Response] = response
            except NameError:
                # response variable wasn't created yet
                err_response = None
            err_msg = self._handle_hub_request_exception(err, err_response)
            # Raise the same type of exception that was caught
            raise type(err)(err_msg) from err

        # Extract the JSON from the response body
        response_json: _PodRegistrationResponseJSON = _extract_response_json(response)

        # Handle non-successful status codes
        if response.status_code in (200, 201):
            logger.info("Pod registration successful")
        else:
            raise HTTPError(
                f"Unexpected response ({response.status_code}): {response.text}",
                response=response,
            )

        # Extract URL to upload schema to and upload it
        logger.info("Uploading schema to S3")
        upload_url: _S3PresignedPOSTURL = response_json["uploadUrl"]
        upload_fields: _S3PresignedPOSTFields = response_json["uploadFields"]
        _upload_data_to_s3(upload_url, upload_fields, public_metadata.schema)

    def do_pod_heartbeat(
        self, pod_names: list[str], pod_public_key: RSAPublicKey
    ) -> None:
        """Makes a "heartbeat" update to the hub.

        This takes the form of a PATCH request to the `/api/pods` endpoint.

        Args:
            pod_names: The names of the pods.
            pod_public_key: The public key of the pod.
        """
        json_patch = {
            "names": pod_names,
            "podPublicKey": _RSAEncryption.serialize_public_key(
                pod_public_key, form="SSH"
            ).decode("utf-8"),
        }

        # We don't need to catch RequestExceptions here as the calling loop
        # handles that.
        response = self.session.patch(
            f"{self.url}/api/pods",
            json=json_patch,
            timeout=10,
        )
        # We do raise_for_status() here but also need to explicitly check
        # if it is status_code 200 below.
        response.raise_for_status()

        # Check that we received valid JSON (though we don't use it)
        try:
            _extract_response_json(response)
        except InvalidJSONError as err:
            logger.warning(err)
            return

        if response.status_code == 200:
            # [LOGGING-IMPROVEMENTS]
            if config.settings.logging.log_pod_heartbeat:
                logger.debug("Status ping successful")
        else:
            logger.warning(
                f"Status update failed with ({response.status_code}): {response.text}"
            )

    def get_pod_schema(
        self, pod_identifier: str, project_id: Optional[str] = None
    ) -> BitfountSchema:
        """Retrieves the schema for a given pod.

        Args:
            pod_identifier: The pod to retrieve the schema of.
            project_id: The project ID to retrieve the schema from.

        Returns:
            The BitfountSchema for that pod.

        Raises:
            HTTPError: If there is an issue in the response.
        """
        log_message = f'Retrieving schema for "{pod_identifier}"'
        if project_id is not None:
            log_message = log_message + f' and project "{project_id}"'
        logger.info(log_message)
        pod_details: Optional[_PodDetailsResponseJSON] = self.get_pod(
            pod_identifier, project_id=project_id
        )

        # Try and extract schema URL from response
        try:
            if pod_details:
                schema_url: _S3PresignedURL = pod_details["schemaDownloadUrl"]
            else:
                # i.e. pod_details is None
                raise TypeError("No pod details retrieved from Hub")
        except (KeyError, TypeError) as e:
            # Either entry isn't in the dict, or it's not a dict (might be None)
            raise InvalidJSONError(
                f"Cannot retrieve pod schema, no schema URL in pod response: "
                f"{pod_details}"
            ) from e

        # Download and parse schema
        schema_json: _JSONDict = _download_data_from_s3(schema_url)
        return BitfountSchema.load(schema_json)

    def send_monitor_update(self, update: _MonitorPostJSON) -> None:
        """Send an update to the monitor service.

        Args:
            update: The monitor service update to send as a JSON dict.

        Raises:
            RequestException: If unable to connect to the hub.
            HTTPError: If the response is not successful.
        """
        try:
            response = self.session.post(
                f"{self.url}/api/ingest", json=update, timeout=5
            )
            response.raise_for_status()
        except RequestException as err:
            try:
                # noinspection PyUnboundLocalVariable
                err_response: Optional[Response] = response
            except NameError:
                # response variable wasn't created yet
                err_response = None
            err_msg = self._handle_hub_request_exception(err, err_response)
            # Raise the same type of exception that was caught
            raise type(err)(err_msg) from err

    def register_user_public_key(self, key: RSAPublicKey) -> Union[str, int]:
        """Register a public key for the signed-in user.

        Args:
            key: The public key to register.
        """
        key_json: _RegisterUserPublicKeyPOSTJSON = {
            "key": _RSAEncryption.serialize_public_key(key, form="SSH").decode("utf-8"),
        }
        try:
            response = self.session.post(
                f"{self.url}/api/{self.username}/keys",
                json=key_json,
                timeout=10,
                params={"version": 2},
            )
            response.raise_for_status()
        except RequestException as err:
            try:
                # noinspection PyUnboundLocalVariable
                err_response: Optional[Response] = response
            except NameError:
                # response variable wasn't created yet
                err_response = None
            err_msg = self._handle_hub_request_exception(err, err_response)
            # Raise the same type of exception that was caught
            raise type(err)(err_msg) from err

        response_json: _CreatedResourceResponseJSON = _extract_response_json(response)
        return response_json["id"]

    def check_public_key_registered_and_active(
        self, key_id: str, username: Optional[str] = None
    ) -> Optional[_ActivePublicKey]:
        """Return key details from hub if key is registered."""
        if username is None:
            username = self.username

        try:
            response = self.session.get(
                f"{self.url}/api/{username}/keys/{key_id}",
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
        except RequestException as err:
            try:
                # noinspection PyUnboundLocalVariable
                err_response: Optional[Response] = response
            except NameError:
                # response variable wasn't created yet
                err_response = None
            err_msg = self._handle_hub_request_exception(err, err_response)
            # Raise the same type of exception that was caught
            raise type(err)(err_msg) from err

        # Load key from response
        response_json: _PublicKeyJSON = _extract_response_json(response)

        if response_json["active"]:
            return _ActivePublicKey(
                public_key=_RSAEncryption.load_public_key(
                    response_json["public_key"].encode()
                ),
                id=response_json["id"],
                active=response_json["active"],
            )
        return None

    def create_project(self, name: str) -> str:
        """Creates a project and returns the ID."""
        try:
            response = self.session.post(
                f"{self.url}/api/projects",
                json={"name": name, "metadata": {}},
                timeout=10,
            )
            # We raise_for_status() here but also need to explicitly check that
            # it's a 200/201 status code later.
            response.raise_for_status()
        except RequestException as err:
            try:
                # noinspection PyUnboundLocalVariable
                err_response: Optional[Response] = response
            except NameError:
                # response variable wasn't created yet
                err_response = None
            err_msg = self._handle_hub_request_exception(err, err_response)
            # Raise the same type of exception that was caught
            raise type(err)(err_msg) from err

        # Extract the JSON from the response body
        response_json: _CreateProjectResponseJSON = _extract_response_json(response)

        # Handle non-successful status codes
        if response.status_code in (200, 201):
            logger.info("Project successfully created")
            return response_json["projectId"]
        else:
            raise HTTPError(
                f"Unexpected response ({response.status_code}): {response.text}",
                response=response,
            )

    def get_projects(
        self,
        offset: Optional[int] = 0,
        limit: Optional[int] = 12,
    ) -> Optional[_GetProjectsPagedResponseJSON]:
        """Gets a page of projects.

        Args:
            offset: Starting point
            limit: Max number of projects to retrieve

        Returns:
            A page of projects
        """
        # Retrieve projects from hub
        try:
            response = self.session.get(
                f"{self.url}/api/projects", params={"limit": limit, "offset": offset}
            )
            response.raise_for_status()
        except RequestException as err:
            try:
                # noinspection PyUnboundLocalVariable
                err_response: Optional[Response] = response
            except NameError:
                # response variable wasn't created yet
                err_response = None
            err_msg = self._handle_hub_request_exception(err, err_response)
            # Raise the same type of exception that was caught
            raise type(err)(err_msg) from err

        # Extract the JSON from the response body
        response_json: _GetProjectsPagedResponseJSON = _extract_response_json(response)
        return response_json

    def add_dataset_to_project_for_user(
        self, project_id: str, dataset_name: str
    ) -> None:
        """Add a dataset to an already existing project.

        Only works for projects owned by the authenticated user.

        Args:
            project_id: The ID of the project to add the dataset to.
            dataset_name: The name of the dataset to add.
        """
        try:
            response = self.session.put(
                f"{self.url}/api/projects/{project_id}/pod",
                json=[{"podName": dataset_name}],
                timeout=10,
            )
            response.raise_for_status()
        except RequestException as err:
            try:
                # noinspection PyUnboundLocalVariable
                err_response: Optional[Response] = response
            except NameError:
                # response variable wasn't created yet
                err_response = None
            err_msg = self._handle_hub_request_exception(err, err_response)
            # Raise the same type of exception that was caught
            raise type(err)(err_msg) from err

        # Handle non-successful status codes
        if response.status_code in (200, 201):
            logger.info(
                f"Dataset {dataset_name} added to project {project_id} successfully"
            )
        else:
            raise HTTPError(
                f"Unexpected response ({response.status_code}): {response.text}",
                response=response,
            )

    @overload
    def get_usage_limits(
        self, project_id: str, model_id: None = ...
    ) -> _ProjectLimitsJSON: ...

    @overload
    def get_usage_limits(
        self, project_id: str, model_id: str = ...
    ) -> _ProjectModelLimitsJSON: ...

    def get_usage_limits(
        self, project_id: str, model_id: Optional[str] = None
    ) -> Union[_ProjectLimitsJSON, _ProjectModelLimitsJSON]:
        """Get usage/limits information in a project for the current user.

        If model_id is provided, will return the usage for that model+user+project
        combination.

        If it is not provided, will return the simple usages for each model
        associated with the project task for user+project combination.
        """
        base_limits_url = f"{self.url}/api/projects/{project_id}/limits"

        try:
            if model_id:
                response = self.session.get(f"{base_limits_url}/models/{model_id}")
            else:
                response = self.session.get(base_limits_url)
            response.raise_for_status()
        except RequestException as err:
            try:
                # noinspection PyUnboundLocalVariable
                err_response: Optional[Response] = response
            except NameError:
                # response variable wasn't created yet
                err_response = None
            err_msg = self._handle_hub_request_exception(err, err_response)
            # Raise the same type of exception that was caught
            raise type(err)(err_msg) from err

        resp_json: Union[_ProjectLimitsJSON, _ProjectModelLimitsJSON] = (
            _extract_response_json(response)
        )
        return resp_json


class BitfountAM:
    """Typed API for communicating with the Bitfount Access Manager.

    Args:
        session: Bitfount session for authentication.
        access_manager_url: URL of the access manager.
    """

    def __init__(
        self,
        session: Optional[BitfountSession] = None,
        access_manager_url: Optional[str] = None,
    ):
        # Set the AM url based on the environment
        access_manager_url = (
            access_manager_url if access_manager_url else self._get_am_url()
        )
        self.session = session if session else BitfountSession()
        if not self.session.authenticated:
            self.session.authenticate()
        self.access_manager_url = access_manager_url.rstrip(
            "/"
        )  # to ensure no trailing slashes

    @staticmethod
    def _handle_am_request_exception(
        err: RequestException, response: Optional[Response]
    ) -> str:
        """Logs out the request exception and response details, if provided."""
        return _handle_request_exception(err, response, "Access Manager")

    @staticmethod
    def _get_am_url() -> str:
        """Gets the AM url based on the environment."""
        environment = _get_environment()
        if environment == _STAGING_ENVIRONMENT:
            access_manager_url = _STAGING_AM_URL
        elif environment == _DEVELOPMENT_ENVIRONMENT:
            access_manager_url = _DEV_AM_URL
        elif environment == _PRODUCTION_ENVIRONMENT:
            access_manager_url = PRODUCTION_AM_URL
        elif environment == _SANDBOX_ENVIRONMENT:
            access_manager_url = _SANDBOX_AM_URL
        return access_manager_url

    def get_access_manager_key(self) -> RSAPublicKey:
        """Gets the Access Manager's public key.

        Returns:
            The access manager's public key.

        Raises:
            RequestException: If there is a problem communicating with the
                              access manager.
        """
        try:
            # No need to use `self.session` here because the endpoint does not require
            # authentication.
            logger.debug(
                f"Retrieving access manager public key from "
                f"{self.access_manager_url}/api/access-manager-key"
            )
            response = web_utils.get(
                f"{self.access_manager_url}/api/access-manager-key",
                timeout=5,
            )
            logger.debug(f"Access manager public key response received: {response}")
            response.raise_for_status()
        except RequestException as err:
            try:
                # noinspection PyUnboundLocalVariable
                err_response: Optional[Response] = response
            except NameError:
                # response variable wasn't created yet
                err_response = None
            err_msg = self._handle_am_request_exception(err, err_response)
            # Raise same type of exception as caught before
            raise type(err)(err_msg) from err

        response_json: _AccessManagerKeyResponseJSON = _extract_response_json(response)

        try:
            am_key: str = response_json["accessManagerPublicKey"]
            logger.debug(f"Received access manager key: {am_key}")
        except (KeyError, TypeError) as e:
            raise InvalidJSONError(
                f"Unable to extract public key from access manager response, "
                f"no key in JSON: {response_json}"
            ) from e
        return _RSAEncryption.load_public_key(am_key.encode())

    def check_oidc_access_request(
        self,
        pod_identifier: str,
        serialized_protocol: SerializedProtocol,
        modeller_name: str,
        modeller_access_token: str,
        project_id: Optional[str] = None,
    ) -> AccessCheckResult:
        """Check access using access token from OIDC request.

        Args:
            pod_identifier: The pod identifier for the request.
            serialized_protocol: The protocol received from the modeller.
            modeller_name: The name of the modeller.
            modeller_access_token: OAuth access token for the modeller.
            project_id: Optional. The project ID associated with the task. Used
                to verify project-based access.

        Returns:
            Response code from the Access manager.

        Raises:
            RequestException: If there is a problem communicating with the
                access manager.
            HTTPError: If it is unable to extract the JSON from the response.
            InvalidJSONError: If JSON does not match expected format.
        """
        post_json = _OIDCAccessCheckPostJSON(
            podIdentifier=pod_identifier,
            modellerProtocolRequest=serialized_protocol,
            modellerName=modeller_name,
            modellerToken=modeller_access_token,
            identityProvider="OIDC",
            projectId=project_id,
        )

        return self._do_authorization_check(
            f"{self.access_manager_url}/api/access", post_json
        )

    def check_signature_based_access_request(
        self,
        unsigned_task: bytes,
        task_signature: bytes,
        pod_identifier: str,
        serialized_protocol: SerializedProtocol,
        modeller_name: str,
        project_id: Optional[str] = None,
        public_key_id: Optional[str] = None,
    ) -> AccessCheckResult:
        """Check access by verifying the signed task against the unsigned task.

        Check that when modeller_name signs the unsigned task it matches the signed
        version of the task.

        Args:
            unsigned_task: Unsigned task.
            task_signature: Task signature.
            pod_identifier: The pod identifier for the request.
            serialized_protocol: The protocol received from the modeller.
            modeller_name: The name of the modeller.
            modeller_access_token: OAuth access token for the modeller.
            project_id: Optional. The project ID associated with the task. Used
                to verify project-based access.
            public_key_id: Optional. The public key ID associated with the modeller.

        Returns:
            Response code from the Access manager.

        Raises:
            RequestException: If there is a problem communicating with the
                access manager.
            HTTPError: If it is unable to extract the JSON from the response.
            InvalidJSONError: If JSON does not match expected format.
        """
        post_json = _SignatureBasedAccessCheckPostJSON(
            podIdentifier=pod_identifier,
            modellerProtocolRequest=serialized_protocol,
            modellerName=modeller_name,
            unsignedTask=base64.b64encode(unsigned_task).decode("utf-8"),
            taskSignature=base64.b64encode(task_signature).decode("utf-8"),
            identityProvider="SIGNATURE",
            projectId=project_id,
            publicKeyId=public_key_id,
        )

        return self._do_authorization_check(
            f"{self.access_manager_url}/api/access", post_json
        )

    def _do_authorization_check(
        self,
        url: str,
        post_json: Mapping[str, Any],
    ) -> AccessCheckResult:
        """Makes an access check to the Access Manager.

        Args:
            url: AM URL to POST to.
            post_json: The JSON to send.

        Returns:
            Response code from the Access manager.

        Raises:
            RequestException: If there is a problem communicating with the
                access manager.
            HTTPError: If it is unable to extract the JSON from the response.
            InvalidJSONError: If JSON does not match expected format.
        """
        try:
            response = self.session.post(
                url=url,
                timeout=10,
                json=post_json,
            )

            response.raise_for_status()
        except RequestException as err:
            try:
                # noinspection PyUnboundLocalVariable
                err_response: Optional[Response] = response
            except NameError:
                # response variable wasn't created yet
                err_response = None
            err_msg = self._handle_am_request_exception(err, err_response)
            # Raise same type of exception as caught before
            raise type(err)(err_msg) from err

        try:
            response_json: _AMAccessCheckResponseJSON = _extract_response_json(response)

            logger.debug(
                "JSON From access manager: "
                f"{web_utils.obfuscate_security_token(str(response_json))}"
            )
            try:
                return AccessCheckResult(
                    response_type=_PodResponseType[response_json["code"]],
                    limits=response_json.get("limits"),
                )
            except KeyError:
                return AccessCheckResult(
                    response_type=_PodResponseType.NO_ACCESS, limits=None
                )
            except TypeError as e:
                raise AttributeError from e
        except AttributeError as ae:
            # raised if response is not a dict
            raise InvalidJSONError(
                f"Invalid JSON response ({response.status_code}): {response.text}"
            ) from ae


class SMARTOnFHIR:
    """API for SMART on FHIR pairing and session management."""

    def __init__(
        self,
        session: Optional[BitfountSession] = None,
        smart_on_fhir_url: Optional[str] = None,
        resource_server_url: Optional[str] = None,
    ):
        """Create API client for SMART on FHIR pairing and session management.

        Args:
            session: The BitfountSession to use for API calls. If not provided,
                a default one is created.
            smart_on_fhir_url: URL for the SMART on FHIR service. If not provided the
                URL will either be pulled from configuration or failing that set
                depending on the BITFOUNT_ENVIRONMENT we are running in.
            resource_server_url: URL for the SMART on FHIR resource server (i.e. the
                NextGen server that the pairings should correspond to). If not provided
                the URL will be pulled from configuration if provided.
        """
        self.session = session if session else BitfountSession()
        if not self.session.authenticated:
            self.session.authenticate()

        self.base_url = (
            smart_on_fhir_url
            if smart_on_fhir_url is not None
            else self._get_base_url_from_env()
        ).rstrip("/")  # to ensure no trailing slash

        self.resource_server_url: Optional[str] = (
            resource_server_url
            if resource_server_url is not None
            else self._get_resource_server_url_from_env()
        )
        if self.resource_server_url is not None:
            # ensure no trailing slash
            self.resource_server_url = self.resource_server_url.rstrip("/")

    @staticmethod
    def _get_base_url_from_env() -> str:
        """Get SMART on FHIR URL from environment variables."""
        environment = _get_environment()

        # Get SMART on FHIR URL from envvar or based on which environment we are in
        url: str
        if (
            config_url
            := config.settings.smart_on_fhir.smart_on_fhir_resource_server_url
        ) is not None:
            url = config_url
        elif environment == _STAGING_ENVIRONMENT:
            url = "https://smartonfhir.staging.bitfount.com"
        elif environment == _DEVELOPMENT_ENVIRONMENT:
            # NOTE: this _should_ work in dev as well as in sandbox
            url = "https://smartonfhir.sandbox.bitfount.com"
        elif environment == _SANDBOX_ENVIRONMENT:
            url = "https://smartonfhir.sandbox.bitfount.com"
        else:
            url = "https://smartonfhir.bitfount.com"

        return url

    @staticmethod
    def _get_resource_server_url_from_env() -> Optional[str]:
        """Get SMART on FHIR resource server URL from environment variables."""
        # Get resource server from envvar if provided
        resource_server_url: Optional[str] = (
            config.settings.smart_on_fhir.smart_on_fhir_resource_server_url
        )
        return resource_server_url

    def _find_pairing_id(self) -> str:
        """Find an appropriate pairing ID for the logged-in user.

        Pairing ID should be for the target resource server and should be marked
        as "paired".

        Returns:
            A pairing ID for the logged-in user that is marked as "paired".

        Raises:
            SMARTOnFHIRError: If no appropriate pairing for the logged-in user is found.
        """
        # TODO: [BIT-4907] How to handle pagination of pairings results
        logger.info("Requesting pairing ID info from SMART on FHIR")

        # BitfountSession will only auto-add headers to hub/AM url requests,
        # so need to add manually
        resp = self.session.get(
            f"{self.base_url}/api/pairings",
            headers=self.session.hub_request_headers,
            timeout=config.settings.smart_on_fhir.smart_on_fhir_api_timeout,
        )
        resp.raise_for_status()

        pairings: list[_InitialisedPairingJSON | _PairedPairingJSON] = resp.json()[
            "results"
        ]

        # Check each of the pairings returned for a match
        for pairing in pairings:
            # Only want actually paired pairings
            if pairing["state"] != "paired":
                continue

            # If we've specified a resource server, need to find a matching one
            if (
                self.resource_server_url
                and pairing["resourceServer"] != self.resource_server_url
            ):
                continue

            logger.info("Found pairing ID info from SMART on FHIR")
            return pairing["id"]
        else:
            err_str = (
                f"Could not find a matching SMART on FHIR pairing"
                f" for {self.session.username}"
            )
            if self.resource_server_url:
                err_str += f" on resource server '{self.resource_server_url}'"
            err_str += f"; checked {len(pairings)} pairings."
            raise SMARTOnFHIRError(err_str)

    def _get_smart_on_fhir_session(self, pairing_id: str) -> _SMARTOnFHIRSessionJSON:
        """Call the SMART on FHIR session endpoint to get access token and context."""
        logger.info("Retrieving access token from SMART on FHIR")

        # BitfountSession will only auto-add headers to hub/AM url requests,
        # so need to add manually
        resp = self.session.get(
            f"{self.base_url}/api/pairings/{pairing_id}/session",
            headers=self.session.hub_request_headers,
            timeout=config.settings.smart_on_fhir.smart_on_fhir_api_timeout,
        )
        resp.raise_for_status()

        resp_json: _SMARTOnFHIRSessionJSON = resp.json()
        return resp_json

    def get_access_token(
        self,
    ) -> SMARTOnFHIRAccessToken:
        """Get a SMART on FHIR access token for the logged-in user.

        Returns the access token string and the nextgen context for that token.

        Returns:
            A SMARTOnFHIRAccessToken instance containing the token string and
            additional context.
        """
        pairing_id = self._find_pairing_id()
        resp_json: _SMARTOnFHIRSessionJSON = self._get_smart_on_fhir_session(pairing_id)
        return SMARTOnFHIRAccessToken(
            token=resp_json["accessToken"],
            context=pydash.get(resp_json, "context.nextgen"),
        )
