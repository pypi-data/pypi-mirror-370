"""Fluid Volume multi-algorithm protocol.

First runs a model inference on the Fluid Volume model,
then the Fluid Volume algorithm to compute the volume
affected by WetAMD. Then CSV Report get generated.
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
from bitfount.federated.algorithms.ophthalmology.fluid_volume_calculation_algorithm import (  # noqa: E501
    FluidVolumeCalculationAlgorithm,
    _WorkerSide as _FVCalcWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    DICOM_COLUMNS_TO_RENAME,
    FLUID_COLUMNS_TO_RENAME,
    FLUID_RESULTS_COLUMNS,
    HEIDELBERG_COLUMNS_TO_RENAME,
    ORIGINAL_DICOM_COLUMNS,
    ORIGINAL_HEIDELBERG_COLUMNS,
    RESULTS_COLUMNS,
    FluidVolumeMetrics,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_utils import (
    _convert_predict_return_type_to_dataframe,
    get_data_for_files,
)
from bitfount.federated.authorisation_checkers import InferenceLimits, ProtocolContext
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.protocols.base import (
    BaseCompatibleAlgoFactory,
    BaseProtocolFactory,
    BaseWorkerProtocol,
    LimitsExceededInfo,
    ModelInferenceProtocolMixin,
    ProtocolState,
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


class _WorkerSide(BaseWorkerProtocol, ModelInferenceProtocolMixin):
    """Worker side of the Fluid Volume protocol.

    Args:
        algorithm: The sequence of Fluid Volume inference and additional algorithms
            to be used.
        mailbox: The mailbox to use for communication with the Modeller.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[
        Union[
            _InferenceWorkerSide,
            _FVCalcWorkerSide,
            _CSVWorkerSide,
        ]
    ]

    def __init__(
        self,
        *,
        algorithm: Sequence[
            Union[
                _InferenceWorkerSide,
                _FVCalcWorkerSide,
                _CSVWorkerSide,
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

    def define_csv_output_columns(self) -> list[str]:
        """Defines the output columns for the CSV report.

        Replaces the RESULTS_COLUMNS with FLUID_RESULTS_COLUMNS.

        Returns:
            A list of column names for the CSV report.
        """
        if type(self.datasource).__name__ == "HeidelbergSource":
            columns = ORIGINAL_HEIDELBERG_COLUMNS

        elif type(self.datasource).__name__ == "DICOMOphthalmologySource":
            columns = ORIGINAL_DICOM_COLUMNS
        else:
            _logger.warning(
                "Datasource type is not recognised; using default columns for CSV"
            )
            # Default to the original results columns if the datasource is not
            # recognised
            columns = RESULTS_COLUMNS

        # Replace RESULTS_COLUMNS with FLUID_RESULTS_COLUMNS
        # Find the index where the RESULTS_COLUMNS starts
        # Delete until the end of the RESULTS_COLUMNS
        # And insert the FLUID_RESULTS_COLUMNS instead
        insert_index = columns.index(RESULTS_COLUMNS[0])
        remove_index = insert_index + len(RESULTS_COLUMNS) - 1
        columns = (
            columns[:insert_index] + FLUID_RESULTS_COLUMNS + columns[remove_index + 1 :]
        )
        return columns

    def define_csv_output_rename_columns(self) -> dict[str, str]:
        """Defines the rename columns for the CSV report.

        If no rename_columns are provided, then FLUID_COLUMNS_TO_RENAME is used.

        Returns:
            A dictionary mapping original column keys to new names for the CSV report.
        """
        rename_columns: dict[str, str] = {}
        if type(self.datasource).__name__ == "HeidelbergSource":
            if self.rename_columns is None:
                rename_columns = dict(
                    HEIDELBERG_COLUMNS_TO_RENAME, **FLUID_COLUMNS_TO_RENAME
                )
        elif type(self.datasource).__name__ == "DICOMOphthalmologySource":
            if self.rename_columns is None:
                rename_columns = dict(
                    DICOM_COLUMNS_TO_RENAME, **FLUID_COLUMNS_TO_RENAME
                )
        if not rename_columns and self.rename_columns is not None:
            rename_columns = dict(self.rename_columns)
        return rename_columns

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
        """Runs Fluid Volume algorithm on worker side followed by csv algorithms.

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

        self.rename_columns = self.define_csv_output_rename_columns()

        # Unpack the algorithms
        (
            inference_algo,
            fluid_volume_calc_algo,
            csv_report_algo,
        ) = self.algorithm

        if pod_vitals:
            pod_vitals.last_task_execution_time = time.time()

        # Run Fluid Volume Algorithm
        # ga_predictions should be a dataframe
        _logger.info("Running Fluid Volume inference algorithm")
        inference_algo = cast(_InferenceWorkerSide, inference_algo)
        inference_predictions = inference_algo.run(return_data_keys=True)
        # Output will either be a dataframe (if ga_algo.class_outputs is set),
        # or a PredictReturnType, which we will need to convert into a dataframe.
        inference_predictions_df = _convert_predict_return_type_to_dataframe(
            inference_predictions
        )
        _logger.info(
            f"Fluid Volume inference algorithm completed:"
            f" {len(inference_predictions_df)} predictions made."
        )

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
            inference_predictions_df = inference_predictions_df.iloc[
                : limits_exceeded_info.allowed
            ]
            if protocol_state is not None:
                self._signal_final_step_for_limits_exceeded(protocol_state)

        # Try to get data keys from the predictions, if present
        try:
            filenames: list[str] = inference_predictions_df[
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
            records_count=len(inference_predictions_df),
            task_id=str(self._task_id),
            algorithm=inference_algo,
            protocol_batch_num=batch_num,
            project_id=self.project_id,
        )
        _logger.info("Metrics uploaded to task meter")

        # Sends empty results to modeller just to inform it to move on to the
        # next algorithm
        await self.mailbox.send_evaluation_results(
            eval_results={},
            resources_consumed=self.apply_actual_usage_to_resources_consumed(
                inference_algo,
                limits_exceeded_info,
            ),
        )

        # Extract Fluid Volume metrics from the predictions
        _logger.info("Running Fluid Volume calculation algorithm")
        fluid_volume_calc_algo = cast(_FVCalcWorkerSide, fluid_volume_calc_algo)
        # This dict maps filenames -> FluidVolumeMetrics or None
        fluid_volume_metrics: Mapping[str, Optional[FluidVolumeMetrics]] = (
            fluid_volume_calc_algo.run(
                predictions=inference_predictions_df, filenames=filenames
            )
        )
        _logger.info(
            f"Fluid Volume calculation algorithm completed:"
            f" metrics for {len(fluid_volume_metrics)} files calculated."
        )

        # Sends empty results to modeller just to inform it to move on to the
        # next algorithm
        await self.mailbox.send_evaluation_results({})

        # Convert fluid_volume_metrics dict to DataFrame for downstream use
        metrics_df = pd.DataFrame.from_records(
            [
                m.to_record() if isinstance(m, FluidVolumeMetrics) else {}
                for m in fluid_volume_metrics.values()
            ]
        )
        metrics_df[ORIGINAL_FILENAME_METADATA_COLUMN] = list(
            fluid_volume_metrics.keys()
        )
        metrics_df.reset_index(drop=True, inplace=True)
        # Ensure all fluid metrics columns are present
        # even if we don't have any metrics for them
        for col in FLUID_RESULTS_COLUMNS:
            if col not in metrics_df.columns:
                metrics_df[col] = pd.NA
        test_data_df: pd.DataFrame = get_data_for_files(
            cast(FileSystemIterableSource, self.datasource), filenames
        )
        # Join the metrics_df with the test_data_df just based on filename
        test_data_df = test_data_df.merge(
            metrics_df, on=ORIGINAL_FILENAME_METADATA_COLUMN
        )

        # Generate CSV(s)
        _logger.info("Generating CSV report")
        csv_report_algo = cast(_CSVWorkerSide, csv_report_algo)
        # Set the default columns for the CSV report algorithm
        csv_report_algo.original_cols = self.define_csv_output_columns()
        # Apply clinical criteria as filters to the algorithm
        # csv_report_algo.set_column_filters(column_filters)
        # Set the rename columns for the CSV report algorithm
        # based on protocol input
        csv_report_algo.rename_columns = self.rename_columns
        csv_report_algo.trial_name = self.trial_name
        csv_report_algo.run(
            results_df=metrics_df,
            task_id=self._task_id,
            final_batch=final_batch,
            filenames=filenames,
        )
        _logger.info("CSV report generation completed")

        # Sends empty results to modeller just to inform it to move on to the
        # next algorithm
        await self.mailbox.send_evaluation_results({})
        _logger.info("Worker side of the protocol completed")

        # Check if limits were exceeded and so we should abort any remaining protocol
        # batches
        if limits_exceeded_info:
            # limits_exceeded_info is not None if and only if limits is not None
            assert limits is not None  # nosec[assert_used]

            await self.handle_limits_exceeded(
                inference_algo, limits_exceeded_info, limits, self.mailbox
            )
        else:
            return pd.DataFrame()


class FluidVolumeScreeningProtocol(BaseProtocolFactory):
    """Protocol for running Fluid Volume Algorithms sequentially."""

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
                FluidVolumeCalculationAlgorithm,
                CSVReportGeneratorOphthalmologyAlgorithm,
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
        if algorithm.class_name not in (
            "bitfount.ModelInference",
            "bitfount.FluidVolumeCalculationAlgorithm",
            "bitfount.CSVReportGeneratorOphthalmologyAlgorithm",
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
                    FluidVolumeCalculationAlgorithm,
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
        """Returns worker side of the FluidVolumeScreeningProtocol protocol.

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
                    FluidVolumeCalculationAlgorithm,
                    CSVReportGeneratorOphthalmologyAlgorithm,
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
