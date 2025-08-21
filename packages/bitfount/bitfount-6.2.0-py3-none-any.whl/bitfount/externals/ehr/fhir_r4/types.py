"""FHIR R4 resource types."""

from typing import ClassVar

from fhir.resources.appointment import Appointment
from fhir.resources.condition import Condition
from fhir.resources.patient import Patient
from fhir.resources.procedure import Procedure


class FHIRPatient(Patient):
    """Type for Patient resource from FHIR endpoint."""

    resourceType: ClassVar[str] = "Patient"
    __init__ = Patient.__init__


class FHIRAppointment(Appointment):
    """Type for Appointment resource from FHIR endpoint."""

    resourceType: ClassVar[str] = "Appointment"
    __init__ = Appointment.__init__


class FHIRCondition(Condition):
    """Type for Condition resource from FHIR endpoint."""

    resourceType: ClassVar[str] = "Condition"
    __init__ = Condition.__init__


class FHIRProcedure(Procedure):
    """Type for Procedure resource from FHIR endpoint."""

    resourceType: ClassVar[str] = "Procedure"
    __init__ = Procedure.__init__
