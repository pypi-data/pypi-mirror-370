"""Basic OCT custom single-algorithm protocol.

Runs the basic OCT aclgorithm to classify a condition from single bscan images.
"""

from __future__ import annotations

from collections.abc import Sequence
import time
from typing import TYPE_CHECKING, Any, Optional, Union, cast

from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.federated.algorithms.base import (
    NoResultsModellerAlgorithm as _CSVModellerSide,
)
from bitfount.federated.algorithms.model_algorithms.inference import (
    ModelInference,
    _ModellerSide as _InferenceModellerSide,
    _WorkerSide as _InferenceWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.csv_report_generation_ophth_algorithm import (  # noqa: E501
    CSVReportGeneratorOphthalmologyAlgorithm,
    _WorkerSide as _CSVWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_utils import (
    _convert_predict_return_type_to_dataframe,
)
from bitfount.federated.authorisation_checkers import InferenceLimits, ProtocolContext
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.protocols.base import (
    BaseCompatibleAlgoFactory,
    BaseModellerProtocol,
    BaseProtocolFactory,
    BaseWorkerProtocol,
    FinalStepProtocol,
    LimitsExceededInfo,
    ModelInferenceProtocolMixin,
)
from bitfount.federated.transport.modeller_transport import (
    _ModellerMailbox,
    _send_model_parameters,
)
from bitfount.federated.transport.worker_transport import (
    _get_model_parameters,
    _WorkerMailbox,
)
from bitfount.types import _SerializedWeights, _Weights
from bitfount.utils.logging_utils import deprecated_class_name

if TYPE_CHECKING:
    from bitfount.federated.pod_vitals import _PodVitals
    from bitfount.hub.api import BitfountHub

_logger = _get_federated_logger(f"bitfount.federated.protocols.{__name__}")


class _ModellerSide(BaseModellerProtocol):
    """Modeller side of the protocol.

    Args:
        algorithm: The single basic OCT algorithm to be used.
        mailbox: The mailbox to use for communication with the Workers.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[Union[_InferenceModellerSide, _CSVModellerSide]]

    def __init__(
        self,
        *,
        algorithm: Sequence[Union[_InferenceModellerSide, _CSVModellerSide]],
        mailbox: _ModellerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

    async def _send_parameters(self, new_parameters: _SerializedWeights) -> None:
        """Sends central model parameters to workers."""
        _logger.debug("Sending global parameters to workers")
        await _send_model_parameters(new_parameters, self.mailbox)

    async def run(
        self, *, context: Optional[ProtocolContext] = None, **kwargs: Any
    ) -> Union[list[Any], Any]:
        """Runs Modeller side of the protocol.

        This just sends the model parameters to the workers and then tells
        the workers when the protocol is finished.

        Args:
            context: Optional. Run-time context for the protocol.
            **kwargs: Additional keyword arguments.
        """
        results = []
        for algo in self.algorithm:
            if hasattr(algo, "model"):
                initial_parameters: _Weights = algo.model.get_param_states()
                serialized_params = algo.model.serialize_params(initial_parameters)
                await self._send_parameters(serialized_params)
                result = await self.mailbox.get_evaluation_results_from_workers()
                results.append(result)
                _logger.info("Received results from Pods.")
        final_results = [
            algo.run(result_) for algo, result_ in zip(self.algorithm, results)
        ]

        return final_results


class _WorkerSide(
    BaseWorkerProtocol,
    FinalStepProtocol,
    ModelInferenceProtocolMixin,
):
    """Worker side of the Basic OCT protocol.

    Args:
        algorithm: The single basic OCT worker algorithms to be used.
        mailbox: The mailbox to use for communication with the Modeller.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[Union[_InferenceWorkerSide, _CSVWorkerSide]]

    def __init__(
        self,
        *,
        algorithm: Sequence[Union[_InferenceWorkerSide, _CSVWorkerSide]],
        mailbox: _WorkerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

    async def _receive_parameters(self) -> _SerializedWeights:
        """Receives new global model parameters."""
        _logger.debug("Receiving global parameters")
        return await _get_model_parameters(self.mailbox)

    async def run(
        self,
        *,
        pod_vitals: Optional[_PodVitals] = None,
        context: Optional[ProtocolContext] = None,
        final_batch: bool = False,
        **kwargs: Any,
    ) -> None:
        """Runs Basic OCT algorithm on worker side.

        Args:
            pod_vitals: Optional. Pod vitals instance for recording run-time details
                from the protocol run.
            context: Optional. Run-time context for the protocol.
            final_batch: If this run of the protocol represents the final run within
                a task.
            **kwargs: Additional keyword arguments.
        """
        # Unpack the algorithm into the two algorithms
        basic_oct_algo, csv_report_algo = self.algorithm

        # Run Fovea Algorithm
        basic_oct_algo = cast(_InferenceWorkerSide, basic_oct_algo)
        model_params = await self._receive_parameters()
        if pod_vitals:
            pod_vitals.last_task_execution_time = time.time()
        oct_predictions = basic_oct_algo.run(
            model_params=model_params, return_data_keys=True
        )

        # Output will either be a dataframe (if basic_oct_algo.class_outputs is set),
        # or a PredictReturnType, which we will need to convert into a dataframe.
        oct_predictions_df = _convert_predict_return_type_to_dataframe(oct_predictions)

        # Calculate resource usage from the previous inference step
        limits_exceeded_info: Optional[LimitsExceededInfo] = None
        limits: Optional[dict[str, InferenceLimits]] = (
            context.inference_limits if context is not None else None
        )
        if limits:
            limits_exceeded_info = self.check_usage_limits(limits, basic_oct_algo)

        # If limits were exceeded, reduce the predictions dataframe and proceed as
        # though this were the last batch
        if limits_exceeded_info:
            # model_id cannot be None as the only way the limits can be
            # calculated/exceeded is if the algo has a slug associated with it
            model_id: str = cast(str, basic_oct_algo.maybe_bitfount_model_slug)
            _logger.warning(
                f"Usage limits for {model_id}"
                f"exceeded by {limits_exceeded_info.overrun} inferences;"
                f" limiting to {limits_exceeded_info.allowed}"
                f" prediction results."
            )
            # Reduce predictions to the number that does _not_ exceed the limit
            oct_predictions_df = oct_predictions_df.iloc[: limits_exceeded_info.allowed]
            final_batch = True

        # Try to get data keys from the predictions, if present
        filenames: Optional[list[str]] = None
        try:
            filenames = oct_predictions_df[ORIGINAL_FILENAME_METADATA_COLUMN].tolist()
        except KeyError:
            _logger.warning(
                "Unable to find data keys/filenames in OCT predictions dataframe"
            )

        csv_report_algo = cast(_CSVWorkerSide, csv_report_algo)
        csv_report_algo.run(
            results_df=oct_predictions_df,
            task_id=self.mailbox._task_id,
            final_batch=final_batch,
            filenames=filenames,
        )

        # Sends empty results to modeller just to inform it to move on to the
        # next algorithm
        await self.mailbox.send_evaluation_results(
            resources_consumed=self.apply_actual_usage_to_resources_consumed(
                basic_oct_algo,
                limits_exceeded_info,
            ),
        )

        # Check if limits were exceeded and so we should abort any remaining protocol
        # batches
        if limits_exceeded_info:
            # limits_exceeded_info is not None if and only if limits is not None
            assert limits is not None  # nosec[assert_used]

            await self.handle_limits_exceeded(
                basic_oct_algo, limits_exceeded_info, limits, self.mailbox
            )


class RetinalDiseaseProtocolCobalt(BaseProtocolFactory):
    """Protocol for running the basic OCT model algorithm."""

    def __init__(
        self,
        *,
        algorithm: Sequence[
            Union[ModelInference, CSVReportGeneratorOphthalmologyAlgorithm]
        ],
        **kwargs: Any,
    ) -> None:
        super().__init__(algorithm=algorithm, **kwargs)

    @classmethod
    def _validate_algorithm(cls, algorithm: BaseCompatibleAlgoFactory) -> None:
        """Validates the algorithm by ensuring it is Basic OCT."""
        if algorithm.class_name not in (
            "bitfount.ModelInference",
            "bitfount.CSVReportGeneratorOphthalmologyAlgorithm",
            "bitfount.CSVReportGeneratorAlgorithm",  # Kept for backwards compatibility
            # Without ".bitfount" prefix for backwards compatibility
            "CSVReportGeneratorOphthalmologyAlgorithm",
            "CSVReportGeneratorAlgorithm",  # Kept for backwards compatibility
        ):
            raise TypeError(
                f"The {cls.__name__} protocol does not support "
                + f"the {type(algorithm).__name__} algorithm.",
            )

    def modeller(self, mailbox: _ModellerMailbox, **kwargs: Any) -> _ModellerSide:
        """Returns the Modeller side of the protocol."""
        algorithms = cast(
            Sequence[Union[ModelInference, CSVReportGeneratorOphthalmologyAlgorithm]],
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
        """Returns worker side of the RetinalDiseaseProtocolCobalt protocol.

        Args:
            mailbox: Worker mailbox instance to allow communication to the modeller.
            hub: `BitfountHub` object to use for communication with the hub.
            context: Optional. Run-time protocol context details for running.
            **kwargs: Additional keyword arguments.
        """
        algorithms = cast(
            Sequence[Union[ModelInference, CSVReportGeneratorOphthalmologyAlgorithm]],
            self.algorithms,
        )
        return _WorkerSide(
            algorithm=[algo.worker(hub=hub, context=context) for algo in algorithms],
            mailbox=mailbox,
            **kwargs,
        )


# Keep old name for backwards compatibility
@deprecated_class_name
class BasicOCTProtocol(RetinalDiseaseProtocolCobalt):
    """Protocol for running the basic OCT model algorithm."""

    pass
