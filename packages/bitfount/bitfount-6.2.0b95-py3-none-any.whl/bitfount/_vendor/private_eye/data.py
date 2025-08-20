from abc import ABC
from collections import Counter
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple, TypeVar, Union, cast, no_type_check

import attr
import numpy as np
from PIL.Image import Image
from ..private_eye.consts import (
    EntireFileOutputFormat,
    ImageModality,
    IndividualImageOutputFormat,
    Laterality,
    SectionName,
)
from ..private_eye.utils.attrs import json_ignore_ib
from ..private_eye.version import separated_version
from pydicom.uid import (
    EncapsulatedPDFStorage,
    OphthalmicVisualFieldStaticPerimetryMeasurementsStorage,
    RawDataStorage,
)

ImageTransform = Callable[[np.ndarray], np.ndarray]


def _not_negative(obj: Any, attribute: attr.Attribute, val: int) -> None:
    if val < 0:
        raise ValueError("Must be a non-negative number")


def _non_empty(obj: Any, attribute: attr.Attribute, val: str) -> None:
    if val == "":
        raise ValueError("Empty string is not valid for attribute")


@no_type_check
def _optional_instance_of(_type):
    return attr.validators.optional(attr.validators.instance_of(_type))


_non_empty_string = attr.validators.and_(attr.validators.instance_of(str), _non_empty)


def _is_absolute_path(obj: Any, attribute: attr.Attribute, value: Any) -> None:
    assert isinstance(value, Path)
    if not cast(Path, value).is_absolute():
        raise ValueError("Image output paths must be absolute")


Number = Union[int, float]


class ImageSourceDataType(Enum):
    JPEG2000 = 0
    UINT8 = 1
    UINT16 = 2
    TIFF = 3
    IMAGENET2000 = 4
    DICOM = 5
    JPEG = 6


@attr.s(auto_attribs=True, frozen=True, slots=True, eq=True)
class ImageProcessingOptions:
    topcon_no_clip_bscan: bool = False
    heidelberg_skip_shape_adjust: bool = False
    heidelberg_skip_intensity_adjust: bool = False
    zeiss_no_censor_annotations: bool = False

    def identifier(self) -> str:
        PREFIX_MAPPING = {
            "topcon_no_clip_bscan": "TC_",
            "heidelberg_skip_shape_adjust": "HS_",
            "heidelberg_skip_intensity_adjust": "HI_",
            "zeiss_no_censor_annotations": "ZC_",
        }
        output_prefix = ""
        if not self.topcon_no_clip_bscan:
            output_prefix += PREFIX_MAPPING["topcon_no_clip_bscan"]
        if not self.heidelberg_skip_shape_adjust:
            output_prefix += PREFIX_MAPPING["heidelberg_skip_shape_adjust"]
        if not self.heidelberg_skip_intensity_adjust:
            output_prefix += PREFIX_MAPPING["heidelberg_skip_intensity_adjust"]
        if not self.zeiss_no_censor_annotations:
            output_prefix += PREFIX_MAPPING["zeiss_no_censor_annotations"]
        return output_prefix or "NONE_"


@attr.s(auto_attribs=True, frozen=True, slots=True, eq=True)
class ParserOptions:
    """
    full_parse: Whether or not the parser will read the entire file when scanning.
    skip_image_data: Whether to skip raw image data when scanning. Useful if only file metadata is required.

    on_string_decode_error: Passed to bytes.decode when decoding strings - set to "ignore" to ignore errors and
        "replace" to replace them https://docs.python.org/3/library/stdtypes.html#bytes.decode

    topcon_encoding: The encoding to use when parsing Topcon strings.  See
    https://docs.python.org/3/library/codecs.html#standard-encodings for the standard Python encodings.

    heidelberg_ignore_patient_data: Allow reading Heidelberg files which don't have a pdb

    image_processing_options: List of ImageProcessingOptions. Where image processing options contains the following
        data:

        topcon_no_clip_bscan: When parsing topcon images, don't perform any rescaling.

        heidelberg_skip_shape_adjust: Don't adjust the shape of Heidelberg bscans
        heidelberg_skip_intensity_adjust: Don't adjust the intensity of heidelberg bscans, and don't downsample to 8bit

        zeiss_no_censor_annotations: Don't censor burnt in annotations on Zeiss images
    """

    full_parse: bool = False
    skip_image_data: bool = False
    on_string_decode_error: str = "strict"
    topcon_encoding: str = "Cp1252"
    heidelberg_skip_pdb: bool = False
    image_processing_options: Sequence[ImageProcessingOptions] = attr.ib(default=[ImageProcessingOptions()])

    @image_processing_options.validator
    def check_minimum_length(self, _: str, value: Sequence[ImageProcessingOptions]) -> None:
        if len(value) < 1:
            raise ValueError("Must have at least one image processing option set.")


