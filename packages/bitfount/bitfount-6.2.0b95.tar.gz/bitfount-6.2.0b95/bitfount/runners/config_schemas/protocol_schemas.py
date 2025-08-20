"""Config YAML specification classes related to protocols."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
import typing
from typing import Any, Optional

import desert
from marshmallow import ValidationError, fields, validate
import marshmallow_enum

from bitfount.federated.protocols.results_only import SaveLocation
from bitfount.federated.types import ProtocolType
from bitfount.runners.config_schemas.algorithm_schemas import AggregatorConfig
from bitfount.runners.config_schemas.common_schemas import FilePath
from bitfount.runners.utils import get_concrete_config_subclasses
from bitfount.types import _JSONDict

_logger = logging.getLogger(__name__)


@dataclass
class ProtocolConfig:
    """Configuration for the Protocol."""

    name: str
    arguments: Optional[Any] = None

    @classmethod
    def _get_subclasses(cls) -> tuple[type[ProtocolConfig], ...]:
        """Get all the concrete subclasses of this config class."""
        return get_concrete_config_subclasses(cls)


@dataclass
class ResultsOnlyProtocolArgumentsConfig:
    """Configuration for the ResultsOnly Protocol arguments."""

    aggregator: Optional[AggregatorConfig] = None
    secure_aggregation: bool = False
    save_location: Optional[list[SaveLocation]] = desert.field(
        fields.List(marshmallow_enum.EnumField(SaveLocation, by_value=True)),
        default_factory=lambda: [SaveLocation.Modeller],
    )
    save_path: Optional[Path] = desert.field(FilePath(allow_none=True), default=None)


@dataclass
class ResultsOnlyProtocolConfig(ProtocolConfig):
    """Configuration for the ResultsOnly Protocol."""

    name: str = desert.field(
        fields.String(validate=validate.Equal(ProtocolType.ResultsOnly.value))
    )
    arguments: Optional[ResultsOnlyProtocolArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(ResultsOnlyProtocolArgumentsConfig)),
        default=ResultsOnlyProtocolArgumentsConfig(),
    )


@dataclass
class FederatedAveragingProtocolArgumentsConfig:
    """Configuration for the FedreatedAveraging Protocol arguments."""

    aggregator: Optional[AggregatorConfig] = None
    steps_between_parameter_updates: Optional[int] = None
    epochs_between_parameter_updates: Optional[int] = None
    auto_eval: bool = True
    secure_aggregation: bool = False


@dataclass
class FederatedAveragingProtocolConfig(ProtocolConfig):
    """Configuration for the FederatedAveraging Protocol."""

    name: str = desert.field(
        fields.String(validate=validate.Equal(ProtocolType.FederatedAveraging.value))
    )
    arguments: Optional[FederatedAveragingProtocolArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(FederatedAveragingProtocolArgumentsConfig)),
        default=FederatedAveragingProtocolArgumentsConfig(),
    )


@dataclass
class InferenceAndCSVReportArgumentsConfig:
    """Configuration for InferenceAndCSVReport arguments."""

    aggregator: Optional[AggregatorConfig] = None


@dataclass
class InferenceAndCSVReportConfig(ProtocolConfig):
    """Configuration for InferenceAndCSVReport."""

    name: str = desert.field(
        fields.String(validate=validate.Equal(ProtocolType.InferenceAndCSVReport.value))
    )
    arguments: Optional[InferenceAndCSVReportArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(InferenceAndCSVReportArgumentsConfig)),
        default=InferenceAndCSVReportArgumentsConfig(),
    )


@dataclass
class InstrumentedInferenceAndCSVReportArgumentsConfig:
    """Configuration for InstrumentedInferenceAndCSVReport arguments."""

    aggregator: Optional[AggregatorConfig] = None


@dataclass
class InstrumentedInferenceAndCSVReportConfig(ProtocolConfig):
    """Configuration for InstrumentedInferenceAndCSVReport."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(
                ProtocolType.InstrumentedInferenceAndCSVReport.value
            )
        )
    )
    arguments: Optional[InstrumentedInferenceAndCSVReportArgumentsConfig] = (
        desert.field(
            fields.Nested(
                desert.schema_class(InstrumentedInferenceAndCSVReportArgumentsConfig)
            ),
            default=InstrumentedInferenceAndCSVReportArgumentsConfig(),
        )
    )


