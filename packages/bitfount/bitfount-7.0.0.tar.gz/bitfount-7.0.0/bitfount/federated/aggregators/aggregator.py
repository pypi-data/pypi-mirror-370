"""Vanilla model parameter aggregators for Federated Averaging."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import logging
from typing import Any, ClassVar, Optional, Union, cast, overload

import numpy as np
import pandas as pd

from bitfount.federated.aggregators.base import (
    AggregationType,
    _AggregatorWorkerFactory,
    _BaseAggregatorFactory,
    _BaseModellerAggregator,
    _BaseWorkerAggregator,
)
from bitfount.federated.exceptions import AggregatorError
from bitfount.federated.shim import BackendTensorShim, _load_default_tensor_shim
from bitfount.types import (
    T_DTYPE,
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    _SerializedWeights,
    _Weights,
)
from bitfount.utils import delegates

logger = logging.getLogger(__name__)


class _ModellerSide(_BaseModellerAggregator[T_DTYPE]):
    """Modeller-side of the vanilla aggregator."""

    def __init__(
        self,
        *,
        tensor_shim: BackendTensorShim,
        weights: Optional[Mapping[str, Union[float, int]]] = None,
        **kwargs: Any,
    ):
        """Create a new modeller-side instance of the vanilla aggregator.

        Args:
            tensor_shim: A shim providing methods to convert to/from
                tensor-like objects.
            weights: A mapping of pod identifiers to the desired weighting to give
                them in the averaging. If not supplied, all will be equally weighted.
                Weights will be normalised so that they sum to 1.0.
            **kwargs: Other keyword arguments.
        """
        super().__init__(tensor_shim=tensor_shim, **kwargs)
        self._weights: Optional[Mapping[str, float]] = self._normalise_weights(weights)

    @property
    def weights(self) -> Optional[Mapping[str, float]]:
        """The per-pod update weightings (for weighted average) for this aggregator.

        This attribute is a dictionary of pod identifiers to weights or `None` if no
        weights were specified.

        :::note

        This does not refer to the weights (parameters) of the model, but rather the
        weights to apply to the parameters of the model when performing a weighted
        average.

        :::
        """
        if self._weights:
            return dict(self._weights)
        else:
            return None

    @staticmethod
    def _normalise_weights(
        weights: Optional[Mapping[str, Union[float, int]]],
    ) -> Optional[Mapping[str, float]]:
        """Normalises the supplied weights to sum to 1.0.

        If no weights supplied, returns None.

        :::note

        This does not refer to the weights (parameters) of the model, but rather the
        weights to apply to the parameters of the model when performing a weighted
        average.

        :::
        """
        if not weights:
            return None

        weight_sum = sum(weights.values())
        return {pod_id: weight / weight_sum for pod_id, weight in weights.items()}

    def _validate_algorithm_outputs(
        self, algorithm_outputs: Iterable[Any], output_type: AggregationType
    ) -> None:
        """Validate the algorithm outputs.

        :::note

        This is used to validate that the algorithm outputs are of the rights type and
        are consistent between workers.

        :::
        """
        if output_type == AggregationType.UNSUPPORTED:
            raise AggregatorError(
                "Algorithm outputs are not recognised. Currently only pandas "
                "dataframes, numpy arrays and tensor state dictionaries are supported."
            )

        if output_type == AggregationType.TENSOR_DICT:
            algorithm_outputs = cast(Iterable[_SerializedWeights], algorithm_outputs)
            algo_outputs_iter = iter(algorithm_outputs)
            first = next(algo_outputs_iter)
            keys = first.keys()

            # Check that these are the same in all others
            if not all(keys == other.keys() for other in algo_outputs_iter):
                raise AggregatorError(
                    f"Keys are not consistent between workers: "
                    f"all names should match {sorted(set(keys))}"
                )

        elif output_type == AggregationType.PANDAS_DATAFRAME:
            # Check if all dataframes have the same columns and shapes
            # Also check if non-numeric columns are the same across all dataframes
            if len(set(i.shape for i in algorithm_outputs)) != 1:
                raise AggregatorError(
                    "Algorithm outputs are not consistent between workers: "
                    "all dataframes should have the same shape."
                )

            if len(set(tuple(i.columns) for i in algorithm_outputs)) != 1:
                raise AggregatorError(
                    "Algorithm outputs are not consistent between workers: "
                    "all dataframes should have the same columns."
                )

            self._set_non_numeric_columns(algorithm_outputs)

        elif output_type == AggregationType.NUMPY_ARRAY:
            if len(set(i.shape for i in algorithm_outputs)) != 1:
                raise AggregatorError(
                    "Algorithm outputs are not consistent between workers: "
                    "all arrays should have the same shape."
                )

            for output in algorithm_outputs:
                output = cast(np.ndarray, output)
                if not np.issubdtype(output.dtype, np.number):
                    raise AggregatorError(
                        f"Numpy array dtype {output.dtype} is not a number type."
                    )

    @overload
    def run(
        self,
        algorithm_outputs: Mapping[str, _SerializedWeights],
        tensor_dtype: Optional[T_DTYPE] = None,
        **kwargs: Any,
    ) -> _Weights:
        """Averages tensor dictionaries and returns the average."""
        ...

    @overload
    def run(
        self,
        algorithm_outputs: Mapping[str, pd.DataFrame],
        tensor_dtype: Optional[T_DTYPE] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Averages pandas dataframes and returns the average."""
        ...

    @overload
    def run(
        self,
        algorithm_outputs: Mapping[str, np.ndarray],
        tensor_dtype: Optional[T_DTYPE] = None,
        **kwargs: Any,
    ) -> np.ndarray:
        """Averages numpy arrays and returns the average."""
        ...

    def run(
        self,
        algorithm_outputs: Union[
            Mapping[str, _SerializedWeights],
            Mapping[str, np.ndarray],
            Mapping[str, pd.DataFrame],
        ],
        tensor_dtype: Optional[T_DTYPE] = None,
        **kwargs: Any,
    ) -> Union[_Weights, np.ndarray, pd.DataFrame]:
        """Averages algorithm outputs and returns them.

        Args:
            algorithm_outputs: A mapping of pod names to their algorithm outputs.
            tensor_dtype: The dtype to use when converting parameter updates to tensors.
            **kwargs: Other keyword arguments.

        Raises:
            AggregatorError: If there is any issue whereby aggregation cannot proceed.
                Details will be included in the error message.
        """
        obj_type = self._get_type(algorithm_outputs.values())
        self._validate_algorithm_outputs(algorithm_outputs.values(), obj_type)
        # Use provided weights or, if none provided, use equal weights.
        weights = self._get_weights(algorithm_outputs)
        averaged_output: Union[pd.DataFrame, np.ndarray, _Weights]

        if obj_type == AggregationType.TENSOR_DICT:
            averaged_output = {}
            algorithm_outputs = cast(
                Mapping[str, _SerializedWeights], algorithm_outputs
            )
            state_dict_param_names = list(algorithm_outputs.values())[0].keys()
            for param_name in state_dict_param_names:
                averaged_output[param_name] = self._tensor_shim.to_tensor(
                    np.stack(
                        [
                            weights[pod_id] * np.asarray(params[param_name])
                            for pod_id, params in algorithm_outputs.items()
                        ],
                        axis=0,
                    ).sum(axis=0),
                    dtype=tensor_dtype,
                )
        elif obj_type == AggregationType.PANDAS_DATAFRAME:
            averaged_output = pd.DataFrame(self.non_numeric_columns)
            algorithm_outputs = cast(Mapping[str, pd.DataFrame], algorithm_outputs)
            df_columns = list(algorithm_outputs.values())[0].columns

            for param_name in df_columns:
                if param_name not in self.non_numeric_columns:
                    averaged_output[param_name] = np.stack(
                        [
                            weights[pod_id] * params[param_name].to_numpy()
                            for pod_id, params in algorithm_outputs.items()
                        ],
                        axis=0,
                    ).sum(axis=0)

        elif obj_type == AggregationType.NUMPY_ARRAY:
            algorithm_outputs = cast(Mapping[str, np.ndarray], algorithm_outputs)
            averaged_output = np.stack(
                [weights[pod_id] * arr for pod_id, arr in algorithm_outputs.items()],
                axis=0,
            ).sum(axis=0)

        return averaged_output

    def _get_weights(self, algorithm_outputs: Mapping[str, Any]) -> Mapping[str, float]:
        """Gets the supplied weights or creates equal weights.

        Will raise appropriate errors if the pods in the supplied weights and
        the pods in the parameter updates don't match.
        """
        weights = self.weights

        if weights is None:
            # Use equal weights
            weights = {
                pod_id: 1 / len(algorithm_outputs)
                for pod_id in algorithm_outputs.keys()
            }
        else:
            # If using provided weights, check we have updates for each pod
            parameter_update_pods = set(algorithm_outputs.keys())
            weights_pods = set(weights.keys())

            extra_in_update = parameter_update_pods.difference(weights_pods)
            missing_in_update = weights_pods.difference(algorithm_outputs)

            if extra_in_update:
                raise AggregatorError(
                    f"Aggregation weightings provided but found updates from "
                    f"unweighted pods in received parameter updates: "
                    f"{';'.join(extra_in_update)}"
                )
            if missing_in_update:
                raise AggregatorError(
                    f"Aggregation weightings provided but missing updates from "
                    f"expected pods in received parameter updates: "
                    f"{';'.join(missing_in_update)}"
                )

        return weights


