"""This module contains the dataclasses and constants used in the Ophthalmology."""

from __future__ import annotations

from collections.abc import Collection
import dataclasses
from dataclasses import dataclass
import logging
import operator
from pathlib import Path
import typing
from typing import Final, Literal, Optional

import desert
from marshmallow import fields
import numpy as np
from numpy.typing import NDArray

from bitfount.data.datasources.utils import (
    LAST_MODIFIED_METADATA_COLUMN,
    ORIGINAL_FILENAME_METADATA_COLUMN,
)
from bitfount.types import UsedForConfigSchemas

_logger = logging.getLogger(__name__)

PartialMatchingType = typing.Literal["any", "all"]

# ===============================================================================
# Clinical criteria constants
# ===============================================================================

# CNV threshold
# TODO: [NO_TICKET: Imported from ophthalmology] This has been chosen arbitrarily
CNV_THRESHOLD: Final = 0.5

# GA area constants
TOTAL_GA_AREA_LOWER_BOUND = 2.5
TOTAL_GA_AREA_UPPER_BOUND = 17.5
LARGEST_GA_LESION_LOWER_BOUND = 1.26
DISTANCE_FROM_FOVEA_LOWER_BOUND = 0.0
DISTANCE_FROM_FOVEA_UPPER_BOUND = float("inf")
EXCLUDE_FOVEAL_GA = False
FOVEA_CENTRE_LANDMARK_INDEX = 2

# Column prefixes corresponding to the "GAMetrics" dictionary keys
TOTAL_GA_AREA_COL_PREFIX: Final = "total_ga_area"
LARGEST_LEGION_SIZE_COL_PREFIX: Final = "largest_lesion_size"
MAX_CNV_PROBABILITY_COL_PREFIX: Final = "max_cnv_probability"

# Columns for GA Metrics
SMALLEST_LEGION_SIZE_COL: Final = "smallest_lesion_size"
NUM_BSCANS_WITH_GA_COL: Final = "num_bscans_with_ga"
NUM_GA_LESIONS_COL: Final = "num_ga_lesions"
DISTANCE_FROM_FOVEA_CENTRE_COL: Final = "distance_from_fovea_centre"
DISTANCE_FROM_IMAGE_CENTRE_COL: Final = "distance_from_image_centre"
FOVEA_DISTANCE_METRIC_COL: Final = "est_fovea_distance"
MAX_GA_BSCAN_INDEX = "max_ga_bscan_index"

# Columns for Fluid Volume Metrics
TOTAL_FLUID_VOLUME_COL: Final = "total_fluid_volume"
SMALLEST_LESION_VOLUME_COL: Final = "smallest_lesion_volume"
LARGEST_LESION_VOLUME_COL: Final = "largest_lesion_volume"
NUM_BSCANS_WITH_FLUID_COL: Final = "num_bscans_with_fluid"
NUM_FLUID_LESIONS_COL: Final = "num_fluid_lesions"
FLUID_DISTANCE_FROM_IMAGE_CENTRE_COL: Final = "distance_from_image_centre"
MAX_FLUID_VOLUME_BSCAN_INDEX: Final = "max_fluid_volume_bscan_index"
CNV_LESION_AREA_COL: Final = "cnv_lesion_area"
# Match from segmentation volumes to columns (via dataframe generation extensions)
SEROUS_RPE_DETACHMENT_COL = "Serous RPE detachment"
INTRARETINAL_CYSTOID_FLUID_COL = "Intraretinal cystoid fluid"
SUBRETINAL_FLUID_COL = "Subretinal fluid"

# ===============================================================================
# DICOM datasource constants
# ===============================================================================


# Note: ensure that any change to the global constants here is also checked
# against the Bitfount-web repo to avoid bugs

# Datasource column names
NAME_COL: Final = "Patient's Name"
DOB_COL: Final = "Patient's Birth Date"
AGE_COL: Final = "Patient's Age"
ACQUISITION_DATE_COL: Final = "Acquisition DateTime"
LATERALITY_COL: Final = "Scan Laterality"

# ================================================================================
# Standard Column Names
# ================================================================================

