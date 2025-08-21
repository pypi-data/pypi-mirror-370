"""Algorithm for calculating the GA area."""

from __future__ import annotations

from bitfount.federated.algorithms.ophthalmology.ga_trial_calculation_algorithm_base import (  # noqa: E501
    GATrialCalculationAlgorithmBase,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.utils.logging_utils import deprecated_class_name

logger = _get_federated_logger("bitfount.federated")


class GATrialCalculationAlgorithmJade(GATrialCalculationAlgorithmBase):
    """Jade Trial Calculation.

    As it requires calculating GA Area and associated metrics,
    it inherits from the generic base class.
    """

    pass


# Kept for backwards compatibility
@deprecated_class_name
class GATrialCalculationAlgorithm(GATrialCalculationAlgorithmJade):
    """Algorithm for calculating the GA Area and associated metrics."""

    pass
