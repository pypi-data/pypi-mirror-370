"""Types corresponding to output JSON objects from various Altris models."""

from typing import Literal, TypedDict


#######################
# Altris Common Types #
#######################
class _MaskInstanceBase(TypedDict):
    """Shared attributes amongst all MaskInstance types."""

    className: str
    probability: float


class MaskInstancePolygon(_MaskInstanceBase):
    """Represents a single polygonal biomarker instance in the segmentation mask."""

    type: Literal["polygon"]
    points: list[float]


class MaskInstancePolyline(_MaskInstanceBase):
    """Represents a single polyline biomarker instance in the segmentation mask."""

    type: Literal["polyline"]
    points: list[float]


class MaskInstanceEllipse(_MaskInstanceBase):
    """Represents a single elliptical biomarker instance in the segmentation mask."""

    type: Literal["ellipse"]
    cx: float
    cy: float
    rx: float
    ry: float
    angle: float


class MaskInstancePoint(_MaskInstanceBase):
    """Represents a single point biomarker instance in the segmentation mask."""

    type: Literal["point"]


class MaskInstanceOther(_MaskInstanceBase):
    """Represents a single unknown type of biomarker instance in the segmentation mask."""  # noqa: E501

    type: str


MaskInstance = (
    MaskInstancePolygon
    | MaskInstancePolyline
    | MaskInstanceEllipse
    | MaskInstancePoint
    | MaskInstanceOther
)
"""Represents a single biomarker instance in the segmentation mask."""


#########################################
# AltrisConfigurablePathologyModel (v2) #
#########################################
class MaskPathologyV2(TypedDict):
    """Represents the segmentation mask containing biomarker instances.

    For AltrisConfigurablePathologyModel (v2).
    """

    instances: list[MaskInstance]


class ClassesPathologyV2(TypedDict):
    """Classification probabilities for different conditions.

    For AltrisConfigurablePathologyModel (v2).
    """

    dry_amd: float
    geographic_atrophy: float
    epiretinal_fibrosis: float
    wet_amd: float
    choroidal_neovascularization: float
    diabetic_macular_edema: float
    diabetic_retinopathy: float
    macular_degeneration: float


class IndexClassDictBiomarker(TypedDict):
    """Metadata dict for indices of the biomarker types.

    The indices/values for these may be consistent and are provided in the comments
    below.
    """

    hypertransmission: int  #  0
    hard_drusen: int  #  1
    soft_drusen: int  #  2
    confluent_drusen: int  #  3
    diffuse_edema: int  #  4
    is_os_disruption: int  #  5
    epiretinal_fibrosis: int  #  6
    hard_exudates: int  #  7
    intraretinal_cystoid_fluid: int  #  8
    intraretinal_hyperreflective_foci: int  #  9
    neurosensory_retina_atrophy: int  #  10
    reticular_pseudodrusen: int  #  11
    rpe_atrophy: int  #  12
    rpe_disruption: int  #  13
    serous_rpe_detachment: int  #  14
    subretinal_fluid: int  #  15
    subretinal_hyperreflective_material__shrm_: int  #  16
    ellipsoid_zone_loss: int  #  17


class IndexClassDictClass(TypedDict):
    """Metadata dict for indices of the classification types.

    The indices/values for these may be consistent and are provided in the comments
    below.
    """

    dry_amd: int  # 0
    geographic_atrophy: int  # 1
    epiretinal_fibrosis: int  # 2
    wet_amd: int  # 3
    choroidal_neovascularization: int  # 4
    diabetic_macular_edema: int  # 5
    diabetic_retinopathy: int  # 6
    macular_degeneration: int  # 7


class MetadataPathologyV2(TypedDict):
    """Metadata containing image dimensions and class mappings.

    For AltrisConfigurablePathologyModel (v2).
    """

    height: float
    width: float
    index_class_dict_biomarker: IndexClassDictBiomarker
    index_class_dict_class: IndexClassDictClass


class AltrisConfigurablePathologyModelV2Entry(TypedDict):
    """Complete biomarker analysis result for AltrisConfigurablePathologyModel (v2)."""

    mask: MaskPathologyV2
    classes: ClassesPathologyV2
    metadata: MetadataPathologyV2


# Type alias for the complete response (list of results)
AltrisConfigurablePathologyModelV2Output = list[AltrisConfigurablePathologyModelV2Entry]
"""Complete biomarker analysis output for AltrisConfigurablePathologyModel (v2)."""


#############################
# AltrisGASegmentationModel #
#############################
class MetadataSegmentationModel(TypedDict):
    """Metadata containing image dimensions and class mappings.

    For AltrisGASegmentationModel.
    """

    height: int
    width: int


class MaskSegmentationModel(TypedDict):
    """Represents the segmentation mask containing biomarker instances.

    For AltrisGASegmentationModel.
    """

    instances: list[MaskInstance]
    metadata: MetadataSegmentationModel


class AltrisGASegmentationModelEntry(TypedDict):
    """Complete biomarker analysis result for AltrisGASegmentationModel."""

    mask: MaskSegmentationModel
    cnv_probability: float


# Type alias for the complete response (list of results)
AltrisGASegmentationModelPreV11Output = list[list[AltrisGASegmentationModelEntry]]
"""Complete biomarker analysis output for AltrisGASegmentationModel (pre-v11)."""
AltrisGASegmentationModelPostV11Output = list[AltrisGASegmentationModelEntry]
"""Complete biomarker analysis output for AltrisGASegmentationModel (post-v11)."""


##########################################
# FoveaCenterLandmarkDetectionModel (v6) #
##########################################
# A list of 3-element integer lists, representing Fovea landmark coordinates in the
# form (slice, x, y),  e.g. `[[62, 467, 694], [62, 585, 685], ...]`.
FoveaLandmarks = list[list[int]]
"""A list of 3-element integer lists, representing Fovea landmark coordinates.

These have the form (slice, x, y),  e.g. `[[62, 467, 694], [62, 585, 685], ...]`
"""


###################################################################################
# Bitfount Altris JSON Format                                                     #
# ===========================                                                     #
# The format that altris model outputs will be converted to internally within the #
# Bitfount SDK, to make it model version agnostic.                                #
#                                                                                 #
# See `PATHOLOGY_TO_SEGMENTATION_TRANSFORMATION` for more details.                #
###################################################################################
class MaskAltrisBiomarker(TypedDict):
    """Represents the segmentation mask containing biomarker instances.

    For post-PATHOLOGY_TO_SEGMENTATION_TRANSFORMATION conversion.
    """

    instances: list[MaskInstance]
    metadata: MetadataPathologyV2


class ClassesAltrisBiomarker(TypedDict):
    """Classification probabilities for different conditions.

    For post-PATHOLOGY_TO_SEGMENTATION_TRANSFORMATION conversion.
    """

    dry_amd: float
    geographic_atrophy: float
    epiretinal_fibrosis: float
    wet_amd: float
    diabetic_macular_edema: float
    diabetic_retinopathy: float
    macular_degeneration: float


class AltrisBiomarkerEntry(TypedDict):
    """Complete biomarker analysis result for Altris model output.

    For post-PATHOLOGY_TO_SEGMENTATION_TRANSFORMATION conversion.
    """

    mask: MaskAltrisBiomarker
    classes: ClassesAltrisBiomarker
    cnv_probability: float


# Type alias for the complete response (list of results)
AltrisBiomarkerOutput = list[AltrisBiomarkerEntry]
"""Complete biomarker analysis output for Altris model outputs post-PATHOLOGY_TO_SEGMENTATION_TRANSFORMATION conversion."""  # noqa: E501
