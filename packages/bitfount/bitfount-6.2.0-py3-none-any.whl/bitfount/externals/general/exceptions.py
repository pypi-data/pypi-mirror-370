"""Generic exceptions for interacting with external services."""

from __future__ import annotations

from bitfount.exceptions import BitfountError


class AuthenticationError(BitfountError, ValueError):
    """Authentication error occurred."""

    pass
