"""Algorithm for filtering data records based on configurable strategies."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Sequence, TypedDict, Union

from dateutil.relativedelta import relativedelta
from marshmallow import fields
import pandas as pd

from bitfount.data.datasources.base_source import BaseSource, FileSystemIterableSource
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.federated.algorithms.base import (
    BaseNonModelAlgorithmFactory,
    BaseWorkerAlgorithm,
    NoResultsModellerAlgorithm,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.utils import delegates

if TYPE_CHECKING:
    from bitfount.types import T_FIELDS_DICT

logger = _get_federated_logger(__name__)


COMBINED_ID_COLUMN = "BitfountFilterCombinedID"


@dataclass
class _FilterStrategyBase:
    """Base class for filter strategies."""

    def __post_init__(self) -> None:
        self.validate_args()

    def validate_args(self) -> None:
        """Validate the arguments for the filter strategy."""
        raise NotImplementedError

    def get_column_names(self) -> list[str]:
        """Get the column names used in the filter strategy.

        Returns:
            list[str]: List of column names used in the filter strategy.
        """
        raise NotImplementedError

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply the filter strategy to the DataFrame."""
        raise NotImplementedError


class LatestFilterArgs(TypedDict):
    """Arguments for LATEST filter strategy.

    This filtering strategy keeps only the latest records per ID.

    See dataclass for meanings of args.
    """

    date_column: str
    id_column: Union[str, list[str]]
    num_latest: int


