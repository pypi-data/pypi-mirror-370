"""Config YAML specification classes related to algorithms."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
import typing
from typing import Any, Optional, Sequence, Union

import desert
from marshmallow import ValidationError, fields, validate
from marshmallow.validate import OneOf
import marshmallow_enum
from marshmallow_union import Union as M_Union

from bitfount.externals.ehr.nextgen.api import NextGenEnterpriseAPI, NextGenFHIRAPI
from bitfount.federated.algorithms.filtering_algorithm import FilterStrategy
from bitfount.federated.algorithms.hugging_face_algorithms.hugging_face_perplexity import (  # noqa: E501
    DEFAULT_STRIDE,
)
from bitfount.federated.algorithms.hugging_face_algorithms.utils import (
    DEFAULT_MAX_LENGTH,
    DEFAULT_MIN_NEW_TOKENS,
    DEFAULT_NUM_BEAMS,
    DEFAULT_NUM_RETURN_SEQUENCES,
    DEFAULT_REPETITION_PENALTY,
    TIMMTrainingConfig,
)
from bitfount.federated.algorithms.ophthalmology import (
    bscan_image_and_mask_generation_algorithm as bscan_mod,
)
from bitfount.federated.algorithms.ophthalmology.csv_report_generation_ophth_algorithm import (  # noqa: E501
    DFSortType,
    MatchPatientVisit,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    CNV_THRESHOLD,
    DISTANCE_FROM_FOVEA_LOWER_BOUND,
    DISTANCE_FROM_FOVEA_UPPER_BOUND,
    EXCLUDE_FOVEAL_GA,
    LARGEST_GA_LESION_LOWER_BOUND,
    TOTAL_GA_AREA_LOWER_BOUND,
    TOTAL_GA_AREA_UPPER_BOUND,
    OCTImageMetadataColumns,
    ReportMetadata,
    SLOImageMetadataColumns,
    SLOSegmentationLocationPrefix,
)
from bitfount.federated.algorithms.ophthalmology.trial_inclusion_filters import (
    ColumnFilter,
)
from bitfount.federated.types import AlgorithmType
from bitfount.runners.config_schemas.common_schemas import FilePath
from bitfount.runners.config_schemas.model_schemas import ModelConfig
from bitfount.runners.utils import get_concrete_config_subclasses
from bitfount.types import _JSONDict
from bitfount.utils import DEFAULT_SEED

_logger = logging.getLogger(__name__)


@dataclass
class AggregatorConfig:
    """Configuration for the Aggregator."""

    secure: bool
    weights: Optional[dict[str, Union[int, float]]] = None

    def __post_init__(self) -> None:
        if self.secure and self.weights:
            # TODO: [BIT-1486] Remove this constraint
            raise NotImplementedError(
                "SecureAggregation does not support update weighting"
            )


@dataclass
class AlgorithmConfig:
    """Configuration for the Algorithm."""

    name: str
    arguments: Optional[Any] = None

    @classmethod
    def _get_subclasses(cls) -> tuple[type[AlgorithmConfig], ...]:
        """Get all the concrete subclasses of this config class."""
        return get_concrete_config_subclasses(cls)


@dataclass
class ModelAlgorithmConfig(AlgorithmConfig):
    """Configuration for the Model algorithms."""

    __config_type: typing.ClassVar[str] = "intermediate"

    model: Optional[ModelConfig] = None
    pretrained_file: Optional[Path] = desert.field(
        FilePath(allow_none=True), default=None
    )


@dataclass
class FederatedModelTrainingArgumentsConfig:
    """Configuration for the FederatedModelTraining algorithm arguments."""

    modeller_checkpointing: bool = True
    checkpoint_filename: Optional[str] = None


@dataclass
class FederatedModelTrainingAlgorithmConfig(ModelAlgorithmConfig):
    """Configuration for the FederatedModelTraining algorithm."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(AlgorithmType.FederatedModelTraining.value)
        )
    )
    arguments: Optional[FederatedModelTrainingArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(FederatedModelTrainingArgumentsConfig)),
        default=FederatedModelTrainingArgumentsConfig(),
    )


@dataclass
class ModelTrainingAndEvaluationArgumentsConfig:
    """Configuration for the ModelTrainingAndEvaluation algorithm arguments."""

    # Currently there are no arguments


