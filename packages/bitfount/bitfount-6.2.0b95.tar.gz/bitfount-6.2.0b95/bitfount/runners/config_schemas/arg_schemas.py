"""Schemas which correspond to sets of args/kwargs for other classes.

This is most important for classes where they cannot be directly represented as
schemas (for instance if they are not dataclasses themselves and so we cannot use
`desert`) OR where we wish to have a tighter allowed range in the YAML configs than
is actually allowed by the class __init__() method.

In particular, many of these classes are designed to avoid a bare dict as the only
typing within the schemas for a "kwargs" entry.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Optional, Sequence, Union

import desert
from marshmallow import fields, validate
from marshmallow_union import Union as M_Union

from bitfount import config
from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
    FileSystemIterableSourceInferrable,
)
from bitfount.data.datasources.csv_source import CSVSource
from bitfount.data.datasources.dicom_source import DICOMSource
from bitfount.data.datasources.image_source import ImageSource
from bitfount.data.datasources.ophthalmology.dicom_ophthalmology_source import (
    DICOMOphthalmologyCSVColumns,
    DICOMOphthalmologySource,
)
from bitfount.data.datasources.ophthalmology.heidelberg_source import (
    HeidelbergCSVColumns,
    HeidelbergSource,
)
from bitfount.data.datasources.ophthalmology.ophthalmology_base_source import (
    OphthalmologyDataSourceArgs,
    _OphthalmologySource,
)
from bitfount.data.datasources.ophthalmology.private_eye_base_source import (
    _PrivateEyeSource,
)
from bitfount.data.datasources.sql_source import OMOPSource
from bitfount.runners.config_schemas.common_schemas import FilePath


@dataclass(kw_only=True)
class _BaseAdditionalArgs:
    """Base args/kwargs dataclass.

    Lists the ClassVar fields that each child class should have, for testing purposes.
    """

    _corresponds_to: ClassVar[type]
    _ignored: ClassVar[list[str]]


################################
# DataSource Arg/Kwarg Classes #
################################
@dataclass(kw_only=True)
class _BaseSourceArgs(_BaseAdditionalArgs):
    """Args dataclass for the BaseSource's args."""

    _corresponds_to: ClassVar[type] = BaseSource
    _ignored: ClassVar[list[str]] = [
        # Deprecated/handled separately in the root PodDataConfig
        "data_splitter",
        # Handled separately in the root PodDataConfig
        "modifiers",
    ]

    # IGNORED: data_splitter: Optional[DatasetSplitter] = None
    seed: Optional[int] = None
    ignore_cols: Optional[Union[str, Sequence[str]]] = desert.field(
        M_Union(
            [
                fields.String(),
                fields.List(fields.String()),
            ],
            allow_none=True,
        ),
        default=None,
    )
    # iterable is deprecated and should only accept True
    iterable: bool = desert.field(
        fields.Boolean(validate=validate.Equal(True)), default=True
    )
    # IGNORED: modifiers: Optional[dict[str, DataPathModifiers]] = None
    partition_size: int = config.settings.task_batch_size
    required_fields: Optional[dict[str, Any]] = None


@dataclass(kw_only=True)
class _FileSystemIterableSourceArgs(_BaseSourceArgs):
    """Args dataclass for the FileSystemIterableSource's args."""

    _corresponds_to: ClassVar[type] = FileSystemIterableSource
    _ignored: ClassVar[list[str]] = [
        # Handled separately in the root PodDataConfig
        "filter",
    ]

    path: Path = desert.field(FilePath())
    output_path: Optional[Path] = desert.field(FilePath(allow_none=True), default=None)
    # iterable is already handled in the parent args class
    # HANDLED IN PARENT DATACLASS iterable: bool = True
    # fast_load is deprecated and should only accept True
    fast_load: bool = desert.field(
        fields.Boolean(validate=validate.Equal(True)), default=True
    )
    # cache_images is deprecated and should only accept False
    cache_images: bool = desert.field(
        fields.Boolean(validate=validate.Equal(False)), default=False
    )
    # IGNORED: filter: Optional[FileSystemFilter] = None


@dataclass(kw_only=True)
class _FileSystemIterableSourceInferrableArgs(_FileSystemIterableSourceArgs):
    """Args dataclass for the FileSystemIterableSourceInferrable source's args."""

    _corresponds_to: ClassVar[type] = FileSystemIterableSourceInferrable
    _ignored: ClassVar[list[str]] = [
        # Handled separately in the Pod Runner loading scripts
        "data_cache"
    ]

    # HANDLED IN PARENT DATACLASS path: Union[os.PathLike, str]
    # IGNORED: data_cache: Optional[DataPersister] = None
    infer_class_labels_from_filepaths: bool = False


