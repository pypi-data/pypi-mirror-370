import logging
from typing import cast

from google.protobuf.timestamp_pb2 import Timestamp
from ....private_eye.consts import SectionName
from ....private_eye.data import PatientData
from ....private_eye.exceptions import ImageParseException
from ....private_eye.external.external_pb2 import ExternalData
from ....private_eye.heidelberg.data import DbFiles, PatientExamSeries, Segment
from ....private_eye.heidelberg.metadata_builder.abstract_data_builder import DataBuilder
from ....private_eye.heidelberg.parser import PatientSegment
from ....private_eye.utils.optional import get_optional, map_optional

logger = logging.getLogger(__name__)


class _PatientDataBuilder(DataBuilder[PatientData]):
    name = SectionName.PATIENT
    requires = [PatientSegment]

    def build(self, pes: PatientExamSeries, db_files: DbFiles) -> PatientData:
        # Quite a high proportion of files return multiple patient segments, we assume this is because they are updated
        # by the operator, and the last one will be the most up to date.
        try:
            patient_segment: Segment[PatientSegment] = db_files.pdb.get_segments(PatientSegment)[-1]
        except IndexError as error:
            if self.external_data:
                return self._patient_from_external_data(pes, self.external_data)
            raise ImageParseException("Cannot parse image with no PatientSegment or external data") from error
        return self._patient_from_segment(pes, patient_segment)

    @staticmethod
    def _patient_from_segment(pes: PatientExamSeries, segment: Segment[PatientSegment]) -> PatientData:
        patient = segment.body
        return PatientData(
            patient_key=patient.patient_key,
            first_name=patient.given_name,
            last_name=patient.surname,
            date_of_birth=patient.birthdate,
            gender=patient.sex,
            source_id=str(get_optional(pes.patient_id)),
        )

    @staticmethod
    def _patient_from_external_data(pes: PatientExamSeries, external_data: ExternalData.Heidelberg) -> PatientData:
        if pes.patient_id != external_data.patient_pid:
            raise ImageParseException("Patient PID does not match PID from external data")
        return PatientData(
            patient_key=external_data.patient_id,
            first_name=external_data.patient_first_name,
            last_name=external_data.patient_last_name,
            date_of_birth=map_optional(cast(Timestamp, external_data.patient_dob), lambda ts: ts.ToDatetime().date()),
            gender=external_data.patient_sex,
            source_id=str(get_optional(pes.patient_id)),
        )