@dataclass
class ModelTrainingAndEvaluationAlgorithmConfig(ModelAlgorithmConfig):
    """Configuration for the ModelTrainingAndEvaluation algorithm."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(AlgorithmType.ModelTrainingAndEvaluation.value)
        )
    )
    arguments: Optional[ModelTrainingAndEvaluationArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(ModelTrainingAndEvaluationArgumentsConfig))
    )


@dataclass
class ModelEvaluationArgumentsConfig:
    """Configuration for the ModelEvaluation algorithm arguments."""

    # Currently there are no arguments


@dataclass
class ModelEvaluationAlgorithmConfig(ModelAlgorithmConfig):
    """Configuration for the ModelEvaluation algorithm."""

    name: str = desert.field(
        fields.String(validate=validate.Equal(AlgorithmType.ModelEvaluation.value))
    )
    arguments: Optional[ModelEvaluationArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(ModelEvaluationArgumentsConfig))
    )


@dataclass
class ModelInferenceArgumentsConfig:
    """Configuration for the ModelInference algorithm arguments."""

    class_outputs: Optional[list[str]] = None
    postprocessors: Optional[list[dict[str, str]]] = None


@dataclass
class ModelInferenceAlgorithmConfig(ModelAlgorithmConfig):
    """Configuration for the ModelInference algorithm."""

    name: str = desert.field(
        fields.String(validate=validate.Equal(AlgorithmType.ModelInference.value))
    )
    arguments: ModelInferenceArgumentsConfig = desert.field(
        fields.Nested(desert.schema_class(ModelInferenceArgumentsConfig)),
        default=ModelInferenceArgumentsConfig(),
    )


@dataclass
class SqlQueryArgumentsConfig:
    """Configuration for the SqlQuery algorithm arguments."""

    query: str
    table: Optional[str] = None


@dataclass
class SqlQueryAlgorithmConfig(AlgorithmConfig):
    """Configuration for the SqlQuery algorithm."""

    name: str = desert.field(
        fields.String(validate=validate.Equal(AlgorithmType.SqlQuery.value))
    )
    arguments: SqlQueryArgumentsConfig = desert.field(
        fields.Nested(desert.schema_class(SqlQueryArgumentsConfig))
    )


@dataclass
class PrivateSqlQueryColumnArgumentsConfig:
    """Configuration for the PrivateSqlQuery algorithm column arguments."""

    lower: Optional[int] = None
    upper: Optional[int] = None


PrivateSqlQueryColumnArgumentsConfigSchema = desert.schema_class(
    PrivateSqlQueryColumnArgumentsConfig
)


@dataclass
class PrivateSqlQueryArgumentsConfig:
    """Configuration for the PrivateSqlQuery algorithm arguments."""

    query: str
    epsilon: float
    delta: float
    column_ranges: Union[
        dict[str, PrivateSqlQueryColumnArgumentsConfig],
        dict[str, dict[str, PrivateSqlQueryColumnArgumentsConfig]],
    ] = desert.field(
        M_Union(
            [
                fields.Dict(
                    keys=fields.String(),
                    values=fields.Nested(
                        PrivateSqlQueryColumnArgumentsConfigSchema,
                    ),
                ),
                fields.Dict(
                    keys=fields.String(),
                    values=fields.Dict(
                        keys=fields.String(),
                        values=fields.Nested(
                            PrivateSqlQueryColumnArgumentsConfigSchema,
                        ),
                    ),
                ),
            ]
        )
    )
    table: Optional[str] = None
    db_schema: Optional[str] = None


@dataclass
class PrivateSqlQueryAlgorithmConfig(AlgorithmConfig):
    """Configuration for the PrivateSqlQuery algorithm."""

    name: str = desert.field(
        fields.String(validate=validate.Equal(AlgorithmType.PrivateSqlQuery.value))
    )
    arguments: PrivateSqlQueryArgumentsConfig = desert.field(
        fields.Nested(desert.schema_class(PrivateSqlQueryArgumentsConfig))
    )


@dataclass
class HuggingFacePerplexityEvaluationArgumentsConfig:
    """Configuration for the HuggingFacePerplexityEvaluation algorithm arguments."""

    model_id: str
    stride: int = DEFAULT_STRIDE
    seed: int = DEFAULT_SEED


@dataclass
class HuggingFacePerplexityEvaluationAlgorithmConfig(AlgorithmConfig):
    """Configuration for the HuggingFacePerplexityEvaluation algorithm."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(AlgorithmType.HuggingFacePerplexityEvaluation.value)
        )
    )

    arguments: Optional[HuggingFacePerplexityEvaluationArgumentsConfig] = desert.field(
        fields.Nested(
            desert.schema_class(HuggingFacePerplexityEvaluationArgumentsConfig)
        )
    )


@dataclass
class HuggingFaceTextGenerationInferenceArgumentsConfig:
    """Configuration for the HuggingFaceTextGenerationInference algorithm arguments."""

    model_id: str
    prompt_format: Optional[str] = None
    max_length: int = DEFAULT_MAX_LENGTH
    num_return_sequences: int = DEFAULT_NUM_RETURN_SEQUENCES
    seed: int = DEFAULT_SEED
    min_new_tokens: int = DEFAULT_MIN_NEW_TOKENS
    repetition_penalty: float = DEFAULT_REPETITION_PENALTY
    num_beams: int = DEFAULT_NUM_BEAMS
    early_stopping: bool = True
    pad_token_id: Optional[int] = None
    eos_token_id: Optional[int] = None
    device: Optional[str] = None
    torch_dtype: str = "float32"

    def __post_init__(self) -> None:
        if self.torch_dtype not in ("bfloat16", "float16", "float32", "float64"):
            raise ValueError(
                f"Invalid torch_dtype {self.torch_dtype}. Must be one of "
                "'bfloat16', 'float16', 'float32', 'float64'."
            )


@dataclass
class HuggingFaceTextGenerationInferenceAlgorithmConfig(AlgorithmConfig):
    """Configuration for the HuggingFaceTextGenerationInference algorithm."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(
                AlgorithmType.HuggingFaceTextGenerationInference.value
            )
        )
    )

    arguments: Optional[HuggingFaceTextGenerationInferenceArgumentsConfig] = (
        desert.field(
            fields.Nested(
                desert.schema_class(HuggingFaceTextGenerationInferenceArgumentsConfig)
            )
        )
    )


@dataclass
class CSVReportAlgorithmArgumentsConfig:
    """Configuration for CSVReportAlgorithm arguments."""

    save_path: Optional[Path] = desert.field(FilePath(allow_none=True), default=None)
    original_cols: Optional[list[str]] = None
    filter: Optional[list[ColumnFilter]] = desert.field(
        fields.Nested(desert.schema_class(ColumnFilter), many=True, allow_none=True),
        default=None,
    )


@dataclass
class CSVReportAlgorithmConfig(AlgorithmConfig):
    """Configuration for CSVReportAlgorithm."""

    name: str = desert.field(
        fields.String(validate=validate.Equal(AlgorithmType.CSVReportAlgorithm.value))
    )
    arguments: Optional[CSVReportAlgorithmArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(CSVReportAlgorithmArgumentsConfig)),
        default=CSVReportAlgorithmArgumentsConfig(),
    )


@dataclass
class HuggingFaceImageClassificationInferenceArgumentsConfig:
    """Configuration for HuggingFaceImageClassificationInference arguments."""

    model_id: str
    apply_softmax_to_predictions: bool = True
    batch_size: int = 1
    seed: int = DEFAULT_SEED
    top_k: int = 5


@dataclass
class HuggingFaceImageClassificationInferenceAlgorithmConfig(AlgorithmConfig):
    """Configuration for HuggingFaceImageClassificationInference."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(
                AlgorithmType.HuggingFaceImageClassificationInference.value
            )
        )
    )
    arguments: Optional[HuggingFaceImageClassificationInferenceArgumentsConfig] = (
        desert.field(
            fields.Nested(
                desert.schema_class(
                    HuggingFaceImageClassificationInferenceArgumentsConfig
                )
            ),
        )
    )


