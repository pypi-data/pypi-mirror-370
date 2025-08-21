"""Symmetric and asymmetric encryption functions."""

from __future__ import annotations

import base64
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Final, Literal, Optional, Union, cast

from cryptography.exceptions import InvalidSignature, InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import (
    RSAPrivateKey,
    RSAPrivateKeyWithSerialization,
    RSAPublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, AESSIV
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from bitfount import config
from bitfount.encryption.exceptions import DecryptError, RSAKeyError

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.dh import DHPrivateKey
    from cryptography.hazmat.primitives.asymmetric.dsa import DSAPrivateKey
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
    from cryptography.hazmat.primitives.asymmetric.ed448 import Ed448PrivateKey
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.asymmetric.padding import MGF
    from cryptography.hazmat.primitives.asymmetric.x448 import X448PrivateKey
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
    from cryptography.hazmat.primitives.hashes import HashAlgorithm


_logger = logging.getLogger(__name__)

# RSA Constants
_RSA_PUBLIC_EXPONENT: Final[int] = 65537
_RSA_KEY_SIZE_BITS: Final[int] = 4096
# Salt length is padding.PSS.MAX_LENGTH, but we manually set it to ensure
# compatibility across platforms.
_RSA_SIGN_SALT_LENGTH: Final[int] = 20
# Encodings/formats
# Based on recommended encodings/formats from `cryptography`:
#   - https://cryptography.io/en/latest/hazmat/primitives/asymmetric/serialization/#cryptography.hazmat.primitives.serialization.PrivateFormat  # noqa: E501
#   - https://cryptography.io/en/latest/hazmat/primitives/asymmetric/serialization/#cryptography.hazmat.primitives.serialization.PublicFormat  # noqa: E501
# PEM - Private
_RSA_PEM_PRIVATE_ENCODING: Final[Encoding] = Encoding.PEM
_RSA_PEM_PRIVATE_FORMAT: Final[PrivateFormat] = PrivateFormat.PKCS8
# PEM - Public
_RSA_PEM_PUBLIC_ENCODING: Final[Encoding] = Encoding.PEM
_RSA_PEM_PUBLIC_FORMAT: Final[PublicFormat] = PublicFormat.SubjectPublicKeyInfo
# SSH - Private
_RSA_SSH_PRIVATE_ENCODING: Final[Encoding] = Encoding.PEM
_RSA_SSH_PRIVATE_FORMAT: Final[PrivateFormat] = PrivateFormat.OpenSSH
# SSH - Public
_RSA_SSH_PUBLIC_ENCODING: Final[Encoding] = Encoding.OpenSSH
_RSA_SSH_PUBLIC_FORMAT: Final[PublicFormat] = PublicFormat.OpenSSH

# AES Constants
# The AES key must provide at least as much security as the RSA key as they are
# both used in hybrid encryption (when the message is too large for RSA encryption
# alone).
#
# This NIST-based table allows us to find values which will enable that:
#   https://www.keylength.com/en/4/
_AES_KEY_SIZE_BITS: Final[int] = 256
_AES_NONCE_SIZE_BYTES: Final[int] = 12


def _read_file(file_to_read: Path) -> bytes:
    """Reads given file and returns contents as a byte string."""
    with open(file_to_read, "rb") as f:
        contents = f.read()
    return contents


def _calc_max_RSA_message_size(rsa_key: Union[RSAPrivateKey, RSAPublicKey]) -> int:
    """Calculates the maximum message size that can be encrypted.

    Calculates the maximum message size, in bytes, that can be encrypted with
    the supplied key.

    https://www.rfc-editor.org/rfc/rfc8017#section-7.1.1
    """
    # This is the approach used internally to cryptography
    # Rounded up byte-size from bit-size
    rsa_key_size_bytes = (rsa_key.key_size + 7) // 8

    # Get the expected padding settings and access the algorithm to get the
    # expected output size.
    oaep_hash_output_size_bytes = (
        _RSAEncryption._get_encryption_padding()._algorithm.digest_size
    )

    # Equation from: https://www.rfc-editor.org/rfc/rfc8017#section-7.1.1
    max_size = rsa_key_size_bytes - (2 * oaep_hash_output_size_bytes) - 2
    return max_size


class _RSAEncryption:
    """Class of functions for dealing with RSA asymmetric encryption."""

    @staticmethod
    def generate_key_pair() -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Generates a new RSA key pair."""
        _logger.debug("Generating RSA key pair")
        # Key size is 4096 bits which means we can only encrypt up to 4096 bits of data
        private_key = rsa.generate_private_key(
            public_exponent=_RSA_PUBLIC_EXPONENT,
            key_size=_RSA_KEY_SIZE_BITS,
            backend=default_backend(),
        )
        return private_key, private_key.public_key()

    @staticmethod
    def load_private_key(private_key: Union[bytes, Path]) -> RSAPrivateKey:
        """Loads a private key either from a byte string or file path."""
        _logger.debug("Attempting to load private key")
        if isinstance(private_key, Path):
            _logger.debug(f"Loading private key from path: {private_key}")
            private_key = _read_file(private_key)

        # Try loading from PEM format first
        try:
            _logger.debug("Attempting to load private key using PEM Format...")
            loaded_private_key = serialization.load_pem_private_key(
                private_key, password=None, backend=default_backend()
            )

        except ValueError as ve:
            # Otherwise try SSH format
            try:
                _logger.debug(
                    "Loading private key using PEM format failed,"
                    " trying to load using SSH format..."
                )
                loaded_private_key = serialization.load_ssh_private_key(
                    private_key, password=None, backend=default_backend()
                )
            except ValueError:
                # If both fail, raise the original error
                raise ve  # noqa: B904

        _logger.debug("Loaded private key")
        return cast(RSAPrivateKey, loaded_private_key)

    @staticmethod
    def serialize_private_key(
        private_key: RSAPrivateKeyWithSerialization, form: Literal["PEM", "SSH"] = "PEM"
    ) -> bytes:
        """Serializes a private key to bytes.

        `form` specifies how it should be encoded/formatted:
            PEM: PEM-encoded, PKCS8 format
            SSH: PEM-encoded, OpenSSH format
        """
        if form == "PEM":
            return private_key.private_bytes(
                _RSA_PEM_PRIVATE_ENCODING, _RSA_PEM_PRIVATE_FORMAT, NoEncryption()
            )
        elif form == "SSH":
            return private_key.private_bytes(
                _RSA_SSH_PRIVATE_ENCODING, _RSA_SSH_PRIVATE_FORMAT, NoEncryption()
            )
        else:
            raise RSAKeyError(
                f"Unable to serialize private key due to incorrect form;"
                f' expected one of "PEM" or "SSH", got "{form}"'
            )

    @staticmethod
    def load_public_key(public_key: Union[bytes, Path]) -> RSAPublicKey:
        """Loads a public key either from a byte string or file path."""
        _logger.debug("Attempting to load public key")
        if isinstance(public_key, Path):
            _logger.debug(f"Loading public key from path: {public_key}")
            public_key = _read_file(public_key)

        # Try loading from PEM format first
        try:
            _logger.debug("Attempting to load public key using PEM Format...")
            loaded_public_key = serialization.load_pem_public_key(
                public_key, backend=default_backend()
            )
        except ValueError as ve:
            # Otherwise try SSH format
            try:
                _logger.debug(
                    "Loading public key using PEM format failed, "
                    "trying to load using SSH format..."
                )
                loaded_public_key = serialization.load_ssh_public_key(
                    public_key, backend=default_backend()
                )
            except ValueError:
                # If both fail, raise the original error
                raise ve  # noqa: B904

        _logger.debug("Loaded public key")
        return cast(RSAPublicKey, loaded_public_key)

    @staticmethod
    def serialize_public_key(
        public_key: RSAPublicKey, form: Literal["PEM", "SSH"] = "PEM"
    ) -> bytes:
        """Serialize an RSAPublicKey to bytes.

        `form` specifies how it should be encoded/formatted:
            PEM: PEM-encoded, SubjectPublicKeyInfo format
            SSH: OpenSSH-encoded, Open SSH format
        """
        if form == "PEM":
            return public_key.public_bytes(
                _RSA_PEM_PUBLIC_ENCODING, _RSA_PEM_PUBLIC_FORMAT
            )
        elif form == "SSH":
            return public_key.public_bytes(
                _RSA_SSH_PUBLIC_ENCODING, _RSA_SSH_PUBLIC_FORMAT
            )
        else:
            raise RSAKeyError(
                f"Unable to serialize public key due to incorrect form;"
                f' expected one of "PEM" or "SSH", got "{form}"'
            )

    @staticmethod
    def _get_hashing_algorithm() -> HashAlgorithm:
        """Retrieves a new instance representing the chosen hash algorithm."""
        return hashes.SHA256()

    @staticmethod
    def _get_mask_gen_function() -> MGF:
        """Retrieves a new instance representing the chosen mask generator function."""
        return padding.MGF1(_RSAEncryption._get_hashing_algorithm())

    @staticmethod
    def _get_signature_padding() -> padding.PSS:
        """Retrieves a new instance representing the padding algo for signatures."""
        return padding.PSS(
            mgf=_RSAEncryption._get_mask_gen_function(),
            salt_length=_RSA_SIGN_SALT_LENGTH,
        )

    @staticmethod
    def _get_encryption_padding() -> padding.OAEP:
        """Retrieves a new instance representing the padding algo for encryption."""
        return padding.OAEP(
            mgf=_RSAEncryption._get_mask_gen_function(),
            algorithm=_RSAEncryption._get_hashing_algorithm(),
            label=None,
        )

    @staticmethod
    def sign_message(private_key: RSAPrivateKey, message: bytes) -> bytes:
        """Cryptographically signs a message.

        Signs provided `message` with provided `private_key` and returns signature.
        """
        signature = private_key.sign(
            message,
            padding=_RSAEncryption._get_signature_padding(),
            algorithm=_RSAEncryption._get_hashing_algorithm(),
        )

        return signature

    @staticmethod
    def verify_signature(
        public_key: RSAPublicKey, signature: bytes, message: bytes
    ) -> bool:
        """Verifies that decrypting `signature` with `public_key` === `message`."""
        try:
            public_key.verify(
                signature,
                message,
                padding=_RSAEncryption._get_signature_padding(),
                algorithm=_RSAEncryption._get_hashing_algorithm(),
            )
        except InvalidSignature:
            return False

        _logger.debug("Signature verified")
        return True

    @staticmethod
    def encrypt(message: bytes, public_key: RSAPublicKey) -> bytes:
        """Encrypts plaintext.

        Encrypts provided `message` with `public_key` and returns ciphertext.
        """
        # If message is small enough to be fully RSA encrypted then do that.
        if len(message) <= _calc_max_RSA_message_size(public_key):
            ciphertext = public_key.encrypt(
                message,
                _RSAEncryption._get_encryption_padding(),
            )
        # Otherwise, use hybrid encryption.
        else:
            _logger.debug(
                "Message too large for RSA encryption, using hybrid encryption."
            )

            # Encrypt message with AES key
            aes_key = _AESEncryption.generate_key()
            aes_ciphertext, aes_nonce = _AESEncryption.encrypt(aes_key, message)

            # Encrypt AES key using RSA encryption
            encrypted_aes_key = public_key.encrypt(
                aes_key,
                _RSAEncryption._get_encryption_padding(),
            )

            # Combine
            ciphertext = encrypted_aes_key + aes_nonce + aes_ciphertext
        return ciphertext

    @staticmethod
    def decrypt(
        ciphertext: bytes,
        private_key: RSAPrivateKey,
    ) -> bytes:
        """Decrypts ciphertext.

        Decrypts provided `ciphertext` with `private_key` and returns plaintext.

        Raises:
            DecryptError: if decryption fails.
        """
        # This is the approach used internally to cryptography
        # Rounded up byte-size from bit-size
        rsa_encrypted_size = (private_key.key_size + 7) // 8

        # If message is the expected RSA size then must have been purely RSA
        # encrypted. Decrypt directly.
        if len(ciphertext) <= rsa_encrypted_size:
            try:
                plaintext = private_key.decrypt(
                    ciphertext,
                    _RSAEncryption._get_encryption_padding(),
                )
            except ValueError as e:
                raise DecryptError("Unable to decrypt RSA-encrypted message.") from e
        # Otherwise, it must have been encrypted using hybrid encryption.
        else:
            # [LOGGING-IMPROVEMENTS]
            if config.settings.logging.log_message_service:
                _logger.debug(
                    "Message too large for RSA encryption, using hybrid decryption."
                )

            # Split received message into relevant parts.
            encrypted_aes_key, aes_payload = (
                ciphertext[:rsa_encrypted_size],
                ciphertext[rsa_encrypted_size:],
            )
            aes_nonce, aes_ciphertext = (
                aes_payload[:_AES_NONCE_SIZE_BYTES],
                aes_payload[_AES_NONCE_SIZE_BYTES:],
            )

            # Decrypt AES key
            try:
                aes_key = private_key.decrypt(
                    encrypted_aes_key,
                    _RSAEncryption._get_encryption_padding(),
                )
            except ValueError as e:
                raise DecryptError(
                    "Unable to decrypt AES key in hybrid RSA-encrypted message."
                ) from e

            # Decrypt message body
            try:
                plaintext = _AESEncryption.decrypt(aes_key, aes_nonce, aes_ciphertext)
            except DecryptError as e:
                raise DecryptError(
                    "Unable to decrypt ciphertext in hybrid RSA-encrypted message."
                ) from e

        return plaintext

    @staticmethod
    def public_keys_equal(k1: RSAPublicKey, k2: RSAPublicKey) -> bool:
        """Compare two RSA public keys for equality."""
        # Cannot compare keys directly as cryptography package does not support
        # direct equality checks:
        # https://github.com/pyca/cryptography/issues/3396
        return k1.public_numbers() == k2.public_numbers()

    @staticmethod
    def private_keys_equal(k1: RSAPrivateKey, k2: RSAPrivateKey) -> bool:
        """Compare two RSA private keys for equality."""
        # Cannot compare keys directly as cryptography package does not support
        # direct equality checks:
        # https://github.com/pyca/cryptography/issues/2122
        return k1.private_numbers() == k2.private_numbers()


class _AESEncryption:
    """Class of functions for dealing with AES symmetric encryption."""

    @staticmethod
    def generate_key() -> bytes:
        """Generates a symmetric encryption key.

        Generates symmetric key using the GCM algorithm (Galois Counter Mode).

        (More secure than CBC (Cipher Block Chaining)).
        """
        key = AESGCM.generate_key(_AES_KEY_SIZE_BITS)  # 256 bits is sufficiently secure
        return key

    @staticmethod
    def encrypt(
        key: bytes, plaintext: bytes, associated_data: Optional[bytes] = None
    ) -> tuple[bytes, bytes]:
        """Encrypts plaintext.

        Encrypts `plaintext` using `key` and a randomly generated `nonce`.
        If `associated_data` is provided, it is authenticated.
        """
        aesgcm = AESGCM(key)
        nonce = os.urandom(_AES_NONCE_SIZE_BYTES)  # 12 bytes
        ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)

        return ciphertext, nonce

    @staticmethod
    def decrypt(
        key: bytes,
        nonce: bytes,
        ciphertext: bytes,
        associated_data: Optional[bytes] = None,
    ) -> bytes:
        """Decrypts ciphertext.

        Decrypts `ciphertext` using `key`, `nonce` and `associated_data` if present.

        If `associated_data` is provided, this must be the same associated data
        used in encryption.

        ***
        NONCE MUST ONLY BE USED ONCE FOR A GIVEN KEY (SAME NONCE AS USED FOR
        ENCRYPTION)
        ***

        Raises:
            DecryptError: if decryption fails.
        """
        aesgcm = AESGCM(key)

        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data)
        except InvalidTag as e:
            raise DecryptError("Unable to decrypt ciphertext") from e

        return plaintext


class _DeterministicAESEncryption:
    """Class of functions for dealing with deterministic AES symmetric encryption.

    Uses AESSIV (https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESSIV)
    which allows for deterministic encryption where the same plaintext can be
    consistently mapped to the same ciphertext.
    """

    @staticmethod
    def generate_key() -> bytes:
        """Generates a random AES-SIV key."""
        # 256 bits is sufficiently secure but AESSIV uses a key double sized from
        # typical AES
        key = AESSIV.generate_key(_AES_KEY_SIZE_BITS * 2)
        return key

    @staticmethod
    def generate_nonce() -> bytes:
        """Generates a random AES-SIV nonce."""
        return os.urandom(16)  # 128-bit nonce

    @staticmethod
    def encrypt(key: bytes, plaintext: bytes, nonce: Optional[bytes] = None) -> bytes:
        """Encrypts plaintext.

        Encrypts `plaintext` using `key` and the optionally supplied nonce.

        Random nonces should have at least 128-bits of entropy. If a nonce is reused
        with SIV authenticity is retained and confidentiality is only compromised to
        the extent that an attacker can determine that the same plaintext (and same
        associated data) was protected with the same nonce and key.

        If you do not supply a nonce, encryption is deterministic and the same
        (plaintext, key) pair will always produce the same ciphertext.
        """
        if nonce:
            associated_data = [nonce]
        else:
            associated_data = None

        aessiv = AESSIV(key)
        ciphertext = aessiv.encrypt(plaintext, associated_data)

        return ciphertext

    @staticmethod
    def decrypt(key: bytes, ciphertext: bytes, nonce: Optional[bytes] = None) -> bytes:
        """Decrypts ciphertext.

        Decrypts `ciphertext` using `key`, and `nonce`. If you called encrypt with a
        nonce you must pass the same nonce in decrypt or the integrity check will fail.

        Raises:
            DecryptError: if decryption fails.
        """
        if nonce:
            associated_data = [nonce]
        else:
            associated_data = None

        aessiv = AESSIV(key)
        try:
            plaintext = aessiv.decrypt(ciphertext, associated_data)
        except InvalidTag as e:
            raise DecryptError("Unable to decrypt ciphertext") from e

        return plaintext


class _FernetEncryption:
    """Class of functions for Fernet encryption key derivation from SSH keys."""

    @staticmethod
    def derive_key_from_bytes(ssh_private_key_bytes: bytes, salt: bytes = b"") -> bytes:
        """Derive a Fernet key from SSH private key bytes.

        Args:
            ssh_private_key_bytes: Bytes of the SSH private key
            salt: Salt to use for key derivation

        Returns:
            Fernet key bytes
        """
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,  # Fernet requires 32 bytes
            salt=salt,
            info=b"fernet-key-derivation",
        )

        derived_key = hkdf.derive(ssh_private_key_bytes)
        return base64.urlsafe_b64encode(derived_key)

    @staticmethod
    def derive_key_from_path(
        ssh_key_path: Path,
        ssh_key_password: Optional[str] = None,
        salt: bytes = b"",
    ) -> Optional[bytes]:
        """Create and return a Fernet key for decryption.

        Args:
            ssh_key_path: Path to the SSH key file
            ssh_key_password: Password to decrypt the SSH key
            salt: Salt to use for key derivation

        Returns:
            Fernet key bytes or None if key file doesn't exist
            or parameters are missing
        """
        try:
            with open(ssh_key_path, "rb") as key_file:
                key_data = key_file.read()

                # Try loading as OpenSSH format first
                private_key: Union[
                    DHPrivateKey,
                    DSAPrivateKey,
                    EllipticCurvePrivateKey,
                    Ed25519PrivateKey,
                    Ed448PrivateKey,
                    RSAPrivateKey,
                    X25519PrivateKey,
                    X448PrivateKey,
                ]
                try:
                    private_key = serialization.load_ssh_private_key(
                        key_data,
                        password=(
                            ssh_key_password.encode() if ssh_key_password else None
                        ),
                    )
                except ValueError:
                    # If OpenSSH format fails, try PEM format
                    private_key = serialization.load_pem_private_key(
                        key_data,
                        password=(
                            ssh_key_password.encode() if ssh_key_password else None
                        ),
                    )

                # All private key types have the private_bytes method
                private_key_bytes = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )

                return _FernetEncryption.derive_key_from_bytes(private_key_bytes, salt)
        except FileNotFoundError:
            _logger.warning("SSH key file not found at a configured path")
            return None
        except Exception as e:
            _logger.error(f"Error reading SSH key: {e}")
            return None
