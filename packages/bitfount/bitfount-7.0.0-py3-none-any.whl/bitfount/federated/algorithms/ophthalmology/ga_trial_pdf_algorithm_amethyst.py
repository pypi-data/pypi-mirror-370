"""Algorithm for outputting GA model results to CSV on the pod-side."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional, cast

import pandas as pd

from bitfount.data.datasources.base_source import FileSystemIterableSource
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.federated.algorithms.ophthalmology.dataframe_generation_extensions import (  # noqa: E501
    DataFrameExtensionError,
    generate_bitfount_patient_id,
    generate_subfoveal_indicator_extension,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_pdf_algorithm_base import (
    ELIGIBLE_PATIENTS,
    BaseGATrialPDFGeneratorAlgorithm,
    _BasePDFWorkerSide as BaseGATrialPDFWorker,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    FILTER_MATCHING_COLUMN,
    SUBFOVEAL_COL,
    TOTAL_GA_AREA_LOWER_BOUND,
    TOTAL_GA_AREA_UPPER_BOUND,
    GAMetrics,
    GAMetricsWithFovea,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_utils import (
    _convert_ga_metrics_to_df,
)
from bitfount.federated.exceptions import DataProcessingError
from bitfount.federated.logging import _get_federated_logger

logger = _get_federated_logger("bitfount.federated")


class _WorkerSide(BaseGATrialPDFWorker):
    """Amethyst-specific worker implementation."""

    def run(
        self,
        results_df: pd.DataFrame,
        ga_dict: Mapping[str, Optional[GAMetrics | GAMetricsWithFovea]],
        task_id: Optional[str] = None,
        filenames: Optional[list[str]] = None,
        total_ga_area_lower_bound: float = TOTAL_GA_AREA_LOWER_BOUND,
        total_ga_area_upper_bound: float = TOTAL_GA_AREA_UPPER_BOUND,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Generates PDF reports for the GA model results.

        Args:
            results_df: The DataFrame containing the predictions from the GA model.
                This DataFrame doesn't contain the full set of file details, but
                rather just the model outputs for each file.
                If `filenames` is provided, each dataframe must contain a
                ORIGINAL_FILENAME_METADATA_COLUMN which describes which file each
                row is associated with.
            ga_dict: The GA metrics calculated from the model outputs, associated
                with each file name.
            task_id: The ID of the task run, if present.
            filenames: The list of files that the results correspond to. If not
                provided, will iterate through all files in the dataset to find
                the corresponding ones.
            total_ga_area_lower_bound: The lower bound for the total GA area.
            total_ga_area_upper_bound: The upper bound for the total GA area.
            kwargs: Additional arguments for the algorithm.

        Returns:
            A DataFrame with the original filename and the path to the saved PDF.
        """
        # We need a dataframe (of the correct length, i.e. the number of files)
        # so we construct it from the ga_metrics dict. Some of the values in
        # this dict may be None, so we handle that conversion.
        # Note: order will be correct as dict is sorted by insertion order,
        # and we only do clean/new insertions into this dict.
        metrics_df = _convert_ga_metrics_to_df(ga_dict)
        test_data_dfs = self._get_test_data_from_data_source(
            metrics_df=metrics_df, filenames=filenames
        )
        # Check that we have the expected number of results for the number of files
        if filenames:
            if len(filenames) != len(results_df):
                raise DataProcessingError(
                    f"Length of results ({len(results_df)})"
                    f" does not match the number of files ({len(filenames)})"
                    f" while processing Amethyst PDF report."
                )
            if len(filenames) != len(ga_dict):
                raise DataProcessingError(
                    f"Length of ga metrics ({len(ga_dict)})"
                    f" does not match the number of files ({len(filenames)})"
                    f" while processing Amethyst PDF report."
                )

        pdf_output_paths: list[tuple[str, Optional[Path]]] = []
        test_data_dfs = self._append_results_to_orig_data(
            test_data_dfs=test_data_dfs,
            results_df=results_df,
            filenames=filenames,
        )

        len_test_data_dfs = 0
        for test_df in test_data_dfs:
            len_test_data_dfs += len(test_df)
            # Add BitfountPatientID to the DataFrame
            try:
                test_df = generate_bitfount_patient_id(test_df)
            except DataFrameExtensionError as e:
                logger.error(f"Error whilst calculating Bitfount Patient IDs: {e}")
            # Add subfoveal indicator to the DataFrame
            try:
                test_df = generate_subfoveal_indicator_extension(test_df)
                successfully_added_subfoveal_indicator = True
            except DataFrameExtensionError as e:
                logger.error(f"Error whilst calculating subfoveal indicator: {e}")
                successfully_added_subfoveal_indicator = False
            # Apply row filtering to supplied dataframe based on some criteria.
            # Assumption here is that the results_df maps correctly
            # to the test_df
            filtered_results_df = self._find_entries_matching_filter(test_df)
            for idx, datasource_row in test_df.iterrows():
                # At this point only records matching filter should be in the data
                eligibility = ELIGIBLE_PATIENTS
                # Iterrows() iterates over DataFrame rows as (index, Series) pairs.
                index = cast(pd.Index, idx)

                original_filename = datasource_row[ORIGINAL_FILENAME_METADATA_COLUMN]

                if (
                    original_filename
                    in filtered_results_df[ORIGINAL_FILENAME_METADATA_COLUMN].values
                ):
                    ga_metrics = self._get_ga_metric_from_dictionary(
                        ga_dict, original_filename
                    )
                    subfoveal_indicator: Optional[str] = None
                    if successfully_added_subfoveal_indicator:
                        # Wrap in try/except to avoid crashing if
                        # the column is not present
                        try:
                            if datasource_row[SUBFOVEAL_COL] == "N":
                                subfoveal_indicator = "No"
                            elif datasource_row[SUBFOVEAL_COL] == "Y":
                                subfoveal_indicator = "Yes"
                        except KeyError as e:
                            logger.error(
                                f"Error whilst calculating subfoveal indicator: {e}"
                            )
                    if ga_metrics is not None:
                        if successfully_added_subfoveal_indicator:
                            # If successfully added subfoveal indicator
                            # then we are working with GAMetricsWithFovea
                            ga_metrics = cast(GAMetricsWithFovea, ga_metrics)
                            ga_metrics.subfoveal_indicator = subfoveal_indicator
                        self._generate_pdf_for_datasource_row(
                            datasource_row=datasource_row,
                            results_df=results_df,
                            index=index,
                            ga_metrics=ga_metrics,
                            task_id=task_id,
                            original_filename=original_filename,
                            pdf_output_paths=pdf_output_paths,
                            eligibility=eligibility,
                        )
                    else:
                        logger.warning(
                            f"No GA metrics found for {original_filename}. Skipping"
                        )
                        pdf_output_paths.append((original_filename, None))
                else:
                    pdf_output_paths.append((original_filename, None))

        if filenames and isinstance(self.datasource, FileSystemIterableSource):
            # Check that the number of predictions (results_df) matched the number
            # of retrieved records (test_data_dfs) (found during iteration);
            # in the case where filenames was supplied we should _only_ be iterating
            # through that number
            if len(results_df) != len_test_data_dfs:
                raise DataProcessingError(
                    f"Length of predictions ({len(results_df)})"
                    f" does not match the number of records ({len_test_data_dfs})"
                    f" while processing Amethyst PDF report."
                )

        # NOTE: The order of this should match the input order of the predictions
        return pd.DataFrame(
            pdf_output_paths,
            columns=[ORIGINAL_FILENAME_METADATA_COLUMN, "pdf_output_path"],
        )

    def _find_entries_matching_filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply row filtering to supplied dataframe based on some criteria."""
        # From the results, only take the ones that match the
        # filter if a filter is provided
        if self.filter is not None:
            logger.info("Applying filters to the data.")
            df[FILTER_MATCHING_COLUMN] = True
            for col_filter in self.filter:
                try:
                    df = col_filter.apply_filter(df)
                except (KeyError, TypeError) as e:
                    if isinstance(e, KeyError):
                        logger.warning(
                            f"No column `{col_filter.column}` found in the data. "
                            "Filtering only on remaining given columns."
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

        # Filter out rows that don't match the filter. We leave the original index,
        # so we can match the rows with the original data when we iterate over it.
        df_subset = (
            df.loc[df[FILTER_MATCHING_COLUMN]] if self.filter is not None else df
        )
        return df_subset


class GATrialPDFGeneratorAlgorithmAmethyst(
    BaseGATrialPDFGeneratorAlgorithm[_WorkerSide]
):
    """Amethyst implementation of the GA Trial PDF Generator Algorithm."""

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Worker-side of the algorithm."""
        return _WorkerSide(
            report_metadata=self.report_metadata,
            filename_prefix=self.filename_prefix,
            path=self.save_path,
            filter=self.filter,
            pdf_filename_columns=self.pdf_filename_columns,
            trial_name=self.trial_name,
            **kwargs,
        )
