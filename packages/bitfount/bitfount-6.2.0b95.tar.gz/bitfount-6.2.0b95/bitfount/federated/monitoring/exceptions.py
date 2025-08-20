"""Exceptions related to monitoring modules."""

from __future__ import annotations

from bitfount.exceptions import BitfountError


class MonitorModuleError(BitfountError):
    """Base exception for monitor module errors."""

    pass


class NoMonitorModuleError(MonitorModuleError):
    """Error for when a monitor module should exist but doesn't."""

    pass


class ExistingMonitorModuleError(MonitorModuleError):
    """Error for when a monitor module already exists.

    Raised when trying to create a second monitor module.
    """

    pass