@dataclass
class HuggingFaceImageSegmentationInferenceArgumentsConfig:
    """Configuration for HuggingFaceImageSegmentationInference arguments."""

    model_id: str
    alpha: float = 0.3
    batch_size: int = 1
    dataframe_output: bool = False
    mask_threshold: float = 0.5
    overlap_mask_area_threshold: float = 0.5
    seed: int = DEFAULT_SEED
    save_path: Optional[str] = None
    subtask: Optional[str] = None
    threshold: float = 0.9


@dataclass
class HuggingFaceImageSegmentationInferenceAlgorithmConfig(AlgorithmConfig):
    """Configuration for HuggingFaceImageSegmentationInference."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(
                AlgorithmType.HuggingFaceImageSegmentationInference.value
            )
        )
    )
    arguments: Optional[HuggingFaceImageSegmentationInferenceArgumentsConfig] = (
        desert.field(
            fields.Nested(
                desert.schema_class(
                    HuggingFaceImageSegmentationInferenceArgumentsConfig
                )
            ),
        )
    )


@dataclass
class HuggingFaceTextClassificationInferenceArgumentsConfig:
    """Configuration for HuggingFaceTextClassificationInference arguments."""

    model_id: str
    batch_size: int = 1
    function_to_apply: Optional[str] = None
    seed: int = DEFAULT_SEED
    top_k: int = 5


@dataclass
class HuggingFaceTextClassificationInferenceAlgorithmConfig(AlgorithmConfig):
    """Configuration for HuggingFaceTextClassificationInference."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(
                AlgorithmType.HuggingFaceTextClassificationInference.value
            )
        )
    )
    arguments: Optional[HuggingFaceTextClassificationInferenceArgumentsConfig] = (
        desert.field(
            fields.Nested(
                desert.schema_class(
                    HuggingFaceTextClassificationInferenceArgumentsConfig
                )
            ),
        )
    )


@dataclass
class TIMMFineTuningArgumentsConfig:
    """Configuration for TIMMFineTuning algorithm arguments."""

    model_id: str
    args: Optional[TIMMTrainingConfig] = desert.field(
        fields.Nested(desert.schema_class(TIMMTrainingConfig), allow_none=True),
        default=None,
    )
    batch_transformations: Optional[dict[str, list[Union[str, _JSONDict]]]] = (
        desert.field(
            fields.Dict(
                keys=fields.Str(validate=OneOf(["train", "validation"])),
            ),
            default=None,
        )
    )
    labels: Optional[list[str]] = None
    return_weights: bool = False
    save_path: Optional[Path] = desert.field(FilePath(allow_none=True), default=None)


@dataclass
class TIMMFineTuningAlgorithmConfig(AlgorithmConfig):
    """Configuration for TIMMFineTuning algorithm."""

    name: str = desert.field(
        fields.String(validate=validate.Equal(AlgorithmType.TIMMFineTuning.value))
    )
    arguments: Optional[TIMMFineTuningArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(TIMMFineTuningArgumentsConfig)),
    )


@dataclass
class TIMMInferenceArgumentsConfig:
    """Configuration for TIMMInference algorithm arguments."""

    model_id: str
    num_classes: Optional[int] = None
    checkpoint_path: Optional[Path] = desert.field(
        FilePath(allow_none=True), default=None
    )
    class_outputs: Optional[list[str]] = None
    batch_transformations: Optional[list[Union[str, _JSONDict]]] = desert.field(
        fields.List(M_Union([fields.String(), fields.Dict()]), allow_none=True),
        default=None,
    )


@dataclass
class TIMMInferenceAlgorithmConfig(AlgorithmConfig):
    """Configuration for TIMMInference algorithm."""

    name: str = desert.field(
        fields.String(validate=validate.Equal(AlgorithmType.TIMMInference.value))
    )
    arguments: Optional[TIMMInferenceArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(TIMMInferenceArgumentsConfig)),
    )


@dataclass
class EHRPatientQueryArgumentsConfig:
    """Configuration for EHRPatientQuery algorithm arguments."""

    querier_type: str
    fhir_url: str = NextGenFHIRAPI.DEFAULT_NEXT_GEN_FHIR_URL
    enterprise_url: str = NextGenEnterpriseAPI.DEFAULT_NEXT_GEN_ENTERPRISE_URL
    smart_on_fhir_url: Optional[str] = None
    smart_on_fhir_resource_server_url: Optional[str] = None