@dataclass
class InferenceAndReturnCSVReportArgumentsConfig:
    """Configuration for InferenceAndReturnCSVReport arguments."""

    aggregator: Optional[AggregatorConfig] = None


@dataclass
class InferenceAndReturnCSVReportConfig(ProtocolConfig):
    """Configuration for InferenceAndReturnCSVReport."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(ProtocolType.InferenceAndReturnCSVReport.value)
        )
    )
    arguments: Optional[InferenceAndReturnCSVReportArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(InferenceAndReturnCSVReportArgumentsConfig)),
        default=InferenceAndReturnCSVReportArgumentsConfig(),
    )


@dataclass
class GenericProtocolConfig(ProtocolConfig):
    """Configuration for unspecified protocol plugins.

    Raises:
        ValueError: if the protocol name starts with `bitfount.`
    """

    __config_type: typing.ClassVar[str] = "fallback"

    name: str
    arguments: _JSONDict = desert.field(
        fields.Dict(keys=fields.Str), default_factory=dict
    )

    def __post_init__(self) -> None:
        _logger.warning(
            f"Protocol configuration was parsed as {self.__class__.__name__};"
            f" was this intended?"
        )
        if self.name.startswith("bitfount."):
            _logger.error(
                f"Unexpected protocol config; was parsed as GenericProtocol:\n{self}"
            )
            raise ValidationError(
                "Protocol names starting with 'bitfount.' are reserved for built-in "
                "protocols. It is likely the provided arguments don't match the "
                "expected schema for the protocol. Please check the documentation "
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
class RetinalDiseaseProtocolCobaltArgumentsConfig:
    """Configuration for RetinalDiseaseProtocolCobalt arguments."""

    aggregator: Optional[AggregatorConfig] = None


@dataclass
class RetinalDiseaseProtocolCobaltConfig(ProtocolConfig):
    """Configuration for RetinalDiseaseProtocolCobalt."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    ProtocolType.RetinalDiseaseProtocolCobalt.value,
                    ProtocolType.BasicOCTProtocol.value,  # Kept for backwards compatibility # noqa: E501
                    # Without ".bitfount" prefix for backwards compatibility
                    "RetinalDiseaseProtocolCobalt",
                    "BasicOCTProtocol",  # Kept for backwards compatibility
                ],
            )
        )
    )
    arguments: Optional[RetinalDiseaseProtocolCobaltArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(RetinalDiseaseProtocolCobaltArgumentsConfig)),
        default=RetinalDiseaseProtocolCobaltArgumentsConfig(),
    )


@dataclass
class FluidVolumeScreeningProtocolArgumentsConfig:
    """Configuration for FluidVolumeScreeningProtocol arguments."""

    aggregator: Optional[AggregatorConfig] = None
    results_notification_email: Optional[bool] = False
    trial_name: Optional[str] = desert.field(fields.String(), default=None)
    rename_columns: Optional[dict[str, str]] = desert.field(
        fields.Dict(keys=fields.Str(), values=fields.Str()), default=None
    )


@dataclass
class FluidVolumeScreeningProtocolConfig(ProtocolConfig):
    """Configuration for FluidVolumeScreeningProtocol."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(
                ProtocolType.FluidVolumeScreeningProtocol.value,
            )
        )
    )
    arguments: Optional[FluidVolumeScreeningProtocolArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(FluidVolumeScreeningProtocolArgumentsConfig)),
        default=FluidVolumeScreeningProtocolArgumentsConfig(),
    )


@dataclass
class GAScreeningProtocolJadeArgumentsConfig:
    """Configuration for GAScreeningProtocolJade arguments."""

    aggregator: Optional[AggregatorConfig] = None
    results_notification_email: Optional[bool] = False
    trial_name: Optional[str] = desert.field(fields.String(), default=None)
    rename_columns: Optional[dict[str, str]] = desert.field(
        fields.Dict(keys=fields.Str(), values=fields.Str()), default=None
    )


@dataclass
class GAScreeningProtocolJadeConfig(ProtocolConfig):
    """Configuration for GAScreeningProtocolJade."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    ProtocolType.GAScreeningProtocolJade.value,
                    ProtocolType.GAScreeningProtocol.value,  # Kept for backwards compatibility # noqa: E501
                    # Without ".bitfount" prefix for backwards compatibility
                    "GAScreeningProtocolJade",
                    "GAScreeningProtocol",  # Kept for backwards compatibility
                ],
            )
        )
    )
    arguments: Optional[GAScreeningProtocolJadeArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(GAScreeningProtocolJadeArgumentsConfig)),
        default=GAScreeningProtocolJadeArgumentsConfig(),
    )


