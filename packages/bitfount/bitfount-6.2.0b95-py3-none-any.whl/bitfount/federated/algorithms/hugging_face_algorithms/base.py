"""Base classes for HuggingFace algorithms."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Optional

from bitfount.federated.algorithms.base import BaseModellerAlgorithm
from bitfount.federated.logging import _get_federated_logger

logger = _get_federated_logger(__name__)


class _HFModellerSide(BaseModellerAlgorithm):
    """Modeller side for HuggingFace algorithms.

    Args:
        task_name: The name of the task to log.
    """

    def __init__(self, task_name: Optional[str] = None) -> None:
        super().__init__()
        self.task_name = task_name

    def initialise(self, task_id: Optional[str] = None, **kwargs: Any) -> None:
        """Nothing to initialise here."""
        pass

    def run(self, results: Mapping[str, Any], log: bool = False) -> dict[str, Any]:
        """Simply returns results and optionally logs them."""
        if log and self.task_name:
            for pod_name, response in results.items():
                for _, response_ in enumerate(response):
                    logger.info(f"{pod_name}: {response_[self.task_name]}")

        return dict(results)
