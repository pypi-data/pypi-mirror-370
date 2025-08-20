"""Typed wrappers around the Bitfount REST api."""

from __future__ import annotations

from bitfount.hub.api import BitfountAM, BitfountHub, PodPublicMetadata
from bitfount.hub.authentication_flow import BitfountSession
from bitfount.hub.authentication_handlers import (
    APIKeysHandler,
    AuthenticationHandler,
    DeviceCodeFlowHandler,
    ExternallyManagedJWTHandler,
)
from bitfount.hub.exceptions import (
    ModelTooLargeError,
    ModelUploadError,
    ModelValidationError,
    PodDoesNotExistError,
    SchemaUploadError,
)
from bitfount.hub.helper import get_pod_schema
from bitfount.hub.types import PRODUCTION_AM_URL, PRODUCTION_HUB_URL

__all__: list[str] = [
    "APIKeysHandler",
    "AuthenticationHandler",
    "BitfountAM",
    "BitfountHub",
    "BitfountSession",
    "DeviceCodeFlowHandler",
    "ExternallyManagedJWTHandler",
    "ModelTooLargeError",
    "ModelUploadError",
    "ModelValidationError",
    "PRODUCTION_AM_URL",
    "PRODUCTION_HUB_URL",
    "PodDoesNotExistError",
    "PodPublicMetadata",
    "SchemaUploadError",
    "get_pod_schema",
]

# See top level `__init__.py` for an explanation
__pdoc__ = {}
for _obj in __all__:
    __pdoc__[_obj] = False