@dataclass
class GAScreeningProtocolAmethystArgumentsConfig:
    """Configuration for GAScreeningProtocolAmethyst arguments."""

    aggregator: Optional[AggregatorConfig] = None
    results_notification_email: Optional[bool] = False
    trial_name: Optional[str] = desert.field(fields.String(), default=None)
    rename_columns: Optional[dict[str, str]] = desert.field(
        fields.Dict(keys=fields.Str(), values=fields.Str()), default=None
    )


@dataclass
class GAScreeningProtocolAmethystConfig(ProtocolConfig):
    """Configuration for GAScreeningProtocolAmethyst."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    ProtocolType.GAScreeningProtocolAmethyst.value,
                    # Without ".bitfount" prefix for backwards compatibility
                    "GAScreeningProtocolAmethyst",
                ]
            )
        )
    )
    arguments: Optional[GAScreeningProtocolAmethystArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(GAScreeningProtocolAmethystArgumentsConfig)),
        default=GAScreeningProtocolAmethystArgumentsConfig(),
    )


@dataclass
class GAScreeningProtocolBronzeArgumentsConfig:
    """Configuration for GAScreeningProtocolBronze arguments."""

    aggregator: Optional[AggregatorConfig] = None
    results_notification_email: Optional[bool] = False
    trial_name: Optional[str] = desert.field(fields.String(), default=None)
    rename_columns: Optional[dict[str, str]] = desert.field(
        fields.Dict(keys=fields.Str(), values=fields.Str()), default=None
    )


@dataclass
class GAScreeningProtocolBronzeConfig(ProtocolConfig):
    """Configuration for GAScreeningProtocolBronze."""

    name: str = desert.field(
        fields.String(
            validate=validate.OneOf(
                [
                    ProtocolType.GAScreeningProtocolBronze.value,
                    # Without ".bitfount" prefix for backwards compatibility
                    "GAScreeningProtocolBronze",
                ]
            )
        )
    )
    arguments: Optional[GAScreeningProtocolBronzeArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(GAScreeningProtocolBronzeArgumentsConfig)),
        default=GAScreeningProtocolBronzeArgumentsConfig(),
    )


@dataclass
class GAScreeningProtocolBronzeWithEHRConfig(ProtocolConfig):
    """Configuration for GAScreeningProtocolBronzeWithEHR."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(ProtocolType.GAScreeningProtocolBronzeWithEHR.value)
        )
    )
    arguments: Optional[GAScreeningProtocolBronzeArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(GAScreeningProtocolBronzeArgumentsConfig)),
        default=GAScreeningProtocolBronzeArgumentsConfig(),
    )


@dataclass
class GAScreeningProtocolCharcoalArgumentsConfig:
    """Configuration for GAScreeningProtocolCharcoal arguments."""

    aggregator: Optional[AggregatorConfig] = None
    results_notification_email: Optional[bool] = False
    trial_name: Optional[str] = desert.field(fields.String(), default=None)
    rename_columns: Optional[dict[str, str]] = desert.field(
        fields.Dict(keys=fields.Str(), values=fields.Str()), default=None
    )


