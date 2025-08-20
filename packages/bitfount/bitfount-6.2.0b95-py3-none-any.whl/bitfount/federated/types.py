"""Useful types for Federated Learning."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
import os
from typing import (
    TYPE_CHECKING,
    Literal,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    TypedDict,
    Union,
    runtime_checkable,
)

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from typing_extensions import NotRequired, TypeAlias

from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.schema import BitfountSchema
from bitfount.types import _JSONDict, _StrAnyDict

if TYPE_CHECKING:
    from bitfount.externals.general.authentication import ExternallyManagedJWT
    from bitfount.hub.api import BitfountHub, BitfountSession, PodPublicMetadata
    from bitfount.hub.types import _AMResourceUsageAndLimitJSON
    from bitfount.runners.config_schemas.common_schemas import DataSplitConfig
    from bitfount.runners.config_schemas.hub_schemas import APIKeys
    from bitfount.runners.config_schemas.pod_schemas import (
        FileSystemFilterConfig,
        PodDataConfig,
        PodDetailsConfig,
    )


@dataclass
class DatasourceContainerConfig:
    """Contains a datasource and maybe some data related to it.

    This represents a datasource configuration _pre_-data-loading/configuration and
    so the data config and schema are not required.
    """

    name: str
    datasource: BaseSource
    datasource_details: Optional[PodDetailsConfig] = None
    data_config: Optional[PodDataConfig] = None
    schema: Optional[Union[str, os.PathLike, BitfountSchema]] = None


@dataclass
class DatasourceContainer:
    """Contains a datasource and all the data related to it.

    This represents a datasource configuration _post_-data-loading/configuration and
    so the data config and schema must be present.
    """

    name: str
    datasource: BaseSource
    datasource_details: PodDetailsConfig
    data_config: PodDataConfig
    schema: BitfountSchema


@dataclass
class MinimalDatasourceConfig:
    """Minimal serializable configuration required for creating a datasource."""

    datasource_cls_name: str
    name: str
    datasource_args: _JSONDict
    file_system_filters: Optional[FileSystemFilterConfig]
    data_split: Optional[DataSplitConfig]


@dataclass
class MinimalSchemaGenerationConfig:
    """Minimal serializable configuration required for creating a schema."""

    datasource_name: str
    description: Optional[str]
    column_descriptions: Optional[
        Union[Mapping[str, Mapping[str, str]], Mapping[str, str]]
    ]
    ignore_cols: Optional[list[str]]
    force_stypes: Optional[
        MutableMapping[
            Literal["categorical", "continuous", "image", "text", "image_prefix"],
            list[str],
        ]
    ]


@dataclass
class MinimalSchemaUploadConfig:
    """Minimal serializable configuration required for uploading a schema."""

    # Metadata required for uploading the schema (including the schema itself)
    public_metadata: PodPublicMetadata
    # Public keys required for having permission to upload the schema
    access_manager_public_key: RSAPublicKey
    pod_public_key: RSAPublicKey


@dataclass
class HubConfig:
    """Configuration for connecting to Bitfount Hub."""

    username: Optional[str]
    secrets: Optional[Union[APIKeys, ExternallyManagedJWT]]
    session: Optional[BitfountSession] = None
    session_info: Optional[dict] = None


class TextGenerationDictionary(TypedDict):
    """Hugging Face dictionary response for text generation."""

    generated_text: str


class HuggingFaceImageClassificationInferenceDictionary(TypedDict):
    """Hugging Face dictionary response for image classification."""

    image_classification: str


TextGenerationDefaultReturnType: TypeAlias = list[list[TextGenerationDictionary]]


class SerializedDataStructure(TypedDict):
    """Serialized representation of a data structure."""

    table: NotRequired[Union[str, dict[str, str]]]
    schema_requirements: NotRequired[_StrAnyDict]
    compatible_datasources: NotRequired[list[str]]


class SerializedModel(TypedDict):
    """Serialized representation of a model."""

    class_name: str
    hub: NotRequired[Optional[BitfountHub]]
    schema: NotRequired[_StrAnyDict]
    datastructure: NotRequired[SerializedDataStructure]


class SerializedAlgorithm(TypedDict):
    """Serialized representation of an algorithm."""

    class_name: str  # value from AlgorithmType enum
    model: NotRequired[SerializedModel]
    datastructure: NotRequired[SerializedDataStructure]
    save_path: NotRequired[str]  # Only certain algorithms have this


class SerializedAggregator(TypedDict):
    """Serialized representation of an aggregator."""

    class_name: str  # value from AggregatorType enum


class SerializedProtocol(TypedDict):
    """Serialized representation of a protocol."""

    class_name: str  # value from ProtocolType enum
    algorithm: Union[SerializedAlgorithm, list[SerializedAlgorithm]]
    aggregator: NotRequired[SerializedAggregator]
    primary_results_path: NotRequired[str]


class ProtocolType(Enum):
    """Available protocol names from `bitfount.federated.protocol`."""

    FederatedAveraging = "bitfount.FederatedAveraging"
    ResultsOnly = "bitfount.ResultsOnly"
    InferenceAndCSVReport = "bitfount.InferenceAndCSVReport"
    InstrumentedInferenceAndCSVReport = "bitfount.InstrumentedInferenceAndCSVReport"
    InferenceAndReturnCSVReport = "bitfount.InferenceAndReturnCSVReport"
    # Ophthalmology Protocols
    GAScreeningProtocolAmethyst = "bitfount.GAScreeningProtocolAmethyst"
    GAScreeningProtocolJade = "bitfount.GAScreeningProtocolJade"
    GAScreeningProtocolBronze = "bitfount.GAScreeningProtocolBronze"
    GAScreeningProtocolBronzeWithEHR = "bitfount.GAScreeningProtocolBronzeWithEHR"
    GAScreeningProtocolCharcoal = "bitfount.GAScreeningProtocolCharcoal"
    GAScreeningProtocol = (
        "bitfount.GAScreeningProtocol"  # Kept for backwards compatibility
    )
    RetinalDiseaseProtocolCobalt = "bitfount.RetinalDiseaseProtocolCobalt"
    BasicOCTProtocol = "bitfount.BasicOCTProtocol"  # Kept for backwards compatibility
    InferenceAndImageOutput = "bitfount.InferenceAndImageOutput"
    InSiteInsightsProtocol = "bitfount.InSiteInsightsProtocol"
    # EHR Protocols
    NextGenSearchProtocol = "bitfount.NextGenSearchProtocol"
    DataExtractionProtocolCharcoal = "bitfount.DataExtractionProtocolCharcoal"
    FluidVolumeScreeningProtocol = "bitfount.FluidVolumeScreeningProtocol"


class AlgorithmType(Enum):
    """Available algorithm names from `bitfount.federated.algorithm`."""

    FederatedModelTraining = "bitfount.FederatedModelTraining"
    ModelTrainingAndEvaluation = "bitfount.ModelTrainingAndEvaluation"
    ModelEvaluation = "bitfount.ModelEvaluation"
    ModelInference = "bitfount.ModelInference"
    SqlQuery = "bitfount.SqlQuery"
    PrivateSqlQuery = "bitfount.PrivateSqlQuery"
    HuggingFacePerplexityEvaluation = "bitfount.HuggingFacePerplexityEvaluation"
    HuggingFaceTextGenerationInference = "bitfount.HuggingFaceTextGenerationInference"
    HuggingFaceImageClassificationInference = (
        "bitfount.HuggingFaceImageClassificationInference"
    )
    HuggingFaceImageSegmentationInference = (
        "bitfount.HuggingFaceImageSegmentationInference"
    )
    HuggingFaceTextClassificationInference = (
        "bitfount.HuggingFaceTextClassificationInference"
    )
    CSVReportAlgorithm = "bitfount.CSVReportAlgorithm"
    TIMMFineTuning = "bitfount.TIMMFineTuning"
    TIMMInference = "bitfount.TIMMInference"
    # Ophthalmology Algorithms
    CSVReportGeneratorOphthalmologyAlgorithm = (
        "bitfount.CSVReportGeneratorOphthalmologyAlgorithm"
    )
    CSVReportGeneratorAlgorithm = (
        "bitfount.CSVReportGeneratorAlgorithm"  # Kept for backwards compatibility
    )
    ETDRSAlgorithm = "bitfount.ETDRSAlgorithm"
    FluidVolumeCalculationAlgorithm = "bitfount.FluidVolumeCalculationAlgorithm"
    FoveaCoordinatesAlgorithm = "bitfount.FoveaCoordinatesAlgorithm"
    GATrialCalculationAlgorithmJade = "bitfount.GATrialCalculationAlgorithmJade"
    GATrialCalculationAlgorithmAmethyst = "bitfount.GATrialCalculationAlgorithmAmethyst"
    GATrialCalculationAlgorithmCharcoal = "bitfount.GATrialCalculationAlgorithmCharcoal"
    GATrialCalculationAlgorithmBronze = "bitfount.GATrialCalculationAlgorithmBronze"
    GATrialCalculationAlgorithm = (
        "bitfount.GATrialCalculationAlgorithm"  # Kept for backwards compatibility
    )
    TrialInclusionCriteriaMatchAlgorithmAmethyst = (
        "bitfount.TrialInclusionCriteriaMatchAlgorithmAmethyst"
    )
    TrialInclusionCriteriaMatchAlgorithmBronze = (
        "bitfount.TrialInclusionCriteriaMatchAlgorithmBronze"
    )
    TrialInclusionCriteriaMatchAlgorithmJade = (
        "bitfount.TrialInclusionCriteriaMatchAlgorithmJade"
    )
    TrialInclusionCriteriaMatchAlgorithmCharcoal = (
        "bitfount.TrialInclusionCriteriaMatchAlgorithmCharcoal"
    )
    TrialInclusionCriteriaMatchAlgorithm = "bitfount.TrialInclusionCriteriaMatchAlgorithm"  # Kept for backwards compatibility # noqa: E501
    GATrialPDFGeneratorAlgorithmAmethyst = (
        "bitfount.GATrialPDFGeneratorAlgorithmAmethyst"
    )
    GATrialPDFGeneratorAlgorithmJade = "bitfount.GATrialPDFGeneratorAlgorithmJade"
    GATrialPDFGeneratorAlgorithm = (
        "bitfount.GATrialPDFGeneratorAlgorithm"  # Kept for backwards compatibility
    )
    _SimpleCSVAlgorithm = "bitfount._SimpleCSVAlgorithm"
    ReduceCSVAlgorithmCharcoal = "bitfount.ReduceCSVAlgorithmCharcoal"
    RecordFilterAlgorithm = "bitfount.RecordFilterAlgorithm"
    BscanImageAndMaskGenerationAlgorithm = (
        "bitfount.BscanImageAndMaskGenerationAlgorithm"
    )
    # EHR Algorithms
    EHRPatientQueryAlgorithm = "bitfount.EHRPatientQueryAlgorithm"
    NextGenPatientInfoDownloadAlgorithm = "bitfount.NextGenPatientInfoDownloadAlgorithm"


class AggregatorType(Enum):
    """Available aggregator names from `bitfount.federated.aggregator`."""

    Aggregator = "bitfount.Aggregator"
    SecureAggregator = "bitfount.SecureAggregator"


class _PodResponseType(Enum):
    """Pod response types sent to `Modeller` on a training job request.

    Responses correspond to those from /api/access.
    """

    ACCEPT = auto()
    NO_ACCESS = auto()
    INVALID_PROOF_OF_IDENTITY = auto()
    UNAUTHORISED = auto()
    NO_PROOF_OF_IDENTITY = auto()
    NO_DATA = auto()
    INCOMPATIBLE_DATASOURCE = auto()


class AccessCheckResult(TypedDict):
    """Container for the result of the access manager check."""

    response_type: _PodResponseType
    limits: Optional[list[_AMResourceUsageAndLimitJSON]]


class _DataLessAlgorithm:
    """Base algorithm class for tagging purposes.

    Used in algorithms for which data loading is done at runtime.
    """

    ...


_RESPONSE_MESSAGES = {
    # /api/access response messages
    _PodResponseType.ACCEPT: "Job accepted",
    _PodResponseType.NO_ACCESS: "There are no permissions for this modeller/pod combination.",  # noqa: E501
    _PodResponseType.INVALID_PROOF_OF_IDENTITY: "Unable to verify identity; ensure correct login used.",  # noqa: E501
    _PodResponseType.UNAUTHORISED: "Insufficient permissions for the requested task on this pod.",  # noqa: E501
    _PodResponseType.NO_PROOF_OF_IDENTITY: "Unable to verify identity, please try again.",  # noqa: E501
    _PodResponseType.NO_DATA: "No data available for the requested task.",
    _PodResponseType.INCOMPATIBLE_DATASOURCE: "Incompatible datasource for the requested task.",  # noqa: E501
}


@runtime_checkable
class _TaskRequestMessageGenerator(Protocol):
    """Callback protocol describing a task request message generator."""

    def __call__(
        self,
        serialized_protocol: SerializedProtocol,
        pod_identifiers: list[str],
        aes_key: bytes,
        pod_public_key: RSAPublicKey,
        project_id: Optional[str],
        run_on_new_data_only: bool = False,
        batched_execution: Optional[bool] = None,
        test_run: bool = False,
        force_rerun_failed_files: bool = True,
    ) -> bytes:
        """Function signature for the callback."""
        ...
