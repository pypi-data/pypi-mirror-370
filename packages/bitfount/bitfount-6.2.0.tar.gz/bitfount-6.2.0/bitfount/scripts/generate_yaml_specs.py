#!/usr/bin/env python3
"""Generate OpenAPI specs for the YAML interface."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any, Optional, Union, cast

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec.ext.marshmallow.field_converter import FieldConverterMixin
import desert
from fire import Fire
from marshmallow import RAISE, Schema
import marshmallow.fields as fields
from marshmallow.validate import ContainsOnly, OneOf
from marshmallow_union import Union as M_Union
from packaging.version import Version

from bitfount import config
from bitfount.__version__ import (
    __version__ as bf_version,
    __yaml_versions__ as yaml_version,
)
from bitfount.runners.config_schemas.common_schemas import FilePath, ModelReference
from bitfount.runners.config_schemas.modeller_schemas import (
    ModellerConfig,
    TemplatedModellerConfig,
)
from bitfount.runners.config_schemas.pod_schemas import PodConfig

config._BITFOUNT_CLI_MODE = True


def _resolve_schema_cls(schema: Union[Schema, type[Schema]]) -> type[Schema]:
    """Return schema class for given schema (instance or class).

    Args:
        schema: Instance or class of marshmallow.Schema

    Returns:
        Schema class of given schema.

    Raises:
        LookupError: If schema class could not be found.
    """
    if isinstance(schema, type) and issubclass(schema, Schema):
        return schema
    if isinstance(schema, Schema):
        return type(schema)
    raise LookupError(f"Could not find schema class for {schema}")


def _maybe_replace_nested_schema(
    field: fields.Nested, local_schema_register: dict[str, type[Schema]]
) -> None:
    """Looks into a Nested field and attempts to replace its schema.

    Tries to find a schema type for the same class in the local_schema_register.
    If found mutates the Nested field to reference that schema type instead
    (de-duplicate). If not found, calls the base recursive method on that schema so
    that it's added to the register and processed.

    Args:
        field: The Nested field to mutate.
        local_schema_register: The local schema register.
    """
    field_schema_cls = _resolve_schema_cls(field.nested)  # type: ignore[arg-type] # Reason: it works # noqa: E501
    if field_schema_cls.__name__ in local_schema_register:
        field.nested = local_schema_register[field_schema_cls.__name__]
        field._schema = None
    else:
        _recursive_deduplicate_schema_classes(field.schema, local_schema_register)


def _recursive_find_nested(
    field: fields.Field, local_schema_register: dict[str, type[Schema]]
) -> None:
    """Look into a Field and recurse until a Nested is found.

    This method will:
        if a Nested is found call `maybe_replace_nested_schema`
        if a Field containing other Fields is found, recurse further
        if a simple Field is found do nothing

    Args:
        field: The field to inspect.
        local_schema_register: The local schema register.
    """
    if isinstance(field, fields.Nested):
        _maybe_replace_nested_schema(field, local_schema_register)
    if isinstance(field, fields.List):
        _recursive_find_nested(field.inner, local_schema_register)
    if isinstance(field, M_Union):
        for union_field in field._candidate_fields:  # type: ignore[attr-defined] # Reason: Private attribute # noqa: E501
            _recursive_find_nested(union_field, local_schema_register)
    if isinstance(field, fields.Mapping) and isinstance(
        field.value_field, fields.Nested
    ):
        _maybe_replace_nested_schema(field.value_field, local_schema_register)


def _recursive_deduplicate_schema_classes(
    schema: Union[Schema, type[Schema]], local_schema_register: dict[str, type[Schema]]
) -> None:
    """Save this schema to the local schema register.

    Also process its fields to find and replace replicated schemas for the same class

    Args:
        schema: The schema to process.
        local_schema_register: The local schema register.
    """
    # save current schema to the register
    schema_cls = _resolve_schema_cls(schema)
    local_schema_register[schema_cls.__name__] = schema_cls
    # process fields
    for field in schema.fields.values():
        _recursive_find_nested(field, local_schema_register)


def _set_meta_unknown(
    local_schema_register: dict[str, type[Schema]], meta_unknown: str
) -> None:
    """For all the schemas in the local_schema_register, set Meta.unknown.

    This is required because of https://github.com/python-desert/desert/issues/100.

    Args:
        local_schema_register: The local schema register.
        meta_unknown: The desired value of Meta.unknown.
    """
    for schema in local_schema_register.values():
        schema.Meta.unknown = meta_unknown  # type: ignore[attr-defined] # Reason: It does have this attribute # noqa: E501


def _convert_union_to_spec(
    self: FieldConverterMixin, field: fields.Field, **kwargs: Any
) -> dict[str, list[Any]]:
    """Converts M_Unions fields to OpenAPI spec.

    Handles M_Union fields, including complex validations such as ContainsOnly.
    Dynamically infers enum values from field constraints.
    """
    if not isinstance(field, M_Union):
        return {}

    ret: dict[str, list[Any]] = {"anyOf": []}

    for union_field in getattr(field, "_candidate_fields", []):
        if isinstance(union_field, fields.Dict):
            key_field = getattr(union_field, "key_field", None)
            value_field = getattr(union_field, "value_field", None)

            keys_enum: Optional[list[Any]] = (
                list(key_field.validate.choices)
                if key_field
                and hasattr(key_field, "validate")
                and isinstance(key_field.validate, OneOf)
                else None
            )
            values_enum: Optional[list[Any]] = (
                list(value_field.validate.choices)
                if value_field
                and hasattr(value_field, "validate")
                and isinstance(value_field.validate, ContainsOnly)
                else None
            )

            # If we've found enum entries, use those and manually construct the dict
            # schema
            if (
                values_enum
                and len(values_enum) > 0
                and keys_enum
                and len(keys_enum) > 0
            ):
                for key_value in keys_enum:
                    dict_schema = {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            key_value: {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": values_enum,  # Use inferred values enum
                                },
                            },
                        },
                    }
                    ret["anyOf"].append(dict_schema)
            # Otherwise, use the default dict field parsing
            else:
                dict_schema = self.field2property(union_field)
                ret["anyOf"].append(dict_schema)
        else:
            ret["anyOf"].append(self.field2property(union_field))

    # Need to remove the default {'type': 'null'}
    # Because this method is run after the existing `self.attribute_functions` of the
    # mixin, it runs after `self.field2nullable` which, in this field's usage,
    # results in an erroneous {'type': 'null'} being in the `ret` entries already
    # created. In order to give priority to the `anyOf` functionality, we need to
    # remove this and set it on the anyOf tag instead.
    if field.allow_none:
        ret["anyOf"].append({"type": "null"})
        existing_ret = kwargs.get("ret")
        if (
            existing_ret
            and "type" in existing_ret
            and (existing_ret["type"] == "null" or existing_ret["type"] == ["null"])
        ):
            del existing_ret["type"]

    # Filter out any schemas where enum remains empty
    ret["anyOf"] = [
        schema
        for schema in ret["anyOf"]
        if not (
            "enum" in schema.get("properties", {}).get("keys", {})
            and not schema["properties"]["keys"]["enum"]
        )
        and not (
            "enum" in schema.get("properties", {}).get("values", {}).get("items", {})
            and not schema["properties"]["values"]["items"]["enum"]
        )
    ]

    return ret


def _remove_generic_plugin_options_from_spec(spec: APISpec) -> APISpec:
    """Remove GenericPluginOptions from the spec.

    We want to remove generic plugin type from the schema because
    if we keep it, any validation falls back this. and we won't
    Specific plugin types won't be validated otherwise.
    """
    # Remove Generic Protocol from the spec
    del spec.components.schemas["GenericProtocolConfig"]
    # Remove references to Generic Protocol from the spec
    key_to_remove = "#/components/schemas/GenericProtocolConfig"
    i = 0
    protocol_list = spec.components.schemas["TaskConfig"]["properties"]["protocol"][
        "anyOf"
    ]
    while i < len(protocol_list):
        protocol = protocol_list[i]
        # Exclude any protocol that references GenericProtocolConfig
        if protocol.get("$ref") == key_to_remove:
            protocol_list.remove(protocol)
            break
        else:
            i += 1

    # Remove Generic Algorithm from the spec
    del spec.components.schemas["GenericAlgorithmConfig"]
    # Remove references to Generic Algorithm from the spec
    key_to_remove = "#/components/schemas/GenericAlgorithmConfig"
    i = 0
    algorithm_list = spec.components.schemas["TaskConfig"]["properties"]["algorithm"][
        "anyOf"
    ]
    while i < len(algorithm_list):
        algorithm = algorithm_list[i]
        # Exclude any algorithm that references GenericAlgorithmConfig
        if algorithm.get("$ref") == key_to_remove:
            algorithm_list.remove(algorithm)
            continue
        else:
            # Exclude any algorithm that has GenericAlgorithmConfig as item
            if algorithm.get("items"):
                k = 0
                while k < len(algorithm["items"]["anyOf"]):
                    item = algorithm["items"]["anyOf"][k]
                    if item["$ref"] == key_to_remove:
                        algorithm["items"]["anyOf"].pop(k)
                    else:
                        k += 1
            i += 1

    return spec


def _remove_default_null_pairs(
    data: dict[Any, Any], pairs_to_remove: list[tuple[str, Optional[str]]]
) -> dict[Any, Any]:
    """Recursively remove certain key-value pairs from nested dict.

    Args:
        data: The nested dictionary.
        pairs_to_remove: The list of (key, values) to remove.

    Returns:
        The dictionary with the (key, value) pairs removed.
    """
    result = {}

    for key, value in data.items():
        if isinstance(value, dict):
            value = _remove_default_null_pairs(value, pairs_to_remove)
        result[key] = value

    for key, value in pairs_to_remove:
        if key in result and result[key] == value:
            del result[key]

    return result


def generate_spec(root_class: type) -> dict[str, Any]:
    """Generate OpenAPI spec for given root class.

    Args:
        root_class: Class to generate OpenAPI spec for.

    Returns:
        OpenAPI spec for given root class as a dict.
    """
    ma_plugin = MarshmallowPlugin()
    root_class_name = root_class.__name__
    # normalize bf versions
    bf_norm_version = str(Version(bf_version))

    spec = APISpec(
        title=f"{root_class_name} OpenAPI Spec",
        version=bf_norm_version,
        yaml_versions=yaml_version,
        openapi_version="3.1.0",
        plugins=[ma_plugin],
        options={
            "externalDocs": {
                "description": "More information about the YAML API",
                "url": "https://docs.bitfount.com/api/bitfount/runners/config_schemas",
            }
        },
    )
    assert (  # nosec[assert_used] # Reason: Reassuring mypy
        ma_plugin.converter is not None
    )

    # Additions/modifications to the Marshmallow plugin
    # Support Union
    ma_plugin.converter.add_attribute_function(_convert_union_to_spec)
    # Support FilePath field type
    ma_plugin.map_to_openapi_type(FilePath, fields.String)
    # Support ModelReference field type
    ma_plugin.map_to_openapi_type(ModelReference, fields.String)

    schema = desert.schema_class(root_class)()
    local_schema_register: dict[str, type[Schema]] = {}
    _recursive_deduplicate_schema_classes(schema, local_schema_register)
    _set_meta_unknown(local_schema_register, RAISE)
    spec.components.schema(root_class_name, schema=schema)
    if "ModellerConfig" in root_class_name:
        spec = _remove_generic_plugin_options_from_spec(spec)
    spec_dict = cast(dict, spec.to_dict())
    # Remove "default": null from the api spec since it's not needed
    # and causes issues with openapi changes.
    # From: https://swagger.io/docs/specification/describing-parameters/:
    # "Use the default keyword in the parameter schema to specify
    # the default value for an optional parameter. The default
    # value is the one that the server uses if the client
    # does not supply the parameter value in the request.
    # The value type must be the same as the parameter's data type."
    # Since the value is None, and the type will be defined as
    # ["sometype", "null"], there is no need for explicit
    # "default": null in the openapi config.
    spec_dict = _remove_default_null_pairs(spec_dict, [("default", None)])
    # This signifies that the top level object is the rootClass
    spec_dict["allOf"] = [{"$ref": f"#/components/schemas/{root_class_name}"}]
    # OpenAPI version 3.1.0 corresponds to JSON Schema draft 2020-12
    spec_dict["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    return spec_dict


def generate_yaml_specs(
    output_directory: str = "task_templates",
    breaking_changes_check: bool = False,
    specs: Optional[str] = None,
    templated: bool = True,
    *modules_to_import: str,
) -> None:
    """Generate OpenAPI specs for the YAML interface.

    Args:
        output_directory: Directory to store the generated specs,
            will be created if it doesn't already exist.
        breaking_changes_check: Whether this is run for checking for breaking changes.
        specs: Whether to generate "pod" or "task" spec. If not provided, generates
            both.
        templated: Whether to generate the templated modeller config spec or regular
            modeller config spec.
        modules_to_import: Module paths to be imported, this is used so that any
            plugins can be loaded and included in the specs.
    """
    if modules_to_import:
        [importlib.import_module(module) for module in modules_to_import]

    _output_directory = Path(output_directory)

    _output_directory.mkdir(parents=True, exist_ok=True)
    if breaking_changes_check:
        task_spec_file = "task-spec-new.json"
        pod_spec_file = "pod-spec-new.json"
    else:
        task_spec_file = "task-spec.json"
        pod_spec_file = "pod-spec.json"
    if specs == "task" or not specs:
        with (_output_directory / task_spec_file).open(mode="w", encoding="utf-8") as f:
            json.dump(
                generate_spec(TemplatedModellerConfig if templated else ModellerConfig),
                f,
                indent=2,
                sort_keys=True,
            )
            f.write("\n")
    if specs == "pod" or not specs:
        with (_output_directory / pod_spec_file).open(mode="w", encoding="utf-8") as f:
            json.dump(generate_spec(PodConfig), f, indent=2, sort_keys=True)
            f.write("\n")


if __name__ == "__main__":
    Fire(generate_yaml_specs)
