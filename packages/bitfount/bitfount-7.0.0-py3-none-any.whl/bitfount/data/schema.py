"""Classes concerning data schemas."""

from __future__ import annotations

import collections
from collections.abc import Iterable, MutableMapping, Sequence
import datetime
import hashlib
import json
import logging
from os import PathLike
from typing import Any, List, Literal, Mapping, Optional, TypeAlias, Union, cast

from marshmallow import fields, post_dump, post_load, pre_dump, pre_load
import numpy as np
import pandas as pd
from pandas._typing import Dtype
from pandas.core.dtypes.common import (
    is_datetime64_any_dtype as is_datetime,
    is_numeric_dtype,
)
import yaml

from bitfount.__version__ import __version__ as bitfount_version
from bitfount.data.datasources.base_source import (
    BITFOUNT_INFERRED_LABEL_COLUMN,
    BaseSource,
)
from bitfount.data.exceptions import BitfountSchemaError
from bitfount.data.types import (
    CategoricalRecord,
    ContinuousRecord,
    ImageRecord,
    SemanticType,
    TextRecord,
    _CamelCaseSchema,
    _FeatureDict,
    _ForceStypeValue,
    _SemanticTypeRecord,
    _SemanticTypeValue,
)
from bitfount.hooks import DataSourceHook
from bitfount.types import _Dtypes, _DtypesValues, _JSONDict
from bitfount.utils import _add_this_to_list, delegates

# Type alias for schema metadata
SchemaMetadata: TypeAlias = dict[
    str,
    Union[
        str,
        Optional[
            MutableMapping[
                Literal["categorical", "continuous", "image", "text", "image_prefix"],
                list[str],
            ]
        ],
    ],
]


logger = logging.getLogger(__name__)


class SchemaGenerationFromYieldData(DataSourceHook):
    """Custom hook to execute logic during datasource yield data."""

    def __init__(
        self,
        schema: BitfountSchema,
        ignore_cols: Optional[list[str]] = None,
        force_stypes: Optional[
            MutableMapping[
                Literal["categorical", "continuous", "image", "text", "image_prefix"],
                list[str],
            ]
        ] = None,
    ) -> None:
        """Initialize the hook.

        Args:
            schema: The schema to update.
            ignore_cols: Columns to ignore when updating the schema.
            force_stypes: Forced semantic types for specific columns.
        """
        super().__init__()
        self.schema = schema
        self.ignore_cols = ignore_cols if ignore_cols is not None else []
        self.force_stypes = force_stypes if force_stypes is not None else {}

    def on_datasource_yield_data(
        self, data: pd.DataFrame, *args: Any, **kwargs: Any
    ) -> None:
        """Hook method triggered when the datasource yields data.

        Args:
            data: The dataframe yielded by the datasource.
            args: Additional arguments.
            kwargs: Additional keyword arguments.
        """
        self.schema.add_dataframe_features(
            data=data,
            ignore_cols=self.ignore_cols,
            force_stypes=self.force_stypes,
        )
        logger.debug(
            f"Schema updated with new dataframe features from {len(data)} datapoints."
        )


