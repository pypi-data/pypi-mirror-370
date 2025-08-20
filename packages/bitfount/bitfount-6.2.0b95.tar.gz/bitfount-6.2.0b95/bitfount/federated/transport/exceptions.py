"""Transport layer exceptions."""

from __future__ import annotations

from bitfount.exceptions import BitfountError


class BitfountMessageServiceError(BitfountError):
    """Bitfount exception related to interaction with the message service."""

    pass
