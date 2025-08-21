"""Datasource related types."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, NamedTuple, Optional, Protocol, Union

# TypedDict needs to be imported from typing_extensions to avoid pydantic errors
# https://docs.pydantic.dev/2.3/errors/usage_errors/#typed-dict-version
from typing_extensions import NotRequired, TypedDict

from bitfount.types import UsedForConfigSchemas


@dataclass
class Date(UsedForConfigSchemas):
    """Simple date class used for filtering files based on date headers.

    This is used by `FileSystemIterableSource` to filter files based on
    their creation and modification dates.

    Args:
        year: The oldest possible year to consider.
        month: The oldest possible month to consider. If None, all months
            in the given year are considered. Defaults to None.
        day: The oldest possible day to consider. If None, all days in the
            given month are considered. If month is None, this is ignored.
            Defaults to None.
    """

    year: int
    month: Optional[int] = None
    day: Optional[int] = None

    def get_date(self) -> date:
        """Get a datetime.date object from the date components year, month and day."""
        if self.month:
            if self.day:
                min_datetime = datetime(self.year, self.month, self.day)
            else:
                min_datetime = datetime(self.year, self.month, 1)
        else:
            min_datetime = datetime(self.year, 1, 1)

        return min_datetime.date()


class DateTD(TypedDict):
    """Typed dict form of Date dataclass."""

    year: int
    month: NotRequired[int]
    day: NotRequired[int]


# DICOM TYPES


class _DICOMField(NamedTuple):
    """Type definition for a DICOM field."""

    name: str
    value: Any


class _DICOMSequenceField(NamedTuple):
    """Named tuple for DICOM sequence field.

    Args:
        name: The name of the sequence field.
        elements: The elements of the sequence field.
    """

    name: str
    value: list[_DICOMSequenceElement]


class _DICOMSequenceElement(Protocol):
    """Typed dict form of DICOM sequence element."""

    def elements(self) -> list[Union[_DICOMField, _DICOMSequenceField]]: ...


class _DICOMImage(TypedDict):
    """Type definition for a DICOM image.

    None of the fields are required. The only other field-related assumption we are
    making is that if there is a field called "Pixel Data", that must mean there is
    also an attribute called `pixel_array` which is a numpy array. This should be a
    safe assumption based on the pydicom documentation.
    """

    NumberOfFrames: NotRequired[_DICOMField]
    PatientID: NotRequired[_DICOMField]
    StudyDate: NotRequired[_DICOMField]
    StudyTime: NotRequired[_DICOMField]
    pixel_array: NotRequired[Any]


class DataSourceFileFilter(Protocol):
    """A datasource-level filter that can be applied to files.

    Provides a datasource-level filter (i.e. one that does not rely solely on
    filesystem information, but instead on contents of the data) that can be applied
    to files to include/exclude it from a datasource.
    """

    def __call__(self, file_names: list[str]) -> list[str]:
        """Filter a list of files for those that match a criteria."""
        ...
