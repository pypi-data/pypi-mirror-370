"""Algorithm for establishing number of results that match a given criteria."""

from __future__ import annotations

from datetime import date, datetime
import re
from typing import TYPE_CHECKING, Any, ClassVar, Counter, Mapping, Optional

from dateutil.relativedelta import relativedelta
from marshmallow import fields
import pandas as pd

from bitfount.externals.ehr.types import DATE_STR_FORMAT
from bitfount.federated.algorithms.ophthalmology.ga_trial_inclusion_criteria_match_algorithm_base import (  # noqa: E501
    BaseGATrialInclusionAlgorithmFactorySingleEye,
    BaseGATrialInclusionWorkerAlgorithmSingleEye,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    AGE_COL,
    CNV_THRESHOLD,
    CPT4_COLUMN,
    FILTER_FAILED_REASON_COLUMN,
    ICD10_COLUMN,
    LARGEST_GA_LESION_LOWER_BOUND,
    MAX_CNV_PROBABILITY_COL_PREFIX,
    PREV_APPOINTMENTS_COL,
    TOTAL_GA_AREA_COL_PREFIX,
    TOTAL_GA_AREA_LOWER_BOUND,
    TOTAL_GA_AREA_UPPER_BOUND,
)
from bitfount.federated.algorithms.ophthalmology.trial_inclusion_filters import (
    ColumnFilter,
    MethodFilter,
)
from bitfount.federated.logging import _get_federated_logger

if TYPE_CHECKING:
    from bitfount.types import T_FIELDS_DICT


# Constrain on age of patient
# Allow for patients about to turn 50 in the next year
PATIENT_AGE_LOWER_BOUND_CHARCOAL = 50 - 1

# Constraint on minimum number of years of history = 3
# Allow for patients with slightly fewer years of history
YEARS_OF_APPOINTMENT_HISTORY: int = 2
MIN_APPOINTMENTS_PER_HISTORY_YEAR: int = 2

# Constraint on the recency of appointments to be considered a "current" patient
CURRENT_PATIENT_MONTHS_THRESHOLD: int = 12

CHARCOAL_INCLUDED_CONDITIONS: set[str] = {
    "H35.3112",  # Right: Intermediate Dry Stage
    "H35.3113",  # Right: Advanced Atrophic w/o Subfoveal Involvement
    "H35.3114",  # Right: Advanced Atrophic w/ Subfoveal Involvement
    "H35.3122",  # Left: Intermediate Dry Stage
    "H35.3123",  # Left: Advance Atrophic w/o Subfoveal Involvement
    "H35.3124",  # Left: Advance Atrophic w/ Subfoveal Involvement
    "H35.3132",  # BiLateral: Intermediate Dry Stage
    "H35.3133",  # BiLateral: Advance Atrophic w/o Subfoveal Involvement
    "H35.3134",  # BiLateral: Advance Atrophic w/ Subfoveal Involvement
}