@dataclass
class EHRPatientQueryAlgorithmConfig(AlgorithmConfig):
    """Configuration for EHRPatientQuery algorithm."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(AlgorithmType.EHRPatientQueryAlgorithm.value)
        )
    )
    arguments: EHRPatientQueryArgumentsConfig = desert.field(
        fields.Nested(desert.schema_class(EHRPatientQueryArgumentsConfig)),
    )


@dataclass
class NextGenPatientInfoDownloadArgumentsConfig:
    """Configuration for NextGenPatientInfoDownloadAlgorithm arguments."""

    fhir_url: str = NextGenFHIRAPI.DEFAULT_NEXT_GEN_FHIR_URL
    enterprise_url: str = NextGenEnterpriseAPI.DEFAULT_NEXT_GEN_ENTERPRISE_URL
    smart_on_fhir_url: Optional[str] = None
    smart_on_fhir_resource_server_url: Optional[str] = None


@dataclass
class NextGenPatientInfoDownloadAlgorithmConfig(AlgorithmConfig):
    """Configuration for NextGenPatientInfoDownloadAlgorithm."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(
                AlgorithmType.NextGenPatientInfoDownloadAlgorithm.value
            )
        )
    )
    arguments: Optional[NextGenPatientInfoDownloadArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(NextGenPatientInfoDownloadArgumentsConfig)),
        default=NextGenPatientInfoDownloadArgumentsConfig(),
    )


@dataclass
class RecordFilterAlgorithmArgumentsConfig:
    """Configuration for RecordFilter algorithm arguments."""

    strategies: Sequence[Union[FilterStrategy, str]]
    filter_args_list: list[dict[str, Any]]


@dataclass
class RecordFilterAlgorithmConfig(AlgorithmConfig):
    """Configuration for RecordFilter algorithm."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(AlgorithmType.RecordFilterAlgorithm.value)
        )
    )
    arguments: Optional[RecordFilterAlgorithmArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(RecordFilterAlgorithmArgumentsConfig))
    )


@dataclass
class GenericAlgorithmConfig(AlgorithmConfig):
    """Configuration for unspecified algorithm plugins.

    Raises:
        ValueError: if the algorithm name starts with `bitfount.`
    """

    __config_type: typing.ClassVar[str] = "fallback"

    name: str
    arguments: _JSONDict = desert.field(
        fields.Dict(keys=fields.Str), default_factory=dict
    )

    def __post_init__(self) -> None:
        _logger.warning(
            f"Algorithm configuration was parsed as {self.__class__.__name__};"
            f" was this intended?"
        )

        if self.name.startswith("bitfount."):
            _logger.error(
                f"Unexpected algorithm config; was parsed as GenericAlgorithm:\n{self}"
            )
            raise ValidationError(
                "Algorithm names starting with 'bitfount.' are reserved for built-in "
                "algorithms. It is likely the provided arguments don't match the "
                "expected schema for the algorithm. Please check the documentation "
            )


#############################################################################
#  _____       _     _   _           _                 _                    #
# |  _  |     | |   | | | |         | |               | |                   #
# | | | |_ __ | |__ | |_| |__   __ _| |_ __ ___   ___ | | ___   __ _ _   _  #
# | | | | '_ \| '_ \| __| '_ \ / _` | | '_ ` _ \ / _ \| |/ _ \ / _` | | | | #
# \ \_/ / |_) | | | | |_| | | | (_| | | | | | | | (_) | | (_) | (_| | |_| | #
#  \___/| .__/|_| |_|\__|_| |_|\__,_|_|_| |_| |_|\___/|_|\___/ \__, |\__, | #
#       | |                                                     __/ | __/ | #
#       |_|                                                    |___/ |___/  #
#############################################################################
@dataclass
class BscanImageAndMaskGenerationAlgorithmArgumentsConfig:
    """Configuration for BscanImageAndMaskGenerationAlgorithm arguments."""

    segmentation_configs: list[bscan_mod.SegmentationConfig] = desert.field(
        fields.List(
            fields.Nested(desert.schema_class(bscan_mod.SegmentationConfig)),
            required=True,
        )
    )
    save_path: Optional[Path] = desert.field(FilePath(allow_none=True), default=None)
    output_original_bscans: Optional[bool] = desert.field(
        fields.Bool(allow_none=True), default=False
    )
    image_format: Optional[bscan_mod.ImageFormats] = desert.field(
        marshmallow_enum.EnumField(
            bscan_mod.ImageFormats, by_value=True, allow_none=True
        ),
        default=bscan_mod.ImageFormats.JPEG,
    )
    image_optimize: Optional[bool] = desert.field(
        fields.Bool(allow_none=True), default=True
    )
    image_quality: Optional[int] = desert.field(fields.Int(allow_none=True), default=90)
    image_subsampling: Optional[int] = desert.field(
        fields.Int(allow_none=True), default=0
    )
    image_progressive: Optional[bool] = desert.field(
        fields.Bool(allow_none=True), default=True
    )
    image_transparency: Optional[bool] = desert.field(
        fields.Bool(allow_none=True), default=False
    )


@dataclass
class BscanImageAndMaskGenerationAlgorithmConfig(AlgorithmConfig):
    """Configuration for BscanImageAndMaskGenerationAlgorithm."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(
                AlgorithmType.BscanImageAndMaskGenerationAlgorithm.value
            )
        )
    )
    arguments: Optional[BscanImageAndMaskGenerationAlgorithmArgumentsConfig] = (
        desert.field(
            fields.Nested(
                desert.schema_class(BscanImageAndMaskGenerationAlgorithmArgumentsConfig)
            )
        )
    )


