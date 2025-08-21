"""Config YAML specification classes that are common to multiple other uses."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Literal, Optional, Union

import desert
from marshmallow import fields
from marshmallow.validate import OneOf
from marshmallow_union import Union as M_Union

from bitfount.data.datasplitters import PercentageSplitter, SplitterDefinedInData
from bitfount.runners.config_schemas.utils import (
    _deserialize_model_ref,
    _deserialize_path,
    keep_desert_output_as_dict,
)
from bitfount.types import _JSONDict

_DEFAULT_YAML_VERSION: Final[str] = "1.0.0"  # Default version is `1.0.0`
# so that unversioned yamls are still compatible with this version


@dataclass
class DataSplitConfig:
    """Configuration for the data splitter."""

    data_splitter: str = desert.field(
        fields.String(validate=OneOf(["percentage", "predefined"])),
        default="percentage",
    )
    # noinspection PyDataclass
    args: _JSONDict = desert.field(
        M_Union(
            [
                fields.Nested(
                    keep_desert_output_as_dict(desert.schema_class(PercentageSplitter))
                ),
                fields.Nested(
                    keep_desert_output_as_dict(
                        desert.schema_class(SplitterDefinedInData)
                    )
                ),
            ]
        ),
        default_factory=dict,
    )


class FilePath(fields.Field):
    """Field for representing file paths.

    Serializes to a string representation of the path and deserializes to a Python
    pathlib representation.
    """

    default_error_messages = {
        "invalid_path": 'Not a valid path; got "{invalid_type}"',
        "input_type": '"str" input type required, got "{input_type}"',
    }

    def _serialize(
        self, value: Any, attr: str | None, obj: Any, **kwargs: Any
    ) -> Optional[str]:
        """Take an Optional[Path] and convert to an absolute str-repr."""
        if value is None:
            return None
        if not isinstance(value, Path):
            raise self.make_error("invalid_path", invalid_type=str(type(value)))
        return str(value.expanduser().resolve())

    def _deserialize(
        self,
        value: Any,
        attr: str | None,
        data: Mapping[str, Any] | None,
        **kwargs: Any,
    ) -> Optional[Path]:
        """Take a str-repr path and convert to an absolute Path-repr."""
        if value is None:
            return None
        elif not isinstance(value, str):
            raise self.make_error("input_type", input_type=str(type(value)))
        else:
            return _deserialize_path(value, self.context)


class ModelReference(fields.Field):
    """Field for representing model references.

    If the reference is a path to a file (and that file exists), deserializes a Path
    instance. Otherwise, deserializes the str reference unchanged.

    Serializes both path and str to string.
    """

    default_error_messages = {
        "output_type": 'Not a valid "str" or path; got "{invalid_type}"',
        "input_type": '"str" input type required, got "{input_type}"',
    }

    def _serialize(
        self, value: Any, attr: str | None, obj: Any, **kwargs: Any
    ) -> Optional[str]:
        """Serialize a model reference.

        If the reference is a string, serialize to string.
        If the reference is a path, convert to an absolute str-repr.
        """
        if value is None:
            return None
        if not isinstance(value, (str, Path)):
            raise self.make_error("output_type", invalid_type=str(type(value)))
        if isinstance(value, str):
            return value
        else:
            return str(value.expanduser().resolve())

    def _deserialize(
        self,
        value: Any,
        attr: str | None,
        data: Mapping[str, Any] | None,
        **kwargs: Any,
    ) -> Optional[Union[Path, str]]:
        """Deserialize a model reference.

        If the model reference seems to be a file path (and that file exists)
        deserialize as a Path instance.
        Otherwise deserialize as a string.
        """
        if value is None:
            return None
        elif not isinstance(value, str):
            raise self.make_error("input_type", input_type=str(type(value)))
        else:
            return _deserialize_model_ref(value)


@dataclass
class PathConfig:
    """Configuration for the path."""

    path: Path = desert.field(FilePath())


SecretsUse = Literal["bitfount", "ehr"]
