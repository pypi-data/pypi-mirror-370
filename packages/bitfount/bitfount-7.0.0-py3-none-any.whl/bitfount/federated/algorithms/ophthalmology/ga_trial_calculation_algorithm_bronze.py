"""Algorithm for calculating the GA area."""

from __future__ import annotations

from typing import Any

from bitfount.federated.algorithms.ophthalmology.ga_trial_calculation_algorithm_base import (  # noqa: E501
    GATrialCalculationAlgorithmWithFoveaBase,
    _BaseWorkerSideWithFovea,
)
from bitfount.federated.logging import _get_federated_logger

logger = _get_federated_logger("bitfount.federated")


class _WorkerSide(_BaseWorkerSideWithFovea):
    """Worker side of the algorithm."""

    pass


class GATrialCalculationAlgorithmBronze(GATrialCalculationAlgorithmWithFoveaBase):
    """Algorithm for calculating the GA Area and associated metrics.

    Args:
        ga_area_include_segmentations: List of segmentation labels to be used for
            calculating the GA area. The logical AND of the masks for these labels will
            be used to calculate the GA area. If not provided, the default inclusion
            labels for the GA area will be used.
        ga_area_exclude_segmentations: List of segmentation labels to be excluded from
            calculating the GA area. If any of these segmentations are present in the
            axial segmentation masks, that axis will be excluded from the GA area
            calculation. If not provided, the default exclusion labels for the GA area
            will be used.
        fovea_landmark_idx: index of the fovea landmark in the tuple.
            0 for fovea start, 1 for fovea middle, 2 for fovea end. Default is 1.

    Raises:
        ValueError: If an invalid segmentation label is provided.
        ValueError: If a segmentation label is provided in both the include and exclude
            lists.
    """

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Worker-side of the algorithm."""
        return _WorkerSide(
            ga_area_include_segmentations=self.ga_area_include_segmentations,
            ga_area_exclude_segmentations=self.ga_area_exclude_segmentations,
            fovea_landmark_idx=self.fovea_landmark_idx,
            **kwargs,
        )
