"""Secure model parameter aggregators for Federated Averaging."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any, ClassVar, Optional, Union, cast, overload

import numpy as np
import pandas as pd

from bitfount.federated.aggregators.aggregator import (
    _ModellerSide as ModellerSide_,
    _WorkerSide as WorkerSide_,
)
from bitfount.federated.aggregators.base import AggregationType, _BaseAggregatorFactory
from bitfount.federated.exceptions import AggregatorError
from bitfount.federated.secure import SecureShare, _secure_share_registry
from bitfount.federated.shim import BackendTensorShim, _load_default_tensor_shim
from bitfount.federated.task_requests import _TaskRequest
from bitfount.federated.transport.worker_transport import _InterPodWorkerMailbox
from bitfount.federated.types import AggregatorType
from bitfount.types import (
    T_DTYPE,
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    _SerializedWeights,
    _Weights,
)
from bitfount.utils import delegates


class _BaseSecureAggregator:
    """Shared behaviour and attributes for SecureAggregator classes."""

    def __init__(self, *, secure_share: SecureShare, **kwargs: Any):
        self.secure_share = secure_share
        super().__init__(**kwargs)


class _ModellerSide(_BaseSecureAggregator, ModellerSide_):
    """Modeller-side of the secure aggregator."""

    def __init__(
        self,
        *,
        secure_share: SecureShare,
        tensor_shim: BackendTensorShim,
        **kwargs: Any,
    ):
        # SecureAggregation not yet compatible with update weighting; need to
        # check it hasn't been supplied.
        # TODO: [BIT-1486] Remove this constraint
        try:
            if kwargs["weights"] is not None:
                raise NotImplementedError(
                    "SecureAggregation does not support update weighting"
                )
        except KeyError:
            pass

        super().__init__(secure_share=secure_share, tensor_shim=tensor_shim, **kwargs)

    @overload
    def run(
        self,
        algorithm_outputs: Mapping[str, _SerializedWeights],
        tensor_dtype: Optional[T_DTYPE] = None,
        **kwargs: Any,
    ) -> _Weights:
        """Decodes and averages tensor dictionaries and returns the average."""
        ...

    @overload
    def run(
        self,
        algorithm_outputs: Mapping[str, pd.DataFrame],
        tensor_dtype: Optional[T_DTYPE] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Decodes and averages pandas dataframes and returns the average."""
        ...

    @overload
    def run(
        self,
        algorithm_outputs: Mapping[str, np.ndarray],
        tensor_dtype: Optional[T_DTYPE] = None,
        **kwargs: Any,
    ) -> np.ndarray:
        """Decodes and averages numpy arrays and returns the average."""
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
        """Decodes and averages algorithm outputs and returns them.

        Args:
            algorithm_outputs: A mapping of pod names to their algorithm outputs.
            tensor_dtype: The dtype to use when converting parameter updates to tensors.
            **kwargs: Additional keyword arguments.

        Raises:
            AggregatorError: If there is any issue whereby aggregation cannot proceed.
                Details will be included in the error message.
        """
        obj_type = self._get_type(algorithm_outputs.values())
        self._validate_algorithm_outputs(algorithm_outputs.values(), obj_type)
        averaged_output: Union[pd.DataFrame, np.ndarray, _Weights]

        if obj_type == AggregationType.TENSOR_DICT:
            # First we convert the parameter updates to numpy to allow them to be
            # decoded more easily.
            algorithm_outputs = cast(
                Mapping[str, _SerializedWeights], algorithm_outputs
            )
            new_parameter_updates: list[dict[str, np.ndarray]] = []
            for update in algorithm_outputs.values():
                new_update: dict[str, np.ndarray] = {}
                for name, param in update.items():
                    new_update[name] = self._tensor_shim.to_numpy(param)
                new_parameter_updates.append(new_update)

            # Then we average and decode the parameters.
            average_state_dict = self.secure_share.average_and_decode_state_dicts(
                new_parameter_updates
            )

            # Finally we convert the averaged parameters back to tensors.
            averaged_output = {}
            for param_name, param_ in average_state_dict.items():
                averaged_output[param_name] = self._tensor_shim.to_tensor(
                    param_, dtype=tensor_dtype
                ).squeeze()

        elif obj_type == AggregationType.PANDAS_DATAFRAME:
            # First we convert the dataframes to dictionaries of numpy arrays to allow
            # them to be decoded more easily.
            algorithm_outputs = cast(Mapping[str, pd.DataFrame], algorithm_outputs)
            algorithm_output_values = [
                {
                    col: output[col].to_numpy()
                    for col in output.columns
                    if col not in self.non_numeric_columns
                }
                for output in algorithm_outputs.values()
            ]
            # Average and decode the numeric columns in the dataframes
            averaged_columns: dict[str, np.ndarray] = (
                self.secure_share.average_and_decode_state_dicts(
                    algorithm_output_values
                )
            )
            # Add back the non-numeric columns to the averaged columns.
            averaged_output = pd.DataFrame(
                {**self.non_numeric_columns, **averaged_columns}
            )
        elif obj_type == AggregationType.NUMPY_ARRAY:
            algorithm_outputs = cast(Mapping[str, np.ndarray], algorithm_outputs)
            averaged_numpy_array = self.secure_share.average_and_decode_state_dicts(
                [{"array": i} for i in algorithm_outputs.values()]
            )
            averaged_output = averaged_numpy_array["array"]

        return averaged_output