# Note: ensure that any change to the global constants here is also checked
# against the Bitfount-web repo to avoid bugs
SCAN_DATE_COL: Final = "Scan date"

ICD10_PREFIX: str = "ICD10_"
CPT4_PREFIX: str = "CPT4_"

ICD10_COLUMN: str = "ICD10"
CPT4_COLUMN: str = "CPT4"

# ================================================================================
# EHR Column Names
# ================================================================================

NEXT_APPOINTMENT_COL = "Next Appointment Date"
PREV_APPOINTMENTS_COL = "Previous Appointments Info"
NEW_PATIENT_COL = "New Patient"
GENDER_COL = "Sex"
HOME_NUMBER_COL = "Home Numbers"
CELL_NUMBER_COL = "Cell Numbers"
EMAIL_COL = "Emails"
ADDRESS_COL = "Mailing Address"
MRN_COL = "Medical Record Number (MRN)"
GIVEN_NAME_COL = "Extracted Given Name"
FAMILY_NAME_COL = "Extracted Family Name"
LATEST_PRACTITIONER_NAME_COL = "Latest Practitioner Name"

# ================================================================================
# Eligibility column and value constants
# ================================================================================

# Note: ensure that any change to the global constants here is also checked
# against the Bitfount-web repo to avoid bugs
ELIGIBILITY_COL: Final = "Eligibility"
ELIGIBILE_VALUE: Final = "Eligible"
NON_ELIGIBILE_VALUE: Final = "Not eligible"


# ================================================================================
# Trial name column
# ================================================================================

# Note: ensure that any change to the global constants here is also checked
# against the Bitfount-web repo to avoid bugs
TRIAL_NAME_COL: Final = "Study name"


# ===============================================================================
# Filtering constants
# ===============================================================================
# Note: ensure that any change to the global constants here is also checked
# against the Bitfount-web repo to avoid bugs
FILTER_MATCHING_COLUMN = "Matches all criteria"
FILTER_FAILED_REASON_COLUMN = "Reasons for exclusion"

_FilterOperatorTypes = Literal[
    "equal",
    "==",
    "equals",
    "not equal",
    "!=",
    "less than",
    "<",
    "less than or equal",
    "<=",
    "greater than",
    ">",
    "greater than or equal",
    ">=",
]

_OperatorMapping = {
    "less than": operator.lt,
    "<": operator.lt,
    "less than or equal": operator.le,
    "<=": operator.le,
    "greater than": operator.gt,
    ">": operator.gt,
    "greater than or equal": operator.ge,
    ">=": operator.ge,
    "equal": operator.eq,
    "==": operator.eq,
    "equals": operator.eq,
    "not equal": operator.ne,
    "!=": operator.ne,
}

_OperatorOppositeMapping = {
    operator.lt: ">=",
    operator.le: ">",
    operator.gt: "<=",
    operator.ge: "<",
    operator.eq: "!=",
    operator.ne: "==",
}

# ===============================================================================
# PDF Algorithm constants
# ===============================================================================

DATASOURCE_IMAGE_PREFIX_COLUMNS = "Pixel Data"
RESULTS_SUFFIX = "_prediction"
RESULTS_IMAGE_PREFIX = "Pixel_Data"
NUMBER_OF_FRAMES_COLUMN = "Number of Frames"

# ===============================================================================
# Fovea Algorithm constants
# ===============================================================================

FOVEA_CENTRAL_SLICE_COLUMN = "central_slice"
FOVEA_LANDMARKS_COLUMN = "landmarks"
FOVEA_LANDMARK_LABELS: tuple[str, str, str] = ("start", "end", "middle")

# ===============================================================================
# Segmentation constants
# ===============================================================================


# Mapping of class names to their corresponding label indices. This has been provided
# by the model developers and is used to parse the model predictions.
# Segmentation labels for GA
GA_SEGMENTATION_LABELS: dict[str, int] = {
    "hypertransmission": 0,  # Included in GA
    "rpe_disruption": 1,  # Excluded from GA
    "is_os_disruption": 2,  # Excluded from GA
    "rpe_atrophy": 3,  # Included in GA
    "neurosensory_retina_atrophy": 4,  # Included in GA
}
# Segmentation labels for Fluid Volume
FV_SEGMENTATION_LABELS: dict[str, int] = {
    "serous_rpe_detachment": 0,  # Included in Fluid Volume
    "intraretinal_cystoid_fluid": 1,  # Included in Fluid Volume
    "subretinal_fluid": 2,  # Included in Fluid Volume
}