@attr.s(auto_attribs=True, frozen=True, slots=True)
class IndividualImageOutputRequest:
    source_id: str
    output_path_prefix: Path = attr.ib(validator=_is_absolute_path)
    output_format: IndividualImageOutputFormat
    output_sensitive_data: bool
    pepper: Optional[str] = attr.ib(repr=lambda pepper: "*REDACTED*" if pepper else "None")
    extra_entropy: List[Any] = attr.ib(factory=list)
    image_modality_code: Optional[str] = attr.ib(default=None)
    save_to_file: bool = True


@attr.s(auto_attribs=True, frozen=True, slots=True)
class EntireFileOutputRequest:
    output_path_prefix: Path = attr.ib(validator=_is_absolute_path)
    output_format: EntireFileOutputFormat
    output_sensitive_data: bool
    pepper: Optional[str] = attr.ib(repr=lambda pepper: "*REDACTED*" if pepper else "None")


OutputRequest = Union[IndividualImageOutputRequest, EntireFileOutputRequest]


@attr.s(frozen=True, slots=True, repr=False)
class Size2D:
    width: Number = attr.ib(validator=_not_negative)
    height: Number = attr.ib(validator=_not_negative)

    def to_tuple(self) -> Tuple[Number, Number]:
        return self.width, self.height

    def __mul__(self, other: Number) -> "Size2D":
        return Size2D(self.width * other, self.height * other)

    __rmul__ = __mul__

    def __repr__(self) -> str:
        return f"Size2D({self.width}, {self.height})"


@attr.s(frozen=True, slots=True, repr=False)
class Size3D:
    width: Number = attr.ib(validator=_not_negative)
    height: Number = attr.ib(validator=_not_negative)
    depth: Number = attr.ib(validator=_not_negative)

    def to_tuple(self) -> Tuple[Number, Number, Number]:
        return self.width, self.height, self.depth

    def __repr__(self) -> str:
        return f"Size3D({self.width}, {self.height}, {self.depth})"


@attr.s(auto_attribs=True, frozen=True, slots=True, repr=False)
class Point:
    x: int
    y: int

    def to_tuple(self) -> Tuple[int, int]:
        return self.x, self.y

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

    def __mul__(self, other: int) -> "Point":
        return Point(self.x * other, self.y * other)

    __rmul__ = __mul__


@attr.s(auto_attribs=True, frozen=True, slots=True, repr=False)
class PointF:
    x: float
    y: float

    def to_tuple(self) -> Tuple[float, float]:
        return self.x, self.y

    def __repr__(self) -> str:
        return f"PointF({self.x}, {self.y})"

    def __mul__(self, other: Number) -> "PointF":
        return PointF(self.x * other, self.y * other)

    __rmul__ = __mul__


@attr.s(auto_attribs=True, frozen=True, repr=False)
class Circle:
    centre: PointF
    radius: float
    # Measured in radians from the positive x-axis
    start_angle: float

    def __repr__(self) -> str:
        return f"Circle(centre=({self.centre.x}, {self.centre.y}), radius={self.radius})"


@attr.s(auto_attribs=True, frozen=True, repr=False)
class Line:
    start: PointF
    end: PointF

    def __repr__(self) -> str:
        return f"Line(start=({self.start.x}, {self.start.y}), end=({self.end.x}, {self.end.y}))"


BscanLocation = Union[Line, Circle]


class AbstractData(ABC):
    """
    Base class for all sections of a parsed file
    """


TImageData = TypeVar("TImageData", bound=AbstractData)
TExternalData = TypeVar("TExternalData")


