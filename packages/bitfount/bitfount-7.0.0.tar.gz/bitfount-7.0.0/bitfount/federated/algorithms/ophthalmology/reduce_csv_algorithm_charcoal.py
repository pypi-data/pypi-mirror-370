"""Algorithms and related functionality for simply outputting data to CSV."""

from __future__ import annotations

from functools import partial
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Union

from marshmallow import fields
import pandas as pd

from bitfount import config
from bitfount.data.datasources.base_source import (
    BaseSource,
)
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.federated.algorithms.base import (
    BaseNonModelAlgorithmFactory,
    BaseWorkerAlgorithm,
    NoResultsModellerAlgorithm,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    _BITFOUNT_PATIENT_ID_KEY,
    ADDRESS_COL,
    AGE_COL,
    CELL_NUMBER_COL,
    DOB_COL,
    EMAIL_COL,
    FILTER_FAILED_REASON_COLUMN,
    FILTER_MATCHING_COLUMN,
    GENDER_COL,
    HOME_NUMBER_COL,
    LATERALITY_COL,
    LATEST_PRACTITIONER_NAME_COL,
    MRN_COL,
    NAME_COL,
    NEXT_APPOINTMENT_COL,
    PREV_APPOINTMENTS_COL,
    SUBFOVEAL_COL,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.types import T_FIELDS_DICT
from bitfount.utils.fs_utils import safe_write_to_file

if TYPE_CHECKING:
    from bitfount.federated.privacy.differential import DPPodConfig


_logger = _get_federated_logger("bitfount.federated")


REDUCE_CSV_ALGORITHM_CHARCOAL_COLUMNS = [
    "Left Eye Scan Details",
    "Right Eye Scan Details",
    "Latest Left Scan Filename",
    "Latest Right Scan Filename",
    "Latest Left Scan Exclusion Reason",
    "Latest Right Scan Exclusion Reason",
    "Scanned Files",
    "Number of scans",
    "Patient Eligible",
]


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side of the ReduceCSVAlgorithmCharcoal algorithm."""

    def __init__(
        self,
        save_path: Path,
        **kwargs: Any,
    ) -> None:
        """Create a new worker side of the _SimpleCSVAlgorithm algorithm.

        Args:
            save_path: The path to a directory to output the CSV to from the worker.
            **kwargs: Passed to parent.
        """
        super().__init__(**kwargs)
        self.save_path = save_path

    def initialise(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Sets Datasource."""
        self.initialise_data(datasource=datasource, data_splitter=data_splitter)

    def run(
        self,
        task_id: Optional[str] = None,
    ) -> None:
        """Reads previous CSV output and reduces it to one-row-per-patient."""
        if task_id is not None:
            csv_path = self.save_path / task_id / "results.csv"
            output_csv_path = self.save_path / task_id / "final_results.csv"
        else:
            Path(self.save_path).mkdir(parents=True, exist_ok=True)
            csv_path = self.save_path / "results.csv"
            output_csv_path = self.save_path / "final_results.csv"

        if not os.path.exists(csv_path):
            _logger.warning(
                f"File not found at {csv_path}, aborting ReduceCSVAlgorithmCharcoal"
            )
            return

        _logger.info(f"Reading intermediate results CSV at {csv_path}.")

        df = pd.read_csv(csv_path)

        df = self._reduce_df(df)

        # Write the final dataframe to CSV
        _, output_csv_path = safe_write_to_file(
            partial(df.to_csv, mode="w", header=True, index=True, na_rep="N/A"),
            output_csv_path,
        )
        _logger.info(f"Reduced (final) CSV output to {output_csv_path}")

    def _reduce_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reduces dataframe from one-row-per-scan to one-row-per-patient."""
        date_sorted_df = df.sort_values("Acquisition DateTime")
        grouped = date_sorted_df.groupby(_BITFOUNT_PATIENT_ID_KEY)

        results_df = pd.DataFrame()
        results_df["Number of scans"] = grouped[NAME_COL].count()

        # All EHR columns would have the same value for all rows of a patient
        EHR_COLS = [
            NAME_COL,
            DOB_COL,
            AGE_COL,
            GENDER_COL,
            HOME_NUMBER_COL,
            CELL_NUMBER_COL,
            EMAIL_COL,
            ADDRESS_COL,
            MRN_COL,
            NEXT_APPOINTMENT_COL,
            PREV_APPOINTMENTS_COL,
            LATEST_PRACTITIONER_NAME_COL,
        ]
        results_df = results_df.join(grouped.first()[EHR_COLS])

        # Display the names of files we've looked at
        results_df["Scanned Files"] = grouped[ORIGINAL_FILENAME_METADATA_COLUMN].apply(
            ", ".join
        )

        most_recent_scan_per_patient_lat = (
            date_sorted_df.groupby([_BITFOUNT_PATIENT_ID_KEY, LATERALITY_COL])
            .tail(1)
            .set_index("BitfountPatientID")
        )

        # Provide details about most recent Left scan
        left_results = most_recent_scan_per_patient_lat[
            most_recent_scan_per_patient_lat[LATERALITY_COL].apply(
                lambda lat: lat.lower() in ("l", "left")
            )
        ]
        left_results["Left Eye Scan Details"] = left_results.apply(
            self._format_scan_details,
            axis=1,
        )
        # Provide details about most recent Right scan
        right_results = most_recent_scan_per_patient_lat[
            most_recent_scan_per_patient_lat[LATERALITY_COL].apply(
                lambda lat: lat.lower() in ("r", "right")
            )
        ]

        right_results["Right Eye Scan Details"] = right_results.apply(
            self._format_scan_details,
            axis=1,
        )

        results_df = results_df.join(left_results["Left Eye Scan Details"])
        results_df["Latest Left Scan Filename"] = left_results["_original_filename"]
        results_df["Latest Left Scan Exclusion Reason"] = left_results[
            FILTER_FAILED_REASON_COLUMN
        ]

        results_df = results_df.join(right_results["Right Eye Scan Details"])
        results_df["Latest Right Scan Filename"] = right_results["_original_filename"]
        results_df["Latest Right Scan Exclusion Reason"] = right_results[
            FILTER_FAILED_REASON_COLUMN
        ]

        # Eligibility column - Patient is only eligible if most recent scan says so
        results_df["Patient Eligible"] = most_recent_scan_per_patient_lat.groupby(
            _BITFOUNT_PATIENT_ID_KEY
        )[FILTER_MATCHING_COLUMN].any()

        return results_df.fillna("Not Applicable")

    def _format_scan_details(self, row: pd.Series) -> str:
        """Formats GA metrics into a readable string."""
        subfov_str = ""
        if row[SUBFOVEAL_COL] == "N":
            subfov_str = " Subfoveal lesion not detected,"
        elif row[SUBFOVEAL_COL] == "Y":
            subfov_str = " Subfoveal lesion detected,"
        elif row[SUBFOVEAL_COL] == "Fovea not detected":
            subfov_str = " Fovea not detected,"

        scan_details = (
            f"Latest Scan on {row['Acquisition DateTime']}"
            f" detected {row['total_ga_area']} mm2 area of GA,{subfov_str}"
            f" max cnv probability: {row['max_cnv_probability']},"
            f" max hard drusen probability: {row['max_hard_drusen_probability']},"
            f" max soft drusen probability: {row['max_soft_drusen_probability']},"
            f" max confluent drusen probability:"
            f" {row['max_confluent_drusen_probability']}"
        )

        return scan_details


class ReduceCSVAlgorithmCharcoal(
    BaseNonModelAlgorithmFactory[NoResultsModellerAlgorithm, _WorkerSide]
):
    """Algorithm that reduces Charcoal CSV results to one-row-per-patient.

    Args:
        datastructure: The datastructure to use.
        save_path: Optional. The path to save the CSV to from the worker.
        **kwargs: Passed to parent.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "save_path": fields.Str(allow_none=True),
    }

    def __init__(
        self,
        datastructure: DataStructure,
        save_path: Optional[Union[str, os.PathLike]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(datastructure=datastructure, **kwargs)

        self.save_path: Path
        if save_path is None:
            self.save_path = config.settings.paths.output_dir
        else:
            self.save_path = Path(save_path)

        # Sanity check if nothing was supplied
        if not self.save_path:
            _logger.warning(
                f"Worker save path was not specified"
                f" for {self.__class__.__name__}, so nothing will be saved out."
                f" Was this intentional?"
            )

    def modeller(self, **kwargs: Any) -> NoResultsModellerAlgorithm:
        """Modeller-side of the ReduceCSVAlgorithmCharcoal algorithm."""
        return NoResultsModellerAlgorithm(
            log_message="Running Reduce CSV Algorithm",
            **kwargs,
        )

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Worker-side of the ReduceCSVAlgorithmCharcoal algorithm."""
        return _WorkerSide(
            self.save_path,
            **kwargs,
        )
