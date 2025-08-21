"""Generic EHR query algorithm for patient data access.

This module implements a generic algorithm for querying patient data from EHR systems.
It provides functionality to:
- Work with NextGen's FHIR, Enterprise, and SMART on FHIR APIs
- Work with generic FHIR R4 compatible systems
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, ClassVar, List, Literal, Optional

from fhirpy import SyncFHIRClient
from marshmallow import fields
from nameparser import HumanName
import pandas as pd

from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.externals.ehr.exceptions import (
    GetPatientInfoError,
    NoMatchingPatientError,
    NonSpecificPatientError,
    NoPatientIDError,
)
from bitfount.externals.ehr.fhir_r4.querier import FHIRR4PatientQuerier
from bitfount.externals.ehr.nextgen.api import NextGenEnterpriseAPI, NextGenFHIRAPI
from bitfount.externals.ehr.nextgen.authentication import NextGenAuthSession
from bitfount.externals.ehr.nextgen.querier import (
    FromPatientQueryError,
    NextGenPatientQuerier,
)
from bitfount.externals.ehr.nextgen.types import (
    PatientCodeDetails,
    RetrievedPatientDetailsJSON,
)
from bitfount.externals.ehr.types import EHRAppointment
from bitfount.externals.general.authentication import (
    ExternallyManagedJWT,
    ExternallyManagedJWTSession,
    GenericExternallyManagedJWTHandler,
)
from bitfount.federated.algorithms.base import (
    BaseNonModelAlgorithmFactory,
    BaseWorkerAlgorithm,
    NoResultsModellerAlgorithm,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    _BITFOUNT_PATIENT_ID_KEY,
    ACQUISITION_DATE_COL,
    ADDRESS_COL,
    CELL_NUMBER_COL,
    CPT4_COLUMN,
    DOB_COL,
    EMAIL_COL,
    FAMILY_NAME_COL,
    GENDER_COL,
    GIVEN_NAME_COL,
    HOME_NUMBER_COL,
    ICD10_COLUMN,
    LATERALITY_COL,
    LATEST_PRACTITIONER_NAME_COL,
    MRN_COL,
    NAME_COL,
    NEW_PATIENT_COL,
    NEXT_APPOINTMENT_COL,
    PREV_APPOINTMENTS_COL,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.hub.api import (
    BitfountHub,
    SMARTOnFHIR,
)
from bitfount.hub.authentication_flow import (
    BitfountSession,
)
from bitfount.types import T_FIELDS_DICT
from bitfount.utils.pandas_utils import (
    BITFOUNT_ID_COLUMNS,
    DOB_COLUMNS,
    find_bitfount_id_column,
    find_dob_column,
    find_family_name_column,
    find_full_name_column,
    find_given_name_column,
)

_logger = _get_federated_logger("bitfount.federated")

EHR_QUERY_COLUMNS = [
    _BITFOUNT_PATIENT_ID_KEY,
    DOB_COL,
    NAME_COL,
    GENDER_COL,
    HOME_NUMBER_COL,
    CELL_NUMBER_COL,
    EMAIL_COL,
    ADDRESS_COL,
    MRN_COL,
    GIVEN_NAME_COL,
    FAMILY_NAME_COL,
    NEXT_APPOINTMENT_COL,
    PREV_APPOINTMENTS_COL,
    NEW_PATIENT_COL,
    ORIGINAL_FILENAME_METADATA_COLUMN,
    ACQUISITION_DATE_COL,
    LATERALITY_COL,
    ICD10_COLUMN,
    CPT4_COLUMN,
    LATEST_PRACTITIONER_NAME_COL,
]

QuerierType = Literal["nextgen", "fhir_r4"]


@dataclass(frozen=True)
class PatientDetails:
    """Patient identifying information."""

    bitfount_patient_id: str
    dob: str | date
    given_name: Optional[str] = None
    family_name: Optional[str] = None


@dataclass(frozen=True)
class PatientQueryResults:
    """Container indicating the results of the various queries for a given patient."""

    codes: PatientCodeDetails
    next_appointment: Optional[date]
    previous_appointments: Optional[List[EHRAppointment]]
    id: Optional[str]
    given_name: Optional[str]
    family_name: Optional[str]
    date_of_birth: Optional[str | date]
    gender: Optional[str]
    home_numbers: List[str]
    cell_numbers: List[str]
    emails: List[str]
    mailing_address: Optional[str]
    medical_record_number: Optional[str]
    latest_practitioner_name: Optional[str]


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side of the algorithm for querying EHR systems."""

    def __init__(
        self,
        querier_type: QuerierType,
        *,
        fhir_url: Optional[str] = None,
        enterprise_url: Optional[str] = None,
        smart_on_fhir_url: Optional[str] = None,
        smart_on_fhir_resource_server_url: Optional[str] = None,
        session: Optional[BitfountSession] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the worker-side algorithm.

        Args:
            querier_type: Type of querier to use ("nextgen" or "fhir_r4").
            fhir_url: Base URL for the NextGen FHIR API (nextgen only).
            enterprise_url: Base URL for the NextGen Enterprise API (nextgen only).
            smart_on_fhir_url: Optional custom SMART on FHIR service URL (nextgen only).
            smart_on_fhir_resource_server_url: Optional custom SMART on FHIR resource
                server URL (nextgen only).
            session: BitfountSession object for use with SMARTOnFHIR service.
                Will be created if not provided. (nextgen only)
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)

        self.querier_type = querier_type

        if querier_type == "nextgen":
            self.fhir_url = fhir_url or NextGenFHIRAPI.DEFAULT_NEXT_GEN_FHIR_URL
            self.enterprise_url: Optional[str] = (
                enterprise_url or NextGenEnterpriseAPI.DEFAULT_NEXT_GEN_ENTERPRISE_URL
            )
            self.smart_on_fhir_url: Optional[str] = smart_on_fhir_url
            self.smart_on_fhir_resource_server_url: Optional[str] = (
                smart_on_fhir_resource_server_url
            )

            self.session: Optional[BitfountSession] = (
                session if session else BitfountSession()
            )
            if not self.session.authenticated:
                self.session.authenticate()

            self._get_nextgen_session()

            self.fhir_client: Optional[SyncFHIRClient] = None
        elif querier_type == "fhir_r4":
            if fhir_url is None:
                raise ValueError(
                    "fhir_url must be provided when querier_type is 'fhir_r4'"
                )
            self.fhir_url = fhir_url
            self.fhir_client = SyncFHIRClient(self.fhir_url)

            self.enterprise_url = None
            self.smart_on_fhir_url = None
            self.smart_on_fhir_resource_server_url = None
            self.session = None
            self.nextgen_session: Optional[NextGenAuthSession] = None
        else:
            raise ValueError(
                f"Invalid querier_type: {querier_type}. Must be 'nextgen' or 'fhir_r4'"
            )

    def initialise(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        ehr_secrets: Optional[ExternallyManagedJWT] = None,
        **kwargs: Any,
    ) -> None:
        """Sets Datasource and EHR secrets."""
        if ehr_secrets:
            self.ehr_secrets = ehr_secrets
            self.ehr_session = ExternallyManagedJWTSession(
                authentication_handler=GenericExternallyManagedJWTHandler(
                    jwt=self.ehr_secrets.jwt,
                    expires=self.ehr_secrets.expires,
                    get_token=self.ehr_secrets.get_token,
                )
            )

        self.initialise_data(datasource=datasource, data_splitter=data_splitter)

    def run(
        self,
        patients: List[PatientDetails],
    ) -> dict[PatientDetails, PatientQueryResults]:
        """Query EHR APIs for matching patient information.

        Args:
            patients: List of patient details to search for.

        Returns:
            Dict of {patient: query_results}. There will be an entry for every
            patient in `patients`, with an "empty" query results for those whose
            query results could not be retrieved (which is distinct from just having
            empty results).
        """
        self._refresh_fhir_client_token()

        patient_query_results = self._run(patients)

        # For any patient for whom results were not found, create an empty
        # PatientQueryDetails entry
        for missed_patient in (p for p in patients if p not in patient_query_results):
            patient_query_results[missed_patient] = PatientQueryResults(
                codes=PatientCodeDetails(
                    condition_codes=None,
                    procedure_codes=None,
                ),
                next_appointment=None,
                previous_appointments=None,
                id="",
                given_name=missed_patient.given_name,
                family_name=missed_patient.family_name,
                date_of_birth=missed_patient.dob,
                gender=None,
                home_numbers=[],
                cell_numbers=[],
                emails=[],
                mailing_address=None,
                medical_record_number=None,
                latest_practitioner_name=None,
            )

        return patient_query_results

    def _get_nextgen_session(self) -> None:
        """Get NextGenAuthSession."""
        # Get SMART on FHIR bearer token
        smart_auth = SMARTOnFHIR(
            session=self.session,
            smart_on_fhir_url=self.smart_on_fhir_url,
            resource_server_url=self.smart_on_fhir_resource_server_url,
        )
        self.nextgen_session = NextGenAuthSession(smart_auth)

    def _refresh_fhir_client_token(self) -> None:
        if self.querier_type == "fhir_r4":
            if self.fhir_client is None:
                raise ValueError(
                    "Worker should not have been initialized without fhir_client"
                )

            if self.ehr_secrets is None:
                raise ValueError(
                    "Worker should have been initialised with ehr secrets before run"
                )

            handler: GenericExternallyManagedJWTHandler = (
                self.ehr_session.authentication_handler
            )
            token: str = handler.get_valid_token()
            self.fhir_client.authorization = f"Bearer {token}"

    def get_patient_querier(
        self, patient: PatientDetails
    ) -> NextGenPatientQuerier | FHIRR4PatientQuerier:
        """Get Patient Querier class for this patient."""
        patient_querier: NextGenPatientQuerier | FHIRR4PatientQuerier
        if self.querier_type == "nextgen":
            if self.nextgen_session is None:
                raise ValueError("Worker should not be run without nextgen_session.")
            patient_querier = NextGenPatientQuerier.from_patient_query(
                patient_dob=patient.dob,
                given_name=patient.given_name,
                family_name=patient.family_name,
                nextgen_session=self.nextgen_session,
            )
        elif self.querier_type == "fhir_r4":
            if self.fhir_client is None:
                raise ValueError(
                    "Worker should not have been initialized without fhir_client"
                )
            patient_querier = FHIRR4PatientQuerier.from_patient_query(
                patient_dob=patient.dob,
                given_name=patient.given_name,
                family_name=patient.family_name,
                fhir_client=self.fhir_client,
            )
        return patient_querier

    def _run(
        self, patients: List[PatientDetails]
    ) -> dict[PatientDetails, PatientQueryResults]:
        """Run patient queries."""
        patient_query_results: dict[PatientDetails, PatientQueryResults] = {}

        # Process each patient
        for patient in patients:
            # Build patient querier for accessing all information
            try:
                patient_querier = self.get_patient_querier(patient)
            except (
                NoMatchingPatientError,
                NonSpecificPatientError,
                NoPatientIDError,
                FromPatientQueryError,
            ):
                _logger.warning("Unable to retrieve a patient ID; skipping.")
                continue

            # Get patient code states
            try:
                patient_code_details = patient_querier.get_patient_code_states()
            except GetPatientInfoError:
                patient_code_details = PatientCodeDetails(
                    condition_codes=None,
                    procedure_codes=None,
                )

            # Find next appointment for patient
            try:
                next_appointment: Optional[date] = (
                    patient_querier.get_next_appointment()
                )
            except GetPatientInfoError:
                next_appointment = None

            try:
                previous_appointments: Optional[list[EHRAppointment]] = (
                    patient_querier.get_previous_appointment_details()
                )
            except GetPatientInfoError:
                previous_appointments = None

            # Get latest practitioner name for patient
            try:
                latest_practitioner_name = (
                    patient_querier.get_patient_latest_medical_practitioner()
                )
            except GetPatientInfoError:
                latest_practitioner_name = None

            # Create entry for this patient
            fhir_patient_info: RetrievedPatientDetailsJSON | dict = (
                patient_querier.fhir_patient_info or {}
            )
            patient_query_results[patient] = PatientQueryResults(
                codes=patient_code_details,
                next_appointment=next_appointment,
                previous_appointments=previous_appointments,
                id=patient_querier.patient_id,
                given_name=patient.given_name,
                family_name=patient.family_name,
                date_of_birth=patient.dob,
                gender=fhir_patient_info.get("gender"),
                home_numbers=fhir_patient_info.get("home_numbers", []),
                cell_numbers=fhir_patient_info.get("cell_numbers", []),
                emails=fhir_patient_info.get("emails", []),
                mailing_address=fhir_patient_info.get("mailing_address"),
                medical_record_number=(fhir_patient_info.get("medical_record_number")),
                latest_practitioner_name=latest_practitioner_name,
            )

        return patient_query_results

    @staticmethod
    def dataframe_to_patient_details(
        df: pd.DataFrame,
        bitfount_patient_id_column: str = _BITFOUNT_PATIENT_ID_KEY,
        dob_column: str = DOB_COL,
        name_column: Optional[str] = None,
        given_name_column: Optional[str] = None,
        family_name_column: Optional[str] = None,
    ) -> list[PatientDetails]:
        """Convert a pandas DataFrame into a list of PatientDetails objects.

        Args:
            df: DataFrame containing patient information. Must have `NAME_COL`
                and `DOB_COL`
            bitfount_patient_id_column: Explicit column name for Bitfount patient ID.
            dob_column: Explicit column name for date of birth.
            name_column: Optional explicit column name for full name. Mutually
                exclusive with given_name_column and family_name_column.
            given_name_column: Optional explicit column name for given name.
            family_name_column: Optional explicit column name for family name.

        Returns:
            List of PatientDetails objects constructed from the DataFrame rows.

        Raises:
            ValueError: If required date of birth or Bitfount patient ID columns are
                missing, or if both name_column and given/family name columns are
                provided.
        """
        # Check for mutually exclusive name columns
        if name_column and (given_name_column or family_name_column):
            raise ValueError(
                "Cannot specify both name_column"
                " and given_name_column/family_name_column"
            )

        # Use explicit column names if provided, otherwise try to find a matching
        # column from the potential name lists that is in the dataframe.
        bitfount_id_col: Optional[str]
        if bitfount_patient_id_column in df.columns:
            bitfount_id_col = bitfount_patient_id_column
        else:
            bitfount_id_col = find_bitfount_id_column(df)
        if bitfount_id_col is None:
            raise ValueError(
                f"DataFrame must contain a Bitfount patient ID column."
                f" Expected one of: {BITFOUNT_ID_COLUMNS}"
                f" or explicitly provided column: {bitfount_patient_id_column}"
            )

        dob_col: Optional[str]
        if dob_column in df.columns:
            dob_col = dob_column
        else:
            dob_col = find_dob_column(df)
        if dob_col is None:
            raise ValueError(
                f"DataFrame must contain a date of birth column."
                f" Expected one of: {DOB_COLUMNS}"
                f" or explicitly provided column: {dob_column}"
            )

        name_col: Optional[str] = (
            name_column
            if name_column in df.columns
            else (
                find_full_name_column(df)
                if not (given_name_column or family_name_column)
                else None
            )
        )
        given_name_col: Optional[str] = (
            given_name_column
            if given_name_column in df.columns
            else find_given_name_column(df)
            if not name_column
            else None
        )
        family_name_col: Optional[str] = (
            family_name_column
            if family_name_column in df.columns
            else find_family_name_column(df)
            if not name_column
            else None
        )

        patients = []
        for _, row in df.iterrows():
            # Get date of birth value
            dob = row[dob_col]

            # Convert string to date if needed
            if isinstance(dob, str):
                try:
                    dob = pd.to_datetime(dob).date()
                except (ValueError, TypeError):
                    _logger.warning(f"Invalid date format for DOB: {dob}")
                    continue

            # Get Bitfount patient ID (required)
            bitfount_patient_id: str = row[bitfount_id_col]
            if pd.isna(bitfount_patient_id):
                _logger.warning("Missing required Bitfount patient ID, skipping record")  # type: ignore[unreachable] # Reason: should be unreachable but just sanity checking # noqa: E501
                continue

            # Handle name fields
            given_name: Optional[str]
            family_name: Optional[str]

            if name_col:
                # Split full name into given and family names
                given_name, family_name = _WorkerSide._split_full_name(row[name_col])
            else:
                # Get separate name fields
                given_name = row[given_name_col] if given_name_col else None
                family_name = row[family_name_col] if family_name_col else None

            # Create PatientDetails object
            patient = PatientDetails(
                bitfount_patient_id=bitfount_patient_id,
                dob=dob,
                given_name=given_name,
                family_name=family_name,
            )
            patients.append(patient)

        return patients

    @staticmethod
    def _split_full_name(full_name: str) -> tuple[Optional[str], Optional[str]]:
        """Split a full name into given name and family name components.

        Args:
            full_name: The full name string to split.

        Returns:
            Tuple of (given_name, family_name). Either component may be None if
            the name cannot be split properly.
        """
        if pd.isna(full_name) or not full_name.strip():
            return None, None

        # Handle DICOM-style names with carets
        if "^" in full_name:
            name_parts = full_name.split("^")
            if len(name_parts) >= 2:
                return name_parts[1], name_parts[0]  # DICOM format is Last^First
            return None, name_parts[0]

        # Handle other formats of name
        human_name = HumanName(full_name.strip())
        return (
            human_name.first if human_name.first else None,
            human_name.last if human_name.last else None,
        )

    @staticmethod
    def merge_results_with_dataframe(
        query_results: dict[PatientDetails, PatientQueryResults],
        df: pd.DataFrame,
        bitfount_patient_id_column: str = _BITFOUNT_PATIENT_ID_KEY,
        next_appointment_col: str = NEXT_APPOINTMENT_COL,
        prev_appointments_col: str = PREV_APPOINTMENTS_COL,
    ) -> pd.DataFrame:
        """Merge patient query results with the original DataFrame.

        Args:
            query_results: Dictionary mapping PatientDetails to their query results.
            df: DataFrame containing patient information. Must have a Bitfount patient
                ID column, `NAME_COL`, `DOB_COL`, `ORIGINAL_FILENAME_METADATA_COLUMN`,
                `ACQUISITION_DATE_COL`, and `LATERALITY_COL`.
            bitfount_patient_id_column: Explicit column name for Bitfount patient ID.
            next_appointment_col: The name to use for the column containing next
                appointment date information.
            prev_appointments_col: The name to use for the column containing previous
                appointments information.

        Returns:
            DataFrame with additional columns for query results information.

        Raises:
            ValueError: If required Bitfount patient ID column is missing.
        """
        # Create a copy of the input DataFrame
        result_df = df.reset_index(drop=True).copy()

        # Use explicit column names if provided, otherwise try to find a matching
        # column from the potential name lists that is in the dataframe.
        bitfount_id_col: Optional[str]
        if bitfount_patient_id_column in df.columns:
            bitfount_id_col = bitfount_patient_id_column
        else:
            bitfount_id_col = find_bitfount_id_column(df)
            if bitfount_id_col is None:
                raise ValueError(
                    f"DataFrame must contain a Bitfount patient ID column."
                    f" Expected one of: {BITFOUNT_ID_COLUMNS}"
                    f" or explicitly provided column: {bitfount_patient_id_column}"
                )
            else:
                result_df[_BITFOUNT_PATIENT_ID_KEY] = df[bitfount_id_col]

        required_cols = [
            NAME_COL,
            DOB_COL,
            ORIGINAL_FILENAME_METADATA_COLUMN,
            ACQUISITION_DATE_COL,
            LATERALITY_COL,
        ]
        missing_cols = [col for col in required_cols if col not in result_df.columns]
        if missing_cols:
            raise ValueError(
                f"DataFrame must contain required columns. Missing: {missing_cols}"
            )

        # Add next appointment information as column
        # Initialise column to all `None`s
        result_df[next_appointment_col] = None
        result_df[prev_appointments_col] = None
        result_df[GENDER_COL] = None
        result_df[HOME_NUMBER_COL] = None
        result_df[CELL_NUMBER_COL] = None
        result_df[EMAIL_COL] = None
        result_df[ADDRESS_COL] = None
        result_df[MRN_COL] = None
        result_df[CPT4_COLUMN] = None
        result_df[ICD10_COLUMN] = None
        result_df[LATEST_PRACTITIONER_NAME_COL] = None
        if DOB_COL not in result_df:
            result_df[DOB_COL] = None

        for patient, patient_query_results in query_results.items():
            mask = result_df[_BITFOUNT_PATIENT_ID_KEY] == patient.bitfount_patient_id
            result_df.loc[mask, next_appointment_col] = (
                patient_query_results.next_appointment
            )
            result_df.loc[mask, GENDER_COL] = patient_query_results.gender
            result_df.loc[mask, ADDRESS_COL] = patient_query_results.mailing_address
            result_df.loc[mask, MRN_COL] = patient_query_results.medical_record_number
            result_df.loc[mask, DOB_COL] = (
                patient.dob or patient_query_results.date_of_birth
            )
            result_df.loc[mask, GIVEN_NAME_COL] = patient_query_results.given_name
            result_df.loc[mask, FAMILY_NAME_COL] = patient_query_results.family_name
            result_df.loc[mask, LATEST_PRACTITIONER_NAME_COL] = (
                patient_query_results.latest_practitioner_name
            )

            # This is for elements which are lists, as they don't work with .loc
            for idx in result_df[mask].index:
                if patient_query_results.previous_appointments is not None:
                    result_df.at[idx, prev_appointments_col] = [
                        appt.format_for_csv()
                        for appt in patient_query_results.previous_appointments
                    ]
                result_df.at[idx, HOME_NUMBER_COL] = patient_query_results.home_numbers
                result_df.at[idx, CELL_NUMBER_COL] = patient_query_results.cell_numbers
                result_df.at[idx, EMAIL_COL] = patient_query_results.emails

                if patient_query_results.codes.condition_codes is not None:
                    result_df.at[idx, ICD10_COLUMN] = (
                        patient_query_results.codes.condition_codes
                    )

                if patient_query_results.codes.procedure_codes is not None:
                    result_df.at[idx, CPT4_COLUMN] = (
                        patient_query_results.codes.procedure_codes
                    )

        result_df[NEW_PATIENT_COL] = result_df[prev_appointments_col].apply(
            lambda x: len(x) <= 1 if x is not None else "Unknown"
        )

        # Drop other unnecessary columns
        result_df = result_df[EHR_QUERY_COLUMNS]

        return result_df


