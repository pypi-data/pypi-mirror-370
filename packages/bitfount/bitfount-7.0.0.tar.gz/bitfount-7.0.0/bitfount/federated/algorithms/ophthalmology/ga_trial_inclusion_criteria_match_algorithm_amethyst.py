"""Algorithm for establishing number of results that match a given criteria."""

from __future__ import annotations

import hashlib
from typing import Any

import pandas as pd

from bitfount.federated.algorithms.ophthalmology.ga_trial_inclusion_criteria_match_algorithm_base import (  # noqa: E501
    BaseGATrialInclusionAlgorithmFactorySingleEye,
    BaseGATrialInclusionWorkerAlgorithmSingleEye,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    NAME_COL,
)
from bitfount.federated.algorithms.ophthalmology.trial_inclusion_filters import (
    ColumnFilter,
)
from bitfount.federated.logging import _get_federated_logger

logger = _get_federated_logger("bitfount.federated")

# This algorithm is designed to find patients that match a set of clinical criteria.
# The criteria are as follows:
# 1. Total GA area between TOTAL_GA_AREA_LOWER_BOUND and TOTAL_GA_AREA_UPPER_BOUND
# 2. Largest GA lesion size greater than LARGEST_GA_LESION_LOWER_BOUND
# 3. No CNV (CNV probability less than CNV_THRESHOLD)


class _WorkerSide(BaseGATrialInclusionWorkerAlgorithmSingleEye):
    """Worker side of the algorithm."""

    def get_column_filters(self) -> list[ColumnFilter]:
        """Returns the column filters for the algorithm.

        Returns a list of ColumnFilter objects that specify the filters for the
        columns that the algorithm is interested in.
        """
        return self.get_base_column_filters()

    def _filter_by_criteria(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter the dataframe based on the clinical criteria."""
        # Establish which rows fit all the criteria
        match_rows: list[pd.Series] = []
        for _idx, row in df.iterrows():
            # TODO: [NO_TICKET: Imported from ophthalmology] Do we need a better way
            #       of identifying this?
            patient_name: str = str(row[NAME_COL])
            patient_name_hash: str = hashlib.md5(patient_name.encode()).hexdigest()  # nosec[blacklist] # Reason: this is not a security use case

            # Apply common criteria
            if not self._apply_common_criteria(row, patient_name_hash):
                continue

            # If we reach here, all criteria have been matched
            logger.debug(f"Patient {patient_name_hash} included: matches all criteria")
            match_rows.append(row)

        # Create new dataframe from the matched rows
        return pd.DataFrame(match_rows)


class TrialInclusionCriteriaMatchAlgorithmAmethyst(
    BaseGATrialInclusionAlgorithmFactorySingleEye
):
    """Algorithm for establishing number of patients that match clinical criteria."""

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Worker-side of the algorithm."""
        return _WorkerSide(
            cnv_threshold=self.cnv_threshold,
            largest_ga_lesion_lower_bound=self.largest_ga_lesion_lower_bound,
            largest_ga_lesion_upper_bound=self.largest_ga_lesion_upper_bound,
            total_ga_area_lower_bound=self.total_ga_area_lower_bound,
            total_ga_area_upper_bound=self.total_ga_area_upper_bound,
            patient_age_lower_bound=self.patient_age_lower_bound,
            patient_age_upper_bound=self.patient_age_upper_bound,
            **kwargs,
        )