class DebugData(dict, AbstractData):
    """Raw debug data."""

    images: Dict[str, Image]
    files: Dict[str, bytes]

    def __init__(
        self, metadata: dict, images: Optional[Dict[str, Image]] = None, files: Optional[Dict[str, bytes]] = None
    ) -> None:
        super().__init__(metadata)

        self.images = {} if images is None else images
        self.files = {} if files is None else files

    def get_images(self) -> Dict[str, Image]:
        return self.images

    def get_files(self) -> Dict[str, bytes]:
        return self.files


@attr.s(auto_attribs=True, frozen=True)
class PatientData(AbstractData):
    """Data class containing all information pertaining to the patient"""

    # MEH patient key
    patient_key: Optional[str] = attr.ib(validator=_optional_instance_of(str))

    # Patient first name
    first_name: Optional[str] = attr.ib(validator=_optional_instance_of(str))

    # Patient last name
    last_name: Optional[str] = attr.ib(validator=_optional_instance_of(str))

    # Patient date of birth
    date_of_birth: Optional[date] = attr.ib(validator=_optional_instance_of(date))

    # Patient gender
    gender: Optional[str] = attr.ib(validator=_optional_instance_of(str))

    # Source ID
    # Identifier used by the specific manufacturer and site to uniquely identify the patient.  On some manufacturers
    # this is the same as the patient key (e.g. topcon), on others it is not (e.g. Heidelberg).
    #
    # This field is used along with manufacturer and site by the librarian and portable librarian to deduce equality of
    # patients.
    source_id: str = attr.ib(validator=_non_empty_string)


@attr.s(auto_attribs=True, frozen=True)
class ExamData(AbstractData):
    """Data about the particular exam"""

    # Name of the scanner hardware manufacturer
    manufacturer: str = attr.ib(validator=attr.validators.instance_of(str))
    # Date and time when the scan was taken
    scan_datetime: Optional[datetime] = attr.ib(validator=_optional_instance_of(datetime))
    # Model of the scanner
    scanner_model: Optional[str] = attr.ib(validator=_optional_instance_of(str))
    # Serial number of the scanner
    scanner_serial_number: Optional[str] = attr.ib(validator=_optional_instance_of(str))
    # Software version of the scanner
    scanner_software_version: Optional[str] = attr.ib(validator=_optional_instance_of(str))
    # Date when the scanner was last calibrated
    scanner_last_calibration_date: Optional[datetime] = attr.ib(validator=_optional_instance_of(datetime))

    # Source ID
    # Identifier which uniquely identifies the exam when combined with the manufacturer, site, and patient IDs.
    #
    # This field is used by the librarian and portable librarian to deduce equality of exams.
    source_id: str = attr.ib(validator=_non_empty_string)


@attr.s(auto_attribs=True, frozen=True)
class SeriesData(AbstractData):
    """Data about the scan itself"""

    # Which eye was scanned. See :class:`Eye`.
    laterality: Laterality = attr.ib(validator=attr.validators.instance_of(Laterality))

    # Fixation of the scan. See :class:`Fixation`
    fixation: Optional[str] = attr.ib(validator=_optional_instance_of(str))

    # Whether the scan is anterior or not
    anterior: Optional[bool] = attr.ib(validator=_optional_instance_of(bool))

    # What types of images are outputted by the machine
    protocol: Optional[str] = attr.ib(validator=_optional_instance_of(str))

    # Source ID
    # Identifier which uniquely identifies the series when combined with the manufacturer, site, and exam IDs.
    # Acceptable values include a globally unique UUID (such as Heidelberg would provide), or an incrementing integer
    # which starts at 1 for each exam.
    #
    # This field is used by the librarian and portable librarian to deduce equality of series.
    source_id: str = attr.ib(validator=_non_empty_string)


@attr.s(auto_attribs=True, frozen=True)
class ContourLine:
    # Code of the current retina/cornea layer.
    layer_name: str = attr.ib(validator=_non_empty_string)

    # The array representing y-coordinates of the layer relative to a b-scan
    data: np.ndarray = json_ignore_ib(eq=False, repr=False)


@attr.s(auto_attribs=True, frozen=True)
class ContourData:
    # Index of the B-Scan to which this contour refers
    bscan_index: int

    # List of contour lines, each annotated with the name of the layer represented by the line
    contour_layers: Sequence[ContourLine]


@attr.s(auto_attribs=True, frozen=True, eq=True)
class ImageOutputParams:
    image_processing_options: ImageProcessingOptions
    image_mode: Optional[str]
    image_transform_functions: List[ImageTransform] = attr.ib(eq=False, repr=False)
    contour: Optional[ContourData] = attr.ib(default=None)