class EHRPatientQueryAlgorithm(
    BaseNonModelAlgorithmFactory[NoResultsModellerAlgorithm, _WorkerSide]
):
    """Algorithm for querying patient data from EHR systems."""

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "querier_type": fields.Str(),
        "fhir_url": fields.Str(allow_none=True),
        "enterprise_url": fields.Str(allow_none=True),
        "smart_on_fhir_url": fields.Str(allow_none=True),
        "smart_on_fhir_resource_server_url": fields.Str(allow_none=True),
    }

    def __init__(
        self,
        datastructure: DataStructure,
        querier_type: QuerierType,
        fhir_url: Optional[str] = None,
        enterprise_url: Optional[
            str
        ] = NextGenEnterpriseAPI.DEFAULT_NEXT_GEN_ENTERPRISE_URL,
        smart_on_fhir_url: Optional[str] = None,
        smart_on_fhir_resource_server_url: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the algorithm.

        Args:
            datastructure: The data structure definition
            querier_type: Type of querier to use ("nextgen" or "fhir_r4")
            fhir_url: Optional custom FHIR API URL (for both NextGen and FHIRR4)
            enterprise_url: Optional custom Enterprise API URL (for NextGen)
            smart_on_fhir_url: Optional custom SMART on FHIR service URL (for NextGen)
            smart_on_fhir_resource_server_url: Optional custom SMART on FHIR resource
                server URL (for NextGen)
            **kwargs: Additional keyword arguments.
        """
        super().__init__(datastructure=datastructure, **kwargs)

        self.querier_type = querier_type
        self.fhir_url = fhir_url
        self.enterprise_url = enterprise_url
        self.smart_on_fhir_url = smart_on_fhir_url
        self.smart_on_fhir_resource_server_url = smart_on_fhir_resource_server_url

    def modeller(self, **kwargs: Any) -> NoResultsModellerAlgorithm:
        """Modeller-side of the algorithm."""
        return NoResultsModellerAlgorithm(
            log_message=f"Running {self.querier_type.title()} EHR "
            f"Patient Query Algorithm",
            **kwargs,
        )

    def worker(
        self,
        *,
        hub: Optional[BitfountHub] = None,
        session: Optional[BitfountSession] = None,
        **kwargs: Any,
    ) -> _WorkerSide:
        """Worker-side of the algorithm."""
        if self.querier_type == "nextgen":
            if hub is None and session is None:
                raise ValueError(
                    "One of hub or session must be provided for NextGen querier."
                )

            session_: BitfountSession
            if hub is not None and session is not None:
                _logger.warning(
                    "Both hub and session were provided;"
                    " using provided session in preference to hub session."
                )
                session_ = session
            elif hub is not None:
                session_ = hub.session
            else:  # session is not None
                assert session is not None  # nosec[assert_used]: Previous checks guarantee this is not None here # noqa: E501
                session_ = session

            return _WorkerSide(
                querier_type=self.querier_type,
                fhir_url=self.fhir_url,
                enterprise_url=self.enterprise_url,
                smart_on_fhir_url=self.smart_on_fhir_url,
                smart_on_fhir_resource_server_url=self.smart_on_fhir_resource_server_url,
                session=session_,
                **kwargs,
            )
        elif self.querier_type == "fhir_r4":
            if self.fhir_url is None:
                raise ValueError("fhir_url must be provided for FHIR R4 querier.")

            return _WorkerSide(
                querier_type=self.querier_type,
                fhir_url=self.fhir_url,
                **kwargs,
            )
        else:
            raise ValueError(
                f"Invalid querier_type: {self.querier_type}. "
                f"Must be 'nextgen' or 'fhir_r4'"
            )
