"""API stubs for interacting with NextGen services."""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from datetime import date
from enum import Enum
import functools
import hashlib
import logging
from pathlib import Path
from typing import (
    Callable,
    Final,
    Iterable,
    List,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    cast,
    overload,
)
import warnings

from dateutil.parser import parse as dateutil_parse
from pydantic_core import Url
import pydash
from requests import HTTPError
from slugify import slugify

from bitfount.externals.ehr.nextgen.authentication import NextGenAuthSession
from bitfount.externals.ehr.nextgen.exceptions import (
    NextGenFHIRAPIError,
    NoMatchingNextGenPatientError,
    NoNextGenPatientIDError,
    NonSpecificNextGenPatientError,
)
from bitfount.externals.ehr.nextgen.types import (
    BulkPatientInfo,
    FHIRBundleEntryJSON,
    FHIRBundleJSON,
    FHIRBundleResourceJSON,
    NextGenEnterpriseAppointmentsEntryJSON,
    NextGenEnterpriseAppointmentsJSON,
    NextGenEnterpriseChartJSON,
    NextGenEnterpriseDiagnosesEntryJSON,
    NextGenEnterpriseDiagnosesJSON,
    NextGenEnterpriseDocumentsJSON,
    NextGenEnterpriseEncountersEntryJSON,
    NextGenEnterpriseEncountersJSON,
    NextGenEnterpriseMedicationsEntryJSON,
    NextGenEnterpriseMedicationsJSON,
    NextGenEnterprisePersonJSON,
    NextGenEnterpriseProceduresEntryJSON,
    NextGenEnterpriseProceduresJSON,
    NextGenEnterpriseSocialHistoryEntryJSON,
    NextGenEnterpriseSocialHistoryJSON,
    PatientNameJSON,
    RetrievedPatientDetailsJSON,
)
from bitfount.externals.general.authentication import BearerAuthSession
from bitfount.persistence.caching import (
    EncryptedDiskcacheFunctionCache,
    FunctionCache,
)

logger = logging.getLogger(__name__)

func_cache: FunctionCache = EncryptedDiskcacheFunctionCache()

JSON_RESPONSE_TYPES = (
    NextGenEnterpriseDiagnosesJSON
    | NextGenEnterpriseProceduresJSON
    | NextGenEnterprisePersonJSON
    | NextGenEnterpriseChartJSON
    | NextGenEnterpriseSocialHistoryJSON
    | NextGenEnterpriseEncountersJSON
    | NextGenEnterpriseMedicationsJSON
    | NextGenEnterpriseDocumentsJSON
)


@func_cache.memoize(ignore=(0, "session"))
def _cached_get(
    session: BearerAuthSession | NextGenAuthSession,
    url: str,
    token_hash: str,
    params: Optional[dict[str, str]] = None,
) -> JSON_RESPONSE_TYPES:
    """Cached get responses from Nextgen Enterprise and FHIR.

    Note that this uses the current session token (hashed) as a cache key,
    so the cache will be invalidated when the token is refreshed.
    """
    resp = session.get(
        url,
        params=params,
    )
    resp.raise_for_status()
    resp_json: JSON_RESPONSE_TYPES = resp.json()
    return resp_json


def _get_token_hash(
    session: BearerAuthSession | NextGenAuthSession,
) -> str:
    """Get a hashed session token to use as cache key."""
    token = getattr(session, "token", None)
    if token is None:
        return ""
    return hashlib.sha256(token.encode("UTF-8")).hexdigest()


class AppointmentTemporalState(Enum):
    """Denotes whether appointment is in the past or the future."""

    PAST = "past"
    FUTURE = "future"


@dataclass
class DocumentInfo:
    """Document Info to facilitate download of documents."""

    document_id: str
    document_date: str = ""
    document_description: str = ""


