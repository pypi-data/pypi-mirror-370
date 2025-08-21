"""Algorithm for establishing number of results that match a given criteria."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Any, ClassVar, Mapping, Optional

from marshmallow import fields
import pandas as pd

from bitfount.data.datastructure import DataStructure
from bitfount.federated.algorithms.ophthalmology.ga_trial_inclusion_criteria_match_algorithm_base import (  # noqa: E501
    BaseGATrialInclusionAlgorithmFactorySingleEye,
    BaseGATrialInclusionWorkerAlgorithmSingleEye,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    CNV_THRESHOLD,
    DISTANCE_FROM_FOVEA_CENTRE_COL,
    DISTANCE_FROM_FOVEA_LOWER_BOUND,
    DISTANCE_FROM_FOVEA_UPPER_BOUND,
    EXCLUDE_FOVEAL_GA,
    LARGEST_GA_LESION_LOWER_BOUND,
    NAME_COL,
    TOTAL_GA_AREA_LOWER_BOUND,
    TOTAL_GA_AREA_UPPER_BOUND,
)
from bitfount.federated.algorithms.ophthalmology.trial_inclusion_filters import (
    ColumnFilter,
)
from bitfount.federated.logging import _get_federated_logger

if TYPE_CHECKING:
    from bitfount.types import T_FIELDS_DICT


logger = _get_federated_logger("bitfount.federated")

# This algorithm is designed to find patients that match a set of clinical criteria.
# The criteria are as follows:
# 1. Total GA area between TOTAL_GA_AREA_LOWER_BOUND and TOTAL_GA_AREA_UPPER_BOUND
# 2. Largest GA lesion size greater than LARGEST_GA_LESION_LOWER_BOUND
# 3. No CNV (CNV probability less than CNV_THRESHOLD)
# 4. Distance from fovea centre less than DISTANCE_FROM_FOVEA_UPPER_BOUND
# 5. GA does not cross the fovea centre (if EXCLUDE_FOVEAL_GA is True)


class _WorkerSide(BaseGATrialInclusionWorkerAlgorithmSingleEye):
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
        distance_from_fovea_lower_bound: float = DISTANCE_FROM_FOVEA_LOWER_BOUND,
        distance_from_fovea_upper_bound: float = DISTANCE_FROM_FOVEA_UPPER_BOUND,
        exclude_foveal_ga: bool = EXCLUDE_FOVEAL_GA,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            cnv_threshold=cnv_threshold,
            largest_ga_lesion_lower_bound=largest_ga_lesion_lower_bound,
            largest_ga_lesion_upper_bound=largest_ga_lesion_upper_bound,
            total_ga_area_lower_bound=total_ga_area_lower_bound,
            total_ga_area_upper_bound=total_ga_area_upper_bound,
            patient_age_lower_bound=patient_age_lower_bound,
            patient_age_upper_bound=patient_age_upper_bound,
            renamed_columns=renamed_columns,
            **kwargs,
        )
        self.distance_from_fovea_lower_bound = distance_from_fovea_lower_bound
        self.distance_from_fovea_upper_bound = distance_from_fovea_upper_bound
        self.exclude_foveal_ga = exclude_foveal_ga

    def get_column_filters(self) -> list[ColumnFilter]:
        """Returns the column filters for the algorithm.

        Returns a list of ColumnFilter objects that specify the filters for the
        columns that the algorithm is interested in. This is used to filter other
        algorithms using the same filters.
        """
        base_filters = self.get_base_column_filters()
        bronze_specific_filters = [
            ColumnFilter(
                column=DISTANCE_FROM_FOVEA_CENTRE_COL,
                operator=">=",
                value=self.distance_from_fovea_lower_bound,
            ),
            ColumnFilter(
                column=DISTANCE_FROM_FOVEA_CENTRE_COL,
                operator="<=",
                value=self.distance_from_fovea_upper_bound,
            ),
        ]

        if self.exclude_foveal_ga:
            bronze_specific_filters.append(
                ColumnFilter(
                    column=DISTANCE_FROM_FOVEA_CENTRE_COL,
                    operator="not equal",
                    value=0.0,
                )
            )

        return base_filters + bronze_specific_filters

    def _filter_by_criteria(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter the dataframe based on the clinical criteria."""
        # Establish which rows fit all the criteria
        match_rows: list[pd.Series] = []
        for _idx, row in df.iterrows():
            # TODO: [NO_TICKET: Imported from ophthalmology] Do we need a better way
            #       of identifying this?
            patient_name: str = str(row[NAME_COL])
            patient_name_hash: str = hashlib.md5(patient_name.encode()).hexdigest()  # nosec[blacklist] # Reason: this is not a security use case
            # Apply common criteria from base class
            if not self._apply_common_criteria(row, patient_name_hash):
                continue

            # Apply Bronze-specific criteria
            # Distance from fovea < 1.5mm
            # If distance from fovea is not available, use distance from center
            distance_entry = row[DISTANCE_FROM_FOVEA_CENTRE_COL]
            if not (
                (distance_entry >= self.distance_from_fovea_lower_bound)
                & (distance_entry <= self.distance_from_fovea_upper_bound)
            ):
                logger.debug(
                    f"Patient {patient_name_hash} excluded due to"
                    f" distance from fovea being out of bounds"
                )
                continue

            # Exclude foveal GA if required
            if self.exclude_foveal_ga and distance_entry == 0.0:
                logger.debug(
                    f"Patient {patient_name_hash} excluded due to"
                    f" foveal GA being present"
                )
                continue

            # If we reach here, all criteria have been matched
            logger.debug(f"Patient {patient_name_hash} included: matches all criteria")
            match_rows.append(row)

        # Create new dataframe from the matched rows
        return pd.DataFrame(match_rows)


