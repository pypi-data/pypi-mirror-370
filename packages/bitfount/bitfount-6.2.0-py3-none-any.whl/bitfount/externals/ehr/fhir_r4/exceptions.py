"""Exceptions related to NextGen interactions."""

from __future__ import annotations

from bitfount.exceptions import BitfountError
from bitfount.externals.ehr.exceptions import (
    NoMatchingPatientError,
    NonSpecificPatientError,
    NoPatientIDError,
    QuotaExceeded,
)


class FHIRR4APIError(BitfountError):
    """Exception raised when interacting with FHIR R4 APIs."""

    pass


class NonSpecificFHIRR4PatientError(NonSpecificPatientError, FHIRR4APIError):
    """Exception raised when patient could not be narrowed to a single person."""

    pass


class NoMatchingFHIRR4PatientError(NoMatchingPatientError, FHIRR4APIError):
    """Exception raised when no patient matching filters is found."""

    pass


class NoFHIRR4PatientIDError(NoPatientIDError, FHIRR4APIError):
    """Exception raised when patient ID could not be extracted."""

    pass


class FHIRR4QuotaExceeded(QuotaExceeded, FHIRR4APIError):
    """Exception raised when we have exceeded any FHIR R4 call limit."""

    pass