class NextGenFHIRAPI:
    """API for interacting with the NextGen FHIR API."""

    DEFAULT_NEXT_GEN_FHIR_URL: Final[str] = (
        "https://fhir.nextgen.com/nge/prod/fhir-api-r4/fhir/R4"
    )

    def __init__(
        self,
        session: BearerAuthSession | NextGenAuthSession,
        next_gen_fhir_url: str = DEFAULT_NEXT_GEN_FHIR_URL,
    ):
        """Create a new instance for interacting with the NextGen FHIR API.

        Args:
            session: Session containing bearer token information for NextGen API.
            next_gen_fhir_url: Base URL of the FHIR API endpoint. Should be of a
                similar style to
                `https://fhir.nextgen.com/nge/prod/fhir-api-r4/fhir/R4/`.
        """
        if isinstance(session, BearerAuthSession):
            warnings.warn(
                "Using BearerAuthSession in NextGenFHIRAPI is deprecated."
                " Please use NextGenAuthSession instead.",
                DeprecationWarning,
            )
        self.session = session
        self.url = next_gen_fhir_url.rstrip("/")  # to ensure no trailing slash

    def get_patient_info(
        self,
        dob: str | date,
        given_name: Optional[str] = None,
        family_name: Optional[str] = None,
    ) -> Optional[RetrievedPatientDetailsJSON]:
        """Search for a patient info given patient information.

        If unable to find, or unable to narrow down to a specific patient, return None.

        Arguments except for DoB are optional, but additional arguments will help to
        narrow down the patients to a singular patient.

        Args:
            dob: Date of birth as either a string (must contain YMD information as
                minimum and in that order) or an existing date/datetime object
                representing the date of birth.
            given_name: The given name of the patient. Can be a portion of the given
                name as will be substring-matched.
            family_name: The family name of the patient. Can be a portion of the given
                name as will be substring-matched.

        Returns:
            The patient info if a singular match was found, otherwise None.

        Raises:
            ValueError: if no criteria are supplied.
        """
        try:
            patient_entry: FHIRBundleResourceJSON = self._get_patient_entry(
                dob, given_name, family_name
            )
        except NextGenFHIRAPIError as e:
            logger.error(f"Failed to retrieve patient entry; error was: {str(e)}")
            return None

        try:
            patient_id = self._extract_id(patient_entry)
        except NoNextGenPatientIDError as e:
            logger.error(f"Failed to retrieve patient entry; error was: {str(e)}")
            return None

        given_name, family_name = self._extract_name_fields(patient_entry)
        mrn = self._extract_mrn(patient_entry)
        address = self._extract_address(patient_entry)
        extracted_dob = self._extract_dob(patient_entry)
        gender = self._extract_gender(patient_entry)
        home_numbers, cell_numbers = self._extract_contact_numbers(patient_entry)
        emails = self._extract_emails(patient_entry)

        patient_info = RetrievedPatientDetailsJSON(
            id=patient_id,
            given_name=given_name,
            family_name=family_name,
            date_of_birth=extracted_dob,
            gender=gender,
            home_numbers=home_numbers,
            cell_numbers=cell_numbers,
            emails=emails,
            mailing_address=address,
            medical_record_number=mrn,
        )

        return patient_info

    @staticmethod
    def _extract_name_fields(
        patient_entry: FHIRBundleResourceJSON,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Extract names from Patient API response.

        Returns a tuple of given names, family name
        """

        list_names = patient_entry.get("name", [])

        if len(list_names) == 0:
            logger.info("Name was not found in FHIR Patient entry.")
            return None, None

        if len(list_names) > 1:
            # This may happen if there are nicknames and aliases
            # See HumanName: https://www.hl7.org/fhir/R4/datatypes.html#HumanName
            logger.info("Found more than 1 name, returning the first one found.")

        latest_given_name = list_names[0]["given"][-1]
        family_name = list_names[0]["family"]

        return latest_given_name, family_name

    @staticmethod
    def _extract_mrn(patient_entry: FHIRBundleResourceJSON) -> Optional[str]:
        """Extract medical record name from Patient API response."""
        mrns = pydash.filter_(
            patient_entry.get("identifier", []),
            {"type": {"text": "Medical Record Number"}},
        )

        if len(mrns) == 0:
            logger.info("No MRN identifier found.")
            return None

        if len(mrns) > 1:
            logger.info("Found more than one MRN, returning the first one found.")

        mrn_value: str = mrns[0]["value"]
        return mrn_value

    @staticmethod
    def _extract_address(patient_entry: FHIRBundleResourceJSON) -> Optional[str]:
        """Extract address from Patient API response."""

        list_addresses: List[dict] = patient_entry.get("address", [])

        home_addresses = pydash.filter_(list_addresses, {"use": "home"})

        if len(home_addresses) == 0:
            logger.info("No home_addresses found.")
            return None

        latest_add = home_addresses[-1]
        address_str = "\n".join(latest_add["line"])

        for address_part in ["city", "state", "postalCode"]:
            if latest_add.get(address_part):
                address_str += "\n"
                address_str += latest_add.get(address_part, "")

        return address_str

    @staticmethod
    def _extract_dob(patient_entry: FHIRBundleResourceJSON) -> Optional[str]:
        """Extract date of birth from Patient API response."""

        return patient_entry.get("birthDate", None)

    @staticmethod
    def _extract_gender(patient_entry: FHIRBundleResourceJSON) -> Optional[str]:
        """Extract gender info from Patient API response."""

        return patient_entry.get("gender", None)

    @staticmethod
    def _extract_contact_numbers(
        patient_entry: FHIRBundleResourceJSON,
    ) -> Tuple[List[str], List[str]]:
        """Extract contact numbers from Patient API response.

        Returns a tuple of home numbers and cell numbers
        """
        list_numbers: List[dict] = patient_entry.get("telecom", [])

        home_numbers = (
            pydash.py_(list_numbers)
            .filter_({"system": "phone", "use": "home"})
            .map_("value")
            .value()
        )
        cell_numbers = (
            pydash.py_(list_numbers)
            .filter_({"system": "phone", "use": "mobile"})
            .map_("value")
            .value()
        )

        return home_numbers, cell_numbers

    @staticmethod
    def _extract_emails(patient_entry: FHIRBundleResourceJSON) -> List[str]:
        """Extract list of emails from Patient API response."""

        return (
            pydash.py_(patient_entry.get("telecom", []))
            .filter_({"system": "email"})
            .map_("value")
            .value()
        )

    def _get_patient_entry(
        self,
        dob: str | date,
        given_name: Optional[str] = None,
        family_name: Optional[str] = None,
    ) -> FHIRBundleResourceJSON:
        """Find specific Patient EHR entry based on name and DOB."""
        # Construct the birthdate query params object
        dob_date: date
        if isinstance(dob, str):
            # Parse a date string of any amount of detail but assuming YMD if the
            # date section is ambiguous
            dob_date = dateutil_parse(dob, yearfirst=True, dayfirst=False)
        else:
            dob_date = dob
        params = {"birthdate": dob_date.strftime("%Y-%m-%d")}

        # Query for the patient(s). We only query on DoB as this is far more
        # structured than names. We will perform filtering on name locally.
        resp = self.session.get(f"{self.url}/Patient", params=params)
        resp.raise_for_status()
        resp_json: FHIRBundleJSON = resp.json()

        resp_json_entries: Optional[list[FHIRBundleEntryJSON]] = resp_json.get("entry")
        if resp_json_entries is None:
            # DEV: Should we log some of the query criteria here? Need to avoid PPI?
            raise NoMatchingNextGenPatientError(
                "No patient matching DoB criteria was found."
            )

        # Filter found entries based on names
        patient_entries: list[FHIRBundleResourceJSON] = list(
            self._filter_entries_by_name(
                # Get iterable of FHIRBundleResourceJSON elements
                map(lambda x: x["resource"], resp_json_entries),
                given_name,
                family_name,
            )
        )

        # Handle unsupported conditions, e.g. multiple patients matching criteria
        # returned
        if (num_patients := len(patient_entries)) > 1:
            # DEV: Should we log some of the query criteria here? Need to avoid PPI?
            raise NonSpecificNextGenPatientError(
                f"Could not narrow down to a single patient from information provided."
                f" Got {num_patients} patients matching query criteria."
            )
        elif num_patients == 0:
            # DEV: Should we log some of the query criteria here? Need to avoid PPI?
            raise NoMatchingNextGenPatientError(
                "After applying filters, no patient matching DoB"
                " and other criteria were found."
            )

        return patient_entries[0]

    @staticmethod
    def _extract_id(entry: FHIRBundleResourceJSON) -> str:
        """Extracts patient ID from the json patient entry."""

        # Extract the patient ID from the nested structure
        patient_id: Optional[str] = pydash.get(entry, "id")
        if patient_id is None:
            raise NoNextGenPatientIDError(
                "Found matching patient information but could not extract"
                " patient ID from the response."
            )
        else:
            return patient_id

    @classmethod
    def _filter_entries_by_name(
        cls,
        patient_entries: Iterable[FHIRBundleResourceJSON],
        given_name: Optional[str] = None,
        family_name: Optional[str] = None,
    ) -> Iterable[FHIRBundleResourceJSON]:
        """Filter results from Patients endpoint on name."""
        # DEV: We may want to replace this with smarter/fuzzy matching to account for
        #      minor differences in spelling, structure, or case.

        # Fast-return if no filtering criteria were specified.
        if given_name is None and family_name is None:
            yield from patient_entries

        # Create name checker that is usable as a filter
        patient_name_checker: Callable[[PatientNameJSON], bool] = functools.partial(
            cls._check_patient_names,
            given_name=given_name,
            family_name=family_name,
        )

        # Filter for only patients that match on given and family name
        for patient_entry in patient_entries:
            patient_names: list[PatientNameJSON] = patient_entry.get("name", [])
            if not any(map(patient_name_checker, patient_names)):
                continue

            # Otherwise, if all filters are passed, yield entry
            yield patient_entry

    @classmethod
    def _check_patient_names(
        cls,
        patient_name_info: PatientNameJSON,
        given_name: Optional[str] = None,
        family_name: Optional[str] = None,
    ) -> bool:
        """Check for match in family and given name."""
        # Check family name directly (with substring matching)
        family_name_match: bool = False
        if family_name is not None:
            family_name_entry: Optional[str] = patient_name_info.get("family")
            if family_name_entry is not None:
                family_name_match = family_name in family_name_entry

        # Check given name against each entry in the given names list (with substring
        # matching)
        given_name_match: bool = False
        if given_name is not None:
            given_name_entries: list[str] = patient_name_info.get("given", [])
            for given_name_entry in given_name_entries:
                if given_name in given_name_entry:
                    given_name_match = True
                    break

        return family_name_match and given_name_match


T_Item_Type = TypeVar("T_Item_Type")
T_Endpoint_Response_Type = TypeVar("T_Endpoint_Response_Type", covariant=True)


class _SinglePageRetrieveCallable(Protocol[T_Item_Type]):
    """Callable that returns `items` and `nextPageLink` from single paginated page."""

    def __call__(
        self,
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> tuple[Optional[list[T_Item_Type]], Optional[Url]]: ...


class _EndpointGetCallable(Protocol[T_Endpoint_Response_Type]):
    """A callable that will actually make a GET request and return the JSON.

    The endpoint URL includes the patient ID.
    """

    def __call__(
        self,
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> T_Endpoint_Response_Type: ...


class NextGenEnterpriseAPI:
    """API for interacting with the NextGen Enterprise API."""

    DEFAULT_NEXT_GEN_ENTERPRISE_URL: Final[str] = (
        "https://nativeapi.nextgen.com/nge/prod/nge-api/api"
    )
    DATETIME_STR_FORMAT = "%Y-%m-%dT%H:%M:%S"

    def __init__(
        self,
        session: BearerAuthSession | NextGenAuthSession,
        next_gen_enterprise_url: str = DEFAULT_NEXT_GEN_ENTERPRISE_URL,
    ):
        """Create a new instance for interacting with the NextGen Enterprise API.

        Args:
            session: Session containing bearer token information for NextGen API.
            next_gen_enterprise_url: Base URL of the FHIR API endpoint. Should be of a
                similar style to
                `https://nativeapi.nextgen.com/nge/prod/nge-api/api/`.
        """
        if isinstance(session, BearerAuthSession):
            warnings.warn(
                "Using BearerAuthSession in NextGenEnterpriseAPI is deprecated."
                " Please use NextGenAuthSession instead.",
                DeprecationWarning,
            )
        self.session = session
        self.url = next_gen_enterprise_url.rstrip("/")  # to ensure no trailing slash

    def get_conditions_information(
        self, patient_id: str, expand_options: Optional[Collection[str]] = None
    ) -> Optional[list[NextGenEnterpriseDiagnosesEntryJSON]]:
        """Retrieve the diagnoses/conditions information for a patient.

        Args:
            patient_id: The NextGen patient identifier for the target patient.
            expand_options: `$expand` query args to pass through to the API call.

        Returns:
            A list of JSON objects containing information on diagnoses/conditions of
            the patient. The list may be empty. If there was no such list in the JSON
            at all, return None.
        """
        # Create `$expand` params if needed
        if expand_options is not None:
            params = {"$expand": ",".join(expand_options)}
        else:
            params = None

        items = self._retrieve_items_from_paginated_endpoint(
            self._get_conditions_information,
            patient_id,
            params,
            expected_path_end_formattable="/api/persons/{patient_id}/chart/diagnoses",
        )

        return items

    def _get_conditions_information(
        self, patient_id: str, params: Optional[dict[str, str]] = None
    ) -> tuple[Optional[list[NextGenEnterpriseDiagnosesEntryJSON]], Optional[Url]]:
        # DEV: Could be replaced by a `partial()` but that makes mypy unhappy
        return self._get_and_extract_items(
            self._cached_conditions_get, patient_id, params
        )

    def _cached_conditions_get(
        self,
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> NextGenEnterpriseDiagnosesJSON:
        resp_json: NextGenEnterpriseDiagnosesJSON = cast(
            NextGenEnterpriseDiagnosesJSON,
            _cached_get(
                session=self.session,
                url=f"{self.url}/persons/{patient_id}/chart/diagnoses",
                token_hash=_get_token_hash(self.session),
                params=params,
            ),
        )
        return resp_json

    def get_conditions_information_for_dump(
        self, patient_id: str
    ) -> Optional[list[NextGenEnterpriseDiagnosesEntryJSON]]:
        """Retrieve the diagnoses/conditions information for a patient for JSON dump.

        Includes predefined `$expand` options we want for JSON dumping purposes.

        Args:
            patient_id: The NextGen patient identifier for the target patient.

        Returns:
            A list of JSON objects containing information on diagnoses/conditions of
            the patient. The list may be empty. If there was no such list in the JSON
            at all, return None.
        """
        return self.get_conditions_information(
            patient_id, expand_options=["Diagnosis", "Encounter"]
        )

    # DEV: Just syntactic sugar as the endpoint is "diagnoses" but it _contains_
    #      conditions
    def get_diagnoses_information(
        self, patient_id: str
    ) -> Optional[list[NextGenEnterpriseDiagnosesEntryJSON]]:
        """Retrieve the diagnoses/conditions information for a patient.

        Args:
            patient_id: The NextGen patient identifier for the target patient.

        Returns:
            A list of JSON objects containing information on diagnoses/conditions of
            the patient. If there was no such list, return None.
        """
        return self.get_conditions_information(patient_id)

    def get_procedures_information(
        self, patient_id: str, expand_options: Optional[Collection[str]] = None
    ) -> Optional[list[NextGenEnterpriseProceduresEntryJSON]]:
        """Retrieve the procedures information for a patient.

        Args:
            patient_id: The NextGen patient identifier for the target patient.
            expand_options: `$expand` query args to pass through to the API call.

        Returns:
            A list of JSON objects containing information on procedures of the
            patient. The list may be empty. If there was no such list in the JSON at
            all, return None.
        """
        # Create `$expand` params if needed
        if expand_options is not None:
            params = {"$expand": ",".join(expand_options)}
        else:
            params = None

        items = self._retrieve_items_from_paginated_endpoint(
            self._get_procedures_information,
            patient_id,
            params,
            expected_path_end_formattable="/api/persons/{patient_id}/chart/procedures",
        )

        return items

    def _get_procedures_information(
        self, patient_id: str, params: Optional[dict[str, str]] = None
    ) -> tuple[Optional[list[NextGenEnterpriseProceduresEntryJSON]], Optional[Url]]:
        # DEV: Could be replaced by a `partial()` but that makes mypy unhappy
        return self._get_and_extract_items(
            self._cached_procedures_get, patient_id, params
        )

    def _cached_procedures_get(
        self,
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> NextGenEnterpriseProceduresJSON:
        resp_json: NextGenEnterpriseProceduresJSON = cast(
            NextGenEnterpriseProceduresJSON,
            _cached_get(
                session=self.session,
                url=f"{self.url}/persons/{patient_id}/chart/procedures",
                token_hash=_get_token_hash(self.session),
                params=params,
            ),
        )
        return resp_json

    def get_procedures_information_for_dump(
        self, patient_id: str
    ) -> Optional[list[NextGenEnterpriseProceduresEntryJSON]]:
        """Retrieve the procedures information for a patient for JSON dump.

        Includes predefined `$expand` options we want for JSON dumping purposes.

        Args:
            patient_id: The NextGen patient identifier for the target patient.

        Returns:
            A list of JSON objects containing information on procedures of the
            patient. The list may be empty. If there was no such list in the JSON at
            all, return None.
        """
        return self.get_procedures_information(
            patient_id, expand_options=["Encounter", "Procedure"]
        )

    def get_appointments_information(
        self,
        patient_id: str,
        appointment_temporal_state: Optional[AppointmentTemporalState] = None,
        expand_options: Optional[Collection[str]] = None,
    ) -> Optional[list[NextGenEnterpriseAppointmentsEntryJSON]]:
        """Retrieve the upcoming appointments information for a patient.

        Args:
            patient_id: The NextGen patient identifier for the target patient.
            appointment_temporal_state: Filter for appointments either in past or
              future. If None, returns all appointments.
            expand_options: `$expand` query args to pass through to the API call.
                This will always include at least `Appointment`.

        Returns:
            A list of JSON objects containing information on appointments for a
            patient. The list may be empty. If there was no such list in the JSON at
            all, return None.
        """
        # Create `$expand` params if needed
        if expand_options is not None:
            # We _always_ want `Appointment` here so add it if it's not already there
            expand_options_set = set(expand_options)
            expand_options_set.add("Appointment")
            params = {"$expand": ",".join(sorted(list(expand_options_set)))}
        else:
            params = {"$expand": "Appointment"}

        # Craft filter string
        filter_string = f"personId eq guid'{patient_id}'"
        # Add filter from today if looking at past or future
        if appointment_temporal_state is not None:
            # Convert today date to appropriate string format
            # Expected format is "%Y-%m-%dT%H:%M:%S", e.g. '2025-04-08T00:00:00'
            date_str = date.today().strftime(self.DATETIME_STR_FORMAT)

            if appointment_temporal_state is AppointmentTemporalState.FUTURE:
                filter_string += f" and appointmentDate gt datetime'{date_str}'"
            elif appointment_temporal_state is AppointmentTemporalState.PAST:
                filter_string += f" and appointmentDate lt datetime'{date_str}'"
            else:
                raise ValueError(
                    "Argument 'appointment_temporal_state' is invalid "
                    "for retrieving appointments information"
                )
        # Otherwise construct filter to get all appointments
        else:
            # Timestamp filter is still required to get all appointments.
            # Otherwise, only the appointments in the next 7 days is retrieved.
            filter_string += " and appointmentDate gt datetime'1900-01-01T00:00:00'"

        # Minimum params that we're expecting:
        # $expand=Appointment # handled elsewhere
        # &$filter=personId eq guid'{{personId}}' and appointmentDate gt datetime'2025-04-08T00:00:00'  # noqa: E501
        params["$filter"] = filter_string

        items = self._retrieve_items_from_paginated_endpoint(
            self._get_appointments_information,
            patient_id,
            params,
            expected_path_end_formattable="/api/appointments",
        )

        return items

    def _get_appointments_information(
        self,
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> tuple[Optional[list[NextGenEnterpriseAppointmentsEntryJSON]], Optional[Url]]:
        # DEV: Could be replaced by a `partial()` but that makes mypy unhappy
        return self._get_and_extract_items(
            self._cached_appointments_get, patient_id, params
        )

    def _cached_appointments_get(
        self,
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> NextGenEnterpriseAppointmentsJSON:
        """Cached call to GET:/api/appointments.

        Args:
            patient_id: Unused, but needed for callback protocol adherence.
                The patient ID to get appointments information for.
                Is instead encoded in the params.
            params: Any other query params to put in the GET request.

        Returns:
            The JSON returned from the request.
        """
        resp_json: NextGenEnterpriseAppointmentsJSON = cast(
            NextGenEnterpriseAppointmentsJSON,
            _cached_get(
                session=self.session,
                url=f"{self.url}/appointments",
                token_hash=_get_token_hash(self.session),
                params=params,
            ),
        )
        return resp_json

    def get_appointments_information_for_dump(
        self,
        patient_id: str,
    ) -> Optional[list[NextGenEnterpriseAppointmentsEntryJSON]]:
        """Retrieve the all appointments information for a patient for JSON dump.

        Includes predefined `$expand` options we want for JSON dumping purposes.

        Args:
            patient_id: The NextGen patient identifier for the target patient.

        Returns:
            A list of JSON objects containing information on appointments for a
            patient. The list may be empty. If there was no such list in the JSON at
            all, return None.
        """
        return self.get_appointments_information(
            patient_id,
            appointment_temporal_state=None,
            expand_options=["Appointment", "Encounter"],
        )

    def get_person_information(
        self, patient_id: str, expand_options: Optional[Collection[str]] = None
    ) -> Optional[NextGenEnterprisePersonJSON]:
        """Retrieve the personal information for a patient.

        Args:
            patient_id: The NextGen patient identifier for the target patient.
            expand_options: `$expand` query args to pass through to the API call.

        Returns:
            A JSON object containing the personal information of the patient. If
            there was no such object in the JSON at all, return None.
        """
        # Create `$expand` params if needed
        if expand_options is not None:
            params = {"$expand": ",".join(expand_options)}
        else:
            params = None

        output: Optional[NextGenEnterprisePersonJSON] = self._cached_person_get(
            patient_id,
            params=params,
        )
        if not output:
            output = None

        return output

    def _cached_person_get(
        self,
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> NextGenEnterprisePersonJSON:
        resp_json: NextGenEnterprisePersonJSON = cast(
            NextGenEnterprisePersonJSON,
            _cached_get(
                session=self.session,
                url=f"{self.url}/persons/{patient_id}",
                token_hash=_get_token_hash(self.session),
                params=params,
            ),
        )
        return resp_json

    def get_person_information_for_dump(
        self, patient_id: str
    ) -> Optional[NextGenEnterprisePersonJSON]:
        """Retrieve the personal information for a patient for JSON dump.

        Includes predefined `$expand` options we want for JSON dumping purposes.

        Args:
            patient_id: The NextGen patient identifier for the target patient.

        Returns:
            A JSON object containing the personal information of the patient. If
            there was no such object in the JSON at all, return None.
        """
        return self.get_person_information(
            patient_id,
            expand_options=[
                "AddressHistories",
                "Ethnicities",
                "GenderIdentities",
                "Races",
            ],
        )

    def get_patient_chart(
        self, patient_id: str, expand_options: Optional[Collection[str]] = None
    ) -> Optional[NextGenEnterpriseChartJSON]:
        """Retrieve the chart information for a patient.

        Args:
            patient_id: The NextGen patient identifier for the target patient.
            expand_options: `$expand` query args to pass through to the API call.

        Returns:
            A JSON object containing the chart of the patient. If there was no such
            object in the JSON at all, return None.
        """
        # Create `$expand` params if needed
        if expand_options is not None:
            params = {"$expand": ",".join(expand_options)}
        else:
            params = None

        output: Optional[NextGenEnterpriseChartJSON] = self._cached_chart_get(
            patient_id=patient_id,
            params=params,
        )
        if not output:
            output = None

        return output

    def _cached_chart_get(
        self,
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> NextGenEnterpriseChartJSON:
        resp_json: NextGenEnterpriseChartJSON = cast(
            NextGenEnterpriseChartJSON,
            _cached_get(
                session=self.session,
                url=f"{self.url}/persons/{patient_id}/chart",
                token_hash=_get_token_hash(self.session),
                params=params,
            ),
        )
        return resp_json

    def get_patient_chart_for_dump(
        self, patient_id: str
    ) -> Optional[NextGenEnterpriseChartJSON]:
        """Retrieve the chart information for a patient for JSON dump.

        Includes predefined `$expand` options we want for JSON dumping purposes.

        Args:
            patient_id: The NextGen patient identifier for the target patient.

        Returns:
            A JSON object containing the chart of the patient. If there was no such
            object in the JSON at all, return None.
        """
        return self.get_patient_chart(patient_id, expand_options=["SupportRoles"])

    def get_social_history(
        self, patient_id: str, expand_options: Optional[Collection[str]] = None
    ) -> Optional[list[NextGenEnterpriseSocialHistoryEntryJSON]]:
        """Retrieve the social history information for a patient.

        Args:
            patient_id: The NextGen patient identifier for the target patient.
            expand_options: `$expand` query args to pass through to the API call.

        Returns:
            A list of JSON objects containing information on social history for a
            patient. The list may be empty. If there was no such list in the JSON at
            all, return None.
        """
        # Create `$expand` params if needed
        if expand_options is not None:
            params = {"$expand": ",".join(expand_options)}
        else:
            params = None

        items = self._retrieve_items_from_paginated_endpoint(
            self._get_social_history,
            patient_id,
            params,
            expected_path_end_formattable="/persons/{personId}/chart/social-history",
        )

        return items

    def _get_social_history(
        self, patient_id: str, params: Optional[dict[str, str]] = None
    ) -> tuple[Optional[list[NextGenEnterpriseSocialHistoryEntryJSON]], Optional[Url]]:
        # DEV: Could be replaced by a `partial()` but that makes mypy unhappy
        return self._get_and_extract_items(
            self._cached_social_history_get, patient_id, params
        )

    def _cached_social_history_get(
        self,
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> NextGenEnterpriseSocialHistoryJSON:
        resp_json: NextGenEnterpriseSocialHistoryJSON = cast(
            NextGenEnterpriseSocialHistoryJSON,
            _cached_get(
                session=self.session,
                url=f"{self.url}/persons/{patient_id}/chart/social-history",
                token_hash=_get_token_hash(self.session),
                params=params,
            ),
        )
        return resp_json

    def get_encounters(
        self, patient_id: str, expand_options: Optional[Collection[str]] = None
    ) -> Optional[list[NextGenEnterpriseEncountersEntryJSON]]:
        """Retrieve the encounters information for a patient.

        Args:
            patient_id: The NextGen patient identifier for the target patient.
            expand_options: `$expand` query args to pass through to the API call.

        Returns:
            A list of JSON objects containing information on encounters for a
            patient. The list may be empty. If there was no such list in the JSON at
            all, return None.
        """
        # Create `$expand` params if needed
        if expand_options is not None:
            params = {"$expand": ",".join(expand_options)}
        else:
            params = None

        items = self._retrieve_items_from_paginated_endpoint(
            self._get_encounters,
            patient_id,
            params,
            expected_path_end_formattable="/persons/{personId}/chart/encounters",
        )

        return items

    def _get_encounters(
        self, patient_id: str, params: Optional[dict[str, str]] = None
    ) -> tuple[Optional[list[NextGenEnterpriseEncountersEntryJSON]], Optional[Url]]:
        # DEV: Could be replaced by a `partial()` but that makes mypy unhappy
        return self._get_and_extract_items(
            self._cached_encounters_get, patient_id, params
        )

    def _cached_encounters_get(
        self,
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> NextGenEnterpriseEncountersJSON:
        resp_json: NextGenEnterpriseEncountersJSON = cast(
            NextGenEnterpriseEncountersJSON,
            _cached_get(
                session=self.session,
                url=f"{self.url}/persons/{patient_id}/chart/encounters",
                token_hash=_get_token_hash(self.session),
                params=params,
            ),
        )
        return resp_json

    def get_encounters_for_dump(
        self, patient_id: str
    ) -> Optional[list[NextGenEnterpriseEncountersEntryJSON]]:
        """Retrieve the encounters information for a patient for JSON dump.

        Includes predefined `$expand` options we want for JSON dumping purposes.

        Args:
            patient_id: The NextGen patient identifier for the target patient.

        Returns:
            A list of JSON objects containing information on encounters for a
            patient. The list may be empty. If there was no such list in the JSON at
            all, return None.
        """
        return self.get_encounters(patient_id, expand_options=["Encounter"])

    def get_medications(
        self, patient_id: str, expand_options: Optional[Collection[str]] = None
    ) -> Optional[list[NextGenEnterpriseMedicationsEntryJSON]]:
        """Retrieve the medications information for a patient.

        Args:
            patient_id: The NextGen patient identifier for the target patient.
            expand_options: `$expand` query args to pass through to the API call.

        Returns:
            A list of JSON objects containing information on medications for a
            patient. The list may be empty. If there was no such list in the JSON at
            all, return None.
        """
        # Create `$expand` params if needed
        if expand_options is not None:
            params = {"$expand": ",".join(expand_options)}
        else:
            params = None

        items = self._retrieve_items_from_paginated_endpoint(
            self._get_medications,
            patient_id,
            params,
            expected_path_end_formattable="/persons/{personId}/chart/medications",
        )

        return items

    def _get_medications(
        self, patient_id: str, params: Optional[dict[str, str]] = None
    ) -> tuple[Optional[list[NextGenEnterpriseMedicationsEntryJSON]], Optional[Url]]:
        # DEV: Could be replaced by a `partial()` but that makes mypy unhappy
        return self._get_and_extract_items(
            self._cached_medications_get, patient_id, params
        )

    def _cached_medications_get(
        self,
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> NextGenEnterpriseMedicationsJSON:
        resp_json: NextGenEnterpriseMedicationsJSON = cast(
            NextGenEnterpriseMedicationsJSON,
            _cached_get(
                session=self.session,
                url=f"{self.url}/persons/{patient_id}/chart/medications",
                token_hash=_get_token_hash(self.session),
                params=params,
            ),
        )
        return resp_json

    def get_medications_for_dump(
        self, patient_id: str
    ) -> Optional[list[NextGenEnterpriseMedicationsEntryJSON]]:
        """Retrieve the medications information for a patient for JSON dump.

        Includes predefined `$expand` options we want for JSON dumping purposes.

        Args:
            patient_id: The NextGen patient identifier for the target patient.

        Returns:
            A list of JSON objects containing information on medications for a
            patient. The list may be empty. If there was no such list in the JSON at
            all, return None.
        """
        return self.get_medications(
            patient_id, expand_options=["Encounter", "Medication"]
        )

    def _retrieve_items_from_paginated_endpoint(
        self,
        single_page_retrieve_callable: _SinglePageRetrieveCallable[T_Item_Type],
        patient_id: str,
        query_params: Optional[dict[str, str]],
        expected_path_end_formattable: str,
    ) -> Optional[list[T_Item_Type]]:
        """Retrieve the list of `items` entries from paginated endpoint.

        Combines the `items` entries from each of the paginated JSON responses into
        a single list.

        Args:
            single_page_retrieve_callable: Callable that returns the `items` entry
                for a single paginated result as well as the next page link.
            patient_id: The NextGen patient identifier for the target patient.
            query_params: Additional query params to be passed to each page query.
            expected_path_end_formattable: Expected end of URL path component.
                This is used convert the next page link to the correct format.
                Should be a string in python `format()` compatible style containing
                a `patient_id` field. e.g. "/api/persons/{patient_id}/chart/procedures".

        Returns:
            A combined list of JSON objects as contained in the `items` entry of the
            endpoint response. The list may be empty. If there was no such list in
            the JSON at all, return None.
        """
        items: Optional[list[T_Item_Type]] = None

        # Handle first page of results
        new_items, next_page_url = single_page_retrieve_callable(
            patient_id, params=query_params
        )
        if new_items is not None:
            items = new_items

        # Handle subsequent pages of results
        while next_page_url:
            # The nextPageLink from NextGen is in a weird format. For instance,
            # for a base_url of "https://nativeapi.nextgen.com/nge/prod/nge-api/api",
            # the nextPageLink returned is
            # "http://127.0.0.1:889/VEND2-591.NextGenDemo/NextGen.Api.Edge/6.0.0.1719/api/persons/<personId>/chart/diagnoses?$skip=25"  # noqa: E501
            # with a host/start of path that seems to be linking as though within the
            # system. In order for us to access it externally, we need to verify that
            # it looks correct, and instead construct our expected URL.

            # Check that it looks like the path is mostly correct (particularly the end)

            if not self._is_next_page_link_form_correct(
                next_page_url,
                expected_path_end_formattable=expected_path_end_formattable,
                patient_id=patient_id,
            ):
                break

            # Use the params from the next page URL but construct it against our
            # known API URL
            new_items, next_page_url = single_page_retrieve_callable(
                patient_id,
                # nextPageLink contains any query params we passed into the original
                # call, plus `$skip`
                params=dict(next_page_url.query_params()),
            )
            if new_items is not None:
                if items is None:
                    items = new_items
                else:
                    items.extend(new_items)

        return items

    @staticmethod
    def _is_next_page_link_form_correct(
        next_page_url: Url, expected_path_end_formattable: str, patient_id: str
    ) -> bool:
        """Test if the nextPageLink URL matches an expected format at the end.

        Logs a warning if the nextPageLink does not match the expected format (with
        patient ID redacted).

        Args:
            next_page_url: The next page URL to check.
            expected_path_end_formattable: A formattable string for the expected path
                end. Must include a "{patient_id}" format field.
            patient_id: The patient ID to replace in the expected path end.

        Returns:
            True if the nextPageLink matches the expected format, False otherwise.
        """
        expected_path_end = expected_path_end_formattable.format(patient_id=patient_id)

        if not next_page_url.path or not next_page_url.path.endswith(expected_path_end):
            log_safe_path_end = expected_path_end.replace(
                patient_id, "<redactedPersonId>"
            )
            logger.warning(
                f"Unexpected nextPageLink; did not end with expected path:"
                f" {log_safe_path_end} (patient ID redacted)."
            )
            return False
        else:
            return True

    @staticmethod
    @overload
    def _get_and_extract_items(
        endpoint_get_callable: _EndpointGetCallable[NextGenEnterpriseDiagnosesJSON],
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> tuple[Optional[list[NextGenEnterpriseDiagnosesEntryJSON]], Optional[Url]]: ...

    @staticmethod
    @overload
    def _get_and_extract_items(
        endpoint_get_callable: _EndpointGetCallable[NextGenEnterpriseProceduresJSON],
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> tuple[Optional[list[NextGenEnterpriseProceduresEntryJSON]], Optional[Url]]: ...

    @staticmethod
    @overload
    def _get_and_extract_items(
        endpoint_get_callable: _EndpointGetCallable[NextGenEnterpriseAppointmentsJSON],
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> tuple[
        Optional[list[NextGenEnterpriseAppointmentsEntryJSON]], Optional[Url]
    ]: ...

    @staticmethod
    @overload
    def _get_and_extract_items(
        endpoint_get_callable: _EndpointGetCallable[NextGenEnterpriseMedicationsJSON],
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> tuple[
        Optional[list[NextGenEnterpriseMedicationsEntryJSON]], Optional[Url]
    ]: ...

    @staticmethod
    @overload
    def _get_and_extract_items(
        endpoint_get_callable: _EndpointGetCallable[NextGenEnterpriseEncountersJSON],
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> tuple[Optional[list[NextGenEnterpriseEncountersEntryJSON]], Optional[Url]]: ...

    @staticmethod
    @overload
    def _get_and_extract_items(
        endpoint_get_callable: _EndpointGetCallable[NextGenEnterpriseSocialHistoryJSON],
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> tuple[
        Optional[list[NextGenEnterpriseSocialHistoryEntryJSON]], Optional[Url]
    ]: ...

    @staticmethod
    def _get_and_extract_items(
        endpoint_get_callable: _EndpointGetCallable[T_Endpoint_Response_Type],
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> tuple[Optional[list[T_Item_Type]], Optional[Url]]:
        """Get a single page's worth of `items` information for a patient.

        Will return an empty list if no `items` were found in the returned JSON,
        will return None if there was no `items` entry at all in the JSON.

        Will also return the next page URL if present, else None.

        Args:
            endpoint_get_callable: The callable to make a call to the NextGen API
                and return the returned JSON. Should be cached.
            patient_id: The ID of the patient.
            params: Any additional query params to include in the request.

        Returns:
            A tuple containing the list of `items` and the next page URL,
            if present, else None
        """
        resp_json = endpoint_get_callable(
            patient_id,
            params=params,
        )

        items: Optional[list[T_Item_Type]] = pydash.get(
            resp_json,
            "items",
        )
        next_page_url: Optional[Url] = (
            Url(url_str) if (url_str := pydash.get(resp_json, "nextPageLink")) else None
        )

        return items, next_page_url

    def get_bulk_patient_info(
        self,
        patient_id: str,
    ) -> Optional[BulkPatientInfo]:
        """Retrieve bulk patient information for a given patient ID.

        If unable to find, or patient has no relevant information, return None.

        This method is a sugar method for the cases where _all_ information for a
        given patient might be needed. Generally the specific calls should be used in
        preference to avoid unnecessary API calls to NextGen.

        Returned patient information contains:
            - list of diagnoses/conditions for the patient
            - list of procedures for the patient
            - list of future appointments
            - list of past appointments

        Args:
            patient_id: The NextGen patient identifier for the target patient.

        Returns:
            A BulkPatientInfo object containing information on the patient. If no
            information could be retrieved, returns None.
        """
        conditions: Optional[list[NextGenEnterpriseDiagnosesEntryJSON]] = None
        try:
            conditions = self.get_conditions_information(patient_id)
        except Exception as e:
            logger.error(
                f"Unable to retrieve conditions information for patient: {str(e)}"
            )
        if conditions is None:
            logger.warning(
                "Patient conditions/diagnoses information could not be retrieved"
            )

        procedures: Optional[list[NextGenEnterpriseProceduresEntryJSON]] = None
        try:
            procedures = self.get_procedures_information(patient_id)
        except Exception as e:
            logger.error(
                f"Unable to retrieve procedures information for patient: {str(e)}"
            )
        if procedures is None:
            logger.warning("Patient procedures information could not be retrieved")

        future_appointments: Optional[list[NextGenEnterpriseAppointmentsEntryJSON]] = (
            None
        )
        try:
            future_appointments = self.get_appointments_information(
                patient_id, appointment_temporal_state=AppointmentTemporalState.FUTURE
            )
        except Exception as e:
            logger.error(
                f"Unable to retrieve upcoming appointments information for patient:"
                f" {str(e)}"
            )
        if future_appointments is None:
            logger.warning(
                "Patient upcoming appointments information could not be retrieved"
            )

        past_appointments: Optional[list[NextGenEnterpriseAppointmentsEntryJSON]] = None
        try:
            past_appointments = self.get_appointments_information(
                patient_id, appointment_temporal_state=AppointmentTemporalState.PAST
            )
        except Exception as e:
            logger.error(
                f"Unable to retrieve past appointments information for patient:"
                f" {str(e)}"
            )
        if past_appointments is None:
            logger.warning(
                "Patient past appointments information could not be retrieved"
            )

        if any(
            i is not None
            for i in (conditions, procedures, future_appointments, past_appointments)
        ):
            return BulkPatientInfo(
                conditions=conditions if conditions is not None else [],
                procedures=procedures if procedures is not None else [],
                future_appointments=(
                    future_appointments if future_appointments is not None else []
                ),
                past_appointments=(
                    past_appointments if past_appointments is not None else []
                ),
            )
        else:
            return None

    def yield_document_infos(self, patient_id: str) -> Iterable[List[DocumentInfo]]:
        """Yields pages of document infos."""
        # Gets the first page of document_infos
        document_infos, next_page_url = self.get_documents_information(patient_id)
        yield document_infos

        # Handle subsequent pages of results
        while next_page_url:
            # The nextPageLink from NextGen is in a weird format. For instance,
            # for a base_url of "https://nativeapi.nextgen.com/nge/prod/nge-api/api",
            # the nextPageLink returned is
            # "http://127.0.0.1:889/VEND2-591.NextGenDemo/NextGen.Api.Edge/6.0.0.1719/api/persons/<personId>/chart/diagnoses?$skip=25"  # noqa: E501
            # with a host/start of path that seems to be linking as though within the
            # system. In order for us to access it externally, we need to verify that
            # it looks correct, and instead construct our expected URL.

            # Check that it looks like the path is mostly correct (particularly the end)
            if not self._is_next_page_link_form_correct(
                next_page_url=next_page_url,
                expected_path_end_formattable="/api/persons/{patient_id}/chart/documents",
                patient_id=patient_id,
            ):
                break

            # Use the params from the next page URL but construct it against our
            # known API URL
            document_infos, next_page_url = self.get_documents_information(
                patient_id, params=dict(next_page_url.query_params())
            )

            yield document_infos

    def _format_timestamp_to_date_str(
        self, datetime_str: Optional[str]
    ) -> Optional[str]:
        if datetime_str is None:
            return None

        # Take only part of the datetime string before T
        return datetime_str.split("T")[0]

    def get_documents_information(
        self, patient_id: str, params: Optional[dict[str, str]] = None
    ) -> Tuple[List[DocumentInfo], Optional[Url]]:
        """Get a single page of documents information for a patient.

        Will return an empty list if no documents were found.

        Will also return the next page URL if present, else None.

        Args:
            patient_id: The ID of the patient.
            params: Any additional query params to include in the request,
                usually the $skip= param for pagination.

        Returns:
            A tuple containing:
              - the list of DocumentInfo if present, else [].
              - the next page URL, if present, else None
        """
        try:
            resp_json = self._cached_documents_get(
                patient_id,
                params=params,
            )
        except HTTPError as e:
            logger.warning(f"Failed to get page of documents: {e}.")
            return [], None

        document_infos = [
            DocumentInfo(
                document_id=item["id"],
                document_date=self._format_timestamp_to_date_str(
                    item.get("createTimestampUtc")
                )
                or "",
                document_description=item.get("description", ""),
            )
            for item in resp_json.get("items", [])
        ]
        next_page_url: Optional[Url] = (
            Url(url_str) if (url_str := pydash.get(resp_json, "nextPageLink")) else None
        )

        return document_infos, next_page_url

    def _cached_documents_get(
        self,
        patient_id: str,
        params: Optional[dict[str, str]] = None,
    ) -> NextGenEnterpriseDocumentsJSON:
        resp_json: NextGenEnterpriseDocumentsJSON = cast(
            NextGenEnterpriseDocumentsJSON,
            _cached_get(
                session=self.session,
                url=f"{self.url}/persons/{patient_id}/chart/documents",
                token_hash=_get_token_hash(self.session),
                params=params,
            ),
        )
        return resp_json

    def download_documents_batch(
        self, path: Path, patient_id: str, document_infos: List[DocumentInfo]
    ) -> Tuple[List[str], List[str]]:
        """Downloads a batch of documents given a list of document ids.

        Args:
            path: Download path for the document to be saved.
            patient_id: The ID of the patient.
            document_infos: List of document IDs to be downloaded.

        Returns:
            A tuple containing:
              - list of documents that downloaded successfully.
              - list of documents that could not be downloaded.
        """
        success_documents = []
        failed_documents = []
        for doc_info in document_infos:
            if self._download_document(path, patient_id, doc_info):
                success_documents.append(doc_info.document_id)
            else:
                failed_documents.append(doc_info.document_id)

        return success_documents, failed_documents

    def _download_document(
        self, path: Path, patient_id: str, document_info: DocumentInfo
    ) -> bool:
        """Download a single document."""
        document_id = document_info.document_id
        try:
            resp = self.session.get(
                f"{self.url}/persons/{patient_id}/chart/documents/{document_id}/pdf",
            )
            resp.raise_for_status()

        except HTTPError as e:
            logger.warning(f"Failed to download {document_id}: {e}")

            return False
        else:
            if document_info.document_date or document_info.document_description:
                file_name = slugify(
                    f"{document_info.document_date}-"
                    f"{document_info.document_description}"
                )
                if len(file_name) > 40:
                    logger.info("Truncating file name as description is too long.")
                    file_name = file_name[:40]
            else:
                file_name = f"{document_id}"

            truncated_doc_id = document_info.document_id[:15]
            with open(path / f"{file_name}_{truncated_doc_id}.pdf", "wb") as f:
                f.write(resp.content)
            return True
