"""Exceptions related to NextGen interactions."""

from __future__ import annotations

from bitfount.exceptions import BitfountError
from bitfount.externals.ehr.exceptions import (
    NoMatchingPatientError,
    NonSpecificPatientError,
    NoPatientIDError,
    QuotaExceeded,
)


class NextGenAPIError(BitfountError):
    """Exception raised when interacting with NextGen's APIs."""

    pass


###########################
# NextGen FHIR Exceptions #
###########################
class NextGenFHIRAPIError(NextGenAPIError):
    """Exception raised when interacting with NextGen's FHIR API."""

    pass


class NonSpecificNextGenPatientError(NonSpecificPatientError, NextGenFHIRAPIError):
    """Exception raised when patient could not be narrowed to a single person."""

    pass


class NoMatchingNextGenPatientError(NoMatchingPatientError, NextGenFHIRAPIError):
    """Exception raised when no patient matching filters is found."""

    pass


class NoNextGenPatientIDError(NoPatientIDError, NextGenFHIRAPIError):
    """Exception raised when patient ID could not be extracted."""

    pass


#################################
# NextGen Enterprise Exceptions #
#################################
class NextGenEnterpriseAPIError(NextGenAPIError):
    """Exception raised when interacting with NextGen's Enterprise API."""

    pass


#####################
# Shared Exceptions #
#####################
class NextGenQuotaExceeded(
    QuotaExceeded, NextGenFHIRAPIError, NextGenEnterpriseAPIError
):
    """Exception raised when we have exceeded our NextGen daily call quota limit.

    This limit is detailed at https://developer.nextgen.com/wiki/pages/999bfa5c-947d-43df-a9ed-591d6690884f/intro-to-api-dev-portal
    and applies across the _entirety_ of Bitfount applications.

    It is indicated by receiving "a 200 status code but an empty payload".
    """

    pass
