"""PyTorch implementations for the Bitfount framework."""

from __future__ import annotations

from bitfount.backends.pytorch.data.dataloaders import (
    PyTorchIterableBitfountDataLoader,
)
from bitfount.backends.pytorch.data.utils import DEFAULT_BUFFER_SIZE
from bitfount.backends.pytorch.federated.shim import PyTorchBackendTensorShim
from bitfount.backends.pytorch.loss import SoftDiceLoss, soft_dice_loss
from bitfount.backends.pytorch.models.base_models import PyTorchClassifierMixIn
from bitfount.backends.pytorch.models.bitfount_model import (
    PyTorchBitfountModel as PyTorchBitfountModel,
    PyTorchBitfountModelv2,
)
from bitfount.backends.pytorch.utils import autodetect_gpu

__all__: list[str] = [
    "autodetect_gpu",
    "DEFAULT_BUFFER_SIZE",
    "PyTorchBackendTensorShim",
    "PyTorchBitfountModelv2",
    "PyTorchClassifierMixIn",
    "PyTorchIterableBitfountDataLoader",
    "soft_dice_loss",
    "SoftDiceLoss",
]

# See top level `__init__.py` for an explanation
__pdoc__ = {}
for _obj in __all__:
    __pdoc__[_obj] = False
