"""Algorithm for outputting results to CSV on the pod-side."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
import typing
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Optional, Union, cast
import warnings

import desert
from marshmallow import fields, validate
import pandas as pd

from bitfount import config
from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
)
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.federated.algorithms.base import (
    BaseNonModelAlgorithmFactory,
    BaseWorkerAlgorithm,
    FinalStepAlgorithm,
    NoResultsModellerAlgorithm,
)
from bitfount.federated.algorithms.ophthalmology.dataframe_generation_extensions import (  # noqa: E501
    extensions as extensions_registry,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    _BITFOUNT_PATIENT_ID_KEY,
    _BITFOUNT_PATIENT_ID_RENAMED,
    DEFAULT_AUX_COLS,
    ELIGIBILE_VALUE,
    FILTER_FAILED_REASON_COLUMN,
    FILTER_MATCHING_COLUMN,
    NON_ELIGIBILE_VALUE,
    ORIGINAL_DICOM_COLUMNS,
    ORIGINAL_HEIDELBERG_COLUMNS,
    TRIAL_NAME_COL,
    TrialNotesCSVArgs,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_utils import (
    get_data_for_files,
    get_dataframe_iterator_from_datasource,
    is_file_iterable_source,
)
from bitfount.federated.algorithms.ophthalmology.trial_inclusion_filters import (
    ColumnFilter,
)
from bitfount.federated.exceptions import DataProcessingError
from bitfount.federated.logging import _get_federated_logger
from bitfount.types import UsedForConfigSchemas
from bitfount.utils.logging_utils import deprecated_class_name
from bitfount.utils.pandas_utils import (
    append_dataframe_to_csv,
    append_encrypted_dataframe_to_csv,
    dataframe_iterable_join,
    read_encrypted_csv,
    to_encrypted_csv,
)

if TYPE_CHECKING:
    from bitfount.federated.privacy.differential import DPPodConfig
    from bitfount.types import T_FIELDS_DICT

logger = _get_federated_logger("bitfount.federated")

DFMergeType = Literal["inner", "outer", "left", "right"]
DFSortType = Literal["asc", "desc"]
DFSortMapping = {"asc": True, "desc": False}


@dataclass
class MatchPatientVisit(UsedForConfigSchemas):
    """Dataclass for matching patient visits.

    Allows matching of different scans and results for the same patient visit.
    Only two records can be matched for the same patient visit.

    Args:
        cols_to_match: List of columns on which to match.
        divergent_col: Column containing the divergent strings for
            the same patient. E.g. the column indicating whether the
            scan was performed on the left or right eye.
        date_time_col: The column indicating the date of the patient visit.
    """

    # TODO: [BIT-3641] Add support for datasource-agnostic matching criteria
    cols_to_match: list[str]
    divergent_col: str
    date_time_col: str
    how: DFMergeType = desert.field(
        fields.String(validate=validate.OneOf(typing.get_args(DFMergeType))),
        default="outer",
    )


class _WorkerSide(BaseWorkerAlgorithm, FinalStepAlgorithm):
    """Worker side of the algorithm."""

    def __init__(
        self,
        path: Union[str, os.PathLike],
        trial_name: Optional[str] = None,
        original_cols: Optional[list[str]] = None,
        rename_columns: Optional[Mapping[str, str]] = None,
        aux_cols: Optional[list[str]] = DEFAULT_AUX_COLS,
        filter: Optional[list[ColumnFilter]] = None,
        matcher: Optional[MatchPatientVisit] = None,
        matched_csv_path: Optional[Union[str, os.PathLike]] = None,
        produce_matched_only: bool = True,
        csv_extensions: Optional[list[str]] = None,
        produce_trial_notes_csv: bool = False,
        sorting_columns: Optional[dict[str, DFSortType]] = None,
        decimal_places: int = 3,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.path = Path(path)
        self.trial_name = trial_name
        self.task_start_date = datetime.today().strftime("%Y-%m-%d")

        self.original_cols = original_cols
        self.rename_columns = rename_columns
        self.aux_cols = aux_cols
        self.filter = filter

        self.matcher = matcher
        self.produce_trial_notes_csv = produce_trial_notes_csv
        self.produce_matched_only = produce_matched_only
        # This should be populated by the protocol if matching is requested
        self.matched_filter: Optional[list[ColumnFilter]] = None
        # This should be populated by protocol if trial notes csv is requested
        self.trial_notes_csv_args: Optional[TrialNotesCSVArgs] = None
        # Set the path for the matched CSV file output, using sensible defaults
        self.matched_csv_path: Path
        if matched_csv_path is not None:
            self.matched_csv_path = Path(matched_csv_path)
        else:  # matched_csv_path is None
            # If self.matcher is None then no matching will occur, so it doesn't
            # matter what the path is set to/we don't need to log it
            if self.matcher is not None:
                logger.debug("No matched_csv_path defined, using `path`")
            self.matched_csv_path = self.path

        # If we are doing matching AND are expecting two CSVs (matched and unmatched)
        # AND the two paths are pointing to the same FILE (not directory), this is a
        # mistake. We will defer to there only being one output CSV (with the matched
        # overwriting the unmatched), but we warn.
        if (
            # are we doing matching?
            self.matcher is not None
            # are we expecting two CSVs (matched and unmatched)?
            and not self.produce_matched_only
            # are the two paths pointing to the same FILE?
            and self.matched_csv_path == self.path
            and self.path.suffix
        ):
            logger.warning(
                f"Both matched and unmatched CSVs have been requested but"
                f" they are to be saved to the same file path"
                f" ({self.path}); the matched CSV will overwrite the"
                f" unmatched CSV."
            )
        self.sorting_columns = sorting_columns
        self.csv_extensions = []
        if csv_extensions is not None:
            for ext in csv_extensions:
                if ext not in extensions_registry:
                    logger.warning(
                        f'CSV extension "{ext}" was requested but was not found'
                        f" in the extensions registry. Will not be applied."
                    )
                else:
                    logger.info(
                        f'CSV extension "{ext}" was requested and will be applied.'
                    )
                    self.csv_extensions.append(ext)
        self.decimal_places = decimal_places
        self.encryption_key: Optional[str] = None
        self._run_csv_path: Optional[Path] = (
            None  # Path to the CSV file created during run
        )

    def _append_to_csv(self, csv_path: Path, df: pd.DataFrame) -> Path:
        """Append DataFrame to CSV file with optional encryption.

        Args:
            csv_path: Path to the CSV file.
            df: DataFrame to append.

        Returns:
            The actual path where the CSV was written.
        """
        if self.encryption_key is not None:
            return append_encrypted_dataframe_to_csv(csv_path, df, self.encryption_key)
        else:
            return append_dataframe_to_csv(csv_path, df)

    def _write_to_csv(self, csv_path: Path, df: pd.DataFrame, **kwargs: Any) -> Path:
        """Write DataFrame to CSV file with optional encryption.

        Args:
            csv_path: Path to the CSV file.
            df: DataFrame to write.
            **kwargs: Additional arguments for to_csv/to_encrypted_csv.

        Returns:
            The actual path where the CSV was written.
        """
        if self.encryption_key is not None:
            return to_encrypted_csv(df, csv_path, self.encryption_key, **kwargs)
        else:
            df.to_csv(csv_path, **kwargs)
            return csv_path

    def _read_from_csv(self, csv_path: Path, **kwargs: Any) -> pd.DataFrame:
        """Read DataFrame from CSV file with optional encryption.

        Args:
            csv_path: Path to the CSV file.
            **kwargs: Additional arguments for read_csv/read_encrypted_csv.

        Returns:
            The DataFrame read from the CSV file.
        """
        if self.encryption_key is not None:
            return read_encrypted_csv(csv_path, self.encryption_key, **kwargs)
        else:
            return cast(pd.DataFrame, pd.read_csv(csv_path, **kwargs))

    @property
    def file_name(self) -> str:
        """Returns the file name for the CSV report."""
        if self.trial_name is not None:
            file_name = (
                f"{self.trial_name}-prescreening-patients-{self.task_start_date}"
            )
        else:
            file_name = "results"

        return file_name

    def set_column_filters(self, filters: list[ColumnFilter]) -> None:
        """Sets the column filters for the worker.

        If filters already exist, the new filters will be appended to the existing ones.
        """
        if self.filter is None:
            self.filter = filters
        else:
            self.filter.extend(filters)

    def use_default_columns(self) -> None:
        """Sets the default columns to include based on the datasource."""
        if self.original_cols is None:
            # Add the relevant columns for the datasources
            if type(self.datasource).__name__ == "HeidelbergSource":
                self.original_cols = ORIGINAL_HEIDELBERG_COLUMNS

            elif type(self.datasource).__name__ == "DICOMOphthalmologySource":
                self.original_cols = ORIGINAL_DICOM_COLUMNS

    def _update_matcher_columns(self) -> None:
        """Updates the matcher columns to the renamed columns."""
        # We should only enter this function if there is a matcher defined
        self.matcher = cast(MatchPatientVisit, self.matcher)
        if self.rename_columns:
            self.matcher.cols_to_match = [
                self.rename_columns.get(col, col) for col in self.matcher.cols_to_match
            ]
            self.matcher.divergent_col = self.rename_columns.get(
                self.matcher.divergent_col, self.matcher.divergent_col
            )
            self.matcher.date_time_col = self.rename_columns.get(
                self.matcher.date_time_col, self.matcher.date_time_col
            )

    def _match_same_patient_visit(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Matches two patient records to the same visit within 24 hours.

        Args:
            df: The dataframe on which the filter is applied.
        """
        if self.matcher is None:
            return df
        else:
            self._update_matcher_columns()
        try:
            if len(unique_vals := df[self.matcher.divergent_col].unique()) != 2:
                if len(unique_vals) > 2:
                    logger.warning(
                        f"Divergent column `{self.matcher.divergent_col}` has more "
                        "than 2 unique values. We can only match two patient visits. "
                        "Saving CSV report without matching individual visits."
                    )
                    return df
                elif len(unique_vals) == 1:
                    if self.matcher.how == "outer":
                        logger.warning(
                            f"Divergent column `{self.matcher.divergent_col}` "
                            f"has only 1 unique value. Saving CSV report "
                            f"without matching individual visits."
                        )
                        return df
                    else:
                        # Return empty df if only one unique value
                        # and `how` is not outer
                        return pd.DataFrame(columns=df.columns)
            elif not df[self.matcher.cols_to_match].duplicated().any():
                # TODO: [BIT-2621] This doesn't take into account the `date_time_col`
                #       when checking for duplicates. This means that even if there
                #       are two records with the same values in the `cols_to_match`
                #       columns, but datetimes that are more than 24 hours apart, they
                #       won't be matched but the dataframe will still be split anyway.
                #       It also doesn't take into account the `divergent_col` column
                #       which means that even if there are two records with the same
                #       values in the `cols_to_match` columns, they may still have
                #       the same values in the `divergent_col` column and therefore
                #       won't be matched either. Therefore, this check is not sufficient
                #       to determine whether or not the dataframe definitely will have
                #       matches but it should account for the vast majority of cases
                #       where there are definitely no matches.
                logger.info(
                    "No duplicate records found across the specified columns. "
                    "Saving CSV report without matching individual visits."
                )
                return df

            df[self.matcher.date_time_col] = pd.to_datetime(
                df[self.matcher.date_time_col],
                format="mixed",
            )
            df_list = []
            if any(
                df[self.matcher.cols_to_match]
                .apply(pd.to_numeric, errors="ignore")
                .applymap(lambda x: isinstance(x, float), na_action="ignore")
                .any()
            ):
                # merge_asof does not allow matching on float values,
                # so we log a warning
                logger.warning(
                    "Matching records is not supported on float columns."
                    "Saving CSV report without matching individual visits."
                )
                return df
            for item in unique_vals:
                df_list.append(
                    df.where(df[self.matcher.divergent_col] == item)
                    .dropna(how="all")
                    .copy()
                )
            # sort values and convert dtypes
            df1 = df_list[0].sort_values(self.matcher.date_time_col).convert_dtypes()
            df2 = df_list[1].sort_values(self.matcher.date_time_col).convert_dtypes()

            # merge on datetime within 24hours by specific column
            # merge_asof does not implement outer merge, so we have to merge
            # separately left and right and then combine them.
            df_left_to_right_merge = pd.merge_asof(
                df1,
                df2,
                on=self.matcher.date_time_col,
                by=self.matcher.cols_to_match,
                tolerance=pd.Timedelta("24h"),
                suffixes=[
                    "_" + str(unique_vals[0]),
                    "_" + str(unique_vals[1]),
                ],
                direction="nearest",
            )
            df_right_to_left_merge = pd.merge_asof(
                df2,
                df1,
                on=self.matcher.date_time_col,
                by=self.matcher.cols_to_match,
                tolerance=pd.Timedelta("24h"),
                suffixes=[
                    "_" + str(unique_vals[1]),
                    "_" + str(unique_vals[0]),
                ],
                direction="nearest",
            )
            # get common cols and remove the date-time
            common_cols = df_left_to_right_merge.columns.to_list()
            common_cols.remove(self.matcher.date_time_col)
            # final merge to ensure date-time for both patient visits are there
            matched_df = pd.merge(
                df_left_to_right_merge,
                df_right_to_left_merge,
                on=common_cols,
                suffixes=[
                    "_" + str(unique_vals[0]),
                    "_" + str(unique_vals[1]),
                ],
                how=self.matcher.how,
            )

            return matched_df
        except KeyError as e:
            logger.warning(
                f"KeyError: {str(e)}. Saving CSV report without matching "
                "individual visits."
            )
            return df

    def initialise(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        encryption_key: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Sets Datasource."""
        self.initialise_data(datasource=datasource, data_splitter=data_splitter)

        # Set the encryption key if provided
        if encryption_key is not None:
            logger.debug("Setting encryption key.")
            self.encryption_key = encryption_key

    def _add_filtering_to_csv_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds filtering to the CSV dataframe.

        Args:
            df: The Dataframe to which the filter is applied.

        Returns:
            df: The Dataframe with additional columns corresponding to the filter.
        """
        if self.filter is not None:
            logger.debug("Filtering data.")
            df[FILTER_MATCHING_COLUMN] = True
            df[FILTER_FAILED_REASON_COLUMN] = ""
            for i, col_filter in enumerate(self.filter):
                logger.debug(f"Running filter {i + 1}")
                try:
                    df = col_filter.apply_filter(df, rename_columns=self.rename_columns)
                except (KeyError, TypeError) as e:
                    if isinstance(e, KeyError):
                        logger.warning(
                            f"No column `{col_filter.column}` found in the data. "
                            f"Filtering only on remaining given columns"
                        )
                    else:
                        # if TypeError
                        logger.warning(
                            f"Filter column {col_filter.column} is incompatible "  # noqa: E501
                            f"with operator type {col_filter.operator}. "
                            f"Raised TypeError: {str(e)}"
                        )
                    logger.info(
                        f"Filtering will skip `{col_filter.column} "
                        f"{col_filter.operator} {col_filter.value}`."
                    )
        return df

    def _add_filtering_to_matched_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds filtering to the matched dataframe.

        Args:
            df: The matched Dataframe to which the filter is applied.

        Returns:
            df: The matched Dataframe with additional columns corresponding
                to the filter.
        """
        # Filter columns are renamed at this point, so need to update the filters
        logger.debug("Filtering data.")
        df[FILTER_MATCHING_COLUMN] = True
        df[FILTER_FAILED_REASON_COLUMN] = ""
        if self.matched_filter is not None:
            for i, col_filter in enumerate(self.matched_filter):
                logger.debug(f"Running filter {i + 1}")
                try:
                    df = col_filter._add_partial_filtering_to_df(
                        df,
                        drop_filtered_cols=True,
                        add_new_col_for_filter=False,
                        rename_columns=self.rename_columns,
                    )
                except (KeyError, TypeError) as e:
                    if isinstance(e, KeyError):
                        logger.warning(
                            f"No column `{col_filter.column}` found in the data. "
                            "Filtering only on remaining given columns"
                        )
                    else:
                        # if TypeError
                        logger.warning(
                            f"Filter column {col_filter.column} is incompatible with "  # noqa: E501
                            f"operator type {col_filter.operator}. "
                            f"Raised TypeError: {str(e)}"
                        )
                    logger.info(
                        f"Filtering will skip `{col_filter.column} "
                        f"{col_filter.operator} {col_filter.value}`."
                    )
        return df

    def run(
        self,
        results_df: Union[pd.DataFrame, list[pd.DataFrame]],
        task_id: Optional[str] = None,
        final_batch: bool = False,
        filenames: Optional[list[str]] = None,
        encryption_key: Optional[str] = None,
    ) -> tuple[Optional[Path], int, bool]:
        """Generates a CSV file at the user specified path.

        :::caution

        If batched execution is enabled and the task ID is not provided, we are unable
        to append the results to the CSV file across batches so this will result in
        multiple CSV files being created.

        :::

        Args:
            results_df: The results of the inference task as either a single dataframe
                or a list of dataframes. If `filenames` is provided, each dataframe
                must contain a ORIGINAL_FILENAME_METADATA_COLUMN which describes
                which file each row is associated with.
            task_id: The ID of the task.
            final_batch: Whether this is the final batch of the algo run. Deprecated.
            filenames: The list of files that the results correspond to. If not
                provided, will iterate through all files in the dataset to find
                the corresponding ones.
            encryption_key: The encryption key to use for decrypting the CSV data.
                If not provided, encryption will not be used.

        Returns:
            The path to the matched CSV if matching is requested and it is the final
            batch, otherwise `None`.
        """
        if final_batch:
            warnings.warn(
                "final_batch parameter is deprecated and will be removed "
                "in a future release. Matching logic moved to "
                "run_final_step() method.",
                DeprecationWarning,
                stacklevel=2,
            )

        # Set the encryption key if provided
        if encryption_key is not None:
            logger.debug("Setting encryption key.")
            self.encryption_key = encryption_key

        # Get the path to the CSV file.
        csv_path = self._get_unique_csv_path(self.path, self.file_name, task_id)

        # Store csv_path for later use in final reduce step
        self._run_csv_path = csv_path
        # First, we need to extract the appropriate data from the datasource by
        # combining it with the output from the previous inference (i.e. joining
        # on the identifiers).
        test_data_dfs: Iterable[pd.DataFrame]
        if filenames is not None and is_file_iterable_source(self.datasource):
            logger.debug(f"Retrieving data for: {filenames}")

            df: pd.DataFrame = get_data_for_files(
                cast(FileSystemIterableSource, self.datasource), filenames
            )
            test_data_dfs = [df]

            # Check that we have the expected number of results for the number of files
            if len(filenames) != len(test_data_dfs[0]):
                raise DataProcessingError(
                    f"Length of results ({len(test_data_dfs[0])}"
                    f" does not match the number of files ({len(filenames)})"
                    f" while processing CSV report."
                )
        else:
            logger.warning(
                "Iterating over all files to find prediction<->file match;"
                " this may take a long time."
            )
            test_data_dfs = get_dataframe_iterator_from_datasource(
                self.datasource, self.data_splitter
            )

        # Combine multiple results dataframes into one.
        # The strategy for combining depends on if the data is keyed or not; if it
        # is, we merge on the key (e.g. "_original_filename"); if it isn't we simply
        # concat along the columns axis
        if isinstance(results_df, list):
            # If we have been provided filenames, the results data frames should all
            # be keyed
            if filenames is not None:
                # Check for required key
                for i, df in enumerate(results_df):
                    if ORIGINAL_FILENAME_METADATA_COLUMN not in df.columns:
                        raise ValueError(
                            f"Results dataframe at index {i}"
                            f" is missing required key column"
                            f" {ORIGINAL_FILENAME_METADATA_COLUMN}"
                        )

                # Merge in order, always merging on the keys column
                aux_results_df = results_df[0]
                for index in range(1, len(results_df)):
                    aux_results_df = pd.merge(
                        aux_results_df,
                        results_df[index],
                        on=ORIGINAL_FILENAME_METADATA_COLUMN,
                    )
            else:
                aux_results_df = pd.concat(results_df, axis="columns")
        else:
            aux_results_df = results_df
        if self.original_cols is not None and not all(
            res_col in self.original_cols for res_col in aux_results_df.columns.tolist()
        ):
            if self.aux_cols is None:
                # If aux_cols is None, include all additional columns
                self.original_cols += [
                    res_col
                    for res_col in aux_results_df.columns.tolist()
                    if res_col not in self.original_cols
                ]
            else:
                # If aux_cols is specified, only include columns that are in aux_cols
                self.original_cols += [
                    res_col
                    for res_col in aux_results_df.columns.tolist()
                    if (
                        (res_col not in self.original_cols)
                        and (res_col in self.aux_cols)
                    )
                ]
        len_aux_results_df = len(aux_results_df)

        # Check that we have the expected number of results for the number of files
        if filenames is not None:
            if len(filenames) != len_aux_results_df:
                raise DataProcessingError(
                    f"Length of results ({len_aux_results_df})"
                    f" does not match the number of files ({len(filenames)})"
                    f" while processing CSV report."
                )

        # Append the results to the original data
        logger.debug("Appending results to the original data.")

        # Merge the test data Dataframes and auxiliary results dataframes.
        # The manner in which they are merged depends on if the data is keyed or not
        # (i.e. if we have filenames)
        if filenames is not None:
            test_data_dfs = cast(list[pd.DataFrame], test_data_dfs)

            # Check that both dataframes have the required key column
            if ORIGINAL_FILENAME_METADATA_COLUMN not in test_data_dfs[0].columns:
                raise ValueError(
                    f"Retrieved file data dataframe is missing"
                    f" the required key column: {ORIGINAL_FILENAME_METADATA_COLUMN}"
                )
            if ORIGINAL_FILENAME_METADATA_COLUMN not in aux_results_df.columns:
                raise ValueError(
                    f"Results dataframe is missing"
                    f" the required key column: {ORIGINAL_FILENAME_METADATA_COLUMN}"
                )

            test_data_dfs = [
                test_data_dfs[0].merge(
                    aux_results_df, on=ORIGINAL_FILENAME_METADATA_COLUMN
                )
            ]
        else:
            logger.warning(
                "Joining results and original data iteratively;"
                " data must be provided in the same order in both"
            )
            test_data_dfs = dataframe_iterable_join(test_data_dfs, aux_results_df)
        # Work through each dataframe in the collection, filtering and removing
        # unneeded columns
        len_test_data_dfs = 0

        for df in test_data_dfs:
            len_test_data_dfs += len(df)

            # Filter the data if a filter is provided
            if self.filter is not None:
                df = self._add_filtering_to_csv_df(df)
            # If needed change FILTER_MATCHING_COLUMN to "Eligible" or "Not Eligible"
            if (
                self.rename_columns is not None
                and (FILTER_MATCHING_COLUMN, "Eligibility")
                in self.rename_columns.items()
                and FILTER_MATCHING_COLUMN in df.columns
            ):
                df[FILTER_MATCHING_COLUMN] = df[FILTER_MATCHING_COLUMN].replace(
                    {True: "Eligible", False: "Not Eligible"}
                )

            # Remove trailing comma from FILTER_FAILED_REASON_COLUMN
            if FILTER_FAILED_REASON_COLUMN in df.columns:
                df[FILTER_FAILED_REASON_COLUMN] = df[
                    FILTER_FAILED_REASON_COLUMN
                ].str.rstrip(", ")

            if (
                isinstance(self.datasource, FileSystemIterableSource)
                and self.original_cols is not None
                and len(self.original_cols) > 0
                and ORIGINAL_FILENAME_METADATA_COLUMN not in self.original_cols
            ):
                self.original_cols.append(ORIGINAL_FILENAME_METADATA_COLUMN)

            if isinstance(self.datasource, FileSystemIterableSource):
                img_columns = list(self.datasource.image_columns)
                # Find the intersection of image_cols and data.columns
                existing_img_columns = list(set(img_columns) & set(df.columns))
                missing_img_columns = set(img_columns) - set(df.columns)

                if missing_img_columns:
                    logger.warning(
                        f"DataFrame has {len(existing_img_columns)} out of"
                        f" {len(img_columns)} image columns."
                        f"Missing {len(missing_img_columns)} image columns."
                    )
                    logger.debug(
                        "The following image columns are missing from"
                        f" the DataFrame: {missing_img_columns}"
                    )

                # Add True/None to indicate the number of frame based
                # on the pixel data columns if images are not cached.
                if existing_img_columns:
                    img_df = df[existing_img_columns]
                    # Replace non-NA elements with True
                    img_df = img_df.mask(img_df.notna(), other=True)
                    # Replace NA elements with False
                    img_df = img_df.mask(img_df.isna(), other=None)
                    df[existing_img_columns] = img_df

            # Apply any CSV extension functions
            for ext in self.csv_extensions:
                logger.info(f"Applying {ext} extension to CSV")
                logger.info(f"DataFrame columns before {ext}: {df.columns.tolist()}")
                ext_func = extensions_registry[ext]
                df = ext_func(df)
                logger.info(f"DataFrame columns after {ext}: {df.columns.tolist()}")

            # Add static column for the trial name if present
            if self.trial_name:
                df["Study name"] = self.trial_name
            if self.trial_name and self.matcher is not None:
                # This value is static acros the dataframe
                self.matcher.cols_to_match.append("Study name")
            # These values should be consistent for matching patient visits
            if _BITFOUNT_PATIENT_ID_RENAMED in df.columns and self.matcher is not None:
                self.matcher.cols_to_match.append(_BITFOUNT_PATIENT_ID_RENAMED)
            if _BITFOUNT_PATIENT_ID_KEY in df.columns and self.matcher is not None:
                self.matcher.cols_to_match.append(_BITFOUNT_PATIENT_ID_KEY)
            # Get only columns specified by original_cols if it is not None.
            if self.original_cols is not None:
                report_cols = [col for col in self.original_cols if col in df.columns]
                if len(report_cols) != 0:
                    csv_df = df[report_cols].copy()
                else:
                    csv_df = df.copy()
                    logger.warning(
                        "No columns from the original_cols list were found "
                        "in the data. Saving the whole dataframe to csv."
                    )
            else:
                csv_df = df.copy()
            # Rename columns if specified.
            if self.rename_columns is not None:
                csv_df.rename(
                    columns=self.rename_columns, inplace=True, errors="ignore"
                )

            # Write the dataframe to CSV, handling appending to existing CSV
            this_csv_path = self._append_to_csv(
                csv_path, csv_df.round(decimals=self.decimal_places)
            )
            logger.debug(f"CSV output to {this_csv_path}")
            # Update csv_path and self._run_csv_path to the actual file path
            # (important when encryption is used, as file extension changes to .crypt)
            csv_path = this_csv_path
            self._run_csv_path = this_csv_path
        if self.sorting_columns is not None:
            logger.info("Sorting the CSV file based on the specified columns.")
            self.sort_csv(csv_path)
        if filenames is not None and isinstance(
            self.datasource, FileSystemIterableSource
        ):
            # Check that the number of predictions (aux_results_df) matched the number
            # of retrieved records (test_data_dfs) (found during iteration);
            # in the case where filenames was supplied we should _only_ be iterating
            # through that number
            if len_aux_results_df != len_test_data_dfs:
                raise DataProcessingError(
                    f"Number of predictions ({len_aux_results_df})"
                    f" does not match the number of records ({len_test_data_dfs})"
                    f" while processing CSV report."
                )

        unique_patient_count = self._get_unique_patients_id_count(csv_path)
        # Return intermediate results
        return None, unique_patient_count, False

    def run_final_step(self, **kwargs: Any) -> tuple[Optional[Path], int, bool]:
        """Execute CSV matching and sorting post main run."""
        matched_csv_path: Optional[Path] = None
        matched_data: bool = False
        if self.matcher is not None:
            task_id = kwargs.get("task_id", None)
            if self._run_csv_path is None or not self._run_csv_path.exists():
                logger.warning("No CSV file found for final reduce step")
                return None, 0, False
            matched_csv_path, matched_data = self._produce_matched_csv(
                self._run_csv_path, task_id
            )
            if self.sorting_columns is not None and matched_csv_path is not None:
                logger.info(
                    "Sorting the matched CSV file based on the specified columns."
                )
                self.sort_csv(matched_csv_path)

            # Handle trial notes CSV
            if matched_csv_path and self.produce_trial_notes_csv:
                self._produce_trial_notes_csv(matched_csv_path, task_id)
            elif self.produce_trial_notes_csv:
                self._produce_trial_notes_csv(self._run_csv_path, task_id)
        if self._run_csv_path is not None and self._run_csv_path.exists():
            # Get unique patient count
            unique_patient_count = self._get_unique_patients_id_count(
                self._run_csv_path
            )
        else:
            unique_patient_count = 0

        return matched_csv_path, unique_patient_count, matched_data

    def _produce_matched_csv(
        self, csv_path: Path, task_id: Optional[str]
    ) -> tuple[Optional[Path], bool]:
        """Produce the matched CSV file."""
        # Match patients across visits if specified.
        logger.info("Matching patient info across visits.")
        # TODO: [BIT-3486] This may be too large by itself as it
        #       potentially contains all records processed thus far.
        #       May need to solve this iterably.
        # May need to update this to be read in an iterable manner
        data = self._read_from_csv(csv_path, index_col=False)
        matched_data = False
        if not data.empty:
            try:
                all_data = self._match_same_patient_visit(data)
            except Exception as e:
                logger.error(
                    f"Error while matching patient visits: {str(e)}. "
                    "Skipping patient matching."
                )
                all_data = pd.DataFrame()
            # Only write out if there's actually any data
            if not all_data.empty:
                matched_csv_path = self._get_matched_csv_path(csv_path, task_id)
                logger.debug(f"Saving matched patients data to {matched_csv_path}")
                if self.filter:
                    all_data = self._add_filtering_to_matched_df(all_data)
                    # If needed change FILTER_MATCHING_COLUMN to "Eligible"
                    # or "Not Eligible"
                    if FILTER_MATCHING_COLUMN in all_data.columns:
                        all_data[FILTER_MATCHING_COLUMN] = all_data[
                            FILTER_MATCHING_COLUMN
                        ].astype(str)
                        all_data[FILTER_MATCHING_COLUMN] = all_data[
                            FILTER_MATCHING_COLUMN
                        ].replace(
                            {"True": ELIGIBILE_VALUE, "False": NON_ELIGIBILE_VALUE}
                        )
                        # Reorder columns to have the filter column right after trial
                        # name column if it exists or first if tral name is not present
                        col_list = [
                            c for c in all_data.columns if c != FILTER_MATCHING_COLUMN
                        ]

                        if TRIAL_NAME_COL in col_list:
                            col_list.insert(1, FILTER_MATCHING_COLUMN)
                        else:
                            col_list.insert(0, FILTER_MATCHING_COLUMN)
                        all_data = all_data[col_list]
                    # Rename the filter column if needed
                    if (
                        self.rename_columns
                        and FILTER_MATCHING_COLUMN in self.rename_columns
                    ):
                        all_data.rename(
                            columns={
                                FILTER_MATCHING_COLUMN: self.rename_columns[
                                    FILTER_MATCHING_COLUMN
                                ]
                            },
                            inplace=True,
                            errors="ignore",
                        )

                # Write the dataframe to CSV, handling appending to existing CSV
                matched_csv_path = self._append_to_csv(
                    matched_csv_path, all_data.round(decimals=self.decimal_places)
                )
                logger.info(f"Saved matched patients data to {matched_csv_path}")
                matched_data = True
                return matched_csv_path, matched_data
            else:
                logger.warning(
                    "No matches were found, but matching was requested. "
                    "Returning original csv path."
                )
                return csv_path, matched_data
        else:
            return None, matched_data

    def _get_unique_patients_id_count(self, csv_path: Path) -> int:
        """Get the unique patient ids from the csv file."""
        # TODO: [BIT-3486]
        try:
            all_data = self._read_from_csv(
                csv_path, usecols=[_BITFOUNT_PATIENT_ID_RENAMED], index_col=False
            )
            return len(all_data[_BITFOUNT_PATIENT_ID_RENAMED].unique())
        except ValueError:
            try:
                all_data = self._read_from_csv(
                    csv_path, usecols=[_BITFOUNT_PATIENT_ID_KEY], index_col=False
                )
                return len(all_data[_BITFOUNT_PATIENT_ID_KEY].unique())
            except ValueError:
                all_data = self._read_from_csv(csv_path, index_col=False)
                return len(all_data)

    def sort_csv(self, csv_path: Path) -> None:
        """Sort the csv file based on the columns specified in the sorting_columns."""
        if self.sorting_columns is not None:
            # TODO: [BIT-3486] May need revisiting to handle large files,
            #  altough not sure how sorting would work without the whole dataset
            logger.info("Sorting the CSV file based on the specified columns.")
            all_data = self._read_from_csv(csv_path)
            columns_to_sort_by = []
            how_to_sort = []
            for column, sort_type in self.sorting_columns.items():
                # This allows for partial matching of the column names,
                # useful especially in the case of matched data
                find_matching_cols = [
                    col
                    for col in all_data.columns
                    if col.lower()
                    .replace(" ", "")
                    .startswith(column.lower().replace(" ", ""))
                ]
                if len(find_matching_cols) == 0:
                    # Try checking if the column has been renamed
                    if self.rename_columns and column in self.rename_columns.keys():
                        find_matching_cols_renamed = [
                            col
                            for col in all_data.columns
                            if col.lower()
                            .replace(" ", "")
                            .startswith(
                                self.rename_columns[column].lower().replace(" ", "")
                            )
                        ]
                        # Add any relevant columns found to the sorting list
                        columns_to_sort_by.extend(find_matching_cols_renamed)
                        # Extend the how_to_sort list with the appropriate sort types,
                        # based on the number of columns found
                        how_to_sort.extend(
                            [DFSortMapping[sort_type]] * len(find_matching_cols_renamed)
                        )
                    else:
                        logger.warning(
                            f"Column {column} not found in the data, "
                            "skipping any sorting based on it."
                        )
                else:
                    # Add any relevant columns found to the sorting list
                    columns_to_sort_by.extend(find_matching_cols)
                    # Extend the how_to_sort list with the appropriate sort types,
                    # based on the number of columns found
                    how_to_sort.extend(
                        [DFSortMapping[sort_type]] * len(find_matching_cols)
                    )
            if not len(columns_to_sort_by) == 0:
                # If any of the columns were found in the data,
                # sort the data and save the new csv
                all_data.sort_values(
                    columns_to_sort_by, ascending=how_to_sort, inplace=True
                )
                csv_path = self._write_to_csv(csv_path, all_data, index=False)
                # Update self._run_csv_path to the actual file path
                self._run_csv_path = csv_path
            else:
                logger.warning(
                    "None of the columns specified for sorting were found in the data."
                )

    def _trial_notes_csv_path(
        self, task_id: Optional[str], eligible_only: bool = True
    ) -> Path:
        """Get the path to save the trial notes CSV to.

        This is based in the supplied path directory (`self.path`) and the final
        path depends on aspects of the run (whether `task_id` is supplied, whether
        a file of that name already exists, etc).
        """
        if self.trial_name is not None and eligible_only:
            file_name = f"{self.trial_name}-eligible-patients-notes-template"
        elif self.trial_name:
            file_name = f"{self.trial_name}-patients-notes-template"
        else:
            file_name = "bitfount-trial-notes-template"
        return self._get_unique_csv_path(self.path, file_name, task_id)

    def _produce_trial_notes_csv(
        self, csv_path: Path, task_id: Optional[str] = None
    ) -> None:
        """Produce the trial notes CSV file."""
        if self.trial_notes_csv_args is None:
            logger.warning(
                "Trial notes csv was requested, but no arguments "
                "were passed from the protocol. Trial notes "
                "CSV will not be generated "
            )
        else:
            data = self._read_from_csv(csv_path, index_col=False)
            trial_notes_csv_path = self._trial_notes_csv_path(
                task_id, self.trial_notes_csv_args.eligible_only
            )
            df = pd.DataFrame(columns=self.trial_notes_csv_args.columns_for_csv)
            if self.trial_notes_csv_args.eligible_only:
                data = data[data["Eligibility"] == ELIGIBILE_VALUE]

            if self.trial_notes_csv_args.columns_from_data:
                # Add the required data from the existing data
                for (
                    new_col,
                    orig_col,
                ) in self.trial_notes_csv_args.columns_from_data.items():
                    df[new_col] = data[orig_col]

            if self.trial_notes_csv_args.columns_to_populate_with_static_values:
                # Populate columns with required static values
                for (
                    col,
                    val,
                ) in self.trial_notes_csv_args.columns_to_populate_with_static_values.items():  # noqa: E501
                    df[col] = [val] * len(df)

            if len(df) > 0:
                # drop duplicate rows
                df.drop_duplicates(inplace=True)
                # Make sure that NaNs are replaced by N/A strings
                df.fillna("N/A", inplace=True)
                # Write the dataframe to CSV, handling appending to existing CSV
                trial_notes_csv_path = self._append_to_csv(
                    trial_notes_csv_path, df.round(decimals=self.decimal_places)
                )
                logger.info(f"Saved trial notes data to {trial_notes_csv_path}")
            else:
                logger.warning(
                    "No eligible patients were found, trial notes CSV "
                    "will not be generated"
                )

    def _get_matched_csv_path(self, csv_path: Path, task_id: Optional[str]) -> Path:
        """Get the path to save the matched patients CSV to.

        Depending on settings this will either be a supplied path, the same path as
        `csv_path` (i.e. overwrite the file), or an automatically generated path
        using `csv_path` as the base.
        """
        # If we are only producing the matched CSV, we can overwrite the original CSV
        if self.produce_matched_only:
            return csv_path

        # Otherwise generate a unique path using the same criteria as used to
        # generate csv_path
        return self._get_unique_csv_path(
            self.matched_csv_path, f"{self.file_name}-matched eyes", task_id
        )

    @staticmethod
    def _get_unique_csv_path(
        base_path: Path, file_name: str, task_id: Optional[str]
    ) -> Path:
        """Generate a unique file path for saving a CSV to.

        If the base_path points to a file (even if it doesn't exist or have a ".csv"
        extension), we will use that file.

        If the base_path is a directory, then we will use that (potentially with a
        `task_id` subdirectory).

        If we are not using a `task_id` subdirectory and the chosen file already
        exists, then we will increment the filename with a " (N)" suffix.
        """
        # If the path is explicitly a file, we will use that.
        # As the path may not exist, we use whether it has a .csv suffix to determine
        # whether it is a file path or not.
        if base_path.suffix:
            if base_path.suffix != ".csv":
                logger.warning(
                    f"Supplied save path was not for a CSV file ("
                    f"{base_path}). Saving to this file anyway."
                )
            return base_path
        # If it is a directory (has no suffix)
        else:
            base_dir: Path = base_path

        base_dir.mkdir(parents=True, exist_ok=True)

        # If we have task_id, then we put it in that subfolder
        # This is guaranteed to be unique/we don't care if we overwrite it.
        if task_id is not None:
            task_id_dir = base_dir / task_id
            task_id_dir.mkdir(parents=True, exist_ok=True)
            csv_path = task_id_dir / f"{file_name}.csv"
        # Otherwise, create a unique path within the target directory
        else:
            csv_path = base_dir / f"{file_name}.csv"
            i = 1
            while csv_path.exists():
                csv_path = base_dir / f"{file_name} ({i}).csv"
                i += 1
        return csv_path


class CSVReportGeneratorOphthalmologyAlgorithm(
    BaseNonModelAlgorithmFactory[NoResultsModellerAlgorithm, _WorkerSide]
):
    """Algorithm for generating the CSV results reports.

    Args:
        datastructure: The data structure to use for the algorithm.
        save_path: The folder path where the csv report should be saved.
        trial_name: The name of the trial for the csv report. If provided,
            the CSV will be saved as "trial_name"-prescreening-patients-"date".csv.
            Defaults to None.
        original_cols: The tabular columns from the datasource to include
            in the report. If not specified it will include all
            tabular columns from the datasource.
        aux_cols: The auxiliary columns from other datasources to include
            in the report. If not specified it will include all
            auxiliary columns from the datasource.
        rename_columns: A dictionary of columns to rename. Defaults to None.
        filter: A list of `ColumnFilter` instances on which
            we will filter the data on. Defaults to None. If supplied,
            columns will be added to the output csv indicating the
            records that match the specified criteria. If more than one
            `ColumnFilter` is given, and additional column will be added
            to the output csv indicating the datapoints that match all
            given criteria (as well as the individual matches)
        match_patient_visit: Used for matching the same patient visit.
        matched_csv_path: Path to save the matched patients CSV to, if requested.
            Defaults to `save_path` (i.e. overwrites the non-matched CSV) if
            `produce_matched_only` is True. Otherwise, will create a file based off of
            the `save_path` argument.
        produce_matched_only: If True, only the matched CSV will be generated at the
            end of the run. If False, both the non-matched and matched CSV will be
            generated.
        produce_trial_notes_csv: If True, a CSV file containing the trial notes will
            be generated at the end of the run. Defaults to False.
        csv_extensions: List of named CSV extension functions that will be applied
            to the output CSV just before saving to file.
        sorting_columns: A dictionary of columns to sort the output CSV by.
            The keys are column names the values are either 'asc' or 'desc'. Defaults
            to None.
        decimal_places: Number of decimal places to round to in output CSVs.
            Defaults to 3.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "save_path": fields.Str(),
        "original_cols": fields.List(fields.Str(), allow_none=True),
        "aux_cols": fields.List(fields.Str(), allow_none=True),
        "trial_name": fields.Str(allow_none=True),
        "rename_columns": fields.Dict(
            keys=fields.Str(), values=fields.Str(), allow_none=True
        ),
        "filter": fields.Nested(
            desert.schema_class(ColumnFilter), many=True, allow_none=True
        ),
        "match_patient_visit": fields.Nested(
            desert.schema_class(MatchPatientVisit), allow_none=True
        ),
        "matched_csv_path": fields.Str(allow_none=True),
        "produce_matched_only": fields.Bool(),
        "produce_trial_notes_csv": fields.Bool(),
        "csv_extensions": fields.List(fields.Str(), allow_none=True),
        "sorting_columns": fields.Dict(
            keys=fields.Str(),
            values=fields.Str(validate=validate.OneOf(typing.get_args(DFSortType))),
            allow_none=True,
        ),
        "decimal_places": fields.Int(validate=validate.Range(min=0), load_default=3),
    }

    def __init__(
        self,
        datastructure: DataStructure,
        save_path: Optional[Union[str, os.PathLike]] = None,
        trial_name: Optional[str] = None,
        rename_columns: Optional[Mapping[str, str]] = None,
        original_cols: Optional[list[str]] = None,
        aux_cols: Optional[list[str]] = DEFAULT_AUX_COLS,
        filter: Optional[list[ColumnFilter]] = None,
        match_patient_visit: Optional[MatchPatientVisit] = None,
        matched_csv_path: Optional[Union[str, os.PathLike]] = None,
        produce_matched_only: bool = True,
        csv_extensions: Optional[list[str]] = None,
        produce_trial_notes_csv: bool = False,
        sorting_columns: Optional[dict[str, DFSortType]] = None,
        decimal_places: int = 3,
        **kwargs: Any,
    ) -> None:
        self.save_path: Path
        if save_path is None:
            self.save_path = config.settings.paths.output_dir
        else:
            self.save_path = Path(save_path)
        self.trial_name = trial_name
        self.original_cols = original_cols
        self.aux_cols = aux_cols
        self.rename_columns = rename_columns
        self.filter = filter

        self.match_patient_visit = match_patient_visit
        self.matched_csv_path: Optional[Path] = (
            Path(matched_csv_path) if matched_csv_path is not None else None
        )
        self.produce_matched_only = produce_matched_only
        self.produce_trial_notes_csv = produce_trial_notes_csv
        self.csv_extensions = csv_extensions
        self.sorting_columns = sorting_columns
        self.decimal_places = decimal_places
        super().__init__(datastructure=datastructure, **kwargs)

    def modeller(self, **kwargs: Any) -> NoResultsModellerAlgorithm:
        """Modeller-side of the algorithm."""
        return NoResultsModellerAlgorithm(
            log_message="Running CSV report generation algorithm",
            **kwargs,
        )

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Worker-side of the algorithm."""
        return _WorkerSide(
            path=self.save_path,
            trial_name=self.trial_name,
            original_cols=self.original_cols,
            rename_columns=self.rename_columns,
            aux_cols=self.aux_cols,
            filter=self.filter,
            matcher=self.match_patient_visit,
            matched_csv_path=self.matched_csv_path,
            produce_matched_only=self.produce_matched_only,
            produce_trial_notes_csv=self.produce_trial_notes_csv,
            csv_extensions=self.csv_extensions,
            sorting_columns=self.sorting_columns,
            decimal_places=self.decimal_places,
            **kwargs,
        )


# Keep old name for backwards compatibility
@deprecated_class_name
class CSVReportGeneratorAlgorithm(CSVReportGeneratorOphthalmologyAlgorithm):
    """Algorithm for generating the CSV results reports."""

    pass