@dataclass
class _LatestFilterStrategy(_FilterStrategyBase):
    """Filter strategy to keep only the latest records per ID.

    Args:
        date_column: The name of the column containing date information.
        id_column: Name of column (or columns) to use as the ID(s) for grouping
            and filtering the dates.
        num_latest: The number of records to return for each ID.
    """

    date_column: str
    id_column: Union[str, list[str]]
    num_latest: int = 1

    def validate_args(self) -> None:
        """Validate the arguments for the LATEST strategy."""
        if not self.date_column:
            raise ValueError("date_column is required for LATEST strategy")
        if not self.id_column:
            raise ValueError("id_column is required for LATEST strategy")
        if self.num_latest < 1:
            raise ValueError("num_latest must be at least 1")

    def get_column_names(self) -> list[str]:
        """Get the column names used in the filter strategy.

        Returns:
            list[str]: List of column names used in the filter strategy.
        """
        if isinstance(self.id_column, list):
            return [self.date_column] + self.id_column
        return [self.date_column, self.id_column]

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply the latest filter strategy to the DataFrame.

        This method filters the DataFrame to keep only the latest records
        per unique ID. It handles both single and multiple ID columns by
        creating a combined ID column if necessary. The method retains only
        the latest records for each unique ID based on the specified date column.

        Args:
            df (pd.DataFrame): The input DataFrame to be filtered.

        Returns:
            pd.DataFrame: The filtered DataFrame containing only the latest records
            for each unique ID.

        Raises:
            ValueError: If any of the specified ID columns or the date column are not
            found in the DataFrame.
        """
        if self.date_column not in df.columns:
            raise ValueError(f"Date column '{self.date_column}' not found in data")

        # Get ID column to use, either a combined ID if multiple ID columns were
        # selected, or the single ID column itself.
        if isinstance(self.id_column, list):
            for col in self.id_column:
                if col not in df.columns:
                    raise ValueError(f"ID column '{col}' not found in data")
            df[COMBINED_ID_COLUMN] = (
                df[self.id_column].astype(str).agg("-".join, axis=1)
            )
            id_column = COMBINED_ID_COLUMN
        else:
            id_column = self.id_column
            if id_column not in df.columns:
                raise ValueError(f"ID column '{id_column}' not found in data")

        # Sort, group, and filter for the latest records for the ID combination
        df.loc[:, self.date_column] = pd.to_datetime(df[self.date_column])
        df = df.sort_values([id_column, self.date_column], ascending=[True, False])
        latest_records = (
            df.groupby(id_column).head(self.num_latest).reset_index(drop=True)
        )

        logger.info(
            f"Filtered {len(df)} records down to {len(latest_records)} latest records"
        )
        return latest_records


class FrequencyFilterArgs(TypedDict, total=False):
    """Arguments for FREQUENCY filter strategy.

    This filtering strategy keeps only records with a specified
    frequency of ID occurrence.
    """

    id_column: Union[str, list[str]]
    min_frequency: int
    max_frequency: int


@dataclass
class _FrequencyFilterStrategy(_FilterStrategyBase):
    """Filter strategy to keep records based on frequency of ID occurrence."""

    id_column: Union[str, list[str]]
    min_frequency: Optional[int] = None
    max_frequency: Optional[int] = None

    def validate_args(self) -> None:
        """Validate the arguments for the FREQUENCY strategy."""
        if not self.id_column:
            raise ValueError("id_column is required for FREQUENCY strategy")
        if self.min_frequency is None and self.max_frequency is None:
            raise ValueError(
                "Either min_frequency or max_frequency "
                "must be specified for FREQUENCY strategy"
            )
        if self.min_frequency is not None and self.min_frequency < 1:
            raise ValueError("min_frequency must be a non-negative non-zero integer")
        if self.max_frequency is not None and self.max_frequency < 1:
            raise ValueError("max_frequency must be a non-negative non-zero integer")
        if (
            self.min_frequency is not None
            and self.max_frequency is not None
            and self.min_frequency > self.max_frequency
        ):
            raise ValueError(
                "min_frequency must be less than or equal to max_frequency"
            )

    def get_column_names(self) -> list[str]:
        """Get the column names used in the filter strategy.

        Returns:
            list[str]: List of column names used in the filter strategy.
        """
        if isinstance(self.id_column, list):
            return self.id_column
        return [self.id_column]

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply the frequency filter strategy to the DataFrame.

        This method filters the DataFrame based on the frequency of occurrences
        of specified ID columns. It handles both single and multiple ID columns
        by creating a combined ID column if necessary. The method retains only
        the records with IDs that meet the specified minimum and maximum frequency
        criteria.

        Args:
            df (pd.DataFrame): The input DataFrame to be filtered.

        Returns:
            pd.DataFrame: The filtered DataFrame containing only the records
            with IDs that meet the frequency criteria.

        Raises:
            ValueError: If any of the specified ID columns are not
            found in the DataFrame.
        """
        if isinstance(self.id_column, list):
            for col in self.id_column:
                if col not in df.columns:
                    raise ValueError(f"ID column '{col}' not found in data")
            df[COMBINED_ID_COLUMN] = (
                df[self.id_column].astype(str).agg("-".join, axis=1)
            )
            id_column = COMBINED_ID_COLUMN
        else:
            id_column = self.id_column
            if id_column not in df.columns:
                raise ValueError(f"ID column '{id_column}' not found in data")

        id_counts = df[id_column].value_counts()
        valid_ids = id_counts.copy()

        if self.min_frequency is not None:
            valid_ids = valid_ids[valid_ids >= self.min_frequency]
        if self.max_frequency is not None:
            valid_ids = valid_ids[valid_ids <= self.max_frequency]

        filtered_df = df[df[id_column].isin(valid_ids.index)]

        logger.info(
            f"Filtered {len(df)} records down to {len(filtered_df)} records "
            f"based on frequency criteria "
            f"(min={self.min_frequency}, max={self.max_frequency})"
        )
        return filtered_df


class AgeRangeFilterArgs(TypedDict, total=False):
    """Arguments for AGE_RANGE filter strategy.

    This filtering strategy keeps only records within a specified age range
    in a given column.
    """

    birth_date_column: str
    min_age: int
    max_age: int