@dataclass
class CSVReportGeneratorOphthalmologyAlgorithmArgumentsConfig:
    """Configuration for CSVReportGeneratorOphthalmologyAlgorithm arguments."""

    save_path: Optional[Path] = desert.field(FilePath(allow_none=True), default=None)
    trial_name: Optional[str] = desert.field(fields.String(), default=None)
    original_cols: Optional[list[str]] = None
    aux_cols: Optional[list[str]] = desert.field(
        fields.List(fields.String(), allow_none=True),
        default_factory=list,
    )
    rename_columns: Optional[dict[str, str]] = desert.field(
        fields.Dict(keys=fields.Str(), values=fields.Str()), default=None
    )
    filter: Optional[list[ColumnFilter]] = desert.field(
        fields.Nested(desert.schema_class(ColumnFilter), many=True, allow_none=True),
        default=None,
    )
    match_patient_visit: Optional[MatchPatientVisit] = desert.field(
        fields.Nested(desert.schema_class(MatchPatientVisit), allow_none=True),
        default=None,
    )
    matched_csv_path: Optional[Path] = desert.field(
        FilePath(allow_none=True), default=None
    )
    produce_matched_only: bool = True
    csv_extensions: Optional[list[str]] = None
    produce_trial_notes_csv: bool = False
    sorting_columns: Optional[dict[str, str]] = desert.field(
        fields.Dict(
            keys=fields.Str(),
            values=fields.Str(validate=validate.OneOf(typing.get_args(DFSortType))),
        ),
        default=None,
    )


@dataclass
class CSVReportGeneratorOphthalmologyAlgorithmConfig(AlgorithmConfig):
    """Configuration for CSVReportGeneratorOphthalmologyAlgorithm."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    AlgorithmType.CSVReportGeneratorOphthalmologyAlgorithm.value,
                    AlgorithmType.CSVReportGeneratorAlgorithm.value,  # Kept for backwards compatibility # noqa: E501
                    # Without ".bitfount" prefix for backwards compatibility
                    "CSVReportGeneratorOphthalmologyAlgorithm",
                    "CSVReportGeneratorAlgorithm",  # Kept for backwards compatibility
                ]
            )
        )
    )
    arguments: Optional[CSVReportGeneratorOphthalmologyAlgorithmArgumentsConfig] = (
        desert.field(
            fields.Nested(
                desert.schema_class(
                    CSVReportGeneratorOphthalmologyAlgorithmArgumentsConfig
                )
            ),
            default=CSVReportGeneratorOphthalmologyAlgorithmArgumentsConfig(),
        )
    )


@dataclass
class ETDRSAlgorithmArgumentsConfig:
    """Configuration for ETDRSAlgorithm arguments."""

    laterality: str
    slo_photo_location_prefixes: Optional[SLOSegmentationLocationPrefix] = desert.field(
        fields.Nested(
            desert.schema_class(SLOSegmentationLocationPrefix), allow_none=True
        ),
        default=None,
    )
    slo_image_metadata_columns: Optional[SLOImageMetadataColumns] = desert.field(
        fields.Nested(desert.schema_class(SLOImageMetadataColumns), allow_none=True),
        default=None,
    )
    oct_image_metadata_columns: Optional[OCTImageMetadataColumns] = desert.field(
        fields.Nested(
            desert.schema_class(OCTImageMetadataColumns),
            allow_none=True,
        ),
        default=None,
    )
    threshold: float = 0.7
    calculate_on_oct: bool = False
    slo_mm_width: float = 8.8
    slo_mm_height: float = 8.8


@dataclass
class ETDRSAlgorithmConfig(AlgorithmConfig):
    """Configuration for ETDRSAlgorithm."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    AlgorithmType.ETDRSAlgorithm.value,
                    # Without ".bitfount" prefix for backwards compatibility
                    "ETDRSAlgorithm",
                ]
            )
        )
    )
    arguments: Optional[ETDRSAlgorithmArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(ETDRSAlgorithmArgumentsConfig)),
    )


@dataclass
class FluidVolumeCalculationAlgorithmArgumentsConfig:
    """Configuration for FluidVolumeCalculationAlgorithm arguments."""

    fluid_volume_include_segmentations: Optional[list[str]] = None


@dataclass
class FluidVolumeCalculationAlgorithmConfig(AlgorithmConfig):
    """Configuration for FluidVolumeCalculationAlgorithm."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(AlgorithmType.FluidVolumeCalculationAlgorithm.value)
        )
    )
    arguments: Optional[FluidVolumeCalculationAlgorithmArgumentsConfig] = desert.field(
        fields.Nested(
            desert.schema_class(FluidVolumeCalculationAlgorithmArgumentsConfig)
        ),
        default=FluidVolumeCalculationAlgorithmArgumentsConfig(),
    )


@dataclass
class FoveaCoordinatesAlgorithmArgumentsConfig:
    """Configuration for FoveaCoordinatesAlgorithm arguments."""

    bscan_width_col: str = "size_width"
    location_prefixes: Optional[SLOSegmentationLocationPrefix] = desert.field(
        fields.Nested(
            desert.schema_class(SLOSegmentationLocationPrefix),
            allow_none=True,
        ),
        default=None,
    )


@dataclass
class FoveaCoordinatesAlgorithmConfig(AlgorithmConfig):
    """Configuration for FoveaCoordinatesAlgorithm."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    AlgorithmType.FoveaCoordinatesAlgorithm.value,
                    # Without ".bitfount" prefix for backwards compatibility
                    "FoveaCoordinatesAlgorithm",
                ]
            )
        )
    )
    arguments: Optional[FoveaCoordinatesAlgorithmArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(FoveaCoordinatesAlgorithmArgumentsConfig)),
        default=FoveaCoordinatesAlgorithmArgumentsConfig(),
    )