class TrialInclusionCriteriaMatchAlgorithmBronze(
    BaseGATrialInclusionAlgorithmFactorySingleEye
):
    """Algorithm for establishing number of patients that match clinical criteria."""

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "distance_from_fovea_lower_bound": fields.Float(allow_none=True),
        "distance_from_fovea_upper_bound": fields.Float(allow_none=True),
        "exclude_foveal_ga": fields.Boolean(allow_none=True),
    }

    def __init__(
        self,
        datastructure: DataStructure,
        cnv_threshold: float = CNV_THRESHOLD,
        largest_ga_lesion_lower_bound: float = LARGEST_GA_LESION_LOWER_BOUND,
        largest_ga_lesion_upper_bound: Optional[float] = None,
        total_ga_area_lower_bound: float = TOTAL_GA_AREA_LOWER_BOUND,
        total_ga_area_upper_bound: float = TOTAL_GA_AREA_UPPER_BOUND,
        patient_age_lower_bound: Optional[int] = None,
        patient_age_upper_bound: Optional[int] = None,
        distance_from_fovea_lower_bound: float = DISTANCE_FROM_FOVEA_LOWER_BOUND,
        distance_from_fovea_upper_bound: float = DISTANCE_FROM_FOVEA_UPPER_BOUND,
        exclude_foveal_ga: bool = EXCLUDE_FOVEAL_GA,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            datastructure=datastructure,
            cnv_threshold=cnv_threshold,
            largest_ga_lesion_lower_bound=largest_ga_lesion_lower_bound,
            largest_ga_lesion_upper_bound=largest_ga_lesion_upper_bound,
            total_ga_area_lower_bound=total_ga_area_lower_bound,
            total_ga_area_upper_bound=total_ga_area_upper_bound,
            patient_age_lower_bound=patient_age_lower_bound,
            patient_age_upper_bound=patient_age_upper_bound,
            **kwargs,
        )
        self.distance_from_fovea_lower_bound = distance_from_fovea_lower_bound
        self.distance_from_fovea_upper_bound = distance_from_fovea_upper_bound
        self.exclude_foveal_ga = exclude_foveal_ga

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
            distance_from_fovea_lower_bound=self.distance_from_fovea_lower_bound,
            distance_from_fovea_upper_bound=self.distance_from_fovea_upper_bound,
            exclude_foveal_ga=self.exclude_foveal_ga,
            **kwargs,
        )
