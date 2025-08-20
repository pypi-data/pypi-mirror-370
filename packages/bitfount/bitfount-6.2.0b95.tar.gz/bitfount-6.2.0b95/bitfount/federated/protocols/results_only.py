"""Results Only protocol."""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
import os
from pathlib import Path
import time
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Final,
    Optional,
    Protocol,
    Union,
    cast,
    runtime_checkable,
)

from marshmallow import fields
import pandas as pd

from bitfount import config
from bitfount.federated.aggregators.base import (
    _AggregatorWorkerFactory,
    _BaseAggregatorFactory,
    _BaseModellerAggregator,
    _BaseWorkerAggregator,
    registry as aggregators_registry,
)
from bitfount.federated.aggregators.secure import _InterPodAggregatorWorkerFactory
from bitfount.federated.algorithms.base import registry as algorithms_registry
from bitfount.federated.algorithms.model_algorithms.inference import (
    _WorkerSide as _InferenceWorkerSide,
)
from bitfount.federated.authorisation_checkers import InferenceLimits, ProtocolContext
from bitfount.federated.helper import _create_aggregator
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.model_reference import BitfountModelReference
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
    _InterPodWorkerMailbox,
    _WorkerMailbox,
)
from bitfount.types import (
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    DistributedModelProtocol,
    _StrAnyDict,
)
from bitfount.utils import delegates

if TYPE_CHECKING:
    from bitfount.federated.pod_vitals import _PodVitals
    from bitfount.hub.api import BitfountHub

logger = _get_federated_logger(__name__)

DEFAULT_CSV_FILENAME: Final[str] = "results.csv"


class SaveLocation(Enum):
    """Enum for the location to save the results to."""

    Worker = "Worker"
    Modeller = "Modeller"


def _save_results_to_csv(df: pd.DataFrame, save_path: Path) -> None:
    """Saves dataframe to CSV."""
    try:
        logger.info(f"Saving results to {save_path}")
        df.to_csv(save_path, index=False)
    except Exception as e:
        logger.error(f"Error saving results to CSV: {e}")
        # We don't want to raise an error here as


def _save_results(results: Any, save_path: Path) -> None:
    """Saves dataframe results to either modeller side or pode side.

    Currently this only handles saving dataframes to CSV.
    """
    if isinstance(results, pd.DataFrame):
        _save_results_to_csv(results, save_path)
    # Dictionary of pod names to actual results
    elif isinstance(results, dict):
        for result in results.values():
            _save_results(result, save_path)
    else:
        logger.warning("Result could not be saved to CSV as it was not a dataframe.")


@runtime_checkable
class _ResultsOnlyCompatibleModellerAlgorithm(
    BaseCompatibleModellerAlgorithm, Protocol
):
    """Defines modeller-side algorithm compatibility."""

    def run(self, results: Mapping[str, Any]) -> _StrAnyDict:
        """Runs the modeller-side algorithm."""
        ...


@runtime_checkable
class _ResultsOnlyCompatibleWorkerAlgorithm(BaseCompatibleWorkerAlgorithm, Protocol):
    """Defines worker-side algorithm compatibility."""

    def run(self, *, final_batch: bool = False) -> Any:
        """Runs the worker-side algorithm."""
        ...


class _ModellerSide(BaseModellerProtocol):
    """Modeller side of the ResultsOnly protocol."""

    algorithm: _ResultsOnlyCompatibleModellerAlgorithm
    aggregator: Optional[_BaseModellerAggregator]

    def __init__(
        self,
        *,
        algorithm: _ResultsOnlyCompatibleModellerAlgorithm,
        aggregator: Optional[_BaseModellerAggregator],
        mailbox: _ModellerMailbox,
        save_location: list[SaveLocation],
        save_path: Path,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)
        self.aggregator = aggregator
        self.save_location = save_location
        self.save_path = save_path

    async def run(
        self, *, context: Optional[ProtocolContext] = None, **kwargs: Any
    ) -> Union[list[Any], Any]:
        """Runs Modeller side of the protocol.

        Args:
            context: Optional. Run-time context for the protocol.
            **kwargs: Additional keyword arguments.
        """
        eval_results = await self.mailbox.get_evaluation_results_from_workers()
        logger.info("Results received from Pods.")

        modeller_results: Any
        modeller_results = self.algorithm.run(eval_results)

        if self.aggregator:
            modeller_results = self.aggregator.run(modeller_results)

        if SaveLocation.Modeller in self.save_location:
            _save_results(modeller_results, self.save_path)

        return modeller_results


