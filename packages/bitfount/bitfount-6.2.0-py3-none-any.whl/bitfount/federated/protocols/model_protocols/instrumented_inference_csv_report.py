"""Copy of the InferenceAndCSVReport protocol that sends metrics to Bitfount."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Optional, Union, cast

import pandas as pd

from bitfount.federated.algorithms.base import _BaseAlgorithm
from bitfount.federated.authorisation_checkers import ProtocolContext
from bitfount.federated.protocols.model_protocols.inference_csv_report import (
    InferenceAndCSVReport,
    _InferenceAndCSVReportCompatibleAlgoFactory_,
    _InferenceAndCSVReportCompatibleHuggingFaceAlgoFactory,
    _InferenceAndCSVReportCompatibleModelAlgoFactory,
    _InferenceAndCSVReportCSVCompatibleWorkerAlgorithm,
    _InferenceAndCSVReportModelCompatibleWorkerAlgorithm,
    _InferenceAndCSVReportModelIncompatibleWorkerAlgorithm,
    _WorkerSide as _InferenceCSVWorkerSide,
)
from bitfount.federated.transport.opentelemetry import get_task_meter
from bitfount.federated.transport.worker_transport import _WorkerMailbox

if TYPE_CHECKING:
    from bitfount.federated.pod_vitals import _PodVitals
    from bitfount.hub.api import BitfountHub


class _WorkerSide(_InferenceCSVWorkerSide):
    """Worker side of the protocol.

    Args:
        algorithm: A list of algorithms to be run by the protocol. This should be
            a list of two algorithms, the first being the model inference algorithm
            and the second being the csv report algorithm.
        mailbox: The mailbox to use for communication with the Modeller.
        **kwargs: Additional keyword arguments.
    """

    def __init__(
        self,
        *,
        algorithm: Sequence[
            Union[
                _InferenceAndCSVReportModelCompatibleWorkerAlgorithm,
                _InferenceAndCSVReportModelIncompatibleWorkerAlgorithm,
                _InferenceAndCSVReportCSVCompatibleWorkerAlgorithm,
            ]
        ],
        mailbox: _WorkerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

        self._task_meter = get_task_meter()
        self._task_id = mailbox._task_id if mailbox._task_id is not None else "None"

    async def run(
        self,
        *,
        pod_vitals: Optional[_PodVitals] = None,
        context: Optional[ProtocolContext] = None,
        batch_num: Optional[int] = None,
        final_batch: bool = False,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Runs the algorithm on worker side.

        Args:
            pod_vitals: Optional. Pod vitals instance for recording run-time details
                from the protocol run.
            context: Optional. Run-time context for the protocol.
            batch_num: The number of the batch being run. 0-indexed.
            final_batch: If this run of the protocol represents the final run within
                a task.
            **kwargs: Additional keyword arguments.
        """
        model_predictions, limits_exceeded_tuple = await super()._run(
            pod_vitals=pod_vitals, context=context, final_batch=final_batch, **kwargs
        )

        algorithm: Union[_BaseAlgorithm, str] = (
            self.algorithm[0]
            if isinstance(self.algorithm[0], _BaseAlgorithm)  # should always be
            else self.algorithm[0].__class__.__module__
        )
        self._task_meter.submit_algorithm_records_returned(
            records_count=len(model_predictions.index),
            task_id=self._task_id,
            algorithm=algorithm,
            protocol_batch_num=batch_num,
            project_id=self.project_id,
        )

        # Check if limits were exceeded and so we should abort any remaining protocol
        # batches
        if limits_exceeded_tuple is not None:
            limits_exceeded_info, limits, model_inference_algo = limits_exceeded_tuple
            if limits_exceeded_info:
                # This will deliberately raise an exception
                await self.handle_limits_exceeded(
                    model_inference_algo, limits_exceeded_info, limits, self.mailbox
                )

        # Return the model_predictions from the model inference
        # algorithm so we can enable saving to the project database
        # for this protocol type
        return model_predictions


class InstrumentedInferenceAndCSVReport(InferenceAndCSVReport):
    """Protocol that sends telemetry metrics back to Bitfount.

    Extends InferenceAndCSVReport to send the number of records output to CSV.
    """

    def worker(
        self,
        mailbox: _WorkerMailbox,
        hub: BitfountHub,
        context: Optional[ProtocolContext] = None,
        **kwargs: Any,
    ) -> _WorkerSide:
        """Returns worker side of the InstrumentedInferenceAndCSVReport protocol.

        Args:
            mailbox: Worker mailbox instance to allow communication to the modeller.
            hub: `BitfountHub` object to use for communication with the hub.
            context: Optional. Run-time protocol context details for running.
            **kwargs: Additional keyword arguments.
        """
        algorithms = cast(
            Sequence[
                Union[
                    _InferenceAndCSVReportCompatibleAlgoFactory_,
                    _InferenceAndCSVReportCompatibleModelAlgoFactory,
                    _InferenceAndCSVReportCompatibleHuggingFaceAlgoFactory,
                ]
            ],
            self.algorithms,
        )
        return _WorkerSide(
            algorithm=[algo.worker(hub=hub, context=context) for algo in algorithms],
            mailbox=mailbox,
            **kwargs,
        )
