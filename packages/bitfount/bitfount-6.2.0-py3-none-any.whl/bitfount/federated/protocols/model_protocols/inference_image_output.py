"""Protocol for combining a single model inference and a image output algorithm."""

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
class _InferenceAndImageOutputCompatibleModellerAlgorithm(
    BaseCompatibleModellerAlgorithm, Protocol
):
    """Defines modeller-side algorithm compatibility."""

    def run(self, results: Mapping[str, Any]) -> _StrAnyDict:
        """Runs the modeller-side algorithm."""
        ...


@runtime_checkable
class _InferenceAndImageOutputCompatibleWorkerAlgorithm(
    BaseCompatibleWorkerAlgorithm, Protocol
):
    """Defines worker-side algorithm compatibility."""

    pass


@runtime_checkable
class _InferenceAndImageOutputModelIncompatibleWorkerAlgorithm(
    _InferenceAndImageOutputCompatibleWorkerAlgorithm, Protocol
):
    """Defines worker-side algorithm compatibility without model params."""

    def run(self, *, return_data_keys: bool = False, final_batch: bool = False) -> Any:
        """Runs the worker-side algorithm."""
        ...


@runtime_checkable
class _InferenceAndImageOutputModelCompatibleWorkerAlgorithm(
    _InferenceAndImageOutputCompatibleWorkerAlgorithm, Protocol
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
class _InferenceAndImageOutputBscanCompatibleWorkerAlgorithm(
    _InferenceAndImageOutputCompatibleWorkerAlgorithm, Protocol
):
    """Defines worker-side algorithm compatibility for image output algorithm."""

    def run(
        self,
        results_df: Union[pd.DataFrame, list[pd.DataFrame]],
        filenames: list[str],
        task_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Runs the worker-side algorithm."""
        ...


class _ModellerSide(BaseModellerProtocol):
    """Modeller side of the protocol.

    Args:
        algorithm: A list of algorithms to be run by the protocol. This should be
            a list of two algorithms, the first being the model inference algorithm
            and the second being the image output report algorithm.
        mailbox: The mailbox to use for communication with the Workers.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[_InferenceAndImageOutputCompatibleModellerAlgorithm]

    def __init__(
        self,
        *,
        algorithm: Sequence[_InferenceAndImageOutputCompatibleModellerAlgorithm],
        mailbox: _ModellerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

    async def run(
        self,
        *,
        context: Optional[ProtocolContext] = None,
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
        return results


class _WorkerSide(BaseWorkerProtocol, ModelInferenceProtocolMixin):
    """Worker side of the protocol.

    Args:
        algorithm: A list of algorithms to be run by the protocol. This should be
            a list of two algorithms, the first being the model inference algorithm
            and the second being the BscanImageAndMaskGenerationAlgorithm.
        mailbox: The mailbox to use for communication with the Modeller.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[
        Union[
            _InferenceAndImageOutputModelCompatibleWorkerAlgorithm,
            _InferenceAndImageOutputModelIncompatibleWorkerAlgorithm,
            _InferenceAndImageOutputBscanCompatibleWorkerAlgorithm,
        ]
    ]

    def __init__(
        self,
        *,
        algorithm: Sequence[
            Union[
                _InferenceAndImageOutputModelCompatibleWorkerAlgorithm,
                _InferenceAndImageOutputModelIncompatibleWorkerAlgorithm,
                _InferenceAndImageOutputBscanCompatibleWorkerAlgorithm,
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
            final_batch: If this run of the protocol represents the final run within
                a task.
            **kwargs: Additional keyword arguments.

        Returns:
            2-tuple of the results from the run and an optional 3-tuple regarding
            usage limits being exceeded and so the task should be aborted:
            information on how the limits were exceeded, the limits information in
            question, and the model inference algorithm where the limits were exceeded.
        """
        # Update vitals if available
        if pod_vitals:
            pod_vitals.last_task_execution_time = time.time()

        # Run model inference
        model_predictions_df = self._run_model_inference(final_batch)

        # Extract filenames
        filenames = self._extract_filenames(model_predictions_df)

        # Check limits and adjust predictions if needed
        limits_exceeded_tuple, model_predictions_df = self._check_and_apply_limits(
            model_predictions_df, context
        )

        # Run image output algorithm
        self._run_image_output(model_predictions_df, filenames)

        # Send results to modeller
        await self._send_evaluation_results(limits_exceeded_tuple)

        return model_predictions_df, limits_exceeded_tuple

    def _run_model_inference(self, final_batch: bool) -> pd.DataFrame:
        """Run the model inference algorithm and process the results.

        Args:
            final_batch: If this run represents the final batch.

        Returns:
            DataFrame containing the model predictions.

        Raises:
            TypeError: If the algorithm type is invalid or if
                predictions format is unsupported.
        """
        # Unpack algorithms
        model_inference_algo, _ = self.algorithm

        # Run Inference Algorithm
        logger.info("Running model inference algorithm")
        if isinstance(model_inference_algo, _BaseWorkerModelAlgorithm):
            model_predictions = model_inference_algo.run(
                return_data_keys=True, final_batch=final_batch
            )
        else:
            if isinstance(
                model_inference_algo,
                _InferenceAndImageOutputBscanCompatibleWorkerAlgorithm,
            ):
                raise TypeError(
                    "Invalid algorithm type: BscanCompatibleWorkerAlgorithm "
                    "cannot be used as a model inference algorithm"
                )
            model_inference_algo = cast(
                _InferenceAndImageOutputModelIncompatibleWorkerAlgorithm,
                model_inference_algo,
            )
            model_predictions = model_inference_algo.run(
                return_data_keys=True, final_batch=final_batch
            )

        # Convert to DataFrame
        return self._convert_predictions_to_dataframe(model_predictions)

    def _convert_predictions_to_dataframe(
        self, model_predictions: Union[PredictReturnType, pd.DataFrame]
    ) -> pd.DataFrame:
        """Convert model predictions to a DataFrame format.

        Args:
            model_predictions: The model prediction output.

        Returns:
            DataFrame with predictions.

        Raises:
            TypeError: If predictions format is not supported.
        """
        if isinstance(model_predictions, PredictReturnType):
            if isinstance(model_predictions.preds, pd.DataFrame):
                model_predictions_df = model_predictions.preds
            else:
                raise TypeError(
                    f"Model prediction must return a Dataframe"
                    f" to enable image and mask output;"
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

        return model_predictions_df

    def _extract_filenames(self, model_predictions_df: pd.DataFrame) -> list[str]:
        """Extract filenames from the predictions DataFrame.

        Args:
            model_predictions_df: DataFrame containing predictions.

        Returns:
            List of filenames.

        Raises:
            ValueError: If filenames cannot be found in the DataFrame.
        """
        try:
            return model_predictions_df[ORIGINAL_FILENAME_METADATA_COLUMN].tolist()
        except KeyError as ke:
            logger.critical(
                "Unable to find data keys/filenames in predictions dataframe;"
                " unable to continue"
            )
            raise ValueError(
                "Unable to find data keys/filenames in predictions dataframe;"
                " unable to continue"
            ) from ke

    def _check_and_apply_limits(
        self, model_predictions_df: pd.DataFrame, context: Optional[ProtocolContext]
    ) -> tuple[
        Optional[
            tuple[LimitsExceededInfo, dict[str, InferenceLimits], _InferenceWorkerSide]
        ],
        pd.DataFrame,
    ]:
        """Check inference limits and apply them if needed.

        Args:
            model_predictions_df: DataFrame containing predictions.
            context: Protocol context containing limits information.

        Returns:
            Optional tuple with limits exceeded information if applicable.
        """
        model_inference_algo, _ = self.algorithm
        limits_exceeded_info: Optional[LimitsExceededInfo] = None
        limits: Optional[dict[str, InferenceLimits]] = (
            context.inference_limits if context is not None else None
        )

        if isinstance(model_inference_algo, _InferenceWorkerSide) and limits:
            limits_exceeded_info = self.check_usage_limits(limits, model_inference_algo)

            # If limits were exceeded, reduce the predictions dataframe
            if limits_exceeded_info:
                model_id: str = cast(
                    str, model_inference_algo.maybe_bitfount_model_slug
                )
                logger.warning(
                    f"Usage limits for {model_id} "
                    f"exceeded by {limits_exceeded_info.overrun} inferences;"
                    f" limiting to {limits_exceeded_info.allowed} prediction results."
                )

                return (
                    limits_exceeded_info,
                    limits,
                    model_inference_algo,
                ), model_predictions_df.iloc[: limits_exceeded_info.allowed]

        return None, model_predictions_df

    def _run_image_output(
        self, model_predictions_df: pd.DataFrame, filenames: list[str]
    ) -> None:
        """Run the image output algorithm.

        Args:
            model_predictions_df: DataFrame with model predictions.
            filenames: List of filenames to process.
        """
        _, image_output_algo = self.algorithm

        # Run BscanImageAndMaskGenerationAlgorithm
        logger.info("Running Image output algorithm")
        image_output_algo = cast(
            _InferenceAndImageOutputBscanCompatibleWorkerAlgorithm, image_output_algo
        )
        image_output_algo.run(
            results_df=model_predictions_df,
            filenames=filenames,
            task_id=self.mailbox._task_id,
        )

    async def _send_evaluation_results(
        self,
        limits_exceeded_tuple: Optional[
            tuple[LimitsExceededInfo, dict[str, InferenceLimits], _InferenceWorkerSide]
        ],
    ) -> None:
        """Send evaluation results to the modeller.

        Args:
            limits_exceeded_tuple: Optional tuple with limits exceeded information.
        """
        model_inference_algo, _ = self.algorithm

        # Apply limits to the resources consumed information
        resources_consumed: Optional[list[ResourceConsumed]] = None
        if isinstance(model_inference_algo, _InferenceWorkerSide):
            limits_exceeded_info = (
                limits_exceeded_tuple[0] if limits_exceeded_tuple else None
            )
            resources_consumed = self.apply_actual_usage_to_resources_consumed(
                model_inference_algo,
                limits_exceeded_info,
            )

        await self.mailbox.send_evaluation_results(
            resources_consumed=resources_consumed,
        )


@runtime_checkable
class _InferenceAndImageOutputCompatibleAlgoFactory(Protocol):
    """Defines algo factory compatibility."""

    def modeller(
        self, **kwargs: Any
    ) -> _InferenceAndImageOutputCompatibleModellerAlgorithm:
        """Create a modeller-side algorithm."""
        ...


@runtime_checkable
class _InferenceAndImageOutputCompatibleAlgoFactory_(
    _InferenceAndImageOutputCompatibleAlgoFactory,
    BaseCompatibleAlgoFactoryWorkerStandard[
        Union[
            _InferenceAndImageOutputModelIncompatibleWorkerAlgorithm,
            _InferenceAndImageOutputModelCompatibleWorkerAlgorithm,
            _InferenceAndImageOutputBscanCompatibleWorkerAlgorithm,
        ]
    ],
    Protocol,
):
    """Defines algo factory compatibility."""

    def worker(
        self, **kwargs: Any
    ) -> Union[
        _InferenceAndImageOutputModelIncompatibleWorkerAlgorithm,
        _InferenceAndImageOutputModelCompatibleWorkerAlgorithm,
        _InferenceAndImageOutputBscanCompatibleWorkerAlgorithm,
    ]:
        """Create a worker-side algorithm."""
        ...


@runtime_checkable
class _InferenceAndImageOutputCompatibleHuggingFaceAlgoFactory(
    _InferenceAndImageOutputCompatibleAlgoFactory,
    BaseCompatibleAlgoFactoryWorkerHubNeeded[
        Union[
            _InferenceAndImageOutputModelIncompatibleWorkerAlgorithm,
            _InferenceAndImageOutputModelCompatibleWorkerAlgorithm,
            _InferenceAndImageOutputBscanCompatibleWorkerAlgorithm,
        ]
    ],
    Protocol,
):
    """Defines algo factory compatibility."""

    model_id: str

    def worker(
        self, *, hub: BitfountHub, **kwargs: Any
    ) -> Union[
        _InferenceAndImageOutputModelIncompatibleWorkerAlgorithm,
        _InferenceAndImageOutputModelCompatibleWorkerAlgorithm,
        _InferenceAndImageOutputBscanCompatibleWorkerAlgorithm,
    ]:
        """Create a worker-side algorithm."""
        ...


@runtime_checkable
class _InferenceAndImageOutputCompatibleModelAlgoFactory(
    _InferenceAndImageOutputCompatibleAlgoFactory,
    BaseCompatibleAlgoFactoryWorkerHubNeeded[
        Union[
            _InferenceAndImageOutputModelIncompatibleWorkerAlgorithm,
            _InferenceAndImageOutputModelCompatibleWorkerAlgorithm,
            _InferenceAndImageOutputBscanCompatibleWorkerAlgorithm,
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
        _InferenceAndImageOutputModelIncompatibleWorkerAlgorithm,
        _InferenceAndImageOutputModelCompatibleWorkerAlgorithm,
        _InferenceAndImageOutputBscanCompatibleWorkerAlgorithm,
    ]:
        """Create a worker-side algorithm."""
        ...


class InferenceAndImageOutput(BaseProtocolFactory):
    """Protocol for running a model inference generating image outputs with masks."""

    def __init__(
        self,
        *,
        algorithm: Sequence[
            Union[
                _InferenceAndImageOutputCompatibleAlgoFactory_,
                _InferenceAndImageOutputCompatibleModelAlgoFactory,
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
            "bitfount.BscanImageAndMaskGenerationAlgorithm",
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
                    _InferenceAndImageOutputCompatibleAlgoFactory_,
                    _InferenceAndImageOutputCompatibleModelAlgoFactory,
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
        """Returns worker side of the InferenceAndImageOutput protocol.

        Args:
            mailbox: Worker mailbox instance to allow communication to the modeller.
            hub: `BitfountHub` object to use for communication with the hub.
            context: Optional. Run-time protocol context details for running.
            **kwargs: Additional keyword arguments.
        """
        algorithms = cast(
            Sequence[
                Union[
                    _InferenceAndImageOutputCompatibleAlgoFactory_,
                    _InferenceAndImageOutputCompatibleModelAlgoFactory,
                ]
            ],
            self.algorithms,
        )
        return _WorkerSide(
            algorithm=[algo.worker(hub=hub, context=context) for algo in algorithms],
            mailbox=mailbox,
            **kwargs,
        )
