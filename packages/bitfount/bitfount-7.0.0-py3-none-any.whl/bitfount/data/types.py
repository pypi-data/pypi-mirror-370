"""Classes concerning data types."""

from __future__ import annotations

from abc import abstractmethod
import ast
from collections import Counter, OrderedDict
from collections.abc import Callable, Iterable, Mapping, Sequence
import copy
from enum import Enum
import logging
from typing import TYPE_CHECKING, Any, Literal, Optional, TypedDict, TypeVar, Union

from marshmallow import (
    Schema as MarshmallowSchema,
    ValidationError,
    fields,
    post_dump,
    post_load,
    pre_dump,
)
from marshmallow.fields import Field
from marshmallow_enum import EnumField
from mypy_extensions import Arg, KwArg
import numpy as np
import pandas as pd
from pandas._typing import Dtype
from pandas.core.dtypes.common import pandas_dtype
from typing_extensions import List, NotRequired

from bitfount.types import _Dtypes, _JSONDict
from bitfount.utils import delegates

if TYPE_CHECKING:
    from bitfount.data.datasources.base_source import BaseSource
    from bitfount.data.schema import BitfountSchema

logger = logging.getLogger(__name__)

T = TypeVar("T")
Multi = Sequence[T]
SingleOrMulti = Union[T, Multi[T]]

##################################
# Types for datasets/dataloaders #
##################################
# Data types: the individual elements that might be returned in a sample/batch/entry
_ImagesData = SingleOrMulti[np.ndarray]
_TabularData = np.ndarray
_TextData = np.ndarray
_SupportData = np.ndarray
_Y_VAR = np.ndarray

# Entry types: the composite types that may be returned from a dataset/dataloader
_TabularEntry = Union[
    tuple[tuple[_TabularData, _SupportData], _Y_VAR],
    tuple[_TabularData, _Y_VAR],
]
_TextEntry = tuple[_TextData, _Y_VAR]
_ImageEntry = Union[
    tuple[tuple[_ImagesData, _SupportData], _Y_VAR],
    tuple[_ImagesData, _Y_VAR],
]
_ImageAndTabularEntry = Union[
    tuple[tuple[_TabularData, _ImagesData, _SupportData], _Y_VAR],
    tuple[tuple[_TabularData, _ImagesData], _Y_VAR],
]
_Segmentation_ImageEntry = Union[
    tuple[tuple[_ImagesData, _SupportData], _ImagesData],
    tuple[_ImagesData, _ImagesData],
]
_Segmentation_ImageAndTabEntry = Union[
    tuple[tuple[_TabularData, _ImagesData, _SupportData], _ImagesData],
    tuple[tuple[_TabularData, _ImagesData], _ImagesData],
]
_HFSegmentation_ImageTextEntry = tuple[_ImagesData, _TextData, _Y_VAR]
_DataEntry = Union[
    _TabularEntry,
    _ImageEntry,
    _ImageAndTabularEntry,
    _Segmentation_ImageEntry,
    _Segmentation_ImageAndTabEntry,
]
_DataEntryAllowingText = Union[_HFSegmentation_ImageTextEntry, _DataEntry, _TextEntry]

