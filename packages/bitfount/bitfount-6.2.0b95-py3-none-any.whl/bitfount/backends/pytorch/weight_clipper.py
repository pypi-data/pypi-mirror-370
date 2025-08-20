"""Parameter clipping for continuous attributes secure aggergation.

Based on discussions from:
https://discuss.pytorch.org/t/set-constraints-on-parameters-or-layers/23620
"""

from __future__ import annotations

import logging
from typing import cast

import torch
from torch import Tensor
import torch.nn as nn

logger = logging.getLogger(__name__)


class _PytorchParamConstraint:
    """Class for clamping model parameters.

    Used to make sure that the model parameters stay within
    the constraints for secure aggregation.
    """

    def __init__(self, prime_q: int, precision: int, num_workers: int) -> None:
        self.prime_q = prime_q
        self.precision = precision
        self.num_workers = num_workers

    def __call__(self, module: nn.Module) -> None:
        """Clamp the required parameters on call."""
        w: Tensor

        if hasattr(module, "weight"):
            # Get the parameter data
            w = cast(Tensor, module.weight.data)
            # Clamp the data in the required interval
            w = torch.clamp(
                w,
                -self.prime_q / (self.precision * 2 * self.num_workers),
                self.prime_q / (self.precision * 2 * self.num_workers),
            )
            # Assign the clamped value to the parameter
            module.weight.data = w

        if hasattr(module, "running_var"):
            # Get the parameter data
            w = cast(Tensor, module.running_var.data)
            # Clamp the data in the required interval
            w = torch.clamp(
                w,
                -self.prime_q / (self.precision * 2 * self.num_workers),
                self.prime_q / (self.precision * 2 * self.num_workers),
            )
            # Assign the clamped value to the parameter
            module.running_var.data = w

        if hasattr(module, "running_mean"):
            # Get the parameter data
            w = cast(Tensor, module.running_mean.data)
            # Clamp the data in the required interval
            w = torch.clamp(
                w,
                -self.prime_q / (self.precision * 2 * self.num_workers),
                self.prime_q / (self.precision * 2 * self.num_workers),
            )
            # Assign the clamped value to the parameter
            module.running_mean.data = w
