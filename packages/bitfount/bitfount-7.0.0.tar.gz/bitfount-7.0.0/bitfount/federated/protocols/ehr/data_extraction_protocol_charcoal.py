"""EHR Data Extraction protocol for Charcoal project.

Retrieves EHR JSON data and documents to dump to a location.
"""

from __future__ import annotations

from collections.abc import Sequence
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Union, cast

from marshmallow import fields
import torch

from bitfount import config
from bitfount.federated.algorithms.base import NoResultsModellerAlgorithm
from bitfount.federated.algorithms.ehr.nextgen_patient_info_download_algorithm import (
    NextGenPatientInfoDownloadAlgorithm,
    _WorkerSide as _DownloadAlgoWorkerSide,
)
from bitfount.federated.authorisation_checkers import ProtocolContext
from bitfount.federated.exceptions import ProtocolError
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.protocols.base import (
    BaseCompatibleAlgoFactory,
    BaseModellerProtocol,
    BaseProtocolFactory,
    BaseWorkerProtocol,
    ModelInferenceProtocolMixin,
)
from bitfount.federated.transport.message_service import (
    _BitfountMessageType,
)
from bitfount.federated.transport.modeller_transport import _ModellerMailbox
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.types import T_FIELDS_DICT

if TYPE_CHECKING:
    from bitfount.federated.pod_vitals import _PodVitals
    from bitfount.hub.api import BitfountHub

_logger = _get_federated_logger(f"bitfount.federated.protocols.{__name__}")