@dataclass
class _SimpleCSVAlgorithmArgumentsConfig:
    """Configuration for _SimpleCSVAlgorithm arguments."""

    save_path: Optional[Path] = desert.field(FilePath(allow_none=True), default=None)


@dataclass
class _SimpleCSVAlgorithmAlgorithmConfig(AlgorithmConfig):
    """Configuration for _SimpleCSVAlgorithm."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    AlgorithmType._SimpleCSVAlgorithm.value,
                    # Without ".bitfount" prefix for backwards compatibility
                    "_SimpleCSVAlgorithm",
                ]
            )
        )
    )
    arguments: Optional[_SimpleCSVAlgorithmArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(_SimpleCSVAlgorithmArgumentsConfig)),
        default=_SimpleCSVAlgorithmArgumentsConfig(),
    )


@dataclass
class ReduceCSVAlgorithmCharcoalArgumentsConfig:
    """Configuration for ReduceCSVAlgorithmCharcoal arguments."""

    save_path: Optional[Path] = desert.field(FilePath(allow_none=True), default=None)


@dataclass
class ReduceCSVAlgorithmCharcoalConfig(AlgorithmConfig):
    """Configuration for ReduceCSVAlgorithmCharcoal."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    AlgorithmType.ReduceCSVAlgorithmCharcoal.value,
                    # Without ".bitfount" prefix for backwards compatibility
                    "ReduceCSVAlgorithmCharcoal",
                ]
            )
        )
    )
    arguments: Optional[ReduceCSVAlgorithmCharcoalArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(ReduceCSVAlgorithmCharcoalArgumentsConfig)),
        default=ReduceCSVAlgorithmCharcoalArgumentsConfig(),
    )


@dataclass
class _GATrialCalculationAlgorithmBaseArgumentsConfig:
    """Configuration for GATrialCalculationAlgorithmBase arguments."""

    ga_area_include_segmentations: Optional[list[str]] = None
    ga_area_exclude_segmentations: Optional[list[str]] = None


@dataclass
class GATrialCalculationAlgorithmJadeArgumentsConfig(
    _GATrialCalculationAlgorithmBaseArgumentsConfig
):
    """Configuration for GATrialCalculationAlgorithmJade arguments."""

    pass


@dataclass
class GATrialCalculationAlgorithmJadeConfig(AlgorithmConfig):
    """Configuration for GATrialCalculationAlgorithmJade."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    AlgorithmType.GATrialCalculationAlgorithmJade.value,
                    AlgorithmType.GATrialCalculationAlgorithm.value,  # Kept for backwards compatibility # noqa: E501
                    # Without ".bitfount" prefix for backwards compatibility
                    "GATrialCalculationAlgorithmJade",
                    "GATrialCalculationAlgorithm",  # Kept for backwards compatibility
                ]
            )
        )
    )
    arguments: Optional[GATrialCalculationAlgorithmJadeArgumentsConfig] = desert.field(
        fields.Nested(
            desert.schema_class(GATrialCalculationAlgorithmJadeArgumentsConfig)
        ),
        default=GATrialCalculationAlgorithmJadeArgumentsConfig(),
    )


@dataclass
class GATrialCalculationAlgorithmAmethystArgumentsConfig(
    _GATrialCalculationAlgorithmBaseArgumentsConfig
):
    """Configuration for GATrialCalculationAlgorithmAmethyst arguments."""

    pass


@dataclass
class GATrialCalculationAlgorithmAmethystConfig(AlgorithmConfig):
    """Configuration for GATrialCalculationAlgorithmAmethyst."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    AlgorithmType.GATrialCalculationAlgorithmAmethyst.value,
                    AlgorithmType.GATrialCalculationAlgorithmJade.value,  # Kept for backwards compatibility # noqa: E501
                    AlgorithmType.GATrialCalculationAlgorithm.value,  # Kept for backwards compatibility # noqa: E501
                    # Without "bitfount." prefix for backwards compatibility
                    "GATrialCalculationAlgorithmAmethyst",
                    "GATrialCalculationAlgorithmJade",  # Kept for backwards compatibility # noqa: E501
                    "GATrialCalculationAlgorithm",  # Kept for backwards compatibility
                ]
            )
        )
    )
    arguments: Optional[GATrialCalculationAlgorithmAmethystArgumentsConfig] = (
        desert.field(
            fields.Nested(
                desert.schema_class(GATrialCalculationAlgorithmAmethystArgumentsConfig)
            ),
            default=GATrialCalculationAlgorithmAmethystArgumentsConfig(),
        )
    )


@dataclass
class _GATrialCalculationWithFoveaAlgorithmBaseArgumentsConfig:
    """Configuration for GATrialCalculationAlgorithmWithFoveaBase arguments."""

    ga_area_include_segmentations: Optional[list[str]] = None
    ga_area_exclude_segmentations: Optional[list[str]] = None
    fovea_landmark_idx: Optional[int] = 1


@dataclass
class GATrialCalculationAlgorithmBronzeArgumentsConfig(
    _GATrialCalculationWithFoveaAlgorithmBaseArgumentsConfig
):
    """Configuration for GATrialCalculationAlgorithmBronze arguments."""

    pass


