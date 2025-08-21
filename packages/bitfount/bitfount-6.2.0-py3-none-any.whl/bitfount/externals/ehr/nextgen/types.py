"""Types related to NextGen interactions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, List, Literal, Optional, TypeVar

from typing_extensions import (
    NotRequired,
    # We import this version of TypedDict rather than typing.TypedDict as in Python
    # <3.11 typing.TypedDict does not support generics in TypedDict.
    # TODO: [Python 3.11]
    TypedDict as ExtendedTypedDict,
)


########################################
# NextGen FHIR API JSON Objects: Start #
########################################
class FHIRBundleJSON(ExtendedTypedDict):
    """JSON Object for patient search results.

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    resourceType: Literal["Bundle"]
    entry: NotRequired[Optional[list[FHIRBundleEntryJSON]]]


class FHIRBundleEntryJSON(ExtendedTypedDict):
    """JSON Object for patient search results entry objects.

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    fullUrl: str
    resource: FHIRBundleResourceJSON


class FHIRBundleResourceJSON(ExtendedTypedDict):
    """JSON Object for patient search results resource objects.

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    resourceType: Literal["Patient"]
    id: str
    name: list[PatientNameJSON]
    gender: str  # e.g. male
    birthDate: str  # datestring (format "1975-07-17")
    identifier: List
    address: List[dict]
    telecom: List[dict]


class PatientNameJSON(ExtendedTypedDict):
    """JSON Object for patient name objects.

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    given: list[str]
    family: str


class RetrievedPatientDetailsJSON(ExtendedTypedDict):
    """JSON Object for patient details retrieved.

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    id: str
    given_name: Optional[str]
    family_name: Optional[str]
    date_of_birth: Optional[str]
    gender: Optional[str]
    home_numbers: List[str]
    cell_numbers: List[str]
    emails: List[str]
    mailing_address: Optional[str]
    medical_record_number: Optional[str]

    # legal_ability: Optional[bool]
    # eye_physician: Optional[str]


######################################
# NextGen FHIR API JSON Objects: End #
######################################


##############################################
# NextGen Enterprise API JSON Objects: Start #
##############################################
# DEV: See https://www.notion.so/bitfount/NextGen-Enterprise-JSONs-and-Examples-20aa5f6187c180369999d1ec8f157a09#20aa5f6187c180b7a17ac9ef1a996f21 # noqa: E501
#      for examples of these JSON objects.
T = TypeVar("T")


class _NextGenEnterprisePaginatedJSON(Generic[T], ExtendedTypedDict):
    """Genericised paginated form for NextGen Enterprise JSON."""

    items: list[T]
    # link to the next page of results, if available
    nextPageLink: NotRequired[Optional[str]]


class NextGenEnterpriseDiagnosesEntryJSON(ExtendedTypedDict):
    """JSON Object for patient diagnoses return object entries.

    i.e. entries from a call to [enterprise_url]/persons/[patient_id]/chart/diagnoses

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    id: str  # uuid
    personId: str  # uuid
    encounterId: str  # uuid
    encounterTimestamp: str  # timestring (format "2025-01-31T11:16:53")
    encounterTimestampUtc: str  # timestring (format "2025-01-31T16:16:53")
    encounterTimestampLocalUtcOffset: int  # (format -18000)
    billingDescription: str  # e.g. "Partial retinal artery occlusion, unspecified eye"
    onsetDate: str  # timestring (format "2025-01-31T00:00:00")

    # These are only present in the JSON if the corresponding `$expand` query
    # parameter is passed to the request (e.g. `$expand=AddressHistories`)
    diagnosis: NotRequired[NextGenEnterpriseDiagnosisJSON]
    encounter: NotRequired[NextGenEnterpriseEncounterJSON]

    # DEV: these are the elements we're most likely to care about
    icdCode: str  # ICD code (e.g. "H34.219")
    icdCodeSystem: str  # ICD code family type (e.g. "10")
    description: str  # e.g. "Partial retinal artery occlusion, unspecified eye"


class NextGenEnterpriseDiagnosisJSON(ExtendedTypedDict):
    """JSON Object for specific patient diagnosis return object.

    i.e. entries from a call to
    [enterprise_url]/persons/[patient_id]/chart/diagnoses/[diagnosis_id]

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    pass


