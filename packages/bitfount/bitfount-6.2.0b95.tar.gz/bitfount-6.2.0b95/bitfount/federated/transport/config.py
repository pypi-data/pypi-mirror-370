"""Message Service configuration."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import socket
from typing import Optional

from bitfount.config import (
    _DEVELOPMENT_ENVIRONMENT,
    _SANDBOX_ENVIRONMENT,
    _STAGING_ENVIRONMENT,
    _get_environment,
)
from bitfount.types import UsedForConfigSchemas

logger = logging.getLogger(__name__)

#: Production message service URL.
PRODUCTION_MESSAGE_SERVICE_URL = "messaging.bitfount.com"
_STAGING_MESSAGE_SERVICE_URL = "messaging.staging.bitfount.com"
_SANDBOX_MESSAGE_SERVICE_URL = "messaging.sandbox.bitfount.com"
_DEV_MESSAGE_SERVICE_URL = "localhost"
_DEV_MESSAGE_SERVICE_PORT = 5001
_DEV_MESSAGE_SERVICE_TLS = False


@dataclass
class MessageServiceConfig(UsedForConfigSchemas):
    """Configuration for the message service.

    Args:
        url: The URL of the message service. Defaults to
            `PRODUCTION_MESSAGE_SERVICE_URL`.
        port: The port of the message service. Defaults to 443.
        tls: Whether to use TLS. Defaults to True.
        use_local_storage: Whether to use local storage instead of communicating via the
            message service if both parties are on the same device. This can be used to
            remove the overhead of communication. Defaults to False.

    Raises:
        ValueError: If `tls` is False and `url` is a Bitfount URL.
    """

    url: Optional[str] = None
    port: int = 443
    tls: bool = True  # only used for development
    use_local_storage: bool = False

    def __post_init__(self) -> None:
        if not self.url:
            # get the correct URL based on environment
            environment = _get_environment()
            if environment == _STAGING_ENVIRONMENT:
                self.url = _STAGING_MESSAGE_SERVICE_URL
            elif environment == _DEVELOPMENT_ENVIRONMENT:
                self.url = _DEV_MESSAGE_SERVICE_URL
                self.port = _DEV_MESSAGE_SERVICE_PORT
                self.tls = _DEV_MESSAGE_SERVICE_TLS
            elif environment == _SANDBOX_ENVIRONMENT:
                self.url = _SANDBOX_MESSAGE_SERVICE_URL
            else:
                self.url = PRODUCTION_MESSAGE_SERVICE_URL
        if not self.tls and ".bitfount.com" in self.url:
            raise ValueError(
                "TLS disabled. Message service communication must be with TLS."
            )
        elif not self.tls:
            logger.warning("Message service communication without TLS.")

        # Log the config for easier debugging.
        logger.debug(f"Message service configuration: {vars(self)}")

    def test_connection(self) -> bool:
        """Check if the Message Service instance is reachable."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            result = s.connect_ex((self.url, self.port))
            s.close()
            if result == 0:
                return True
            else:
                return False
        except OSError:
            return False