@dataclass
class GAScreeningProtocolCharcoalConfig(ProtocolConfig):
    """Configuration for GAScreeningProtocolCharcoal."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(ProtocolType.GAScreeningProtocolCharcoal.value)
        )
    )
    arguments: Optional[GAScreeningProtocolCharcoalArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(GAScreeningProtocolCharcoalArgumentsConfig)),
        default=GAScreeningProtocolCharcoalArgumentsConfig(),
    )


@dataclass
class NextGenSearchProtocolArgumentsConfig:
    """Configuration for NextGenSearchProtocol arguments."""

    rename_columns: Optional[dict[str, str]] = desert.field(
        fields.Dict(keys=fields.Str(), values=fields.Str()), default=None
    )


@dataclass
class NextGenSearchProtocolConfig(ProtocolConfig):
    """Configuration for NextGenSearchProtocol."""

    name: str = desert.field(
        fields.String(validate=validate.Equal(ProtocolType.NextGenSearchProtocol.value))
    )
    arguments: Optional[NextGenSearchProtocolArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(NextGenSearchProtocolArgumentsConfig)),
        default=NextGenSearchProtocolArgumentsConfig(),
    )


@dataclass
class DataExtractionProtocolCharcoalArgumentsConfig:
    """Configuration for DataExtractionProtocolCharcoal arguments."""

    trial_name: Optional[str] = desert.field(
        fields.String(allow_none=True), default=None
    )
    patient_ids: Optional[list[str]] = desert.field(
        fields.List(fields.String(), allow_none=True), default=None
    )
    patient_ids_file: Optional[Path] = desert.field(
        FilePath(allow_none=True), default=None
    )

    def __post_init__(self) -> None:
        # Check that we have only one of `patient_ids` and `patient_ids_file`
        if self.patient_ids is not None and self.patient_ids_file is not None:
            _logger.error(
                "Cannot have both `patient_ids` and `patient_ids_file`,"
                " please supply only one option."
            )
            raise ValueError(
                "Cannot have both `patient_ids` and `patient_ids_file`"
                " in DataExtractionProtocolCharcoal arguments,"
                " please supply only one option."
            )
        if self.patient_ids is None and self.patient_ids_file is None:
            _logger.error(
                "Must have one of `patient_ids` and `patient_ids_file`,"
                " please supply one option."
            )
            raise ValueError(
                "Must have one of `patient_ids` and `patient_ids_file`,"
                " in DataExtractionProtocolCharcoal arguments,"
                " please supply one option."
            )


@dataclass
class DataExtractionProtocolCharcoalConfig(ProtocolConfig):
    """Configuration for DataExtractionProtocolCharcoal."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(ProtocolType.DataExtractionProtocolCharcoal.value)
        )
    )
    arguments: Optional[DataExtractionProtocolCharcoalArgumentsConfig] = desert.field(
        fields.Nested(
            desert.schema_class(DataExtractionProtocolCharcoalArgumentsConfig)
        ),
    )


@dataclass
class InferenceAndImageOutputArgumentsConfig:
    """Configuration for InferenceAndImageOutput arguments."""

    aggregator: Optional[AggregatorConfig] = None
    rename_columns: Optional[dict[str, str]] = desert.field(
        fields.Dict(keys=fields.Str(), values=fields.Str()), default=None
    )


@dataclass
class InferenceAndImageOutputConfig(ProtocolConfig):
    """Configuration for InferenceAndImageOutput."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(ProtocolType.InferenceAndImageOutput.value)
        )
    )
    arguments: Optional[InferenceAndImageOutputArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(InferenceAndImageOutputArgumentsConfig)),
        default=InferenceAndImageOutputArgumentsConfig(),
    )


@dataclass
class InSiteInsightsProtocolArgumentsConfig:
    """Configuration for InSiteInsightsProtocol arguments."""

    aggregator: Optional[AggregatorConfig] = None
    results_notification_email: Optional[bool] = False


@dataclass
class InSiteInsightsProtocolConfig(ProtocolConfig):
    """Configuration for InSiteInsightsProtocol."""

    name: str = desert.field(
        fields.String(
            validate=validate.Equal(ProtocolType.InSiteInsightsProtocol.value)
        )
    )
    arguments: Optional[InSiteInsightsProtocolArgumentsConfig] = desert.field(
        fields.Nested(desert.schema_class(InSiteInsightsProtocolArgumentsConfig)),
        default=InSiteInsightsProtocolArgumentsConfig(),
    )
