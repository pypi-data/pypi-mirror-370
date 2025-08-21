"""Protocol for querying NextGen EHR data and outputting results to CSV.

This protocol first queries patient data from NextGen's APIs based on specified
criteria, then outputs the results to a CSV file.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import time
from typing import TYPE_CHECKING, Any, ClassVar, Optional, cast

from marshmallow import fields
import pandas as pd
import torch

from bitfount.federated.algorithms.base import NoResultsModellerAlgorithm
from bitfount.federated.algorithms.ehr.ehr_patient_query_algorithm import (
    EHRPatientQueryAlgorithm,
    PatientDetails,
    PatientQueryResults,
    _WorkerSide as _NextGenQueryWorkerSide,
)
from bitfount.federated.algorithms.filtering_algorithm import (
    RecordFilterAlgorithm,
    _WorkerSide as _RecordFilterWorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.dataframe_generation_extensions import (  # noqa: E501
    generate_bitfount_patient_id,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    DOB_COL,
    NAME_COL,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_utils import (
    use_default_rename_columns,
)
from bitfount.federated.algorithms.ophthalmology.simple_csv_algorithm import (
    _SimpleCSVAlgorithm,
    _WorkerSide as _CSVWorkerSide,
)
from bitfount.federated.authorisation_checkers import ProtocolContext
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.protocols.base import (
    BaseCompatibleAlgoFactory,
    BaseModellerProtocol,
    BaseProtocolFactory,
    BaseWorkerProtocol,
    InitialSetupProtocol,
)
from bitfount.federated.transport.modeller_transport import _ModellerMailbox
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.hub.api import BitfountHub
from bitfount.types import T_FIELDS_DICT
from bitfount.utils.pandas_utils import find_dob_column, find_full_name_column

if TYPE_CHECKING:
    from bitfount.federated.pod_vitals import _PodVitals

_logger = _get_federated_logger(f"bitfount.federated.protocols.{__name__}")


class _ModellerSide(BaseModellerProtocol):
    """Modeller side of the NextGenSearchProtocol protocol.

    Args:
        algorithm: The sequence of algorithms to be used. On the modeller side these
            should be no-op algorithms.
        mailbox: The mailbox to use for communication with the Workers.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[NoResultsModellerAlgorithm]

    def __init__(
        self,
        *,
        algorithm: Sequence[NoResultsModellerAlgorithm],
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
    ) -> list[Any]:
        """Runs Modeller side of the protocol.

        Retrieves messages from the workers sequentially and then tells the workers
        when the protocol is finished.

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
            algo.run(result_)  # type: ignore[func-returns-value] # Reason: algos return None by design # noqa: E501
            for algo, result_ in zip(self.algorithm, results)
        ]

        return final_results


class _WorkerSide(BaseWorkerProtocol, InitialSetupProtocol[_RecordFilterWorkerSide]):
    """Worker side of the NextGenSearchProtocol protocol."""

    algorithm: Sequence[
        _RecordFilterWorkerSide | _NextGenQueryWorkerSide | _CSVWorkerSide
    ]

    def __init__(
        self,
        *,
        algorithm: Sequence[
            _RecordFilterWorkerSide | _NextGenQueryWorkerSide | _CSVWorkerSide
        ],
        mailbox: _WorkerMailbox,
        rename_columns: Optional[Mapping[str, str]] = None,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)
        self.rename_columns = rename_columns
        self._task_id: Optional[str] = mailbox._task_id

    async def run(
        self,
        *,
        pod_vitals: Optional[_PodVitals] = None,
        context: Optional[ProtocolContext] = None,
        batch_num: Optional[int] = None,
        final_batch: bool = False,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Run NextGen query on patients in data, then runs CSV report generation.

        Args:
            pod_vitals: Optional. Pod vitals instance for recording run-time details.
            context: Optional. Run-time context for the protocol.
            batch_num: The number of the batch being run.
            final_batch: If this run represents the final batch.
            **kwargs: Additional keyword arguments.
        """
        # Use datasource-default column renamings if none provided
        self.rename_columns = use_default_rename_columns(
            self.datasource, self.rename_columns
        )

        # Unpack the algorithms
        record_filter_algo, query_algo, csv_output_algo = self.algorithm

        if pod_vitals:
            pod_vitals.last_task_execution_time = time.time()

        # Run record filter algo (noop)
        cast(_RecordFilterWorkerSide, record_filter_algo).run()
        # Send empty results to modeller to move to next algorithm
        await self.mailbox.send_evaluation_results({})

        # Retrieve the data for this run
        dfs: list[pd.DataFrame] = list(self.datasource.yield_data(use_cache=True))
        file_data: pd.DataFrame
        if any(not df.empty for df in dfs):
            file_data = pd.concat(dfs, axis="index")
            file_data = generate_bitfount_patient_id(
                file_data,
                name_col=(
                    found_name_col
                    if (found_name_col := find_full_name_column(file_data)) is not None
                    else NAME_COL
                ),
                dob_col=(
                    found_dob_col
                    if (found_dob_col := find_dob_column(file_data)) is not None
                    else DOB_COL
                ),
            )
            if found_name_col is not None:
                file_data = file_data.rename({found_name_col: NAME_COL}, axis=1)
            if found_dob_col is not None:
                file_data = file_data.rename({found_dob_col: DOB_COL}, axis=1)
        else:
            file_data = pd.DataFrame()

        # Run NextGen Query Algorithm
        _logger.info("Running NextGen patient query algorithm")
        data_with_ehr: pd.DataFrame
        query_results: dict[PatientDetails, PatientQueryResults] = {}
        if not file_data.empty:
            query_algo = cast(_NextGenQueryWorkerSide, query_algo)
            query_results = query_algo.run(
                query_algo.dataframe_to_patient_details(file_data)
            )
            data_with_ehr = query_algo.merge_results_with_dataframe(
                query_results,
                file_data,
            )
        else:
            _logger.warning(
                "No file data was extracted. No queries to EHR will be made."
            )
            data_with_ehr = pd.DataFrame()
        _logger.info(
            f"NextGen query algorithm completed: {len(query_results)} records found"
        )

        # Send empty results to modeller to move to next algorithm
        await self.mailbox.send_evaluation_results({})

        # Generate CSV Report
        _logger.info("Generating CSV report")
        if not data_with_ehr.empty:
            csv_output_algo = cast(_CSVWorkerSide, csv_output_algo)
            csv_output_algo.run(
                df=data_with_ehr,
                task_id=self._task_id,
            )
        else:
            _logger.warning(
                "No new data was extracted. Nothing will be written to CSV."
            )
        _logger.info("CSV report generation completed")

        # Send empty results to modeller to indicate completion
        await self.mailbox.send_evaluation_results({})
        _logger.info("Worker side of the protocol completed")

        return data_with_ehr


