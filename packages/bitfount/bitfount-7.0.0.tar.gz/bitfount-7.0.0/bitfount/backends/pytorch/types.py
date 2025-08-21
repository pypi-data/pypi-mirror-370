"""Type Variable for our PyTorch Models."""

from __future__ import annotations

from typing import Any, Optional

import torch

from bitfount.types import _TensorLike


class _AdaptorForPyTorchTensor(_TensorLike):
    """Adapter protocol for pytorch Tensor.

    This is a thin wrapper around a pytorch tensor. It is required to provide definitive
    type annotations for different tensor operations.
    """

    def __init__(self, tensor: torch.Tensor):
        self.torchtensor = tensor

    def __mul__(self, other: Any) -> _AdaptorForPyTorchTensor:
        return _AdaptorForPyTorchTensor(self.torchtensor * other)

    def __sub__(self, other: Any) -> _AdaptorForPyTorchTensor:
        return _AdaptorForPyTorchTensor(self.torchtensor - other)

    def squeeze(self, axis: Optional[Any] = None) -> _AdaptorForPyTorchTensor:
        """Returns a tensor with all the dimensions of input of size 1 removed."""
        if axis is not None:
            return _AdaptorForPyTorchTensor(torch.squeeze(self.torchtensor, dim=axis))
        else:
            return _AdaptorForPyTorchTensor(torch.squeeze(self.torchtensor))
