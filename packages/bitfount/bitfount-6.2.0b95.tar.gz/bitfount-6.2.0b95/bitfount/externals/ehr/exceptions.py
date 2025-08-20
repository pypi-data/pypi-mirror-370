"""EHR-related exceptions."""


class GetPatientInfoError(BaseException):
    """Could not retrieve patient info."""

    pass


class NonSpecificPatientError(BaseException):
    """Exception raised when patient could not be narrowed to a single person."""

    pass


class NoMatchingPatientError(BaseException):
    """Exception raised when no patient matching filters is found."""

    pass


class NoPatientIDError(BaseException):
    """Exception raised when patient ID could not be extracted."""

    pass


class QuotaExceeded(BaseException):
    """Exception raised when we have exceeded our API call quota limit."""

    pass
