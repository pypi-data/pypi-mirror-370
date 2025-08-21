"""Custom exceptions for the hub package."""

from __future__ import annotations

from bitfount.exceptions import BitfountError
from bitfount.externals.general.exceptions import AuthenticationError


class AuthenticatedUserError(AuthenticationError):
    """Error related to user authentication."""

    pass


class PodDoesNotExistError(BitfountError):
    """Errors related to references to a non-existent Pod."""

    pass


class SchemaUploadError(BitfountError, ValueError):
    """Could not upload schema to hub."""

    pass


class ModelUploadError(BitfountError):
    """Error occurred whilst uploading model to hub."""

    pass


class ModelValidationError(ModelUploadError):
    """Error occurred in validating model format."""

    pass


class ModelTooLargeError(ModelUploadError, ValueError):
    """The model is too large to upload to the hub."""

    pass


class NoModelCodeError(BitfountError):
    """The model exists but no download URL was returned by the hub."""

    pass


############################
# SMART on FHIR Exceptions #
############################
class SMARTOnFHIRError(BitfountError):
    """Exception raised when interacting with SMART on FHIR system."""

    pass