class _WorkerSide(BaseWorkerProtocol, ModelInferenceProtocolMixin, FinalStepProtocol):
    """Worker side of the ResultsOnly protocol."""

    algorithm: _ResultsOnlyCompatibleWorkerAlgorithm
    aggregator: Optional[_BaseWorkerAggregator]

    def __init__(
        self,
        *,
        algorithm: _ResultsOnlyCompatibleWorkerAlgorithm,
        aggregator: Optional[_BaseWorkerAggregator],
        mailbox: _WorkerMailbox,
        save_location: list[SaveLocation],
        save_path: Path,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)
        self.aggregator = aggregator
        self.save_location = save_location
        self.save_path = save_path

    async def run(
        self,
        *,
        pod_vitals: Optional[_PodVitals] = None,
        context: Optional[ProtocolContext] = None,
        final_batch: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Runs Worker side of the protocol.

        Args:
            pod_vitals: Optional. Pod vitals instance for recording run-time details
                from the protocol run.
            context: Optional. Run-time context for the protocol.
            final_batch: If this run of the protocol represents the final run within
                a task.
            **kwargs: Additional keyword arguments.
        """
        if pod_vitals:
            pod_vitals.last_task_execution_time = time.time()

        results = self.algorithm.run(final_batch=final_batch)

        # Calculate resource usage from the previous inference step
        limits_exceeded_info: Optional[LimitsExceededInfo] = None
        limits: Optional[dict[str, InferenceLimits]] = (
            context.inference_limits if context is not None else None
        )
        if isinstance(self.algorithm, _InferenceWorkerSide):
            if limits:
                limits_exceeded_info = self.check_usage_limits(limits, self.algorithm)

            # If limits were exceeded, reduce the predictions dataframe and proceed as
            # though this were the last batch
            if limits_exceeded_info:
                # model_id cannot be None as the only way the limits can be
                # calculated/exceeded is if the algo has a slug associated with it
                model_id: str = cast(str, self.algorithm.maybe_bitfount_model_slug)
                logger.warning(
                    f"Usage limits for {model_id}"
                    f"exceeded by {limits_exceeded_info.overrun} inferences;"
                    f" limiting to {limits_exceeded_info.allowed} prediction results."
                )
                # Reduce predictions to the number that does _not_ exceed the limit
                results = cast(pd.DataFrame, results)  # as is _InferenceWorkerSide
                results = results.iloc[: limits_exceeded_info.allowed]
                final_batch = True

        if self.aggregator:
            logger.debug("Aggregating results...")
            results = await self.aggregator.run(results)
            logger.debug("Aggregation complete.")

        # Apply limits to the resources consumed information
        resources_consumed: Optional[list[ResourceConsumed]] = None
        if isinstance(self.algorithm, _InferenceWorkerSide):
            resources_consumed = self.apply_actual_usage_to_resources_consumed(
                self.algorithm,
                limits_exceeded_info,
            )

        if hasattr(results, "msgpack_serialize"):
            await self.mailbox.send_evaluation_results(
                eval_results=results.msgpack_serialize(),
                resources_consumed=resources_consumed,
            )
        else:
            await self.mailbox.send_evaluation_results(
                eval_results=results,
                resources_consumed=resources_consumed,
            )

        if SaveLocation.Worker in self.save_location:
            _save_results(results, self.save_path)

        # Check if limits were exceeded and so we should abort any remaining protocol
        # batches
        if limits_exceeded_info:
            # limits_exceeded_info is not None if and only if limits is not None
            assert limits is not None  # nosec[assert_used]

            # limits_exceeded_info is only not None when we are looking at a
            # _InferenceWorkerSide algorithm instance
            await self.handle_limits_exceeded(
                cast(_InferenceWorkerSide, self.algorithm),
                limits_exceeded_info,
                limits,
                self.mailbox,
            )
        else:
            return results


@runtime_checkable
class _ResultsOnlyCompatibleAlgoFactory(Protocol):
    """Defines algo factory compatibility."""

    def modeller(self, **kwargs: Any) -> _ResultsOnlyCompatibleModellerAlgorithm:
        """Create a modeller-side algorithm."""
        ...


@runtime_checkable
class _ResultsOnlyCompatibleNonModelAlgoFactory(
    _ResultsOnlyCompatibleAlgoFactory,
    BaseCompatibleAlgoFactoryWorkerStandard[_ResultsOnlyCompatibleWorkerAlgorithm],
    Protocol,
):
    """Defines algo factory compatibility."""

    def worker(self, **kwargs: Any) -> _ResultsOnlyCompatibleWorkerAlgorithm:
        """Create a worker-side algorithm."""
        ...


@runtime_checkable
class _ResultsOnlyCompatibleModelAlgoFactory(
    _ResultsOnlyCompatibleAlgoFactory,
    BaseCompatibleAlgoFactoryWorkerHubNeeded[_ResultsOnlyCompatibleWorkerAlgorithm],
    Protocol,
):
    """Defines algo factory compatibility."""

    model: Union[DistributedModelProtocol, BitfountModelReference]
    pretrained_file: Optional[Union[str, os.PathLike]] = None

    def worker(
        self, *, hub: BitfountHub, **kwargs: Any
    ) -> _ResultsOnlyCompatibleWorkerAlgorithm:
        """Create a worker-side algorithm."""
        ...


@delegates()
class ResultsOnly(BaseProtocolFactory):
    """Simply returns the results from the provided algorithm.

    This protocol is the most permissive protocol and only involves one round of
    communication. It simply runs the algorithm on the `Pod`(s) and returns the
    results as a list (one element for every pod) unless an aggregator is specified.

    Args:
        algorithm: The algorithm to run.
        aggregator: The aggregator to use for updating the algorithm results across all
            Pods participating in the task.  This argument takes priority over the
            `secure_aggregation` argument.
        secure_aggregation: Whether to use secure aggregation. This argument is
            overridden by the `aggregator` argument.

    Attributes:
        name: The name of the protocol.
        algorithm: The algorithm to run. This must be compatible with the `ResultsOnly`
            protocol.
        aggregator: The aggregator to use for updating the algorithm results.

    Raises:
        TypeError: If the `algorithm` is not compatible with the protocol.
    """

    # TODO: [BIT-1047] Consider separating this protocol into two separate protocols
    # for each algorithm. The algorithms may not be similar enough to benefit
    # from sharing one protocol.

    algorithm: Union[
        _ResultsOnlyCompatibleNonModelAlgoFactory,
        _ResultsOnlyCompatibleModelAlgoFactory,
    ]
    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "secure_aggregation": fields.Boolean(default=False),
        "save_location": fields.List(fields.Enum(SaveLocation)),
        "save_path": fields.String(allow_none=True),
    }
    nested_fields: ClassVar[T_NESTED_FIELDS] = {
        "algorithm": algorithms_registry,
        "aggregator": aggregators_registry,
    }

    def __init__(
        self,
        *,
        algorithm: Union[
            _ResultsOnlyCompatibleNonModelAlgoFactory,
            _ResultsOnlyCompatibleModelAlgoFactory,
        ],
        aggregator: Optional[_BaseAggregatorFactory] = None,
        secure_aggregation: bool = False,
        save_location: Optional[list[SaveLocation]] = None,
        save_path: Optional[Union[str, os.PathLike]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(algorithm=algorithm, **kwargs)
        self.aggregator: Optional[_BaseAggregatorFactory] = None
        self.save_location = (
            save_location if save_location is not None else [SaveLocation.Modeller]
        )
        self.save_path: Path
        if save_path is None:
            self.save_path = config.settings.paths.output_dir
        else:
            self.save_path = Path(save_path).expanduser().absolute().resolve()

        if self.save_path.suffix != ".csv":
            # Create the output directory if it doesn't exist
            self.save_path.mkdir(parents=True, exist_ok=True)
            # If save_path is not a CSV file, then add the default CSV filename
            self.save_path = self.save_path / DEFAULT_CSV_FILENAME
        else:
            # Create the output directory if it doesn't exist
            self.save_path.parent.mkdir(parents=True, exist_ok=True)

        if aggregator:
            self.aggregator = aggregator
        elif secure_aggregation:
            self.aggregator = _create_aggregator(secure_aggregation=secure_aggregation)
        else:
            logger.info("No aggregator specified. Will return a dictionary of results.")

    @classmethod
    def _validate_algorithm(
        cls,
        algorithm: BaseCompatibleAlgoFactory,
    ) -> None:
        """Checks that `algorithm` is compatible with the protocol."""
        if not isinstance(
            algorithm,
            (
                _ResultsOnlyCompatibleNonModelAlgoFactory,
                _ResultsOnlyCompatibleModelAlgoFactory,
            ),
        ):
            raise TypeError(
                f"The {cls.__name__} protocol does not support "
                + f"the {type(algorithm).__name__} algorithm.",
            )

    def modeller(self, mailbox: _ModellerMailbox, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the ResultsOnly protocol."""
        if isinstance(self.algorithm, _ResultsOnlyCompatibleModelAlgoFactory):
            algorithm = self.algorithm.modeller(
                pretrained_file=self.algorithm.pretrained_file
            )
        else:
            algorithm = self.algorithm.modeller()
        return _ModellerSide(
            algorithm=algorithm,
            aggregator=self.aggregator.modeller() if self.aggregator else None,
            mailbox=mailbox,
            save_location=self.save_location,
            save_path=self.save_path,
            **kwargs,
        )

    def worker(
        self,
        mailbox: _WorkerMailbox,
        hub: BitfountHub,
        context: Optional[ProtocolContext] = None,
        **kwargs: Any,
    ) -> _WorkerSide:
        """Returns the worker side of the ResultsOnly protocol.

        Args:
            mailbox: Worker mailbox instance to allow communication to the modeller.
            hub: `BitfountHub` object to use for communication with the hub.
            context: Optional. Run-time protocol context details for running.
            **kwargs: Additional keyword arguments.

        Raises:
            TypeError: If the mailbox is not compatible with the aggregator.
        """
        worker_agg: Optional[_BaseWorkerAggregator] = None
        if self.aggregator is not None:
            if isinstance(self.aggregator, _AggregatorWorkerFactory):
                worker_agg = self.aggregator.worker()
            elif isinstance(self.aggregator, _InterPodAggregatorWorkerFactory):
                if not isinstance(mailbox, _InterPodWorkerMailbox):
                    raise TypeError(
                        "Inter-pod aggregators require an inter-pod worker mailbox."
                    )
                worker_agg = self.aggregator.worker(mailbox=mailbox)
            else:
                raise TypeError(
                    f"Unrecognised aggregator factory ({type(self.aggregator)}); "
                    f"unable to determine how to call .worker() factory method."
                )

        return _WorkerSide(
            algorithm=self.algorithm.worker(hub=hub, context=context),
            aggregator=worker_agg,
            mailbox=mailbox,
            save_location=self.save_location,
            save_path=self.save_path,
            **kwargs,
        )
