"""Algorithm for calculating the GA area."""

from __future__ import annotations

from bitfount.federated.algorithms.ophthalmology.ga_trial_calculation_algorithm_base import (  # noqa: E501
    GATrialCalculationAlgorithmBase,
)
from bitfount.federated.logging import _get_federated_logger

logger = _get_federated_logger("bitfount.federated")


class GATrialCalculationAlgorithmAmethyst(GATrialCalculationAlgorithmBase):
    """Amethyst Trial Calculation.

    As it requires calculating GA Area and associated metrics,
    it inherits from the generic base class.
    """

    pass