# Entry types with data key: the composite types that may be returned from a
# dataset/dataloader but which also contain a key to identify the input row
_TabularEntryWithKey = Union[
    tuple[tuple[_TabularData, _SupportData], _Y_VAR, str],
    tuple[_TabularData, _Y_VAR, str],
]
_TextEntryWithKey = tuple[_TextData, _Y_VAR, str]
_ImageEntryWithKey = Union[
    tuple[tuple[_ImagesData, _SupportData], _Y_VAR, str],
    tuple[_ImagesData, _Y_VAR, str],
]
_ImageAndTabularEntryWithKey = Union[
    tuple[tuple[_TabularData, _ImagesData, _SupportData], _Y_VAR, str],
    tuple[tuple[_TabularData, _ImagesData], _Y_VAR, str],
]
_Segmentation_ImageEntryWithKey = Union[
    tuple[tuple[_ImagesData, _SupportData], _ImagesData, str],
    tuple[_ImagesData, _ImagesData, str],
]
_Segmentation_ImageAndTabEntryWithKey = Union[
    tuple[tuple[_TabularData, _ImagesData, _SupportData], _ImagesData, str],
    tuple[tuple[_TabularData, _ImagesData], _ImagesData, str],
]
_HFSegmentation_ImageTextEntryWithKey = tuple[_ImagesData, _TextData, _Y_VAR, str]
_DataEntryWithKey = Union[
    _TabularEntryWithKey,
    _ImageEntryWithKey,
    _ImageAndTabularEntryWithKey,
    _Segmentation_ImageEntryWithKey,
    _Segmentation_ImageAndTabEntryWithKey,
]
_DataEntryAllowingTextWithKey = Union[
    _HFSegmentation_ImageTextEntryWithKey, _DataEntryWithKey, _TextEntryWithKey
]

# Batch types: collections of data entries
_DataBatch = list[_DataEntry]
_DataBatchAllowingText = list[_DataEntryAllowingText]

_DataBatchWithKey = list[_DataEntryWithKey]
_DataBatchAllowingTextWithKey = list[_DataEntryAllowingTextWithKey]

# type alias for the values in the `SemanticType` enum
_SemanticTypeValue = Literal["categorical", "continuous", "image", "text"]
_ForceStypeValue = Literal["categorical", "continuous", "image", "text", "image_prefix"]
S = TypeVar("S", bound="BaseSource")
_Column = Union[np.ndarray, pd.Series]
_GetColumnCallable = Callable[
    [Arg(S, "self"), Arg(str, "col_name"), KwArg(Any)], _Column
]
_GetDtypesCallable = Callable[[Arg(S, "self"), KwArg(Any)], _Dtypes]


class DataSplit(Enum):
    """Enum corresponding to the available data splits."""

    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"


class _CamelCaseSchema(MarshmallowSchema):
    """Schema that uses camelCase for its external representation.

    snake_case is used for its internal representation.
    """

    @staticmethod
    def camel_case(s: str) -> str:
        """Converts a string from snake_case to camelCase."""
        parts = iter(s.split("_"))
        return next(parts) + "".join(i.title() for i in parts)

    def on_bind_field(self, field_name: str, field_obj: Field) -> None:
        """Converts the field's name to camelCase during hook."""
        field_obj.data_key = self.camel_case(field_obj.data_key or field_name)


