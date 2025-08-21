"""GA custom multi-algorithm protocol.

First runs a model inference on the Fovea model, then GA model, then
the GA algorithm to compute the area affected by GA.
Then CSV and PDF Reports get generated.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Union, cast

from marshmallow import fields
import pandas as pd

from bitfount.federated.algorithms.model_algorithms.inference import (
    ModelInference,
    _WorkerSide as _InferenceWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.csv_report_generation_ophth_algorithm import (  # noqa: E501
    CSVReportGeneratorOphthalmologyAlgorithm,
    _WorkerSide as _CSVWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_calculation_algorithm_bronze import (  # noqa: E501
    GATrialCalculationAlgorithmBronze,
    _WorkerSide as _GACalcWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_inclusion_criteria_match_algorithm_bronze import (  # noqa: E501
    TrialInclusionCriteriaMatchAlgorithmBronze,
    _WorkerSide as _CriteriaMatchWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_pdf_algorithm_amethyst import (  # noqa: E501
    GATrialPDFGeneratorAlgorithmAmethyst,
    _WorkerSide as _PDFGenWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_utils import (
    _convert_ga_metrics_to_df,
    use_default_rename_columns,
)
from bitfount.federated.authorisation_checkers import InferenceLimits, ProtocolContext
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.protocols.base import (
    BaseCompatibleAlgoFactory,
    BaseProtocolFactory,
    ProtocolState,
)
from bitfount.federated.protocols.ophthalmology.ga_screening_protocol_bronze_base import (  # noqa: E501
    _WorkerSideBronzeBase,
)
from bitfount.federated.protocols.ophthalmology.utils import (
    GenericOphthalmologyModellerSide as _ModellerSide,
)
from bitfount.federated.transport.modeller_transport import _ModellerMailbox
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.types import T_FIELDS_DICT

if TYPE_CHECKING:
    from bitfount.federated.pod_vitals import _PodVitals
    from bitfount.hub.api import BitfountHub

_logger = _get_federated_logger(f"bitfount.federated.protocols.{__name__}")


class _WorkerSide(_WorkerSideBronzeBase):
    async def run(
        self,
        *,
        pod_vitals: Optional[_PodVitals] = None,
        context: Optional[ProtocolContext] = None,
        batch_num: Optional[int] = None,
        final_batch: bool = False,
        protocol_state: Optional[ProtocolState] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Runs GA algorithm on worker side followed by metrics and csv algorithms.

        Args:
            pod_vitals: Optional. Pod vitals instance for recording run-time details
                from the protocol run.
            context: Optional. Run-time context for the protocol.
            batch_num: The number of the batch being run.
            final_batch: If this run of the protocol represents the final run within
                a task.
            protocol_state: The state of the protocol, used to signal final step.
            **kwargs: Additional keyword arguments.
        """
        self.rename_columns = use_default_rename_columns(
            self.datasource, self.rename_columns
        )

        limits: Optional[dict[str, InferenceLimits]] = (
            context.inference_limits if context is not None else None
        )

        # Unpack the algorithms
        (
            fovea_algo,
            ga_algo,
            ga_calc_algo,
            criteria_match_algo,
            csv_report_algo,
            pdf_gen_algo,
        ) = self.algorithm

        fovea_algo = cast(_InferenceWorkerSide, fovea_algo)
        ga_algo = cast(_InferenceWorkerSide, ga_algo)
        ga_calc_algo = cast(_GACalcWorkerSide, ga_calc_algo)
        criteria_match_algo = cast(_CriteriaMatchWorkerSide, criteria_match_algo)
        csv_report_algo = cast(_CSVWorkerSide, csv_report_algo)
        pdf_gen_algo = cast(_PDFGenWorkerSide, pdf_gen_algo)

        # Run Fovea inference
        (
            fovea_predictions_df,
            fovea_limits_exceeded_info,
            final_batch,
        ) = await self._run_fovea_inference(
            fovea_algo, limits, pod_vitals, final_batch, protocol_state
        )

        # Run GA inference
        (
            ga_predictions_df,
            ga_limits_exceeded_info,
            final_batch,
            filenames,
        ) = await self._run_ga_inference(
            ga_algo, limits, batch_num, final_batch, protocol_state
        )

        # Run GA calculation
        ga_metrics = await self._run_ga_calculation(
            ga_calc_algo,
            ga_predictions_df,
            fovea_predictions_df,
            filenames,
        )

        # Run criteria matching
        (
            test_data_df,
            criteria_yes,
            criteria_no,
            column_filters,
            task_notification,
        ) = await self._run_criteria_matching(
            criteria_match_algo,
            ga_metrics,
            filenames,
            batch_num,
        )

        # Run report generation
        results_with_pdf_paths = await self._run_reports_generation(
            csv_report_algo,
            pdf_gen_algo,
            ga_metrics,
            ga_predictions_df,
            _convert_ga_metrics_to_df(ga_metrics),
            filenames,
            column_filters,
            criteria_match_algo,
            final_batch,
        )

        # Check if limits were exceeded and so we should abort any remaining protocol
        # batches
        if fovea_limits_exceeded_info:
            # fovea_limits_exceeded_info is not None if and only if limits is not None
            assert limits is not None  # nosec[assert_used]

            await self.handle_limits_exceeded(
                fovea_algo, fovea_limits_exceeded_info, limits, self.mailbox
            )
        elif ga_limits_exceeded_info:
            # ga_limits_exceeded_info is not None if and only if limits is not None
            assert limits is not None  # nosec[assert_used]

            await self.handle_limits_exceeded(
                ga_algo, ga_limits_exceeded_info, limits, self.mailbox
            )
        else:
            return results_with_pdf_paths


