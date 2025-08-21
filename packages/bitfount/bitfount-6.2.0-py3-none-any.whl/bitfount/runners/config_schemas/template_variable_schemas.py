"""Schemas for entries on the "template" tag of TemplateModellerConfig schemas."""

from dataclasses import dataclass
from typing import Literal, Optional

import desert
from marshmallow import fields
from marshmallow.validate import Equal, OneOf
from marshmallow_union import Union as M_Union

from bitfount.data.types import _SemanticTypeValue


########
# Base #
########
@dataclass(kw_only=True)
class _TemplateVariablesEntryCommon:
    label: str
    tooltip: Optional[str] = None


##########
# String #
##########
@dataclass(kw_only=True)
class TemplateVariablesEntryString(_TemplateVariablesEntryCommon):
    """Represents a "type: string" template variable entry."""

    type: Literal["string"] = desert.field(fields.String(validate=Equal("string")))
    pattern: Optional[str] = None
    default: Optional[str] = None


@dataclass(kw_only=True)
class TemplateVariablesEntryBool(_TemplateVariablesEntryCommon):
    """Represents a "type: string" template variable entry."""

    type: Literal["string"] = desert.field(fields.String(validate=Equal("boolean")))
    default: Optional[bool] = None


##########
# Number #
##########
@dataclass(kw_only=True)
class TemplateVariablesEntryNumber(_TemplateVariablesEntryCommon):
    """Represents a "type: number" template variable entry."""

    type: Literal["number"] = desert.field(fields.String(validate=Equal("number")))
    minimum: Optional[int | float] = desert.field(
        M_Union([fields.Integer(), fields.Float()], allow_none=True),
        default=None,
    )
    default: Optional[int | float] = desert.field(
        M_Union([fields.Integer(), fields.Float()], allow_none=True),
        default=None,
    )


#########
# Array #
#########
@dataclass(kw_only=True)
class _TemplateArrayItemsDetails:
    type: Literal["string"] = desert.field(fields.String(validate=Equal("string")))


@dataclass(kw_only=True)
class TemplateVariablesEntryArray(_TemplateVariablesEntryCommon):
    """Represents a "type: array" template variable entry."""

    type: Literal["array"] = desert.field(fields.String(validate=Equal("array")))
    items: _TemplateArrayItemsDetails = desert.field(
        fields.Nested(desert.schema_class(_TemplateArrayItemsDetails))
    )
    minItems: Optional[int] = None
    default: Optional[list[str]] = None


#############
# File Path #
#############
@dataclass(kw_only=True)
class _TemplateFilePathTypeDetails:
    extension: str


@dataclass(kw_only=True)
class _TemplateFilePathTypeEntry:
    # This template corresponds to a file path with a particular extension
    file_path: _TemplateFilePathTypeDetails = desert.field(
        fields.Nested(desert.schema_class(_TemplateFilePathTypeDetails))
    )


@dataclass(kw_only=True)
class TemplateVariablesEntryFilePath(_TemplateVariablesEntryCommon):
    """Represents a "type: file_path" template variable entry."""

    type: _TemplateFilePathTypeEntry = desert.field(
        fields.Nested(desert.schema_class(_TemplateFilePathTypeEntry))
    )


##############
# Model Slug #
##############
@dataclass(kw_only=True)
class _TemplateModelSlugTypeDetails:
    provider: str
    library: str
    pipeline_tag: Optional[str] = None
    author: Optional[str] = None


@dataclass(kw_only=True)
class _TemplateModelSlugTypeEntry:
    # This template corresponds to a model_id (and provides some
    # additional details to create it from)
    model_slug: _TemplateModelSlugTypeDetails = desert.field(
        fields.Nested(desert.schema_class(_TemplateModelSlugTypeDetails))
    )


@dataclass(kw_only=True)
class TemplateVariablesEntryModelSlug(_TemplateVariablesEntryCommon):
    """Represents a "type: model_slug" template variable entry."""

    type: _TemplateModelSlugTypeEntry = desert.field(
        fields.Nested(desert.schema_class(_TemplateModelSlugTypeEntry))
    )


###################################################
# Schema Column Name and Schema Column Name Array #
###################################################
@dataclass(kw_only=True)
class _TemplateSchemaColumnNameTypeDetails:
    semantic_type: _SemanticTypeValue = desert.field(
        fields.String(validate=OneOf(("categorical", "continuous", "image", "text")))
    )


@dataclass(kw_only=True)
class _TemplateSchemaColumnNameTypeEntry:
    # This template corresponds to a single column name in the schema (and the
    # semantic type to associate it with)
    schema_column_name: _TemplateSchemaColumnNameTypeDetails = desert.field(
        fields.Nested(desert.schema_class(_TemplateSchemaColumnNameTypeDetails))
    )


@dataclass(kw_only=True)
class TemplateVariablesEntrySchemaColumnName(_TemplateVariablesEntryCommon):
    """Represents a "type: schema_column_name" template variable entry."""

    type: _TemplateSchemaColumnNameTypeEntry = desert.field(
        fields.Nested(desert.schema_class(_TemplateSchemaColumnNameTypeEntry))
    )
    default: Optional[str] = None


@dataclass(kw_only=True)
class _TemplateSchemaColumnNameArrayTypeEntry:
    schema_column_name_array: _TemplateSchemaColumnNameTypeDetails = desert.field(
        fields.Nested(desert.schema_class(_TemplateSchemaColumnNameTypeDetails))
    )


@dataclass(kw_only=True)
class TemplateVariablesEntrySchemaColumnNameArray(_TemplateVariablesEntryCommon):
    """Represents a "type: schema_column_name_array" template variable entry."""

    type: _TemplateSchemaColumnNameArrayTypeEntry = desert.field(
        fields.Nested(desert.schema_class(_TemplateSchemaColumnNameArrayTypeEntry))
    )
    default: Optional[list[str]] = None


####################
# Combination Type #
####################
TemplateVariablesEntry = (
    TemplateVariablesEntryString
    | TemplateVariablesEntryNumber
    | TemplateVariablesEntryArray
    | TemplateVariablesEntryFilePath
    | TemplateVariablesEntryModelSlug
    | TemplateVariablesEntrySchemaColumnName
    | TemplateVariablesEntrySchemaColumnNameArray
    | TemplateVariablesEntryBool
)


@dataclass
class TemplatesMixin:
    """Schema for schemas having a `template` field."""

    template: Optional[dict[str, TemplateVariablesEntry]] = desert.field(
        fields.Dict(
            keys=fields.String(),
            values=M_Union(
                [
                    fields.Nested(desert.schema_class(TemplateVariablesEntryString)),
                    fields.Nested(desert.schema_class(TemplateVariablesEntryBool)),
                    fields.Nested(desert.schema_class(TemplateVariablesEntryNumber)),
                    fields.Nested(desert.schema_class(TemplateVariablesEntryArray)),
                    fields.Nested(desert.schema_class(TemplateVariablesEntryFilePath)),
                    fields.Nested(desert.schema_class(TemplateVariablesEntryModelSlug)),
                    fields.Nested(
                        desert.schema_class(TemplateVariablesEntrySchemaColumnName)
                    ),
                    fields.Nested(
                        desert.schema_class(TemplateVariablesEntrySchemaColumnNameArray)
                    ),
                ],
            ),
            allow_none=True,
        ),
        default=None,
    )