@dataclass(kw_only=True)
class _OphthalmologySourceArgs(_FileSystemIterableSourceInferrableArgs):
    """Args dataclass for the OphthalmologySource's args."""

    _corresponds_to: ClassVar[type] = _OphthalmologySource
    _ignored: ClassVar[list[str]] = []

    # HANDLED IN PARENT DATACLASS path: Union[str, os.PathLike]
    ophthalmology_args: Optional[OphthalmologyDataSourceArgs] = desert.field(
        fields.Nested(
            desert.schema_class(OphthalmologyDataSourceArgs), allow_none=True
        ),
        default=None,
    )


@dataclass(kw_only=True)
class _PrivateEyeSourceArgs(_OphthalmologySourceArgs):
    """Args dataclass for the PrivateEyeSource's args."""

    _corresponds_to: ClassVar[type] = _PrivateEyeSource
    _ignored: ClassVar[list[str]] = [
        # Not exposed via YAML
        "private_eye_parser"
    ]

    # HANDLED IN PARENT DATACLASS path: Union[str, os.PathLike]
    # IGNORED: private_eye_parser: Union[PrivateEyeParser, Mapping[str, PrivateEyeParser]] # noqa: E501


@dataclass(kw_only=True)
class CSVSourceArgs(_BaseSourceArgs):
    """Args dataclass for the CSVSource's args."""

    _corresponds_to: ClassVar[type] = CSVSource
    _ignored: ClassVar[list[str]] = []

    # Actually `path: Union[os.PathLike, AnyUrl, str]`
    path: Path = desert.field(FilePath())
    read_csv_kwargs: Optional[dict[str, Any]] = None
    # HANDLED IN PARENT DATACLASS modifiers: Optional[dict[str, DataPathModifiers]] = None # noqa: E501


@dataclass(kw_only=True)
class DICOMSourceArgs(_FileSystemIterableSourceInferrableArgs):
    """Args dataclass for the DICOMSource's args."""

    _corresponds_to: ClassVar[type] = DICOMSource
    _ignored: ClassVar[list[str]] = []

    # HANDLED IN PARENT DATACLASS path: Union[os.PathLike, str]
    images_only: bool = True


@dataclass(kw_only=True)
class DICOMOphthalmologySourceArgs(DICOMSourceArgs, _OphthalmologySourceArgs):
    """Args dataclass for the DICOMOphthalmologySource's args."""

    _corresponds_to: ClassVar[type] = DICOMOphthalmologySource
    _ignored: ClassVar[list[str]] = []

    # HANDLED IN PARENT DATACLASS path: Union[os.PathLike, str]
    dicom_ophthalmology_csv_columns: Optional[DICOMOphthalmologyCSVColumns] = (
        desert.field(
            fields.Nested(
                desert.schema_class(DICOMOphthalmologyCSVColumns), allow_none=True
            ),
            default=None,
        )
    )
    # HANDLED IN PARENT DATACLASS required_fields: Optional[dict[str, Any]] = None


@dataclass(kw_only=True)
class HeidelbergSourceArgs(_PrivateEyeSourceArgs):
    """Args dataclass for the HeidelbergSource's args."""

    _corresponds_to: ClassVar[type] = HeidelbergSource
    _ignored: ClassVar[list[str]] = [
        # Not exposed via YAML
        "parsers"
    ]

    # HANDLED IN PARENT DATACLASS path: Union[os.PathLike, str]
    # IGNORED: parsers: Optional[Union[PrivateEyeParser, Mapping[str, PrivateEyeParser]]] = None # noqa: E501
    heidelberg_csv_columns: Optional[HeidelbergCSVColumns] = desert.field(
        fields.Nested(desert.schema_class(HeidelbergCSVColumns), allow_none=True),
        default=None,
    )
    # HANDLED IN PARENT DATACLASS required_fields: Optional[dict[str, Any]] = None


@dataclass(kw_only=True)
class ImageSourceArgs(_FileSystemIterableSourceInferrableArgs):
    """Args dataclass for the HeidelbergSource's args."""

    _corresponds_to: ClassVar[type] = ImageSource
    _ignored: ClassVar[list[str]] = []

    # HANDLED IN PARENT DATACLASS path: Union[os.PathLike, str]
    file_extensions: list[str] = desert.field(
        fields.List(fields.String(), allow_none=True), default=None
    )


@dataclass(kw_only=True)
class OMOPSourceArgs(_BaseSourceArgs):
    """Args dataclass for the OMOPSource's args."""

    _corresponds_to: ClassVar[type] = OMOPSource
    _ignored: ClassVar[list[str]] = []

    connection_string: str
    version: str = desert.field(
        fields.String(validate=validate.OneOf(["v3.0", "v5.3", "v5.4"]))
    )
    read_sql_kwargs: Optional[dict[str, Any]] = None


#####################################
# End: DataSource Arg/Kwarg Classes #
#####################################
