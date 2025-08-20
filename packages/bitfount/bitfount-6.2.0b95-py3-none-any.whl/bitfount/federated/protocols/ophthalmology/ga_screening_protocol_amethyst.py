"""GA custom multi-algorithm protocol.

First runs a model inference on the GA model, then
the GA algorithm to compute the area affected by GA.
Then CSV and PDF Reports get generated.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import time
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Union, cast
import warnings

from marshmallow import fields
import pandas as pd

from bitfount.data.datasources.base_source import FileSystemIterableSource
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.federated.algorithms.model_algorithms.inference import (
    ModelInference,
    _WorkerSide as _InferenceWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.csv_report_generation_ophth_algorithm import (  # noqa: E501
    CSVReportGeneratorOphthalmologyAlgorithm,
    _WorkerSide as _CSVWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_calculation_algorithm_amethyst import (  # noqa: E501
    GATrialCalculationAlgorithmAmethyst,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_calculation_algorithm_base import (  # noqa: E501
    GAMetrics,
    _WorkerSide as _GACalcWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_calculation_algorithm_jade import (  # noqa: E501
    GATrialCalculationAlgorithmJade,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_inclusion_criteria_match_algorithm_amethyst import (  # noqa: E501
    TrialInclusionCriteriaMatchAlgorithmAmethyst,
    _WorkerSide as _CriteriaMatchWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_pdf_algorithm_amethyst import (  # noqa: E501
    GATrialPDFGeneratorAlgorithmAmethyst,
    _WorkerSide as _PDFGenWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_utils import (
    _convert_ga_metrics_to_df,
    _convert_predict_return_type_to_dataframe,
    get_data_for_files,
    use_default_rename_columns,
)
from bitfount.federated.authorisation_checkers import InferenceLimits, ProtocolContext
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.protocols.base import (
    BaseCompatibleAlgoFactory,
    BaseProtocolFactory,
    BaseWorkerProtocol,
    FinalStepReduceProtocol,
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

if TYPE_CHECKING:
    from bitfount.federated.pod_vitals import _PodVitals
    from bitfount.hub.api import BitfountHub

_logger = _get_federated_logger(f"bitfount.federated.protocols.{__name__}")

# TODO: [NO_TICKET: Imported from ophthalmology] Change these?
_CRITERIA_MATCH_YES_KEY = "Yes"
_CRITERIA_MATCH_NO_KEY = "No"


class _WorkerSide(
    BaseWorkerProtocol,
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
            _InferenceWorkerSide,
            _GACalcWorkerSide,
            _CriteriaMatchWorkerSide,
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
            context: Run-time context for the protocol. Optional, defaults to None.
            batch_num: The number of the batch being run.
            final_batch: Whether this is the last batch of the protocol. Deprecated.
            protocol_state: State of the protocol, used to signal final reduce.
            **kwargs: Additional keyword arguments.
        """
        if final_batch:
            warnings.warn(
                "final_batch parameter is deprecated and will be removed in a "
                "future release. Memory cleanup logic moved to run_final_step() "
                "method.",
                DeprecationWarning,
                stacklevel=2,
            )
        self.rename_columns = use_default_rename_columns(
            self.datasource, self.rename_columns
        )

        # Unpack the algorithms
        (
            ga_algo,
            ga_calc_algo,
            criteria_match_algo,
            csv_report_algo,
            pdf_gen_algo,
        ) = self.algorithm

        if pod_vitals:
            pod_vitals.last_task_execution_time = time.time()

        # Run GA Algorithm
        # ga_predictions should be a dataframe
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

        # Calculate resource usage from the previous inference step
        limits_exceeded_info: Optional[LimitsExceededInfo] = None
        limits: Optional[dict[str, InferenceLimits]] = (
            context.inference_limits if context is not None else None
        )
        if limits:
            limits_exceeded_info = self.check_usage_limits(limits, ga_algo)

        # If limits were exceeded, reduce the predictions dataframe and proceed as
        # though this were the last batch
        if limits_exceeded_info:
            # model_id cannot be None as the only way the limits can be
            # calculated/exceeded is if the algo has a slug associated with it
            model_id: str = cast(str, ga_algo.maybe_bitfount_model_slug)
            _logger.warning(
                f"Usage limits for {model_id}"
                f"exceeded by {limits_exceeded_info.overrun} inferences;"
                f" limiting to {limits_exceeded_info.allowed} prediction results."
            )
            # Reduce predictions to the number that does _not_ exceed the limit
            ga_predictions_df = ga_predictions_df.iloc[: limits_exceeded_info.allowed]
            if protocol_state is not None:
                self._signal_final_step_for_limits_exceeded(protocol_state)

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
                limits_exceeded_info,
            ),
        )

        # Extract GA metrics from the predictions
        _logger.info("Running GA calculation algorithm")
        ga_calc_algo = cast(_GACalcWorkerSide, ga_calc_algo)
        # This dict maps filenames -> metrics
        # Note: order will be correct as dict is sorted by insertion order,
        # and we only do clean/new insertions into this dict.
        ga_metrics: Mapping[str, Optional[GAMetrics]] = ga_calc_algo.run(
            predictions=ga_predictions_df, filenames=filenames
        )
        _logger.info(
            f"GA calculation algorithm completed:"
            f" metrics for {len(ga_metrics)} files calculated."
        )

        # Sends empty results to modeller just to inform it to move on to the
        # next algorithm
        await self.mailbox.send_evaluation_results({})

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

        criteria_match_algo = cast(_CriteriaMatchWorkerSide, criteria_match_algo)

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

        # Generate CSV(s)
        _logger.info("Generating CSV report")
        csv_report_algo = cast(_CSVWorkerSide, csv_report_algo)
        # Set the default columns for the CSV report algorithm
        csv_report_algo.use_default_columns()
        # Apply clinical criteria as filters to the algorithm
        csv_report_algo.set_column_filters(column_filters)
        # Set the rename columns for the CSV report algorithm
        # based on protocol input
        csv_report_algo.rename_columns = self.rename_columns
        csv_report_algo.trial_name = self.trial_name
        csv_report_algo.run(
            results_df=metrics_df,
            task_id=self._task_id,
            filenames=filenames,
        )
        _logger.info("CSV report generation completed")

        # Sends empty results to modeller just to inform it to move on to the
        # next algorithm
        await self.mailbox.send_evaluation_results({})
        # Create PDFs
        _logger.info("Generating PDF report")
        pdf_gen_algo = cast(_PDFGenWorkerSide, pdf_gen_algo)
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

        # Check if limits were exceeded and so we should abort any remaining protocol
        # batches
        if limits_exceeded_info:
            # limits_exceeded_info is not None if and only if limits is not None
            assert limits is not None  # nosec[assert_used]

            await self.handle_limits_exceeded(
                ga_algo, limits_exceeded_info, limits, self.mailbox
            )
        else:
            return results_with_pdf_paths


