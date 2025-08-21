"""In-site insights protocol.

This protocol is used to generate aggregated patient insights for clinics. First, the
fovea model is run, then the GA model, then the GA calculation algorithm, and finally
CSV generation. Each task run produces a CSV file as normal but no PDF files.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
import time
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Union, cast

from marshmallow import fields

from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.encryption.encryption import _FernetEncryption
from bitfount.federated.algorithms.filtering_algorithm import (
    RecordFilterAlgorithm,
    _WorkerSide as _FilterWorkerSide,
)
from bitfount.federated.algorithms.model_algorithms.inference import (
    ModelInference,
    _WorkerSide as _InferenceWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.csv_report_generation_ophth_algorithm import (  # noqa: E501
    CSVReportGeneratorOphthalmologyAlgorithm,
    _WorkerSide as _CSVWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_calculation_algorithm_bronze import (  # noqa: E501
    GATrialCalculationAlgorithmBronze,
    _WorkerSide as _GACalcWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    GAMetricsWithFovea,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_utils import (
    _convert_ga_metrics_to_df,
    _convert_predict_return_type_to_dataframe,
    use_default_rename_columns,
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
)
from bitfount.federated.protocols.ophthalmology.utils import (
    GenericOphthalmologyModellerSide as _ModellerSide,
)
from bitfount.federated.transport.modeller_transport import _ModellerMailbox
from bitfount.federated.transport.opentelemetry import get_task_meter
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.types import T_FIELDS_DICT

if TYPE_CHECKING:
    from bitfount.federated.pod_vitals import _PodVitals
    from bitfount.hub.api import BitfountHub

_logger = _get_federated_logger(f"bitfount.federated.protocols.{__name__}")


class _WorkerSide(
    BaseWorkerProtocol,
    InitialSetupProtocol[_FilterWorkerSide],
    FinalStepReduceProtocol,
    ModelInferenceProtocolMixin,
):
    """Worker side of the InSite Insights protocol.

    Args:
        algorithm: The sequence of algorithms to be used.
        mailbox: The mailbox to use for communication with the Modeller.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[
        Union[
            _FilterWorkerSide,
            _InferenceWorkerSide,
            _GACalcWorkerSide,
            _CSVWorkerSide,
        ]
    ]

    def __init__(
        self,
        *,
        algorithm: Sequence[
            Union[
                _FilterWorkerSide,
                _InferenceWorkerSide,
                _GACalcWorkerSide,
                _CSVWorkerSide,
            ]
        ],
        mailbox: _WorkerMailbox,
        results_notification_email: bool = False,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)
        self.results_notification_email = results_notification_email
        self._task_meter = get_task_meter()
        self._task_id: Optional[str] = mailbox._task_id

    def _get_encryption_key(self) -> Optional[str]:
        """Get the encryption key for the pod.

        Derives a Fernet encryption key from the pod's RSA private key.
        If the pod private key is not found, returns None.

        Returns:
            The derived Fernet key as a string, or None if encryption is not available.
        """
        if not hasattr(self, "parent_pod_identifier") or not self.parent_pod_identifier:
            _logger.warning("No parent pod identifier for encryption key derivation")
            return None

        # Extract username and pod name from parent_pod_identifier
        # (format: username/pod_name)
        pod_identifier = self.parent_pod_identifier
        if not pod_identifier or "/" not in pod_identifier:
            _logger.warning("Invalid pod_identifier format: %s", pod_identifier)
            return None

        username, pod_name = pod_identifier.split("/", 1)

        # Construct path to pod's private key
        key_path = Path(f"~/.bitfount/{username}/pods/{pod_name}/pod_rsa.pem")
        key_path = key_path.expanduser()

        # Check if the key file exists
        if not key_path.exists():
            _logger.warning("Pod private key not found")
            return None

        try:
            # Derive Fernet key from the pod's RSA private key
            derived_key = _FernetEncryption.derive_key_from_path(
                ssh_key_path=key_path, salt=b"insite-insights-csv"
            )
            if derived_key is None:
                _logger.warning("Failed to derive encryption key from pod private key")
                return None
            return derived_key.decode("utf-8")
        except Exception as e:
            _logger.warning("Failed to derive encryption key: %s", e)
            return None

    async def run(
        self,
        *,
        pod_vitals: Optional[_PodVitals] = None,
        context: Optional[ProtocolContext] = None,
        batch_num: Optional[int] = None,
        final_batch: bool = False,
        **kwargs: Any,
    ) -> None:
        """Runs algorithms on worker side.

        Filtering, fovea, GA, GA calculation and CSV generation.

        Args:
            pod_vitals: Optional. Pod vitals instance for recording run-time details
                from the protocol run.
            context: Optional. Run-time context for the protocol.
            batch_num: The number of the batch being run.
            final_batch: If this run of the protocol represents the final run within
                a task.
            **kwargs: Additional keyword arguments.
        """
        rename_columns = use_default_rename_columns(self.datasource, None)

        limits: Optional[dict[str, InferenceLimits]] = (
            context.inference_limits if context is not None else None
        )

        # Unpack algorithms with filter
        filter_algo, fovea_algo, ga_algo, ga_calc_algo, csv_report_algo = self.algorithm

        # Run Filter Algorithm (just for consistency - filtering has already been done)
        cast(_FilterWorkerSide, filter_algo).run()

        # Send empty results to modeller to indicate filter step is complete
        await self.mailbox.send_evaluation_results({})

        if pod_vitals:
            pod_vitals.last_task_execution_time = time.time()

        # Run Fovea Algorithm
        _logger.info("Running fovea inference algorithm")
        fovea_algo = cast(_InferenceWorkerSide, fovea_algo)
        fovea_predictions = fovea_algo.run(return_data_keys=True)
        # Output will either be a dataframe (if fovea_algo.class_outputs is set),
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
                f"Usage limits for {ga_model_id} "
                f"exceeded by {ga_limits_exceeded_info.overrun} inferences;"
                f" limiting to {ga_limits_exceeded_info.allowed}"
                f" prediction results."
            )
            # Reduce predictions to the number that does _not_ exceed the limit
            ga_predictions_df = ga_predictions_df.iloc[
                : ga_limits_exceeded_info.allowed
            ]
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

        # Extract GA metrics from the predictions
        _logger.info("Running GA calculation algorithm")
        ga_calc_algo = cast(_GACalcWorkerSide, ga_calc_algo)
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

        # Convert GA metrics to dataframe for CSV generation
        metrics_df = _convert_ga_metrics_to_df(
            ga_metrics,
            additional_pathology_prob_cols=[
                "diabetic_macular_edema",
                "dry_amd",
                "wet_amd",
            ],
        )

        # Generate CSV report
        _logger.info("Generating CSV report")
        csv_report_algo = cast(_CSVWorkerSide, csv_report_algo)
        # Set the default columns for the CSV report algorithm
        csv_report_algo.use_default_columns()
        # Set the rename columns for the CSV report algorithm
        # based on protocol input
        csv_report_algo.rename_columns = rename_columns
        csv_report_algo.run(
            results_df=metrics_df,
            task_id=self._task_id,
            final_batch=final_batch,
            filenames=filenames,
            encryption_key=self._get_encryption_key(),
        )
        _logger.info("CSV report generation completed")

        # Sends empty results to modeller just to inform it that we have finished
        await self.mailbox.send_evaluation_results({})
        _logger.info("Worker side of the protocol completed")

        # Check if limits were exceeded and so we should abort any remaining protocol
        # batches
        if fovea_limits_exceeded_info:
            # fovea_limits_exceeded_info is not None if and only if limits is not None
            assert limits is not None  # nosec[assert_used]

            await self.handle_limits_exceeded(
                fovea_algo, fovea_limits_exceeded_info, limits, self.mailbox
            )
        elif ga_limits_exceeded_info:
            # ga_limits_exceeded_info is not None if and only if limits is not None
            assert limits is not None  # nosec[assert_used]

            await self.handle_limits_exceeded(
                ga_algo, ga_limits_exceeded_info, limits, self.mailbox
            )