# TODO: [NO_TICKET: Imported from ophthalmology] Add `is_os_loss` to the segmentation
#       labels once available
GA_INCLUDE_SEGMENTATION_LABELS: list[str] = [
    "hypertransmission",
    "rpe_atrophy",
    "neurosensory_retina_atrophy",
]

GA_EXCLUDE_SEGMENTATION_LABELS: list[str] = [
    "rpe_disruption",
    "is_os_disruption",
]

FLUID_VOLUME_INCLUDE_SEGMENTATION_LABELS: list[str] = [
    "serous_rpe_detachment",
    "intraretinal_cystoid_fluid",
    "subretinal_fluid",
]

LABELS_SEG_FORMATTED: dict[str, str] = {
    "hypertransmission": "Choroidal Hypertransmission",
    "rpe_disruption": "RPE Disruption",
    "is_os_disruption": "EZ Disruption",
    "rpe_atrophy": "RPE Atrophy",
    "neurosensory_retina_atrophy": "Neurosensory Retina Atrophy",
    "diffuse_edema": "Diffuse Edema",
    "serous_rpe_detachment": "Pigment Epithelial Detachment (PED)",
    "intraretinal_cystoid_fluid": "Intraretinal fluid (IRF)",
    "subretinal_fluid": "Subretinal Fluid (SRF)",
    "subretinal_hyperreflective_material__shrm_": (
        "Subretinal Hyperreflective Material (SHRM)"
    ),
}

SEGMENTATION_COLORS: dict[str, tuple[int, int, int]] = {
    "hypertransmission": (255, 126, 203),
    "rpe_disruption": (255, 214, 0),
    "is_os_disruption": (22, 180, 242),
    "rpe_atrophy": (96, 219, 0),
    "neurosensory_retina_atrophy": (225, 106, 255),
    "diffuse_edema": (255, 150, 3),
    "serous_rpe_detachment": (77, 22, 220),
    "intraretinal_cystoid_fluid": (100, 126, 62),
    "subretinal_fluid": (204, 76, 45),
    "subretinal_hyperreflective_material__shrm_": (225, 0, 255),
}
COLOR_NOT_DETECTED: tuple[int, int, int] = (243, 243, 247)

MARKER_NOT_DETECTED_TEXT: str = "No markers detected"

TEXT_TO_IMAGE_RATIO_NO_MARKERS: float = 0.9

_ROOT_DIR = Path(__file__).parent.parent.parent.parent
PATH_FONT_NO_MARKER: str = str(_ROOT_DIR / "assets" / "Inter-Regular.ttf")

# ===============================================================================
# CSV original columns and renamed columns based on datasource type
# ===============================================================================
# Note: ensure that any change to the global constants here is also checked
# against the Bitfount-web repo to avoid bugs
# BITFOUNT Generated Patient ID
_BITFOUNT_PATIENT_ID_KEY: Final = "BitfountPatientID"
_BITFOUNT_PATIENT_ID_RENAMED: Final = "Bitfount patient ID"

# Patient ID column
PATIENT_ID_COL: Final = "Patient ID"

# Constants for the Subfoveal extension
SUBFOVEAL_COL: Final = "Subfoveal lesion?"
DEFAULT_MAX_SUBFOVEAL_DISTANCE: Final = 0.1


