"""Algorithm for establishing number of results that match a given criteria."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

import pandas as pd

from bitfount.federated.algorithms.base import (
    NoResultsModellerAlgorithm,
)
from bitfount.federated.algorithms.ophthalmology.ga_trial_inclusion_criteria_match_algorithm_base import (  # noqa: E501
    BaseGATrialInclusionAlgorithmFactoryBothEyes,
    BaseGATrialInclusionWorkerAlgorithmBothEyes,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    CNV_THRESHOLD,
    ELIGIBILE_VALUE,
    ELIGIBILITY_COL,
    FILTER_MATCHING_COLUMN,
    LARGEST_GA_LESION_LOWER_BOUND,
    TOTAL_GA_AREA_LOWER_BOUND,
    TOTAL_GA_AREA_UPPER_BOUND,
)
from bitfount.federated.algorithms.ophthalmology.trial_inclusion_filters import (
    ColumnFilter,
)
from bitfount.federated.exceptions import AlgorithmError
from bitfount.federated.logging import _get_federated_logger
from bitfount.utils.logging_utils import deprecated_class_name

if TYPE_CHECKING:
    pass


# Age constants
PATIENT_AGE_LOWER_BOUND_JADE = 60

logger = _get_federated_logger("bitfount.federated")
# This algorithm is designed to find patients that match a set of clinical criteria.
# The criteria are as follows:
# 1. There are scans for both eyes for the same patient,
#   taken within 24 hours of each other
# 2. Age greater than or equal to PATIENT_AGE_LOWER_BOUND_JADE
# 3. Total GA area between TOTAL_GA_AREA_LOWER_BOUND and TOTAL_GA_AREA_UPPER_BOUND
# 4. Largest GA lesion size greater than LARGEST_GA_LESION_LOWER_BOUND
# 5. No CNV in either eye (CNV probability less than CNV_THRESHOLD)


class _WorkerSide(BaseGATrialInclusionWorkerAlgorithmBothEyes):
    """Worker side of the algorithm."""

    def __init__(
        self,
        *,
        cnv_threshold: float = CNV_THRESHOLD,
        largest_ga_lesion_lower_bound: float = LARGEST_GA_LESION_LOWER_BOUND,
        largest_ga_lesion_upper_bound: Optional[float] = None,
        total_ga_area_lower_bound: float = TOTAL_GA_AREA_LOWER_BOUND,
        total_ga_area_upper_bound: float = TOTAL_GA_AREA_UPPER_BOUND,
        patient_age_lower_bound: Optional[int] = None,
        patient_age_upper_bound: Optional[int] = None,
        renamed_columns: Optional[Mapping[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        if patient_age_upper_bound is not None:
            logger.warning(
                f"Charcoal algorithm explicitly sets patient_age_lower_bound;"
                f" received value of {patient_age_lower_bound}."
                f" Using {PATIENT_AGE_LOWER_BOUND_JADE} instead."
            )
        super().__init__(
            cnv_threshold=cnv_threshold,
            largest_ga_lesion_lower_bound=largest_ga_lesion_lower_bound,
            largest_ga_lesion_upper_bound=largest_ga_lesion_upper_bound,
            total_ga_area_lower_bound=total_ga_area_lower_bound,
            total_ga_area_upper_bound=total_ga_area_upper_bound,
            # Explicitly overriden
            patient_age_lower_bound=PATIENT_AGE_LOWER_BOUND_JADE,
            patient_age_upper_bound=patient_age_upper_bound,
            renamed_columns=renamed_columns,
            **kwargs,
        )

        self._paired_col_prefixes.append(FILTER_MATCHING_COLUMN)

    def get_column_filters(self) -> list[ColumnFilter]:
        """Returns the column filters for the algorithm.

        Returns a list of ColumnFilter objects that specify the filters for the
        columns that the algorithm is interested in. This is used to filter other
        algorithms using the same filters.
        """
        return self.get_base_column_filters()

    def run(
        self,
        matched_csv_path: Path,
    ) -> tuple[int, int, int]:
        """Finds number of patients that match the clinical criteria.

        Args:
            matched_csv_path: The path to the CSV containing matched patient info.

        Returns:
            A tuple of counts of patients that match/don't match the clinical criteria.
            Tuple is of form (match criteria, exclude due to eye criteria,
            exclude due to age).
        """
        self.update_renamed_columns()

        # Get the dataframe from the CSV file
        df = self._get_df_for_criteria(matched_csv_path)

        # Calculate age from DoB
        df = self._add_age_col(df)

        # Get the number of patients for which we have scans for both eyes
        number_of_patients_matched_eyes_records = len(
            df[self.bitfount_patient_id].unique()
        )

        # number of patients for which the ophthalmology trial criteria has been met
        number_of_patients_with_matching_ophthalmology_criteria = len(
            df[df[ELIGIBILITY_COL] == ELIGIBILE_VALUE][
                self.bitfount_patient_id
            ].unique()
        )
        number_excluded_due_to_eye_criteria = (
            number_of_patients_matched_eyes_records
            - number_of_patients_with_matching_ophthalmology_criteria
        )

        matched_df = self._filter_by_criteria(df)

        if not matched_df.empty:
            num_patients_matching_all_criteria = len(
                matched_df[self.bitfount_patient_id].unique()
            )
        else:
            num_patients_matching_all_criteria = 0

        number_of_patients_excluded_due_to_age = (
            number_of_patients_with_matching_ophthalmology_criteria
            - num_patients_matching_all_criteria
        )

        return (
            num_patients_matching_all_criteria,
            number_excluded_due_to_eye_criteria,
            number_of_patients_excluded_due_to_age,
        )

    def _filter_by_criteria(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter the dataframe based on the clinical criteria."""
        if self._paired_cols is None:
            raise AlgorithmError(
                "self._paired_cols not populated"
                " when calling _filter_by_criteria"
                " in a Both Eyes trial inclusion algorithm."
            )

        # Establish which rows fit all the criteria
        match_rows: dict[str, pd.Series] = {}
        for _idx, row in df.iterrows():
            bitfount_patient_id: str = str(
                row[self._paired_cols[self.bitfount_patient_id]].iloc[0]
            )

            # Apply common criteria for both eyes algorithms
            if not self._apply_base_both_eyes_criteria(row, bitfount_patient_id):
                continue

            # Age >= 60
            age_entries = row[self._paired_cols[self.age_col]]
            if not (age_entries >= self.patient_age_lower_bound).any():
                logger.debug(f"Patient {bitfount_patient_id} excluded due to age")
                continue

            # If we reach here, all criteria have been matched
            logger.debug(
                f"Patient {bitfount_patient_id} included: matches all criteria"
            )

            # Keep the latest row for each patient
            existing_row = match_rows.get(bitfount_patient_id)
            existing_row_scan_date_entries = (
                existing_row[self._paired_cols[self.scan_date_col]]
                if existing_row is not None
                else None
            )
            new_row_scan_date_entries = row[self._paired_cols[self.scan_date_col]]
            # No need to parse Scan dates to date as with ISO timestamp strings
            # lexicographical order is equivalent to chronological order
            if (
                existing_row_scan_date_entries is None
                or (existing_row_scan_date_entries <= new_row_scan_date_entries).any()
            ):
                match_rows[bitfount_patient_id] = row

        # Create new dataframe from the matched rows
        return pd.DataFrame(match_rows.values())


class TrialInclusionCriteriaMatchAlgorithmJade(
    BaseGATrialInclusionAlgorithmFactoryBothEyes
):
    """Algorithm for establishing number of patients that match clinical criteria."""

    def modeller(self, **kwargs: Any) -> NoResultsModellerAlgorithm:
        """Modeller-side of the algorithm."""
        return NoResultsModellerAlgorithm(
            log_message="Running Trial Inclusion Criteria Match Algorithm",
            **kwargs,
        )

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Worker-side of the algorithm."""
        return _WorkerSide(renamed_columns=self.renamed_columns, **kwargs)


# Kept for backwards compatibility
@deprecated_class_name
class TrialInclusionCriteriaMatchAlgorithm(TrialInclusionCriteriaMatchAlgorithmJade):
    """Algorithm for establishing number of patients that match clinical criteria."""

    pass
