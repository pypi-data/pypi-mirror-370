"""EHR types."""

from dataclasses import dataclass
from datetime import date
from typing import Optional

DATE_STR_FORMAT = "%Y-%m-%d"


@dataclass
class EHRAppointment:
    """Class for Patient Appointment."""

    appointment_date: Optional[date]
    location_name: Optional[str]
    event_name: Optional[str]

    def format_for_csv(self) -> dict[str, str]:
        """Format into a readable dictionary for csv."""
        output = {}

        if self.appointment_date:
            output["Appointment Date"] = self.appointment_date.strftime(DATE_STR_FORMAT)
        if self.location_name:
            output["Location Name"] = self.location_name
        if self.event_name:
            output["Event Name"] = self.event_name

        return output
