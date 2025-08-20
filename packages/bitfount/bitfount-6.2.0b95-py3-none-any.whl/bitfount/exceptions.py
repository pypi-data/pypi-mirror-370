"""Custom exceptions for the Bitfount codebase."""

from __future__ import annotations

__all__: list[str] = [
    "BitfountEngineError",
    "BitfountError",
]


class BitfountError(Exception):
    """Base exception class that all others should inherit from."""

    pass


class BitfountEngineError(BitfountError):
    """Exception for any issues relating to the backend engine."""

    pass


class HookError(BitfountError):
    """Exception for any issues relating to hooks."""

    pass


class BitfountVersionError(BitfountError):
    """Exception for issues related to version incompatibility."""
