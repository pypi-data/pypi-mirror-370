import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional

import attr
from .....private_eye.consts import ImageModality
from .....private_eye.data import ImageData, SeriesResult
from .....private_eye.output_formatter.dicom.dicom_helpers import (
    DEFAULT_DATE,
    DEFAULT_TIME,
    crop_number,
    format_date,
    format_time,
    generate_uid_from_source,
    render_name,
)
from .....private_eye.utils.optional import convert_or_default, map_optional
from pydicom import Dataset
from pydicom.tag import Tag
from pydicom.uid import UID

if TYPE_CHECKING:
    from .....private_eye.output_formatter.dicom.classes.common import DicomClass

logger = logging.getLogger(__name__)


@attr.s(auto_attribs=True, frozen=True)
class DicomData:
    image_processing_options: str
    parser_result: SeriesResult
    image: ImageData
    bits_stored: int
    pixel_data: bytes
    uid: UID


class DicomModule(ABC):
    def __init__(self, parent: "DicomClass"):
        self.parent = parent

    @abstractmethod
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        raise NotImplementedError()


class SOPCommon(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        ds.SOPClassUID = self.parent.get_sop_class(data)
        ds.SOPInstanceUID = self.parent.generate_image_uid(data.parser_result, data.image)
        ds.SpecificCharacterSet = "ISO_IR 192"  # Unicode


class Patient(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        if self.parent.is_anonymised:
            ds.PatientID = "Anonymous"
            ds.PatientName = render_name("Anonymous", "Anonymous")
            ds.PatientBirthDate = DEFAULT_DATE
            ds.PatientSex = ""
        else:
            patient_data = data.parser_result.patient
            ds.PatientID = patient_data.patient_key or "Unknown"
            name = render_name(patient_data.first_name, patient_data.last_name) or render_name("Unknown", "Unknown")
            ds.PatientName = name
            ds.PatientBirthDate = map_optional(patient_data.date_of_birth, format_date) or DEFAULT_DATE
            ds.PatientSex = map_optional(patient_data.gender, lambda x: x.upper()) or ""


class GeneralStudy(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        ds.StudyInstanceUID = self._instance_uid(data)
        # A RIS generated number that identifies the order for the Study.  Required, Empty if Unknown.
        ds.AccessionNumber = ""
        ds.ReferringPhysicianName = ""

        if self.parent.is_anonymised:
            ds.StudyID = "0"
            ds.StudyDate = DEFAULT_DATE
            ds.StudyTime = DEFAULT_TIME
        else:
            exam = data.parser_result.exam
            ds.StudyID = exam.source_id
            ds.StudyDate = map_optional(exam.scan_datetime, format_date)
            ds.StudyTime = map_optional(exam.scan_datetime, format_time)

    def _instance_uid(self, data: DicomData) -> str:
        return generate_uid_from_source(
            self.parent.pepper,
            [
                # Using comment in exam.source_id, uniqueness guaranteed with manufacturer, site, patient ID
                data.parser_result.exam.source_id,
                data.parser_result.exam.manufacturer,
                *self.parent.uid_entropy,  # Librarian passes in 'imaging system' here
                data.parser_result.patient.source_id,
                # Other fields to add to entropy that are exam-specific
                data.parser_result.exam.scan_datetime,
            ],
        )


class GeneralSeries(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        ds.SeriesInstanceUID = self._instance_uid(data)
        laterality = data.parser_result.series.laterality.value
        # Valid values for (0020, 0060)
        if laterality in ["L", "R"]:
            ds.Laterality = laterality

        ds.Modality = self._get_modality(data)
        ds.SeriesNumber = self._get_series_number(data)

    def _get_series_number(self, data: DicomData) -> Optional[int]:
        if self.parent.is_anonymised:
            return 1
        else:
            return convert_or_default(data.parser_result.series.source_id, int, 1)

    @staticmethod
    def _get_modality(data: DicomData) -> str:
        if data.image.is_2d:
            return "OP"  # Ophthalmic Photography
        elif data.image.modality == ImageModality.OCT:
            return "OPT"  # Ophthalmic Tomography
        else:
            raise ValueError(f"Modality not supported for {data.image.modality}")

    def _instance_uid(self, data: DicomData) -> str:
        return generate_uid_from_source(
            self.parent.pepper,
            [
                # Using comment in series.source_id, uniqueness guaranteed with manufacturer, site and exam ID, which is
                # all incorporated in exam.source_id
                data.parser_result.series.source_id,
                data.parser_result.exam.manufacturer,
                self.parent.uid_entropy,  # Librarian passes in 'imaging system' here
                data.parser_result.exam.source_id,
                # Other fields to add to entropy that are series-specific
                data.parser_result.series.protocol,
                data.parser_result.series.laterality,
                self._get_modality(data),
            ],
        )


class Synchronisation(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        # Required.
        # NO TRIGGER - data acquisition not synchronized by common channel or trigger
        ds.SynchronizationTrigger = "NO TRIGGER"
        # Required, The Acquisition Time Synchronized (0018,1800) Attribute specifies whether Acquisition DateTime
        # (0008,002A) of the Waveform Identification Module or the General Image Module represents an accurate
        # synchronized timestamp for the acquisition of the waveform and/or image data.
        ds.AcquisitionTimeSynchronized = "N"
        ds.SynchronizationFrameOfReferenceUID = self._synchronisation_uid(data)

    def _synchronisation_uid(self, data: DicomData) -> str:
        """
        A set of equipment may share a common acquisition synchronization environment, which is identified by a
        Synchronization Frame of Reference UID. All SOP Instances that share the same Synchronization Frame of Reference
        UID shall be temporally related to each other. If a Synchronization Frame of Reference UID is present, all SOP
        Instances in the Series must share the same Frame of Reference.
        """
        return generate_uid_from_source(self.parent.pepper, [data.parser_result.exam.source_id])


class MultiFrameAndCine(DicomModule):
    """
    We break convention and have two distinct modules in one class, as their contents are directly linked.

    The Cine module contains the FrameIncrementPointer and NumberOfFrames attributes
    The MultiFrame module contains the FrameTime and FrameTimeVector attributes
    """

    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        ds.NumberOfFrames = len(data.image.contents)

        # Only assume temporal data if a valid frame time vector exists.
        # Otherwise, assume separate images and do not set cine data.
        frame_time_vector = self._get_frame_time_vector(data)
        if frame_time_vector:
            ds.FrameIncrementPointer = Tag("FrameTimeVector")
            ds.FrameTimeVector = frame_time_vector
        else:
            ds.FrameIncrementPointer = Tag("FrameTime")
            ds.FrameTime = "0"

    @staticmethod
    def _get_frame_time_vector(data: DicomData) -> List[str]:
        """
        Return a vector of time deltas in milliseconds between individual frames.
        As per spec, the time delta of the n-th frame is represented by:
         * 0 if n == 0
         * the sum between 1st and nth element of the vector if n > 0

        If the images do not contain sufficient information, or the information is malformed,
        return an empty list
        """
        image_count = len(data.image.contents)
        if image_count > 1:
            image_times = [im.capture_datetime for im in data.image.contents]
            if all(t is not None for t in image_times):
                # The first item in the vector is 0 as per spec
                deltas = [0.0]
                # All other deltas are milliseconds between i-th and (i-1)-th time
                deltas.extend(
                    (image_times[i] - image_times[i - 1]).total_seconds() * 1000 for i in range(1, image_count)
                )
                if all(delta == 0 for delta in deltas):
                    logger.info(
                        "Multi-frame image capture dates are all identical; " "Assuming insufficient detail in raw file"
                    )
                elif any(delta < 0 for delta in deltas):
                    # This is the only issue we should flag as dodgy data. All others could occur in the wild
                    logger.warning("Multi-frame image capture dates are not in ascending order")
                else:
                    return [crop_number(n) for n in deltas]
            else:
                logger.info("Not all image capture dates are set")
        return []


class FrameOfReference(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        # The Frame of Reference UID (0020,0052) shall be used to uniquely identify a Frame of Reference for a Series.
        # Each Series shall have a single Frame of Reference UID. However, multiple Series within a Study may share
        # a Frame of Reference UID. All images in a Series that share the same Frame of Reference UID shall be
        # spatially related to each other.
        ds.FrameOfReferenceUID = "1"

        # The Position Reference Indicator (0020,1040) specifies the part of the imaging target that was used as
        # a reference point associated with a specific Frame of Reference UID.
        ds.PositionReferenceIndicator = ""