@attr.s(auto_attribs=True, frozen=True, kw_only=True)
class BaseImageDataBytes(ABC):
    image_output_params: List[ImageOutputParams] = attr.ib()

    # The image itself.
    image: Optional[bytes] = json_ignore_ib(eq=False, repr=False)

    # A representation of the storage format of the raw image data in bytes.
    image_byte_format: ImageSourceDataType = attr.ib(default=ImageSourceDataType.UINT8)

    # The pixel width of the image
    width: Optional[int] = attr.ib(default=None)

    # The pixel height of the image
    height: Optional[int] = attr.ib(default=None)

    extras: Optional[Dict] = attr.ib(default=None)

    @image_output_params.validator
    def confirm_image_output_params_lenth(self, attribute: attr.Attribute, value: Any) -> None:
        if len(value) < 1:
            raise ValueError("image_output_params must have atleast one item")


@attr.s(auto_attribs=True, frozen=True, kw_only=True)
class PhotoImageData(BaseImageDataBytes):
    """Data about a specific photo image"""

    # The colour depth of the image in bits.
    colour_depth: int

    # Date and time when the image was taken.
    capture_datetime: Optional[datetime] = attr.ib(validator=_optional_instance_of(datetime))


@attr.s(auto_attribs=True, frozen=True, eq=False)
class HeidelbergImageTransforms:
    affine_transform: Optional[np.ndarray] = attr.ib(validator=_optional_instance_of(np.ndarray))
    intensity_scaling_multiplier: Optional[float] = attr.ib(validator=_optional_instance_of(float))
    intensity_scaling_exponent: Optional[int] = attr.ib(validator=_optional_instance_of(int))


@attr.s(auto_attribs=True, frozen=True)
class TopconImageTransforms:
    lower: int
    higher: int


@attr.s(auto_attribs=True, frozen=True, kw_only=True)
class BScanImageData(BaseImageDataBytes):
    """Data corresponding to a single B-scan of the image"""

    # Quality descriptor of the scan. This may vary between different scan providers.
    quality: Optional[float] = attr.ib(validator=_optional_instance_of(float))

    # ART value - only present for Heidelberg scans
    art_average: Optional[int] = attr.ib(validator=_optional_instance_of(int))

    # Where the B-scan is located on each photos. The index will match in index of the photo.
    photo_locations: List[BscanLocation] = attr.ib(eq=False, repr=False)

    # Date and time when the image was taken.
    capture_datetime: Optional[datetime] = attr.ib(validator=_optional_instance_of(datetime))

    # Data related to transforms on images
    image_transform_metadata: Dict[str, Union[TopconImageTransforms, HeidelbergImageTransforms]] = attr.ib(default={})


# Floating point values in VF files should be truncated to 2dp
# Generic converts are broken in mypy/attrs, so implement this twice
# See https://github.com/python/mypy/issues/8625
def two_dp(x: float) -> float:
    return round(x, 2)


def optional_two_dp(x: Optional[float]) -> Optional[float]:
    if x is None:
        return None
    return round(x, 2)


@attr.s(auto_attribs=True, frozen=True)
class VisualFieldTestPointNormals:
    age_corrected_sensitivity_deviation: Optional[float] = attr.ib(converter=optional_two_dp)
    age_corrected_sensitivity_deviation_probability: Optional[float] = attr.ib(converter=optional_two_dp)
    generalized_defect_corrected_sensitivity_deviation: Optional[float] = attr.ib(converter=optional_two_dp)
    generalized_defect_corrected_sensitivity_deviation_probability: Optional[float] = attr.ib(converter=optional_two_dp)


@attr.s(auto_attribs=True, frozen=True)
class VisualFieldTestPoint:
    x_coord: float = attr.ib(converter=two_dp)
    y_coord: float = attr.ib(converter=two_dp)
    stimulus_results: str
    sensitivity: float = attr.ib(converter=two_dp)
    retest_stimulus_seen: Optional[str]
    retest_sensitivity: Optional[float] = attr.ib(converter=optional_two_dp)
    normals: Optional[VisualFieldTestPointNormals]


