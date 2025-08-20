"""Types for ophthalmology data sources."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any, Literal, NamedTuple, Optional, Protocol, TypedDict, Union

import pandas as pd
from typing_extensions import NotRequired

from bitfount.data.datasources.types import _DICOMField

OphthalmologyModalityType = Literal["OCT", "SLO", None]


# PRIVATE EYE TYPES

PRIVATE_EYE_PATIENT_DOB_ATTRIBUTE = "date_of_birth"


class Metadata(TypedDict):
    """The initial JSON output of from parsing a single ophthalmology file."""

    patient: _PatientInfo
    exam: _ExamInfo
    series: _SeriesInfo
    images: _ImagesInfo


# Processed Data Required Types for DICOM compatiblitity
# These have been specified in a separate class to `ProcessedDataRequiredTypes` so
# that a different method of instantiation can be used to allow for spaces in the
# field names.
ProcessedDataRequiredTypesDICOM = TypedDict(
    "ProcessedDataRequiredTypesDICOM",
    {
        "Columns": int,
        "Rows": int,
        "Pixel Spacing Row": float,
        "Pixel Spacing Column": float,
        "Slice Thickness": float,
        "Number of Frames": int,
        "Patient's Birth Date": Union[str, pd.Timestamp],
        "Patient's Sex": str,
        "Patient's Name": str,
        "Scan Laterality": str,
        "Acquisition DateTime": Union[str, pd.Timestamp],
        "Study Date": Union[str, pd.Timestamp],
        "Manufacturer": str,
        "Manufacturer's Model Name": str,
    },
)


class ProcessedDataRequiredTypes(ProcessedDataRequiredTypesDICOM):
    """The final output of the processing from a single ophthalmology file."""

    images: NotRequired[list[str]]  # list of paths
    source_info: str
    group_id: int
    slo_size_width: int
    slo_size_height: int
    slo_dimensions_mm_width: float
    slo_dimensions_mm_height: float
    size_width: int
    size_height: int
    dimensions_mm_width: float
    dimensions_mm_height: float
    dimensions_mm_depth: float
    resolutions_mm_width: float
    resolutions_mm_height: float
    resolutions_mm_depth: float
    photo_locations_start_x: list[float]
    photo_locations_start_y: list[float]
    photo_locations_end_x: list[float]
    photo_locations_end_y: list[float]
    slo_images: NotRequired[list[str]]  # list of paths
    patient_key: str
    first_name: str
    last_name: str
    scan_datetime: str
    scanner_model: str
    laterality: str
    fixation: str
    protocol: str
    num_bscans: int
    num_modalities: int
    gender: str
    date_of_birth: str

    # Metadata
    _original_filename: str
    _last_modified: Union[str, datetime]
    _series_index: int


ProcessedDataTypes = Union[ProcessedDataRequiredTypes, dict]


class _PatientInfo(TypedDict):
    """Patient information."""

    patient_key: str
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str


class _ExamInfo(TypedDict):
    """Exam information."""

    manufacturer: str
    scan_datetime: str
    scanner_model: str


class _SeriesInfo(TypedDict):
    """Series information."""

    laterality: str
    fixation: str
    protocol: Literal["OCT ART Volume", "Rectangular volume"]


class _ImageSize(TypedDict):
    """OCT image size."""

    width: float
    height: float
    depth: NotRequired[float]  # only present for OCT images


class _PrivateEyeImage(TypedDict):
    """Image sequence."""

    group_id: Optional[int]
    size: _ImageSize
    resolutions_mm: _ImageSize
    dimensions_mm: _ImageSize
    contents: list[Any]
    modality: str


_ImageSequence = list[_PrivateEyeImage]


class _ImagesInfo(TypedDict):
    """Images information."""

    images: _ImageSequence


# DICOM TYPES


class DICOMImage(NamedTuple):
    """Named tuple for a DICOM image."""

    AcquisitionDeviceTypeCodeSequence: Sequence[
        _AcquisitionDeviceTypeCodeSequenceElement
    ]
    PatientName: str
    PatientBirthDate: str
    AcquisitionDateTime: str
    ImageLaterality: str
    NumberOfFrames: int


class ProcessedDICOMImage(NamedTuple):
    """Named tuple for a processed DICOM image."""

    file_name: str
    modality: OphthalmologyModalityType
    patient_key: str
    acquisition_datetime: Optional[datetime]


class _AcquisitionDeviceTypeCodeSequenceElement(NamedTuple):
    """Named tuple for Acquisition Device Type Code Sequence (0008, 1094)."""

    CodeValue: str
    CodingSchemeDesignator: str
    CodeMeaning: str


class _SliceThicknessElement(_DICOMField):
    """Named tuple for slice thickness element (0018, 0050)."""

    name: Literal["Slice Thickness"]
    value: float


class _PixelSpacingElement(_DICOMField):
    """Named tuple for pixel spacing element (0028, 0030)."""

    name: Literal["Pixel Spacing"]
    value: tuple[float, float]  # row, column


# Union of the two possible sequence elements within the sequence field
# Pixel Measures Sequence (0028, 9110)
_PixelMeasure = Union[_SliceThicknessElement, _PixelSpacingElement]


class _AcquisitionDeviceTypeCodeSequenceField(NamedTuple):
    """Named tuple for Acquisition Device Type Code Sequence field (0008, 1094).

    Args:
        name: The name of the sequence field.
        elements: The elements of the sequence field.
    """

    name: Literal["Acquisition Device Type Code Sequence"]
    value: list[_AcquisitionDeviceTypeCodeSequenceElement]


# Types for Functional Groups Sequence (5200, {9229, 9230}) fields
# and its nested sequence field Pixel Measures Sequence (0028, 9110)
class FunctionalGroupsSequenceField(NamedTuple):
    """Named tuple for Functional Groups Sequence Fields.

    Applies to Shared Functional Groups Sequence (5200, 9229) and
    Per-Frame Functional Groups Sequence (0028, 9230).

    Args:
        name: The name of the sequence field.
        elements: The elements of the sequence field.
    """

    name: Literal[
        "Shared Functional Groups Sequence", "Per-Frame Functional Groups Sequence"
    ]
    value: list[_FunctionalGroupsSequenceFieldElement]


class _PixelMeasuresSequenceField(NamedTuple):
    """Named tuple for Pixel Measures Sequence (0028, 9110) sequence field.

    Args:
        name: The name of the sequence field.
        elements: The elements of the sequence field.
    """

    name: Literal["Pixel Measures Sequence"]
    value: list[_PixelMeasuresSequenceElement]


class _PixelMeasuresSequenceElement(Protocol):
    """Pixel Measures Sequence (0028, 9110) sequence element."""

    def elements(self) -> list[_PixelMeasure]:
        """Return the elements of the sequence element."""
        ...


class _FunctionalGroupsSequenceFieldElement(Protocol):
    """Functional Groups Sequence (5200, {9229, 9230}) sequence field."""

    def elements(self) -> list[_PixelMeasuresSequenceField]:
        """Return the elements of the sequence field."""
        ...


FunctionalGroupsSequenceProcessingOutput = TypedDict(
    "FunctionalGroupsSequenceProcessingOutput",
    {
        "Slice Thickness": float,
        "Pixel Spacing Row": float,
        "Pixel Spacing Column": float,
    },
)