# Columns to rename for the CSV files for both types of datasources
DEFAULT_COLUMNS_TO_RENAME = {
    ORIGINAL_FILENAME_METADATA_COLUMN: "File path",
    LAST_MODIFIED_METADATA_COLUMN: "File last modified",
    _BITFOUNT_PATIENT_ID_KEY: _BITFOUNT_PATIENT_ID_RENAMED,
    TOTAL_GA_AREA_COL_PREFIX: "Total GA area (mm2)",
    SMALLEST_LEGION_SIZE_COL: "Smallest lesion size (mm2)",
    LARGEST_LEGION_SIZE_COL_PREFIX: "Largest lesion size (mm2)",
    NUM_BSCANS_WITH_GA_COL: "No. of slices with GA",
    MAX_GA_BSCAN_INDEX: "Slice with largest amount of GA",
    NUM_GA_LESIONS_COL: "No. of GA lesions",
    DISTANCE_FROM_IMAGE_CENTRE_COL: "Distance from image centre (mm)",
    DISTANCE_FROM_FOVEA_CENTRE_COL: "Distance from fovea centre (mm)",
    MAX_CNV_PROBABILITY_COL_PREFIX: "Probability of CNV (%)",
    FILTER_MATCHING_COLUMN: ELIGIBILITY_COL,
}
# Results columns for the CSV files
RESULTS_COLUMNS = [
    TOTAL_GA_AREA_COL_PREFIX,
    MAX_CNV_PROBABILITY_COL_PREFIX,
    SUBFOVEAL_COL,
    _BITFOUNT_PATIENT_ID_KEY,
    DISTANCE_FROM_FOVEA_CENTRE_COL,
    DISTANCE_FROM_IMAGE_CENTRE_COL,
    LARGEST_LEGION_SIZE_COL_PREFIX,
    SMALLEST_LEGION_SIZE_COL,
    NUM_GA_LESIONS_COL,
    NUM_BSCANS_WITH_GA_COL,
    MAX_GA_BSCAN_INDEX,
    "Hypertransmission",
    "RPE disruption",
    "IS/OS disruption",
    "RPE atrophy",
    "Neurosensory retina atrophy",
]

FLUID_COLUMNS_TO_RENAME = {
    ORIGINAL_FILENAME_METADATA_COLUMN: "File path",
    LAST_MODIFIED_METADATA_COLUMN: "File last modified",
    _BITFOUNT_PATIENT_ID_KEY: _BITFOUNT_PATIENT_ID_RENAMED,
    MAX_CNV_PROBABILITY_COL_PREFIX: "Probability of CNV (%)",
    TOTAL_FLUID_VOLUME_COL: "Total fluid volume (nL)",
    FLUID_DISTANCE_FROM_IMAGE_CENTRE_COL: "Distance from image centre (mm)",
    LARGEST_LESION_VOLUME_COL: "Largest lesion volume (nL)",
    SMALLEST_LESION_VOLUME_COL: "Smallest lesion volume (nL)",
    NUM_FLUID_LESIONS_COL: "No. of fluid lesions",
    NUM_BSCANS_WITH_FLUID_COL: "No. of slices with fluid",
    MAX_FLUID_VOLUME_BSCAN_INDEX: "Slice with largest amount of fluid",
}

FLUID_RESULTS_COLUMNS = [
    TOTAL_FLUID_VOLUME_COL,
    MAX_CNV_PROBABILITY_COL_PREFIX,
    _BITFOUNT_PATIENT_ID_KEY,
    FLUID_DISTANCE_FROM_IMAGE_CENTRE_COL,
    LARGEST_LESION_VOLUME_COL,
    SMALLEST_LESION_VOLUME_COL,
    NUM_FLUID_LESIONS_COL,
    NUM_BSCANS_WITH_FLUID_COL,
    MAX_FLUID_VOLUME_BSCAN_INDEX,
    SEROUS_RPE_DETACHMENT_COL,
    INTRARETINAL_CYSTOID_FLUID_COL,
    SUBRETINAL_FLUID_COL,
]

# DICOMOphthalmology specific columns
DICOM_COLUMNS_TO_RENAME = {
    "Patient's Name": "Name",
    "Patient's Sex": "Sex",
    "Patient's Birth Date": "DOB",
    "Number of Frames": "No. of slices",
    ACQUISITION_DATE_COL: SCAN_DATE_COL,
    "Acquisition Device Type": "Device type",
    "Study Date": "Study date",
    "Study Time": "Study time",
    "Scan Laterality": "Laterality",
}