@attr.s(auto_attribs=True, frozen=True)
class VisualFieldPatientClinicalInformation:
    rx_ds: float = attr.ib(converter=two_dp)
    rx_dc: float = attr.ib(converter=two_dp)
    rx_axis: float = attr.ib(converter=two_dp)
    pupil_diameter: Optional[float] = attr.ib(converter=optional_two_dp)


@attr.s(auto_attribs=True, frozen=True)
class VisualFieldReliabilityIndex:
    numerator: int
    denominator: int


class VisualFieldStorageType(Enum):
    OPV = OphthalmicVisualFieldStaticPerimetryMeasurementsStorage
    RAW = RawDataStorage
    PDF = EncapsulatedPDFStorage


class GoldmannStimulus(Enum):
    I = "I"  # noqa: E741 - name is not ambiguous in this context
    II = "II"
    III = "III"
    IV = "IV"
    V = "V"
    UNKNOWN = "UNKNOWN"


@attr.s(auto_attribs=True, frozen=True)
class VisualFieldData(AbstractData):
    storage_type: VisualFieldStorageType
    modality: Optional[str]
    source_id: str
    protocol: Optional[str]
    strategy: Optional[str]
    left_eye_patient_clinical_information: Optional[VisualFieldPatientClinicalInformation]
    right_eye_patient_clinical_information: Optional[VisualFieldPatientClinicalInformation]
    fixation_loss: VisualFieldReliabilityIndex
    false_positive_errors: VisualFieldReliabilityIndex
    false_negative_errors: VisualFieldReliabilityIndex
    visual_field_index: Optional[int]
    glaucoma_hemifield_test: Optional[str]
    mean_deviation: Optional[float] = attr.ib(converter=optional_two_dp)
    mean_deviation_significance: Optional[float] = attr.ib(converter=optional_two_dp)
    """
    Where -1 for mean_deviation_significance means "Not Significant".  This is a bit of a hack, it might be better to
    have another way to encode this, but since this is currently only set by the PDF parser and these values are never
    used anywhere, it doesn't seem worth it yet.
    """

    pattern_standard_deviation: Optional[float] = attr.ib(converter=optional_two_dp)
    pattern_standard_deviation_significance: Optional[float] = attr.ib(converter=optional_two_dp)
    test_duration: Optional[float] = attr.ib(converter=optional_two_dp)
    fixation_monitors: List[str]
    stimulus_size: Optional[GoldmannStimulus]
    stimulus_colour: Optional[str]
    background_luminance: Optional[float] = attr.ib(converter=optional_two_dp)
    foveal_sensitivity: Optional[float] = attr.ib(converter=optional_two_dp)
    visual_field_data: List[VisualFieldTestPoint]


ImageContent = Union[PhotoImageData, BScanImageData]


