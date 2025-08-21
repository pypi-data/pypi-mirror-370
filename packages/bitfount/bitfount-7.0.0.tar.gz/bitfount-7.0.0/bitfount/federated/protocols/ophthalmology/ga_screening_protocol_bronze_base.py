"""GA custom multi-algorithm protocol.

First runs a model inference on the Fovea model, then GA model, then
the GA algorithm to compute the area affected by GA.
Then CSV and PDF Reports get generated.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import time
from typing import TYPE_CHECKING, Any, Optional, Union, cast
import warnings

import pandas as pd

from bitfount.data.datasources.base_source import FileSystemIterableSource
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.federated.algorithms.ehr.ehr_patient_query_algorithm import (
    _WorkerSide as _NextGenQueryWorkerSide,
)
from bitfount.federated.algorithms.model_algorithms.inference import (
    _WorkerSide as _InferenceWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.csv_report_generation_ophth_algorithm import (  # noqa: E501
    _WorkerSide as _CSVWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_calculation_algorithm_bronze import (  # noqa: E501
    _WorkerSide as _GACalcWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_inclusion_criteria_match_algorithm_bronze import (  # noqa: E501
    _WorkerSide as _CriteriaMatchWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_pdf_algorithm_amethyst import (  # noqa: E501
    _WorkerSide as _PDFGenWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    GAMetricsWithFovea,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_utils import (
    _convert_ga_metrics_to_df,
    _convert_predict_return_type_to_dataframe,
    get_data_for_files,
)
from bitfount.federated.algorithms.ophthalmology.trial_inclusion_filters import (
    ColumnFilter,
)
from bitfount.federated.authorisation_checkers import InferenceLimits, ProtocolContext
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.protocols.base import (
    BaseWorkerProtocol,
    FinalStepReduceProtocol,
    LimitsExceededInfo,
    ModelInferenceProtocolMixin,
    ProtocolState,
)
from bitfount.federated.transport.message_service import TaskNotification
from bitfount.federated.transport.opentelemetry import get_task_meter
from bitfount.federated.transport.worker_transport import _WorkerMailbox

if TYPE_CHECKING:
    from bitfount.federated.pod_vitals import _PodVitals

_logger = _get_federated_logger(f"bitfount.federated.protocols.{__name__}")

# TODO: [NO_TICKET: Imported from ophthalmology] Change these?
_CRITERIA_MATCH_YES_KEY = "Yes"
_CRITERIA_MATCH_NO_KEY = "No"


class _WorkerSideBronzeBase(
    BaseWorkerProtocol,
    FinalStepReduceProtocol,
    ModelInferenceProtocolMixin,
):
    """Worker side of the GA protocol.

    Args:
        algorithm: The sequence of Fovea and GA inference
            and additional algorithms to be used.
        mailbox: The mailbox to use for communication with the Modeller.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[
        Union[
            _InferenceWorkerSide,
            _GACalcWorkerSide,
            _CriteriaMatchWorkerSide,
            _NextGenQueryWorkerSide,
            _CSVWorkerSide,
            _PDFGenWorkerSide,
        ]
    ]

    def __init__(
        self,
        *,
        algorithm: Sequence[
            Union[
                _InferenceWorkerSide,
                _GACalcWorkerSide,
                _CriteriaMatchWorkerSide,
                _NextGenQueryWorkerSide,
                _CSVWorkerSide,
                _PDFGenWorkerSide,
            ]
        ],
        mailbox: _WorkerMailbox,
        results_notification_email: bool = False,
        rename_columns: Optional[Mapping[str, str]] = None,
        trial_name: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)
        self.results_notification_email = results_notification_email
        self.rename_columns = rename_columns
        self.trial_name = trial_name
        self._task_meter = get_task_meter()
        self._task_id: Optional[str] = mailbox._task_id

    async def _run_fovea_inference(
        self,
        fovea_algo: _InferenceWorkerSide,
        limits: Optional[dict[str, InferenceLimits]],
        pod_vitals: Optional[_PodVitals],
        final_batch: bool,
        protocol_state: Optional[ProtocolState] = None,
    ) -> tuple[pd.DataFrame, Optional[LimitsExceededInfo], bool]:
        """Run Fovea inference algorithm.

        Args:
            fovea_algo: The Fovea inference algorithm.
            limits: Optional inference limits.
            pod_vitals: Optional pod vitals instance.
            final_batch: Indicates if this run is the final batch of the task.
            protocol_state: The state of the protocol, used to signal final step.

        Returns:
            Tuple of (fovea_predictions_df, fovea_limits_exceeded_info, final_batch).
        """
        if final_batch:
            warnings.warn(
                "final_batch parameter is deprecated and will be removed in a "
                "future release. Memory cleanup logic moved to run_final_reduce_step() "
                "method.",
                DeprecationWarning,
                stacklevel=2,
            )
        if pod_vitals:
            pod_vitals.last_task_execution_time = time.time()

        # Run Fovea Algorithm
        _logger.info("Running fovea inference algorithm")
        fovea_predictions = fovea_algo.run(return_data_keys=True)
        # Output will either be a dataframe (if ga_algo.class_outputs is set),
        # or a PredictReturnType, which we will need to convert into a dataframe.
        fovea_predictions_df = _convert_predict_return_type_to_dataframe(
            fovea_predictions
        )

        # Calculate resource usage from the previous inference step
        fovea_limits_exceeded_info: Optional[LimitsExceededInfo] = None
        if limits:
            fovea_limits_exceeded_info = self.check_usage_limits(limits, fovea_algo)

        # If limits were exceeded, reduce the predictions dataframe and proceed as
        # though this were the last batch
        if fovea_limits_exceeded_info:
            # model_id cannot be None as the only way the limits can be
            # calculated/exceeded is if the algo has a slug associated with it
            fovea_model_id: str = cast(str, fovea_algo.maybe_bitfount_model_slug)
            _logger.warning(
                f"Usage limits for {fovea_model_id}"
                f" exceeded by {fovea_limits_exceeded_info.overrun} inferences;"
                f" limiting to {fovea_limits_exceeded_info.allowed}"
                f" prediction results."
            )
            # Reduce predictions to the number that does _not_ exceed the limit
            fovea_predictions_df = fovea_predictions_df.iloc[
                : fovea_limits_exceeded_info.allowed
            ]
            if protocol_state is not None:
                self._signal_final_step_for_limits_exceeded(protocol_state)
            else:
                final_batch = True

        # Sends empty results to modeller just to inform it to move on to the
        # next algorithm
        await self.mailbox.send_evaluation_results(
            eval_results={},
            resources_consumed=self.apply_actual_usage_to_resources_consumed(
                fovea_algo,
                fovea_limits_exceeded_info,
            ),
        )

        return fovea_predictions_df, fovea_limits_exceeded_info, final_batch

    async def _run_ga_inference(
        self,
        ga_algo: _InferenceWorkerSide,
        limits: Optional[dict[str, InferenceLimits]],
        batch_num: Optional[int],
        final_batch: bool,
        protocol_state: Optional[ProtocolState] = None,
    ) -> tuple[pd.DataFrame, Optional[LimitsExceededInfo], bool, list[str]]:
        """Run GA inference algorithm.

        Args:
            ga_algo: The GA inference algorithm.
            limits: Optional inference limits.
            batch_num: The number of the batch being run.
            final_batch: Indicates if this run is the final batch of the task.
            protocol_state: The state of the protocol, used to signal final step.

        Returns:
            Tuple of (ga_predictions_df, ga_limits_exceeded_info,
              final_batch, filenames).
        """
        # Run GA Algorithm
        _logger.info("Running GA inference algorithm")
        ga_predictions = ga_algo.run(return_data_keys=True)
        # Output will either be a dataframe (if ga_algo.class_outputs is set),
        # or a PredictReturnType, which we will need to convert into a dataframe.
        ga_predictions_df = _convert_predict_return_type_to_dataframe(ga_predictions)
        _logger.info(
            f"GA inference algorithm completed:"
            f" {len(ga_predictions_df)} predictions made."
        )

        # Calculate resource usage from the previous inference step
        ga_limits_exceeded_info: Optional[LimitsExceededInfo] = None
        if limits:
            ga_limits_exceeded_info = self.check_usage_limits(limits, ga_algo)

        # If limits were exceeded, reduce the predictions dataframe and proceed as
        # though this were the last batch
        if ga_limits_exceeded_info:
            # model_id cannot be None as the only way the limits can be
            # calculated/exceeded is if the algo has a slug associated with it
            ga_model_id: str = cast(str, ga_algo.maybe_bitfount_model_slug)
            _logger.warning(
                f"Usage limits for {ga_model_id}"
                f"exceeded by {ga_limits_exceeded_info.overrun} inferences;"
                f" limiting to {ga_limits_exceeded_info.allowed}"
                f" prediction results."
            )
            # Reduce predictions to the number that does _not_ exceed the limit
            ga_predictions_df = ga_predictions_df.iloc[
                : ga_limits_exceeded_info.allowed
            ]
            if protocol_state is not None:
                self._signal_final_step_for_limits_exceeded(protocol_state)
            else:
                final_batch = True
        # Try to get data keys from the predictions, if present
        try:
            filenames: list[str] = ga_predictions_df[
                ORIGINAL_FILENAME_METADATA_COLUMN
            ].tolist()
        except KeyError as ke:
            # `filenames` is needed below, fail out if we cannot find them for this
            # protocol
            _logger.critical(
                "Unable to find data keys/filenames in GA predictions dataframe;"
                " unable to continue"
            )
            raise ValueError(
                "Unable to find data keys/filenames in GA predictions dataframe;"
                " unable to continue"
            ) from ke

        # Upload metrics to task meter
        _logger.info("Uploading metrics to task meter")
        self._task_meter.submit_algorithm_records_returned(
            records_count=len(ga_predictions_df),
            task_id=str(self._task_id),
            algorithm=ga_algo,
            protocol_batch_num=batch_num,
            project_id=self.project_id,
        )
        _logger.info("Metrics uploaded to task meter")

        # Sends empty results to modeller just to inform it to move on to the
        # next algorithm
        await self.mailbox.send_evaluation_results(
            eval_results={},
            resources_consumed=self.apply_actual_usage_to_resources_consumed(
                ga_algo,
                ga_limits_exceeded_info,
            ),
        )

        return ga_predictions_df, ga_limits_exceeded_info, final_batch, filenames

    async def _run_ga_calculation(
        self,
        ga_calc_algo: _GACalcWorkerSide,
        ga_predictions_df: pd.DataFrame,
        fovea_predictions_df: pd.DataFrame,
        filenames: list[str],
    ) -> dict[str, Optional[GAMetricsWithFovea]]:
        """Run GA calculation algorithm.

        Args:
            ga_calc_algo: The GA calculation algorithm.
            ga_predictions_df: GA predictions dataframe.
            fovea_predictions_df: Fovea predictions dataframe.
            filenames: List of filenames.

        Returns:
            Dictionary mapping filenames to GA metrics.
        """
        # Extract GA metrics from the predictions
        _logger.info("Running GA calculation algorithm")
        # This dict maps filenames -> metrics
        # Note: order will be correct as dict is sorted by insertion order,
        # and we only do clean/new insertions into this dict.
        ga_metrics: dict[str, Optional[GAMetricsWithFovea]] = ga_calc_algo.run(
            predictions=ga_predictions_df,
            fovea_predictions=fovea_predictions_df,
            filenames=filenames,
        )
        _logger.info(
            f"GA calculation algorithm completed:"
            f" metrics for {len(ga_metrics)} files calculated."
        )

        # Sends empty results to modeller just to inform it to move on to the
        # next algorithm
        await self.mailbox.send_evaluation_results({})

        return ga_metrics

    async def _run_criteria_matching(
        self,
        criteria_match_algo: _CriteriaMatchWorkerSide,
        ga_metrics: dict[str, Optional[GAMetricsWithFovea]],
        filenames: list[str],
        batch_num: Optional[int],
    ) -> tuple[pd.DataFrame, int, int, list[ColumnFilter], Optional[TaskNotification]]:
        """Run criteria matching algorithm.

        Args:
            criteria_match_algo: The criteria matching algorithm.
            ga_metrics: Dictionary mapping filenames to GA metrics.
            filenames: List of filenames.
            batch_num: The number of the batch being run.

        Returns:
            Tuple of (criteria_yes, criteria_no, column_filters, task_notification).
        """
        # Criteria matching
        _logger.info("Applying clinical criteria to CSV")
        # Apply clinical criteria to output dataframe and notify task meter
        _logger.debug("Finding outputs that match the clinical criteria")
        # We need a dataframe (of the correct length, i.e. the number of files)
        # so we construct it from the ga_metrics dict. Some of the values in
        # this dict may be None, so we handle that conversion.
        # Note: order will be correct as dict is sorted by insertion order,
        # and we only do clean/new insertions into this dict.
        metrics_df = _convert_ga_metrics_to_df(ga_metrics)
        test_data_df: pd.DataFrame = get_data_for_files(
            cast(FileSystemIterableSource, self.datasource), filenames
        )
        # Join the metrics_df with the test_data_df just based on filename
        test_data_df = test_data_df.merge(
            metrics_df, on=ORIGINAL_FILENAME_METADATA_COLUMN
        )

        criteria_yes, criteria_no = criteria_match_algo.run(test_data_df)
        column_filters = criteria_match_algo.get_column_filters()

        task_notification: Optional[TaskNotification] = None
        if criteria_yes > 0:
            plurarized_scans = "scan" if criteria_yes == 1 else "scans"
            task_notification = TaskNotification(
                message=(f"{criteria_yes} eligible {plurarized_scans} found"),
                email=self.results_notification_email,
            )

        # Upload metrics to task meter
        _logger.info("Uploading metrics to task meter")
        self._task_meter.submit_algorithm_records_per_class_returned(
            records_count_per_class={
                _CRITERIA_MATCH_YES_KEY: criteria_yes,
                _CRITERIA_MATCH_NO_KEY: criteria_no,
            },
            task_id=str(self._task_id),
            algorithm=criteria_match_algo,
            protocol_batch_num=batch_num,
            project_id=self.project_id,
        )
        _logger.info("Metrics uploaded to task meter")

        # Sends result count to modeller
        await self.mailbox.send_evaluation_results(
            {
                _CRITERIA_MATCH_YES_KEY: criteria_yes,
                _CRITERIA_MATCH_NO_KEY: criteria_no,
            },
            task_notification,
        )

        return (
            test_data_df,
            criteria_yes,
            criteria_no,
            column_filters,
            task_notification,
        )

    async def _run_reports_generation(
        self,
        csv_report_algo: _CSVWorkerSide,
        pdf_gen_algo: _PDFGenWorkerSide,
        ga_metrics: dict[str, Optional[GAMetricsWithFovea]],
        ga_predictions_df: pd.DataFrame,
        csv_results_df: pd.DataFrame,
        filenames: list[str],
        column_filters: list[ColumnFilter],
        criteria_match_algo: _CriteriaMatchWorkerSide,
        final_batch: bool,
    ) -> pd.DataFrame:
        """Run report generation (CSV and PDF).

        Args:
            csv_report_algo: The CSV report generation algorithm.
            pdf_gen_algo: The PDF generation algorithm.
            ga_metrics: Dictionary mapping filenames to GA metrics.
            ga_predictions_df: GA predictions dataframe.
            csv_results_df: dataframe for CSV results.
            filenames: List of filenames.
            column_filters: Column filters from criteria matching.
            criteria_match_algo: The criteria matching algorithm.
            final_batch: Indicates if this is the final batch.

        Returns:
            Results with PDF paths.
        """
        # Generate CSV(s)
        _logger.info("Generating CSV report")
        # Set the default columns for the CSV report algorithm
        csv_report_algo.use_default_columns()
        # Apply clinical criteria as filters to the algorithm
        csv_report_algo.set_column_filters(column_filters)
        # Set the rename columns for the CSV report algorithm
        # based on protocol input
        csv_report_algo.rename_columns = self.rename_columns
        csv_report_algo.trial_name = self.trial_name

        csv_report_algo.run(
            results_df=csv_results_df,
            task_id=self._task_id,
            final_batch=final_batch,
            filenames=filenames,
        )
        _logger.info("CSV report generation completed")

        # Sends empty results to modeller just to inform it to move on to the
        # next algorithm
        await self.mailbox.send_evaluation_results({})

        # Create PDFs
        _logger.info("Generating PDF report")
        # Apply clinical criteria as filters to the algorithm
        pdf_gen_algo.set_column_filters(column_filters)
        pdf_gen_algo.trial_name = self.trial_name
        results_with_pdf_paths = pdf_gen_algo.run(
            ga_predictions_df,
            ga_metrics,
            task_id=self._task_id,
            filenames=filenames,
            # We need to pass the total GA area bounds to the PDF generator so that the
            # graphics slider will match the scale of the GA area
            total_ga_area_lower_bound=criteria_match_algo.total_ga_area_lower_bound,
            total_ga_area_upper_bound=criteria_match_algo.total_ga_area_upper_bound,
        )
        _logger.info("PDF report generation completed")

        # Sends empty results to modeller just to inform it that we have finished
        await self.mailbox.send_evaluation_results({})
        _logger.info("Worker side of the protocol completed")
        _logger.info("")

        return results_with_pdf_paths

    async def run(
        self,
        *,
        pod_vitals: Optional[_PodVitals] = None,
        context: Optional[ProtocolContext] = None,
        batch_num: Optional[int] = None,
        final_batch: bool = False,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Runs GA algorithm on worker side followed by metrics and csv algorithms.

        Args:
            pod_vitals: Optional. Pod vitals instance for recording run-time details
                from the protocol run.
            context: Optional. Run-time context for the protocol.
            batch_num: The number of the batch being run.
            final_batch: If this run of the protocol represents the final run within
                a task.
            **kwargs: Additional keyword arguments.
        """
        raise NotImplementedError()