class GAScreeningProtocolBronze(BaseProtocolFactory):
    """Protocol for running GA Algorithms and fovea sequentially."""

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "results_notification_email": fields.Boolean(allow_none=True),
        "rename_columns": fields.Dict(
            keys=fields.Str(), values=fields.Str(), allow_none=True
        ),
        "trial_name": fields.Str(allow_none=True),
    }

    def __init__(
        self,
        *,
        algorithm: Sequence[
            Union[
                ModelInference,
                ModelInference,
                GATrialCalculationAlgorithmBronze,
                TrialInclusionCriteriaMatchAlgorithmBronze,
                CSVReportGeneratorOphthalmologyAlgorithm,
                GATrialPDFGeneratorAlgorithmAmethyst,
            ]
        ],
        results_notification_email: Optional[bool] = False,
        trial_name: Optional[str] = None,
        rename_columns: Optional[Mapping[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(algorithm=algorithm, **kwargs)
        self.results_notification_email = (
            results_notification_email
            if results_notification_email is not None
            else False
        )
        self.rename_columns = rename_columns
        self.trial_name = trial_name

    @classmethod
    def _validate_algorithm(cls, algorithm: BaseCompatibleAlgoFactory) -> None:
        """Validates the algorithms by ensuring they are either GA or Fovea."""
        if (
            algorithm.class_name
            not in (
                "bitfount.ModelInference",
                "bitfount.GATrialCalculationAlgorithmBronze",
                "bitfount.TrialInclusionCriteriaMatchAlgorithmBronze",
                "bitfount.CSVReportGeneratorOphthalmologyAlgorithm",
                "bitfount.CSVReportGeneratorAlgorithm",  # Kept for backwards compatibility # noqa: E501
                "bitfount.GATrialPDFGeneratorAlgorithmAmethyst",
                # Without ".bitfount" prefix for backwards compatibility
                "GATrialCalculationAlgorithmBronze",
                "TrialInclusionCriteriaMatchAlgorithmBronze",
                "CSVReportGeneratorOphthalmologyAlgorithm",
                "CSVReportGeneratorAlgorithm",  # Kept for backwards compatibility
                "GATrialPDFGeneratorAlgorithmAmethyst",
            )
        ):
            raise TypeError(
                f"The {cls.__name__} protocol does not support "
                + f"the {type(algorithm).__name__} algorithm.",
            )

    def modeller(self, mailbox: _ModellerMailbox, **kwargs: Any) -> _ModellerSide:
        """Returns the Modeller side of the protocol."""
        algorithms = cast(
            Sequence[
                Union[
                    ModelInference,
                    ModelInference,
                    GATrialCalculationAlgorithmBronze,
                    TrialInclusionCriteriaMatchAlgorithmBronze,
                    CSVReportGeneratorOphthalmologyAlgorithm,
                    GATrialPDFGeneratorAlgorithmAmethyst,
                ]
            ],
            self.algorithms,
        )
        modeller_algos = []
        for algo in algorithms:
            if hasattr(algo, "pretrained_file"):
                modeller_algos.append(
                    algo.modeller(pretrained_file=algo.pretrained_file)
                )
            else:
                modeller_algos.append(algo.modeller())
        return _ModellerSide(
            algorithm=modeller_algos,
            mailbox=mailbox,
            **kwargs,
        )

    def worker(
        self,
        mailbox: _WorkerMailbox,
        hub: BitfountHub,
        context: Optional[ProtocolContext] = None,
        **kwargs: Any,
    ) -> _WorkerSide:
        """Returns worker side of the GAScreeningProtocolBronze protocol.

        Args:
            mailbox: Worker mailbox instance to allow communication to the modeller.
            hub: `BitfountHub` object to use for communication with the hub.
            context: Optional. Run-time protocol context details for running.
            **kwargs: Additional keyword arguments.
        """
        algorithms = cast(
            Sequence[
                Union[
                    ModelInference,
                    ModelInference,
                    GATrialCalculationAlgorithmBronze,
                    TrialInclusionCriteriaMatchAlgorithmBronze,
                    CSVReportGeneratorOphthalmologyAlgorithm,
                    GATrialPDFGeneratorAlgorithmAmethyst,
                ]
            ],
            self.algorithms,
        )
        return _WorkerSide(
            algorithm=[algo.worker(hub=hub, context=context) for algo in algorithms],
            mailbox=mailbox,
            results_notification_email=self.results_notification_email,
            trial_name=self.trial_name,
            rename_columns=self.rename_columns,
            **kwargs,
        )