@dataclass
class GATrialCalculationAlgorithmBronzeConfig(AlgorithmConfig):
    """Configuration for GATrialCalculationAlgorithmBronze."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    AlgorithmType.GATrialCalculationAlgorithmBronze.value,
                    # Without "bitfount." prefix for backwards compatibility
                    "GATrialCalculationAlgorithmBronze",
                ]
            )
        )
    )
    arguments: Optional[GATrialCalculationAlgorithmBronzeArgumentsConfig] = (
        desert.field(
            fields.Nested(
                desert.schema_class(GATrialCalculationAlgorithmBronzeArgumentsConfig)
            ),
            default=GATrialCalculationAlgorithmBronzeArgumentsConfig(),
        )
    )


@dataclass
class GATrialCalculationAlgorithmCharcoalArgumentsConfig(
    _GATrialCalculationWithFoveaAlgorithmBaseArgumentsConfig
):
    """Configuration for GATrialCalculationAlgorithmCharcoal arguments."""

    pass


@dataclass
class GATrialCalculationAlgorithmCharcoalConfig(AlgorithmConfig):
    """Configuration for GATrialCalculationAlgorithmCharcoal."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    AlgorithmType.GATrialCalculationAlgorithmCharcoal.value,
                ]
            )
        )
    )
    arguments: Optional[GATrialCalculationAlgorithmCharcoalArgumentsConfig] = (
        desert.field(
            fields.Nested(
                desert.schema_class(GATrialCalculationAlgorithmCharcoalArgumentsConfig)
            ),
            default=GATrialCalculationAlgorithmCharcoalArgumentsConfig(),
        )
    )


@dataclass
class GATrialPDFGeneratorAlgorithmJadeArgumentsConfig:
    """Configuration for GATrialPDFGeneratorAlgorithmJade arguments."""

    # TODO: [BIT-2926] ReportMetadata should not be optional
    report_metadata: Optional[ReportMetadata] = desert.field(
        fields.Nested(desert.schema_class(ReportMetadata)),
        default=None,
    )
    filename_prefix: Optional[str] = desert.field(
        fields.String(validate=validate.Regexp("[a-zA-Z]+")), default=None
    )
    save_path: Optional[Path] = desert.field(FilePath(allow_none=True), default=None)
    filter: Optional[list[ColumnFilter]] = desert.field(
        fields.Nested(desert.schema_class(ColumnFilter), many=True, allow_none=True),
        default=None,
    )
    pdf_filename_columns: Optional[list[str]] = None
    trial_name: Optional[str] = desert.field(fields.String(), default=None)


@dataclass
class GATrialPDFGeneratorAlgorithmJadeConfig(AlgorithmConfig):
    """Configuration for GATrialPDFGeneratorAlgorithmJade."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    AlgorithmType.GATrialPDFGeneratorAlgorithmJade.value,
                    AlgorithmType.GATrialPDFGeneratorAlgorithm.value,  # Kept for backwards compatibility # noqa: E501
                    # Without "bitfount." prefix for backwards compatibility
                    "GATrialPDFGeneratorAlgorithmJade",
                    "GATrialPDFGeneratorAlgorithm",  # Kept for backwards compatibility
                ]
            )
        )
    )
    arguments: Optional[GATrialPDFGeneratorAlgorithmJadeArgumentsConfig] = desert.field(
        fields.Nested(
            desert.schema_class(GATrialPDFGeneratorAlgorithmJadeArgumentsConfig)
        ),
        default=GATrialPDFGeneratorAlgorithmJadeArgumentsConfig(),
    )


@dataclass
class GATrialPDFGeneratorAlgorithmAmethystArgumentsConfig:
    """Configuration for GATrialPDFGeneratorAlgorithmAmethyst arguments."""

    # TODO: [BIT-2926] ReportMetadata should not be optional
    report_metadata: Optional[ReportMetadata] = desert.field(
        fields.Nested(desert.schema_class(ReportMetadata)),
        default=None,
    )
    filename_prefix: Optional[str] = desert.field(
        fields.String(validate=validate.Regexp("[a-zA-Z]+")), default=None
    )
    save_path: Optional[Path] = desert.field(FilePath(allow_none=True), default=None)
    filter: Optional[list[ColumnFilter]] = desert.field(
        fields.Nested(desert.schema_class(ColumnFilter), many=True, allow_none=True),
        default=None,
    )
    pdf_filename_columns: Optional[list[str]] = None
    trial_name: Optional[str] = desert.field(fields.String(), default=None)


@dataclass
class GATrialPDFGeneratorAlgorithmAmethystConfig(AlgorithmConfig):
    """Configuration for GATrialPDFGeneratorAlgorithmAmethyst."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    AlgorithmType.GATrialPDFGeneratorAlgorithmAmethyst.value,
                    # Without "bitfount." prefix for backwards compatibility
                    "GATrialPDFGeneratorAlgorithmAmethyst",
                ]
            )
        )
    )
    arguments: Optional[GATrialPDFGeneratorAlgorithmAmethystArgumentsConfig] = (
        desert.field(
            fields.Nested(
                desert.schema_class(GATrialPDFGeneratorAlgorithmAmethystArgumentsConfig)
            ),
            default=GATrialPDFGeneratorAlgorithmAmethystArgumentsConfig(),
        )
    )


@dataclass
class TrialInclusionCriteriaMatchAlgorithmJadeArgumentsConfig:
    """Configuration for TrialInclusionCriteriaMatchAlgorithmJade arguments."""

    # Jade exposes nothing here, using the defaults instead.
    pass