ORIGINAL_DICOM_COLUMNS = [
    TRIAL_NAME_COL,
    PATIENT_ID_COL,
    FILTER_MATCHING_COLUMN,
    FILTER_FAILED_REASON_COLUMN,
    "Patient's Name",
    "Patient's Sex",
    "Patient's Birth Date",
    "Scan Laterality",
    ACQUISITION_DATE_COL,
    *RESULTS_COLUMNS,
    "Number of Frames",
    "Referring Physician's Name",
    "Study Date",
    "Study Time",
    "Modality",
    "Manufacturer",
    "Acquisition Device Type",
    ORIGINAL_FILENAME_METADATA_COLUMN,
    LAST_MODIFIED_METADATA_COLUMN,
]

# Heidelberg specific columns
HEIDELBERG_COLUMNS_TO_RENAME = {
    "Patient's Name": "Name",
    "Patient's Sex": "Sex",
    "Patient's Birth Date": "DOB",
    "Number of Frames": "No. of slices",
    ACQUISITION_DATE_COL: SCAN_DATE_COL,
    "manufacturer": "Manufacturer",
    "Scan Laterality": "Laterality",
}
ORIGINAL_HEIDELBERG_COLUMNS = [
    "Study name",
    PATIENT_ID_COL,
    FILTER_MATCHING_COLUMN,
    FILTER_FAILED_REASON_COLUMN,
    "Patient's Name",
    "Patient's Birth Date",
    "Patient's Sex",
    "Scan Laterality",
    ACQUISITION_DATE_COL,
    *RESULTS_COLUMNS,
    "Number of Frames",
    "manufacturer",
    ORIGINAL_FILENAME_METADATA_COLUMN,
    LAST_MODIFIED_METADATA_COLUMN,
]

DEFAULT_AUX_COLS: Final[list[str]] = []


def max_pathology_prob_col_name(pathology_name: str) -> str:
    """Generate the max probability column name for a given pathology."""
    return f"max_{pathology_name}_probability"


@dataclass
class SLOSegmentationLocationPrefix(UsedForConfigSchemas):
    """Dataclass for location columns prefixes for the OCT images on the SLO.

    Args:
        start_x_image: Column name prefix where the start x-axis pixel location
            of the first OCT image is on SLO. Defaults to `loc_start_x_image_`.
        start_y_image: Column name prefix where the start y-axis pixel location
            of the first OCT image is on SLO. Defaults to `loc_start_y_image_`.
        end_x_image: Column name prefix where the end x-axis pixel location
            of the first OCT image is on SLO. Defaults to `loc_end_x_image_`.
        end_y_image: Column name prefix where the end y-axis pixel location
            of the first OCT image is on SLO. Defaults to `loc_end_y_image_`.
    """

    start_x_image: str = "loc_start_x_image_"
    start_y_image: str = "loc_start_y_image_"
    end_x_image: str = "loc_end_x_image_"
    end_y_image: str = "loc_end_y_image_"


@dataclass
class SLOImageMetadataColumns(UsedForConfigSchemas):
    """Dataclass for storing columns related to the SLO dimensions.

    Args:
        height_mm_column: The name of the column for where the
            height in mm of the SLO image. Defaults to `slo_dimensions_mm_height`.
        width_mm_column: The name of the column for where the
            width in mm of the SLO image. Defaults to `slo_dimensions_mm_width`.
    """

    height_mm_column: str = "slo_dimensions_mm_height"
    width_mm_column: str = "slo_dimensions_mm_width"


@dataclass
class OCTImageMetadataColumns(UsedForConfigSchemas):
    """Dataclass for storing columns related to the OCT dimensions.

    Args:
        height_mm_column: The name of the column for where the
            height in mm of the OCT image. Defaults to `dimensions_mm_height`.
        width_mm_column: The name of the column for where the
            width in mm of the OCT image. Defaults to `dimensions_mm_width`.
        depth_mm_column: The name of the column for where the
            depth in mm of the OCT image. Defaults to `dimensions_mm_depth`.
    """

    height_mm_column: str = "dimensions_mm_height"
    width_mm_column: str = "dimensions_mm_width"
    depth_mm_column: str = "dimensions_mm_depth"