class NextGenEnterpriseDiagnosesJSON(
    _NextGenEnterprisePaginatedJSON[NextGenEnterpriseDiagnosesEntryJSON]
):
    """JSON Object for patient diagnoses return object.

    i.e. a call to [enterprise_url]/persons/[patient_id]/chart/diagnoses

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    pass


class NextGenEnterpriseProceduresEntryJSON(ExtendedTypedDict):
    """JSON Object for patient procedures return object entries.

    i.e. entries from a call to [enterprise_url]/persons/[patient_id]/chart/procedures

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    id: str  # uuid
    personId: str  # uuid
    encounterId: str  # uuid
    encounterTimestamp: str  # timestring (format "2025-01-31T11:16:53")
    encounterTimestampUtc: str  # timestring (format "2025-01-31T16:16:53")
    encounterTimestampLocalUtcOffset: int  # (format -18000)

    # These are only present in the JSON if the corresponding `$expand` query
    # parameter is passed to the request (e.g. `$expand=AddressHistories`)
    encounter: NotRequired[NextGenEnterpriseEncounterJSON]
    procedure: NotRequired[NextGenEnterpriseProcedureJSON]

    # DEV: these are the elements we're most likely to care about
    serviceItemId: str  # e.g. "67028"
    serviceItemDescription: str  # e.g. "INJECTION EYE DRUG"
    cpt4Code: str  # e.g. "67028"
    serviceDate: str  # timestring (format "2025-02-04T00:00:00")
    isCompleted: bool
    status: str  # e.g. "Completed"


class NextGenEnterpriseProcedureJSON(ExtendedTypedDict):
    """JSON Object for specific patient procedure return object.

    i.e. entries from a call to
    [enterprise_url]/persons/[patient_id]/chart/encounters/[encounter_id]/procedures/[procedure_id]

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """  # noqa: E501

    pass


class NextGenEnterpriseProceduresJSON(
    _NextGenEnterprisePaginatedJSON[NextGenEnterpriseProceduresEntryJSON]
):
    """JSON Object for patient procedures return object.

    i.e. a call to [enterprise_url]/persons/[patient_id]/chart/procedures

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    pass


class _NextGenEnterpriseSharedAppointmentsJSONDetails(ExtendedTypedDict):
    """Shared fields for appointments(s) return type."""

    id: str  # uuid
    eventId: str  # uuid
    eventName: str  # e.g. "3 Month Follow-Up"

    # Person-related
    personId: str  # uuid
    firstName: str  # e.g. "Bit"
    middleName: str  # e.g. ""
    lastName: str  # e.g. "Fount"

    # Appointment status related
    appointmentConfirmed: bool
    appointmentNumber: int  # e.g. 19803
    isCancelled: bool
    isDeleted: bool

    # Appointment time related
    appointmentDate: str  # timestring (format "2027-10-08T00:00:00")
    beginTime: str  # e.g. "0820"
    endTime: str  # e.g. "0835"
    duration: int  # e.g. 15

    # Appointment location related
    locationName: str  # e.g. "Pediatrics Location"
    locationId: str  # uuid


class NextGenEnterpriseAppointmentsEntryJSON(
    _NextGenEnterpriseSharedAppointmentsJSONDetails
):
    """JSON Object for appointments return object entries.

    i.e. entries from a call to [enterprise_url]/appointments?$expand=Appointment

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    # These are only present in the JSON if the corresponding `$expand` query
    # parameter is passed to the request (e.g. `$expand=AddressHistories`)
    appointment: NotRequired[NextGenEnterpriseAppointmentJSON]
    encounter: NotRequired[NextGenEnterpriseEncounterJSON]


