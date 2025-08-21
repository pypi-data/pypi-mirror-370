"""Classes concerning datasets."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict
from collections.abc import Iterator, Mapping, Sequence
from functools import cached_property
import logging
from typing import TYPE_CHECKING, Any, Literal, Optional, Union, cast, overload

from natsort import natsorted
import numpy as np
from numpy.typing import NDArray
import pandas as pd
from skimage.color import gray2rgb
from skimage.io import imread

from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
)
from bitfount.data.datasplitters import (
    DatasetSplitter,
    PercentageSplitter,
    SplitterDefinedInData,
    _InferenceSplitter,
)
from bitfount.data.exceptions import DataNotLoadedError
from bitfount.data.types import DataSplit, _DataEntryAllowingText
from bitfount.transformations.base_transformation import Transformation
from bitfount.transformations.batch_operations import BatchTimeOperation
from bitfount.transformations.parser import TransformationsParser
from bitfount.transformations.processor import TransformationProcessor
from bitfount.utils import _array_version

if TYPE_CHECKING:
    from bitfount.data.schema import BitfountSchema
    from bitfount.data.types import _JSONDict, _SemanticTypeValue

logger = logging.getLogger(__name__)


class _BaseBitfountDataset(ABC):
    """Base class for representing a dataset."""

    x_columns: list[str]
    x_var: tuple[Any, Any, np.ndarray]
    y_columns: list[str]
    y_var: np.ndarray

    embedded_col_names: list[str]
    image_columns: list[str]
    processors: dict[int, TransformationProcessor]
    image: np.ndarray
    tabular: np.ndarray
    text: np.ndarray
    support_cols: np.ndarray

    def __init__(
        self,
        datasource: BaseSource,
        data_split: DataSplit,
        selected_cols: list[str],
        selected_cols_semantic_types: Mapping[_SemanticTypeValue, list[str]],
        schema: Optional[BitfountSchema] = None,
        data_splitter: Optional[DatasetSplitter] = None,
        target: Optional[Union[str, list[str]]] = None,
        batch_transforms: Optional[list[dict[str, _JSONDict]]] = None,
        auto_convert_grayscale_images: bool = True,
        ignore_support_cols: bool = False,
        selected_col_prefix: Optional[str] = None,
        image_cols_prefix: Optional[str] = None,
        image_prefix_batch_transforms: Optional[list[dict[str, _JSONDict]]] = None,
    ) -> None:
        super().__init__()
        self.datasource = datasource
        self.schema = schema
        self.selected_cols = selected_cols
        self.selected_cols_semantic_types = selected_cols_semantic_types
        self.data_splitter = data_splitter
        self.target = target
        self.batch_transforms = batch_transforms
        self.data_split = data_split
        self.auto_convert_grayscale_images = auto_convert_grayscale_images
        self.ignore_support_cols = ignore_support_cols
        self.selected_prefix = selected_col_prefix
        self.image_cols_prefix = image_cols_prefix
        self.image_prefix_batch_transforms = image_prefix_batch_transforms
        # Empty placeholder arrays for images - will be populated later if necessary
        self.image = np.array([])
        self._set_column_name_attributes()

    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    def _apply_schema(self, data: pd.DataFrame) -> None:
        """Applies `self.schema` to `data` and sets the result to `self.data`.

        `selected_cols` needs to be passed to the `apply` method here to ensure
        that we don't end up removing the extra columns in our dataframe that are
        used during training (e.g. loss_weights_col, etc.) but aren't part of the
        schema. Applying the schema adds extra columns to the dataframe if they
        are missing. Therefore, we need to subset the data columns here to ensure
        we are only using the columns specified for this task
        """
        self._get_columns_from_prefixes(data)
        diff = sorted(set(self.selected_cols) - set(data.columns))
        if diff:
            logger.warning(
                f"Selected columns `{','.join(diff)}` "
                f"were not found in the data, continuing without them."
            )
            self.selected_cols = [i for i in self.selected_cols if i not in diff]
        if self.schema is not None:
            # Schema is None for HuggingFace datasets which is handled separately
            self.data = self.schema.apply(data, keep_cols=self.selected_cols)[
                self.selected_cols
            ].reset_index(drop=True)

    def _set_column_name_attributes(self) -> None:
        """Sets the attributes concerning column names.

        Namely, `self.x_columns`, `self.y_columns`, `self.embedded_col_names`,
        and `self.image_columns`.
        """
        self.image_columns = self.selected_cols_semantic_types.get("image", [])

        self.embedded_col_names = self.selected_cols_semantic_types.get(
            "categorical", []
        )
        self.x_columns = (
            self.embedded_col_names
            + self.selected_cols_semantic_types.get("continuous", [])
            + self.selected_cols_semantic_types.get("image", [])
        )
        if self.target is not None:
            self.y_columns = _array_version(self.target)
            self.embedded_col_names = [
                i for i in self.embedded_col_names if i not in self.y_columns
            ]
            self.x_columns = [i for i in self.x_columns if i not in self.y_columns]

    def get_batch_transformations(self) -> Optional[list[BatchTimeOperation]]:
        """Returns batch transformations to be performed as callables.

        Returns:
            A list of batch transformations to be passed to
                TransformationProcessor.
        """
        if self.batch_transforms is not None:
            parser = TransformationsParser()
            transformations, _ = parser.deserialize_transformations(
                self.batch_transforms
            )
            return cast(list[BatchTimeOperation], transformations)
        return None

    def _set_batch_transformation_processors(self) -> None:
        """Sets `self.processors` for batch transformations."""
        if (
            self.image_prefix_batch_transforms is not None
            and self.image_cols_prefix is not None
        ):
            image_batch_transforms: list[dict[str, _JSONDict]] = []
            for image_transform in self.image_prefix_batch_transforms:
                albumentations = image_transform.get("albumentations")
                if albumentations is not None:
                    for col in self.datasource.image_columns:
                        if col.startswith(self.image_cols_prefix):
                            col_specific_albumentations = albumentations.copy()
                            col_specific_albumentations["arg"] = col
                            img_transform = {
                                "albumentations": col_specific_albumentations
                            }
                            if self.batch_transforms is None:
                                image_batch_transforms.append(img_transform)
                            elif img_transform not in self.batch_transforms:
                                image_batch_transforms.append(img_transform)
                else:
                    logger.warning(
                        f"Skipping unsupported transform: "
                        f"{self.image_prefix_batch_transforms}"
                    )
            if image_batch_transforms:
                if self.batch_transforms is None:
                    self.batch_transforms = image_batch_transforms
                else:
                    self.batch_transforms += image_batch_transforms

        self.batch_transforms_parsed = self.get_batch_transformations()

        if self.batch_transforms_parsed is not None:
            # We create a dictionary mapping each image feature to the corresponding
            # list of transformations. This dictionary must be an OrderedDict so that
            # the order of the features is preserved and indexable. Currently, we only
            # support image transformations at batch time.
            feature_transforms: OrderedDict[str, list[BatchTimeOperation]] = (
                OrderedDict(
                    {i: [] for i in self.selected_cols_semantic_types.get("image", [])}
                )
            )

            for tfm in self.batch_transforms_parsed:
                if tfm.arg in feature_transforms:
                    feature_transforms[tfm.arg].append(tfm)

            # Each feature that will be transformed needs to have its own transformation
            # processor. These processors need to correspond to the index of the feature
            # to be transformed because at batch time, the feature name is unavailable -
            # we only have the feature index. Finally, we only leave transformations if
            # the 'step' corresponds to the 'step' of the Dataset. This is to optimise
            # for efficiency only since the processor will ignore transformations that
            # are not relevant to the current step at batch time anyway.
            self.processors: dict[int, TransformationProcessor] = {
                list(feature_transforms).index(col): TransformationProcessor(
                    [
                        cast(Transformation, i)
                        for i in tfms
                        if i.step == self.data_split
                    ],
                )
                for col, tfms in feature_transforms.items()
            }

    def _transform_image(self, img: np.ndarray, idx: int) -> np.ndarray:
        """Performs image transformations if they have been specified.

        Args:
            img: The image to be transformed.
            idx: The index of the image.

        Returns:
            The transformed image.

        """
        # `albumentations` (which makes up most of our image transformations)
        # normally only supports `uint8` or `float32` image arrays. We will attempt
        # to pass it through regardless, but warn the user here.
        if img.dtype not in (np.uint8, np.float32):
            logger.warning(
                f'Image array has dtype "{img.dtype}".'
                f" `albumentations` normally expects `uint8` or `float32`."
            )

        if not self.batch_transforms_parsed:
            return img

        return self.processors[idx].batch_transform(img, step=self.data_split)

    @overload
    def _load_images(
        self, idx: Union[int, Sequence[int]], what_to_load: Literal["image"] = "image"
    ) -> Union[np.ndarray, tuple[np.ndarray, ...]]:
        """Overload of _load_images()."""  # noqa: D402
        ...

    @overload
    def _load_images(
        self, idx: Union[int, Sequence[int]], what_to_load: Literal["target"]
    ) -> np.ndarray:
        """Overload of _load_images()."""  # noqa: D402
        ...

    def _load_images(
        self,
        idx: Union[int, Sequence[int]],
        what_to_load: Literal["target", "image"] = "image",
    ) -> Union[np.ndarray, tuple[np.ndarray, ...]]:
        """Loads images and performs transformations if specified.

        This involves first converting grayscale images to RGB if necessary.

        Args:
            idx: The index to be loaded.
            what_to_load: Str variable specifying whether to load 'image' or 'target'.

        Returns:
            Loaded and transformed image.

        """
        if what_to_load == "image":
            img_features = self.image[idx]
        else:  # what_to_load == "target":
            img_features = np.array([self.y_var[idx]])

        imgs: tuple[np.ndarray, ...] = tuple(
            imread(image, plugin="pil")
            for image in img_features
            if image is not pd.NA
            and image is not np.nan
            and image != [np.nan]
            and image != [pd.NA]
        )

        if len(imgs) == 0:
            return imgs

        if self.auto_convert_grayscale_images:
            try:
                imgs = tuple(
                    (
                        gray2rgb(image_array)
                        if len(image_array.squeeze().shape) < 3
                        else image_array
                    )
                    for image_array in imgs
                )
            except AttributeError:
                # If the error is due to "'str' object has no attribute 'squeeze'"
                # then we have likely fallen into an issue where the image "data" has
                # been loaded from cache and so is the placeholder string rather than
                # the image arrays. We log this detail out for easy debugging.
                if any(isinstance(image_array, str) for image_array in imgs):
                    logger.error(
                        "Image data column contained unexpected strings;"
                        " this is likely caused by loading data from the cache"
                        " rather than fresh and so we have pulled"
                        " the placeholder string."
                    )
                raise

        imgs = tuple(
            self._transform_image(image_array, i) for i, image_array in enumerate(imgs)
        )
        if len(img_features) == 1:
            return imgs[0]

        return imgs

    def _set_support_column_values(self, data: pd.DataFrame) -> None:
        """Sets `self.support_cols` - auxiliary columns for loss manipulation."""
        weights = np.ones(len(data), dtype=np.float32)
        weights = weights.reshape(len(weights), 1)
        ignore_classes = -np.ones(len(data), dtype=np.int64)
        ignore_classes = ignore_classes.reshape(len(ignore_classes), 1)
        self.support_cols = cast(
            np.ndarray, np.concatenate([weights, ignore_classes], axis=1)
        )

    def _set_image_values(self, data: pd.DataFrame) -> None:
        """Sets `self.image`."""
        # Reset the image attr
        self.image = np.array([])
        for col in natsorted(self.image_columns):
            x_img = np.expand_dims(cast(np.ndarray, data.loc[:, col].values), axis=1)
            # If there are multiple images, we start concatenating `self.image`
            # with each next image
            self.image = (
                x_img
                if self.image.size == 0
                else np.concatenate((self.image, x_img), axis=1)
            )

    def _set_tabular_values(self, data: pd.DataFrame) -> None:
        """Sets `self.tabular`."""
        x1_var = data.loc[:, self.embedded_col_names].values.astype(np.int64)
        # Fill NaTypes to make sure it does not error (due to files loading iteratively)
        # and having missing columns when loading small batches. For the
        # non-iterable datasets, this just replaces all `nan` by 0,
        # similar to the `CleanDataTransformation`.
        x2_var = (
            data.loc[:, self.selected_cols_semantic_types.get("continuous", [])]
            .fillna(value=0.0)
            .values.astype(np.float32)
        )
        self.tabular = np.concatenate([x1_var, x2_var], axis=1)

    def _set_target_values(
        self, target: Optional[Union[pd.DataFrame, pd.Series]]
    ) -> None:
        """Sets `self.y_var`."""
        if target is not None:
            self.y_var = cast(np.ndarray, target.values)
        else:
            self.y_var = np.array([])

    def _get_xy(
        self, data: pd.DataFrame
    ) -> tuple[pd.DataFrame, Optional[Union[pd.DataFrame, pd.Series]]]:
        """Returns the x and y variables.

        By default, there is no target unless `self.target` has been specified.
        """
        X, Y = data, None

        if self.target is not None:
            # ignore error if target is already not part of the X data
            X = X.drop(columns=self.target, errors="ignore").reset_index(drop=True)
            Y = data[self.target].reset_index(drop=True)
        return X, Y

    def _getitem(self, idx: Union[int, Sequence[int]]) -> _DataEntryAllowingText:
        """Returns the item referenced by index `idx` in the data."""
        raise NotImplementedError

    def _reformat_data(self, data: pd.DataFrame) -> None:
        """Reformats the data to be compatible with the Dataset class."""

        self._apply_schema(data)
        self._set_batch_transformation_processors()

        X, Y = self._get_xy(self.data)

        if self.image_columns or self.image_cols_prefix:
            self._set_image_values(X)

        self._set_tabular_values(X)

        self._set_support_column_values(X)

        # Package tabular, image and support columns together under the x_var attribute
        self.x_var = (self.tabular, self.image, self.support_cols)

        self._set_target_values(Y)

    def _get_columns_from_prefixes(self, data: pd.DataFrame) -> None:
        """Adds columns to `self.selected_cols` and `self.image_columns` by prefix.

        These lists should both be updated before calling `schema.apply` to ensure
        that the columns are correctly populated.
        """
        # First make sure that all appropriate columns are added to
        # the selected_cols by prefix
        if self.selected_prefix is not None:
            # Add columns that start with the prefix in natural order
            for col in natsorted(data.columns):
                if (
                    col.startswith(self.selected_prefix)
                    and col not in self.selected_cols
                ):
                    self.selected_cols.append(col)
        # Similarly, add image columns by prefix
        if self.image_cols_prefix is not None:
            image_columns = [
                col
                for col in data.columns
                if col.startswith(self.image_cols_prefix)
                and col not in self.image_columns
            ]
            self.image_columns += image_columns

    def get_dataset_split(
        self,
        split: DataSplit,
        data_splitter: DatasetSplitter,
    ) -> pd.DataFrame:
        """Returns the relevant portion of `self.data`.

        Args:
            split: The portion of data to return.
            data_splitter: The splitter object used to split the data.

        Returns:
            A dataframe-type object containing the data points specified by the data
            splitter.

        Raises:
            DataNotLoadedError: If data has not been loaded.
        """
        df: pd.DataFrame = pd.concat(
            data_splitter.iter_dataset_split(self.datasource, split)
        )
        return df.reset_index(drop=True)

    def _split_data(
        self,
        split_value: str,
        data_splitter: DatasetSplitter,
    ) -> NDArray[np.integer]:
        """Split the data into training, validation and test datasets.

        This method is idempotent, so it can be called multiple times without
        re-splitting the data.

        Args:
            split_value: The split value to get the indices for.
            data_splitter: An optional data splitter object.
        """
        if split_value == "train":
            return np.fromiter(
                data_splitter.iter_dataset_split_indices(
                    self.datasource, DataSplit.TRAIN
                ),
                int,
            )
        elif split_value == "validation":
            return np.fromiter(
                data_splitter.iter_dataset_split_indices(
                    self.datasource, DataSplit.VALIDATION
                ),
                int,
            )
        elif split_value == "test":
            return np.fromiter(
                data_splitter.iter_dataset_split_indices(
                    self.datasource, DataSplit.TEST
                ),
                int,
            )
        else:
            raise ValueError(f"Invalid split value: {split_value}")


class _BitfountDataset(_BaseBitfountDataset):
    """A dataset for supervised tasks.

    When indexed, returns numpy arrays corresponding to
    categorical features, continuous features, weights and target value (and
    optionally category)
    """

    def __init__(
        self,
        datasource: BaseSource,
        data_split: DataSplit,
        selected_cols: list[str],
        selected_cols_semantic_types: Mapping[_SemanticTypeValue, list[str]],
        selected_col_prefix: Optional[str] = None,
        image_cols_prefix: Optional[str] = None,
        schema: Optional[BitfountSchema] = None,
        data_splitter: Optional[DatasetSplitter] = None,
        target: Optional[Union[str, list[str]]] = None,
        batch_transforms: Optional[list[dict[str, _JSONDict]]] = None,
        image_prefix_batch_transforms: Optional[list[dict[str, _JSONDict]]] = None,
        auto_convert_grayscale_images: bool = True,
        ignore_support_cols: bool = False,
    ) -> None:
        super().__init__(
            datasource=datasource,
            data_split=data_split,
            schema=schema,
            selected_cols=selected_cols,
            selected_cols_semantic_types=selected_cols_semantic_types,
            selected_col_prefix=selected_col_prefix,
            image_cols_prefix=image_cols_prefix,
            data_splitter=data_splitter,
            target=target,
            batch_transforms=batch_transforms,
            auto_convert_grayscale_images=auto_convert_grayscale_images,
            ignore_support_cols=ignore_support_cols,
            image_prefix_batch_transforms=image_prefix_batch_transforms,
        )

        if self.data_splitter is None:
            logger.warning(
                "No datasplitter was specified during dataset creation."
                " Defaulting to InferenceSplitter."
            )
            self.data_splitter = _InferenceSplitter()

        data = self.get_dataset_split(
            split=self.data_split, data_splitter=self.data_splitter
        )
        self._reformat_data(data)

    def __len__(self) -> int:
        return len(self.x_var[0])


class _IterableBitfountDataset(_BaseBitfountDataset):
    """Iterable Dataset.

    Currently, this is only used for Database connections.
    """

    datasource: BaseSource

    def __iter__(self) -> Iterator[_DataEntryAllowingText]:
        """Iterates over the dataset."""
        raise NotImplementedError

    def get_dataset_split_length(
        self, split: DataSplit, data_splitter: Optional[DatasetSplitter] = None
    ) -> int:
        """Returns the length of the specified dataset split.

        Args:
            split: The split to get the length of.
            data_splitter: The splitter object used to split the data if the BaseSource
                does not have one.

        Returns:
            The length of the specified dataset split.

        Raises:
            DataNotLoadedError: If unable to get the length of the dataset split.
        """
        if data_splitter is not None and isinstance(
            self.datasource, FileSystemIterableSource
        ):
            return len(data_splitter.get_filenames(self.datasource, split))

        # If PercentageSplitter is used regardless of the data loader.
        if isinstance(data_splitter, PercentageSplitter):
            len_datasource = len(self.datasource)
            if split == DataSplit.TRAIN:
                return int(len_datasource * data_splitter.train_percentage / 100)
            elif split == DataSplit.VALIDATION:
                return int(len_datasource * data_splitter.validation_percentage / 100)
            elif split == DataSplit.TEST:
                return int(len_datasource * data_splitter.test_percentage / 100)

        # For _InferenceSplitter, everything is "test"
        if isinstance(data_splitter, _InferenceSplitter):
            if split == DataSplit.TEST:
                return len(self.datasource)
            else:
                return 0
        # For non-FileSystemIterableSources with SplitterDefinedInData
        if isinstance(data_splitter, SplitterDefinedInData):
            split_length = 0
            for _ in data_splitter.iter_dataset_split_indices(self.datasource, split):
                split_length += 1
            return split_length

        # `load_data` should be called to avoid this error being raised
        raise DataNotLoadedError("Unable to get length of dataset split")

    @cached_property
    def _len(self) -> int:
        """Returns the length of the dataset."""
        return self.get_dataset_split_length(
            split=self.data_split, data_splitter=self.data_splitter
        )

    def __len__(self) -> int:
        return self._len

    def yield_dataset_split(
        self,
        split: DataSplit,
        data_splitter: Optional[DatasetSplitter] = None,
    ) -> Iterator[pd.DataFrame]:
        """Returns an iterator over the relevant data split.

        Args:
            split: The portion of data to yield from.
            data_splitter: The splitter object used to split the data.

        Returns:
            A iterator of pandas dataframes containing the relevant data split.

        Raises:
            ValueError: If no query or table name has been supplied for multi-table
                data.
        """
        # We cannot use any cached data here as we must ensure that any
        # non-cacheable data (such as image data) is produced in the data
        # partition
        if data_splitter is not None:
            yield from data_splitter.iter_dataset_split(
                self.datasource, split, use_cache=False
            )
        else:
            logger.warning(
                "No data splitter provided to yield_dataset_split();"
                " yielding whole dataset."
            )

            # We cannot use any cached data here as we must ensure that any
            # non-cacheable data (such as image data) is produced in the data partition
            for data_partition in self.datasource.yield_data(use_cache=False):
                yield data_partition


class _FileSystemIterableBitfountDataset(_IterableBitfountDataset):
    """Iterable Dataset.

    Used for FileSystemIterableSource.
    This class is to overwrite _load_images and _apply_schema.
    """

    datasource: FileSystemIterableSource

    def _apply_schema(self, data: pd.DataFrame) -> None:
        """Applies `self.schema` to `data` and sets the result to `self.data`.

        `selected_cols` needs to be passed to the `apply` method here to ensure
        that we don't end up removing the extra columns in our dataframe that are
        used during training (e.g. loss_weights_col, etc.) but aren't part of the
        schema. Applying the schema adds extra columns to the dataframe if they
        are missing. Therefore, we need to subset the data columns here to ensure
        we are only using the columns specified for this task
        """
        self._get_columns_from_prefixes(data)
        diff = sorted(set(self.selected_cols) - set(data.columns))
        if diff:
            logger.warning(
                f"Selected columns `{','.join(diff)}` "
                f"were not found in the data, continuing without them."
            )
            self.selected_cols = [i for i in self.selected_cols if i not in diff]
        if self.schema is not None:
            # Schema is None for HuggingFace datasets which is handled separately
            self.data = self.schema.apply(
                data,
                keep_cols=self.selected_cols,
                image_cols=list(self.datasource.image_columns),
            )[self.selected_cols].reset_index(drop=True)

    @overload
    def _load_images(
        self, idx: Union[int, Sequence[int]], what_to_load: Literal["image"] = "image"
    ) -> Union[np.ndarray, tuple[np.ndarray, ...]]:
        """Overload of _load_images()."""  # noqa: D402
        ...

    @overload
    def _load_images(
        self, idx: Union[int, Sequence[int]], what_to_load: Literal["target"]
    ) -> np.ndarray:
        """Overload of _load_images()."""  # noqa: D402
        ...

    def _load_images(
        self,
        idx: Union[int, Sequence[int]],
        what_to_load: Literal["target", "image"] = "image",
    ) -> Union[np.ndarray, tuple[np.ndarray, ...]]:
        """Loads images and performs transformations if specified.

        This involves first converting grayscale images to RGB if necessary.

        Args:
            idx: The index to be loaded.
            what_to_load: Str variable specifying whether to load 'image' or 'target'.

        Returns:
            Loaded and transformed image.

        """
        if what_to_load == "image":
            img_features = self.image[idx]
        else:  # what_to_load == "target":
            img_features = np.array([self.y_var[idx]])

        imgs: tuple[np.ndarray, ...] = tuple(
            image
            for image in img_features
            if image is not pd.NA and image is not np.nan
        )

        if self.auto_convert_grayscale_images:
            try:
                imgs = tuple(
                    (
                        gray2rgb(image_array)
                        if len(image_array.squeeze().shape) < 3
                        else image_array
                    )
                    for image_array in imgs
                )
            except AttributeError:
                # If the error is due to "'str' object has no attribute 'squeeze'"
                # then we have likely fallen into an issue where the image "data" has
                # been loaded from cache and so is the placeholder string rather than
                # the image arrays. We log this detail out for easy debugging.
                if any(isinstance(image_array, str) for image_array in imgs):
                    logger.error(
                        "Image data column contained unexpected strings;"
                        " this is likely caused by loading data from the cache"
                        " rather than fresh and so we have pulled"
                        " the placeholder string."
                    )
                raise

        imgs = tuple(
            self._transform_image(image_array, i) for i, image_array in enumerate(imgs)
        )

        if len(img_features) == 1:
            return imgs[0]

        return imgs
