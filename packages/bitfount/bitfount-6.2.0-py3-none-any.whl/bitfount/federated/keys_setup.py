"""Module for setting up the pod keys."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

from bitfount.encryption.encryption import _RSAEncryption
from bitfount.encryption.exceptions import RSAKeyError
from bitfount.federated.logging import _get_federated_logger

_POD_PRIVATE_KEY_FILE = "pod_rsa.pem"
_POD_PUBLIC_KEY_FILE = "pod_rsa.pub.pem"
_MODELLER_PRIVATE_KEY_FILE = "modeller_rsa.pem"
_MODELLER_PUBLIC_KEY_FILE = "modeller_rsa.pub.pem"
_MODELLER_KEY_ID_FILE = "modeller_key_id.txt"

logger = _get_federated_logger(__name__)


@dataclass
class RSAKeyPair:
    """A public-private RSA key pair.

    Args:
        public: The public key.
        private: The private key.
    """

    public: RSAPublicKey
    private: RSAPrivateKey


def _generate_key_pair(private_key_path: Path, public_key_path: Path) -> RSAKeyPair:
    """Generates, saves and returns an RSA key pair.

    Args:
        private_key_path: the path to save the private key to
        public_key_path: the path to save the public key to

    Returns:
        A tuple of (private key, public key)
    """
    private_key_path.parent.mkdir(exist_ok=True, parents=True)
    public_key_path.parent.mkdir(exist_ok=True, parents=True)

    private_key, public_key = _RSAEncryption.generate_key_pair()

    private_key_path.write_bytes(
        _RSAEncryption.serialize_private_key(private_key, form="SSH")
    )
    public_key_path.write_bytes(
        _RSAEncryption.serialize_public_key(public_key, form="SSH")
    )
    return RSAKeyPair(private=private_key, public=public_key)


def _load_key_pair(private_key_path: Path, public_key_path: Path) -> RSAKeyPair:
    """Loads an existing RSA key pair.

    Args:
        private_key_path: the path to load the private key from
        public_key_path: the path to load the public key from

    Returns:
        A tuple of (private key, public key)
    """
    public_key = _RSAEncryption.load_public_key(public_key_path)
    private_key = _RSAEncryption.load_private_key(private_key_path)

    if not _RSAEncryption.public_keys_equal(public_key, private_key.public_key()):
        raise RSAKeyError(
            f"The public key loaded from {str(public_key_path)} does not correspond"
            f" to the private key loaded from {str(private_key_path)}"
        )

    return RSAKeyPair(public=public_key, private=private_key)


def _get_key_pair(private_key_path: Path, public_key_path: Path) -> RSAKeyPair:
    """Get a pair of encryption keys.

    Get the keys from the target directory, generating them if they don't
    already exist.

    Args:
        private_key_path: path to load/generate the private key from/to
        public_key_path: path to load/generate the public key from/to

    Returns:
        A tuple of (private key, public key)
    """
    # If both keys exist, load them
    if private_key_path.exists() and public_key_path.exists():
        logger.debug(
            f"Loading private key ({str(private_key_path)})"
            f" and public key ({str(public_key_path)})"
        )
        key_pair = _load_key_pair(private_key_path, public_key_path)
    # If only the private key exists, extract and save the public key
    elif private_key_path.exists():
        logger.warning(
            f"Private key found at {str(private_key_path)} but no public key at"
            f" {str(public_key_path)}. Extracting public key from private key and"
            f" saving to {str(public_key_path)}."
        )
        private_key = _RSAEncryption.load_private_key(private_key_path)
        public_key = private_key.public_key()
        public_key_path.write_bytes(
            _RSAEncryption.serialize_public_key(public_key, form="SSH")
        )
        key_pair = RSAKeyPair(public_key, private_key)
    # If only the public key exists, unrecoverable
    elif public_key_path.exists():
        raise RSAKeyError(
            f"Could not find private key corresponding to public key"
            f" {str(public_key_path)} (private key path was {str(private_key_path)})"
        )
    # Otherwise generate new keys
    else:
        logger.debug(
            f"Generating and saving private key ({str(private_key_path)})"
            f" and public key ({str(public_key_path)})"
        )
        key_pair = _generate_key_pair(private_key_path, public_key_path)
    return key_pair


def _get_pod_keys(key_directory: Path) -> RSAKeyPair:
    """Gets the encryption key pair for the pod.

    Get the pod keys from the target directory, generating them if they don't
    already exist.

    Args:
        key_directory: the directory where the keys are located or should be saved

    Returns:
        A tuple of (private key, public key)
    """
    private_key_path = key_directory / _POD_PRIVATE_KEY_FILE
    public_key_path = key_directory / _POD_PUBLIC_KEY_FILE
    return _get_key_pair(private_key_path, public_key_path)


def _get_modeller_keys(key_directory: Path) -> RSAKeyPair:
    """Gets the encryption key pair for the modeller.

    Get the modeller keys from the target directory, generating them if they don't
    already exist.

    Args:
        key_directory: the directory where the keys are located or should be saved

    Returns:
        A tuple of (private key, public key)
    """
    private_key_path = key_directory / _MODELLER_PRIVATE_KEY_FILE
    public_key_path = key_directory / _MODELLER_PUBLIC_KEY_FILE
    return _get_key_pair(private_key_path, public_key_path)


def _store_key_id(key_directory: Path, key_id: str) -> None:
    # Create the file if it doesn't exist
    (key_directory / _MODELLER_KEY_ID_FILE).touch(exist_ok=True)
    with open(key_directory / _MODELLER_KEY_ID_FILE, "w") as key_id_file:
        key_id_file.write(key_id)


def _get_key_id(key_directory: Path) -> str:
    with open(key_directory / _MODELLER_KEY_ID_FILE) as key_id_file:
        return key_id_file.readline()
