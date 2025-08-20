"""GA custom multi-algorithm protocol.

First runs a model inference on the GA model, then
the GA algorithm to compute the area affected by GA.
Then CSV and PDF Reports get generated.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import time
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Tuple, Union, cast

from marshmallow import fields
import pandas as pd

from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.federated.algorithms.ehr.ehr_patient_query_algorithm import (
    EHR_QUERY_COLUMNS,
    EHRPatientQueryAlgorithm,
    PatientDetails,
    PatientQueryResults,
    _WorkerSide as _NextGenQueryWorkerSide,
)
from bitfount.federated.algorithms.filtering_algorithm import (
    RecordFilterAlgorithm,
    _WorkerSide as _RecordFilterWorkerSide,
)
from bitfount.federated.algorithms.model_algorithms.inference import (
    ModelInference,
    _WorkerSide as _InferenceWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.dataframe_generation_extensions import (  # noqa: E501
    generate_bitfount_patient_id,
    generate_subfoveal_indicator,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_calculation_algorithm_base import (  # noqa: E501
    _BaseWorkerSideWithFovea as _GACalcWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_calculation_algorithm_charcoal import (  # noqa: E501
    GATrialCalculationAlgorithmCharcoal,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_inclusion_criteria_match_algorithm_charcoal import (  # noqa: E501
    TrialInclusionCriteriaMatchAlgorithmCharcoal,
    _WorkerSide as _TrialInclWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    AGE_COL,
    DOB_COL,
    FILTER_FAILED_REASON_COLUMN,
    FILTER_MATCHING_COLUMN,
    MAX_CNV_PROBABILITY_COL_PREFIX,
    NAME_COL,
    SUBFOVEAL_COL,
    TOTAL_GA_AREA_COL_PREFIX,
    GAMetricsWithFovea,
    max_pathology_prob_col_name,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_utils import (
    _convert_ga_metrics_to_df,
    _convert_predict_return_type_to_dataframe,
    use_default_rename_columns,
)
from bitfount.federated.algorithms.ophthalmology.reduce_csv_algorithm_charcoal import (
    ReduceCSVAlgorithmCharcoal,
    _WorkerSide as _ReduceCSVWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.simple_csv_algorithm import (
    _SimpleCSVAlgorithm,
    _WorkerSide as _CSVWorkerSide,
)
from bitfount.federated.authorisation_checkers import InferenceLimits, ProtocolContext
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.protocols.base import (
    BaseCompatibleAlgoFactory,
    BaseProtocolFactory,
    BaseWorkerProtocol,
    FinalStepReduceProtocol,
    InitialSetupProtocol,
    LimitsExceededInfo,
    ModelInferenceProtocolMixin,
    ProtocolState,
)
from bitfount.federated.protocols.ophthalmology.utils import (
    GenericOphthalmologyModellerSide as _ModellerSide,
)
from bitfount.federated.transport.message_service import TaskNotification
from bitfount.federated.transport.modeller_transport import _ModellerMailbox
from bitfount.federated.transport.opentelemetry import get_task_meter
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.types import T_FIELDS_DICT
from bitfount.utils.pandas_utils import (
    find_dob_column,
    find_full_name_column,
)

if TYPE_CHECKING:
    from bitfount.federated.pod_vitals import _PodVitals
    from bitfount.hub.api import BitfountHub

_logger = _get_federated_logger(f"bitfount.federated.protocols.{__name__}")

# TODO: [NO_TICKET: Imported from ophthalmology] Change these?
_CRITERIA_MATCH_YES_KEY = "Yes"
_CRITERIA_MATCH_NO_KEY = "No"

CHARCOAL_INTERMEDIATE_CSV_COLUMNS = EHR_QUERY_COLUMNS + [
    # Patient details
    AGE_COL,
    # Model metrics
    TOTAL_GA_AREA_COL_PREFIX,
    SUBFOVEAL_COL,
    MAX_CNV_PROBABILITY_COL_PREFIX,
    max_pathology_prob_col_name("hard_drusen"),
    max_pathology_prob_col_name("soft_drusen"),
    max_pathology_prob_col_name("confluent_drusen"),
    # Eligibility
    FILTER_MATCHING_COLUMN,
    FILTER_FAILED_REASON_COLUMN,
]


class _WorkerSide(
    BaseWorkerProtocol,
    InitialSetupProtocol[_RecordFilterWorkerSide],
    FinalStepReduceProtocol,
    ModelInferenceProtocolMixin,
):
    """Worker side of the GA protocol.

    Args:
        algorithm: The sequence of GA inference and additional algorithms to be used.
        mailbox: The mailbox to use for communication with the Modeller.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[
        Union[
            _RecordFilterWorkerSide,
            _NextGenQueryWorkerSide,
            _InferenceWorkerSide,
            _GACalcWorkerSide,
            _TrialInclWorkerSide,
            _CSVWorkerSide,
            _ReduceCSVWorkerSide,
        ]
    ]

    def __init__(
        self,
        *,
        algorithm: Sequence[
            Union[
                _RecordFilterWorkerSide,
                _NextGenQueryWorkerSide,
                _InferenceWorkerSide,
                _GACalcWorkerSide,
                _TrialInclWorkerSide,
                _CSVWorkerSide,
                _ReduceCSVWorkerSide,
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
        self.new_data_available: bool = False

    async def run(
        self,
        *,
        pod_vitals: Optional[_PodVitals] = None,
        context: Optional[ProtocolContext] = None,
        batch_num: Optional[int] = None,
        final_batch: bool = False,
        protocol_state: Optional[ProtocolState] = None,
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
            protocol_state: The state of the protocol, used to signal final step.
            **kwargs: Additional keyword arguments.
        """
        # Use datasource-default column renamings if none provided
        self.rename_columns = use_default_rename_columns(
            self.datasource, self.rename_columns
        )

        # Unpack the algorithms
        (
            record_filter_algo,
            next_gen_query_algo,
            fovea_algo,
            ga_algo,
            ga_calc_algo,
            trial_incl_algo,
            csv_report_algo,
            reduce_csv_algo,
        ) = self.algorithm

        if pod_vitals:
            pod_vitals.last_task_execution_time = time.time()

        # Run record filter algo (noop)
        cast(_RecordFilterWorkerSide, record_filter_algo).run()
        # Send empty results to modeller to move to next algorithm
        await self.mailbox.send_evaluation_results({})

        # Retrieve the data for this run
        # This should only read the current batch into memory (roughly 16 rows)
        dfs: list[pd.DataFrame] = list(self.datasource.yield_data(use_cache=True))
        file_data: pd.DataFrame
        if any(not df.empty for df in dfs):
            file_data = pd.concat(dfs, axis="index")
            file_data = generate_bitfount_patient_id(
                file_data,
                name_col=(
                    found_name_col
                    if (found_name_col := find_full_name_column(file_data)) is not None
                    else NAME_COL
                ),
                dob_col=(
                    found_dob_col
                    if (found_dob_col := find_dob_column(file_data)) is not None
                    else DOB_COL
                ),
            )

            if found_name_col is not None:
                file_data = file_data.rename({found_name_col: NAME_COL}, axis=1)
            if found_dob_col is not None:
                file_data = file_data.rename({found_dob_col: DOB_COL}, axis=1)
        else:
            file_data = pd.DataFrame()

        # Run NextGen Query Algorithm
        _logger.info("Running NextGen patient query algorithm")
        data_with_ehr: pd.DataFrame
        query_results: dict[PatientDetails, PatientQueryResults] = {}
        if not file_data.empty:
            next_gen_query_algo = cast(_NextGenQueryWorkerSide, next_gen_query_algo)
            query_results = next_gen_query_algo.run(
                next_gen_query_algo.dataframe_to_patient_details(file_data)
            )
            data_with_ehr = next_gen_query_algo.merge_results_with_dataframe(
                query_results,
                file_data,
            )
            # Remove full dataframe from memory once necessary info is used
            del file_data
        else:
            _logger.warning(
                "No file data was extracted. No queries to EHR will be made."
            )
            data_with_ehr = pd.DataFrame()
        _logger.info(
            f"NextGen query algorithm completed: {len(query_results)} records found"
        )

        # Send empty results to modeller to move to next algorithm
        await self.mailbox.send_evaluation_results({})

        # Run Fovea Algorithm
        # fovea_predictions should be a dataframe
        _logger.info("Running fovea inference algorithm")
        fovea_algo = cast(_InferenceWorkerSide, fovea_algo)
        fovea_predictions = fovea_algo.run(return_data_keys=True)
        # Output will either be a dataframe (if ga_algo.class_outputs is set),
        # or a PredictReturnType, which we will need to convert into a dataframe.
        fovea_predictions_df = _convert_predict_return_type_to_dataframe(
            fovea_predictions
        )

        _logger.info(
            f"Fovea inference algorithm completed:"
            f" {len(fovea_predictions_df)} predictions made."
        )

        # If limits were exceeded, reduce the predictions dataframe and proceed as
        # though this were the last batch
        fovea_predictions_df, fovea_limits_exceeded_info, final_batch = (
            self.apply_usage_limits(
                context, fovea_predictions_df, fovea_algo, final_batch
            )
        )

        # Sends empty results to modeller just to inform it to move on to the
        # next algorithm
        await self.mailbox.send_evaluation_results(
            eval_results={},
            resources_consumed=self.apply_actual_usage_to_resources_consumed(
                fovea_algo,
                fovea_limits_exceeded_info,
            ),
        )

        # Run GA Algorithm
        _logger.info("Running GA inference algorithm")
        ga_algo = cast(_InferenceWorkerSide, ga_algo)
        ga_predictions = ga_algo.run(return_data_keys=True)

        # Output will either be a dataframe (if ga_algo.class_outputs is set),
        # or a PredictReturnType, which we will need to convert into a dataframe.
        ga_predictions_df = _convert_predict_return_type_to_dataframe(ga_predictions)

        _logger.info(
            f"GA inference algorithm completed:"
            f" {len(ga_predictions_df)} predictions made."
        )

        ga_predictions_df, ga_limits_exceeded_info, final_batch = (
            self.apply_usage_limits(context, ga_predictions_df, ga_algo, final_batch)
        )

        # Try to get data keys from the predictions, if present
        try:
            if ga_predictions_df.empty:
                filenames: list[str] = []
            else:
                filenames = ga_predictions_df[
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

        # Trial Calculations (GA Metrics) from the predictions
        _logger.info("Running GA calculation algorithm")
        ga_calc_algo = cast(_GACalcWorkerSide, ga_calc_algo)
        # This dict maps filenames -> metrics
        # Note: order will be correct as dict is sorted by insertion order,
        # and we only do clean/new insertions into this dict.
        ga_metrics: Mapping[str, Optional[GAMetricsWithFovea]] = ga_calc_algo.run(
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

        # Combine GA Metrics with existing dataframe
        metrics_df = _convert_ga_metrics_to_df(
            ga_metrics,
            additional_pathology_prob_cols=[
                "hard_drusen",
                "soft_drusen",
                "confluent_drusen",
            ],
        )

        # Join the metrics_df with the test_data_df just based on filename
        if not ga_predictions_df.empty:
            # Merge EHR data with ga_predictions
            # DEV: We merge on ga_predictions_df rather than fovea_predictions_df as
            #      we only need one df to contain the EHR data and the
            #      ga_predictions_df is used in downstream algos whereas the
            #      fovea_predictions_df is not.
            ga_predictions_with_ehr_df = data_with_ehr.merge(
                ga_predictions_df, on=ORIGINAL_FILENAME_METADATA_COLUMN
            )
            test_data_df = ga_predictions_with_ehr_df.merge(
                metrics_df, on=ORIGINAL_FILENAME_METADATA_COLUMN
            )
        else:
            test_data_df = pd.DataFrame()

        # Trial Inclusion Algo - Criteria matching
        _logger.info("Applying clinical criteria")
        # Apply clinical criteria to output dataframe and notify task meter
        _logger.debug("Finding outputs that match the clinical criteria")

        criteria_match_algo = cast(_TrialInclWorkerSide, trial_incl_algo)
        matched_df = criteria_match_algo.run_and_return_dataframe(test_data_df)

        if matched_df.empty:
            criteria_yes_count, criteria_no_count = 0, 0
        else:
            criteria_yes_count = int(matched_df[FILTER_MATCHING_COLUMN].sum())
            criteria_no_count = int((~matched_df[FILTER_MATCHING_COLUMN]).sum())

        task_notification: Optional[TaskNotification] = None
        if criteria_yes_count > 0:
            plurarized_scans = "scan" if criteria_yes_count == 1 else "scans"
            task_notification = TaskNotification(
                message=f"{criteria_yes_count} eligible {plurarized_scans} found",
                email=self.results_notification_email,
            )

        # Upload metrics to task meter
        _logger.info("Uploading metrics to task meter")
        self._task_meter.submit_algorithm_records_per_class_returned(
            records_count_per_class={
                _CRITERIA_MATCH_YES_KEY: criteria_yes_count,
                _CRITERIA_MATCH_NO_KEY: criteria_no_count,
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
                _CRITERIA_MATCH_YES_KEY: criteria_yes_count,
                _CRITERIA_MATCH_NO_KEY: criteria_no_count,
            },
            task_notification,
        )

        # Generate Intermediate CSV Reports
        _logger.info("Generating (Intermediate) CSV report")
        if not matched_df.empty:
            # Add subfoveal indicator column
            _logger.debug("Adding subfoveal indicator column to CSV")
            matched_df = generate_subfoveal_indicator(matched_df)

            csv_report_algo = cast(_CSVWorkerSide, csv_report_algo)
            csv_report_algo.run(
                df=matched_df,
                task_id=self._task_id,
                output_columns=CHARCOAL_INTERMEDIATE_CSV_COLUMNS,
            )
        else:
            _logger.warning(
                "No new data was extracted. Nothing will be written to CSV."
            )
        _logger.info("Intermediate CSV report generation completed")

        # Sends empty results to modeller just to inform it to move on to the
        # next algorithm
        await self.mailbox.send_evaluation_results({})
        if not matched_df.empty:
            self.new_data_available = True
        else:
            self.new_data_available = False

        # Sends empty results to modeller just to inform it to move on to the
        # next algorithm
        await self.mailbox.send_evaluation_results({})

        _logger.info("Worker side of the protocol completed")

        # Check if limits were exceeded and if so
        # we abort any remaining protocol batches
        if ga_limits_exceeded_info:
            limits = context.inference_limits if context is not None else None
            # limits_exceeded_info is not None if and only if limits is not None
            assert limits is not None  # nosec[assert_used]
            if protocol_state is not None:
                self._signal_final_step_for_limits_exceeded(protocol_state)
            await self.handle_limits_exceeded(
                ga_algo,
                ga_limits_exceeded_info,
                limits,
                self.mailbox,
            )

        else:
            return matched_df

    async def run_final_step(
        self, context: Optional[ProtocolContext] = None, **kwargs: Any
    ) -> None:
        """Runs the final reduce step for the protocol."""
        if self.new_data_available:
            _logger.info("Running final reduce step for the protocol")
            reduce_csv_algo = cast(_ReduceCSVWorkerSide, self.algorithm[-1])
            reduce_csv_algo.run(task_id=self._task_id)
            _logger.info("Final reduce step completed")
        else:
            _logger.info(
                "No new data was available for the final reduce step; skipping."
            )

    def apply_usage_limits(
        self,
        context: Optional[ProtocolContext],
        predictions_df: pd.DataFrame,
        inference_algo: _InferenceWorkerSide,
        final_batch: bool,
    ) -> Tuple[pd.DataFrame, Optional[LimitsExceededInfo], bool]:
        """Apply usage limits by reducing inference results.

        Returns:
            3-tuple of the predictions dataframe (potentially reduced), limits
            exceeded info (or None if limits not exceeded), and a boolean indicating
            whether this should now be treated as the final batch.
        """
        # Calculate resource usage from the previous inference step
        limits_exceeded_info: Optional[LimitsExceededInfo] = None
        limits: Optional[dict[str, InferenceLimits]] = (
            context.inference_limits if context is not None else None
        )
        if limits:
            limits_exceeded_info = self.check_usage_limits(limits, inference_algo)

        # If limits were exceeded, reduce the predictions dataframe and proceed as
        # though this were the last batch
        if limits_exceeded_info:
            # model_id cannot be None as the only way the limits can be
            # calculated/exceeded is if the algo has a slug associated with it
            model_id: str = cast(str, inference_algo.maybe_bitfount_model_slug)
            _logger.warning(
                f"Usage limits for {model_id}"
                f"exceeded by {limits_exceeded_info.overrun} inferences;"
                f" limiting to {limits_exceeded_info.allowed} prediction results."
            )

            # Reduce predictions to the number that does _not_ exceed the limit
            predictions_df = predictions_df.iloc[: limits_exceeded_info.allowed]
            final_batch = True

        return predictions_df, limits_exceeded_info, final_batch


class GAScreeningProtocolCharcoal(BaseProtocolFactory):
    """Protocol for running GA Algorithms sequentially."""

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "results_notification_email": fields.Boolean(allow_none=True),
        "rename_columns": fields.Dict(
            keys=fields.Str(), values=fields.Str(), allow_none=True
        ),
        "trial_name": fields.Str(allow_none=True),
    }

    def __init__(
        self,
        *,
        algorithm: Sequence[
            Union[
                RecordFilterAlgorithm,
                EHRPatientQueryAlgorithm,
                ModelInference,
                GATrialCalculationAlgorithmCharcoal,
                TrialInclusionCriteriaMatchAlgorithmCharcoal,
                _SimpleCSVAlgorithm,
                ReduceCSVAlgorithmCharcoal,
            ]
        ],
        results_notification_email: Optional[bool] = False,
        trial_name: Optional[str] = None,
        rename_columns: Optional[Mapping[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(algorithm=algorithm, **kwargs)
        self.results_notification_email = (
            results_notification_email
            if results_notification_email is not None
            else False
        )
        self.rename_columns = rename_columns
        self.trial_name = trial_name

    @classmethod
    def _validate_algorithm(cls, algorithm: BaseCompatibleAlgoFactory) -> None:
        """Validates the algorithms by ensuring they are either GA or Fovea."""
        if (
            algorithm.class_name
            not in (
                "bitfount.RecordFilterAlgorithm",
                "bitfount.EHRPatientQueryAlgorithm",
                "bitfount.ModelInference",
                "bitfount.GATrialCalculationAlgorithmCharcoal",
                "bitfount.TrialInclusionCriteriaMatchAlgorithmCharcoal",
                "bitfount._SimpleCSVAlgorithm",
                "bitfount.ReduceCSVAlgorithmCharcoal",
                "bitfount.CSVReportGeneratorAlgorithm",  # Kept for backwards compatibility # noqa: E501
            )
        ):
            raise TypeError(
                f"The {cls.__name__} protocol does not support "
                + f"the {type(algorithm).__name__} algorithm.",
            )

    def modeller(self, mailbox: _ModellerMailbox, **kwargs: Any) -> _ModellerSide:
        """Returns the Modeller side of the protocol."""
        algorithms = cast(
            Sequence[
                Union[
                    RecordFilterAlgorithm,
                    EHRPatientQueryAlgorithm,
                    ModelInference,
                    GATrialCalculationAlgorithmCharcoal,
                    TrialInclusionCriteriaMatchAlgorithmCharcoal,
                    _SimpleCSVAlgorithm,
                    ReduceCSVAlgorithmCharcoal,
                ]
            ],
            self.algorithms,
        )
        modeller_algos = []
        for algo in algorithms:
            if hasattr(algo, "pretrained_file"):
                modeller_algos.append(
                    algo.modeller(pretrained_file=algo.pretrained_file)
                )
            else:
                modeller_algos.append(algo.modeller())
        return _ModellerSide(
            algorithm=modeller_algos,
            mailbox=mailbox,
            **kwargs,
        )

    def worker(
        self,
        mailbox: _WorkerMailbox,
        hub: BitfountHub,
        context: Optional[ProtocolContext] = None,
        **kwargs: Any,
    ) -> _WorkerSide:
        """Returns worker side of the GAScreeningProtocolCharcoal protocol.

        Args:
            mailbox: Worker mailbox instance to allow communication to the modeller.
            hub: `BitfountHub` object to use for communication with the hub.
            context: Optional. Run-time protocol context details for running.
            **kwargs: Additional keyword arguments.
        """
        algorithms = cast(
            Sequence[
                Union[
                    RecordFilterAlgorithm,
                    EHRPatientQueryAlgorithm,
                    ModelInference,
                    GATrialCalculationAlgorithmCharcoal,
                    TrialInclusionCriteriaMatchAlgorithmCharcoal,
                    _SimpleCSVAlgorithm,
                    ReduceCSVAlgorithmCharcoal,
                ]
            ],
            self.algorithms,
        )
        return _WorkerSide(
            algorithm=[algo.worker(hub=hub, context=context) for algo in algorithms],
            mailbox=mailbox,
            results_notification_email=self.results_notification_email,
            trial_name=self.trial_name,
            rename_columns=self.rename_columns,
            **kwargs,
        )