class _WorkerSide(_BaseWorkerAggregator):
    """Worker-side of the vanilla aggregator."""

    def __init__(self, *, tensor_shim: BackendTensorShim, **kwargs: Any):
        super().__init__(tensor_shim=tensor_shim, **kwargs)

    @overload
    async def run(
        self, algorithm_output: _Weights, **kwargs: Any
    ) -> _SerializedWeights:
        """Converts tensors to list of floats and returns them."""
        ...

    @overload
    async def run(self, algorithm_output: np.ndarray, **kwargs: Any) -> np.ndarray:
        """Doesn't do anything - leaves the type as it is."""
        ...

    @overload
    async def run(self, algorithm_output: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
        """Doesn't do anything - leaves the type as it is."""
        ...

    async def run(
        self, algorithm_output: Union[_Weights, np.ndarray, pd.DataFrame], **kwargs: Any
    ) -> Union[_SerializedWeights, np.ndarray, pd.DataFrame]:
        """Converts input to a serializable format if applicable and returns it.

        Args:
            algorithm_output: The algorithm output to be encoded and sent to the
                modeller.
            **kwargs: Other keyword arguments.

        Raises:
            AggregatorError: If the algorithm output is not a supported type.
        """
        obj_type = self._get_type([algorithm_output])
        aggregator_output: Union[_SerializedWeights, pd.DataFrame, np.ndarray]
        if obj_type == AggregationType.TENSOR_DICT:
            algorithm_output = cast(_Weights, algorithm_output)
            aggregator_output = {
                name: self._tensor_shim.to_list(param)
                for name, param in algorithm_output.items()
            }
        elif obj_type in (
            AggregationType.PANDAS_DATAFRAME,
            AggregationType.NUMPY_ARRAY,
        ):
            # Pandas dataframes and numpy arrays are converted to lists of floats
            # at the transport layer so no need to deal with them here
            algorithm_output = cast(Union[pd.DataFrame, np.ndarray], algorithm_output)
            aggregator_output = algorithm_output
        else:
            raise AggregatorError("Unrecognised type received from algorithm.")

        return aggregator_output


@delegates()
class Aggregator(_BaseAggregatorFactory, _AggregatorWorkerFactory):
    """Vanilla model parameter aggregator for Federated Averaging.

    Performs simple arithmetic mean of unencrypted model parameters.

    :::danger

    This aggregator is not secure. Algorithm outputs are shared with participants in an
    unencrypted manner. It is not recommended to use this aggregator in a zero-trust
    setting.

    :::

    Attributes:
        name: The name of the aggregator.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {}
    nested_fields: ClassVar[T_NESTED_FIELDS] = {}

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._tensor_shim = _load_default_tensor_shim()

    def modeller(self, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the Aggregator."""
        return _ModellerSide(tensor_shim=self._tensor_shim, **kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the Aggregator."""
        return _WorkerSide(tensor_shim=self._tensor_shim, **kwargs)
