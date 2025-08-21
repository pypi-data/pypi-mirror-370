"""Algorithm for outputting GA model results to CSV on the pod-side."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional, Union, cast

import pandas as pd

from bitfount.data.datasources.base_source import (
    FileSystemIterableSource,
)
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.federated.algorithms.ophthalmology.dataframe_generation_extensions import (  # noqa: E501
    DataFrameExtensionError,
    generate_bitfount_patient_id,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_pdf_algorithm_base import (
    BaseGATrialPDFGeneratorAlgorithm,
    _BasePDFWorkerSide as BaseGATrialPDFWorker,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    FILTER_MATCHING_COLUMN,
    TOTAL_GA_AREA_LOWER_BOUND,
    TOTAL_GA_AREA_UPPER_BOUND,
    GAMetrics,
    ReportMetadata,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_utils import (
    _convert_ga_metrics_to_df,
)
from bitfount.federated.algorithms.ophthalmology.trial_inclusion_filters import (
    ColumnFilter,
)
from bitfount.federated.exceptions import DataProcessingError
from bitfount.federated.logging import _get_federated_logger
from bitfount.utils.logging_utils import deprecated_class_name

logger = _get_federated_logger("bitfount.federated")

ELIGIBLE_PATIENTS = "Eligible"
NON_ELIGIBLE_PATIENTS = "Not-eligible"


class _WorkerSide(BaseGATrialPDFWorker):
    """Worker side of the algorithm."""

    def __init__(
        self,
        *,
        path: Union[str, os.PathLike],
        report_metadata: ReportMetadata,
        filename_prefix: Optional[str] = None,
        filter: Optional[list[ColumnFilter]] = None,
        pdf_filename_columns: Optional[list[str]] = None,
        total_ga_area_lower_bound: float = TOTAL_GA_AREA_LOWER_BOUND,
        total_ga_area_upper_bound: float = TOTAL_GA_AREA_UPPER_BOUND,
        trial_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            path=path,
            report_metadata=report_metadata,
            filename_prefix=filename_prefix,
            filter=filter,
            pdf_filename_columns=pdf_filename_columns,
            total_ga_area_lower_bound=total_ga_area_lower_bound,
            total_ga_area_upper_bound=total_ga_area_upper_bound,
            trial_name=trial_name,
            **kwargs,
        )

    def run(
        self,
        results_df: pd.DataFrame,
        ga_dict: dict[str, Optional[GAMetrics]],
        task_id: Optional[str] = None,
        filenames: Optional[list[str]] = None,
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
            kwargs: Additional keyword arguments.

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
        if filenames:
            if len(filenames) != len(results_df):
                raise DataProcessingError(
                    f"Length of results ({len(results_df)})"
                    f" does not match the number of files ({len(filenames)})"
                    f" while processing PDF report."
                )
            if len(filenames) != len(ga_dict):
                raise DataProcessingError(
                    f"Length of ga metrics ({len(ga_dict)})"
                    f" does not match the number of files ({len(filenames)})"
                    f" while processing PDF report."
                )

        pdf_output_paths: list[tuple[str, Optional[Path]]] = []

        len_test_data_dfs = 0
        for test_df in test_data_dfs:
            len_test_data_dfs += len(test_df)

            # Add BitfountPatientID to the DataFrame
            try:
                test_df = generate_bitfount_patient_id(test_df)
            except DataFrameExtensionError as e:
                logger.error(f"Error whilst calculating Bitfount Patient IDs: {e}")

            # Apply row filtering to supplied dataframe based on some criteria.
            # Assumption here is that the results_df maps correctly
            # to the test_df

            files_matching_filters = self._find_entries_matching_filter(
                results_df, test_df
            )
            for idx, datasource_row in test_df.iterrows():
                # Iterrows() iterates over DataFrame rows as (index, Series) pairs.
                index = cast(pd.Index, idx)

                original_filename = datasource_row[ORIGINAL_FILENAME_METADATA_COLUMN]
                if original_filename in files_matching_filters:
                    eligibility = ELIGIBLE_PATIENTS
                else:
                    eligibility = NON_ELIGIBLE_PATIENTS

                if (
                    original_filename
                    in results_df[ORIGINAL_FILENAME_METADATA_COLUMN].values
                ):
                    ga_metrics = self._get_ga_metric_from_dictionary(
                        ga_dict, original_filename
                    )
                    if ga_metrics is not None:
                        pdf_output_paths = self._generate_pdf_for_datasource_row(
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
                    f" while processing PDF report."
                )

        # NOTE: The orders of these should match the input order of the predictions
        return pd.DataFrame(
            pdf_output_paths,
            columns=[ORIGINAL_FILENAME_METADATA_COLUMN, "pdf_output_path"],
        )

    def _find_entries_matching_filter(
        self, df: pd.DataFrame, test_df: pd.DataFrame
    ) -> list[str]:
        """Apply row filtering to supplied dataframe based on some criteria.

        Returns:
            A list of filenames that match the filter criteria.
        """
        # Assumption here is that the results_df maps correctly
        # to the test_df
        if ORIGINAL_FILENAME_METADATA_COLUMN not in df.columns:
            df[ORIGINAL_FILENAME_METADATA_COLUMN] = test_df[
                ORIGINAL_FILENAME_METADATA_COLUMN
            ]
        # From the results, only take the ones that match the
        # filter if a filter is provided
        if self.filter is not None:
            logger.info("Applying filters to the data.")
            test_df[FILTER_MATCHING_COLUMN] = True
            for col_filter in self.filter:
                try:
                    test_df = col_filter.apply_filter(test_df)
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
        test_df_subset = (
            test_df.loc[test_df[FILTER_MATCHING_COLUMN]]
            if self.filter is not None
            else test_df
        )
        return test_df_subset[ORIGINAL_FILENAME_METADATA_COLUMN].tolist()


class GATrialPDFGeneratorAlgorithmJade(BaseGATrialPDFGeneratorAlgorithm[_WorkerSide]):
    """Jade implementation of the PDF results report for the GA Algorithm."""

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Worker-side of the algorithm."""
        return _WorkerSide(
            report_metadata=self.report_metadata,
            filename_prefix=self.filename_prefix,
            path=self.save_path,
            filter=self.filter,
            pdf_filename_columns=self.pdf_filename_columns,
            total_ga_area_lower_bound=self.total_ga_area_lower_bound,
            total_ga_area_upper_bound=self.total_ga_area_upper_bound,
            trial_name=self.trial_name,
            **kwargs,
        )


# Keep old name for backwards compatibility
@deprecated_class_name
class GATrialPDFGeneratorAlgorithm(GATrialPDFGeneratorAlgorithmJade):
    """Jade implementation of the PDF results report for the GA Algorithm."""

    pass