class GAScreeningProtocolAmethyst(BaseProtocolFactory):
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
                ModelInference,
                GATrialCalculationAlgorithmJade,
                GATrialCalculationAlgorithmAmethyst,
                TrialInclusionCriteriaMatchAlgorithmAmethyst,
                CSVReportGeneratorOphthalmologyAlgorithm,
                GATrialPDFGeneratorAlgorithmAmethyst,
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
                "bitfount.ModelInference",
                "bitfount.GATrialCalculationAlgorithmJade",  # Kept for backwards compatibility # noqa: E501
                "bitfount.GATrialCalculationAlgorithmAmethyst",
                "bitfount.TrialInclusionCriteriaMatchAlgorithmAmethyst",
                "bitfount.CSVReportGeneratorOphthalmologyAlgorithm",
                "bitfount.CSVReportGeneratorAlgorithm",  # Kept for backwards compatibility # noqa: E501
                "bitfount.GATrialPDFGeneratorAlgorithmAmethyst",
                # Without "bitfount." prefix for backwards compatibility
                "GATrialCalculationAlgorithmJade",  # Kept for backwards compatibility
                "GATrialCalculationAlgorithmAmethyst",
                "CSVReportGeneratorOphthalmologyAlgorithm",
                "CSVReportGeneratorAlgorithm",  # Kept for backwards compatibility
                "GATrialPDFGeneratorAlgorithmAmethyst",
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
                    ModelInference,
                    GATrialCalculationAlgorithmJade,  # Kept for backwards compatibility
                    GATrialCalculationAlgorithmAmethyst,
                    TrialInclusionCriteriaMatchAlgorithmAmethyst,
                    CSVReportGeneratorOphthalmologyAlgorithm,
                    GATrialPDFGeneratorAlgorithmAmethyst,
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
        """Returns worker side of the GAScreeningProtocolAmethyst protocol.

        Args:
            mailbox: Worker mailbox instance to allow communication to the modeller.
            hub: `BitfountHub` object to use for communication with the hub.
            context: Optional. Run-time protocol context details for running.
            **kwargs: Additional keyword arguments.
        """
        algorithms = cast(
            Sequence[
                Union[
                    ModelInference,
                    GATrialCalculationAlgorithmJade,  # Kept for backwards compatibility
                    GATrialCalculationAlgorithmAmethyst,
                    TrialInclusionCriteriaMatchAlgorithmAmethyst,
                    CSVReportGeneratorOphthalmologyAlgorithm,
                    GATrialPDFGeneratorAlgorithmAmethyst,
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