class _ExtendableLabelEncoder:
    """Encodes strings as integers.

    A label encoder class which allows for building up the set of classes in multiple
    calls to `add_values` instead of having to create the set with one "fit" call.
    """

    def __init__(self) -> None:
        self.classes: dict[str, int] = {}  # Mapping from class label to index
        self.dtype = str  # Fixed to str for now

    class _Schema(MarshmallowSchema):
        classes = fields.Dict(keys=fields.Str(), values=fields.Int())

        @post_load
        def recreate_encoder(
            self, data: _JSONDict, **_kwargs: Any
        ) -> _ExtendableLabelEncoder:
            """Recreates ExtendableLabelEncoder."""
            new_encoder = _ExtendableLabelEncoder()
            new_encoder.classes = dict(data["classes"])
            return new_encoder

    def add_values(self, values: Union[np.ndarray, pd.Series]) -> None:
        """Adds all entries in the column to the set."""
        uniques: Iterable
        if isinstance(values, np.ndarray):
            uniques = sorted(set(values.astype(self.dtype)))
        else:
            uniques = sorted(set(values.astype(self.dtype).tolist()))

        # Remove classes that are already present in `self.classes`
        new_uniques = sorted(u for u in uniques if u not in self.classes)
        cur_size = len(self.classes)

        # Adds a label for each new class by incrementing the previously largest label
        for i, new_val in enumerate(new_uniques):
            self.classes[new_val] = i + cur_size

    def add_values_with_encoding(self, values: Mapping[str, int]) -> None:
        """Adds all entries in the column to the set.

        This is used for the schema override in order to make
        sure that the encodings are the user defined encodings.

        Args:
            values: A mapping of strings to integer encodings, defined by the modeller.
        """
        for value, mapping in values.items():
            self.classes[value] = mapping

    def transform(self, values: pd.Series) -> list[int]:
        """Transforms the given column and returns it as a list of encoded values.

        Args:
            values: The column to encode as a `pandas.Series`.

        Returns:
            A list of encoded values.

        Raises:
            ValueError: If the encoder encounters a previously unseen label.
        """
        previously_unseen_label: str
        try:
            return [self.classes[v] for v in values.astype(self.dtype).tolist()]
        except KeyError as err:
            previously_unseen_label = str(err)
            logger.debug(f"Previously unseen label: {previously_unseen_label}")
        # If the encoder fails, we also try to see if it is
        # mapping different null types incorrectly
        try:
            replaced_values = values.replace({np.nan: None})
            return [
                self.classes[v] for v in replaced_values.astype(self.dtype).tolist()
            ]
        except Exception:
            logger.debug(
                f"Failed to interpret {previously_unseen_label} as a None type. "
                f"Trying to interpret as datetime."
            )

        # If the encoder encounters a previously unseen label, we instead try to
        # interpret it as a datetime and see if there is a match there instead.
        # This is done because the same datetime can have multiple different formats
        # and pandas and numpy display these differently when converting to a string
        # so we try to convert them into the same format before encoding.
        logger.debug(f"Interpreting {previously_unseen_label} as a datetime.")
        try:
            classes = {}
            for _cls, val in self.classes.items():
                date = str(pd.to_datetime(_cls))
                classes[date] = val

            # We first try to see if there is a match once the schema label has been
            # converted into a datetime. If there is no match, this could be due to an
            # empty time component in the value to be encoded so we try again after
            # adding this.
            return [
                classes.get(v, classes[str(pd.to_datetime(v))])
                for v in values.astype(self.dtype).tolist()
            ]
        except Exception:
            logger.debug(
                f"Failed to interpret {previously_unseen_label} as a datetime."
            )

        raise ValueError(f"Previously unseen label: {previously_unseen_label}")

    @property
    def size(self) -> int:
        """Number of values in the encoder."""
        return len(self.classes)

    def __eq__(self, other: Any) -> bool:
        if self.classes == other.classes and self.dtype == other.dtype:
            return True
        return False

    def __hash__(self) -> int:
        return hash((self.classes, self.dtype))


class SemanticType(Enum):
    """Simple wrapper for some basic data types."""

    CATEGORICAL = "categorical"
    CONTINUOUS = "continuous"
    IMAGE = "image"
    TEXT = "text"


