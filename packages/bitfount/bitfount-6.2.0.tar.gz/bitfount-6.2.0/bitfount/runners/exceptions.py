"""Custom exceptions for the runners package."""

from __future__ import annotations

from bitfount import BitfountError


class PlugInAlgorithmError(BitfountError):
    """Raised if the specified algorithm in not found in the plugins."""

    pass


class PlugInProtocolError(BitfountError):
    """Raised if the specified protocol in not found in the plugins."""

    pass