class NextGenEnterpriseAppointmentsJSON(
    _NextGenEnterprisePaginatedJSON[NextGenEnterpriseAppointmentsEntryJSON]
):
    """JSON Object for appointments return object.

    i.e. a call to [enterprise_url]/appointments?$expand=Appointment

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    pass


class NextGenEnterpriseAppointmentJSON(_NextGenEnterpriseSharedAppointmentsJSONDetails):
    """JSON Object for appointment return object.

    i.e. entries from [enterprise_url]/appointments/[appointment_id]

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    pass


class NextGenEnterpriseDocumentsEntryJSON(ExtendedTypedDict):
    """JSON Object for patient documents return object entries.

    i.e. entries from a call to [enterprise_url]/persons/[patient_id]/chart/documents

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    id: str  # uuid
    personId: str  # uuid
    encounterId: str  # uuid
    description: str
    itemType: str
    fileType: str
    createTimestamp: str  # timestring (format "2025-01-31T11:16:53")
    createTimestampUtc: str  # timestring (format "2025-01-31T16:16:53")
    createTimestampLocalUtcOffset: int  # (format -18000)

    # DEV: these are the elements we're most likely to care about
    isSensitive: bool


class NextGenEnterpriseDocumentsJSON(
    _NextGenEnterprisePaginatedJSON[NextGenEnterpriseDocumentsEntryJSON]
):
    """JSON Object for patient documents return object.

    i.e. a call to [enterprise_url]/persons/[patient_id]/chart/documents

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    pass


class NextGenEnterpriseAddressHistoriesEntryJSON(ExtendedTypedDict):
    """JSON Object for patient address history information return object entry.

    i.e. a call to [enterprise_url]/persons/[patient_id]/address-histories

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    pass


NextGenEnterpriseAddressHistoriesJSON = list[NextGenEnterpriseAddressHistoriesEntryJSON]
"""JSON Object for patient address history information return object.

i.e. a call to [enterprise_url]/persons/[patient_id]/address-histories

Note: this is an incomplete JSON object, only containing the elements we care about.
"""


class NextGenEnterpriseGenderIdentitiesEntryJSON(ExtendedTypedDict):
    """JSON Object for patient gender identity information return object entry.

    i.e. a call to [enterprise_url]/persons/[patient_id]/gender-identities

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    pass


NextGenEnterpriseGenderIdentitiesJSON = list[NextGenEnterpriseGenderIdentitiesEntryJSON]
"""JSON Object for patient gender identity information return object.

i.e. a call to [enterprise_url]/persons/[patient_id]/gender-identities

Note: this is an incomplete JSON object, only containing the elements we care about.
"""


class NextGenEnterpriseEthnicitiesEntryJSON(ExtendedTypedDict):
    """JSON Object for patient ethnicities information return object entry.

    i.e. a call to [enterprise_url]/persons/[patient_id]/ethnicities

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    id: str  # uuid
    personId: str  # uuid

    description: str


NextGenEnterpriseEthnicitiesJSON = list[NextGenEnterpriseEthnicitiesEntryJSON]
"""JSON Object for patient ethnicities information return object.

i.e. a call to [enterprise_url]/persons/[patient_id]/ethnicities

Note: this is an incomplete JSON object, only containing the elements we care about.
"""


class NextGenEnterpriseRacesEntryJSON(ExtendedTypedDict):
    """JSON Object for patient races information return object entry.

    i.e. a call to [enterprise_url]/persons/[patient_id]/races

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    id: str  # uuid
    personId: str  # uuid

    description: str


NextGenEnterpriseRacesJSON = list[NextGenEnterpriseRacesEntryJSON]
"""JSON Object for patient races information return object.

i.e. a call to [enterprise_url]/persons/[patient_id]/races

Note: this is an incomplete JSON object, only containing the elements we care about.
"""