@dataclass
class TextFieldType:
    """Stores information for a text field.

    Attrs:
        heading: The heading for the text field.
        column: The column name for the text field from the datasource.
        value: The value for the text field. This should be a
            hardcoded value that will appear in all pdf reports.

    """

    heading: str
    column: Optional[str] = None
    value: Optional[str] = None
    datetime_format: Optional[str] = None

    def __post_init__(self) -> None:
        if self.value is None and self.column is None:
            raise AttributeError(
                "Either value of the field or the column name is required."
            )


@dataclass
class ImageFieldType:
    """Stores information for an image field.

    Attrs:
        column: The column name where the image is in the datasource
    """

    column: str


@dataclass
class ReportMetadata(UsedForConfigSchemas):
    """Dataclass for storing pdf report metadata fields.

    Attrs:
        text_fields: The text fields for the top table of the report.
        heading: The heading for the report. Defaults to None.
        image_field: The image field for the top table of the report.
            Defaults to None.
    """

    text_fields: list[TextFieldType] = desert.field(
        fields.Nested(desert.schema_class(TextFieldType), many=True)
    )
    heading: Optional[str] = None
    image_field: Optional[ImageFieldType] = desert.field(
        fields.Nested(desert.schema_class(ImageFieldType), allow_none=True),
        default=None,
    )


@dataclass(kw_only=True)
class GAMetrics:
    """Output of the GA calculation algorithm.

    Attributes:
        total_ga_area: Total area of GA in the image in mm^2.
        smallest_lesion_size: Size of the smallest lesion in the image in mm^2.
        largest_lesion_size: Size of the largest lesion in the image in mm^2.
        num_bscans_with_ga: Number of B-scans with GA in the image.
        num_ga_lesions: Number of GA lesions in the image.
        distance_from_image_centre: Distance from the image centre to the nearest
            lesion in mm. Image centre is used as a proxy for the fovea.
        max_cnv_probability: Maximum probability of CNV across all B-scans in the
            image. This value will be between 0 and 1.
        max_ga_bscan_index: Index of the B-scan with the largest GA lesion if there is
            GA, otherwise None.
        segmentation_areas: A dictionary containing the area of each segmentation
            class in the image in mm^2.
    """

    total_ga_area: float
    smallest_lesion_size: float
    largest_lesion_size: float
    num_bscans_with_ga: int
    num_ga_lesions: int
    distance_from_image_centre: float
    max_cnv_probability: float
    max_ga_bscan_index: Optional[int]
    segmentation_areas: dict[str, float]
    max_pathology_probabilities: dict[str, float]

    def to_record(
        self, additional_pathology_prob_cols: Optional[Collection[str]] = None
    ) -> dict[str, typing.Any]:
        """Convert to a record format compatible with pd.DataFrame.from_records().

        By default this will be all fields in the dataclass, except for
        `max_pathology_probabilities`. If additional record entries containing these
        pathology probabilities are wanted, supply arguments via
        `additional_pathology_prob_cols` which match the pathology name. This will
        create additional record entries called "max_[pathology_name]_probability"
        for each one requested.
        """
        d = dataclasses.asdict(self)
        d.pop("max_pathology_probabilities", None)

        if additional_pathology_prob_cols is not None:
            for pathology_name in additional_pathology_prob_cols:
                try:
                    max_prob = self.max_pathology_probabilities[pathology_name]
                except KeyError:
                    _logger.warning(
                        f'Could not find requested pathology "{pathology_name}"'
                        f" in the pathology probabilities."
                    )
                    d[max_pathology_prob_col_name(pathology_name)] = 0.0
                else:
                    d[max_pathology_prob_col_name(pathology_name)] = max_prob

        return d

    @classmethod
    def expected_cols(cls) -> list[str]:
        """Returns the expected columns that should be created for a dataframe.

        For dataframes constructed from this class, there should be a set of expected,
        core columns.
        """
        return [
            f.name
            for f in dataclasses.fields(cls)
            # This field is explicitly excluded as `additional_pathology_prob_cols` is
            # used to control elements in this field being pulled into columns
            if f.name != "max_pathology_probabilities"
        ]