class _BitfountSchemaMarshmallowMixIn:
    """MixIn class for Schema serialization."""

    def dump(self, file_path: PathLike) -> None:
        """Dumps the schema as a yaml file.

        Args:
            file_path: The path where the file should be saved

        Returns:
            none
        """
        with open(file_path, "w") as file:
            file.write(self.dumps())

    def dumps(self) -> str:
        """Produces the YAML representation of the schema object.

        Returns:
            The YAML representation of the schema as a string.
        """
        return yaml.dump(self.to_json(), sort_keys=False)

    def to_json(self) -> _JSONDict:
        """Turns a schema object into a JSON compatible dictionary.

        Returns:
            A simple JSON compatible representation of the Schema
        """
        # Our self._Schema() objects are dumped as JSON-compatible dicts
        return cast(_JSONDict, self._Schema().dump(self))

    @classmethod
    def load(cls, data: Mapping) -> BitfountSchema:
        """Loads the schema from a dictionary.

        Args:
            data: The data to load the schema from.

        Returns:
            BitfountSchema.
        """
        # @post_load guarantees this will be a BitfountSchema
        schema: BitfountSchema = cls._Schema().load(data)
        return schema

    @classmethod
    def loads(cls, data: str) -> BitfountSchema:
        """Loads the schema from a yaml string.

        Args:
            data: The yaml string to load the schema from.

        Returns:
            BitfountSchema.
        """
        return cls.load(yaml.safe_load(data))

    @classmethod
    def load_from_file(cls, file_path: Union[str, PathLike]) -> BitfountSchema:
        """Loads the schema from a yaml file.

        This contains validation errors to help fix an invalid YAML file.
        """
        with open(file_path, "r") as f:
            schema_as_yaml = yaml.safe_load(f)
        return cls.load(schema_as_yaml)

    class _Schema(_CamelCaseSchema):
        name = fields.Str(required=True)
        description = fields.Str(allow_none=True)
        categorical_features = fields.List(fields.Nested(CategoricalRecord._Schema))
        continuous_features = fields.List(fields.Nested(ContinuousRecord._Schema))
        image_features = fields.List(fields.Nested(ImageRecord._Schema))
        text_features = fields.List(fields.Nested(TextRecord._Schema))
        number_of_records = fields.Int(
            allow_none=True,
            data_key="number_of_records",  # Explicitly map the field for deserialization #noqa: E501
        )
        # TODO: [BIT-1057] Consider moving metadata to be a separate part of the
        #       output YAML.
        # To maintain backwards compatibility with schemas that may not contain
        # metadata we use a default value.
        metadata = fields.Method(
            serialize="dump_metadata", deserialize="load_metadata", load_default=dict
        )
        schema_type = fields.Str(allow_none=True)

        @pre_dump
        def dump_feature_values(
            self, data: BitfountSchema, **_kwargs: Any
        ) -> BitfountSchema:
            """Modifies features to dump features as a list instead of dictionaries.

            To ensure our YAML is clear, we pre-process our object into lists before
            dumping it. We don't want to modify the actual schema object, as it will
            affect its use, so we create a temporary one just for dumping to YAML.
            """
            temp_schema = BitfountSchema(name=data.name, description=data.description)
            temp_schema.schema_type = data.schema_type
            temp_schema.number_of_records = data.number_of_records
            temp_schema.force_stypes = data.force_stypes
            for stype in data.features:
                setattr(
                    temp_schema,
                    f"{stype}_features",
                    list(data.features[cast(_SemanticTypeValue, stype)].values()),
                )
            return temp_schema

        @post_dump
        def combine_features(self, data: _JSONDict, **kwargs: Any) -> _JSONDict:
            """Combines features belonging to different semantic types under one key.

            After combining the features into one list, it also sorts all the features
            by featureName.
            """
            new_data = {}
            new_data["name"] = data.get("name")
            new_data["description"] = data.get("description")
            new_data["number_of_records"] = data.get("numberOfRecords")
            features: list[_JSONDict] = [
                item for key in data if key.endswith("Features") for item in data[key]
            ]
            # sort features alphabetically
            new_data["features"] = sorted(features, key=lambda d: d["featureName"])
            new_data["metadata"] = data.get("metadata")
            return new_data

        @pre_load
        def split_features(self, data: _JSONDict, **kwargs: Any) -> _JSONDict:
            """Splits features back into a dictionary of lists by semantic type."""
            data = self.convert_schema_version_to_current(data)
            result = collections.defaultdict(list)
            if "number_of_records" in data:
                data["numberOfRecords"] = data.pop("number_of_records")
            if "features" in data:
                # Workaround to ensure that the data is not pre-processed
                # twice for the bitfount reference model.
                features: list[_JSONDict] = data.pop("features")
                for d in features:
                    result[d.pop("semanticType")].append(d)

                for semantic_type in result:
                    data[f"{semantic_type}Features"] = result[semantic_type]
                return data
            elif any([key for key in data if "Features" in key]):
                # Data has been already preprocessed
                return data
            else:
                raise ValueError("No features found in the schema.")

        @post_load
        def recreate_schema(self, data: _JSONDict, **_kwargs: Any) -> BitfountSchema:
            """Recreates Schema."""
            new_schema = BitfountSchema(
                name=data["name"],
                description=data.get("description"),
            )
            new_schema.number_of_records = data.get("number_of_records", 0)
            for key in data:
                if key.endswith("_features"):
                    stype = key.replace("_features", "")
                    new_schema.features[cast(_SemanticTypeValue, stype)] = {
                        feature.feature_name: feature for feature in data[key]
                    }
            # Ensure existing datasources hash is loaded if present
            new_schema._orig_hash = data["metadata"].get("hash")
            # Get the schema type from metadata
            new_schema.schema_type = data["metadata"].get("schema_type")
            new_schema.force_stypes = data["metadata"].get("force_stypes", {})
            return new_schema

        @staticmethod
        def dump_metadata(
            obj: BitfountSchema,
        ) -> SchemaMetadata:
            """Creates and dumps metadata for the schema."""
            metadata = {
                "bitfount_version": bitfount_version,
                "hash": obj.hash,
                "force_stypes": obj.force_stypes,
                "schema_version": "4",
            }
            if obj.schema_type is not None:
                metadata["schema_type"] = obj.schema_type  # Add only if it's not None
            return metadata

        @staticmethod
        def load_metadata(value: SchemaMetadata) -> SchemaMetadata:
            """Loads the metadata dict.

            Args:
                value: Dictionary containing metadata including bitfount_version, hash,
                      force_stypes, schema_version, and optionally schema_type.

            Returns:
                The processed metadata dictionary.
            """
            if "force_stypes" in value and value["force_stypes"] is not None:
                force_stypes = value["force_stypes"]
                if not isinstance(force_stypes, MutableMapping):
                    logger.warning(f"Invalid force_stypes type: {type(force_stypes)}")
                    value["force_stypes"] = None
                    return value
                allowed_keys = {
                    "categorical",
                    "continuous",
                    "image",
                    "text",
                    "image_prefix",
                }

                # Filter out invalid keys
                cleaned_force_stypes = {}
                for key, val in force_stypes.items():
                    if key not in allowed_keys:
                        logger.warning(f"Skipping invalid force_stypes key: {key}")
                        continue

                    # Skip if value isn't a list or contains non-string elements
                    if not isinstance(val, list) or not all(
                        isinstance(x, str) for x in val
                    ):
                        logger.warning(
                            f"Skipping invalid force_stypes value for {key}: {val}"
                        )
                        continue

                    cleaned_force_stypes[key] = val

                value["force_stypes"] = (
                    cleaned_force_stypes if cleaned_force_stypes else None
                )

            return value

        @staticmethod
        def convert_schema_version_to_current(
            data: _JSONDict, **kwargs: Any
        ) -> _JSONDict:
            """Convert schema previous versions to version 3.

            This method is a pre-load hook that checks the schema version
            in the provided data.

            Args:
                data (_JSONDict): The data dictionary containing
                    the schema information.
                **kwargs (Any): Additional keyword arguments.

            Returns:
                _JSONDict: The updated data dictionary with schema
                    version converted to "3".
            """
            schema_version = data.get("metadata", {}).get("schema_version", None)

            # First convert older versions to v3
            if schema_version == "1" or schema_version is None:
                tables = data.get("tables", None)
                if tables is not None:
                    # Sort the tables by the attribute `name`
                    tables.sort(key=lambda table: table.get("name", ""))
                    logger.debug("Schema v1 detected, converting to v3...")
                    data["metadata"]["schema_version"] = "3"
                    table = tables[0]
                    data["name"] = table.get(
                        "name", ""
                    )  # Grab the first table after sorting
                    data["features"] = table.get("features", [])
                    data["description"] = table.get("description", "")
                    del data["tables"]

            if schema_version == "2" or schema_version is None:
                table = data.get("table", None)
                if table is not None:
                    logger.debug("Schema v2 detected, converting to v3...")
                    data["metadata"]["schema_version"] = "3"
                    data["name"] = table.get("name", "")
                    data["features"] = table.get("features", [])
                    data["description"] = table.get("description", "")
                    data["number_of_records"] = table.get("number_of_records", 0)
                    del data["table"]

            # Convert v3 to v4
            if schema_version in ["1", "2", "3"] or schema_version is None:
                if "metadata" in data:
                    logger.debug("Converting schema to v4...")
                    # Initialize force_stypes if not present
                    if "force_stypes" not in data["metadata"]:
                        data["metadata"]["force_stypes"] = None
                    data["metadata"]["schema_version"] = "4"

            return data