# DEV: Some keys are of a form that are invalid Python identifiers so they can't just
#      be supplied in the class-style TypedDict definitions. Instead we define them
#      here as a mixin.
_NextGenEnterprisePersonJSONInvalidKeys = ExtendedTypedDict(
    "_NextGenEnterprisePersonJSONInvalidKeys",
    {
        # These are only present in the JSON if the corresponding `$expand` query
        # parameter is passed to the request (e.g. `$expand=AddressHistories`)
        "address-histories": NotRequired[NextGenEnterpriseAddressHistoriesJSON],
        "gender-identities": NotRequired[NextGenEnterpriseGenderIdentitiesJSON],
    },
)


class NextGenEnterprisePersonJSON(
    ExtendedTypedDict, _NextGenEnterprisePersonJSONInvalidKeys
):
    """JSON Object for patient information return object.

    i.e. a call to [enterprise_url]/persons/[patient_id]

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    id: str  # uuid

    firstName: str
    middleName: NotRequired[Optional[str]]
    lastName: str

    dateOfBirth: str  # timestamp of form 1975-07-17T00:00:00

    sex: str

    # These are only present in the JSON if the corresponding `$expand` query
    # parameter is passed to the request (e.g. `$expand=AddressHistories`)
    chart: NotRequired[NextGenEnterpriseChartJSON]
    ethnicities: NotRequired[NextGenEnterpriseEthnicitiesJSON]
    races: NotRequired[NextGenEnterpriseRacesJSON]


class NextGenEnterpriseSocialHistoryEntryJSON(ExtendedTypedDict):
    """JSON Object for social history return object entries.

    i.e. entries from a call to
    [enterprise_url]/persons/[patient_id]/chart/social-history

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    personId: str  # uuid

    smokingStatus: str
    alcoholYearQuit: Optional[str]  # unknown type


class NextGenEnterpriseSocialHistoryJSON(
    _NextGenEnterprisePaginatedJSON[NextGenEnterpriseSocialHistoryEntryJSON]
):
    """JSON Object for social history return object.

    i.e. a call to [enterprise_url]/persons/[patient_id]/chart/social-history

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    pass


class NextGenEnterpriseSupportRolesEntryJSON(ExtendedTypedDict):
    """JSON Object for patient support roles information return object entry.

    i.e. a call to [enterprise_url]/persons/[patient_id]/chart/support-roles

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    pass


NextGenEnterpriseSupportRolesJSON = list[NextGenEnterpriseSupportRolesEntryJSON]
"""JSON Object for patient support roles information return object.

i.e. a call to [enterprise_url]/persons/[patient_id]/chart/support-roles

Note: this is an incomplete JSON object, only containing the elements we care about.
"""


class NextGenEnterpriseEncountersEntryJSON(ExtendedTypedDict):
    """JSON Object for patient encounters return object entries.

    i.e. entries from a call to [enterprise_url]/persons/[patient_id]/chart/encounters

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    id: str  # uuid
    personId: str  # uuid

    locationId: str  # uuid
    locationName: str

    status: str

    # timestamp of form "2025-05-07T11:27:49.547" (note that the millisecond
    # component is not consistently present)
    timestamp: str

    # name of individual who rendered/referred to the service (i.e. the
    # doctor/medical practitioner)
    renderingProviderName: Optional[str]
    referringProviderName: Optional[str]

    # These are only present in the JSON if the corresponding `$expand` query
    # parameter is passed to the request (e.g. `$expand=AddressHistories`)
    encounter: NotRequired[NextGenEnterpriseEncounterJSON]


class NextGenEnterpriseEncounterJSON(ExtendedTypedDict):
    """JSON Object for specific patient encounter return object.

    i.e. entries from a call to
    [enterprise_url]/persons/[patient_id]/chart/encounters/[encounter_id]

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    pass


