"""Pytorch implementation of the tensor shim."""

from __future__ import annotations

from collections.abc import Sequence
import logging
from typing import Any, ClassVar, Union, cast

import numpy as np
import torch

from bitfount.backends.pytorch.types import _AdaptorForPyTorchTensor
from bitfount.federated.shim import BackendTensorShim
from bitfount.types import (
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    _BaseSerializableObjectMixIn,
    _TensorLike,
)

_logger = logging.getLogger(__name__)


class PyTorchBackendTensorShim(BackendTensorShim, _BaseSerializableObjectMixIn):
    """PyTorch backend shim/bridge for converting from/to PyTorch tensors."""

    fields_dict: ClassVar[T_FIELDS_DICT] = {}
    nested_fields: ClassVar[T_NESTED_FIELDS] = {}

    @staticmethod
    def to_numpy(t: Union[_TensorLike, list[float]]) -> np.ndarray:
        """See base class."""
        if isinstance(t, _AdaptorForPyTorchTensor):
            array_t = t.torchtensor.numpy()
        else:
            array_t = np.asarray(t)
        return array_t

    @staticmethod
    def to_tensor(p: Sequence, **kwargs: Any) -> _TensorLike:
        """See base class."""
        return _AdaptorForPyTorchTensor(torch.tensor(p, **kwargs))

    @staticmethod
    def to_list(p: Union[np.ndarray, _TensorLike]) -> list[float]:
        """See base class."""
        if isinstance(p, np.ndarray):
            return cast(list[float], p.tolist())
        elif isinstance(p, _AdaptorForPyTorchTensor):
            return p.torchtensor.tolist()
        else:
            raise TypeError("Unexpected type")

    @staticmethod
    def is_tensor(p: Any) -> bool:
        """See base class."""
        is_tensor: bool = torch.is_tensor(p)
        return is_tensor

    @staticmethod
    def clamp_params(
        p: _TensorLike, prime_q: int, precision: int, num_workers: int
    ) -> _TensorLike:
        """Method for clipping params for secure sharing.

        Constrains the parameters for secure sharing to be within the
        required range for secure sharing. Used only when
        `steps_between_parameter_updates` is 1.

        Args:
            p: The tensor to be constrained.
            prime_q: The prime use for secret aggregation.
            precision: The precision used for secret aggregation.
            num_workers: The number of workers taking part in the secure aggregation.

        Returns:
            The clamped parameters.
        """
        if isinstance(p, _AdaptorForPyTorchTensor):
            return _AdaptorForPyTorchTensor(
                torch.clamp(
                    p.torchtensor,
                    -prime_q / (precision * 2 * num_workers),
                    prime_q / (precision * 2 * num_workers),
                )
            )
        else:
            # Even if it's not explicitly an _AdaptorForPyTorchTensor we can try
            # to use it anyway
            if not PyTorchBackendTensorShim.is_tensor(p):
                _logger.debug(
                    "PyTorchBackendTensorShim is unsure if using torch.Tensor in"
                    " clamp_params(); will try to use"
                )

            return _AdaptorForPyTorchTensor(
                torch.clamp(
                    cast(torch.Tensor, p),
                    -prime_q / (precision * 2 * num_workers),
                    prime_q / (precision * 2 * num_workers),
                )
            )