class _ModellerSide(BaseModellerProtocol):
    """Modeller side of the data extraction protocol for Charcoal project.

    Patient IDs can either be supplied as an explicit list of patient IDs or as a
    path to a file which contains one patient ID per line. These two options are
    mutually exclusive from each other.

    Args:
        algorithm: The sequence of algorithms to be used. On the modeller side these
            will be noop algorithms.
        mailbox: The mailbox to use for communication with the Workers.
        patient_ids: List of patient ID strings. Mutually exclusive with
            `patient_ids_file`.
        patient_ids_file: Path to file containing patient ID strings, one per line.
            Mutually exclusive with `patient_ids`.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[NoResultsModellerAlgorithm]

    def __init__(
        self,
        *,
        algorithm: Sequence[NoResultsModellerAlgorithm],
        mailbox: _ModellerMailbox,
        patient_ids: Optional[list[str]] = None,
        patient_ids_file: Optional[os.PathLike | str] = None,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

        # Check that we have only one of `patient_ids` and `patient_ids_file`
        if patient_ids is not None and patient_ids_file is not None:
            _logger.error(
                "Cannot have both `patient_ids` and `patient_ids_file`,"
                " please supply only one option."
            )
            raise ProtocolError(
                "Cannot have both `patient_ids` and `patient_ids_file`"
                " in DataExtractionProtocolCharcoal modeller side,"
                " please supply only one option."
            )
        if patient_ids is None and patient_ids_file is None:
            _logger.error(
                "Must have one of `patient_ids` and `patient_ids_file`,"
                " please supply one option."
            )
            raise ProtocolError(
                "Must have one of `patient_ids` and `patient_ids_file`,"
                " in DataExtractionProtocolCharcoal modeller side,"
                " please supply one option."
            )

        self._patient_ids: list[str]
        if patient_ids is not None:
            self._patient_ids = patient_ids
        else:  # patient_ids_file is not None
            # Checks above should ensure, but check again
            if patient_ids_file is None:
                raise ValueError(f"{patient_ids_file=}. Previous checks have failed.")
            self._patient_ids = self._extract_patient_ids_from_file(patient_ids_file)
        # Remove any duplicates
        self._patient_ids = list(set(self._patient_ids))

    @staticmethod
    def _extract_patient_ids_from_file(
        patient_ids_file: os.PathLike | str,
    ) -> list[str]:
        """Extract patient IDs from file.

        Expected format is one patient ID per line.
        """
        _logger.debug(f"Extracting patient IDs from {str(patient_ids_file)}")
        with open(patient_ids_file) as f:
            return f.read().splitlines()

    def initialise(
        self,
        task_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialises the component algorithms."""
        # DEV: Not currently used in this protocol (as no model algos) but protects
        #      for future case

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

        This just sends the patient IDs to the workers and then tells the workers
        when the protocol is finished.

        Args:
            context: Optional. Run-time context for the protocol.
            **kwargs: Additional keyword arguments.
        """
        results = []

        (download_info_algo,) = self.algorithm

        _logger.info(f"Running algorithm {download_info_algo.class_name}")

        _logger.info("Sending patient IDs to worker(s)")
        await self.mailbox._send_to_all_pods_aes_encrypt(
            self._patient_ids,
            # DEV: This is a bit of an abuse for the MODEL_PARAMETERS message type
            #      but it suits our purposes here even though it's not "model weights"
            _BitfountMessageType.MODEL_PARAMETERS,
        )
        _logger.info("Patient IDs sent to worker(s)")

        _logger.info("Waiting on worker(s) to process")
        result = await self.mailbox.get_evaluation_results_from_workers()
        results.append(result)
        _logger.info("Received results from Pods.")

        _logger.info(f"Algorithm {download_info_algo.class_name} completed.")

        final_results = [
            algo.run(result_)  # type: ignore[func-returns-value] # Reason: algos return None by design # noqa: E501
            for algo, result_ in zip(self.algorithm, results)
        ]

        return final_results


class _WorkerSide(BaseWorkerProtocol, ModelInferenceProtocolMixin):
    """Modeller side of the data extraction protocol for Charcoal project.

    Args:
        algorithm: The sequence data extraction algorithms to be used.
        mailbox: The mailbox to use for communication with the Modeller.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[_DownloadAlgoWorkerSide]

    def __init__(
        self,
        *,
        algorithm: Sequence[_DownloadAlgoWorkerSide],
        mailbox: _WorkerMailbox,
        output_dir: Path,
        trial_name: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

        self._task_id: Optional[str] = mailbox._task_id

        self.task_output_dir = (
            output_dir / self._task_id if self._task_id is not None else output_dir
        )
        self.task_output_dir.mkdir(parents=True, exist_ok=True)
        _logger.info(
            f"Created output directory for this algorithm run"
            f" as {str(self.task_output_dir)}"
        )

        self.trial_name = trial_name

    async def run(
        self,
        *,
        pod_vitals: Optional[_PodVitals] = None,
        context: Optional[ProtocolContext] = None,
        batch_num: Optional[int] = None,
        final_batch: bool = False,
        **kwargs: Any,
    ) -> None:
        """Runs worker side of data extraction protocol.

        Args:
            pod_vitals: Optional. Pod vitals instance for recording run-time details
                from the protocol run.
            context: Optional. Run-time context for the protocol.
            batch_num: The number of the batch being run.
            final_batch: If this run of the protocol represents the final run within
                a task.
            **kwargs: Additional keyword arguments.
        """
        (download_info_algo,) = self.algorithm

        # Wait for patient IDs
        _logger.info("Waiting for patient IDs from modeller")
        patient_ids: list[str] = await self.mailbox._get_message_and_decrypt(
            _BitfountMessageType.MODEL_PARAMETERS
        )
        _logger.info("Patient IDs received from modeller")

        # Loop through and dump for each patient
        num_patient_ids = len(patient_ids)
        _logger.info(
            f"Running algorithm {download_info_algo.class_name}"
            f" for {num_patient_ids} patients"
        )
        download_info_algo.run(
            patient_ids=patient_ids,
            download_path=self.task_output_dir,
            run_document_download=True,
            run_json_dump=True,
        )

        # Sends empty results to modeller just to inform it to move on to the
        # next algorithm
        await self.mailbox.send_evaluation_results({})
        _logger.info(f"Algorithm {download_info_algo.class_name} completed.")


class DataExtractionProtocolCharcoal(BaseProtocolFactory):
    """Protocol for running EHR Data Extraction for Charcoal."""

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "trial_name": fields.Str(allow_none=True),
    }

    def __init__(
        self,
        *,
        patient_ids: Optional[list[str]] = None,
        patient_ids_file: Optional[os.PathLike | str] = None,
        algorithm: Sequence[NextGenPatientInfoDownloadAlgorithm],
        trial_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Data extraction protocol for Charcoal project.

        Patient IDs can either be supplied as an explicit list of patient IDs or as a
        path to a file which contains one patient ID per line. These two options are
        mutually exclusive from each other.

        Args:
            patient_ids: List of patient ID strings. Mutually exclusive with
                `patient_ids_file`.
            patient_ids_file: Path to file containing patient ID strings, one per line.
                Mutually exclusive with `patient_ids`.
            algorithm: The sequence of algorithms to be used. On the modeller side these
                will be noop algorithms.
            trial_name: Name of the trial.
            **kwargs: Additional keyword arguments.
        """
        # TODO: [BIT-5727] Need to ensure that `batched_execution` and
        #       `run_on_new_data_only` are both `False` when using this protocol, but
        #       think those args are only exposed at the _Worker/Modeller-level. Might
        #       have to just be explicit in templates using this protocol.
        super().__init__(algorithm=algorithm, **kwargs)

        self.trial_name = trial_name

        # Check that we have only one of `patient_ids` and `patient_ids_file`
        if patient_ids is not None and patient_ids_file is not None:
            _logger.error(
                "Cannot have both `patient_ids` and `patient_ids_file`,"
                " please supply only one option."
            )
            raise ProtocolError(
                "Cannot have both `patient_ids` and `patient_ids_file`"
                " in DataExtractionProtocolCharcoal modeller side,"
                " please supply only one option."
            )
        if patient_ids is None and patient_ids_file is None:
            _logger.error(
                "Must have one of `patient_ids` and `patient_ids_file`,"
                " please supply one option."
            )
            raise ProtocolError(
                "Must have one of `patient_ids` and `patient_ids_file`,"
                " in DataExtractionProtocolCharcoal modeller side,"
                " please supply one option."
            )

        self.patient_ids = patient_ids
        self.patient_ids_file = patient_ids_file

    @classmethod
    def _validate_algorithm(cls, algorithm: BaseCompatibleAlgoFactory) -> None:
        """Validates the algorithms by ensuring they are compatible types.

        For this protocol these are:
            - NextGenPatientInfoDownloadAlgorithm
        """
        if algorithm.class_name not in (
            "bitfount.NextGenPatientInfoDownloadAlgorithm",
        ):
            raise TypeError(
                f"The {cls.__name__} protocol does not support "
                + f"the {type(algorithm).__name__} algorithm.",
            )

    def modeller(self, mailbox: _ModellerMailbox, **kwargs: Any) -> _ModellerSide:
        """Returns the Modeller side of the protocol."""
        algorithms = cast(
            Sequence[NextGenPatientInfoDownloadAlgorithm],
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
            patient_ids=self.patient_ids,
            patient_ids_file=self.patient_ids_file,
            **kwargs,
        )

    def worker(
        self,
        mailbox: _WorkerMailbox,
        hub: BitfountHub,
        context: Optional[ProtocolContext] = None,
        **kwargs: Any,
    ) -> _WorkerSide:
        """Returns worker side of the DataExtractionProtocolCharcoal protocol.

        Args:
            mailbox: Worker mailbox instance to allow communication to the modeller.
            hub: `BitfountHub` object to use for communication with the hub.
            context: Optional. Run-time protocol context details for running.
            **kwargs: Additional keyword arguments.
        """
        algorithms = cast(
            Sequence[NextGenPatientInfoDownloadAlgorithm],
            self.algorithms,
        )

        # TODO: [BIT-5728] Potentially need to find a way to feed the normal task run
        #       output dir through to here? Difficult because this Protocol will be
        #       running on remote pods so cannot guarantee save path on pod; our
        #       existing "save_path" options are all concerned with same-machine
        #       running.
        output_dir = config.settings.paths.output_dir
        _logger.info(
            f"Setting worker side output directory for {self.class_name}"
            f" to {str(output_dir)}"
        )

        return _WorkerSide(
            algorithm=[algo.worker(hub=hub, context=context) for algo in algorithms],
            mailbox=mailbox,
            output_dir=output_dir,
            trial_name=self.trial_name,
            **kwargs,
        )
