"""Helper functions related to hub and AM interactions."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union, cast

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
import yaml

from bitfount import config
from bitfount.config import (
    _DEVELOPMENT_ENVIRONMENT,
    _SANDBOX_ENVIRONMENT,
    _STAGING_ENVIRONMENT,
    _get_environment,
)
from bitfount.data.schema import BitfountSchema
from bitfount.encryption.encryption import _RSAEncryption
from bitfount.hub.api import BitfountAM, BitfountHub
from bitfount.hub.authentication_flow import (
    _DEVELOPMENT_AUTH_DOMAIN,
    _DEVELOPMENT_CLIENT_ID,
    _SANDBOX_AUTH_DOMAIN,
    _SANDBOX_CLIENT_ID,
    _STAGING_AUTH_DOMAIN,
    _STAGING_CLIENT_ID,
    BitfountSession,
)
from bitfount.hub.authentication_handlers import (
    _DEFAULT_USERNAME,
    APIKeysHandler,
    AuthenticationHandler,
    DeviceCodeFlowHandler,
    ExternallyManagedJWTHandler,
)
from bitfount.hub.exceptions import PodDoesNotExistError
from bitfount.hub.types import (
    _DEV_AM_URL,
    _DEV_HUB_URL,
    _SANDBOX_AM_URL,
    _SANDBOX_HUB_URL,
    _STAGING_AM_URL,
    _STAGING_HUB_URL,
    PRODUCTION_AM_URL,
    PRODUCTION_HUB_URL,
)

if TYPE_CHECKING:
    from bitfount.externals.general.authentication import ExternallyManagedJWT
    from bitfount.runners.config_schemas.hub_schemas import APIKeys

logger = logging.getLogger(__name__)


def _create_bitfount_session(
    url: str,
    username: Optional[str] = None,
    secrets: Optional[Union[APIKeys, ExternallyManagedJWT]] = None,
) -> BitfountSession:
    """Creates a relevant Bitfount Session according to the environment.

    Args:
        url: Bitfount hub URL.
        username: Optional. Username. Defaults to DEFAULT_USER_DIRECTORY.
        secrets: Optional

    Returns:
        BitfountSession object.
    """
    username = username if username else _DEFAULT_USERNAME

    handler: AuthenticationHandler
    if secrets:
        if hasattr(secrets, "jwt"):
            if TYPE_CHECKING:
                secrets = cast(ExternallyManagedJWT, secrets)
            handler = ExternallyManagedJWTHandler(
                jwt=secrets.jwt,
                expires=secrets.expires,
                get_token=secrets.get_token,
                username=username,
            )
        else:
            handler = APIKeysHandler(
                api_key_id=secrets.access_key_id,
                api_key=secrets.access_key,
                username=username,
            )
    else:
        if os.getenv("BITFOUNT_API_KEY_ID") and os.getenv("BITFOUNT_API_KEY"):
            # If no secrets are provided in the config, but API keys are set
            # in the environment then they are used by default
            handler = APIKeysHandler(
                os.environ["BITFOUNT_API_KEY_ID"],
                os.environ["BITFOUNT_API_KEY"],
                username=username,
            )
        elif url == _STAGING_HUB_URL:
            handler = DeviceCodeFlowHandler(
                auth_domain=_STAGING_AUTH_DOMAIN,
                client_id=_STAGING_CLIENT_ID,
                username=username,
            )
        elif url == _SANDBOX_HUB_URL:
            handler = DeviceCodeFlowHandler(
                auth_domain=_SANDBOX_AUTH_DOMAIN,
                client_id=_SANDBOX_CLIENT_ID,
                username=username,
            )
        elif "localhost" in url:
            handler = DeviceCodeFlowHandler(
                auth_domain=_DEVELOPMENT_AUTH_DOMAIN,
                client_id=_DEVELOPMENT_CLIENT_ID,
                username=username,
            )
        else:
            handler = DeviceCodeFlowHandler(username=username)
    session = BitfountSession(handler)
    return session


def get_hub_url() -> str:
    """Retrieve the hub URL appropriate for the current environment."""
    environment = _get_environment()
    if environment == _STAGING_ENVIRONMENT:
        return _STAGING_HUB_URL
    elif environment == _DEVELOPMENT_ENVIRONMENT:
        return _DEV_HUB_URL
    elif environment == _SANDBOX_ENVIRONMENT:
        return _SANDBOX_HUB_URL
    else:
        return PRODUCTION_HUB_URL


def _default_bitfounthub(
    hub: Optional[BitfountHub] = None,
    username: Optional[str] = None,
    url: Optional[str] = None,
    secrets: Optional[Union[APIKeys, ExternallyManagedJWT]] = None,
) -> BitfountHub:
    """Gets a default BitfountHub instance if one is not specified.

    Args:
        hub: Optional. The BitfountHub instance to use if it exists.
        username: Optional. Username.
        url: Optional. Bitfount hub URL.
        secrets: Optional. Either APIKeys or JWT to use for authentication.

    Returns:
        BitfountHub object representing the hub.
    """
    if not hub:
        return _create_bitfounthub(username, url, secrets)
    return hub


def _create_bitfounthub(
    username: Optional[str] = None,
    url: Optional[str] = None,
    secrets: Optional[Union[APIKeys, ExternallyManagedJWT]] = None,
    session: Optional[BitfountSession] = None,
) -> BitfountHub:
    """Creates bitfounthub object.

    Args:
        username: Optional. Username.
        url: Optional. Bitfount hub URL. Will use the environment default if not
            supplied.
        secrets: Optional. Either APIKeys or JWT to use for authentication.
        session: Optional. BitfountSession object for authentication.

    Returns:
        BitfountHub object representing the hub.
    """
    if not url:
        url = get_hub_url()
    if not session:
        session = _create_bitfount_session(url=url, username=username, secrets=secrets)
        session.authenticate()
    return BitfountHub(session=session, url=url)


def get_am_url() -> str:
    """Retrieve the hub AM URL appropriate for the current environment."""
    environment = _get_environment()
    if environment == _STAGING_ENVIRONMENT:
        url = _STAGING_AM_URL
    elif environment == _DEVELOPMENT_ENVIRONMENT:
        url = _DEV_AM_URL
    elif environment == _SANDBOX_ENVIRONMENT:
        url = _SANDBOX_AM_URL
    else:
        url = PRODUCTION_AM_URL
    return url


def _create_access_manager(
    session: BitfountSession,
    url: Optional[str] = None,
) -> BitfountAM:
    """Creates and returns Bitfount Access Manager.

    Args:
        session: Bitfount session for authentication.
        url: Optional. URL of the access manager. Will use the environment default
             if not supplied.

    Returns:
        The BitfountAM representing the access manager.
    """
    if not url:
        url = get_am_url()

    return BitfountAM(session, url)


def _save_key_to_key_store(
    key_store_path: Path, pod_identifier: str, serialized_pod_key: str
) -> None:
    """Save pod keys to the key store.

    This will override any previously saved keys.

    Args:
        key_store_path: The path to where the key files are stored
        pod_identifier: The pod identifier of the pod we are saving the key for.
        serialized_pod_key: The serialized pod key
    """
    with open(key_store_path, "r") as key_store:
        known_pod_keys: dict[str, str] = yaml.safe_load(key_store) or {}

    known_pod_keys[pod_identifier] = serialized_pod_key

    with open(key_store_path, "w") as key_store:
        logger.debug(f"Saving pod public keys to {key_store_path}")
        yaml.safe_dump(known_pod_keys, key_store)


def _check_known_pods(
    pod_name: str, pod_public_key: RSAPublicKey, key_store_path: Path
) -> RSAPublicKey:
    """Checks known pods still have valid public key.

    Checks pod public key is the same as in BITFOUNT_KEY_STORE
    If BITFOUNT_KEY_STORE does not exist, it creates it and adds the key
    If it does exist but the key is different, it prompts the user to
    accept or reject new key.

    Returns:
        The new or existing key (depending on which the user chooses) as a string.
    """
    # Serialise to allow comparison with stored keys
    serialized_pod_key: str = _RSAEncryption.serialize_public_key(
        pod_public_key
    ).decode()

    # Check if target key already exists in the key store
    with open(key_store_path, "r") as key_store:
        known_pod_keys: dict[str, str] = yaml.safe_load(key_store) or {}
        serialized_current_pod_key: Optional[str] = known_pod_keys.get(pod_name, None)

        if serialized_current_pod_key is None:
            # No current key for this user, ok to "update" it (i.e. add it)
            logger.debug(f"No existing key found for pod {pod_name}")
        elif serialized_current_pod_key != serialized_pod_key:
            # Key mismatch, check with user for how to proceed
            logger.error(
                f"{pod_name} public key has changed. \n"
                f"Please double check the key has really changed and this "
                f"is not an attack."
            )
            while True:
                # We are only using python3 so this is secure
                response = input("Do you want to trust the new public key? (y/n)")
                if response.lower() == "y":
                    # Break out of the loop
                    break
                elif response.lower() == "n":
                    # Use the old public key
                    return _RSAEncryption.load_public_key(
                        serialized_current_pod_key.encode()
                    )
                else:
                    print("Didn't catch that, please type 'y' or 'n'")
        else:
            # Key matches, just return it
            logger.info(f"Found public key for {pod_name} in key store.")
            return pod_public_key

    # Save known pod key with the new one. We do this here because either
    # the user has approved or there was no key for that user in the first
    # place.
    logger.info(f"Saving public key for {pod_name} in key store.")
    _save_key_to_key_store(key_store_path, pod_name, serialized_pod_key)

    # The new pod key has been saved so we can just return it
    return pod_public_key


def _get_pod_public_key(
    pod_identifier: str,
    hub: BitfountHub,
    pod_public_key_paths: Optional[Mapping[str, Path]] = None,
    project_id: Optional[str] = None,
) -> RSAPublicKey:
    """Gets a pod's public key.

    Either loads it from disk or downloads it from BitfountHub.

    Args:
        pod_identifier: The pod identifier of the pod we get the public key for.
        hub: Hub to download keys from.
        pod_public_key_paths: Mapping of pod identifiers to already existing key files.
            Optional.
        project_id: The project ID to use when connecting to the hub. Optional.

    Returns:
        The public key for the pod.

    Raises:
        PodDoesNotExistError: If the pod does not exist.
    """
    key_store_path = Path(config.settings.paths.key_store).expanduser()

    # Create key store file if file doesn't exist
    if not key_store_path.is_file():
        logger.info("Creating key store for pod public keys...")
        key_store_path.parent.mkdir(parents=True, exist_ok=True)
        key_store_path.touch()

    # Check for the target key against explicitly provided key files
    if pod_public_key_paths:
        logger.debug(f"Checking for public key file for {pod_identifier}")
        try:
            pod_public_key_path: Path = pod_public_key_paths[pod_identifier]
            existing_pod_public_key = _RSAEncryption.load_public_key(
                pod_public_key_path
            )
            return _check_known_pods(
                pod_identifier, existing_pod_public_key, key_store_path
            )
        except KeyError:
            # We have some pod public key files, but not for this pod identifier
            logger.debug(f"No existing public key file for {pod_identifier}")

    # If no key files at all, or just not for that pod, retrieve key
    if pod_key := hub.get_pod_key(pod_identifier=pod_identifier, project_id=project_id):
        pod_public_key = _RSAEncryption.load_public_key(pod_key.encode())

        # Check that the downloaded key matches any existing one we have and save
        # it to the key store.
        return _check_known_pods(pod_identifier, pod_public_key, key_store_path)
    else:
        raise PodDoesNotExistError(f"No public key found for pod: {pod_identifier}")


def _get_pod_public_keys(
    pod_identifiers: Iterable[str],
    hub: BitfountHub,
    pod_public_key_paths: Optional[Mapping[str, Path]] = None,
    project_id: Optional[str] = None,
) -> dict[str, RSAPublicKey]:
    """Retrieve the public keys for a group of pods.

    Either loads it from disk or downloads it from BitfountHub.

    Args:
        pod_identifiers: The pod identifiers of the pods we want the public keys for.
        hub: Hub to download keys from.
        pod_public_key_paths: Mapping of pod identifiers to already existing key files.
            Optional.
        project_id: The project ID to use when connecting to the hub. Optional.

    Returns:
        A dictionary of pod identifiers to the public key for that pod.
    """
    # Either download public key, or load existing, for each pod
    loaded_pod_public_keys: dict[str, RSAPublicKey] = {
        pod_identifier: _get_pod_public_key(
            pod_identifier, hub, pod_public_key_paths, project_id=project_id
        )
        for pod_identifier in pod_identifiers
    }
    return loaded_pod_public_keys


def get_pod_schema(
    pod_identifier: str,
    save_file_path: Optional[Union[str, Path]] = None,
    hub: Optional[BitfountHub] = None,
    username: Optional[str] = None,
    project_id: Optional[str] = None,
    secrets: Optional[Union[APIKeys, ExternallyManagedJWT]] = None,
) -> BitfountSchema:
    """Get a pod's schema from the hub.

    Args:
        pod_identifier: The identifier of the pod. If supplied with only pod name
            assumes the namespace is the current user.
        save_file_path: Optional. Path to save the downloaded schema to. Won't save
            if not provided.
        hub: Optional. The BitfountHub to connect to. The default hub will be
             used if not provided.
        username: The username to use when connecting to the hub if a hub instance is
            not provided.
        project_id: The project ID to use when connecting to the hub.
        secrets: Optional. Either APIKeys or JWT to use for authentication.

    Returns:
        The loaded BitfountSchema object.
    """
    # Generate default hub if not provided
    if not hub:
        hub = _create_bitfounthub(username=username, secrets=secrets)
    elif username:
        logger.warning("Ignoring username argument as hub was provided.")

    # Check if full pod_identifier or pod name only
    if "/" not in pod_identifier:
        # Construct full pod identifier if needed
        pod_identifier = f"{hub.username}/{pod_identifier}"

    schema = hub.get_pod_schema(pod_identifier, project_id=project_id)

    # Save out schema if requested
    if save_file_path:
        schema.dump(Path(save_file_path).expanduser())
    return schema
