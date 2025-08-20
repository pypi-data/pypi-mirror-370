"""Config YAML specification classes related to pods/datasource configuration."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import logging
import os
from pathlib import Path
from typing import Mapping, Optional, Union

import desert
from marshmallow import ValidationError, fields, validate
from marshmallow.validate import OneOf
from marshmallow_union import Union as M_Union

from bitfount.config import (
    _DEVELOPMENT_ENVIRONMENT,
    _SANDBOX_ENVIRONMENT,
    _STAGING_ENVIRONMENT,
    _get_environment,
)
from bitfount.data.datasources.types import Date
from bitfount.data.types import DataPathModifiers, DataSourceType, SingleOrMulti
from bitfount.externals.general.authentication import ExternallyManagedJWT
from bitfount.federated.helper import POD_NAME_REGEX, USERNAME_REGEX
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.federated.transport.config import (
    _DEV_MESSAGE_SERVICE_PORT,
    _DEV_MESSAGE_SERVICE_TLS,
    _DEV_MESSAGE_SERVICE_URL,
    _SANDBOX_MESSAGE_SERVICE_URL,
    _STAGING_MESSAGE_SERVICE_URL,
    MessageServiceConfig,
)
from bitfount.hub.authentication_handlers import _DEFAULT_USERNAME
from bitfount.hub.types import (
    _DEV_AM_URL,
    _DEV_HUB_URL,
    _SANDBOX_AM_URL,
    _SANDBOX_HUB_URL,
    _STAGING_AM_URL,
    _STAGING_HUB_URL,
)
from bitfount.runners.config_schemas.arg_schemas import (
    CSVSourceArgs,
    DICOMOphthalmologySourceArgs,
    DICOMSourceArgs,
    HeidelbergSourceArgs,
    ImageSourceArgs,
    OMOPSourceArgs,
)
from bitfount.runners.config_schemas.common_schemas import (
    _DEFAULT_YAML_VERSION,
    DataSplitConfig,
    FilePath,
    SecretsUse,
)
from bitfount.runners.config_schemas.hub_schemas import (
    AccessManagerConfig,
    APIKeys,
    HubConfig,
)
from bitfount.runners.config_schemas.utils import (
    keep_desert_output_as_dict,
)
from bitfount.types import _JSONDict

_logger = logging.getLogger(__name__)


@dataclass
class FileSystemFilterConfig:
    """Filter files based on various criteria.

    Args:
        file_extension: File extension(s) of the data files. If None, all files
            will be searched. Can either be a single file extension or a list of
            file extensions. Case-insensitive. Defaults to None.
        strict_file_extension: Whether File loading should be strictly done on files
            with the explicit file extension provided. If set to True will only load
            those files in the dataset. Otherwise, it will scan the given path
            for files of the same type as the provided file extension. Only
            relevant if `file_extension` is provided. Defaults to False.
        file_creation_min_date: The oldest possible date to consider for file
            creation. If None, this filter will not be applied. Defaults to None.
        file_modification_min_date: The oldest possible date to consider for file
            modification. If None, this filter will not be applied. Defaults to None.
        file_creation_max_date: The newest possible date to consider for file
            creation. If None, this filter will not be applied. Defaults to None.
        file_modification_max_date: The newest possible date to consider for file
            modification. If None, this filter will not be applied. Defaults to None.
        min_file_size: The minimum file size in megabytes to consider. If None, all
            files will be considered. Defaults to None.
        max_file_size: The maximum file size in megabytes to consider. If None, all
            files will be considered. Defaults to None.
    """

    file_extension: Optional[SingleOrMulti[str]] = desert.field(
        M_Union(
            [
                fields.String(),
                fields.List(fields.String()),
            ],
            allow_none=True,
        ),
        default=None,
    )
    strict_file_extension: bool = desert.field(
        fields.Bool(allow_none=True), default=False
    )
    file_creation_min_date: Optional[Date] = desert.field(
        fields.Nested(desert.schema_class(Date), allow_none=True),
        default=None,
    )
    file_modification_min_date: Optional[Date] = desert.field(
        fields.Nested(desert.schema_class(Date), allow_none=True),
        default=None,
    )
    file_creation_max_date: Optional[Date] = desert.field(
        fields.Nested(desert.schema_class(Date), allow_none=True),
        default=None,
    )
    file_modification_max_date: Optional[Date] = desert.field(
        fields.Nested(desert.schema_class(Date), allow_none=True),
        default=None,
    )
    min_file_size: Optional[float] = desert.field(
        fields.Float(allow_none=True), default=None
    )
    max_file_size: Optional[float] = desert.field(
        fields.Float(allow_none=True), default=None
    )


@dataclass
class PodDataConfig:
    """Configuration for the Schema, BaseSource and Pod.

    Args:
        force_stypes: The semantic types to force for the data. Can either be:
            - A mapping from pod name to type-to-column mapping
              (e.g. `{"pod_name": {"categorical": ["col1", "col2"]}}`).
            - A direct mapping from type to column names
              (e.g. `{"categorical": ["col1", "col2"]}`).
        ignore_cols: The columns to ignore. This is passed to the data source.
        modifiers: The modifiers to apply to the data. This is passed to the
            `BaseSource`.
        datasource_args: Key-value pairs of arguments to pass to the data source
            constructor.
        data_split: The data split configuration. This is passed to the data source.
        auto_tidy: Whether to automatically tidy the data. This is used by the
            `Pod` and will result in removal of NaNs and normalisation of numeric
            values. Defaults to False.
        file_system_filters: Filter files based on various criteria for datasources that
            are `FileSystemIterable`. Defaults to None.
    """

    force_stypes: Optional[dict] = desert.field(
        fields.Raw(validate=lambda data: isinstance(data, (dict, defaultdict))),
        default=None,
    )
    column_descriptions: Optional[
        Union[Mapping[str, Mapping[str, str]], Mapping[str, str]]
    ] = desert.field(
        fields.Dict(
            keys=fields.String(),
            values=M_Union(
                [
                    fields.Dict(keys=fields.String(), values=fields.String()),
                    fields.String(),
                ]
            ),
            allow_none=True,
        ),
        default=None,
    )
    table_descriptions: Optional[Mapping[str, str]] = desert.field(
        fields.Dict(keys=fields.String(), values=fields.String(), default=None),
        default=None,
    )
    description: Optional[str] = desert.field(
        fields.String(),
        default=None,
    )
    ignore_cols: Optional[Union[list[str], Mapping[str, list[str]]]] = desert.field(
        M_Union(
            [
                fields.List(fields.String()),
                fields.Dict(
                    keys=fields.String(),
                    values=fields.List(fields.String()),
                ),
            ],
            allow_none=True,
        ),
        default=None,
    )
    modifiers: Optional[dict[str, DataPathModifiers]] = desert.field(
        fields.Dict(
            keys=fields.Str,
            values=fields.Dict(
                keys=fields.String(
                    validate=OneOf(DataPathModifiers.__annotations__.keys())
                )
            ),
            default=None,
        ),
        default=None,
    )
    # noinspection PyDataclass
    datasource_args: _JSONDict = desert.field(
        M_Union(
            [
                fields.Nested(
                    keep_desert_output_as_dict(desert.schema_class(CSVSourceArgs))
                ),
                fields.Nested(
                    keep_desert_output_as_dict(desert.schema_class(DICOMSourceArgs))
                ),
                fields.Nested(
                    keep_desert_output_as_dict(
                        desert.schema_class(DICOMOphthalmologySourceArgs)
                    )
                ),
                fields.Nested(
                    keep_desert_output_as_dict(
                        desert.schema_class(HeidelbergSourceArgs)
                    )
                ),
                fields.Nested(
                    keep_desert_output_as_dict(desert.schema_class(ImageSourceArgs))
                ),
                fields.Nested(
                    keep_desert_output_as_dict(desert.schema_class(OMOPSourceArgs))
                ),
            ]
        ),
        default_factory=dict,
    )
    data_split: Optional[DataSplitConfig] = desert.field(
        fields.Nested(desert.schema_class(DataSplitConfig)),
        default=None,
    )
    auto_tidy: bool = False
    file_system_filters: Optional[FileSystemFilterConfig] = desert.field(
        fields.Nested(desert.schema_class(FileSystemFilterConfig), allow_none=True),
        default=None,
    )


@dataclass
class PodDetailsConfig:
    """Configuration for the pod details.

    Args:
        display_name: The display name of the pod.
        description: The description of the pod.
    """

    display_name: str
    description: str = ""


@dataclass
class DatasourceConfig:
    """Datasource configuration for a multi-datasource Pod."""

    datasource: str
    name: str = desert.field(fields.String(validate=validate.Regexp(POD_NAME_REGEX)))
    data_config: PodDataConfig = desert.field(
        fields.Nested(desert.schema_class(PodDataConfig)),
        default_factory=PodDataConfig,
    )
    datasource_details_config: Optional[PodDetailsConfig] = desert.field(
        fields.Nested(desert.schema_class(PodDetailsConfig)),
        default=None,
    )
    schema: Optional[Path] = desert.field(FilePath(allow_none=True), default=None)

    def __post_init__(self) -> None:
        """Check that file system filters are provided for appropriate datasources."""
        if self.data_config.file_system_filters is not None:
            supported_datasources = [
                # TODO: [BIT-6091] Change `i.name` to `i.value` when the switch is made
                # enforce the `bitfount.` prefix in the datasource name
                i.name
                for i in (
                    DataSourceType.HeidelbergSource,
                    DataSourceType.DICOMOphthalmologySource,
                    DataSourceType.DICOMSource,
                    DataSourceType.ImageSource,
                )
            ]
            if self.datasource not in supported_datasources:
                raise ValidationError(
                    f"File system filters can only be provided for FileSystemIterable "
                    f"datasources ({', '.join(supported_datasources)});"
                    f" got {self.datasource}"
                )


@dataclass
class PodDbConfig:
    """Configuration of the Pod DB."""

    path: Path = desert.field(FilePath())


@dataclass
class PodConfig:
    """Full configuration for the pod.

    Raises:
        ValueError: If a username is not provided alongside API keys.
    """

    name: str = desert.field(fields.String(validate=validate.Regexp(POD_NAME_REGEX)))

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
    pod_details_config: Optional[PodDetailsConfig] = None
    datasource: Optional[str] = desert.field(fields.String(), default=None)
    data_config: Optional[PodDataConfig] = desert.field(
        fields.Nested(desert.schema_class(PodDataConfig)),
        default=None,
    )
    schema: Optional[Path] = desert.field(FilePath(allow_none=True), default=None)
    datasources: Optional[list[DatasourceConfig]] = desert.field(
        fields.List(fields.Nested(desert.schema_class(DatasourceConfig))),
        default=None,
    )
    access_manager: AccessManagerConfig = desert.field(
        fields.Nested(desert.schema_class(AccessManagerConfig)),
        default_factory=AccessManagerConfig,
    )
    hub: HubConfig = desert.field(
        fields.Nested(desert.schema_class(HubConfig)), default_factory=HubConfig
    )
    message_service: MessageServiceConfig = desert.field(
        fields.Nested(desert.schema_class(MessageServiceConfig)),
        default_factory=MessageServiceConfig,
    )
    differential_privacy: Optional[DPPodConfig] = None
    approved_pods: Optional[list[str]] = None
    username: str = desert.field(
        fields.String(validate=validate.Regexp(USERNAME_REGEX)),
        default=_DEFAULT_USERNAME,
    )
    update_schema: bool = False
    pod_db: Union[bool, PodDbConfig] = False
    # This is kept for backwards compatibility but is not used
    show_datapoints_with_results_in_db: bool = True
    version: Optional[str] = None

    def __post_init__(self) -> None:
        environment = _get_environment()
        if environment == _STAGING_ENVIRONMENT:
            _logger.warning(f"{environment=} detected; changing URLs in config")
            self.hub.url = _STAGING_HUB_URL
            self.access_manager.url = _STAGING_AM_URL
            self.message_service.url = _STAGING_MESSAGE_SERVICE_URL
        elif environment == _DEVELOPMENT_ENVIRONMENT:
            _logger.warning(
                f"{environment=} detected; changing URLs and ports in config"
            )
            self.hub.url = _DEV_HUB_URL
            self.access_manager.url = _DEV_AM_URL
            self.message_service.url = _DEV_MESSAGE_SERVICE_URL
            self.message_service.port = _DEV_MESSAGE_SERVICE_PORT
            self.message_service.tls = _DEV_MESSAGE_SERVICE_TLS
        elif environment == _SANDBOX_ENVIRONMENT:
            _logger.warning(f"{environment=} detected; changing URLs in config")
            self.hub.url = _SANDBOX_HUB_URL
            self.access_manager.url = _SANDBOX_AM_URL
            self.message_service.url = _SANDBOX_MESSAGE_SERVICE_URL
        if self.version is None:
            self.version = _DEFAULT_YAML_VERSION
        _logger.info(f"Current pod config version is {self.version}.")
        # datasource xor datasources must be defined
        if (self.datasource is None) == (self.datasources is None):
            raise ValueError(
                "You must either supply a datasource or a set of datasources"
            )

        # Use API Keys for authentication if provided
        if isinstance(self.secrets, APIKeys):
            if self.username == _DEFAULT_USERNAME:
                raise ValueError("Must specify a username when using API Keys.")

            _logger.info("Setting API Keys as environment variables.")

            if os.environ.get("BITFOUNT_API_KEY_ID") or os.environ.get(
                "BITFOUNT_API_KEY"
            ):
                _logger.warning(
                    "Existing environment variable API keys detected. Overriding with "
                    "those provided in the pod config."
                )
            os.environ["BITFOUNT_API_KEY_ID"] = self.secrets.access_key_id
            os.environ["BITFOUNT_API_KEY"] = self.secrets.access_key

    @property
    def pod_id(self) -> str:
        """The pod ID of the pod specified."""
        return f"{self.username}/{self.name}"
