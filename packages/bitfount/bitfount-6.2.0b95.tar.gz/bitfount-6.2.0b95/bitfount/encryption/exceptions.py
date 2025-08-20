"""Exceptions related to encryption."""

from __future__ import annotations

from bitfount.exceptions import BitfountError


class EncryptionError(BitfountError):
    """Error related to encryption processes."""

    pass


class DecryptError(EncryptionError):
    """Error when attempting to decrypt."""

    pass


class RSAKeyError(EncryptionError):
    """Error related to RSA keys."""

    pass
