"""Protocol for combinging a single model inference and a csv algorithm."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import os
import time
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Protocol,
    Union,
    cast,
    runtime_checkable,
)

import pandas as pd

from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.federated.algorithms.base import FinalStepAlgorithm
from bitfount.federated.algorithms.csv_report_algorithm import (
    _WorkerSide as _CSVWorkerSide,
)
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseWorkerModelAlgorithm,
)
from bitfount.federated.algorithms.model_algorithms.inference import (
    _WorkerSide as _InferenceWorkerSide,
)
from bitfount.federated.authorisation_checkers import InferenceLimits, ProtocolContext
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.protocols.base import (
    BaseCompatibleAlgoFactory,
    BaseCompatibleAlgoFactoryWorkerHubNeeded,
    BaseCompatibleAlgoFactoryWorkerStandard,
    BaseCompatibleModellerAlgorithm,
    BaseCompatibleWorkerAlgorithm,
    BaseModellerProtocol,
    BaseProtocolFactory,
    BaseWorkerProtocol,
    FinalStepProtocol,
    LimitsExceededInfo,
    ModelInferenceProtocolMixin,
)
from bitfount.federated.transport.message_service import ResourceConsumed
from bitfount.federated.transport.modeller_transport import (
    _ModellerMailbox,
)
from bitfount.federated.transport.worker_transport import (
    _WorkerMailbox,
)
from bitfount.types import (
    DistributedModelProtocol,
    PredictReturnType,
    _SerializedWeights,
    _StrAnyDict,
)

if TYPE_CHECKING:
    from bitfount.federated.model_reference import BitfountModelReference
    from bitfount.federated.pod_vitals import _PodVitals
    from bitfount.hub.api import BitfountHub

logger = _get_federated_logger("bitfount.federated.protocols" + __name__)


@runtime_checkable
class _InferenceAndCSVReportCompatibleModellerAlgorithm(
    BaseCompatibleModellerAlgorithm, Protocol
):
    """Defines modeller-side algorithm compatibility."""

    def run(self, results: Mapping[str, Any]) -> _StrAnyDict:
        """Runs the modeller-side algorithm."""
        ...


@runtime_checkable
class _InferenceAndCSVReportCompatibleWorkerAlgorithm(
    BaseCompatibleWorkerAlgorithm, Protocol
):
    """Defines worker-side algorithm compatibility."""

    pass


@runtime_checkable
class _InferenceAndCSVReportModelIncompatibleWorkerAlgorithm(
    _InferenceAndCSVReportCompatibleWorkerAlgorithm, Protocol
):
    """Defines worker-side algorithm compatibility without model params."""

    def run(self, *, return_data_keys: bool = False, final_batch: bool = False) -> Any:
        """Runs the worker-side algorithm."""
        ...


@runtime_checkable
class _InferenceAndCSVReportModelCompatibleWorkerAlgorithm(
    _InferenceAndCSVReportCompatibleWorkerAlgorithm, Protocol
):
    """Defines worker-side algorithm compatibility with model params needed."""

    def run(
        self,
        model_params: _SerializedWeights,
        *,
        return_data_keys: bool = False,
    ) -> Any:
        """Runs the worker-side algorithm."""
        ...


@runtime_checkable
class _InferenceAndCSVReportCSVCompatibleWorkerAlgorithm(
    _InferenceAndCSVReportCompatibleWorkerAlgorithm, Protocol
):
    """Defines worker-side algorithm compatibility for CSV algorithm."""

    def run(
        self,
        results_df: Union[pd.DataFrame, list[pd.DataFrame]],
        task_id: Optional[str] = None,
    ) -> str:
        """Runs the worker-side algorithm."""
        ...


class _ModellerSide(BaseModellerProtocol):
    """Modeller side of the protocol.

    Args:
        algorithm: A list of algorithms to be run by the protocol. This should be
            a list of two algorithms, the first being the model inference algorithm
            and the second being the csv report algorithm.
        mailbox: The mailbox to use for communication with the Workers.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[_InferenceAndCSVReportCompatibleModellerAlgorithm]

    def __init__(
        self,
        *,
        algorithm: Sequence[_InferenceAndCSVReportCompatibleModellerAlgorithm],
        mailbox: _ModellerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

    async def run(
        self,
        *,
        context: Optional[ProtocolContext] = None,
        results_from_worker: bool = False,
        **kwargs: Any,
    ) -> Optional[_StrAnyDict]:
        """Runs Modeller side of the protocol.

        This just sends the model parameters to the workers and then tells
        the workers when the protocol is finished.

        Args:
            context: Optional. Run-time context for the protocol.
            results_from_worker: Whether to return the results received from the
                worker.
            **kwargs: Additional keyword arguments.
        """

        results = await self.mailbox.get_evaluation_results_from_workers()
        return None if not results_from_worker else results


class _WorkerSide(BaseWorkerProtocol, FinalStepProtocol, ModelInferenceProtocolMixin):
    """Worker side of the protocol.

    Args:
        algorithm: A list of algorithms to be run by the protocol. This should be
            a list of two algorithms, the first being the model inference algorithm
            and the second being the csv report algorithm.
        mailbox: The mailbox to use for communication with the Modeller.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[
        Union[
            _InferenceAndCSVReportModelCompatibleWorkerAlgorithm,
            _InferenceAndCSVReportModelIncompatibleWorkerAlgorithm,
            _InferenceAndCSVReportCSVCompatibleWorkerAlgorithm,
        ]
    ]

    def __init__(
        self,
        *,
        algorithm: Sequence[
            Union[
                _InferenceAndCSVReportModelCompatibleWorkerAlgorithm,
                _InferenceAndCSVReportModelIncompatibleWorkerAlgorithm,
                _InferenceAndCSVReportCSVCompatibleWorkerAlgorithm,
            ]
        ],
        mailbox: _WorkerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

    async def run(
        self,
        *,
        pod_vitals: Optional[_PodVitals] = None,
        context: Optional[ProtocolContext] = None,
        return_results_to_modeller: bool = False,
        final_batch: bool = False,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Runs the protocol on worker side.

        Handles ensuring that model usage limits are adhered to.

        Args:
            pod_vitals: Optional. Pod vitals instance for recording run-time details
                from the protocol run.
            context: Optional. Run-time context for the protocol.
            return_results_to_modeller: Whether to return results from the worker to
                the modeller.
            final_batch: If this run of the protocol represents the final run within
                a task.
            **kwargs: Additional keyword arguments.
        """
        model_predictions_df, limits_exceeded_tuple = await self._run(
            pod_vitals=pod_vitals,
            context=context,
            return_results_to_modeller=return_results_to_modeller,
            final_batch=final_batch,
            **kwargs,
        )

        # Check if limits were exceeded and so we should abort any remaining protocol
        # batches
        if limits_exceeded_tuple is not None:
            limits_exceeded_info, limits, model_inference_algo = limits_exceeded_tuple
            if limits_exceeded_info:
                # This will deliberately raise an exception
                await self.handle_limits_exceeded(
                    model_inference_algo,
                    limits_exceeded_info,
                    limits,
                    self.mailbox,
                )

        # Return the model_predictions from the model inference
        # algorithm so we can enable saving to the project database
        # for this protocol type
        return model_predictions_df

    async def _run(
        self,
        *,
        pod_vitals: Optional[_PodVitals] = None,
        context: Optional[ProtocolContext] = None,
        return_results_to_modeller: bool = False,
        final_batch: bool = False,
        **kwargs: Any,
    ) -> tuple[
        pd.DataFrame,
        Optional[
            tuple[LimitsExceededInfo, dict[str, InferenceLimits], _InferenceWorkerSide]
        ],
    ]:
        """Internal runner of the protocol on worker side.

        Handles all steps of the protocol excepting the raising of limits exceeded
        task abortion, so that whatever is calling it can make that call instead.

        Args:
            pod_vitals: Optional. Pod vitals instance for recording run-time details
                from the protocol run.
            context: Optional. Run-time context for the protocol.
            return_results_to_modeller: Whether to return results from the worker to
                the modeller.
            final_batch: If this run of the protocol represents the final run within
                a task.
            **kwargs: Additional keyword arguments.

        Returns:
            2-tuple of the results from the run and an optional 3-tuple regarding
            usage limits being exceeded and so the task should be aborted:
            information on how the limits were exceeded, the limits information in
            question, and the model inference algorithm where the limits were exceeded.
        """
        # Unpack the algorithm into the two algorithms
        model_inference_algo, csv_report_algo = self.algorithm

        if pod_vitals:
            pod_vitals.last_task_execution_time = time.time()

        # Run Inference Algorithm
        logger.info("Running model inference algorithm")
        model_predictions: Union[PredictReturnType, pd.DataFrame]
        if isinstance(model_inference_algo, _BaseWorkerModelAlgorithm):
            model_predictions = model_inference_algo.run(
                return_data_keys=True, final_batch=final_batch
            )
        else:
            assert not isinstance(  # nosec[assert_used]
                model_inference_algo, _CSVWorkerSide
            )
            model_inference_algo = cast(
                _InferenceAndCSVReportModelIncompatibleWorkerAlgorithm,
                model_inference_algo,
            )
            model_predictions = model_inference_algo.run(
                return_data_keys=True, final_batch=final_batch
            )

        # Output will either be a dataframe (if model_inference_algo.class_outputs is
        # set), or a PredictReturnType, which may have the predictions stored as a
        # dataframe.
        model_predictions_df: pd.DataFrame
        if isinstance(model_predictions, PredictReturnType):
            if isinstance(model_predictions.preds, pd.DataFrame):
                model_predictions_df = model_predictions.preds
            else:
                raise TypeError(
                    f"Model prediction must return a Dataframe"
                    f" to enable CSV report output;"
                    f" got {type(model_predictions)}"
                    f" with {type(model_predictions.preds)} predictions instead."
                )

            # Add keys to DataFrame
            if model_predictions.keys is not None:
                model_predictions_df[ORIGINAL_FILENAME_METADATA_COLUMN] = (
                    model_predictions.keys
                )
        else:  # is DataFrame
            model_predictions_df = model_predictions

        # Calculate resource usage from the previous inference step
        limits_exceeded_info: Optional[LimitsExceededInfo] = None
        limits: Optional[dict[str, InferenceLimits]] = (
            context.inference_limits if context is not None else None
        )
        if isinstance(model_inference_algo, _InferenceWorkerSide):
            if limits:
                limits_exceeded_info = self.check_usage_limits(
                    limits, model_inference_algo
                )

            # If limits were exceeded, reduce the predictions dataframe and proceed as
            # though this were the last batch
            if limits_exceeded_info:
                # model_id cannot be None as the only way the limits can be
                # calculated/exceeded is if the algo has a slug associated with it
                model_id: str = cast(
                    str, model_inference_algo.maybe_bitfount_model_slug
                )
                logger.warning(
                    f"Usage limits for {model_id}"
                    f"exceeded by {limits_exceeded_info.overrun} inferences;"
                    f" limiting to {limits_exceeded_info.allowed} prediction results."
                )
                # Reduce predictions to the number that does _not_ exceed the limit
                model_predictions_df = model_predictions_df.iloc[
                    : limits_exceeded_info.allowed
                ]

        # Run CSV Report Generation
        logger.info("Running CSV report algorithm")
        csv_report_algo = cast(_CSVWorkerSide, csv_report_algo)
        csv_formatted_predictions = csv_report_algo.run(
            results_df=model_predictions_df,
            task_id=self.mailbox._task_id,
        )

        # Apply limits to the resources consumed information
        resources_consumed: Optional[list[ResourceConsumed]] = None
        if isinstance(model_inference_algo, _InferenceWorkerSide):
            resources_consumed = self.apply_actual_usage_to_resources_consumed(
                model_inference_algo,
                limits_exceeded_info,
            )

        if return_results_to_modeller:
            # Sends results to modeller if enabled.
            await self.mailbox.send_evaluation_results(
                eval_results={"csv": csv_formatted_predictions},
                resources_consumed=resources_consumed,
            )
        else:
            # Sends empty results to modeller just to inform it to move on to the
            # next algorithm.
            await self.mailbox.send_evaluation_results(
                resources_consumed=resources_consumed,
            )

        # Return the model_predictions from the model inference
        # algorithm so we can enable saving to the project database
        # for this protocol type
        if limits_exceeded_info:
            # limits_exceeded_info is not None if and only if limits is not None
            assert limits is not None  # nosec[assert_used]

            # mypy: Only way to get into this branch is if limits_exceeded is set
            # above, which requires that model_inference_algo is a
            # _InferenceWorkerSide instance.
            return model_predictions_df, (
                limits_exceeded_info,
                limits,
                cast(_InferenceWorkerSide, model_inference_algo),
            )
        else:
            return model_predictions_df, None

    async def run_final_step(
        self, context: Optional[ProtocolContext] = None, **kwargs: Any
    ) -> Any:
        """Run the final reduce step of the protocol.

        Args:
            context: Optional. Run-time context for the protocol.
            **kwargs: Additional keyword arguments.
        """
        for algo in self.algorithm:
            if isinstance(algo, FinalStepAlgorithm):
                # Run the final reduce step of any algorithm that has one
                algo.run_final_step(
                    context=context,
                    **kwargs,
                )


@runtime_checkable
class _InferenceAndCSVReportCompatibleAlgoFactory(Protocol):
    """Defines algo factory compatibility."""

    def modeller(
        self, **kwargs: Any
    ) -> _InferenceAndCSVReportCompatibleModellerAlgorithm:
        """Create a modeller-side algorithm."""
        ...


@runtime_checkable
class _InferenceAndCSVReportCompatibleAlgoFactory_(
    _InferenceAndCSVReportCompatibleAlgoFactory,
    BaseCompatibleAlgoFactoryWorkerStandard[
        Union[
            _InferenceAndCSVReportModelIncompatibleWorkerAlgorithm,
            _InferenceAndCSVReportModelCompatibleWorkerAlgorithm,
        ]
    ],
    Protocol,
):
    """Defines algo factory compatibility."""

    def worker(
        self, **kwargs: Any
    ) -> Union[
        _InferenceAndCSVReportModelIncompatibleWorkerAlgorithm,
        _InferenceAndCSVReportModelCompatibleWorkerAlgorithm,
    ]:
        """Create a worker-side algorithm."""
        ...


@runtime_checkable
class _InferenceAndCSVReportCompatibleHuggingFaceAlgoFactory(
    _InferenceAndCSVReportCompatibleAlgoFactory,
    BaseCompatibleAlgoFactoryWorkerHubNeeded[
        Union[
            _InferenceAndCSVReportModelIncompatibleWorkerAlgorithm,
            _InferenceAndCSVReportModelCompatibleWorkerAlgorithm,
        ]
    ],
    Protocol,
):
    """Defines algo factory compatibility."""

    model_id: str

    def worker(
        self, *, hub: BitfountHub, **kwargs: Any
    ) -> Union[
        _InferenceAndCSVReportModelIncompatibleWorkerAlgorithm,
        _InferenceAndCSVReportModelCompatibleWorkerAlgorithm,
    ]:
        """Create a worker-side algorithm."""
        ...


@runtime_checkable
class _InferenceAndCSVReportCompatibleModelAlgoFactory(
    _InferenceAndCSVReportCompatibleAlgoFactory,
    BaseCompatibleAlgoFactoryWorkerHubNeeded[
        Union[
            _InferenceAndCSVReportModelIncompatibleWorkerAlgorithm,
            _InferenceAndCSVReportModelCompatibleWorkerAlgorithm,
        ]
    ],
    Protocol,
):
    """Defines algo factory compatibility."""

    model: Union[DistributedModelProtocol, BitfountModelReference]
    pretrained_file: Optional[Union[str, os.PathLike]] = None

    def worker(
        self, *, hub: BitfountHub, **kwargs: Any
    ) -> Union[
        _InferenceAndCSVReportModelIncompatibleWorkerAlgorithm,
        _InferenceAndCSVReportModelCompatibleWorkerAlgorithm,
    ]:
        """Create a worker-side algorithm."""
        ...


class InferenceAndCSVReport(BaseProtocolFactory):
    """Protocol for running a model inference generating a csv report."""

    def __init__(
        self,
        *,
        algorithm: Sequence[
            Union[
                _InferenceAndCSVReportCompatibleAlgoFactory_,
                _InferenceAndCSVReportCompatibleModelAlgoFactory,
                _InferenceAndCSVReportCompatibleHuggingFaceAlgoFactory,
            ]
        ],
        **kwargs: Any,
    ) -> None:
        super().__init__(algorithm=algorithm, **kwargs)

    @classmethod
    def _validate_algorithm(cls, algorithm: BaseCompatibleAlgoFactory) -> None:
        """Validates the algorithm."""
        if algorithm.class_name not in (
            "bitfount.ModelInference",
            "bitfount.HuggingFaceImageClassificationInference",
            "bitfount.HuggingFaceImageSegmentationInference",
            "bitfount.HuggingFaceTextClassificationInference",
            "bitfount.HuggingFaceTextGenerationInference",
            "bitfount.HuggingFacePerplexityEvaluation",
            "bitfount.CSVReportAlgorithm",
            "bitfount.TIMMInference",
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
                    _InferenceAndCSVReportCompatibleAlgoFactory_,
                    _InferenceAndCSVReportCompatibleModelAlgoFactory,
                    _InferenceAndCSVReportCompatibleHuggingFaceAlgoFactory,
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
        """Returns worker side of the InferenceAndCSVReport protocol.

        Args:
            mailbox: Worker mailbox instance to allow communication to the modeller.
            hub: `BitfountHub` object to use for communication with the hub.
            context: Optional. Run-time protocol context details for running.
            **kwargs: Additional keyword arguments.
        """
        algorithms = cast(
            Sequence[
                Union[
                    _InferenceAndCSVReportCompatibleAlgoFactory_,
                    _InferenceAndCSVReportCompatibleModelAlgoFactory,
                    _InferenceAndCSVReportCompatibleHuggingFaceAlgoFactory,
                ]
            ],
            self.algorithms,
        )
        return _WorkerSide(
            algorithm=[algo.worker(hub=hub, context=context) for algo in algorithms],
            mailbox=mailbox,
            **kwargs,
        )
