"""Base interface for data persistence implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Collection, Sequence
from dataclasses import dataclass
from functools import cached_property
import logging
from multiprocessing.synchronize import Lock as _Lock
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN

if TYPE_CHECKING:
    from typing import Final, Optional, Union


_IMAGE_COL_PLACEHOLDER: Final = "<Image Data or File Path>"


_logger = logging.getLogger(__name__)


class DataPersister(ABC):
    """Abstract interface for data persistence/caching implementations."""

    def __init__(
        self,
        file_name_column: str,
        lock: Optional[_Lock] = None,
        bulk_partition_size: Optional[int] = None,
    ) -> None:
        self._lock = lock
        self._file_name_column = file_name_column

        # Underlying _bulk_get implementations can have limits on how many items we can
        # query at once so we partition here before calling _bulk_get.
        # SQLLite has a limit of 1M chars per query (https://www.sqlite.org/limits.html)
        # and file paths can get up to ~256 chars on windows/macos,
        # meaning that above 3906 files we're risking errors.
        # Other persistence implementations can have different limits so setting the
        # default to something reasonable.
        self.bulk_partition_size = (
            bulk_partition_size if bulk_partition_size is not None else 1000
        )

    def get(self, file: Union[str, Path]) -> Optional[pd.DataFrame]:
        """Get the persisted data for a given file.

        Returns None if no data has been persisted, if it is out of date, or an
        error was otherwise encountered.
        """
        # Catch underlying errors here.
        # Worst case scenario is that something cannot use the cached data.
        try:
            return self._get(file)
        except Exception as e:
            _logger.warning(f"Error whilst retrieving cache entry for {file}: {str(e)}")
            return None

    @abstractmethod
    def _get(self, file: Union[str, Path]) -> Optional[pd.DataFrame]:
        """Get the persisted data for a given file.

        Returns None if no data has been persisted or if it is out of date.
        """
        raise NotImplementedError

    def bulk_get(self, files: Sequence[Union[str, Path]]) -> BulkResult:
        """Get the persisted data for several files.

        Returns only misses if no data has been persisted, if it is out of date, or an
        error was otherwise encountered.
        """
        try:
            len_ = len(files)
            partition_results: list[BulkResult] = []
            for partition_start_idx in range(0, len_, self.bulk_partition_size):
                partition_results.append(
                    self._bulk_get(
                        files[
                            partition_start_idx : min(
                                partition_start_idx + self.bulk_partition_size, len_
                            )
                        ]
                    )
                )
            return BulkResult(
                file_name_column=self._file_name_column,
                cached=pd.concat(
                    [pr.cached for pr in partition_results if pr.cached is not None],
                    ignore_index=True,
                ),
                misses=[miss for pr in partition_results for miss in pr.misses],
            )
        except Exception as e:
            _logger.debug(f"Error whilst bulk getting cache for {files}: {str(e)}")
            return BulkResult(
                file_name_column=self._file_name_column,
                cached=None,
                misses=[Path(file) for file in files],
            )

    @abstractmethod
    def _bulk_get(self, files: Sequence[Union[str, Path]]) -> BulkResult:
        """Get the persisted data for the target files.

        Returns a dataframe containing the results.
        """
        raise NotImplementedError

    def set(self, file: Union[str, Path], data: pd.DataFrame) -> None:
        """Set the persisted data for a given file.

        If existing data is already set, it will be overwritten.

        The data should only be the data that is related to that file.
        """
        # Catch underlying errors here.
        # Worst case scenario is that something cannot use the cached data later.
        try:
            self._set(file, data)
        except Exception as e:
            _logger.warning(f"Error whilst setting cache entry for {file}: {str(e)}")

    @abstractmethod
    def _set(self, file: Union[str, Path], data: pd.DataFrame) -> None:
        """Set the persisted data for a given file.

        If existing data is already set, it will be overwritten.

        The data should only be the data that is related to that file.
        """
        raise NotImplementedError

    @abstractmethod
    def unset(self, file: Union[str, Path]) -> None:
        """Deletes the persisted data for a given file."""
        # NOTE: We do _not_ implicitly catch underlying errors here.
        # The worst case scenario is that the cache fails to be invalidated, but
        # the calling code assumes it has been.
        raise NotImplementedError

    @staticmethod
    def prep_data_for_caching(
        data: pd.DataFrame, image_cols: Optional[Collection[str]] = None
    ) -> pd.DataFrame:
        """Prepares data ready for caching.

        This involves removing/replacing things that aren't supposed to be cached
        or that it makes no sense to cache, such as image data or file paths that
        won't be relevant except for when the files are actually being used.

        Does not mutate input dataframe.
        """
        data = data.copy()
        if image_cols:
            image_cols_present = set(image_cols).intersection(data.columns)
            # Replace every NON-NULL entry in every image col with
            # _IMAGE_COL_PLACEHOLDER
            for image_col in image_cols_present:
                row_mask = data[image_col].notnull()
                data.loc[row_mask, image_col] = _IMAGE_COL_PLACEHOLDER
        return data

    def bulk_set(
        self,
        data: pd.DataFrame,
        original_file_col: str = ORIGINAL_FILENAME_METADATA_COLUMN,
    ) -> None:
        """Bulk set a bunch of cache entries from a dataframe.

        The dataframe must indicate the original file that each row is associated
        with. This is the `_original_filename` column by default.
        """
        try:
            self._bulk_set(data, original_file_col)
        except Exception as e:
            _logger.warning(
                f"Error whilst bulk setting cache entries for data;"
                f" some or all cache entries may not have been set."
                f" Error was: {str(e)}"
            )
            return None

    def _bulk_set(
        self,
        data: pd.DataFrame,
        original_file_col: str = ORIGINAL_FILENAME_METADATA_COLUMN,
    ) -> None:
        """Bulk set a bunch of cache entries from a dataframe.

        The dataframe must indicate the original file that each row is associated
        with. This is the `_original_filename` column by default.
        """
        if original_file_col not in data.columns:
            _logger.warning(
                f'Original file specifying column, "{original_file_col}",'
                f" was not found in the dataframe."
                f" Unable to bulk cache entries."
            )
            return None

        # Work on copy so we can manipulate the file paths without affecting the
        # original
        data = data.copy()

        # Remove any entries without original_col path
        if not data[data[original_file_col].isnull()].empty:
            _logger.warning(
                f'Some entries are missing entries in column "{original_file_col}";'
                f" removing these before continuing."
            )
            data = data[data[original_file_col].notnull()]

        # Replace the file paths with the canonical versions of those paths
        data[original_file_col] = data[original_file_col].map(
            lambda p: str(Path(p).resolve())
        )

        # Group the data by the original file path and submit each of these to
        # `set()` individually
        file_path_str: str
        file_data: pd.DataFrame
        for file_path, file_data in data.groupby(original_file_col):
            file_path_str = str(file_path)
            self.set(file_path_str, file_data)


@dataclass
class BulkResult:
    """Container for the results of a bulk_get result."""

    file_name_column: str
    cached: Optional[pd.DataFrame]
    misses: list[Path]

    @cached_property
    def hits(self) -> Optional[pd.Series]:
        """Ordered Series of file name hits, possibly including duplicates."""
        if self.cached is not None:
            return self.cached[self.file_name_column]
        return None

    @cached_property
    def data(self) -> Optional[pd.DataFrame]:
        """Ordered DataFrame with cached data, excluding the file names."""
        if self.cached is not None:
            return self.cached.drop(self.file_name_column, axis="columns")
        return None

    def get_cached_by_filename(self, file_name: str) -> Optional[pd.DataFrame]:
        """Dataframe with cached data for a single file.

        May contain multiple lines (e.g. for e2e files that contain several images).
        """
        if self.cached is not None:
            result = self.cached.loc[self.cached[self.file_name_column] == file_name]
            if result.empty:
                return None
            return result.drop(self.file_name_column, axis="columns")
        return None