class _SemanticTypeRecord:
    """Simple semantic type wrapper for an individual record.

    Args:
        feature_name (str): name of the feature
        dtype (Union[Dtype, np.dtype]): data type of the feature
        description (str, optional): description of the feature. Defaults to None.
    """

    def __init__(
        self,
        feature_name: str,
        dtype: Union[Dtype, np.dtype, type[np.generic]],
        description: Optional[str] = None,
    ) -> None:
        self.feature_name = feature_name
        self.dtype: Union[Dtype, np.dtype, type[np.generic]] = dtype
        self.description = description

    @property
    def dtype_name(self) -> str:
        """The string name of the dtype.

        Returns "unknown" if unable to resolve.
        """
        # self.dtype can be any of:
        #   - ExtensionDtype
        #   - str instance
        #   - np.dtype
        #   - explicit types: str, complex, bool, object
        #   - np scalar type (e.g. np.uint8)

        # Handles ExtensionDtype and np.dtype
        if hasattr(self.dtype, "name"):
            return self.dtype.name
        # Handles explicit types and np scalar types
        elif isinstance(self.dtype, type):
            return self.dtype.__name__
        # Handles str instance
        elif isinstance(self.dtype, str):
            return self.dtype
        else:
            return "unknown"

    @property
    @abstractmethod
    def semantic_type(self) -> SemanticType:
        """Returns the relevant SemanticType for the class."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def add_record_to_schema(
        cls, schema: BitfountSchema, **constructor_arguments: Any
    ) -> None:
        """Creates record and adds it to schema features."""
        raise NotImplementedError

    class _Schema(_CamelCaseSchema):
        feature_name = fields.Str()
        dtype = fields.Str()
        semantic_type = EnumField(
            SemanticType,
            by_value=True,
        )
        description = fields.Str(allow_none=True)

        @post_dump
        def sort_alphabetically(self, data: _JSONDict, **kwargs: Any) -> _JSONDict:
            """Sorts the keys of the dictionary alphabetically after dumping.

            The exception is `featureName` which is moved to be the first key.
            """
            data = OrderedDict(dict(sorted(data.items())))
            data.move_to_end("featureName", last=False)
            return dict(data)

        @staticmethod
        def convert_dtype(data: _JSONDict) -> _JSONDict:
            """Converts `dtype` from string representation to actual dtype.

            Raises:
                ValidationError: if the dtype can't be deciphered
            """
            try:
                data["dtype"] = pandas_dtype(data["dtype"])
            except TypeError as e:
                raise ValidationError(
                    f"Continuous record `{data['feature_name']}` expected a "
                    f"valid np.dtype or a pandas dtype but received: `{data['dtype']}`."
                ) from e
            return data


@delegates()
class CategoricalRecord(_SemanticTypeRecord):
    """Stores information for a categorical feature in the schema.

    Args:
        encoder: An encoder for the different categories. Defaults to None.
    """

    def __init__(
        self,
        encoder: Optional[_ExtendableLabelEncoder] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self.encoder: _ExtendableLabelEncoder = (
            encoder if encoder is not None else _ExtendableLabelEncoder()
        )

    @property
    def semantic_type(self) -> SemanticType:
        """Property for the relevant `SemanticType` for the class.

        Returns:
            The categorical `SemanticType`.
        """
        return SemanticType.CATEGORICAL

    @classmethod
    def add_record_to_schema(
        cls, schema: BitfountSchema, **constructor_arguments: Any
    ) -> None:
        """Create a categorical record and add it to the schema features.

        Args:
            schema: A `TableSchema` object.
            **constructor_arguments: Additional arguments to pass to the schema class.
        """
        record = cls(**constructor_arguments)
        if "categorical" not in schema.features:
            schema.features["categorical"] = {record.feature_name: record}
        else:
            schema.features["categorical"][record.feature_name] = record

    @classmethod
    def add_new_encodings_to_schema(
        cls, schema: BitfountSchema, **constructor_arguments: Any
    ) -> None:
        """Create a categorical record and add it to the schema features.

        Args:
            schema: A `TableSchema` object.
            **constructor_arguments: Additional arguments to pass to the schema class.
        """
        record = cls(**constructor_arguments)
        if "categorical" not in schema.features:
            schema.features["categorical"] = {record.feature_name: record}
        else:
            schema.features["categorical"][record.feature_name] = record

    class _Schema(_SemanticTypeRecord._Schema):
        encoder = fields.Nested(_ExtendableLabelEncoder._Schema)

        @post_load
        def recreate_record(self, data: _JSONDict, **_kwargs: Any) -> CategoricalRecord:
            """Recreates CategoricalRecord."""
            data = self.convert_dtype(data)
            return CategoricalRecord(**data)


@delegates()
class TextRecord(_SemanticTypeRecord):
    """Stores information for a text feature in the schema."""

    @property
    def semantic_type(self) -> SemanticType:
        """Property for the relevant `SemanticType` for the class.

        Returns:
            The text `SemanticType`.
        """
        return SemanticType.TEXT

    @classmethod
    def add_record_to_schema(
        cls, schema: BitfountSchema, **constructor_arguments: Any
    ) -> None:
        """Create a text record and add it to schema features.

        Args:
            schema: A `TableSchema` object.
            **constructor_arguments: Additional arguments to pass to the schema class.
        """
        record = cls(**constructor_arguments)
        if "text" not in schema.features:
            schema.features["text"] = {record.feature_name: record}
        else:
            schema.features["text"][record.feature_name] = record

    class _Schema(_SemanticTypeRecord._Schema):
        @post_load
        def recreate_record(self, data: _JSONDict, **_kwargs: Any) -> TextRecord:
            """Recreates TextRecord."""
            data = self.convert_dtype(data)
            return TextRecord(**data)


@delegates()
class ContinuousRecord(_SemanticTypeRecord):
    """Stores information for a continuous feature in the schema."""

    @property
    def semantic_type(self) -> SemanticType:
        """Property for the relevant `SemanticType` for the class.

        Returns:
            The continuous `SemanticType`.
        """
        return SemanticType.CONTINUOUS

    @classmethod
    def add_record_to_schema(
        cls, schema: BitfountSchema, **constructor_arguments: Any
    ) -> None:
        """Create a continuous record and add it to schema features.

        Args:
            schema: A `TableSchema` object.
            **constructor_arguments: Additional arguments to pass to the schema class.
        """
        record = cls(**constructor_arguments)
        if "continuous" not in schema.features:
            schema.features["continuous"] = {record.feature_name: record}
        else:
            schema.features["continuous"][record.feature_name] = record

    class _Schema(_SemanticTypeRecord._Schema):
        @post_load
        def recreate_record(self, data: _JSONDict, **_kwargs: Any) -> ContinuousRecord:
            """Recreates ContinuousRecord."""
            data = self.convert_dtype(data)
            return ContinuousRecord(**data)


class StrDictFieldSchemaReqs(fields.Field):
    """Field that can be a specific string or a dict mapping those strings to data sources."""  # noqa: E501

    allowed_strings: List[str] = ["empty", "partial", "full"]

    def _deserialize(
        self,
        value: Any,
        attr: Optional[str],
        data: Optional[Mapping[str, Any]],
        **kwargs: Any,
    ) -> Union[str, dict]:
        # Check if the value is one of the allowed strings
        if isinstance(value, str):
            if value in self.allowed_strings:
                return value
            else:
                raise ValidationError(
                    f"Field must be one of {self.allowed_strings} if it is a string."
                )

        # Check if the value is a dictionary
        elif isinstance(value, dict):
            invalid_keys = [key for key in value if key not in self.allowed_strings]
            if invalid_keys:
                raise ValidationError(
                    f"Invalid keys in dict. Allowed keys are {self.allowed_strings}. "
                    f"Invalid keys: {invalid_keys}"
                )
            return value

        # If it's neither a valid string nor a valid dict, raise an error
        raise ValidationError(
            f"Field must be a string (one of {self.allowed_strings}) "
            "or a dict mapping these strings to data sources."
        )


@delegates()
class ImageRecord(_SemanticTypeRecord):
    """Stores information for an image feature in the schema."""

    def __init__(
        self,
        dimensions: Optional[Counter] = None,
        modes: Optional[Counter] = None,
        formats: Optional[Counter] = None,
        **kwargs: Any,
    ) -> None:
        """Stores information for an image feature in the schema.

        Args:
            dimensions: The dimensions of the different images in
                the column. Defaults to None.
            modes: The modes of the different images in the column.
                Defaults to None.
            formats: The formats of the different images in the
                column. Defaults to None.
            **kwargs: Additional arguments to pass to the parent class.
        """
        super().__init__(**kwargs)

        self.dimensions: Counter = dimensions if dimensions is not None else Counter()
        self.modes: Counter = modes if modes is not None else Counter()
        self.formats: Counter = formats if formats is not None else Counter()

    @property
    def semantic_type(self) -> SemanticType:
        """Property for the relevant `SemanticType` for the class.

        Returns:
            The image `SemanticType`.
        """
        return SemanticType.IMAGE

    @classmethod
    def add_record_to_schema(
        cls, schema: BitfountSchema, **constructor_arguments: Any
    ) -> None:
        """Create an image record and add it to schema features.

        Args:
            schema: A `BitfountSchema` object.
            **constructor_arguments: Additional arguments to pass to the schema class.
        """
        record = cls(**constructor_arguments)
        if "image" not in schema.features:
            schema.features["image"] = {record.feature_name: record}
        else:
            schema.features["image"][record.feature_name] = record

    class _Schema(_SemanticTypeRecord._Schema):
        dimensions = fields.Dict()
        formats = fields.Dict()
        modes = fields.Dict()

        @pre_dump
        def get_image_features(self, obj: ImageRecord, **_kwargs: Any) -> ImageRecord:
            """Converts image features from Counters to dictionaries."""
            temp_schema = copy.deepcopy(obj)
            # Ignoring these mypy assignment errors so that we can dump the image
            # properties as dictionaries for ease and readability
            temp_schema.dimensions = {  # type: ignore[assignment] # Reason: see comment
                str(key): value
                for key, value in dict(obj.dimensions.most_common()).items()
            }
            temp_schema.modes = {  # type: ignore[assignment] # Reason: see comment
                str(key): value for key, value in dict(obj.modes.most_common()).items()
            }
            temp_schema.formats = {  # type: ignore[assignment] # Reason: see comment
                str(key): value
                for key, value in dict(obj.formats.most_common()).items()
            }
            return temp_schema

        @post_load
        def deserialize_image_features(
            self, data: _JSONDict, **_kwargs: Any
        ) -> ImageRecord:
            """Converts image features back to Counters from dictionaries."""
            data["dimensions"] = Counter(
                {
                    ast.literal_eval(key): value
                    for key, value in data["dimensions"].items()
                }
            )
            data["modes"] = Counter(data["modes"])
            data["formats"] = Counter(data["formats"])
            data = self.convert_dtype(data)
            return ImageRecord(**data)


class _FeatureDict(TypedDict):
    """Typed dictionary for the features in a TableSchema.

    NotRequired indicates that the keys don't all need to be present. But the keys
    that are present need to be one of the ones listed below.
    """

    categorical: NotRequired[dict[str, CategoricalRecord]]
    continuous: NotRequired[dict[str, ContinuousRecord]]
    image: NotRequired[dict[str, ImageRecord]]
    text: NotRequired[dict[str, TextRecord]]


class DataPathModifiers(TypedDict):
    """TypedDict class for path modifiers.

    NotRequired indicates that the keys don't all need to be present. But the keys
    that are present need to be one of the ones listed below.

    Args:
        suffix: The suffix to be used for modifying a path.
        prefix: The prefix to be used for modifying a path.
    """

    suffix: NotRequired[str]
    prefix: NotRequired[str]


SchemaOverrideMapping = Mapping[
    _SemanticTypeValue, list[Union[str, Mapping[str, Mapping[str, int]]]]
]


class DataSourceType(Enum):
    """Available datasource names from `bitfount.data.datasources`."""

    CSVSource = "bitfount.CSVSource"
    DICOMSource = "bitfount.DICOMSource"
    ImageSource = "bitfount.ImageSource"
    OMOPSource = "bitfount.OMOPSource"
    # Ophthalmology Datasources
    DICOMOphthalmologySource = "bitfount.DICOMOphthalmologySource"
    HeidelbergSource = "bitfount.HeidelbergSource"