@dataclass
class TrialInclusionCriteriaMatchAlgorithmJadeConfig(AlgorithmConfig):
    """Configuration for TrialInclusionCriteriaMatchAlgorithmJade."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    AlgorithmType.TrialInclusionCriteriaMatchAlgorithmJade.value,
                    AlgorithmType.TrialInclusionCriteriaMatchAlgorithm.value,  # Kept for backwards compatibility # noqa: E501
                    # Without "bitfount." prefix for backwards compatibility
                    "TrialInclusionCriteriaMatchAlgorithmJade",
                    "TrialInclusionCriteriaMatchAlgorithm",  # Kept for backwards compatibility # noqa: E501
                ]
            )
        )
    )
    arguments: Optional[TrialInclusionCriteriaMatchAlgorithmJadeArgumentsConfig] = (
        desert.field(
            fields.Nested(
                desert.schema_class(
                    TrialInclusionCriteriaMatchAlgorithmJadeArgumentsConfig
                )
            ),
            default=TrialInclusionCriteriaMatchAlgorithmJadeArgumentsConfig(),
        )
    )


@dataclass
class _TrialInclusionCriteriaMatchAlgorithmBaseArgumentsConfig:
    """Shared base arguments for trial inclusion algorithms."""

    cnv_threshold: float = desert.field(fields.Float(), default=CNV_THRESHOLD)
    largest_ga_lesion_lower_bound: float = desert.field(
        fields.Float(), default=LARGEST_GA_LESION_LOWER_BOUND
    )
    largest_ga_lesion_upper_bound: Optional[float] = desert.field(
        fields.Float(allow_none=True), default=None
    )
    total_ga_area_lower_bound: float = desert.field(
        fields.Float(), default=TOTAL_GA_AREA_LOWER_BOUND
    )
    total_ga_area_upper_bound: float = desert.field(
        fields.Float(), default=TOTAL_GA_AREA_UPPER_BOUND
    )
    patient_age_lower_bound: Optional[int] = desert.field(
        fields.Integer(allow_none=True), default=None
    )
    patient_age_upper_bound: Optional[int] = desert.field(
        fields.Integer(allow_none=True), default=None
    )


@dataclass
class TrialInclusionCriteriaMatchAlgorithmAmethystArgumentsConfig(
    _TrialInclusionCriteriaMatchAlgorithmBaseArgumentsConfig
):
    """Configuration for TrialInclusionCriteriaMatchAlgorithmAmethyst arguments."""

    pass


@dataclass
class TrialInclusionCriteriaMatchAlgorithmAmethystConfig(AlgorithmConfig):
    """Configuration for TrialInclusionCriteriaMatchAlgorithmAmethyst."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    AlgorithmType.TrialInclusionCriteriaMatchAlgorithmAmethyst.value,
                    # without "bitfount." prefix for backward compatibility
                    "TrialInclusionCriteriaMatchAlgorithmAmethyst",
                ],
            )
        )
    )
    arguments: Optional[TrialInclusionCriteriaMatchAlgorithmAmethystArgumentsConfig] = (
        desert.field(
            fields.Nested(
                desert.schema_class(
                    TrialInclusionCriteriaMatchAlgorithmAmethystArgumentsConfig
                )
            ),
            default=TrialInclusionCriteriaMatchAlgorithmAmethystArgumentsConfig(),
        )
    )


@dataclass
class TrialInclusionCriteriaMatchAlgorithmBronzeArgumentsConfig(
    _TrialInclusionCriteriaMatchAlgorithmBaseArgumentsConfig
):
    """Configuration for TrialInclusionCriteriaMatchAlgorithmBronze arguments."""

    distance_from_fovea_lower_bound: float = desert.field(
        fields.Float(), default=DISTANCE_FROM_FOVEA_LOWER_BOUND
    )
    distance_from_fovea_upper_bound: float = desert.field(
        fields.Float(), default=DISTANCE_FROM_FOVEA_UPPER_BOUND
    )
    exclude_foveal_ga: bool = desert.field(fields.Bool(), default=EXCLUDE_FOVEAL_GA)


@dataclass
class TrialInclusionCriteriaMatchAlgorithmBronzeConfig(AlgorithmConfig):
    """Configuration for TrialInclusionCriteriaMatchAlgorithmBronze."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    AlgorithmType.TrialInclusionCriteriaMatchAlgorithmBronze.value,
                    # without "bitfount." prefix for backward compatibility
                    "TrialInclusionCriteriaMatchAlgorithmBronze",
                ],
            )
        )
    )
    arguments: Optional[TrialInclusionCriteriaMatchAlgorithmBronzeArgumentsConfig] = (
        desert.field(
            fields.Nested(
                desert.schema_class(
                    TrialInclusionCriteriaMatchAlgorithmBronzeArgumentsConfig
                )
            ),
            default=TrialInclusionCriteriaMatchAlgorithmBronzeArgumentsConfig(),
        )
    )


@dataclass
class TrialInclusionCriteriaMatchAlgorithmCharcoalArgumentsConfig(
    _TrialInclusionCriteriaMatchAlgorithmBaseArgumentsConfig
):
    """Configuration for TrialInclusionCriteriaMatchAlgorithmCharcoal arguments."""

    conditions_inclusion_codes: Optional[list[str]] = None
    conditions_exclusion_codes: Optional[list[str]] = None
    procedures_exclusion_codes: Optional[list[str]] = None


@dataclass
class TrialInclusionCriteriaMatchAlgorithmCharcoalConfig(AlgorithmConfig):
    """Configuration for TrialInclusionCriteriaMatchAlgorithmCharcoal."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    AlgorithmType.TrialInclusionCriteriaMatchAlgorithmCharcoal.value,
                ],
            )
        )
    )
    arguments: Optional[TrialInclusionCriteriaMatchAlgorithmCharcoalArgumentsConfig] = (
        desert.field(
            fields.Nested(
                desert.schema_class(
                    TrialInclusionCriteriaMatchAlgorithmCharcoalArgumentsConfig
                )
            ),
            default=TrialInclusionCriteriaMatchAlgorithmCharcoalArgumentsConfig(),
        )
    )
