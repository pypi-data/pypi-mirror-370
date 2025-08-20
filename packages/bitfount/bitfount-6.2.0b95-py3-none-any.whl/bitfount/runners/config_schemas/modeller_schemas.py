"""Config YAML specification classes related to modeller/task configuration."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Mapping, Optional, Union

import desert
from marshmallow import ValidationError, fields, validate
from marshmallow.validate import OneOf
from marshmallow_union import Union as M_Union

from bitfount import config
from bitfount.config import (
    _DEVELOPMENT_ENVIRONMENT,
    _SANDBOX_ENVIRONMENT,
    _STAGING_ENVIRONMENT,
    _get_environment,
)
from bitfount.data.datastructure import (
    COMPATIBLE_DATASOURCES,
    SCHEMA_REQUIREMENTS_TYPES,
)
from bitfount.data.types import DataSourceType, SchemaOverrideMapping
from bitfount.externals.general.authentication import ExternallyManagedJWT
from bitfount.federated.authorisation_checkers import (
    DEFAULT_IDENTITY_VERIFICATION_METHOD,
    IDENTITY_VERIFICATION_METHODS,
)
from bitfount.federated.helper import USERNAME_REGEX
from bitfount.federated.transport.config import (
    _DEV_MESSAGE_SERVICE_PORT,
    _DEV_MESSAGE_SERVICE_TLS,
    _DEV_MESSAGE_SERVICE_URL,
    _SANDBOX_MESSAGE_SERVICE_URL,
    _STAGING_MESSAGE_SERVICE_URL,
    MessageServiceConfig,
)
from bitfount.federated.types import AlgorithmType
from bitfount.hub.authentication_handlers import _DEFAULT_USERNAME
from bitfount.hub.types import (
    _DEV_HUB_URL,
    _DEV_IDP_URL,
    _PRODUCTION_IDP_URL,
    _SANDBOX_HUB_URL,
    _SANDBOX_IDP_URL,
    _STAGING_HUB_URL,
    _STAGING_IDP_URL,
)
from bitfount.runners.config_schemas.algorithm_schemas import (
    AggregatorConfig,
    AlgorithmConfig,
)
from bitfount.runners.config_schemas.common_schemas import (
    _DEFAULT_YAML_VERSION,
    DataSplitConfig,
    FilePath,
    SecretsUse,
)
from bitfount.runners.config_schemas.hub_schemas import (
    APIKeys,
    HubConfig,
)
from bitfount.runners.config_schemas.protocol_schemas import ProtocolConfig
from bitfount.runners.config_schemas.template_variable_schemas import (
    TemplatesMixin,
)
from bitfount.types import _JSONDict

_logger = logging.getLogger(__name__)


@dataclass
class ModellerUserConfig:
    """Configuration for the modeller.

    Args:
        username: The username of the modeller. This can be picked up automatically
            from the session but can be overridden here.
        identity_verification_method: The method to use for identity verification.
            Accepts one of the values in `IDENTITY_VERIFICATION_METHODS`, i.e. one of
            `key-based`, `oidc-auth-code` or `oidc-device-code`.
        private_key_file: The path to the private key file for key-based identity
            verification.
    """

    username: str = desert.field(
        fields.String(validate=validate.Regexp(USERNAME_REGEX)),
        default=_DEFAULT_USERNAME,
    )

    identity_verification_method: str = desert.field(
        fields.String(validate=OneOf(IDENTITY_VERIFICATION_METHODS)),
        default=DEFAULT_IDENTITY_VERIFICATION_METHOD,
    )
    private_key_file: Optional[Path] = desert.field(
        FilePath(allow_none=True), default=None
    )

    def __post_init__(self) -> None:
        environment = _get_environment()
        self._identity_provider_url: str

        if environment == _STAGING_ENVIRONMENT:
            self._identity_provider_url = _STAGING_IDP_URL
        elif environment == _DEVELOPMENT_ENVIRONMENT:
            self._identity_provider_url = _DEV_IDP_URL
        elif environment == _SANDBOX_ENVIRONMENT:
            self._identity_provider_url = _SANDBOX_IDP_URL
        else:
            self._identity_provider_url = _PRODUCTION_IDP_URL


@dataclass
class PodsConfig:
    """Configuration for the pods to use for the modeller."""

    identifiers: list[str]


@dataclass
class TaskConfig:
    """Configuration for the task."""

    protocol: Union[ProtocolConfig._get_subclasses()]  # type: ignore[valid-type] # reason: no dynamic typing # noqa: E501
    # NOTE: Union[AlgorithmConfig._get_subclasses()] cannot be
    # replaced with a TypeAlias here without breaking the dynamic subtyping
    algorithm: Union[  # type: ignore[valid-type] # reason: no dynamic typing # noqa: E501
        Union[AlgorithmConfig._get_subclasses()],
        list[Union[AlgorithmConfig._get_subclasses()]],
    ]
    data_structure: DataStructureConfig
    aggregator: Optional[AggregatorConfig] = None
    transformation_file: Optional[Path] = desert.field(
        FilePath(allow_none=True), default=None
    )
    primary_results_path: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate that the data structure is appropriate for the given algorithms.

        In particular, the datastructure selected columns should only have one column
        for HuggingFace/TIMM algorithms since those algorithms only support single
        column inputs.
        """
        huggingface_inference_algorithms = {
            AlgorithmType.HuggingFaceImageClassificationInference,
            AlgorithmType.HuggingFaceImageSegmentationInference,
            AlgorithmType.HuggingFacePerplexityEvaluation,
            AlgorithmType.HuggingFaceTextClassificationInference,
            AlgorithmType.HuggingFaceTextGenerationInference,
            AlgorithmType.TIMMInference,
        }
        selected_columns = self.data_structure.select.include

        self.algorithms: list[AlgorithmConfig] = (
            self.algorithm if isinstance(self.algorithm, list) else [self.algorithm]
        )
        if any(
            algorithm.name
            in list(map(lambda x: x.value, huggingface_inference_algorithms))
            for algorithm in self.algorithms
            if algorithm
        ):
            if selected_columns is None or len(selected_columns) != 1:
                raise ValidationError(
                    "Datastructure selected columns should only have one column for "
                    "HuggingFace inference algorithms."
                )