@attr.s(auto_attribs=True)
class ImageData:
    # The type of the image
    modality: ImageModality = attr.ib(validator=attr.validators.instance_of(ImageModality))

    # The group of the image. Identifies related images.
    group_id: Optional[int]

    # The pixel dimensions of the image.
    size: Optional[Size2D]

    # The real-world dimensions of the image in mm
    dimensions_mm: Optional[Union[Size2D, Size3D]]

    # The real-world resolution of the image in mm.
    # For bscans, the height is the distance _between_ bscans. For the width and depth this means the size of a
    # pixel.
    resolutions_mm: Optional[Union[Size2D, Size3D]]

    # The field of view/scan angle of the image in degrees
    field_of_view: Optional[float]

    # Contents of this image
    contents: Sequence[ImageContent] = attr.ib()

    # Source ID
    # Identifier which uniquely identifies the image when combined with the manufacturer, site, and image IDs.
    #
    # This field is used by the librarian and portable librarian to deduce equality of images.
    source_id: str = attr.ib(validator=_non_empty_string)

    # Whether the image is a montage in the sense of section C.8.17.2.1.4 of the DICOM spec
    is_montage: bool = False

    # Fields which don't easily fit into the existing schema, but are nonetheless of interest.  This might include
    # fields which only appear for a single manufacturer, or for a single type of image.
    extras: Dict[str, Any] = attr.ib(factory=dict)

    @property
    def is_colour(self) -> bool:
        return self.modality.is_colour

    @property
    def is_2d(self) -> bool:
        return self.modality.is_2d_image

    @contents.validator
    def _check_image_data_type_consistency(self, attribute: attr.Attribute, value: Any) -> None:
        if len(value) == 0:
            return
        if not len(set(type(image_content) for image_content in value)) == 1:
            raise ValueError("Inconsistent types in image content.")
        content = value[0]
        if isinstance(content, BScanImageData) and (
            isinstance(self.resolutions_mm, Size2D) or isinstance(self.dimensions_mm, Size2D)
        ):
            raise ValueError("2D resolution or size data for OCT image.")
        if isinstance(content, PhotoImageData) and (
            isinstance(self.resolutions_mm, Size3D) or isinstance(self.dimensions_mm, Size3D)
        ):
            raise ValueError("3D resolution or size data for Photo image.")
        if isinstance(content, VisualFieldData) and not (
            self.size is None and self.resolutions_mm is None and self.dimensions_mm is None
        ):
            raise ValueError("Visual fields data must not have geometry data.")

    @contents.validator
    def _check_contour_dimensions_match_image(self, attribute: attr.Attribute, value: Sequence[ImageContent]) -> None:
        if value:
            if isinstance(value[0], BaseImageDataBytes):
                if value[0].image_output_params[0].contour:
                    if self.modality != ImageModality.OCT:
                        raise ValueError("Contour data present in non-OCT image.")
                    ImageData._check_bscan_contour_dimensions_match_image(
                        cast(Size2D, self.size),
                        cast(List[BScanImageData], self.contents),
                    )

    @staticmethod
    def _check_bscan_contour_dimensions_match_image(image_size: Size2D, contents: List[BScanImageData]) -> None:
        bscan_count = len(contents)
        all_contours: List[List[ContourData]] = [[] for _ in contents[0].image_output_params]
        try:
            for bscan in contents:
                for index, processing in enumerate(bscan.image_output_params):
                    if not processing.contour:
                        raise ValueError("Contour is None, whilst another contour is set.")
                    all_contours[index].append(processing.contour)
        except IndexError as error:
            raise ValueError("Different bscans have a different number of processing options") from error
        contour_lengths = {len(contours) for contours in all_contours}
        if len(contour_lengths) > 1:
            raise ValueError("Different number of contours for different image processing options")
        contour_count = list(contour_lengths)[0]

        if contour_count == 0:
            # An empty list just means the OCT file has no contours.
            return
        if contour_count != bscan_count:
            raise ValueError(f"Expected {bscan_count} contour objects, found {contour_count}.")
        for contours in all_contours:
            for index, contour in enumerate(contours):
                layer_names = [layer.layer_name for layer in contour.contour_layers]
                duplicate_layers = {layer for layer, count in Counter(layer_names).items() if count > 1}
                if duplicate_layers:
                    raise ValueError(
                        f"Multiple contours with the same name for b-scan {index} found: {', '.join(duplicate_layers)}"
                    )

                incorrect_width_layers = [
                    layer.layer_name for layer in contour.contour_layers if len(layer.data) != image_size.width
                ]
                if incorrect_width_layers:
                    raise ValueError(
                        f"Layers {', '.join(incorrect_width_layers)} for image {index} "
                        f"have length not matching {image_size.width}"
                    )


@attr.s(auto_attribs=True, frozen=True)
class ImagesData(AbstractData):
    images: List[ImageData] = attr.ib()

    @images.validator
    def _unique_source_ids(self, attribute: attr.Attribute, value: Any) -> None:
        source_ids_seen: Set[str] = set()
        duplicates: Set[str] = set()
        for image in value:
            if image.source_id in source_ids_seen:
                duplicates.add(image.source_id)
            else:
                source_ids_seen.add(image.source_id)
        if len(duplicates) > 0:
            raise ValueError(f"Found duplicate image source IDs: {duplicates}")


@attr.s(auto_attribs=True, frozen=True)
class SeriesResult:
    patient: Optional[PatientData] = None
    exam: Optional[ExamData] = None
    series: Optional[SeriesData] = None
    images: Optional[ImagesData] = None
    visual_field: Optional[VisualFieldData] = None
    debug: Optional[DebugData] = None

    def get(self, section_name: SectionName) -> TImageData:
        return cast(TImageData, getattr(self, section_name.value))


@attr.s(auto_attribs=True, frozen=True)
class ParserResults:
    results: List[SeriesResult]
    is_e2e: bool = False
    parser_version: Tuple[int, int, int] = separated_version