class NextGenEnterpriseEncountersJSON(
    _NextGenEnterprisePaginatedJSON[NextGenEnterpriseEncountersEntryJSON]
):
    """JSON Object for patient encounters return object.

    i.e. entries from a call to [enterprise_url]/persons/[patient_id]/chart/encounters

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    pass


class NextGenEnterpriseMedicationsEntryJSON(ExtendedTypedDict):
    """JSON Object for patient medications return object entries.

    i.e. entries from a call to [enterprise_url]/persons/[patient_id]/chart/medications

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    # These are only present in the JSON if the corresponding `$expand` query
    # parameter is passed to the request (e.g. `$expand=AddressHistories`)
    encounter: NotRequired[NextGenEnterpriseEncounterJSON]
    medication: NotRequired[NextGenEnterpriseMedicationJSON]


class NextGenEnterpriseMedicationJSON(ExtendedTypedDict):
    """JSON Object for specific patient medication return object.

    i.e. entries from a call to
    [enterprise_url]/persons/[patient_id]/chart/medications/[medication_id]

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    pass


class NextGenEnterpriseMedicationsJSON(
    _NextGenEnterprisePaginatedJSON[NextGenEnterpriseMedicationsEntryJSON]
):
    """JSON Object for patient medications return object.

    i.e. entries from a call to [enterprise_url]/persons/[patient_id]/chart/medications

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    pass


# DEV: Some keys are of a form that are invalid Python identifiers so they can't just
#      be supplied in the class-style TypedDict definitions. Instead we define them
#      here as a mixin.
_NextGenEnterpriseChartJSONInvalidKeys = ExtendedTypedDict(
    "_NextGenEnterpriseChartJSONInvalidKeys",
    {
        # These are only present in the JSON if the corresponding `$expand` query
        # parameter is passed to the request (e.g. `$expand=AddressHistories`)
        "social-history": NotRequired[NextGenEnterpriseSocialHistoryJSON],
        "support-roles": NotRequired[NextGenEnterpriseSupportRolesJSON],
    },
)


class NextGenEnterpriseChartEntryJSON(
    ExtendedTypedDict, _NextGenEnterpriseChartJSONInvalidKeys
):
    """JSON Object for patient chart information return object entry.

    i.e. a call to [enterprise_url]/persons/[patient_id]/chart

    Note: this is an incomplete JSON object, only containing the elements we care about.
    """

    personId: str  # uuid
    medicalRecordNumber: str

    # These are only present in the JSON if the corresponding `$expand` query
    # parameter is passed to the request (e.g. `$expand=AddressHistories`)
    diagnoses: NotRequired[NextGenEnterpriseDiagnosesJSON]
    encounters: NotRequired[NextGenEnterpriseEncountersJSON]
    medications: NotRequired[NextGenEnterpriseMedicationsJSON]
    procedures: NotRequired[NextGenEnterpriseProceduresJSON]


NextGenEnterpriseChartJSON = list[NextGenEnterpriseChartEntryJSON]
"""JSON Object for patient chart information return object.

i.e. a call to [enterprise_url]/persons/[patient_id]/chart

Note: this is an incomplete JSON object, only containing the elements we care about.
"""

############################################
# NextGen Enterprise API JSON Objects: End #
############################################


########################################
# NextGen API Interaction Types: Start #
########################################
@dataclass(frozen=True)
class PatientCodeDetails:
    """Container indicating the diagnosis and treatment codes for a given patient."""

    # Note: A None value indicates error during EHR query, while
    # an empty list indicates absence of any condition/medication codes.
    condition_codes: Optional[list[str]]  # e.g. ICD10/SNOMED codes
    procedure_codes: Optional[list[str]]  # e.g. CPT4 codes


@dataclass
class BulkPatientInfo:
    """Container class for NextGen EHR query results."""

    conditions: list[NextGenEnterpriseDiagnosesEntryJSON] = field(default_factory=list)
    procedures: list[NextGenEnterpriseProceduresEntryJSON] = field(default_factory=list)
    future_appointments: list[NextGenEnterpriseAppointmentsEntryJSON] = field(
        default_factory=list
    )
    past_appointments: list[NextGenEnterpriseAppointmentsEntryJSON] = field(
        default_factory=list
    )


######################################
# NextGen API Interaction Types: End #
######################################