@dataclass
class DataStructureSelectConfig:
    """Configuration for the datastructure select argument."""

    include: Optional[list[str]] = desert.field(
        fields.List(fields.String(), allow_none=True), default=None
    )
    include_prefix: Optional[str] = desert.field(
        fields.String(allow_none=True),
        default=None,
    )
    exclude: Optional[list[str]] = desert.field(
        fields.List(fields.String(), allow_none=True), default=None
    )


@dataclass
class DataStructureAssignConfig:
    """Configuration for the datastructure assign argument."""

    target: Optional[Union[str, list[str]]] = desert.field(
        M_Union(
            [
                fields.String(),
                fields.List(fields.String()),
            ],
            allow_none=True,
        ),
        default=None,
    )
    image_cols: Optional[list[str]] = None
    image_prefix: Optional[str] = None


@dataclass
class DataStructureTransformConfig:
    """Configuration for the datastructure transform argument."""

    dataset: Optional[list[dict[str, _JSONDict]]] = None
    batch: Optional[list[dict[str, _JSONDict]]] = None
    image: Optional[list[dict[str, _JSONDict]]] = None
    auto_convert_grayscale_images: bool = True


@dataclass
class DataStructureTableConfig:
    """Configuration for the datastructure table arguments. Deprecated."""  # noqa: E501

    table: Union[str, dict[str, str]] = desert.field(
        M_Union(
            [
                fields.String(),
                fields.Dict(keys=fields.String(), values=fields.String(), default=None),
            ],
        ),
    )
    schema_types_override: Optional[
        Union[SchemaOverrideMapping, Mapping[str, SchemaOverrideMapping]]
    ] = desert.field(
        fields.Dict(
            keys=fields.String(),
            values=fields.List(M_Union([fields.String(), fields.Dict()])),
            default=None,
            allow_none=True,
        ),
        default=None,
    )