@delegates()
class BitfountSchema(_BitfountSchemaMarshmallowMixIn):
    """A schema that defines the tables of a `BaseSource`.

    It includes the table found in `BaseSource` and its features.

    Args:
        name: The name of the datasource associated with
            this schema.
        description: The description of the datasource.
        column_descriptions: A dictionary of column names and their
            descriptions.
        **kwargs: Optional keyword arguments to be provided to
            `_add_dataframe_features`.
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        column_descriptions: Optional[Mapping[str, str]] = None,
        **kwargs: Any,
    ):
        # self._orig_hash is used to store the hash when loading a previously
        # generated schema.
        self._orig_hash: Optional[str] = None
        # Datasource hashes is a set to ensure that adding the same datasource multiple
        # times does not result in a different hash.
        self._datasource_hashes: set[str] = set()
        # Used to stop any more datasources from being added
        self._frozen: bool = False
        self.name = name
        self.description: Optional[str] = description
        self.column_descriptions: Optional[Mapping[str, str]] = column_descriptions
        # ordered dictionaries of features (column names)
        self.features: _FeatureDict = _FeatureDict()
        self.schema_type: Optional[Literal["partial", "full", "empty"]] = None
        self.number_of_records: int = 0
        self.image_prefix: Optional[List[str]] = None
        self.force_stypes: Optional[
            MutableMapping[
                Literal["categorical", "continuous", "image", "text", "image_prefix"],
                list[str],
            ]
        ] = None

    def apply(
        self,
        dataframe: pd.DataFrame,
        keep_cols: Optional[list[str]] = None,
        image_cols: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """Applies the schema to a dataframe and returns the transformed dataframe.

        Sequentially adds missing columns to the dataframe, removes superfluous columns
        from the dataframe, changes the types of the columns in the dataframe and
        finally encodes the categorical columns in the dataframe before returning the
        transformed dataframe.

        Args:
            dataframe: The dataframe to transform.
            keep_cols: A list of columns to keep even if
                they are not part of the schema. Defaults to None.
            image_cols: The list of image columns in the dataframe. Defaults to None.

        Returns:
            The dataframe with the transformations applied.
        """
        if self.features:
            dataframe = self._expand_dataframe(dataframe)
            dataframe = self._reduce_dataframe(dataframe, keep_cols=keep_cols)
            dataframe = self._apply_types(
                dataframe, selected_cols=keep_cols, image_cols=image_cols
            )
            dataframe = self._encode_dataframe(dataframe)
            return dataframe
        else:
            raise BitfountSchemaError("No schema features found.")

    def _remove_feature_from_other_stype(
        self, feature: str, new_stype: SemanticType
    ) -> None:
        """Ensures that features are not duplicated across semantic types."""
        for stype in self.features:
            stype = cast(_SemanticTypeValue, stype)
            if stype != new_stype.value:
                if feature in self.features[stype].keys():
                    del self.features[stype][feature]

    def _expand_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Expands dataframe to include missing columns specified in the schema.

        Simply adds columns populated with default values: 'nan' for categorical
        and text columns and '0' for continuous columns.

        Args:
            dataframe: dataframe without all the required columns

        Returns:
            Dataframe that includes all the required columns

        Raises:
            BitfountSchemaError: if there is a missing image column as this cannot be
                replicated.
        """
        missing_categorical_value = "nan"
        missing_text_value = "nan"
        missing_continuous_value = 0
        missing_image_value = np.nan
        columns = list(dataframe.columns)
        missing_columns: dict[str, Union[str, float]] = {}

        for stype in self.features:
            # Iterate through semantic types
            for feature_name in self.features[cast(_SemanticTypeValue, stype)]:
                # Iterate through each feature in given semantic type
                if feature_name not in columns:
                    # If feature is not present in the given dataframe, add that feature
                    # with a dummy value to the dataframe
                    logger.debug(
                        f"Feature present in schema but missing in data: {feature_name}"
                    )
                    if stype == SemanticType.IMAGE.value:
                        missing_columns[feature_name] = missing_image_value
                    elif stype == SemanticType.TEXT.value:
                        missing_columns[feature_name] = missing_text_value
                    elif stype == SemanticType.CONTINUOUS.value:
                        missing_columns[feature_name] = missing_continuous_value
                    elif stype == SemanticType.CATEGORICAL.value:
                        missing_columns[feature_name] = missing_categorical_value
                        # adds the missing categorical value (i.e. 'nan') to the encoder
                        # for the missing categorical feature
                        self._add_categorical_feature(
                            name=feature_name,
                            values=np.array([missing_categorical_value]),
                        )

        # Add all missing columns to the dataframe at once
        if missing_columns:
            missing_df = pd.DataFrame(
                {k: [v] * len(dataframe) for k, v in missing_columns.items()}
            )
            dataframe = pd.concat([dataframe, missing_df], axis=1)

        return dataframe

    def _reduce_dataframe(
        self, dataframe: pd.DataFrame, keep_cols: Optional[list[str]] = None
    ) -> pd.DataFrame:
        """Drops any columns that are not part of the schema.

        Args:
            dataframe: dataframe which includes extra columns
            keep_cols: optional list of columns to keep even if
                they are not part of the schema. Defaults to None.

        Returns:
            Dataframe with extra columns removed
        """
        cols_to_keep = self.get_feature_names()
        cols_to_keep = _add_this_to_list(keep_cols, cols_to_keep)
        return dataframe[cols_to_keep]

    def _apply_types(
        self,
        dataframe: pd.DataFrame,
        selected_cols: Optional[list[str]] = None,
        image_cols: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """Applies the prescribed feature types to the dataframe.

        Args:
            dataframe: dataframe with varied types
            selected_cols: optional list of columns selected for
                training to which the types will be applied.
            image_cols: optional list of image columns in the dataframe.

        Returns:
            Dataframe with types that are specified in the schema
        """
        if selected_cols:
            selected = [
                feature_name
                for stype in self.features
                for feature_name, record in self.features[
                    cast(_SemanticTypeValue, stype)
                ].items()
                if feature_name in selected_cols
            ]
        else:
            selected = [
                feature_name
                for stype in self.features
                for feature_name, record in self.features[
                    cast(_SemanticTypeValue, stype)
                ].items()
            ]
        types: dict[str, Union[Dtype, np.dtype]] = {
            feature_name: record.dtype
            for stype in self.features
            for feature_name, record in self.features[
                cast(_SemanticTypeValue, stype)
            ].items()
            if feature_name in selected
        }

        if "categorical" in self.features:
            types.update(
                {
                    feature_name: record.encoder.dtype
                    for feature_name, record in self.features["categorical"].items()
                    if feature_name in selected
                }
            )
        # If schema is generated from the pod_db, then images will be typed as strings
        # instead of objects, so we need to manually change the type to object
        if "image" in self.features and image_cols is not None:
            types.update(
                {
                    feature_name: np.object_
                    for feature_name, record in types.items()
                    if feature_name in image_cols
                }
            )
        return dataframe.astype(types)

    def _encode_dataframe(self, data: pd.DataFrame) -> pd.DataFrame:
        """Encodes the dataframe categorical columns according to the schema.

        Args:
            data: the dataframe to be encoded

        Raises:
            ValueError: if the encoder fails to encode a particular column

        Returns:
            The dataframe with the categorical columns encoded
        """
        if "categorical" in self.features:
            for feature_name, record in self.features["categorical"].items():
                if feature_name not in data:
                    logger.warning(
                        f"Column {feature_name} is not in the dataframe. "
                        "Skipping encoding"
                    )
                    continue
                try:
                    data[feature_name] = record.encoder.transform(data[feature_name])
                except ValueError as err:
                    raise ValueError(
                        f"Could not encode column {feature_name}: {str(err)}"
                    ) from err
        else:
            logger.info("No encoding to be done as there are no categorical features.")

        return data

    @property
    def hash(self) -> str:
        """The hash of this schema.

        This relates to the BaseSource(s) that were used in the generation of this
        schema to assure that this schema is used against compatible data sources.

        Returns:
            A sha256 hash of the `_datasource_hashes`.
        """
        # Must be sorted to ensure ordering of BaseSources being added doesn't
        # change things.
        frozen_hashes: str = str(sorted(self._datasource_hashes))
        return _hash_str(frozen_hashes)

    def add_dataframe_features(
        self,
        data: pd.DataFrame,
        ignore_cols: Optional[Sequence[str]] = None,
        force_stypes: Optional[
            MutableMapping[Union[_ForceStypeValue, _SemanticTypeValue], list[str]]
        ] = None,
        column_descriptions: Optional[Mapping[str, str]] = None,
    ) -> None:
        """Add the features of a dataframe to the schema.

        This method is not called directly, but used as a hook in for
        `yield_data` in the `BaseSource` class.
        """
        # Full schema is used for training and we don't want to
        # keep changing the schema during the training process,
        if not self.schema_type == "full" and not data.empty:
            if ignore_cols is None:
                ignore_cols_aux = []
            else:
                ignore_cols_aux = list(ignore_cols)
            if not force_stypes:
                force_stypes = {}
            # TODO: [BIT-4587] Move this to the prefect schema generation
            #  as it checks for duplicate files.
            self.number_of_records += len(data)
            self._add_dataframe_features(
                data=data,
                ignore_cols=ignore_cols_aux,
                force_stype=force_stypes,
                descriptions=column_descriptions
                if column_descriptions is not None
                else {},
            )

    def _add_dataframe_features(
        self,
        data: pd.DataFrame,
        ignore_cols: list[str],
        force_stype: MutableMapping[
            Union[_ForceStypeValue, _SemanticTypeValue], list[str]
        ],
        descriptions: Mapping[str, str],
    ) -> None:
        """Add given dataframe to the schema."""
        table_dtypes = self._get_dataframe_dtypes(data, ignore_cols)
        col_names = self.get_column_names(data, ignore_cols=ignore_cols)
        # TODO: [BIT-3421] move this if check in `_extract_image_cols_from_force_stype`
        # after the above ticket is handled.
        if "image_prefix" in force_stype or self.image_prefix:
            forced_stype = self._extract_image_cols_from_force_stype(
                col_names, force_stype
            )
        else:
            # If `image_prefix` not present, then it's safe to cast
            forced_stype = cast(
                MutableMapping[_SemanticTypeValue, list[str]], force_stype
            )
        for item in forced_stype.values():
            ignore_cols = _add_this_to_list(item, ignore_cols)
        inferred_semantic_types = self._dtype_based_stype_split(
            table_dtypes, ignore_cols
        )
        semantic_types = self._combine_existing_stypes_with_forced_stypes(
            inferred_semantic_types, forced_stype, table_dtypes
        )
        if SemanticType.CATEGORICAL in semantic_types:
            categorical_values = self._get_categorical_values(
                data,
                semantic_types[SemanticType.CATEGORICAL],
            )
        else:
            categorical_values = None
        for stype, features in semantic_types.items():
            self._add_features_to_schema(
                features=features,
                table_dtypes=table_dtypes,
                descriptions=descriptions,
                stype=stype,
                categorical_values=categorical_values,
            )

    def _get_categorical_values(
        self, data: pd.DataFrame, col_names: list[str], **kwargs: Any
    ) -> dict[str, Iterable[Any]]:
        new_encodings = self._get_dataframe_values(data, col_names, **kwargs)
        existing_encodings = self._get_existing_categorical_feature_values()
        # Combine the existing encodings with the new encodings
        for col_name, value_mappings in existing_encodings.items():
            if col_name in new_encodings:
                new_encodings[col_name] = list(
                    set(new_encodings[col_name]) | set(value_mappings.values())
                )
            else:
                new_encodings[col_name] = list(value_mappings.values())
        return new_encodings

    def _get_existing_categorical_feature_values(
        self,
    ) -> dict[str, MutableMapping[Any, Any]]:
        """Returns the existing categorical feature values."""
        categorical_mappings = {}
        for stype in self.features:
            stype = cast(_SemanticTypeValue, stype)
            if stype == SemanticType.CATEGORICAL.value:
                for feature_name in self.features[stype]:
                    categorical_mappings[feature_name] = {
                        i: v
                        for i, v in enumerate(
                            self.features[stype][feature_name].encoder.classes
                        )
                    }
        return cast(dict[str, MutableMapping[Any, Any]], categorical_mappings)

    def _get_dataframe_values(
        self, data: pd.DataFrame, col_names: list[str], **kwargs: Any
    ) -> dict[str, Iterable[Any]]:
        """Get the distinct values of the columns in the iterable datasource."""
        values: dict[str, set[Any]] = collections.defaultdict(set)
        cols_to_skip: set[str] = set()
        for col in col_names:
            if col in cols_to_skip:
                continue
            try:
                values[col].update(data[col].unique())
            except TypeError:
                logger.warning(f"Found unhashable value type, skipping column {col}.")
                # Remove from `values` dict, if present, and add to skip list
                values.pop(col, None)
                cols_to_skip.add(col)
            except KeyError:
                logger.warning(f"Column {col} not found in the data, skipping it.")
        return {k: list(v) for k, v in values.items()}

    def _combine_existing_stypes_with_forced_stypes(
        self,
        existing_stypes: MutableMapping[SemanticType, list[str]],
        forced_stype: MutableMapping[_SemanticTypeValue, list[str]],
        table_dtypes: Mapping[str, Any],
    ) -> MutableMapping[SemanticType, list[str]]:
        """Combine the exiting semantic types with the forced semantic types."""
        for new_stype, feature_list in forced_stype.items():
            try:
                stype = SemanticType(new_stype)

                if stype not in existing_stypes:
                    existing_stypes[stype] = []
                existing_stypes[stype] = _add_this_to_list(
                    feature_list, existing_stypes[stype]
                )
            except ValueError:
                logger.warning(
                    f"Given semantic type {new_stype} is not currently supported. "
                    f"Defaulting to split based on dtype."
                )
                feature_dtypes = {
                    k: v for k, v in table_dtypes.items() if k in feature_list
                }
                dtype_features = self._dtype_based_stype_split(feature_dtypes, [])
                stype = list(dtype_features)[0]
                if stype not in existing_stypes:
                    existing_stypes[stype] = []
                existing_stypes[stype] = _add_this_to_list(
                    feature_list, existing_stypes[stype]
                )
        return existing_stypes

    def get_column_names(
        self, dataframe: pd.DataFrame, ignore_cols: list[str]
    ) -> Iterable[str]:
        """Get the column names of the datasource."""
        return [col for col in dataframe.columns if col not in ignore_cols]

    def _add_features_to_schema(
        self,
        features: list[str],
        stype: SemanticType,
        table_dtypes: _Dtypes,
        descriptions: Optional[Mapping[str, str]] = None,
        categorical_values: Optional[
            dict[str, Union[Iterable[Any], np.ndarray[Any, Any]]]
        ] = None,
    ) -> None:
        """Add features to the schema based on their semantic type."""
        # # Sort the list of features.
        # # This ensures they are added in deterministic order.
        features.sort()
        for feature_name in features:
            if feature_name not in table_dtypes:
                logger.warning(
                    f"Column {feature_name} does not have a data type. "
                    "Skipping it as it is probably not in the source data."
                )
                continue
            else:
                dtype = table_dtypes[feature_name]
            if descriptions is not None:
                description = descriptions.get(feature_name)
            else:
                description = None
            if (
                feature_name not in self.get_feature_names()
                or stype.value not in self.features.keys()
                or feature_name
                not in self.features[cast(_SemanticTypeValue, stype.value)]
            ):
                # We check whether the feature is already in the schema
                # or if it is not mapped correctly to its semantic type
                if stype == SemanticType.TEXT:
                    TextRecord.add_record_to_schema(
                        self,
                        feature_name=feature_name,
                        dtype=dtype,
                        description=description,
                    )
                elif stype == SemanticType.CONTINUOUS:
                    ContinuousRecord.add_record_to_schema(
                        self,
                        feature_name=feature_name,
                        dtype=dtype,
                        description=description,
                    )
                elif stype == SemanticType.CATEGORICAL:
                    # Categorical values are added prior to accessing this
                    # function if they exist
                    if categorical_values:
                        # Convert arbitrary iterable to the right form
                        feature_values: Union[np.ndarray, pd.Series]
                        if not isinstance(
                            (raw_feature_values := categorical_values[feature_name]),
                            (np.ndarray, pd.Series),
                        ):
                            feature_values = np.asarray(raw_feature_values)
                        else:
                            feature_values = raw_feature_values
                        self._add_categorical_feature(
                            name=feature_name,
                            dtype=dtype,
                            values=feature_values,
                            description=description,
                        )
                    else:
                        continue
                elif stype == SemanticType.IMAGE:
                    if (
                        "image" not in self.features
                        or feature_name not in self.features["image"]
                    ):
                        ImageRecord.add_record_to_schema(
                            self,
                            feature_name=feature_name,
                            dtype=dtype,
                            description=description,
                        )
                self._remove_feature_from_other_stype(feature_name, stype)
            elif (
                feature_name in self.get_feature_names()
                and stype.value in self.features.keys()
                and stype == SemanticType.CATEGORICAL
            ):
                # If categorical values, update the encodings accordingly
                if categorical_values:
                    # Convert arbitrary iterable to the right form
                    # feature_values: Union[np.ndarray, pd.Series]
                    if not isinstance(
                        (raw_feature_values := categorical_values[feature_name]),
                        (np.ndarray, pd.Series),
                    ):
                        feature_values = np.asarray(raw_feature_values)
                    else:
                        feature_values = raw_feature_values
                    self._add_categorical_feature(
                        name=feature_name,
                        dtype=dtype,
                        values=feature_values,
                        description=description,
                    )

    def _add_categorical_feature(
        self,
        name: str,
        values: Union[np.ndarray, pd.Series],
        dtype: Optional[Union[Dtype, np.dtype]] = None,
        description: Optional[str] = None,
    ) -> None:
        """Adds the given categorical, with list of values to the schema."""
        if (
            "categorical" not in self.features
            or name not in self.features["categorical"]
        ):
            CategoricalRecord.add_record_to_schema(
                self,
                feature_name=name,
                dtype=dtype,
                description=description,
            )
        elif name in self.features["categorical"]:
            CategoricalRecord.add_new_encodings_to_schema(
                self,
                feature_name=name,
                dtype=dtype,
                description=description,
            )
        self.features["categorical"][name].encoder.add_values(values)

    @staticmethod
    def _get_dataframe_dtypes(data: pd.DataFrame, cols_to_skip: list[str]) -> _Dtypes:
        """Returns the nullable column types of the dataframe.

        This is called by the `_get_datasource_dtypes` method. This method also
        overrides datetime column dtypes to be strings. This is not done for
        date columns which are of type object.
        """
        data = data.convert_dtypes()
        dtypes: _Dtypes = data.dtypes.to_dict()
        for name in list(dtypes):
            if name in cols_to_skip:
                del dtypes[name]
                continue
            if is_datetime(data[name]):
                dtypes[name] = pd.StringDtype()

        return dtypes

    def _dtype_based_stype_split(
        self, data: _Dtypes, ignore_cols: Optional[Sequence[str]] = None
    ) -> dict[SemanticType, list[str]]:
        """Returns dictionary of Semantic types and corresponding columns in `data`.

        This method determines which data types correspond to which semantic types.
        """
        converted_data = data.copy()
        if ignore_cols:
            missing_cols = [i for i in ignore_cols if i not in data]
            if missing_cols:
                logger.warning(
                    f"Could not find ignored columns: {', '.join(missing_cols)}"
                )
            converted_data = {
                k: v for k, v in converted_data.items() if k not in ignore_cols
            }

        semantic_types: dict[SemanticType, list[str]] = {
            stype: [] for stype in SemanticType
        }

        for col, typ in converted_data.items():
            semantic_types[self._determine_semantic_type(col, typ)].append(col)

        return {k: v for k, v in semantic_types.items() if len(v) > 0}

    @staticmethod
    def _determine_semantic_type(col: str, typ: _DtypesValues) -> SemanticType:
        """Determine the inferred semantic type for a given column.

        Args:
            col: the column name
            typ: the pandas dtype of the column

        Returns:
            The semantic type that the column should be associated with.
        """
        # Inferred label column is explicitly categorical
        if col == BITFOUNT_INFERRED_LABEL_COLUMN:
            return SemanticType.CATEGORICAL

        # Strings (normal and bytestrings) are text
        if isinstance(typ, pd.StringDtype) or typ == str or typ == bytes:  # noqa: E721
            return SemanticType.TEXT

        # Booleans are explicitly categorical
        if isinstance(typ, pd.BooleanDtype) or typ == bool:  # noqa: E721
            return SemanticType.CATEGORICAL

        # Other numeric types are mapped to continuous
        if is_numeric_dtype(typ):
            # Booleans get interpreted as continuous, so we must define them as
            # categorical before this function is called
            return SemanticType.CONTINUOUS

        # By default, everything else will be interpreted as text.
        # This should only happen for columns which remain as `object` because
        # pandas is having trouble deciphering their true type
        return SemanticType.TEXT

    def get_feature_names(
        self, semantic_type: Optional[SemanticType] = None
    ) -> list[str]:
        """Returns the names of all the features in the schema.

        Args:
            table_name: The name of the table to get the features from.
            semantic_type: if semantic type is provided, only
                the feature names corresponding to the semantic type are returned.
                Defaults to None.

        Returns:
            features: A list of feature names.
        """
        if semantic_type is not None:
            stype = cast(_SemanticTypeValue, semantic_type.value)
            if stype in self.features:
                features = list(self.features[stype])
            else:
                logger.debug(f"There are no features with semantic type {stype}")
                features = []

        else:
            features = [
                feature_name
                for stype in self.features
                for feature_name in self.features[cast(_SemanticTypeValue, stype)]
            ]
        return features

    def get_categorical_feature_size(self, var: Union[str, list[str]]) -> int:
        """Gets the column dimensions.

        Args:
            var: A column name or a list of column names for which
                to get the dimensions.

        Returns:
            The number of unique value in the categorical column.
        """
        if isinstance(var, list):
            var = var[0]
        if "categorical" not in self.features:
            raise ValueError("No categorical features.")
        elif var not in self.features["categorical"]:
            raise ValueError(f"{var} feature not found in categorical features.")
        return self.features["categorical"][var].encoder.size

    def get_categorical_feature_sizes(
        self, ignore_cols: Optional[Union[str, list[str]]] = None
    ) -> list[int]:
        """Returns a list of categorical feature sizes.

        Args:
            ignore_cols: The column(s) to be ignored from the schema.
        """
        if not ignore_cols:
            ignore_cols = []
        elif isinstance(ignore_cols, str):
            ignore_cols = [ignore_cols]
        return [
            self.get_categorical_feature_size(var)
            for var in self.get_feature_names(SemanticType.CATEGORICAL)
            if var not in ignore_cols
        ]

    def _extract_image_cols_from_force_stype(
        self,
        col_names: Iterable[str],
        force_stype: MutableMapping[
            Union[_ForceStypeValue, _SemanticTypeValue], list[str]
        ],
    ) -> MutableMapping[_SemanticTypeValue, list[str]]:
        """Get all image columns from 'image_prefix' force_stype."""
        img_cols: list[str] = []
        if "image_prefix" in force_stype:
            img_cols = [
                col
                for col in col_names
                if any(col.startswith(stype) for stype in force_stype["image_prefix"])
            ]
        elif self.image_prefix is not None:
            img_cols = [
                col
                for col in col_names
                if any(col.startswith(stype) for stype in self.image_prefix)
            ]
        if "image" in force_stype:
            force_stype["image"] = _add_this_to_list(img_cols, force_stype["image"])
        else:
            force_stype["image"] = img_cols
        if "image_prefix" in force_stype:
            force_stype.pop("image_prefix")
        # After we extract the image features based on image prefix,
        # it's safe to cast as we remove `image_prefix` from force_stype
        return cast(MutableMapping[_SemanticTypeValue, list[str]], force_stype)

    def __eq__(self, other: Any) -> bool:
        """Compare two BitfountSchema objects for equality.

        For two schemas to be equal they must have the same set of table names and
        contents. This does not require them to have come from the same data source
        though (i.e. their hashes might be different).

        Args:
            other: The other object to compare against.

        Returns:
            True if equal, False otherwise.
        """
        # Check if exact same object
        if self is other:
            return True

        # Check comparable types
        if not isinstance(other, BitfountSchema):
            return False

        def extract_features_and_types(
            schema: BitfountSchema,
        ) -> dict[str, dict[str, tuple[Union[Dtype, np.dtype], SemanticType]]]:
            # Extract types from features
            return {
                feature_type: {
                    feature_name: (record.dtype, record.semantic_type)
                    for feature_name, record in cast(
                        dict[str, _SemanticTypeRecord], records_dict
                    ).items()
                }
                for feature_type, records_dict in schema.features.items()
            }

        # Check features and their types
        if extract_features_and_types(self) != extract_features_and_types(other):
            return False

        # Otherwise, equal for our purposes
        return True

    def decode_categorical(self, feature: str, value: int) -> Any:
        """Decode label corresponding to a categorical feature in the schema.

        Args:
            feature: The name of the feature.
            value: The encoded value.

        Returns:
            The decoded feature value.

        Raises:
            ValueError: If the feature cannot be found in the schema.
            ValueError: If the label cannot be found in the feature encoder.
        """
        if feature not in self.features["categorical"]:
            raise ValueError(
                f"Could not find {feature} in categorical features of the schema."
            )
        for k, v in self.features["categorical"][feature].encoder.classes.items():
            if v == value:
                return k

        raise ValueError(f"Could not find {value} in {feature}.")

    def get_num_continuous(
        self, ignore_cols: Optional[Union[str, list[str]]] = None
    ) -> int:
        """Get the number of (non-ignored) continuous features.

        Args:
            ignore_cols: Columns to ignore when counting continuous features.

        Return:
            The number of continuous features.
        """
        if not ignore_cols:
            ignore_cols = []
        elif isinstance(ignore_cols, str):
            ignore_cols = [ignore_cols]
        return len(
            [
                None
                for var in self.get_feature_names(SemanticType.CONTINUOUS)
                if var not in ignore_cols
            ]
        )

    def get_num_categorical(
        self, ignore_cols: Optional[Union[str, list[str]]] = None
    ) -> int:
        """Get the number of (non-ignored) categorical features.

        Args:
            ignore_cols: Columns to ignore when counting categorical features.

        Return:
            The number of categorical features.
        """
        if not ignore_cols:
            ignore_cols = []
        elif isinstance(ignore_cols, str):
            ignore_cols = [ignore_cols]
        return len(
            [
                None
                for var in self.get_feature_names(SemanticType.CATEGORICAL)
                if var not in ignore_cols
            ]
        )

    def generate_partial_schema(self, datasource: BaseSource) -> None:
        """Adds one batch of data to the schema."""
        try:
            data = next(datasource.yield_data())
            if not data.empty:
                self.schema_type = "partial"
                self.number_of_records += len(data)
                logger.info(
                    "Used the first partition from datasource for "
                    f"schema generation. Found {self.number_of_records} "
                    "records."
                )
            else:
                raise StopIteration()
        except StopIteration:
            logger.warning("Selected datasource has no data.")
            self.schema_type = "full"

    def generate_full_schema(
        self,
        datasource: BaseSource,
        force_stypes: Optional[
            MutableMapping[Union[_ForceStypeValue, _SemanticTypeValue], list[str]]
        ] = None,
        ignore_cols: Optional[list[str]] = None,
    ) -> None:
        """Generate a full schema from a datasource."""
        hook = SchemaGenerationFromYieldData(self, ignore_cols, force_stypes)
        datasource.add_hook(hook)
        for _ in datasource.yield_data():
            # Iterate through all the data to populate the schema.
            pass
        self.schema_type = "full"

    def initialize_dataless_schema(self, required_fields: dict[str, Any]) -> None:
        """Initialize the schema with required fields but no data.

        Args:
            required_fields: A dictionary with field names and their types.
        """

        for field, field_type in required_fields.items():
            # Handle Union types
            if hasattr(field_type, "__origin__") and field_type.__origin__ is Union:
                for t in field_type.__args__:
                    if t is int:
                        self.add_feature(field, SemanticType.CONTINUOUS, dtype="int")
                        break
                    elif t is float:
                        self.add_feature(field, SemanticType.CONTINUOUS, dtype="float")
                        break
                    elif t is str:
                        self.add_feature(field, SemanticType.TEXT, dtype="str")
                        break
                    elif t is pd.Timestamp or t is datetime.datetime:
                        self.add_feature(
                            field, SemanticType.TEXT, dtype=datetime.datetime
                        )
                        break
                else:
                    logger.warning(
                        f"Unsupported field type in Union: {field_type}, "
                        "cannot initialise dataless schema."
                    )
            # Handle single types
            elif field_type is int:
                self.add_feature(field, SemanticType.CONTINUOUS, dtype="int")
            elif field_type is float:
                self.add_feature(field, SemanticType.CONTINUOUS, dtype="float")
            elif field_type is str:
                self.add_feature(field, SemanticType.TEXT, dtype="str")
            elif field_type is pd.Timestamp or field_type is datetime.datetime:
                self.add_feature(field, SemanticType.TEXT, dtype=datetime.datetime)
            else:
                logger.warning(
                    f"Unsupported field type: {field_type}, cannot "
                    "initialise dataless schema with this feature."
                )

    def add_feature(
        self, feature_name: str, semantic_type: SemanticType, dtype: Any
    ) -> None:
        """Add a single feature to the schema.

        Note that this method does not support Categorical features.

        Args:
            feature_name: The name of the feature.
            semantic_type: The semantic type of the feature.
            dtype: The dtype of the feature.
        """
        if semantic_type == SemanticType.TEXT:
            TextRecord.add_record_to_schema(
                self, feature_name=feature_name, dtype=dtype
            )
        elif semantic_type == SemanticType.CONTINUOUS:
            ContinuousRecord.add_record_to_schema(
                self,
                feature_name=feature_name,
                dtype=dtype,
            )
        elif semantic_type == SemanticType.IMAGE:
            ImageRecord.add_record_to_schema(
                self, feature_name=feature_name, dtype=dtype
            )
        else:
            logger.warning(
                f"Unsupported semantic type: {semantic_type}, cannot "
                "initialise dataless schema with this feature."
            )


def _hash_str(to_hash: str) -> str:
    """Generates a sha256 hash of a given string.

    Uses UTF-8 to encode the string before hashing.
    """
    return hashlib.sha256(to_hash.encode("utf-8")).hexdigest()


def _generate_dtypes_hash(dtypes: Mapping[str, Any]) -> str:
    """Generates a hash of a column name -> column type mapping.

    Uses column names and column dtypes to generate the hash. DataFrame contents
    is NOT used.

    SHA256 is used for hash generation.

    Args:
        dtypes: The mapping to hash.

    Returns:
        The hexdigest of the mapping hash.
    """
    dtypes = {k: str(v) for k, v in dtypes.items()}
    str_rep: str = json.dumps(dtypes, sort_keys=True)
    return _hash_str(str_rep)