logger = _get_federated_logger("bitfount.federated")


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
        conditions_inclusion_codes: Optional[list[str]] = None,
        conditions_exclusion_codes: Optional[list[str]] = None,
        procedures_exclusion_codes: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        if patient_age_lower_bound is not None:
            logger.warning(
                f"Charcoal algorithm explicitly sets patient_age_lower_bound;"
                f" received value of {patient_age_lower_bound}."
                f" Using {PATIENT_AGE_LOWER_BOUND_CHARCOAL} instead."
            )
        super().__init__(
            cnv_threshold=cnv_threshold,
            largest_ga_lesion_lower_bound=largest_ga_lesion_lower_bound,  # not used
            largest_ga_lesion_upper_bound=largest_ga_lesion_upper_bound,  # not used
            total_ga_area_lower_bound=total_ga_area_lower_bound,
            total_ga_area_upper_bound=total_ga_area_upper_bound,  # not used
            patient_age_lower_bound=PATIENT_AGE_LOWER_BOUND_CHARCOAL,  # Explicitly overridden  # noqa: E501
            patient_age_upper_bound=patient_age_upper_bound,
            renamed_columns=renamed_columns,
            **kwargs,
        )
        if conditions_inclusion_codes is not None:
            self.conditions_inclusion_codes: set[str] = set(conditions_inclusion_codes)
        else:
            logger.info(
                "Charcoal Trial Inclusion: no conditions inclusion codes"
                " provided. Using default AMD ICD10 codes for inclusion."
            )
            self.conditions_inclusion_codes = CHARCOAL_INCLUDED_CONDITIONS

        if procedures_exclusion_codes is not None:
            self.procedures_exclusion_codes: set[str] = set(procedures_exclusion_codes)
        else:
            logger.info(
                "Charcoal Trial Inclusion: no procedure exclusion codes"
                " provided. No procedure exclusion applied."
            )
            self.procedures_exclusion_codes = set()

        self._handle_exclusion_regex_codes(conditions_exclusion_codes)

    def _handle_exclusion_regex_codes(self, list_of_codes: Optional[list[str]]) -> None:
        """Handles list of exclusion codes with literal and regex values."""
        if list_of_codes is None:
            logger.info(
                "Charcoal Trial Inclusion: no conditions exclusion codes"
                " provided. No conditions exclusion applied."
            )
            self.conditions_excl_codes_literal = set()
            self.conditions_excl_regex_pattern = None
            return

        literal_codes = set()
        regex_codes = set()
        for code in list_of_codes:
            if "*" in code:
                escaped_code = code.replace(".", r"\.").replace("*", ".*")
                regex_codes.add(escaped_code)
            else:
                literal_codes.add(code)

        self.conditions_excl_codes_literal = literal_codes

        if regex_codes:
            self.conditions_excl_regex_pattern = re.compile("|".join(regex_codes))
        else:
            self.conditions_excl_regex_pattern = None

    # Note: The following method was renamed from run() as it returns a dataframe
    #     and hence has a different signature from the parent class
    def run_and_return_dataframe(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """Finds number of patients that match the clinical criteria.

        Args:
            dataframe: The dataframe to process.

        Returns:
            A tuple of counts of patients that match the clinical criteria.
            Tuple is of form (match criteria, don't match criteria).
        """
        if dataframe.empty:
            return dataframe

        dataframe = self._add_age_col(dataframe)
        dataframe = self._filter_by_criteria(dataframe)

        return dataframe

    def get_inclusion_filters(self) -> list[ColumnFilter | MethodFilter]:
        """Returns the inclusion filters for the algorithm.

        Returns a list of ColumnFilter or MethodFilter objects for filtering
        patients eligible for trial.

        This algorithm is designed to find patients that match the
        Charcoal clinical criteria.
        The criteria are as follows:
        1. No CNV (CNV probability less than CNV_THRESHOLD)
        2. Age greater than PATIENT_AGE_LOWER_BOUND_CHARCOAL
        3. Has diagnosis of Dry AMD OR
               Total GA area greater than TOTAL_GA_AREA_LOWER_BOUND
        4. Patient is not diagnosed with any of excluded conditions
        5. Patient has not had any of excluded procedures/medications
        6. Appointment history going back at least YEARS_OF_APPOINTMENT_HISTORY years
        """
        max_cnv_column = self._get_column_name(MAX_CNV_PROBABILITY_COL_PREFIX)

        # Note: We are not using self.get_base_column_filters here as it contains
        #     filters not required for charcoal

        return [
            ColumnFilter(
                column=max_cnv_column,
                operator="<=",
                value=self.cnv_threshold,
            ),
            ColumnFilter(
                column=AGE_COL,
                operator=">=",
                value=PATIENT_AGE_LOWER_BOUND_CHARCOAL,
            ),
            MethodFilter(
                method=self.diagnosis_filter,
                required_columns={TOTAL_GA_AREA_COL_PREFIX, ICD10_COLUMN},
                filter_name="MD detected in diagnosis or in scan",
                filter_failed_message="patient does not have"
                " diagnosis for macular degeneration",
            ),
            MethodFilter(
                method=self.excluded_conditions_filter,
                required_columns={ICD10_COLUMN},
                filter_name="Excluded Conditions",
                filter_failed_message="patient diagnosed with one of the"
                " excluded conditions",
            ),
            MethodFilter(
                method=self.excluded_procedures_filter,
                required_columns={CPT4_COLUMN},
                filter_name="Excluded Treatments",
                filter_failed_message="patient has had treatment that"
                " precludes them from the trial",
            ),
            MethodFilter(
                method=self.appointment_history_filter,
                required_columns={PREV_APPOINTMENTS_COL},
                filter_name=f">{YEARS_OF_APPOINTMENT_HISTORY} years"
                f" of appointment history",
                filter_failed_message="patient did not have sufficiently"
                " long history of macular degeneration",
            ),
            MethodFilter(
                method=self.is_current_patient,
                required_columns={PREV_APPOINTMENTS_COL},
                filter_name=(
                    f"Had appointment within last"
                    f" {CURRENT_PATIENT_MONTHS_THRESHOLD} months"
                ),
                filter_failed_message="patient is not a current patient",
            ),
        ]

    def diagnosis_filter(self, row: pd.Series) -> bool:
        """Filter to check patient diagnosis.

        Matches patient if EITHER:
          - Patient has a matching diagnosis code in inclusion list OR
          - Patient has GA detected in scan
        """
        # Any matching diagnosis code to conditions_inclusion_codes
        if (
            row[ICD10_COLUMN]
            and self.conditions_inclusion_codes
            and any(
                code in row[ICD10_COLUMN] for code in self.conditions_inclusion_codes
            )
        ):
            return True

        if row[TOTAL_GA_AREA_COL_PREFIX] is None:
            return False
        elif row[TOTAL_GA_AREA_COL_PREFIX] >= self.total_ga_area_lower_bound:
            return True

        return False

    def excluded_conditions_filter(self, row: pd.Series) -> bool:
        """Filter to exclude any disqualifying conditions for the trial.

        Patient is eligible if they do not have any of the
        excluded diagnosed conditions on file.
        """
        if row[ICD10_COLUMN] is None:
            return True

        # Literal exclusion codes
        patient_conditions = set(row[ICD10_COLUMN])
        if self.conditions_excl_codes_literal & patient_conditions:
            return False

        # Regex matching
        if self.conditions_excl_regex_pattern is not None:
            for patient_condition in patient_conditions:
                if self.conditions_excl_regex_pattern.match(patient_condition):
                    return False

        return True

    def excluded_procedures_filter(self, row: pd.Series) -> bool:
        """Filter to exclude any disqualifying procedures/medications for the trial.

        Patient is eligible if they do not have any of the
        excluded procedures on file
        """
        if row[CPT4_COLUMN] is None:
            return True

        patient_procedures = set(row[CPT4_COLUMN])
        if self.procedures_exclusion_codes & patient_procedures:
            return False

        return True

    def appointment_history_filter(self, row: pd.Series) -> bool:
        """Filter to check patient appointment history length.

        Matches patient with at least YEARS_OF_APPOINTMENT_HISTORY history and at
        least MIN_APPOINTMENTS_PER_HISTORY_YEAR appointment dates per year.
        """
        if not row[PREV_APPOINTMENTS_COL]:
            return False

        appointment_dates = self._convert_appointment_dates(row)

        historic_cutoff_date: date = date.today() - relativedelta(
            years=YEARS_OF_APPOINTMENT_HISTORY
        )

        # Check that there are at least YEARS_OF_APPOINTMENT_HISTORY years of
        # appointments; check that there is at least one appointment at or before the
        # historic cutoff date
        if not any(d <= historic_cutoff_date for d in appointment_dates):
            return False

        # Filter down only to appointments within the last
        # YEARS_OF_APPOINTMENT_HISTORY years
        appointment_dates_within_history: list[date] = [
            d for d in appointment_dates if d >= historic_cutoff_date
        ]

        return self._check_min_appointments_per_year(
            appointment_dates_within_history,
        )

    def _check_min_appointments_per_year(
        self, appointment_dates_within_history: list[date]
    ) -> bool:
        """Checks if patient has at least MIN_APPOINTMENTS_PER_HISTORY_YEAR."""

        # Group the appointment dates into year blocks based from today and count the
        # number of appointments in each year block
        appointments_by_year_ago: Counter[int] = Counter(
            relativedelta(date.today(), d).years
            for d in appointment_dates_within_history
        )

        # Note: Counter[missing_item] == 0 so don't need to worry about KeyError
        return all(
            appointments_by_year_ago[years_ago] >= MIN_APPOINTMENTS_PER_HISTORY_YEAR
            for years_ago in range(YEARS_OF_APPOINTMENT_HISTORY)
        )

    def is_current_patient(self, row: pd.Series) -> bool:
        """Checks if the patient has had an appointment in the last X months."""
        if not row[PREV_APPOINTMENTS_COL]:
            return False

        appointment_dates = self._convert_appointment_dates(row)

        historic_cutoff_date: date = date.today() - relativedelta(
            months=CURRENT_PATIENT_MONTHS_THRESHOLD
        )

        return any(d >= historic_cutoff_date for d in appointment_dates)

    def _convert_appointment_dates(self, row: pd.Series) -> list[date]:
        """Converts appointment dates from JSON format to list of dates."""
        appointment_dates = []
        for appt in row[PREV_APPOINTMENTS_COL]:
            if appt.get("Appointment Date"):
                appointment_dates.append(
                    datetime.strptime(
                        appt.get("Appointment Date"),
                        DATE_STR_FORMAT,
                    ).date()
                )
        return sorted(appointment_dates)

    def _filter_by_criteria(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies matching criteria to a dataframe to determine eligibility.

        This method adds eligibility column and exclusion reason column.
        """

        if FILTER_FAILED_REASON_COLUMN not in df:
            df[FILTER_FAILED_REASON_COLUMN] = ""

        for filter_ in self.get_inclusion_filters():
            df = filter_.apply_filter(df)

        df[FILTER_FAILED_REASON_COLUMN] = df[FILTER_FAILED_REASON_COLUMN].apply(
            lambda x: x.strip(", ")
        )
        return df


class TrialInclusionCriteriaMatchAlgorithmCharcoal(
    BaseGATrialInclusionAlgorithmFactorySingleEye
):
    """Algorithm for establishing number of patients that match clinical criteria."""

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "cnv_threshold": fields.Float(allow_none=True),
        "largest_ga_lesion_lower_bound": fields.Float(allow_none=True),
        "largest_ga_lesion_upper_bound": fields.Float(allow_none=True),
        "total_ga_area_lower_bound": fields.Float(allow_none=True),
        "total_ga_area_upper_bound": fields.Float(allow_none=True),
        "patient_age_lower_bound": fields.Integer(allow_none=True),
        "patient_age_upper_bound": fields.Integer(allow_none=True),
        "conditions_inclusion_codes": fields.List(fields.Str(), allow_none=True),
        "conditions_exclusion_codes": fields.List(fields.Str(), allow_none=True),
        "procedures_exclusion_codes": fields.List(fields.Str(), allow_none=True),
    }

    def __init__(
        self,
        cnv_threshold: float = CNV_THRESHOLD,
        largest_ga_lesion_lower_bound: float = LARGEST_GA_LESION_LOWER_BOUND,
        largest_ga_lesion_upper_bound: Optional[float] = None,
        total_ga_area_lower_bound: float = TOTAL_GA_AREA_LOWER_BOUND,
        total_ga_area_upper_bound: float = TOTAL_GA_AREA_UPPER_BOUND,
        patient_age_lower_bound: Optional[int] = None,
        patient_age_upper_bound: Optional[int] = None,
        conditions_inclusion_codes: Optional[list[str]] = None,
        conditions_exclusion_codes: Optional[list[str]] = None,
        procedures_exclusion_codes: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            cnv_threshold=cnv_threshold,
            largest_ga_lesion_lower_bound=largest_ga_lesion_lower_bound,
            total_ga_area_lower_bound=total_ga_area_lower_bound,
            total_ga_area_upper_bound=total_ga_area_upper_bound,
            largest_ga_lesion_upper_bound=largest_ga_lesion_upper_bound,
            patient_age_lower_bound=patient_age_lower_bound,
            patient_age_upper_bound=patient_age_upper_bound,
            **kwargs,
        )
        self.conditions_inclusion_codes = conditions_inclusion_codes
        self.conditions_exclusion_codes = conditions_exclusion_codes
        self.procedures_exclusion_codes = procedures_exclusion_codes

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
            conditions_inclusion_codes=self.conditions_inclusion_codes,
            conditions_exclusion_codes=self.conditions_exclusion_codes,
            procedures_exclusion_codes=self.procedures_exclusion_codes,
            **kwargs,
        )