@dataclass(kw_only=True)
class GAMetricsWithFovea(GAMetrics):
    """Output of the GA calculation algorithm with fovea detection.

    Attributes:
        distance_from_fovea_centre: Distance from the fovea to the nearest
            lesion in mm where applicable and possible to calcualte.
        fovea_centre: Coordinates of the fovea centre in the image if detected.
            Coordinates are in the form (slice, x, y).
        est_fovea_distance: The final distance metric used for trial inclusion.
            If fovea distance is not available,
            this will be the distance from the image centre.
    """

    distance_from_fovea_centre: Optional[float]
    fovea_centre: Optional[tuple[int, int, int]]
    fovea_landmarks: list[tuple[int, int, int]]
    est_fovea_distance: float
    distance_metric_type: str
    subfoveal_indicator: Optional[str]


@dataclass
class TrialNotesCSVArgs:
    """Dataclass for storing the arguments for the trial notes CSV.

    Args:
       columns_for_csv: The columns to include in the trial notes CSV.
       columns_from_data: The columns to include from the data.
            Defaults to None.
       columns_to_populate_with_static_values: The columns to populate
            with static values. Defaults to None
    """

    columns_for_csv: list[str] = desert.field(fields.List(fields.String()))
    columns_from_data: Optional[dict[str, str]] = desert.field(
        fields.Dict(keys=fields.String(), values=fields.String()), default=None
    )
    columns_to_populate_with_static_values: Optional[dict[str, str]] = desert.field(
        fields.Dict(keys=fields.String(), values=fields.String()), default=None
    )
    eligible_only: bool = True


@dataclass
class ParsedBScanPredictions:
    """Container for the various outputs of parsing bscan predictions.

    Attributes:
        column_masks: Numpy array mask of shape (num_bscans, num_cols) where
            num_bscans is the number of B-scans in the array and num_cols is the number
            of columns in each B-scan.
        class_probabilities: A mapping of class name (e.g. "cnv", "hard_drusen") to a
            numpy array of probabilities for that pathology for each B-scan.
        class_areas: A mapping of class name (e.g. "cnv", "hard_drusen") to a list of
            area (in mm^2) of that pathology on each B-scan. e.g.:
            ```
            {
                segmentation_class_name: [
                    area_in_mm2_in_bscan_0,
                    area_in_mm2_in_bscan_1,
                    ...,
                ]
            }
            ```
    """

    column_masks: NDArray[np.floating]
    class_probabilities: dict[str, NDArray[np.floating]]
    class_areas: dict[str, list[float]]


@dataclass(kw_only=True)
class FluidVolumeMetrics:
    """Output of the Fluid Volume calculation algorithm.

    Attributes:
        total_fluid_volume: Total volume of fluid in the image in mm^3.
        smallest_lesion_volume: Volume of the smallest fluid lesion in mm^3.
        largest_lesion_volume: Volume of the largest fluid lesion in mm^3.
        num_bscans_with_fluid: Number of B-scans with fluid in the image.
        num_fluid_lesions: Number of fluid lesions in the image.
        distance_from_image_centre: Distance from the image centre to the nearest
            fluid lesion in mm.
        max_fluid_volume_bscan_index: Index of the B-scan with the largest fluid
            volume if present, otherwise None.
        segmentation_volumes: A dictionary containing the volume of each fluid
            segmentation class in mm^3.
    """

    total_fluid_volume: float
    smallest_lesion_volume: float
    largest_lesion_volume: float
    num_bscans_with_fluid: int
    num_fluid_lesions: int
    distance_from_image_centre: float
    max_cnv_probability: float
    max_fluid_volume_bscan_index: Optional[int]
    segmentation_volumes: dict[str, float]

    def to_record(self) -> dict[str, typing.Any]:
        """Convert to a record format compatible with pd.DataFrame.from_records()."""

        return dataclasses.asdict(self)

    @classmethod
    def expected_cols(cls) -> list[str]:
        """Returns the expected columns that should be created for a dataframe.

        For dataframes constructed from this class, there should be a set of expected,
        core columns.
        """
        return [
            f.name
            for f in dataclasses.fields(cls)
            # This field is explicitly excluded as `additional_pathology_prob_cols` is
            # used to control elements in this field being pulled into columns
            if f.name != "max_pathology_probabilities"
        ]
