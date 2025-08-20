"""Module for serialization and deserialization of models, algorithms and protocols."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import itertools
from pathlib import Path
from typing import Any, Optional, Union, cast

from marshmallow import Schema as MarshmallowSchema, fields, post_load
from marshmallow_polyfield import PolyField
from marshmallow_union import Union as M_Union

from bitfount.federated.model_reference import BitfountModelReference
from bitfount.schemas.exceptions import SchemaClassError
from bitfount.types import _BaseSerializableObjectMixIn, _JSONDict

# Methods for dumping the schema
# In bf_dump, we take an object which we convert to a schema using the
# `_obj_to_schema` function. For each item provided in to the
# `_obj_to_schema` function we also have to load all attributes
#  of the parent classes,which we do using `_bf_combine_dict_dump.


def bf_dump(bf_obj: _BaseSerializableObjectMixIn) -> _JSONDict:
    """Method for serializing an object.

    Args:
        bf_obj: The object we want to generate the schema dump for.

    Raises:
        SchemaClassError: If the provided object is None.
    """
    # Get the schema class from the object.
    schema_cls = _obj_to_schema(bf_obj)

    if not schema_cls:
        raise SchemaClassError(
            f"There is no schema class that can be "
            f"generated from the given object:{bf_obj}."
        )

    myschema = schema_cls()

    # Get the schema dump
    schema_dump = cast(_JSONDict, myschema.dump(bf_obj))
    # Make sure all fields and the schema are deleted to prevent
    # memory leak.
    del myschema

    return schema_dump


def _obj_to_schema(
    bf_obj: _BaseSerializableObjectMixIn, depth: int = 0
) -> Optional[type[MarshmallowSchema]]:
    """Converts an object to a marshmallow schema."""
    if depth > 5:
        raise SchemaClassError("Cannot have more than depth 5 in serialisation")

    if bf_obj:
        # Load all nested and unnested attributes of the parent classes.
        unnested_fields, nested_fields = _bf_combine_dict_dump(
            bf_obj, bf_obj.fields_dict.copy(), bf_obj.nested_fields.copy()
        )
        unnested_fields["class_name"] = fields.Str()
        nested_fields_helper: dict[
            str, Union[fields.Field, type[MarshmallowSchema]]
        ] = {}

        # For each nested item, go recursively through them and unpack
        # to only have unnested fields and then generate schemas for
        # all of them.
        for k, _ in nested_fields.items():
            nested_attribute = getattr(bf_obj, k)

            # This allows nested fields to be sequences of objects.
            if isinstance(nested_attribute, Sequence):
                # This PolyField is used to allow for multiple types of objects
                # to be in the same sequence e.g. a list of different algorithms
                # in one protocol
                polyfield = PolyField(
                    # The first argument in this lambda is the object to be
                    # serialized.
                    serialization_schema_selector=lambda x, _: _obj_to_schema(
                        x, depth + 1
                    ),
                )

                nested_fields_helper.update({k: fields.List(polyfield)})

            # We only care about the case when `_obj_to_schema` is not None
            elif schema := _obj_to_schema(nested_attribute, depth + 1):
                nested_fields_helper.update({k: fields.Nested(schema)})

        # Get the schema of the object
        return _get_marshmallow_schema(
            bf_obj.__class__, unnested_fields, nested_fields_helper
        )

    return None


def _bf_combine_dict_dump(
    cls: _BaseSerializableObjectMixIn, fields_dict: _JSONDict, nested_fields: _JSONDict
) -> tuple[_JSONDict, _JSONDict]:
    """Combine the nested and unnested fields from the subclasses.

    Loop through the class mro, and get the fields_dict and
    nested_fields from the parent classes.
    """
    for item in cls.__class__.__mro__:
        fields_dict, nested_fields = _combine_dict_helper(
            item, fields_dict, nested_fields
        )
    return fields_dict, nested_fields


# Shared Methods


def _get_marshmallow_schema(
    obj_class: type[_BaseSerializableObjectMixIn],
    unnested_fields: _JSONDict,
    nested_schemas: _JSONDict,
) -> type[MarshmallowSchema]:
    """Generate the marshmallow schema from field dictionaries."""
    # For all nested items, define them as a nested field with the generated schema.
    nested = [(name, value) for name, value in nested_schemas.items()]

    @post_load
    def recreate_factory(self: Any, data: _JSONDict, **_kwargs: Any) -> Any:
        data = data.copy()
        data.pop("class_name")
        return obj_class(**data)

    # Pack all fields needed for the schema generation
    all_fields = dict(
        itertools.chain.from_iterable(
            [
                nested,
                unnested_fields.items(),
                [(recreate_factory.__name__, recreate_factory)],
            ]
        )
    )
    # Get the return schema from the fields.
    return _BitfountGeneratedSchema.from_dict(all_fields)


class _BitfountGeneratedSchema(MarshmallowSchema):
    """Schema class to prevent registering all the Marshmallow Schemas generated."""

    class Meta:
        """Meta class for the _BitfountGeneratedSchema.

        Used to set the register to `False`, to make sure that the newly generated
        schemas are not registered in the marshmallow class registers.
        """

        register = False

    def __del__(self) -> None:
        """Helper function for deleting all schema attributes.

        It makes sure that all the fields are assigned to None
        when schema gets deleted, to free up memory.
        """
        # Mypy complains that there is a type mismatch between these
        # fields and `None` type, however, our goal is to make sure
        # they are set to None when deleting the schema, so we can
        # ignore the assignment.
        self.fields = None  # type: ignore[assignment] # Reason: see above
        self.declared_fields = None  # type: ignore[assignment] # Reason: see above # noqa: E501
        self.load_fields = None  # type: ignore[assignment] # Reason: see above
        self.dump_fields = None  # type: ignore[assignment] # Reason: see above

    # The below methods are related to the `BitfountModelReference`.
    # They are used for serialization and deserialization of the model_ref.
    # The marshmallow field for the model_ref is using these methods for
    # serializing/ deserializing.
    @staticmethod
    def get_model_ref(bfmr: BitfountModelReference) -> str:
        """Returns the model_ref, ready for serialization.

        Used for serialization of BitfountModelReference.
        """
        model_ref = bfmr.model_ref
        try:
            return model_ref.stem  # type: ignore[union-attr]  # Reason: captured by AttributeError below  # noqa: E501
        except AttributeError as ae:
            # Check if class name only, return if is
            if Path(model_ref).stem == str(model_ref):
                return str(model_ref)
            # Otherwise error
            raise TypeError(
                f"Unable to serialise model_ref; "
                f"expected python file path Path or model name str, "
                f"got {type(model_ref)} with value {model_ref}"
            ) from ae

    @staticmethod
    def load_model_ref(value: str) -> Union[Path, str]:
        """Deserialize the model_ref value.

        Used for deserialization of BitfountModelReference.
        """
        try:
            new_value = Path(value).expanduser()
            if new_value.stem == str(new_value):  # i.e. is just a class name
                return str(value)
            return new_value
        except TypeError:
            return str(value)


def _combine_dict_helper(
    item: Any, fields_dict: _JSONDict, nested_fields: _JSONDict
) -> tuple[_JSONDict, _JSONDict]:
    """Helper function for bf_combine_load and _dump.

    Used to get the nested and unnested fields from the `item` class.
    """
    if hasattr(item, "fields_dict"):
        for k, v in item.fields_dict.items():
            if k not in fields_dict:
                fields_dict[k] = v
        for k, v in item.nested_fields.items():
            if k not in nested_fields:
                nested_fields[k] = v

    return fields_dict, nested_fields


# Methods for loading the schema

# In bf_load, we take a dictionary which we convert to a schema using the
# `_dict_to_schema` function. For each item provided in to the
# `_dict_to_schema` function we also have to loop through the registries
#  given to make sure we load all attributes of the parent classes,
#  which we do using `_bf_combine_dict_load`.


def bf_load(dct: _JSONDict, registry: Mapping[str, Any]) -> Any:
    """Method for deserializing an object.

    Args:
        dct: A JSON dictionary with the fields to load.
        registry: The registry where we can access the schema type.
    """
    # TODO: [BIT-5973] Remove
    dct.pop("primary_results_path", None)

    # Marshmallow  `.load()` method loads the same algorithm
    # multiple times if a list is provided, so we iterate
    # through them and load them separately instead
    algorithms_list = []

    if "algorithm" in dct.keys():
        if isinstance(dct["algorithm"], list):
            for alg_dct in dct["algorithm"]:
                from bitfount.federated.utils import _ALGORITHMS

                alg_schema = _dict_to_schema(alg_dct, _ALGORITHMS)()
                loaded_alg = alg_schema.load(alg_dct)
                del alg_schema
                algorithms_list.append(loaded_alg)

    # for loading the proto only choose one algo to avoid errors.
    if "algorithm" in dct.keys():
        if isinstance(dct["algorithm"], list):
            dct["algorithm"] = dct["algorithm"][0]
    # Get the schema given a dictionary with the fields.
    schema = _dict_to_schema(dct, registry)()
    # Load the object from the schema.
    loaded_object = schema.load(dct)
    # Make sure all fields and the schema are deleted to prevent memory leak.
    del schema

    if len(algorithms_list) > 1:
        loaded_object.algorithm = algorithms_list
    return loaded_object


def _dict_to_schema(
    dct: _JSONDict, registry: Mapping[str, type], depth: int = 0
) -> type[MarshmallowSchema]:
    """Converts a dictionary to a marshmallow schema."""
    if depth > 5:
        raise SchemaClassError("Cannot have more than depth 5 in serialisation")
    # Get the class by looking in the given registry for the class_name after
    # removing the `bitfount.` prefix if present. This is present only on protocols,
    # algorithms, aggregators and models.
    cls: Any = registry[dct["class_name"].split(".", 1)[-1]]
    # Load all nested and unnested attributes of the parent classes.
    unnested_fields, nested_fields = _bf_combine_dict_load(
        cls, cls.fields_dict.copy(), cls.nested_fields.copy(), registry
    )
    unnested_fields["class_name"] = fields.Str()
    nested_fields_aux: dict[str, Union[fields.Field, type[MarshmallowSchema]]] = {}

    # For each nested item, go recursively through them and unpack
    # to only have unnested fields and then generate schemas for
    # all of them.
    for k, sub_reg in nested_fields.items():
        try:
            nested_dict_item = dct[k]
        except KeyError:
            # If the key is not present in the dictionary, it means that
            # it was optional
            continue

        # This allows nested fields to be sequences of objects.
        if isinstance(nested_dict_item, list):
            schemas: list[fields.Field] = []
            for i in nested_dict_item:
                schemas.append(fields.Nested(_dict_to_schema(i, sub_reg, depth + 1)))
            nested_fields_aux.update({k: fields.List(M_Union(schemas))})
        else:
            nested_fields_aux.update(
                {
                    k: fields.Nested(
                        _dict_to_schema(nested_dict_item, sub_reg, depth + 1)
                    )
                }
            )

    # Get the schema of the class
    return _get_marshmallow_schema(cls, unnested_fields, nested_fields_aux)


def _bf_combine_dict_load(
    cls: Any,
    fields_dict: _JSONDict,
    nested_fields: _JSONDict,
    registry: Mapping[str, Any],
) -> tuple[_JSONDict, _JSONDict]:
    """Combine the nested and unnested fields from the subclasses.

    This method loops through the registry and checks if any of
    the modules are superclasses of the given class. This is
    done explicitly as some subclasses are not loaded
    properly in the federated setting. This way, it ensures
    that both nested and unnested fields are loaded from all
    the respective subclasses.

    Args:
        cls: The class for which we want the nested and unnested fields.
        fields_dict: The unnested fields dictionary.
        nested_fields: The nested fields' dictionary.
        registry: The registry with the (possible) superclasses
    """
    # Loop through the registry in order to load all relevant
    # nested and unnested fields from the parent classes.
    for item in registry.values():
        if issubclass(cls, item):
            fields_dict, nested_fields = _combine_dict_helper(
                item, fields_dict, nested_fields
            )
    return fields_dict, nested_fields
