"""Base models and helper classes using PyTorch as the backend."""

from __future__ import annotations

import logging
from typing import TypedDict

import torch

# Convention is to import functional as F
# noinspection PyPep8Naming
from torch.nn import functional as F
import torch.optim as optimizers
import torch_optimizer as torch_optimizers
from typing_extensions import NotRequired

from bitfount.models.base_models import ClassifierMixIn
from bitfount.types import _StrAnyDict
from bitfount.utils import delegates

logger = logging.getLogger(__name__)


_OptimizerType = torch_optimizers.Optimizer | optimizers.Optimizer
# From pl.LightningModule, converted for our use:
#   STEP_OUTPUT = Optional[Union[Tensor, Mapping[str, Any]]]
_TRAIN_STEP_OUTPUT = torch.Tensor | _StrAnyDict


class _TEST_STEP_OUTPUT(TypedDict):
    """TypedDict for output from BitfountModel test steps.

    Should be: "A dictionary of predictions and targets, with the dictionary keys
    being "predictions" and "targets" for each of them, respectively. These will be
    passed to the `test_epoch_end` method."
    """

    predictions: torch.Tensor | list[str]
    targets: torch.Tensor | list[str]
    keys: NotRequired[list[str]]


# Non-TypedDict version of _TEST_STEP_OUTPUT for locations where the TypedDict won't
# work
_TEST_STEP_OUTPUT_GENERIC = dict[str, torch.Tensor | list[str]]

# Old name, should not be used. Use _TRAIN_STEP_OUTPUT or _TEST_STEP_OUTPUT instead.
_STEP_OUTPUT = torch.Tensor | _StrAnyDict


@delegates()
class PyTorchClassifierMixIn(ClassifierMixIn):
    """MixIn for PyTorch classification problems.

    PyTorch classification models must have this class in their inheritance hierarchy.
    """

    def _do_output_activation(self, output: torch.Tensor) -> torch.Tensor:
        """Perform final activation function on output."""
        if self.multilabel:
            return torch.sigmoid(output)
        else:
            return F.softmax(output, dim=1)
