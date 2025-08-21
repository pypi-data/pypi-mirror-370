"""Utility functions/classes for ophthalmology protocols."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Optional, Union

import torch

from bitfount.federated.algorithms.base import NoResultsModellerAlgorithm
from bitfount.federated.algorithms.model_algorithms.inference import (
    _ModellerSide as _InferenceModellerSide,
)
from bitfount.federated.authorisation_checkers import ProtocolContext
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.protocols.base import BaseModellerProtocol

_logger = _get_federated_logger(f"bitfount.federated.protocols.{__name__}")

if TYPE_CHECKING:
    from bitfount.federated.transport.modeller_transport import _ModellerMailbox


class GenericOphthalmologyModellerSide(BaseModellerProtocol):
    """Modeller side of a generic ophthalmology protocol.

    Args:
        algorithm: The sequence of GA modeller algorithms to be used.
        mailbox: The mailbox to use for communication with the Workers.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[Union[_InferenceModellerSide, NoResultsModellerAlgorithm]]

    def __init__(
        self,
        *,
        algorithm: Sequence[Union[_InferenceModellerSide, NoResultsModellerAlgorithm]],
        mailbox: _ModellerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

    def initialise(
        self,
        task_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialises the component algorithms."""
        # Modeller is not performing any inference, training, etc., of models,
        # so use CPU rather than taking up GPU resources.
        for algo in self.algorithms:
            updated_kwargs = kwargs.copy()
            if hasattr(algo, "model"):
                updated_kwargs.update(map_location=torch.device("cpu"))
            algo.initialise(
                task_id=task_id,
                **updated_kwargs,
            )

    async def run(
        self,
        *,
        context: Optional[ProtocolContext] = None,
        **kwargs: Any,
    ) -> Union[list[Any], Any]:
        """Runs Modeller side of the protocol.

        This just sends the model parameters to the workers sequentially and then tells
        the workers when the protocol is finished.

        Args:
            context: Optional. Run-time context for the protocol.
            **kwargs: Additional keyword arguments.
        """
        results = []

        for algo in self.algorithm:
            _logger.info(f"Running algorithm {algo.class_name}")
            result = await self.mailbox.get_evaluation_results_from_workers()
            results.append(result)
            _logger.info("Received results from Pods.")
            _logger.info(f"Algorithm {algo.class_name} completed.")

        final_results = [
            algo.run(result_) for algo, result_ in zip(self.algorithm, results)
        ]

        return final_results
