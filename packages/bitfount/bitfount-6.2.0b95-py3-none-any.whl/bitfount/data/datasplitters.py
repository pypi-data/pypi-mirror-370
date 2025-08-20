"""Classes for splitting data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import hashlib
import logging
import random
from typing import TYPE_CHECKING, Any, Iterable, Optional, Union
import warnings

import desert
from marshmallow import fields
from marshmallow_union import Union as M_Union
import numpy as np
from numpy.typing import NDArray
import pandas as pd
from sklearn.model_selection import train_test_split
from typing_extensions import override

from bitfount.data.datasources.base_source import (
    FileSystemIterableSource,
)
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.data.types import DataSplit
from bitfount.types import UsedForConfigSchemas

if TYPE_CHECKING:
    from bitfount.data.datasources.base_source import (
        BaseSource,
    )

logger = logging.getLogger(__name__)
# This is used for defining the column in which the data split is
# defined for SplitterDefinedInData
BITFOUNT_SPLIT_CATEGORY_COLUMN: str = "BITFOUNT_SPLIT_CATEGORY"


class DatasetSplitter(ABC):
    """Parent class for different types of dataset splits."""

    @classmethod
    @abstractmethod
    def splitter_name(cls) -> str:
        """Returns string name for splitter type."""
        raise NotImplementedError()

    @classmethod
    def create(cls, splitter_name: str, **kwargs: Any) -> DatasetSplitter:
        """Create a DataSplitter of the requested type."""
        # We may want to replace this with an `__init_subclass_` based
        # approach if we start adding more DataSplitters
        # See: https://blog.yuo.be/2018/08/16/__init_subclass__-a-simpler-way-to-implement-class-registries-in-python/ # noqa: E501
        if splitter_name == SplitterDefinedInData.splitter_name():
            return SplitterDefinedInData(**kwargs)
        return PercentageSplitter(**kwargs)

    @abstractmethod
    def get_dataset_split_indices(
        self, data: pd.DataFrame
    ) -> tuple[NDArray[np.integer], NDArray[np.integer], NDArray[np.integer]]:
        """Returns indices for data sets."""
        raise NotImplementedError

    @abstractmethod
    def iter_dataset_split_indices(
        self, datasource: BaseSource, split: DataSplit
    ) -> Iterable[int]:
        """Yield indices/keys for a given split."""
        raise NotImplementedError

    @abstractmethod
    def iter_dataset_split(
        self,
        datasource: BaseSource,
        split: DataSplit,
        **kwargs: Any,
    ) -> Iterable[pd.DataFrame]:
        """Yield data for a given split.

        Args:
            datasource: The datasource to iterate over.
            split: The split to yield data for.
            kwargs: Additional args to pass to the underlying datasource yield_data().

        Yields:
            Dataframes that contain data for the given split.
        """
        raise NotImplementedError

    @abstractmethod
    def get_filenames(
        self,
        datasource: FileSystemIterableSource,
        split: DataSplit,
    ) -> list[str]:
        """Returns a list of filenames for a given split.

        Only used for file system sources.

        Args:
            datasource: A `FileSystemIterableSource` object.
            split: The relevant split to return filenames for.

        Returns:
            A list of filenames.
        """
        raise NotImplementedError

    @abstractmethod
    def iter_filenames(
        self,
        datasource: FileSystemIterableSource,
        split: DataSplit,
    ) -> Iterable[str]:
        """Yield filenames for a given split.

        Only used for file system sources.

        Args:
            datasource: A `FileSystemIterableSource` object.
            split: The relevant split to return filenames for.

        Yields:
            Filenames for the given split.
        """
        raise NotImplementedError

    @staticmethod
    def _handle_selected_file_names_iter_data_split(
        datasource: BaseSource, original_kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        """Utility method for handling `selected_file_names` in FSISources.

        By default `iter_data_split()` uses an unmodified call to yield_data(). In
        the case where it is a FileSystemIterableSource, and this source has a
        selected_file_names in place that differs from the normal iteration, we need
        to ensure that this is used instead of iterating the whole datasource.

        We do this by modifying the `data_keys` kwarg to be passed to the
        """
        # This is now handled in the FileSystemIterableSource.
        return original_kwargs


class _InferenceSplitter(DatasetSplitter):
    """Data split that has all data in its `test` set.

    Should not be directly used by the user.
    """

    @classmethod
    @override
    def splitter_name(cls) -> str:
        """Define the name of the splitter."""
        return "inference"

    @override
    def get_dataset_split_indices(
        self, data: pd.DataFrame
    ) -> tuple[NDArray[np.integer], NDArray[np.integer], NDArray[np.integer]]:
        """Returns indices for dataset splits."""
        return np.array([]), np.array([]), np.array([i for i in range(len(data))])

    @override
    def iter_dataset_split_indices(
        self, datasource: BaseSource, split: DataSplit
    ) -> Iterable[int]:
        """Yield indices for a given split."""
        if split == DataSplit.TEST:
            # Try cache-based approach first
            if hasattr(datasource, "get_all_cached_file_paths") and hasattr(
                datasource, "has_uncached_files"
            ):
                try:
                    if not datasource.has_uncached_files():
                        # Cache is complete, use it
                        cached_files = datasource.get_all_cached_file_paths()
                        for i in range(len(cached_files)):
                            yield i
                        return
                except Exception:
                    logger.info(
                        "Failed to get cached file paths, falling back to iteration."
                    )

            # Fallback: count as we iterate (no upfront len() call)
            # This is still efficient as it doesn't load all data into memory
            for i, _ in enumerate(datasource):
                yield i
        else:
            return

    @override
    def iter_dataset_split(
        self, datasource: BaseSource, split: DataSplit, **kwargs: Any
    ) -> Iterable[pd.DataFrame]:
        """Yield data for a given split."""
        kwargs = self._handle_selected_file_names_iter_data_split(datasource, kwargs)

        if split == DataSplit.TEST:
            yield from datasource.yield_data(**kwargs)
        else:
            return

    @override
    def get_filenames(
        self,
        datasource: FileSystemIterableSource,
        split: DataSplit,
    ) -> list[str]:
        """Returns a list of filenames for a given split.

        .. deprecated::
            This method loads all filenames into memory and is inefficient for large
            datasets. Use iter_filenames() instead for memory-efficient streaming.
        """
        warnings.warn(
            "get_filenames() is deprecated and loads all filenames into memory. "
            "Use iter_filenames() instead for better performance and memory "
            "efficiency.",
            DeprecationWarning,
            stacklevel=2,
        )
        if split == DataSplit.TEST:
            return list(datasource.selected_file_names_iter())
        else:
            return []

    @override
    def iter_filenames(
        self, datasource: FileSystemIterableSource, split: DataSplit
    ) -> Iterable[str]:
        """Yield filenames for a given split."""
        if split == DataSplit.TEST:
            yield from datasource.selected_file_names_iter()


@dataclass
class PercentageSplitter(DatasetSplitter, UsedForConfigSchemas):
    """Splits data into sets based on percentages.

    The default split is 80% of the data is used training, and 10% for each
    validation and testing, respectively.

    :::caution

    Filename splitting does not support `time_series_sort_by` and will issue a
    warning if both are used together.

    :::

    Args:
        validation_percentage: The percentage of data to be used for validation.
            Defaults to 10.
        test_percentage: The percentage of data to be used for testing.
            Defaults to 10.
        time_series_sort_by: A string/list of strings to be used for sorting
            time series. The strings should correspond to feature names from the
            dataset. This sorts the dataframe by the values of those features
            ensuring the validation and test sets come after the training set data
            to remove potential bias during training and evaluation. Defaults to None.
        shuffle: A bool indicating whether we shuffle the data for the splits.
            Defaults to True.
        iterative_splitting: A bool indicating whether to use iterative splitting
            for file-based datasources. When True, avoids the expensive len(datasource)
            call by using chunked sklearn train_test_split. Defaults to False for
            backward compatibility, but should be set to True for large datasets.
        time_series_sort_by: A string/list of strings to be used for sorting
            time series. The strings should correspond to feature names from the
            dataset. This sorts the dataframe by the values of those features
            ensuring the validation and test sets come after the training set data
            to remove potential bias during training and evaluation. Defaults to None.

    Examples:
        For large datasets over slow networks, use iterative splitting:

        ```python
        # Traditional approach (slow for large datasets)
        splitter = PercentageSplitter(test_percentage=20)

        # Iterative approach (fast for large datasets)
        splitter = PercentageSplitter(test_percentage=20, iterative_splitting=True)
        ```

        The iterative approach processes files in chunks using sklearn's
        train_test_split to maintain proper percentage distributions without requiring
        len(datasource).
    """

    validation_percentage: int = 10
    test_percentage: int = 10
    shuffle: bool = True
    # TODO: [BIT-5704] Deprecate this in favour of the new iterative splitting
    iterative_splitting: bool = False
    time_series_sort_by: Optional[Union[str, list[str]]] = desert.field(
        M_Union(
            [
                fields.String(),
                fields.List(fields.String()),
            ],
            allow_none=True,
        ),
        default=None,
    )

    def __post_init__(self) -> None:
        self.train_percentage = 100 - self.validation_percentage - self.test_percentage
        self.filenames: list[str] = []

    @classmethod
    @override
    def splitter_name(cls) -> str:
        """Define the name of the splitter."""
        return "percentage"

    @override
    def get_dataset_split_indices(
        self, data: pd.DataFrame
    ) -> tuple[NDArray[np.integer], NDArray[np.integer], NDArray[np.integer]]:
        """Returns indices for dataset splits."""
        # Sort or shuffle data depending on time_series constraint
        if self.time_series_sort_by:
            data = data.sort_values(by=self.time_series_sort_by)

        # Get indices of dataframe
        indices = data.index.to_series().to_list()

        if not self.time_series_sort_by and self.shuffle is True:
            random.shuffle(indices)

        # Create dataset splits
        train_idxs, validation_idxs, test_idxs = np.split(
            indices,
            [
                int(
                    (100 - self.validation_percentage - self.test_percentage)
                    * len(indices)
                    / 100
                ),
                int((100 - self.test_percentage) * len(indices) / 100),
            ],
        )

        # Ensure that time series constraint is enforced correctly
        if self.time_series_sort_by:
            validation_idxs, test_idxs = self._split_indices_time_series(
                validation_idxs, test_idxs, data
            )
            train_idxs, validation_idxs = self._split_indices_time_series(
                train_idxs, validation_idxs, data
            )

            if self.validation_percentage == 0 and self.test_percentage != 0:
                train_idxs, test_idxs = self._split_indices_time_series(
                    train_idxs, test_idxs, data
                )
            if self.shuffle is True:
                np.random.shuffle(train_idxs)
                np.random.shuffle(validation_idxs)
                np.random.shuffle(test_idxs)
        return train_idxs, validation_idxs, test_idxs

    @override
    def iter_dataset_split_indices(
        self, datasource: BaseSource, split: DataSplit
    ) -> Iterable[int]:
        """Yield indices for a given split."""
        # We have no guarantees on the indexing of the chunks, so we need to manually
        # track the index count so that we can use the provided indices extract from
        # chunks at a later point
        base_index = 0

        # Use a partition size of 1000 so we can get good fractional splits
        for chunk in datasource.yield_data(partition_size=1000):
            # Reindex the chunk so that it's indexed with 0...n-1 integers
            chunk_len = len(chunk)
            chunk = chunk.reset_index(drop=True)

            chunk_train_idxs, chunk_validation_idxs, chunk_test_idxs = (
                self.get_dataset_split_indices(chunk)
            )

            indices_to_use: NDArray[np.integer]
            if split == DataSplit.TRAIN:
                indices_to_use = chunk_train_idxs
            elif split == DataSplit.VALIDATION:
                indices_to_use = chunk_validation_idxs
            elif split == DataSplit.TEST:
                indices_to_use = chunk_test_idxs
            else:
                raise ValueError(f"Split type not recognised: {split}")

            for idx in indices_to_use:
                # Yield indices adjusted for the different chunks
                yield int(idx) + base_index

            # Update the base index to work for the next chunk
            base_index = base_index + chunk_len

    @override
    def iter_dataset_split(
        self, datasource: BaseSource, split: DataSplit, **kwargs: Any
    ) -> Iterable[pd.DataFrame]:
        """Yield data for a given split."""
        kwargs = self._handle_selected_file_names_iter_data_split(datasource, kwargs)

        # Use supplied partition_size, or default 1000.
        # Default of 1000 is so we can get good fractional splits
        partition_size: int = kwargs.pop("partition_size", 1000)

        if partition_size < 100:
            logger.warning(
                f"Attempting to perform iterable percentage split,"
                f" but requested partition size was {partition_size}."
                f" Partition sizes <100 are likely to produce strange results."
                f" Setting partition_size to 100."
            )
            partition_size = 100

        for chunk in datasource.yield_data(partition_size=partition_size, **kwargs):
            # Reindex the chunk so that it's indexed with 0...n-1 integers
            chunk_w_int_index = chunk.reset_index(drop=True)

            chunk_train_idxs, chunk_validation_idxs, chunk_test_idxs = (
                self.get_dataset_split_indices(chunk_w_int_index)
            )

            indices_to_use: NDArray[np.integer]
            if split == DataSplit.TRAIN:
                indices_to_use = chunk_train_idxs
            elif split == DataSplit.VALIDATION:
                indices_to_use = chunk_validation_idxs
            elif split == DataSplit.TEST:
                indices_to_use = chunk_test_idxs
            else:
                raise ValueError(f"Split type not recognised: {split}")

            chunk_split = chunk.iloc[indices_to_use]
            if not chunk_split.empty:
                yield chunk_split

    def _split_indices_time_series(
        self,
        index_array_a: NDArray[np.integer],
        index_array_b: NDArray[np.integer],
        data: pd.DataFrame,
    ) -> tuple[NDArray[np.integer], NDArray[np.integer]]:
        """Splits indices in a chronological fashion.

        Helper function which ensures that two arrays of indices of the full
        dataset do not overlap in terms of dates to ensure there is no
        information leakage. This is necessary when there is not enough
        granularity in the dates provided yet we still want to make sure that
        e.g. all the samples in the test set definitely come after the
        validation set and so on. For example in the LendingClub data we are
        only given month and year - this function ensures that the
        training/validation/test splits only occur at month boundaries.

        Args:
            index_array_a: An array of indices from the full dataset.
            index_array_b: An array of indices from the full dataset.
            data: A dataframe type object.

        Returns:
             The two arrays of indices modified by moving items from
             index_list_a into index_list_b until the condition is satisfied.
        """
        # Get the most granular time series column
        time_series_col: str
        if self.time_series_sort_by is None:
            raise ValueError(
                "Tried to split indices by time series by time series sort by"
                " column was not specified"
            )
        elif isinstance(self.time_series_sort_by, list):
            time_series_col = self.time_series_sort_by[-1]
        else:
            time_series_col = self.time_series_sort_by

        # Return if one of the arrays is empty
        if len(index_array_a) == 0 or len(index_array_b) == 0:
            return index_array_a, index_array_b

        first_val_b = data[time_series_col].loc[index_array_b[0].item()]
        last_val_a = data[time_series_col].loc[index_array_a[-1].item()]

        # Move data from a to b whilst condition is still satisfied
        while first_val_b == last_val_a:
            last_idx_a, index_array_a = index_array_a[-1], index_array_a[:-1]
            index_array_b = np.insert(index_array_b, 0, last_idx_a)

            if index_array_a.size == 0:
                raise ValueError(
                    "One or more of the training/test/validation sets ends "
                    "up empty in the _split_indices_time_series() function. "
                    "This is because one of the sets contains only one unique date."
                )
            first_val_b = data[time_series_col].loc[index_array_b[0].item()]
            last_val_a = data[time_series_col].loc[index_array_a[-1].item()]

        return index_array_a, index_array_b

    def _iter_filenames_iterative(
        self,
        datasource: FileSystemIterableSource,
        split: DataSplit,
        chunk_size: int = 1000,
    ) -> Iterable[str]:
        """Yield filenames for a given split using iterative chunked approach.

        This method doesn't require knowing the total number of files upfront.
        It processes files in chunks and uses sklearn's train_test_split to
        maintain proper percentage distributions.

        Args:
            datasource: A `FileSystemIterableSource` object.
            split: The relevant split to return filenames for.
            chunk_size: The size of the chunk to process. Defaults to 1000.

        Yields:
            Filenames for the given split.
        """
        # Get file iterator - use the most efficient approach available
        if hasattr(datasource, "_get_file_names_iterable"):
            file_iterator = datasource._get_file_names_iterable()
        elif hasattr(datasource, "selected_file_names_iter"):
            # Fallback to selected_file_names if _get_file_names_iterable not available
            file_iterator = datasource.selected_file_names_iter()
        else:
            # fallback but should not happen
            file_iterator = iter(datasource.selected_file_names)
        # Convert percentages to fractions for sklearn
        train_size = self.train_percentage / 100.0
        val_size = self.validation_percentage / 100.0
        test_size = self.test_percentage / 100.0

        # Accumulators for each split
        train_files = []
        val_files = []
        test_files = []

        # Process files in chunks
        chunk = []
        for filename in file_iterator:
            chunk.append(filename)

            if len(chunk) >= chunk_size:
                # Split this chunk and add to accumulators
                train_chunk, val_chunk, test_chunk = self._split_file_chunk(
                    chunk, train_size, val_size, test_size
                )
                train_files.extend(train_chunk)
                val_files.extend(val_chunk)
                test_files.extend(test_chunk)

                # Yield files for the requested split and clear that accumulator
                if split == DataSplit.TRAIN:
                    yield from train_files
                    train_files = []
                    # Clear unused accumulators
                    val_files = []
                    test_files = []
                elif split == DataSplit.VALIDATION:
                    yield from val_files
                    val_files = []
                    # Clear unused accumulators
                    train_files = []
                    test_files = []
                elif split == DataSplit.TEST:
                    yield from test_files
                    test_files = []
                    # Clear unused accumulators
                    train_files = []
                    val_files = []

                chunk = []

        # Process any remaining files in the final chunk
        if chunk:
            train_chunk, val_chunk, test_chunk = self._split_file_chunk(
                chunk, train_size, val_size, test_size
            )
            train_files.extend(train_chunk)
            val_files.extend(val_chunk)
            test_files.extend(test_chunk)

        # Yield any remaining files for the requested split
        if split == DataSplit.TRAIN:
            yield from train_files
        elif split == DataSplit.VALIDATION:
            yield from val_files
        elif split == DataSplit.TEST:
            yield from test_files

    def _split_file_chunk(
        self, filenames: list[str], train_size: float, val_size: float, test_size: float
    ) -> tuple[list[str], list[str], list[str]]:
        """Split a chunk of filenames using sklearn's train_test_split.

        Args:
            filenames: List of filenames to split.
            train_size: Fraction for training set.
            val_size: Fraction for validation set.
            test_size: Fraction for test set.

        Returns:
            Tuple of (train_files, val_files, test_files).
        """

        if len(filenames) == 0:
            return [], [], []

        # Use random state for deterministic splits (use seed if available)
        random_state = getattr(self, "seed", None) or 42

        # `train_test_split` doesn't support single file splits, so we need to handle
        # this case separately. If we only have one file, assign it deterministically
        # based on percentages
        if len(filenames) == 1:
            # Use simple modulo assignment for single files
            filename = filenames[0]
            hash_input = f"{filename}_{random_state}".encode()
            file_hash = int(hashlib.md5(hash_input).hexdigest(), 16) % 100  # nosec[B324:hashlib]

            if file_hash < self.train_percentage:
                return [filename], [], []
            elif file_hash < self.train_percentage + self.validation_percentage:
                return [], [filename], []
            else:
                return [], [], [filename]

        # For multiple files, use sklearn's train_test_split
        if val_size == 0 and test_size == 0:
            return filenames, [], []
        elif val_size == 0:
            train_files, test_files = train_test_split(
                filenames,
                test_size=test_size,
                random_state=random_state,
                shuffle=self.shuffle,
            )
            return train_files, [], test_files
        elif test_size == 0:
            train_files, val_files = train_test_split(
                filenames,
                test_size=val_size,
                random_state=random_state,
                shuffle=self.shuffle,
            )
            return train_files, val_files, []
        else:
            # Split into train and temp, then split temp into val and test
            train_files, temp_files = train_test_split(
                filenames,
                test_size=(val_size + test_size),
                random_state=random_state,
                shuffle=self.shuffle,
            )
            val_files, test_files = train_test_split(
                temp_files,
                test_size=test_size / (val_size + test_size),
                random_state=random_state,
                shuffle=self.shuffle,
            )
            return train_files, val_files, test_files

    @override
    def get_filenames(
        self,
        datasource: FileSystemIterableSource,
        split: DataSplit,
    ) -> list[str]:
        """Returns a list of filenames for a given split.

        .. deprecated::
            This method may be slow for large datasets due to len(datasource) usage.
            Use iter_filenames() with iterative_splitting=True instead for better
            performance and memory efficiency on large datasets.
        """
        warnings.warn(
            "get_filenames() is deprecated. Use iter_filenames() instead "
            "for better performance and memory efficiency.",
            DeprecationWarning,
            stacklevel=2,
        )
        len_datasource = len(datasource)

        if split == DataSplit.TRAIN:
            limit = int(len_datasource * self.train_percentage / 100)
            offset = 0
        elif split == DataSplit.VALIDATION:
            limit = int(len_datasource * self.validation_percentage / 100)
            offset = int(len_datasource * self.train_percentage / 100)
        elif split == DataSplit.TEST:
            limit = int(len_datasource * self.test_percentage / 100)
            offset = int(len_datasource * (100 - self.test_percentage) / 100)
        else:
            raise ValueError(f"Split type not recognised: {split}")

        return datasource.selected_file_names[offset : offset + limit]

    @override
    def iter_filenames(
        self, datasource: FileSystemIterableSource, split: DataSplit
    ) -> Iterable[str]:
        """Yield filenames for a given split."""
        if self.iterative_splitting:
            yield from self._iter_filenames_iterative(datasource, split)
        else:
            for filename in self.get_filenames(datasource, split):
                yield filename


@dataclass
class SplitterDefinedInData(DatasetSplitter, UsedForConfigSchemas):
    """Splits data into sets based on value in each row.

    The splitting is done based on the values in a user specified column.

    Args:
        column_name: The column name for which contains the labels
            for splitting. Defaults to "BITFOUNT_SPLIT_CATEGORY".
        training_set_label: The label for the data points to be included
            in the training set. Defaults to "TRAIN".
        validation_set_label: The label for the data points to be included
            in the validation set. Defaults to "VALIDATION".
        test_set_label: The label for the data points to be included in
            the test set. Defaults to "TEST".
    """

    column_name: str = BITFOUNT_SPLIT_CATEGORY_COLUMN
    training_set_label: str = "TRAIN"
    validation_set_label: str = "VALIDATION"
    test_set_label: str = "TEST"
    infer_data_split_labels: bool = False

    @classmethod
    @override
    def splitter_name(cls) -> str:
        """Define the name of the splitter."""
        return "predefined"

    @override
    def get_dataset_split_indices(
        self, data: pd.DataFrame
    ) -> tuple[NDArray[np.integer], NDArray[np.integer], NDArray[np.integer]]:
        """Returns indices for dataset splits."""
        training_indices = data[
            data[self.column_name] == self.training_set_label
        ].index.values
        validation_indices = data[
            data[self.column_name] == self.validation_set_label
        ].index.values
        test_indices = data[data[self.column_name] == self.test_set_label].index.values
        return training_indices, validation_indices, test_indices

    @override
    def iter_dataset_split_indices(
        self, datasource: BaseSource, split: DataSplit
    ) -> Iterable[int]:
        """Yield indices for a given split."""
        label_to_use: str
        if split == DataSplit.TRAIN:
            label_to_use = self.training_set_label
        elif split == DataSplit.VALIDATION:
            label_to_use = self.validation_set_label
        elif split == DataSplit.TEST:
            label_to_use = self.test_set_label
        else:
            raise ValueError(f"Split type not recognised: {split}")

        for i, data in enumerate(datasource):
            if all(data[self.column_name] == label_to_use):
                yield i

    @override
    def iter_dataset_split(
        self, datasource: BaseSource, split: DataSplit, **kwargs: Any
    ) -> Iterable[pd.DataFrame]:
        """Yield data for a given split."""
        kwargs = self._handle_selected_file_names_iter_data_split(datasource, kwargs)

        label_to_use: str
        if split == DataSplit.TRAIN:
            label_to_use = self.training_set_label
        elif split == DataSplit.VALIDATION:
            label_to_use = self.validation_set_label
        elif split == DataSplit.TEST:
            label_to_use = self.test_set_label
        else:
            raise ValueError(f"Split type not recognised: {split}")

        for chunk in datasource.yield_data(**kwargs):
            chunk_split = chunk[chunk[self.column_name] == label_to_use]
            if not chunk_split.empty:
                yield chunk_split

    @override
    def get_filenames(
        self,
        datasource: FileSystemIterableSource,
        split: DataSplit,
    ) -> list[str]:
        """Returns a list of filenames for a given split.

        .. deprecated::
            This method loads all filenames into memory and is inefficient for
            large datasets. Use iter_filenames() instead for memory-efficient
            streaming.
        """
        warnings.warn(
            "get_filenames() is deprecated and loads all filenames into memory. "
            "Use iter_filenames() instead for better performance and memory "
            "efficiency.",
            DeprecationWarning,
            stacklevel=2,
        )

        return list(self.iter_filenames(datasource, split))

    @override
    def iter_filenames(
        self, datasource: FileSystemIterableSource, split: DataSplit
    ) -> Iterable[str]:
        """Yield filenames for a given split."""
        label_to_use: str
        if split == DataSplit.TRAIN:
            label_to_use = self.training_set_label
        elif split == DataSplit.VALIDATION:
            label_to_use = self.validation_set_label
        elif split == DataSplit.TEST:
            label_to_use = self.test_set_label
        else:
            raise ValueError(f"Split type not recognised: {split}")

        # Stream approach: avoid loading all selected_file_names into memory
        for chunk in datasource.yield_data():
            filenames: list[str] = chunk[chunk[self.column_name] == label_to_use][
                ORIGINAL_FILENAME_METADATA_COLUMN
            ].tolist()

            for filename in filenames:
                if self._is_filename_selected(datasource, filename):
                    yield filename

    def _is_filename_selected(
        self, datasource: FileSystemIterableSource, filename: str
    ) -> bool:
        """Check if a filename is selected without loading all filenames into memory."""
        # Use the iterator to check if filename is selected
        for selected_filename in datasource.selected_file_names_iter():
            if selected_filename == filename:
                return True
        return False