class InSiteInsightsProtocol(BaseProtocolFactory):
    """Protocol for generating aggregated patient insights for clinics."""

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "results_notification_email": fields.Boolean(allow_none=True),
    }

    def __init__(
        self,
        *,
        algorithm: Sequence[
            Union[
                RecordFilterAlgorithm,
                ModelInference,
                GATrialCalculationAlgorithmBronze,
                CSVReportGeneratorOphthalmologyAlgorithm,
            ]
        ],
        results_notification_email: Optional[bool] = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(algorithm=algorithm, **kwargs)
        self.results_notification_email = (
            results_notification_email
            if results_notification_email is not None
            else False
        )

    @classmethod
    def _validate_algorithm(cls, algorithm: BaseCompatibleAlgoFactory) -> None:
        """Validates the algorithms by ensuring they are supported algorithm types."""
        if algorithm.class_name not in (
            "bitfount.ModelInference",
            "bitfount.GATrialCalculationAlgorithmBronze",
            "bitfount.CSVReportGeneratorOphthalmologyAlgorithm",
            "bitfount.RecordFilterAlgorithm",
        ):
            raise TypeError(
                f"The {cls.__name__} protocol does not support "
                + f"the {type(algorithm).__name__} algorithm."
            )

    def modeller(self, mailbox: _ModellerMailbox, **kwargs: Any) -> _ModellerSide:
        """Returns the Modeller side of the protocol."""
        algorithms = cast(
            Sequence[
                Union[
                    RecordFilterAlgorithm,
                    ModelInference,
                    GATrialCalculationAlgorithmBronze,
                    CSVReportGeneratorOphthalmologyAlgorithm,
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
        """Returns worker side of the InSiteInsightsProtocol protocol.

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
                    ModelInference,
                    GATrialCalculationAlgorithmBronze,
                    CSVReportGeneratorOphthalmologyAlgorithm,
                ]
            ],
            self.algorithms,
        )
        return _WorkerSide(
            algorithm=[algo.worker(hub=hub, context=context) for algo in algorithms],
            mailbox=mailbox,
            results_notification_email=self.results_notification_email,
            **kwargs,
        )