class _WorkerSide(_BaseSecureAggregator, WorkerSide_):
    """Worker-side of the secure aggregator."""

    def __init__(
        self,
        *,
        secure_share: SecureShare,
        mailbox: _InterPodWorkerMailbox,
        tensor_shim: BackendTensorShim,
        **kwargs: Any,
    ):
        super().__init__(secure_share=secure_share, tensor_shim=tensor_shim, **kwargs)
        self.mailbox = mailbox

    @overload
    async def run(
        self, algorithm_output: _Weights, **kwargs: Any
    ) -> _SerializedWeights:
        """Performs secure aggregation on the tensor dictionary.

        The tensors in the dictionary are then converted into a list of floats before
        being returned.
        """
        ...

    @overload
    async def run(self, algorithm_output: np.ndarray, **kwargs: Any) -> np.ndarray:
        """Performs secure aggregation on the array and returns it."""
        ...

    @overload
    async def run(self, algorithm_output: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
        """Performs secure aggregation on the dataframe and returns it."""
        ...

    async def run(
        self, algorithm_output: Union[_Weights, np.ndarray, pd.DataFrame], **kwargs: Any
    ) -> Union[_SerializedWeights, np.ndarray, pd.DataFrame]:
        """Encodes input, converts it to a serializable object, and returns it.

        Only tensor dictionaries are converted from tensors to lists of floats. Pandas
        dataframes and numpy arrays are left as they are.

        Args:
            algorithm_output: The algorithm output to be encoded and sent to the
                modeller.
            **kwargs: Additional keyword arguments.

        Raises:
            AggregatorError: If the algorithm output is not a supported type.
        """
        obj_type = self._get_type([algorithm_output])

        if obj_type == AggregationType.PANDAS_DATAFRAME:
            algorithm_output = cast(pd.DataFrame, algorithm_output)
            self._set_non_numeric_columns([algorithm_output])
            algorithm_output_np: dict[str, np.ndarray] = {
                col: algorithm_output[col].to_numpy()
                for col in algorithm_output.columns
            }
            keep_columns = [
                i for i in algorithm_output_np if i not in self.non_numeric_columns
            ]
            secure_aggregation_output = await self.secure_share.do_secure_aggregation(
                {k: algorithm_output_np[k] for k in keep_columns},
                self.mailbox,
            )
            return pd.DataFrame(
                {**self.non_numeric_columns, **secure_aggregation_output}
            )

        elif obj_type == AggregationType.NUMPY_ARRAY:
            algorithm_output = cast(np.ndarray, algorithm_output)
            secure_aggregation_output = await self.secure_share.do_secure_aggregation(
                {"array": algorithm_output}, self.mailbox
            )
            return secure_aggregation_output["array"]
        elif obj_type == AggregationType.TENSOR_DICT:
            algorithm_output = cast(_Weights, algorithm_output)
            secure_aggregation_output = await self.secure_share.do_secure_aggregation(
                algorithm_output, self.mailbox
            )
            # We are reusing secure_algorithm_output and changing it to
            # SerializedWeights which is why we ignore the assignment issue.
            for name, param in secure_aggregation_output.items():
                secure_aggregation_output[name] = self._tensor_shim.to_list(param)  # type: ignore[assignment] # Reason: see comment # noqa: E501

            return cast(_SerializedWeights, secure_aggregation_output)

        raise AggregatorError("Unsupported object type for Secure Aggregation.")


class _InterPodAggregatorWorkerFactory(ABC):
    """Defines the worker() factory method for inter-pod aggregation."""

    @abstractmethod
    def worker(self, mailbox: _InterPodWorkerMailbox, **kwargs: Any) -> _WorkerSide:
        """Returns worker side of the SecureAggregator."""
        pass


@delegates()
class SecureAggregator(_BaseAggregatorFactory, _InterPodAggregatorWorkerFactory):
    """Secure aggregation of encrypted model parameters.

    This aggregator is used to aggregate model parameter updates from multiple workers
    without revealing the individual updates to any worker or the modeller. This is
    known as Secure Multi-Party Computation (SMPC).

    Args:
        secure_share: The `SecureShare` object used to encrypt and decrypt model
            parameters and communicate with the other workers.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {}
    nested_fields: ClassVar[T_NESTED_FIELDS] = {"_secure_share": _secure_share_registry}

    def __init__(
        self,
        secure_share: Optional[SecureShare] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self._tensor_shim = _load_default_tensor_shim()
        self._secure_share = secure_share if secure_share else SecureShare()

    def modeller(self, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the SecureAggregator."""
        return _ModellerSide(
            tensor_shim=self._tensor_shim, secure_share=self._secure_share, **kwargs
        )

    def worker(self, mailbox: _InterPodWorkerMailbox, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the SecureAggregator.

        Args:
            mailbox: The mailbox to use for receiving messages.
            **kwargs: Additional keyword arguments to pass to the worker side.

        Returns:
            The worker side of the SecureAggregator.
        """
        return _WorkerSide(
            tensor_shim=self._tensor_shim,
            secure_share=self._secure_share,
            mailbox=mailbox,
            **kwargs,
        )


def _is_secure_share_task_request(task_request: _TaskRequest) -> bool:
    """Checks if a task request is for secure share aggregation."""
    aggregator = task_request.serialized_protocol.get("aggregator")
    if aggregator:
        return aggregator["class_name"] == AggregatorType.SecureAggregator.value
    return False
