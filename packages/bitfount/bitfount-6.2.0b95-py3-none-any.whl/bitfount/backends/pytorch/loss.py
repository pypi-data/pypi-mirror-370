"""Implements loss for pytorch modules."""

from __future__ import annotations

from collections.abc import Sequence

# Based on https://github.com/justusschock/dl-utils/blob/master/dlutils/losses/soft_dice.py # noqa: E501
from typing import Optional, Union, cast

import numpy as np
import torch
import torch.nn.functional as F


class SoftDiceLoss(torch.nn.Module):
    """Soft Dice Loss.

    The soft dice loss is computed as a fraction of nominator over denominator, where:
    nominator is 2 * the area of overlap between targets and predictions plus a
    smooth factor,and the denominator is the total number of pixels in both images
    plus the smooth factor.If weights are provided the fraction is multiplied by the
    provided weights for each class.If either square_nom or square_denom are provided,
    then the respective nominator or denominator will be raised to the power of 2.

    Args:
        square_nom: Whether to square the nominator. Optional.
        square_denom: Whether to square the denominator. Optional.
        weight: Additional weighting of individual classes. Optional.
        smooth: Smoothing for nominator and denominator. Optional.Defaults to 1.
    """

    def __init__(
        self,
        square_nom: bool = False,
        square_denom: bool = False,
        weight: Optional[Union[Sequence, torch.Tensor]] = None,
        smooth: float = 1.0,
    ):
        super().__init__()
        self.square_nom = square_nom
        self.square_denom = square_denom

        self.smooth = smooth

        if weight is not None:
            if not isinstance(weight, torch.Tensor):
                weight = torch.tensor(weight)

            self.register_buffer("weight", weight)
        else:
            self.weight = None

    def forward(self, predictions: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """Computes Soft Dice Loss.

        Args:
            predictions: The predictions obtained by the network.
            targets: The targets (ground truth) for the predictions.

        Returns:
            torch.Tensor: The computed loss value

        Raises:
            ValueError: If the predictions tensor has less than 3 dimensions.
            ValueError: If the targets tensor has less than 2 dimensions.

        """
        # number of classes for onehot
        n_classes = predictions.shape[1]
        if predictions.ndim < 3:
            raise ValueError(
                "Predictions expected to have at least 3 dimensions. "
                f"Your predictions have {predictions.ndim}"
            )
        if targets.ndim < 2:
            raise ValueError(
                "Targets expected to have at least 2 dimensions. "
                f"Your targets have {targets.ndim}"
            )

        # one hot encoding on the batch
        with torch.no_grad():
            target = targets.unsqueeze(1)
            dtype, device, shape = target.dtype, target.device, target.shape
            one_hot = torch.zeros(
                shape[0], n_classes, *shape[2:], dtype=dtype, device=device
            )
            targets_onehot = one_hot.scatter_(1, target, 1.0)

        # sum over spatial dimensions
        dims = tuple(range(2, predictions.dim()))

        # compute nominator
        if self.square_nom:
            nom = torch.sum((predictions * targets_onehot.float()) ** 2, dim=dims)
        else:
            nom = torch.sum(predictions * targets_onehot.float(), dim=dims)
        nom = 2 * nom + self.smooth

        # compute denominator
        if self.square_denom:
            i_sum = torch.sum(predictions**2, dim=dims)
            t_sum = torch.sum(targets_onehot**2, dim=dims)
        else:
            i_sum = torch.sum(predictions, dim=dims)
            t_sum = torch.sum(targets_onehot, dim=dims)

        denom = i_sum + t_sum.float() + self.smooth

        # compute loss
        frac = nom / denom

        # apply weight for individual classes properly
        if self.weight is not None:
            frac = self.weight * frac  # type: ignore[unreachable] # Reason: weight can be a torch.tensor. # noqa: E501
        # average over classes
        frac = -torch.mean(frac, dim=1)

        return frac


def soft_dice_loss(
    pred: np.ndarray,
    targets: np.ndarray,
    square_nom: bool = False,
    square_denom: bool = False,
    weight: Optional[Union[Sequence, torch.Tensor]] = None,
    smooth: float = 1.0,
) -> torch.Tensor:
    """Functional implementation of the SoftDiceLoss.

    Args:
        pred: A numpy array of predictions.
        targets: A numpy array of targets.
        square_nom: Whether to square the nominator.
        square_denom: Whether to square the denominator.
        weight: Additional weighting of individual classes.
        smooth: Smoothing for nominator and denominator.

    Returns:
        A torch tensor with the computed dice loss.
    """
    dice_loss = SoftDiceLoss(square_nom, square_denom, weight, smooth)
    # Make predictions and targets tensors
    pred_tensor, targets_tensor = torch.from_numpy(pred), torch.from_numpy(targets)
    # Targets need to be of torch type long.
    targets_tensor = targets_tensor.long()
    pred_tensor = F.softmax(pred_tensor, dim=1)
    return cast(torch.Tensor, dice_loss(pred_tensor, targets_tensor))
