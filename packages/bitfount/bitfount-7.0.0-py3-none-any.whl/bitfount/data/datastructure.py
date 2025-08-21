"""Classes concerning data structures.

DataStructures provide information about the columns of a BaseSource for a specific
Modelling Job.
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
import inspect
import logging
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Literal,
    Optional,
    Union,
    cast,
)

import desert
from marshmallow import fields
from natsort import natsorted

from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.exceptions import DataStructureError
from bitfount.data.schema import BitfountSchema
from bitfount.data.types import (
    DataSourceType,
    DataSplit,
    SchemaOverrideMapping,
    SemanticType,
    StrDictFieldSchemaReqs,
    _ForceStypeValue,
    _SemanticTypeRecord,
    _SemanticTypeValue,
)
from bitfount.transformations.base_transformation import TRANSFORMATION_REGISTRY
from bitfount.types import (
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    _BaseSerializableObjectMixIn,
    _JSONDict,
)
from bitfount.utils import _add_this_to_list

if TYPE_CHECKING:
    from bitfount.data.datasources.base_source import BaseSource
    from bitfount.runners.config_schemas.common_schemas import DataSplitConfig
    from bitfount.runners.config_schemas.modeller_schemas import (
        DataStructureAssignConfig,
        DataStructureSelectConfig,
        DataStructureTableConfig,
        DataStructureTransformConfig,
    )

logger = logging.getLogger(__name__)

DEFAULT_IMAGE_TRANSFORMATIONS: list[Union[str, _JSONDict]] = [
    {"Resize": {"height": 224, "width": 224}},
    "Normalize",
    "ToTensorV2",
]
# Define the allowed keys as a Literal type
ALLOWED_SCHEMA_TYPES = Literal["empty", "partial", "full"]

# Define the type for the argument
SCHEMA_REQUIREMENTS_TYPES = Union[ALLOWED_SCHEMA_TYPES, Dict[ALLOWED_SCHEMA_TYPES, Any]]
# OMOPSource is not compatible with the datastructure because it has a multitable schema
COMPATIBLE_DATASOURCES = [ds.name for ds in DataSourceType if ds.name != "OMOPSource"]

_registry: dict[str, type[BaseDataStructure]] = {}
registry: Mapping[str, type[BaseDataStructure]] = MappingProxyType(_registry)


@dataclass
class BaseDataStructure:
    """Base DataStructure class."""

    @classmethod
    def __init_subclass__(cls, **kwargs: Any):
        if not inspect.isabstract(cls):
            logger.debug(f"Adding {cls.__name__}: {cls} to registry")
            _registry[cls.__name__] = cls


@dataclass
class DataStructure(BaseDataStructure, _BaseSerializableObjectMixIn):
    """Information about the columns of a BaseSource.

    This component provides the desired structure of data
    to be used by discriminative machine learning models.

    :::note

    If the datastructure includes image columns, batch transformations will be applied
    to them.

    :::

    Args:
        schema_requirements: The schema requirements for the data. This is either a
            string from the list ["none", "partial", "full"], or a mapping from
            each the elements of the list to different datasources. Defaults to
            "partial" for all datasource types.
        target: The training target column or list of columns.
        ignore_cols: A list of columns to ignore when getting the
            data. Defaults to None.
        selected_cols: A list of columns to select when getting the
            data. The order of this list determines the order in which the columns are
            fed to the model. Defaults to None.
        selected_cols_prefix: A prefix to use for selected columns. Defaults to None.
        image_prefix: A prefix to use for image columns. Defaults to None.
        image_prefix_batch_transforms: A mapping of image prefixes to batch transform to apply.
        data_splitter: Approach used for splitting the data into training, test,
            validation. Defaults to None.
        image_cols: A list of columns that will be treated as images in the data.
        batch_transforms: A dictionary of transformations to apply to batches.
            Defaults to None.
        dataset_transforms: A dictionary of transformations to apply to
            the whole dataset. Defaults to None.
        auto_convert_grayscale_images: Whether or not to automatically convert grayscale
            images to RGB. Defaults to True.
        table:  Defaults to None. Deprecated.

    Raises:
        DataStructureError: If 'sql_query' is provided as well as either `selected_cols`
            or `ignore_cols`.
        DataStructureError: If both `ignore_cols` and `selected_cols` are provided.
        ValueError: If a batch transformation name is not recognised.

    """  # noqa: E501

    # TODO: [BIT-3616] Revisit serialisation of datastructure
    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "target": fields.Raw(allow_none=True),
        "schema_requirements": StrDictFieldSchemaReqs(allow_none=True),
        # `ignore_cols` is intentionally not serialised because it can be reconstructed
        # from the `selected_cols`. Furthermore, when it comes to deserialisation, the
        # datastructure can only accept one of these 2 arguments
        "selected_cols": fields.List(fields.Str(), allow_none=True),
        "selected_cols_prefix": fields.Str(allow_none=True),
        "image_cols": fields.List(fields.Str(), allow_none=True),
        "image_prefix": fields.Str(allow_none=True),
        "batch_transforms": fields.List(
            fields.Dict(
                keys=fields.Str(),
                values=fields.Dict(keys=fields.Str()),
            ),
            allow_none=True,
        ),
        "image_prefix_batch_transforms": fields.List(
            fields.Dict(
                keys=fields.Str(),
                values=fields.Dict(keys=fields.Str()),
            ),
            allow_none=True,
        ),
        "dataset_transforms": fields.List(
            fields.Dict(
                keys=fields.Str(),
                values=fields.Dict(keys=fields.Str()),
            ),
            allow_none=True,
        ),
        "auto_convert_grayscale_images": fields.Boolean(),
        "compatible_datasources": fields.List(
            fields.Str(), default=COMPATIBLE_DATASOURCES
        ),
    }
    nested_fields: ClassVar[T_NESTED_FIELDS] = {}
    table: Optional[Union[str, Mapping[str, str]]] = None
    schema_requirements: SCHEMA_REQUIREMENTS_TYPES = "partial"
    schema_types_override: Optional[
        Union[SchemaOverrideMapping, Mapping[str, SchemaOverrideMapping]]
    ] = None
    target: Optional[Union[str, list[str]]] = None
    ignore_cols: list[str] = desert.field(
        fields.List(fields.String()), default_factory=list
    )
    selected_cols: list[str] = desert.field(
        fields.List(fields.String()), default_factory=list
    )
    compatible_datasources: list[str] = desert.field(
        fields.List(fields.String()), default_factory=lambda: COMPATIBLE_DATASOURCES
    )
    selected_cols_prefix: Optional[str] = None
    data_splitter: Optional[DatasetSplitter] = None
    image_cols: Optional[list[str]] = None
    image_prefix: Optional[str] = None
    batch_transforms: Optional[list[dict[str, _JSONDict]]] = None
    dataset_transforms: Optional[list[dict[str, _JSONDict]]] = None
    auto_convert_grayscale_images: bool = True
    image_prefix_batch_transforms: Optional[list[dict[str, _JSONDict]]] = None

    def __post_init__(self) -> None:
        self.class_name = type(self).__name__
        if isinstance(self.schema_requirements, str):
            self.schema_requirements = {
                self.schema_requirements: [ds for ds in self.compatible_datasources]
            }
        if self.selected_cols and self.ignore_cols:
            raise DataStructureError(
                "Invalid parameter specification. "
                "Please provide either columns to select (selected_cols) or "
                "to ignore (ignore_cols), not both."
            )
        if self.dataset_transforms is not None:
            self.set_columns_after_transformations(self.dataset_transforms)
        self._force_stype: MutableMapping[
            Union[_ForceStypeValue, _SemanticTypeValue], list[str]
        ] = {}
        if self.image_cols:
            self._force_stype["image"] = self.image_cols

        if (
            self.batch_transforms is None
            and self.image_prefix_batch_transforms is None
            and self.image_cols
        ):
            default_image_transformations = []
            for col in self.image_cols:
                for step in DataSplit:
                    default_image_transformations.append(
                        {
                            "albumentations": {
                                "arg": col,
                                "output": True,
                                "transformations": DEFAULT_IMAGE_TRANSFORMATIONS,
                                "step": step.value,
                            }
                        }
                    )
            self.batch_transforms = default_image_transformations

        # Ensure specified batch transformations are all valid transformations
        if self.batch_transforms is not None:
            invalid_batch_transforms = []
            for _dict in self.batch_transforms:
                for tfm in _dict:
                    if tfm not in TRANSFORMATION_REGISTRY:
                        invalid_batch_transforms.append(tfm)
            if invalid_batch_transforms:
                raise ValueError(
                    f"The following batch transformations are not recognised: "
                    f"{', '.join(sorted(invalid_batch_transforms))}."
                )

        # Create mapping of all feature names used in training together with the
        # corresponding semantic type. This is the final mapping that will be used
        # to decide which features will be actually be used.
        self.selected_cols_w_types: dict[_SemanticTypeValue, list[str]] = {}

    @classmethod
    def create_datastructure(
        cls,
        select: DataStructureSelectConfig,
        transform: DataStructureTransformConfig,
        assign: DataStructureAssignConfig,
        data_split: Optional[DataSplitConfig] = None,
        schema_requirements: SCHEMA_REQUIREMENTS_TYPES = "partial",
        compatible_datasources: list[str] = COMPATIBLE_DATASOURCES,
        table_config: Optional[DataStructureTableConfig] = None,
        *,
        schema: Optional[BitfountSchema],
    ) -> DataStructure:
        """Creates a datastructure based on the yaml config and pod schema.

        Args:
            select: Configuration for columns to be included/excluded.
            transform: Configuration for dataset and batch transformations.
            assign: Configuration for special columns.
            data_split: Configuration for splitting the data.
            schema_requirements: Schema requirements for the data.
                Defaults to "partial" schema for all datasources.
            compatible_datasources: The datasources that are compatible
                with the datastructure.
            table_config: The table in the Pod schema to be used for local data.
            schema: The Bitfount schema of the target pod.

        Returns:
            A `DataStructure` object.
        """
        # Resolve ignored and selected columns
        if (select.include or select.include_prefix) and select.exclude:
            raise DataStructureError(
                "Please provide either columns to include or to "
                "exclude from data, not both."
            )
        ignore_cols = select.exclude if select.exclude is not None else []
        selected_cols = select.include if select.include is not None else []
        if schema is not None and schema.features is not None:
            # Process image_prefix, include_prefix, and batch_transforms
            image_cols, selected_cols, batch_transforms = (
                _process_prefixes_and_transforms(
                    schema=schema,
                    image_prefix=assign.image_prefix,
                    include_prefix=select.include_prefix,
                    image_transforms=transform.image,
                    batch_transforms=transform.batch,
                    image_cols=assign.image_cols or [],
                    selected_cols=select.include or [],
                )
            )
        else:
            image_cols = assign.image_cols or []
            batch_transforms = None
            selected_cols = []
            ignore_cols = []
        # Create data splitter
        data_splitter = None
        if data_split is not None:
            data_splitter = DatasetSplitter.create(
                data_split.data_splitter, **data_split.args
            )
        # Create and return datastructure
        return cls(
            schema_requirements=schema_requirements,
            compatible_datasources=compatible_datasources,
            target=assign.target,
            ignore_cols=ignore_cols,
            selected_cols=selected_cols,
            image_cols=image_cols,
            batch_transforms=batch_transforms,
            dataset_transforms=transform.dataset,
            auto_convert_grayscale_images=transform.auto_convert_grayscale_images,
            data_splitter=data_splitter,
            image_prefix=assign.image_prefix,
            selected_cols_prefix=select.include_prefix,
            image_prefix_batch_transforms=transform.image,
        )

    def get_columns_ignored_for_training(self, schema: BitfountSchema) -> list[str]:
        """Adds all the extra columns that will not be used in model training.

        Args:
            schema: The schema of the table.

        Returns:
            ignore_cols_aux: A list of columns that will be ignored when
                training a model.
        """
        if self.selected_cols:
            self.ignore_cols = [
                feature
                for feature in schema.get_feature_names()
                if feature not in self.selected_cols
            ]
        ignore_cols_aux = self.ignore_cols[:]
        ignore_cols_aux = _add_this_to_list(self.target, ignore_cols_aux)
        return ignore_cols_aux

    def set_training_input_size(self, schema: BitfountSchema) -> None:
        """Get the input size for model training.

        Args:
            schema: The schema of the table.
            table_name: The name of the table.
        """
        self.input_size = len(
            [
                col
                for col in schema.get_feature_names()
                if col not in self.get_columns_ignored_for_training(schema)
                and col not in schema.get_feature_names(SemanticType.TEXT)
            ]
        )

    def set_training_column_split_by_semantic_type(
        self, schema: BitfountSchema
    ) -> None:
        """Sets the column split by type from the schema.

        This method splits the selected columns from the dataset
        based on their semantic type.

        Args:
            schema: The `TableSchema` for the data.
        """
        if not self.selected_cols and not self.ignore_cols:
            # If neither selected_cols or ignore_cols are provided,
            # select all columns from schema,
            self.selected_cols = schema.get_feature_names()
        elif self.selected_cols:
            # Make sure we set self.ignore_cols
            self.ignore_cols = [
                feature
                for feature in schema.get_feature_names()
                if feature not in self.selected_cols
            ]
        else:
            # Make sure we set self.selected_cols
            self.selected_cols = [
                feature
                for feature in schema.get_feature_names()
                if feature not in self.ignore_cols
            ]
        if self.target and self.target not in self.selected_cols:
            self.selected_cols = _add_this_to_list(self.target, self.selected_cols)
        # Get the list of all columns ignored for training
        ignore_cols_aux = self.get_columns_ignored_for_training(schema)

        # Populate mapping of all feature names used in training
        # together with the corresponding semantic type
        for stype, features in schema.features.items():
            columns_stype_list = list(cast(dict[str, _SemanticTypeRecord], features))

            # Iterating over `self.selected_cols` ensures we preserve the order that the
            # user specified the columns
            self.selected_cols_w_types[cast(_SemanticTypeValue, stype)] = [
                col
                for col in self.selected_cols
                if (col in columns_stype_list and col not in ignore_cols_aux)
            ]
        # Add mapping to empty list for all stypes not present
        # in the current datastructure
        all_stypes = [stype.value for stype in SemanticType]
        for stype in all_stypes:
            if stype not in self.selected_cols_w_types:
                self.selected_cols_w_types[cast(_SemanticTypeValue, stype)] = []

    def set_columns_after_transformations(
        self, transforms: list[dict[str, _JSONDict]]
    ) -> None:
        """Updates the selected/ignored columns based on the transformations applied.

        It updates `self.selected_cols` by adding on the new names of columns after
        transformations are applied, and removing the original columns unless
        explicitly specified to keep.

        Args:
            transforms: A list of transformations to be applied to the data.
        """
        for tfm in transforms:
            for key, value in tfm.items():
                if key == "convert_to":
                    # Column name doesn't change if we only convert type.
                    pass
                else:
                    # Check to see if any original columns are marked to keep
                    original_cols_to_keep = value.get("keep_original", [])

                    # Make a list of all the columns to be discarded
                    if isinstance(value["col"], str):
                        value["col"] = [value["col"]]
                    discard_columns = [
                        col for col in value["col"] if col not in original_cols_to_keep
                    ]
                    new_columns = [f"{col}_{key}" for col in value["col"]]
                    # Error raised in the pods if we set both ignore_cols
                    # and selected_cols here.
                    if self.selected_cols:
                        self.selected_cols.extend(new_columns)
                    else:
                        self.ignore_cols.extend(discard_columns)
                    self.selected_cols = [
                        col for col in self.selected_cols if col not in discard_columns
                    ]

    def apply_dataset_transformations(self, datasource: BaseSource) -> BaseSource:
        """Applies transformations to whole dataset.

        Args:
            datasource: The `BaseSource` object to be transformed.

        Returns:
            datasource: The transformed datasource.
        """
        if self.dataset_transforms:
            # TODO: [BIT-1167] Process dataset transformations
            raise NotImplementedError()

        return datasource


def _process_prefixes_and_transforms(
    datastructure: Optional[DataStructure] = None,
    schema: Optional[BitfountSchema] = None,
    image_prefix: Optional[str] = None,
    include_prefix: Optional[str] = None,
    image_transforms: Optional[list[dict]] = None,
    batch_transforms: Optional[list[dict]] = None,
    image_cols: Optional[list[str]] = None,
    selected_cols: Optional[list[str]] = None,
) -> tuple[list[str], list[str], Optional[list[dict[str, _JSONDict]]]]:
    """Handles processing of image_prefix, include_prefix, and batch_transforms.

    Args:
        datastructure: The DataStructure object.
        schema: The Bitfount schema of the target pod.
        image_prefix: Prefix to identify image columns.
        include_prefix: Prefix to include in selected columns.
        image_transforms: List of image transformation configurations.
        batch_transforms: List of batch transformation configurations.
        image_cols: Existing image columns list.
        selected_cols: Existing selected columns list.

    Returns:
        A tuple containing updated image_cols, selected_cols, and batch_transforms.
    """
    if datastructure:
        # Use class-level defaults if arguments are not provided
        image_prefix = (
            image_prefix
            if image_prefix is not None
            else getattr(datastructure, "image_prefix", None)
        )
        include_prefix = (
            include_prefix
            if include_prefix is not None
            else getattr(datastructure, "selected_cols_prefix", None)
        )
        image_transforms = (
            image_transforms
            if image_transforms is not None
            else getattr(datastructure, "image_prefix_batch_transforms", [])
        )
        batch_transforms = (
            batch_transforms
            if batch_transforms is not None
            else getattr(datastructure, "batch_transforms", [])
        )
        image_cols = (
            image_cols
            if image_cols is not None
            else getattr(datastructure, "image_cols", [])
        )
        selected_cols = (
            selected_cols
            if selected_cols is not None
            else getattr(datastructure, "selected_cols", [])
        )
    selected_cols = selected_cols or []
    image_cols = image_cols or []
    updated_batch_transforms = batch_transforms
    if schema is not None:
        # Handle image_prefix
        if image_prefix is not None:
            for col in schema.get_feature_names():
                if col.startswith(image_prefix) and col not in image_cols:
                    image_cols.append(col)

        # Handle include_prefix
        if include_prefix is not None:
            for col in natsorted(schema.get_feature_names()):
                if col.startswith(include_prefix) and col not in selected_cols:
                    selected_cols.append(col)

        # Generate batch_transforms from image transforms
        if image_transforms:
            image_batch_transforms: list[dict[str, _JSONDict]] = []
            for image_transform in image_transforms:
                albumentations = image_transform.get("albumentations")
                if albumentations is not None:
                    for col in image_cols:
                        col_specific_albumentations = albumentations.copy()
                        col_specific_albumentations["arg"] = col
                        image_batch_transforms.append(
                            {"albumentations": col_specific_albumentations}
                        )
                else:
                    logger.warning(f"Skipping unsupported transform: {image_transform}")
            if image_batch_transforms:
                if updated_batch_transforms is None:
                    updated_batch_transforms = image_batch_transforms
                else:
                    updated_batch_transforms += image_batch_transforms

    return image_cols, selected_cols, updated_batch_transforms