@dataclass
class DataStructureConfig:
    """Configuration for the modeller schema and dataset options."""

    table_config: Optional[DataStructureTableConfig] = desert.field(
        fields.Nested(desert.schema_class(DataStructureTableConfig), allow_none=True),
        default=None,
    )
    assign: DataStructureAssignConfig = desert.field(
        fields.Nested(desert.schema_class(DataStructureAssignConfig)),
        default_factory=DataStructureAssignConfig,
    )
    select: DataStructureSelectConfig = desert.field(
        fields.Nested(desert.schema_class(DataStructureSelectConfig)),
        default_factory=DataStructureSelectConfig,
    )
    transform: DataStructureTransformConfig = desert.field(
        fields.Nested(desert.schema_class(DataStructureTransformConfig)),
        default_factory=DataStructureTransformConfig,
    )
    data_split: Optional[DataSplitConfig] = desert.field(
        fields.Nested(desert.schema_class(DataSplitConfig)),
        default=None,
    )
    schema_requirements: SCHEMA_REQUIREMENTS_TYPES = desert.field(
        M_Union(
            [
                fields.String(validate=OneOf(["empty", "partial", "full"])),
                fields.Dict(
                    keys=fields.String(validate=OneOf(["empty", "partial", "full"])),
                    values=fields.List(
                        fields.String,  # Specify the type of elements in the list
                        validate=validate.ContainsOnly(
                            [ds_type.name for ds_type in DataSourceType]
                        ),
                    ),
                ),
            ]
        ),
        default="partial",
    )
    compatible_datasources: list[str] = desert.field(
        fields.List(fields.String()), default_factory=lambda: COMPATIBLE_DATASOURCES
    )


@dataclass
class ModellerConfig:
    """Full configuration for the modeller."""

    pods: PodsConfig
    task: TaskConfig
    # `secrets` can be either a single authentication object (APIKeys or
    # ExternallyManagedJWT) which is the secret for "bitfount" authentication. or a
    # dict of what the secret is for to the secrets for that use.
    #
    # `secrets = X` and `secrets = {"bitfount": X}` are equivalent.
    secrets: Optional[
        APIKeys
        | ExternallyManagedJWT
        | dict[SecretsUse, APIKeys | ExternallyManagedJWT]
    ] = desert.field(
        M_Union(
            [
                fields.Nested(desert.schema_class(APIKeys)),
                # Note: It is not possible to supply the JWT via the YAML as it
                #       requires a Callable, which cannot be serialized.
                fields.Dict(
                    keys=fields.String(validate=validate.OneOf(("bitfount", "ehr"))),
                    values=M_Union(
                        [
                            fields.Nested(desert.schema_class(APIKeys)),
                            # Note: It is not possible to supply the JWT via the YAML
                            #       as it requires a Callable, which cannot be
                            #       serialized.
                        ]
                    ),
                ),
            ],
            allow_none=True,
        ),
        default=None,
    )
    modeller: ModellerUserConfig = desert.field(
        fields.Nested(desert.schema_class(ModellerUserConfig)),
        default_factory=ModellerUserConfig,
    )
    hub: HubConfig = desert.field(
        fields.Nested(desert.schema_class(HubConfig)), default_factory=HubConfig
    )
    message_service: MessageServiceConfig = desert.field(
        fields.Nested(desert.schema_class(MessageServiceConfig)),
        default_factory=MessageServiceConfig,
    )
    version: Optional[str] = None
    project_id: Optional[str] = None
    run_on_new_data_only: bool = False
    batched_execution: Optional[bool] = None
    test_run: bool = False
    force_rerun_failed_files: bool = True

    def __post_init__(self) -> None:
        environment = _get_environment()
        if environment == _STAGING_ENVIRONMENT:
            self.hub.url = _STAGING_HUB_URL
            self.message_service.url = _STAGING_MESSAGE_SERVICE_URL
        elif environment == _DEVELOPMENT_ENVIRONMENT:
            self.hub.url = _DEV_HUB_URL
            self.message_service.url = _DEV_MESSAGE_SERVICE_URL
            self.message_service.port = _DEV_MESSAGE_SERVICE_PORT
            self.message_service.tls = _DEV_MESSAGE_SERVICE_TLS
        elif environment == _SANDBOX_ENVIRONMENT:
            self.hub.url = _SANDBOX_HUB_URL
            self.message_service.url = _SANDBOX_MESSAGE_SERVICE_URL
        if self.batched_execution is None:
            self.batched_execution = config.settings.default_batched_execution
        if self.version is None:
            self.version = _DEFAULT_YAML_VERSION


@dataclass
class TemplatedModellerConfig(TemplatesMixin, ModellerConfig):
    """Schema for task templates."""

    pass