@dataclass
class _AgeRangeFilterStrategy(_FilterStrategyBase):
    """Filter strategy to keep records within a specified age range."""

    birth_date_column: str
    min_age: Optional[int] = None
    max_age: Optional[int] = None

    def validate_args(self) -> None:
        """Validate the arguments for the AGE_RANGE strategy."""
        if not self.birth_date_column:
            raise ValueError("birth_date_column is required for AGE_RANGE strategy")
        if self.min_age is None and self.max_age is None:
            raise ValueError(
                "Either min_age or max_age must be specified for AGE_RANGE strategy"
            )
        if self.min_age is not None and self.min_age < 1:
            raise ValueError("min_age must be a non-negative non-zero integer")
        if self.max_age is not None and self.max_age < 1:
            raise ValueError("max_age must be a non-negative non-zero integer")
        if (
            self.min_age is not None
            and self.max_age is not None
            and self.min_age > self.max_age
        ):
            raise ValueError("min_age must be less than or equal to max_age")

    def get_column_names(self) -> list[str]:
        """Get the column names used in the filter strategy.

        Returns:
            list[str]: List of column names used in the filter strategy.
        """
        return [self.birth_date_column]

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply the age range filter strategy to the DataFrame.

        This method filters the DataFrame based on the specified age range
        in the given column. It retains only the records with dates that fall
        within the specified start and end date range.

        Args:
            df (pd.DataFrame): The input DataFrame to be filtered.

        Returns:
            pd.DataFrame: The filtered DataFrame containing only the records
            with dates that fall within the specified range.

        Raises:
            ValueError: If the specified column is not found in the DataFrame.
        """
        if self.birth_date_column not in df.columns:
            raise ValueError(f"Column '{self.birth_date_column}' not found in data")

        df.loc[:, self.birth_date_column] = pd.to_datetime(df[self.birth_date_column])

        current_date = datetime.now()
        if self.min_age is not None:
            start_date = current_date - relativedelta(years=self.min_age)
            df = df[df[self.birth_date_column] <= start_date]
        if self.max_age is not None:
            end_date = current_date - relativedelta(years=self.max_age)
            df = df[df[self.birth_date_column] >= end_date]

        logger.info(
            f"Filtered {len(df)} records based on age range criteria "
            f"(min_age={self.min_age}, max_age={self.max_age})"
        )
        return df


class FilterStrategy(str, Enum):
    """Enumeration of available filtering strategies.

    Inherits from str to allow for easy conversion to string
    and comparison with other strings.
    The ordering of the inheritance is important (first str then Enum).
    This replicates the strEnum behaviour in Python 3.11+.
    TODO: [Python 3.11] Convert to strEnum when Python 3.11 is the minimum version.
    """

    LATEST = "latest"
    FREQUENCY = "frequency"
    AGE_RANGE = "age_range"


class FilterStrategyClass(Enum):
    """Enumeration map of filter strategies to TypedDict and classes."""

    LATEST = (LatestFilterArgs, _LatestFilterStrategy)
    FREQUENCY = (FrequencyFilterArgs, _FrequencyFilterStrategy)
    AGE_RANGE = (AgeRangeFilterArgs, _AgeRangeFilterStrategy)


FilterArgs = Union[LatestFilterArgs, FrequencyFilterArgs, AgeRangeFilterArgs]


class _RecordFilter:
    """Class to handle record filtering logic."""

    def __init__(
        self, strategies: list[FilterStrategy], filter_args_list: list[FilterArgs]
    ) -> None:
        self.strategies = strategies
        self.filter_args_list = filter_args_list
        self.filters = self._parse_filter_args()
        # Use a set to handle duplicates and flatten the list of columns in use
        self.list_of_columns_in_use = list(
            {
                col
                for filter_strategy in self.filters
                for col in filter_strategy.get_column_names()
            }
        )

    def _parse_filter_args(self) -> list[_FilterStrategyBase]:
        """Convert dictionaries to the appropriate filter strategy class instances."""
        filters = []
        for strategy, filter_args in zip(self.strategies, self.filter_args_list):
            typed_dict_class, strategy_class = FilterStrategyClass[strategy.name].value
            try:
                # Attempt to convert the dictionary to the appropriate class instance
                filters.append(strategy_class(**filter_args))
            except TypeError as e:
                # Capture the error and provide a detailed message
                logger.error(
                    "Error converting filter arguments for strategy "
                    f"'{strategy}': {e}\n"
                    "Valid arguments: "
                    f"{list(typed_dict_class.__annotations__.keys())}"
                )
                logger.error("Filter will be skipped")
        return filters

    def filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply the appropriate filtering strategy to the DataFrame.

        Args:
            df: Input DataFrame

        Returns:
            Filtered DataFrame
        """
        for filter_args in self.filters:
            df = filter_args.apply(df)
        return df


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side of the algorithm."""

    def __init__(
        self,
        strategies: list[FilterStrategy],
        filter_args_list: list[FilterArgs],
        **kwargs: Any,
    ) -> None:
        """Initialize the worker-side algorithm.

        Args:
            strategies: List of filtering strategies
            filter_args_list: List of strategy-specific arguments
            **kwargs: Additional keyword arguments

        Raises:
            ValueError: If required parameters for a strategy are missing
        """
        self.record_filter = _RecordFilter(strategies, filter_args_list)

        super().__init__(**kwargs)

    def initialise(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the algorithm with data source.

        Args:
            datasource: The data source to use
            data_splitter: Optional data splitter
            pod_dp: Optional differential privacy configuration
            pod_identifier: Optional pod identifier
            **kwargs: Additional keyword arguments
        """
        self.initialise_data(datasource=datasource, data_splitter=data_splitter)

    def setup_run(self, **kwargs: Any) -> None:
        """Initial setup run that executes before any batching.

        This method is called by protocols tagged with InitialSetupProtocol
        before any batching occurs.
        """
        if not isinstance(self.datasource, FileSystemIterableSource):
            logger.warning(
                "Filtering is currently only supported for file-based sources"
            )
            return

        # Ensure use of cache data
        if (
            not hasattr(self.datasource, "data_cache")
            or self.datasource.data_cache is None
        ):
            raise ValueError("No data cache provided for filtering")

        data_iterables = []
        for data_chunk in self.datasource.yield_data(use_cache=True):
            # Select only the columns in use, ignoring missing columns
            # Ensure ORIGINAL_FILENAME_METADATA_COLUMN is included
            columns_to_include = [
                ORIGINAL_FILENAME_METADATA_COLUMN
            ] + self.record_filter.list_of_columns_in_use
            available_columns = [
                col for col in columns_to_include if col in data_chunk.columns
            ]
            data_iterables.append(data_chunk[available_columns])

        if not data_iterables:
            logger.warning("No data found in datasource")
            return

        df = pd.concat(data_iterables)
        if df is None or df.empty:
            logger.warning("No data found in concatenated DataFrame")
            return

        # Apply the appropriate filtering strategy
        df = self.record_filter.filter(df)

        # Store the filtered indices/files for subsequent algorithms
        if hasattr(self.datasource, "selected_file_names_override"):
            self.datasource.selected_file_names_override = df[
                ORIGINAL_FILENAME_METADATA_COLUMN
            ].tolist()
            logger.info(
                "Selected files successfully overridden with "
                f"{len(self.datasource.selected_file_names_override)} files"
            )
        else:
            logger.warning("Data source does not support file name override")
            return

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Regular run method - does nothing as filtering is done in setup."""
        pass


@delegates()
class RecordFilterAlgorithm(
    BaseNonModelAlgorithmFactory[NoResultsModellerAlgorithm, _WorkerSide]
):
    """Algorithm factory for filtering records based on various strategies.

    Args:
        datastructure: The data structure to use for the algorithm.
        strategies: List of filtering strategies
        filter_args_list: List of strategy-specific arguments

    Attributes:
        datastructure: The data structure to use for the algorithm
        strategies: List of filtering strategies
        filter_args_list: List of strategy-specific arguments

    Raises:
        ValueError: If required parameters for a strategy are missing
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "strategies": fields.List(
            fields.Enum(FilterStrategy),
            required=True,
        ),
        "filter_args_list": fields.List(fields.Dict(), required=True),
    }

    def __init__(
        self,
        datastructure: DataStructure,
        strategies: Sequence[Union[FilterStrategy, str]],
        filter_args_list: list[FilterArgs],
        **kwargs: Any,
    ) -> None:
        self.strategies: list[FilterStrategy] = [
            FilterStrategy(strategy) if isinstance(strategy, str) else strategy
            for strategy in strategies
        ]
        self.filter_args_list = filter_args_list
        super().__init__(datastructure=datastructure, **kwargs)

    def modeller(self, **kwargs: Any) -> NoResultsModellerAlgorithm:
        """Modeller-side of the algorithm."""
        return NoResultsModellerAlgorithm(**kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Worker-side of the algorithm."""
        return _WorkerSide(
            strategies=self.strategies,
            filter_args_list=self.filter_args_list,
            **kwargs,
        )
