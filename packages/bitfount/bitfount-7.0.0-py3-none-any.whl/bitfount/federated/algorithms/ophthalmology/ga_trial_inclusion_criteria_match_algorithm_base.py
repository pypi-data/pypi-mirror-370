"""Base classes for criteria match algorithms."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
import datetime
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Mapping, Optional, cast

from marshmallow import fields
import pandas as pd
from typing_extensions import override

from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.federated.algorithms.base import (
    BaseNonModelAlgorithmFactory,
    BaseWorkerAlgorithm,
    NoResultsModellerAlgorithm,
    T_WorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    _BITFOUNT_PATIENT_ID_KEY,
    AGE_COL,
    CNV_THRESHOLD,
    DOB_COL,
    ELIGIBILE_VALUE,
    ELIGIBILITY_COL,
    LARGEST_GA_LESION_LOWER_BOUND,
    LARGEST_LEGION_SIZE_COL_PREFIX,
    MAX_CNV_PROBABILITY_COL_PREFIX,
    NAME_COL,
    SCAN_DATE_COL,
    TOTAL_GA_AREA_COL_PREFIX,
    TOTAL_GA_AREA_LOWER_BOUND,
    TOTAL_GA_AREA_UPPER_BOUND,
)
from bitfount.federated.algorithms.ophthalmology.trial_inclusion_filters import (
    ColumnFilter,
)
from bitfount.federated.exceptions import AlgorithmError, DataProcessingError
from bitfount.federated.logging import _get_federated_logger
from bitfount.utils.pandas_utils import calculate_ages

if TYPE_CHECKING:
    from bitfount.federated.privacy.differential import DPPodConfig
    from bitfount.types import T_FIELDS_DICT


logger = _get_federated_logger("bitfount.federated")


class BaseGATrialInclusionWorkerAlgorithm(BaseWorkerAlgorithm, ABC):
    """Base worker side class for all GA trial inclusion criteria match algorithms.

    This base algorithm is designed to find patients that match a set of
    clinical criteria. The baseline criteria are as follows:
    1. Total GA area between TOTAL_GA_AREA_LOWER_BOUND and TOTAL_GA_AREA_UPPER_BOUND
    2. Largest GA lesion size greater than LARGEST_GA_LESION_LOWER_BOUND
    3. No CNV (CNV probability less than CNV_THRESHOLD)
    """

    def __init__(
        self,
        *,
        cnv_threshold: float = CNV_THRESHOLD,
        largest_ga_lesion_lower_bound: float = LARGEST_GA_LESION_LOWER_BOUND,
        largest_ga_lesion_upper_bound: Optional[float] = None,
        total_ga_area_lower_bound: float = TOTAL_GA_AREA_LOWER_BOUND,
        total_ga_area_upper_bound: float = TOTAL_GA_AREA_UPPER_BOUND,
        patient_age_lower_bound: Optional[int] = None,
        patient_age_upper_bound: Optional[int] = None,
        renamed_columns: Optional[Mapping[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self.cnv_threshold = cnv_threshold

        self.largest_ga_lesion_lower_bound = largest_ga_lesion_lower_bound
        self.largest_ga_lesion_upper_bound = largest_ga_lesion_upper_bound

        self.total_ga_area_lower_bound = total_ga_area_lower_bound
        self.total_ga_area_upper_bound = total_ga_area_upper_bound

        self.patient_age_lower_bound = patient_age_lower_bound
        self.patient_age_upper_bound = patient_age_upper_bound

        self.renamed_columns = renamed_columns

    def initialise(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Sets Datasource."""
        self.initialise_data(datasource=datasource, data_splitter=data_splitter)

    def get_base_column_filters(self) -> list[ColumnFilter]:
        """Returns the basic column filters common to all GA algorithms.

        These are the most fundamental filters that all variants might use.
        Subclasses should extend this with their specific filters.
        """
        total_ga_area_column = self._get_column_name(TOTAL_GA_AREA_COL_PREFIX)
        largest_lesion_column = self._get_column_name(LARGEST_LEGION_SIZE_COL_PREFIX)
        max_cnv_column = self._get_column_name(MAX_CNV_PROBABILITY_COL_PREFIX)
        age_column = self._get_column_name(AGE_COL)

        column_filters = [
            ColumnFilter(
                column=max_cnv_column,
                operator="<=",
                value=self.cnv_threshold,
            ),
            ColumnFilter(
                column=largest_lesion_column,
                operator=">=",
                value=self.largest_ga_lesion_lower_bound,
            ),
            ColumnFilter(
                column=total_ga_area_column,
                operator=">=",
                value=self.total_ga_area_lower_bound,
            ),
            ColumnFilter(
                column=total_ga_area_column,
                operator="<=",
                value=self.total_ga_area_upper_bound,
            ),
        ]
        if self.largest_ga_lesion_upper_bound is not None:
            column_filters.append(
                ColumnFilter(
                    column=largest_lesion_column,
                    operator="<=",
                    value=self.largest_ga_lesion_upper_bound,
                )
            )
        if self.patient_age_lower_bound is not None:
            column_filters.append(
                ColumnFilter(
                    column=age_column,
                    operator=">=",
                    value=self.patient_age_lower_bound,
                )
            )
        if self.patient_age_upper_bound is not None:
            column_filters.append(
                ColumnFilter(
                    column=age_column,
                    operator="<=",
                    value=self.patient_age_upper_bound,
                )
            )
        return column_filters

    def _get_column_name(self, column_prefix: str) -> str:
        """Get the actual column name using renamed_columns if present.

        This is helpful for any algorithm that uses renamed columns.
        """
        if self.renamed_columns and column_prefix in self.renamed_columns:
            return self.renamed_columns[column_prefix]
        return column_prefix

    @abstractmethod
    def _add_age_col(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add age column to the dataframe based on the DOB column.

        If an age column is already present, should just return the dataframe unchanged.

        Args:
            df: the original dataframe

        Returns:
            The same dataframe with the extra age column.
        """
        pass


class BaseGATrialInclusionAlgorithmFactory(
    BaseNonModelAlgorithmFactory[NoResultsModellerAlgorithm, T_WorkerSide],
    ABC,
):
    """Base factory class for all GA trial inclusion criteria match algorithms."""

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "cnv_threshold": fields.Float(allow_none=True),
        "largest_ga_lesion_lower_bound": fields.Float(allow_none=True),
        "largest_ga_lesion_upper_bound": fields.Float(allow_none=True),
        "total_ga_area_lower_bound": fields.Float(allow_none=True),
        "total_ga_area_upper_bound": fields.Float(allow_none=True),
        "patient_age_lower_bound": fields.Integer(allow_none=True),
        "patient_age_upper_bound": fields.Integer(allow_none=True),
    }

    def __init__(
        self,
        datastructure: DataStructure,
        cnv_threshold: float = CNV_THRESHOLD,
        largest_ga_lesion_lower_bound: float = LARGEST_GA_LESION_LOWER_BOUND,
        largest_ga_lesion_upper_bound: Optional[float] = None,
        total_ga_area_lower_bound: float = TOTAL_GA_AREA_LOWER_BOUND,
        total_ga_area_upper_bound: float = TOTAL_GA_AREA_UPPER_BOUND,
        patient_age_lower_bound: Optional[int] = None,
        patient_age_upper_bound: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(datastructure=datastructure, **kwargs)
        self.cnv_threshold = cnv_threshold

        self.largest_ga_lesion_lower_bound = largest_ga_lesion_lower_bound
        self.largest_ga_lesion_upper_bound = largest_ga_lesion_upper_bound

        self.total_ga_area_lower_bound = total_ga_area_lower_bound
        self.total_ga_area_upper_bound = total_ga_area_upper_bound

        self.patient_age_lower_bound = patient_age_lower_bound
        self.patient_age_upper_bound = patient_age_upper_bound

    def modeller(self, **kwargs: Any) -> NoResultsModellerAlgorithm:
        """Modeller-side of the algorithm."""
        return NoResultsModellerAlgorithm(
            log_message="Running Trial Inclusion Criteria Match Algorithm",
            **kwargs,
        )


#############################
# Single Eye Algorithm
#############################
class BaseGATrialInclusionWorkerAlgorithmSingleEye(BaseGATrialInclusionWorkerAlgorithm):
    """Base worker class for single eye ga trial inclusion criteria match algorithms.

    This algorithm uses the same baseline criteria as the superclass:
    1. Total GA area between TOTAL_GA_AREA_LOWER_BOUND and TOTAL_GA_AREA_UPPER_BOUND
    2. Largest GA lesion size greater than LARGEST_GA_LESION_LOWER_BOUND
    3. No CNV (CNV probability less than CNV_THRESHOLD)
    """

    def run(
        self,
        dataframe: pd.DataFrame,
    ) -> tuple[int, int]:
        """Finds number of patients that match the clinical criteria.

        Args:
            dataframe: The dataframe to process.

        Returns:
            A tuple of counts of patients that match the clinical criteria.
            Tuple is of form (match criteria, don't match criteria).
        """
        if (
            self.patient_age_lower_bound is not None
            or self.patient_age_upper_bound is not None
        ):
            dataframe = self._add_age_col(dataframe)

        matched_df = self._filter_by_criteria(dataframe)

        num_matches = len(matched_df)
        return num_matches, len(dataframe) - num_matches

    def _apply_common_criteria(self, row: pd.Series, patient_name_hash: str) -> bool:
        """Apply common filtering criteria between Amethyst and Bronze algorithms.

        Returns:
            True if all common criteria pass, False otherwise.
        """
        # Requirement: lower bound < Total GA area < upper bound
        ga_area_entry = row[TOTAL_GA_AREA_COL_PREFIX]
        # TODO: [NO_TICKET: Imported from ophthalmology] Should this be `any()`
        #       or `all()`
        if not (
            (ga_area_entry > self.total_ga_area_lower_bound)
            and (ga_area_entry < self.total_ga_area_upper_bound)
        ):
            logger.debug(
                f"Patient {patient_name_hash} excluded due to"
                f" total GA area being out of bounds"
            )
            return False

        # Requirement: Largest GA lesion > lower bound
        ga_lesion_entry = row[LARGEST_LEGION_SIZE_COL_PREFIX]
        if not (ga_lesion_entry > self.largest_ga_lesion_lower_bound):
            logger.debug(
                f"Patient {patient_name_hash} excluded due to"
                f" largest GA lesion size being smaller than target"
            )
            return False

        # Requirement: Largest GA lesion < upper bound
        if self.largest_ga_lesion_upper_bound is not None:
            if not (ga_lesion_entry < self.largest_ga_lesion_upper_bound):
                logger.debug(
                    f"Patient {patient_name_hash} excluded due to"
                    f" largest GA lesion size being larger than target"
                )
                return False

        # Requirement: Patient older than minimum (inclusive)
        if self.patient_age_lower_bound is not None:
            age_entry = row[AGE_COL]
            if not (age_entry >= self.patient_age_lower_bound):
                logger.debug(
                    f"Patient {patient_name_hash} excluded due to being younger"
                    f" than minimum age requirement."
                )
                return False

        # Requirement: Patient younger than maximum (inclusive)
        if self.patient_age_upper_bound is not None:
            age_entry = row[AGE_COL]
            if not (age_entry <= self.patient_age_upper_bound):
                logger.debug(
                    f"Patient {patient_name_hash} excluded due to being older"
                    f" than maximum age requirement."
                )
                return False

        # Requirement: Eye does not have CNV
        cnv_entry = row[MAX_CNV_PROBABILITY_COL_PREFIX]
        if cnv_entry >= self.cnv_threshold:
            logger.debug(
                f"Patient {patient_name_hash} excluded due to CNV in one or both eyes"
            )
            return False

        return True

    def _filter_by_criteria(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter the dataframe based on the clinical criteria.

        This is an abstract method that should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _filter_by_criteria")

    @override
    def _add_age_col(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add age column to the dataframe based on the DOB column.

        If an age column is already present, should just return the dataframe unchanged.

        Args:
            df: the original dataframe

        Returns:
            The same dataframe with the extra age column.
        """
        if AGE_COL in df.columns:
            logger.warning(
                f"Age column ({AGE_COL}) has already been added to this dataframe,"
                f" not adding again."
            )
            return df

        if DOB_COL not in df.columns:
            raise ValueError(
                f"DataFrame contained no column called {DOB_COL}; cannot calculate age."
            )

        df[DOB_COL] = pd.to_datetime(df[DOB_COL], utc=True)
        try:
            age_series: pd.Series[int] = calculate_ages(df[DOB_COL])
        except OverflowError:
            # If the difference in time is too large, we will get an OverflowError.
            # This should only happen when the DOB is unknown and set to
            # `pd.Timestamp.min` as a placeholder.
            now = pd.to_datetime("now", utc=True)
            age_series = (
                now.to_pydatetime() - df[DOB_COL].dt.to_pydatetime()
            ) // timedelta(days=365.25)

        df[AGE_COL] = age_series

        return df


class BaseGATrialInclusionAlgorithmFactorySingleEye(
    BaseGATrialInclusionAlgorithmFactory[BaseGATrialInclusionWorkerAlgorithmSingleEye]
):
    """Base factory class single eye GA trial inclusion criteria match algorithms."""

    def worker(self, **kwargs: Any) -> BaseGATrialInclusionWorkerAlgorithmSingleEye:
        """Worker-side of the algorithm.

        This is an abstract method that should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement worker.")


#############################
# Both Eyes Algorithm
#############################
class BaseGATrialInclusionWorkerAlgorithmBothEyes(BaseGATrialInclusionWorkerAlgorithm):
    """Base worker side class for criteria match algorithms that handle both eyes.

    This base algorithm is designed to find patients that match a set of
    clinical criteria. The criteria are as follows:
    1. There are scans for both eyes for the same patient,
      taken within 24 hours of each other
    2. Age greater than or equal to PATIENT_AGE_LOWER_BOUND
    3. Total GA area between TOTAL_GA_AREA_LOWER_BOUND and TOTAL_GA_AREA_UPPER_BOUND
    4. Largest GA lesion size greater than LARGEST_GA_LESION_LOWER_BOUND
    5. No CNV in either eye (CNV probability less than CNV_THRESHOLD)
    """

    def __init__(
        self,
        *,
        cnv_threshold: float = CNV_THRESHOLD,
        largest_ga_lesion_lower_bound: float = LARGEST_GA_LESION_LOWER_BOUND,
        largest_ga_lesion_upper_bound: Optional[float] = None,
        total_ga_area_lower_bound: float = TOTAL_GA_AREA_LOWER_BOUND,
        total_ga_area_upper_bound: float = TOTAL_GA_AREA_UPPER_BOUND,
        patient_age_lower_bound: Optional[int] = None,
        patient_age_upper_bound: Optional[int] = None,
        renamed_columns: Optional[Mapping[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            cnv_threshold=cnv_threshold,
            largest_ga_lesion_lower_bound=largest_ga_lesion_lower_bound,
            total_ga_area_lower_bound=total_ga_area_lower_bound,
            total_ga_area_upper_bound=total_ga_area_upper_bound,
            renamed_columns=renamed_columns,
            largest_ga_lesion_upper_bound=largest_ga_lesion_upper_bound,
            patient_age_lower_bound=patient_age_lower_bound,
            patient_age_upper_bound=patient_age_upper_bound,
            **kwargs,
        )
        self._static_cols: list[str] = [NAME_COL]

        # Define the base paired column prefixes that all both-eyes implementations need
        self._paired_col_prefixes: list[str] = [
            DOB_COL,
            TOTAL_GA_AREA_COL_PREFIX,
            LARGEST_LEGION_SIZE_COL_PREFIX,
            MAX_CNV_PROBABILITY_COL_PREFIX,
            SCAN_DATE_COL,
            _BITFOUNT_PATIENT_ID_KEY,
        ]

        # Set up standard column names
        self.name_col = NAME_COL
        self.dob_col = DOB_COL
        self.total_ga_area = TOTAL_GA_AREA_COL_PREFIX
        self.largest_legion_size = LARGEST_LEGION_SIZE_COL_PREFIX
        self.max_cnv_probability = MAX_CNV_PROBABILITY_COL_PREFIX
        self.age_col = AGE_COL
        self.scan_date_col = SCAN_DATE_COL
        self.bitfount_patient_id = _BITFOUNT_PATIENT_ID_KEY

        # Initialize paired column tracking
        self._paired_cols: Optional[defaultdict[str, list[str]]] = None

    def _get_all_paired_cols(self) -> list[str]:
        """Get all the paired column names as a single list."""
        if self._paired_cols is None:
            return []
        else:
            return [col for col_list in self._paired_cols.values() for col in col_list]

    def update_renamed_columns(self) -> None:
        """Update the renamed columns."""
        if self.renamed_columns:
            renamed_static_cols = []
            for col in self._static_cols:
                if col in self.renamed_columns.keys():
                    renamed_static_cols.append(self.renamed_columns[col])
                else:
                    renamed_static_cols.append(col)
            self._static_cols = renamed_static_cols

            renamed_paired_cols_list = []
            for col in self._paired_col_prefixes:
                if col in self.renamed_columns.keys():
                    renamed_paired_cols_list.append(self.renamed_columns[col])
                else:
                    renamed_paired_cols_list.append(col)
            self._paired_col_prefixes = renamed_paired_cols_list

            if self.dob_col in self.renamed_columns.keys():
                self.dob_col = self.renamed_columns[self.dob_col]
            if self.name_col in self.renamed_columns.keys():
                self.name_col = self.renamed_columns[self.name_col]
            if self.total_ga_area in self.renamed_columns.keys():
                self.total_ga_area = self.renamed_columns[self.total_ga_area]
            if self.largest_legion_size in self.renamed_columns.keys():
                self.largest_legion_size = self.renamed_columns[
                    self.largest_legion_size
                ]
            if self.max_cnv_probability in self.renamed_columns.keys():
                self.max_cnv_probability = self.renamed_columns[
                    self.max_cnv_probability
                ]
            if self.age_col in self.renamed_columns.keys():
                self.age_col = self.renamed_columns[self.age_col]
            if self.scan_date_col in self.renamed_columns.keys():
                self.scan_date_col = self.renamed_columns[self.scan_date_col]
            if self.bitfount_patient_id in self.renamed_columns.keys():
                self.bitfount_patient_id = self.renamed_columns[
                    self.bitfount_patient_id
                ]

    @override
    def _add_age_col(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add age column to the dataframe based on the DOB column.

        If an age column is already present, should just return the dataframe unchanged.

        Args:
            df: the original dataframe

        Returns:
            The same dataframe with the extra age column.
        """
        # This should already be set post _get_df_for_criteria()
        if self._paired_cols is None:
            raise AlgorithmError(
                "self._paired_cols not populated"
                " when calling _add_age_col"
                " in a Both Eyes trial inclusion algorithm."
            )

        # Check if age column is already present, exit early if so
        if len(self._paired_cols[AGE_COL]) > 0:
            logger.warning(
                f"Age columns ({', '.join(self._paired_cols[AGE_COL])}) have already"
                f" been added to this dataframe, not adding again."
            )
            return df

        # TODO: [NO_TICKET: Imported from ophthalmology] This needs to happen across
        #       two cols atm as it's included in the post-merge suffixing; should
        #       ideally just be the one column
        # df[_DOB_COL] = pd.to_datetime(df[_DOB_COL], utc=True)
        # now = pd.to_datetime("now", utc=True)
        # # This gets us the year-only element of the timedelta (i.e. age)
        # df[_AGE_COL] = (now - df[_DOB_COL]).astype("timedelta64[Y]")  # type: ignore[operator] # Reason: df["dob"] is a Series[Timestamp], so this works # noqa: E501
        now = pd.to_datetime("now", utc=True)
        for dob_col in self._paired_cols[self.dob_col]:
            df[dob_col] = pd.to_datetime(df[dob_col], utc=True)

            dob_col_suffix = dob_col[len(self.dob_col) :]  # e.g. _L or _R
            age_col = f"{AGE_COL}{dob_col_suffix}"
            self._paired_cols[AGE_COL].append(age_col)

            # This gets us the year-only element of the timedelta (i.e. age)
            try:
                age_series: pd.Series[int] = calculate_ages(df[dob_col], now)
            except OverflowError:
                # If the difference in time is too large, we will get an OverflowError.
                # This should only happen when the DOB is unknown and set to
                # `pd.Timestamp.min` as a placeholder.
                age_series = (
                    now.to_pydatetime() - df[dob_col].dt.to_pydatetime()
                ) / datetime.timedelta(days=365.25)

            df[age_col] = age_series
        return df

    def _get_df_for_criteria(self, matched_csv_path: Path) -> pd.DataFrame:
        """Gets a dataframe from a CSV file but only the columns we care about."""
        # This file could be very large, so we read it in chunk-wise, drop the columns
        # we don't care about, and concatenate
        filtered_chunks: list[pd.DataFrame] = []
        for chunk in pd.read_csv(matched_csv_path, chunksize=100, index_col=False):
            chunk = cast(pd.DataFrame, chunk)
            chunk = self._filter_chunk(chunk)
            filtered_chunks.append(chunk)
        return pd.concat(filtered_chunks, axis="index", ignore_index=True)

    def _filter_chunk(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """Filters out columns from a chunk that we don't need."""
        # If we've not found the paired columns yet, find them
        if self._paired_cols is None:
            paired_cols = defaultdict(list)

            # Find the set of columns that start with any of the
            # self._paired_col_prefixes strings.
            #
            # Map them to the prefix they matched against.
            for col in chunk.columns:
                col_str = str(col)
                for col_prefix in self._paired_col_prefixes:
                    if col_str.startswith(col_prefix):
                        logger.debug(f"Found paired col {col_str}")
                        paired_cols[col_prefix].append(col_str)
            self._paired_cols = paired_cols
            logger.debug(f"Paired cols are: {self._get_all_paired_cols()}")

        # Return only the subset of the chunk that correspond to the columns we
        # care about
        col_list: list[str] = [*self._static_cols, *self._get_all_paired_cols()]

        try:
            return chunk[col_list]
        except KeyError as ke:
            raise DataProcessingError(
                f"Unable to extract expected columns from matched CSV: {ke}"
            ) from ke

    def get_matched_column_filters(self) -> list[ColumnFilter]:
        """Returns the column filters for the matched data."""
        return [
            ColumnFilter(
                column=ELIGIBILITY_COL,
                operator="equals",
                value=ELIGIBILE_VALUE,
                how="any",
            ),
            ColumnFilter(
                column=MAX_CNV_PROBABILITY_COL_PREFIX,
                operator="<=",
                value=self.cnv_threshold,
                how="all",
            ),
        ]

    # Helper methods for filtering criteria
    def _apply_area_criteria(self, row: pd.Series, patient_id: str) -> bool:
        """Apply total GA area criteria."""
        if self._paired_cols is None:
            raise AlgorithmError(
                "self._paired_cols not populated"
                " when calling _apply_area_criteria"
                " in a Both Eyes trial inclusion algorithm."
            )

        ga_area_entries = row[self._paired_cols[self.total_ga_area]]
        if not (
            (ga_area_entries > self.total_ga_area_lower_bound)
            & (ga_area_entries < self.total_ga_area_upper_bound)
        ).any():
            logger.debug(
                f"Patient {patient_id} excluded due to"
                f" total GA area being out of bounds"
            )
            return False
        return True

    def _apply_lesion_criteria(self, row: pd.Series, patient_id: str) -> bool:
        """Apply largest GA lesion criteria."""
        if self._paired_cols is None:
            raise AlgorithmError(
                "self._paired_cols not populated"
                " when calling _apply_lesion_criteria"
                " in a Both Eyes trial inclusion algorithm."
            )
        ga_lesion_entries = row[self._paired_cols[self.largest_legion_size]]
        if not (ga_lesion_entries > self.largest_ga_lesion_lower_bound).any():
            logger.debug(
                f"Patient {patient_id} excluded due to"
                f" largest GA lesion size being smaller than target"
            )
            return False
        return True

    def _apply_cnv_criteria(self, row: pd.Series, patient_id: str) -> bool:
        """Apply CNV criteria."""
        if self._paired_cols is None:
            raise AlgorithmError(
                "self._paired_cols not populated"
                " when calling _apply_cnv_criteria"
                " in a Both Eyes trial inclusion algorithm."
            )

        cnv_entries = row[self._paired_cols[self.max_cnv_probability]]
        if (cnv_entries >= self.cnv_threshold).any():
            logger.debug(
                f"Patient {patient_id} excluded due to CNV in one or both eyes"
            )
            return False
        return True

    def _apply_base_both_eyes_criteria(self, row: pd.Series, patient_id: str) -> bool:
        """Apply the common criteria for both eyes algorithms.

        This combines the area, lesion, and CNV criteria checks.

        Returns:
            True if all criteria pass, False otherwise.
        """
        if not self._apply_area_criteria(row, patient_id):
            return False

        if not self._apply_lesion_criteria(row, patient_id):
            return False

        if not self._apply_cnv_criteria(row, patient_id):
            return False

        return True


class BaseGATrialInclusionAlgorithmFactoryBothEyes(
    BaseGATrialInclusionAlgorithmFactory[BaseGATrialInclusionWorkerAlgorithmBothEyes]
):
    """Base class for GA trial criteria match algorithms that handle both eyes."""

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "renamed_columns": fields.Dict(
            keys=fields.Str(), values=fields.Str(), allow_none=True
        ),
    }

    def __init__(
        self,
        datastructure: DataStructure,
        renamed_columns: Optional[Mapping[str, str]] = None,
        cnv_threshold: float = CNV_THRESHOLD,
        largest_ga_lesion_lower_bound: float = LARGEST_GA_LESION_LOWER_BOUND,
        largest_ga_lesion_upper_bound: Optional[float] = None,
        total_ga_area_lower_bound: float = TOTAL_GA_AREA_LOWER_BOUND,
        total_ga_area_upper_bound: float = TOTAL_GA_AREA_UPPER_BOUND,
        patient_age_lower_bound: Optional[int] = None,
        patient_age_upper_bound: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            datastructure=datastructure,
            cnv_threshold=cnv_threshold,
            largest_ga_lesion_lower_bound=largest_ga_lesion_lower_bound,
            largest_ga_lesion_upper_bound=largest_ga_lesion_upper_bound,
            total_ga_area_lower_bound=total_ga_area_lower_bound,
            total_ga_area_upper_bound=total_ga_area_upper_bound,
            patient_age_lower_bound=patient_age_lower_bound,
            patient_age_upper_bound=patient_age_upper_bound,
            **kwargs,
        )
        self.renamed_columns = renamed_columns

    def worker(self, **kwargs: Any) -> BaseGATrialInclusionWorkerAlgorithmBothEyes:
        """Worker-side of the algorithm.

        This is an abstract method that should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement worker")