class NextGenSearchProtocol(BaseProtocolFactory):
    """Protocol for querying NextGen EHR data and generating CSV reports."""

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "rename_columns": fields.Dict(
            keys=fields.Str(), values=fields.Str(), allow_none=True
        ),
    }

    def __init__(
        self,
        *,
        algorithm: Sequence[
            RecordFilterAlgorithm | EHRPatientQueryAlgorithm | _SimpleCSVAlgorithm
        ],
        rename_columns: Optional[Mapping[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the protocol.

        Args:
            algorithm: Sequence containing NextGen query and CSV report algorithms
            rename_columns: Optional mapping of columns to rename in output
            **kwargs: Additional keyword arguments
        """
        super().__init__(algorithm=algorithm, **kwargs)
        self.rename_columns = rename_columns

    @classmethod
    def _validate_algorithm(cls, algorithm: BaseCompatibleAlgoFactory) -> None:
        """Validates the algorithms assigned to this protocol."""
        if algorithm.class_name not in (
            "bitfount.RecordFilterAlgorithm",
            "bitfount.EHRPatientQueryAlgorithm",
            "bitfount._SimpleCSVAlgorithm",
        ):
            raise TypeError(
                f"The {cls.__name__} protocol does not support "
                + f"the {type(algorithm).__name__} algorithm.",
            )

    def modeller(self, mailbox: _ModellerMailbox, **kwargs: Any) -> _ModellerSide:
        """Returns the Modeller side of the NextGenSearchProtocol protocol."""
        algorithms = cast(
            Sequence[
                RecordFilterAlgorithm | EHRPatientQueryAlgorithm | _SimpleCSVAlgorithm
            ],
            self.algorithms,
        )
        modeller_algos = []
        for algo in algorithms:
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
        """Returns worker side of the NextGenSearchProtocol protocol.

        Args:
            mailbox: Worker mailbox instance to allow communication to the modeller.
            hub: `BitfountHub` object to use for communication with the hub.
            context: Optional. Run-time protocol context details for running.
            **kwargs: Additional keyword arguments.
        """
        algorithms = cast(
            Sequence[
                RecordFilterAlgorithm | EHRPatientQueryAlgorithm | _SimpleCSVAlgorithm
            ],
            self.algorithms,
        )
        return _WorkerSide(
            algorithm=[algo.worker(hub=hub, context=context) for algo in algorithms],
            mailbox=mailbox,
            rename_columns=self.rename_columns,
            **kwargs,
        )
