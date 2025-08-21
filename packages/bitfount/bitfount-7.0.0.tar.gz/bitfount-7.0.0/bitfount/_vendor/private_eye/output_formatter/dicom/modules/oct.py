import copy
import logging
import math
from typing import Dict, List, Optional, Tuple

import numpy as np
from .....private_eye.data import BScanImageData, Circle, HeidelbergImageTransforms, ImageData, Line, TopconImageTransforms
from .....private_eye.output_formatter.dicom.data_dictionary import (
    HEIDELBERG_AFFINE_TRANSFORM,
    HEIDELBERG_AFFINE_TRANSFORM_APPLIED,
    HEIDELBERG_INTENSITY_EXPONENT,
    HEIDELBERG_INTENSITY_MULTIPLIER,
    HEIDELBERG_INTENSITY_SCALING_APPLIED,
    HEIDELBERG_PRIVATE_DATA_GROUP,
    TOPCON_HIGHER,
    TOPCON_LOWER,
    TOPCON_PRIVATE_DATA_GROUP,
    TOPCON_SCALING_APPLIED,
)
from .....private_eye.output_formatter.dicom.dicom_helpers import (
    DEFAULT_DATE,
    DEFAULT_DATETIME,
    DEFAULT_RESOLUTIONS_MM,
    DEFAULT_TIME,
    as_sequence,
    code_sequence,
    crop_number,
    format_date,
    format_datetime,
    format_time,
    generate_bool_coded_string,
    generate_uid_from_source,
)
from .....private_eye.output_formatter.dicom.modules.common import DicomData, DicomModule
from .....private_eye.utils.optional import convert_or_default, map_optional
from pydicom import Dataset, Sequence
from pydicom.uid import OphthalmicPhotography8BitImageStorage

logger = logging.getLogger(__name__)


class OphthalmicTomographySeries(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        # Override SeriesNumber to always be set
        if self.parent.is_anonymised:
            ds.SeriesNumber = 1
        else:
            ds.SeriesNumber = convert_or_default(data.parser_result.series.source_id, int, 1)


class AcquisitionContext(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        ds.AcquisitionContextSequence = Sequence()


class MultiFrameFunctionalGroups(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        image_processing_options = data.image_processing_options
        try:
            fundus_index, fundus_image = self._get_fundus_image_and_index(data)
            reference_image = self._build_referenced_image(data, fundus_image)
        except ValueError:
            reference_image = None
            fundus_index = None
        if "heidelberg_processing_flags" in data.image.extras[image_processing_options]:
            processing_flags = data.image.extras[image_processing_options]["heidelberg_processing_flags"]
            self._build_heidelberg_processing_private_data_block(ds, processing_flags)
        if "topcon_processing_flags" in data.image.extras[image_processing_options]:
            processing_flags = data.image.extras[image_processing_options]["topcon_processing_flags"]
            self._build_topcon_processing_private_data_block(ds, processing_flags)
        ds.SharedFunctionalGroupsSequence = self._build_shared_functional_group(data, reference_image)
        ds.PerFrameFunctionalGroupsSequence = self._build_per_frame_functional_groups(
            data, reference_image, fundus_index
        )

        ds.InstanceNumber = 1
        # These require a value
        if self.parent.is_anonymised:
            ds.ContentDate = DEFAULT_DATE
            ds.ContentTime = DEFAULT_TIME
        else:
            scan_datetime = data.parser_result.exam.scan_datetime
            ds.ContentDate = map_optional(scan_datetime, format_date) or DEFAULT_DATE
            ds.ContentTime = map_optional(scan_datetime, format_time) or DEFAULT_TIME

        ds.NumberOfFrames = len(data.image.contents)

        # Concatenations are not allowed in OCT images, so do not include Concatenation IUD or related properties
        # See http://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.17.16.3.html#sect_C.8.17.16.3
        # However, omitting actually causes a conflict in the spec:
        # * In-concatenation Number and In-concatenation Total Number are required IFF ConcatenationUID is set
        #   according to the spec for the Multi-frame Functional Groups Module (C.7.6.16)
        # * In-concatenation Number and In-concatenation Total Number are ALWAYS required according to the spec for
        #   the Ophthalmic Tomography Image Module (C.8.17.7)
        # We shall exclude any concatenation properties and accept the spec break

    @staticmethod
    def _get_fundus_image_and_index(data: DicomData) -> Tuple[int, ImageData]:
        # Filter by group first, so the returned index is relative to images for group ONLY
        images_for_group = [im for im in data.parser_result.images.images if im.group_id == data.image.group_id]
        images = [(idx, im) for idx, im in enumerate(images_for_group) if im.is_2d]
        if not images:
            raise ValueError("No images found")
        # try to get the colour one (Topcon has both colour and IR fundus images), otherwise return the first
        colour_image = next(((idx, im) for idx, im in images if im.is_colour), None)
        if colour_image:
            return colour_image
        else:
            return images[0]

    @staticmethod
    def _build_heidelberg_bscan_private_data_block(frame_content: Dataset, transform_data: HeidelbergImageTransforms):
        block = frame_content.private_block(
            HEIDELBERG_PRIVATE_DATA_GROUP.element_tag, HEIDELBERG_PRIVATE_DATA_GROUP.group_name, create=True
        )
        if transform_data:
            if isinstance(transform_data.affine_transform, np.ndarray):
                block.add_new(HEIDELBERG_AFFINE_TRANSFORM, "FD", transform_data.affine_transform.flatten().tolist())
            block.add_new(HEIDELBERG_INTENSITY_MULTIPLIER, "FD", float(transform_data.intensity_scaling_multiplier))
            block.add_new(HEIDELBERG_INTENSITY_EXPONENT, "SL", int(transform_data.intensity_scaling_exponent))

    @staticmethod
    def _build_topcon_bscan_private_data_block(frame_content: Dataset, transform_data: TopconImageTransforms):
        block = frame_content.private_block(
            TOPCON_PRIVATE_DATA_GROUP.element_tag, TOPCON_PRIVATE_DATA_GROUP.group_name, create=True
        )
        block.add_new(TOPCON_LOWER, "SS", transform_data.lower)
        block.add_new(TOPCON_HIGHER, "SS", transform_data.higher)

    @staticmethod
    def _build_topcon_processing_private_data_block(img: Dataset, processing_flags: Dict[str, bool]):
        block = img.private_block(
            TOPCON_PRIVATE_DATA_GROUP.element_tag, TOPCON_PRIVATE_DATA_GROUP.group_name, create=True
        )
        # DICOM does not have a boolean VR instead use a coded STRING
        block.add_new(TOPCON_SCALING_APPLIED, "CS", generate_bool_coded_string(processing_flags["clipping"]))

    @staticmethod
    def _build_heidelberg_processing_private_data_block(img: Dataset, processing_flags: Dict[str, bool]):
        block = img.private_block(
            HEIDELBERG_PRIVATE_DATA_GROUP.element_tag, HEIDELBERG_PRIVATE_DATA_GROUP.group_name, create=True
        )
        # DICOM does not have a boolean VR instead use a coded STRING
        block.add_new(
            HEIDELBERG_INTENSITY_SCALING_APPLIED,
            "CS",
            generate_bool_coded_string(processing_flags["intensity_adjustment"]),
        )
        block.add_new(
            HEIDELBERG_AFFINE_TRANSFORM_APPLIED,
            "CS",
            generate_bool_coded_string(processing_flags["transform"]),
        )

    def _build_per_frame_functional_groups(
        self, data: DicomData, reference_image: Optional[Dataset], reference_index: Optional[int]
    ) -> Sequence:
        seq = Sequence()
        image_processing_options = data.image_processing_options
        if self.parent.is_anonymised:
            datetime = DEFAULT_DATETIME
        else:
            scan_datetime = data.parser_result.exam.scan_datetime
            datetime = map_optional(scan_datetime, format_datetime) or DEFAULT_DATE

        for index, frame in enumerate(data.image.contents, start=1):
            frame_group = Dataset()

            frame_content = Dataset()
            frame_content.StackID = "1"
            frame_content.InStackPositionNumber = index
            frame_content.DimensionIndexValues = [1, index]
            frame_content.FrameAcquisitionDateTime = datetime
            frame_content.FrameReferenceDateTime = datetime
            # This value is required
            frame_content.FrameAcquisitionDuration = 1.0
            if isinstance(frame, BScanImageData):
                if isinstance(frame.image_transform_metadata[image_processing_options], HeidelbergImageTransforms):
                    self._build_heidelberg_bscan_private_data_block(
                        frame_content, frame.image_transform_metadata[image_processing_options]
                    )
                if isinstance(frame.image_transform_metadata[image_processing_options], TopconImageTransforms):
                    self._build_topcon_bscan_private_data_block(
                        frame_content, frame.image_transform_metadata[image_processing_options]
                    )
            frame_group.FrameContentSequence = as_sequence(frame_content)

            if reference_image and reference_index is not None:
                # Use ds._dict.copy() instead of ds.copy(), as Dataset.copy() is broken - see
                # https://github.com/pydicom/pydicom/issues/1146
                # It will be fixed in 2.1.0, which at time of this comment is not yet released.
                frame_location = Dataset(reference_image._dict.copy())
                location = frame.photo_locations[reference_index]
                if isinstance(location, Line):
                    # DICOM uses the (rows, columns) system which translates to (y, x) in standard terms
                    frame_location.ReferenceCoordinates = [
                        location.start.y,
                        location.start.x,
                        location.end.y,
                        location.end.x,
                    ]
                    frame_location.OphthalmicImageOrientation = "LINEAR"
                    frame_group.OphthalmicFrameLocationSequence = as_sequence(frame_location)
                elif isinstance(location, Circle):
                    frame_location.ReferenceCoordinates = self._build_circle_coords(location)
                    frame_location.OphthalmicImageOrientation = "NONLINEAR"
                    frame_group.OphthalmicFrameLocationSequence = as_sequence(frame_location)
                else:
                    logger.error(f"Unknown photo location type {type(location)} for {reference_image}")

            plane_position = Dataset()
            # Value is required by the spec, so set it to a placeholder
            plane_position.ImagePositionPatient = [0, 0, 0]
            frame_group.PlanePositionSequence = as_sequence(plane_position)

            seq.append(frame_group)
        return seq

    @staticmethod
    def _build_shared_functional_group(data: DicomData, reference_image: Optional[Dataset]) -> Sequence:
        fun_group = Dataset()

        pixel_measures = Dataset()
        image_resolutions_mm = data.image.resolutions_mm or DEFAULT_RESOLUTIONS_MM
        # Pixel spacing = (distance between rows, distance between cols). Hence, (height resolution, width resolution)
        pixel_measures.PixelSpacing = [
            crop_number(image_resolutions_mm.height),
            crop_number(image_resolutions_mm.width),
        ]
        pixel_measures.SliceThickness = crop_number(image_resolutions_mm.depth)
        fun_group.PixelMeasuresSequence = as_sequence(pixel_measures)

        if reference_image:
            fun_group.ReferencedImageSequence = as_sequence(reference_image)

        frame_anatomy = Dataset()
        frame_anatomy.FrameLaterality = data.parser_result.series.laterality.value
        # See http://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_CID_4030.html
        frame_anatomy.AnatomicRegionSequence = code_sequence("SCT", "81745001", "Eye")

        fun_group.FrameAnatomySequence = as_sequence(frame_anatomy)
        plane_orientation = Dataset()
        plane_orientation.ImageOrientationPatient = [
            "1.000000",
            "0.000000",
            "0.000000",
            "0.000000",
            "1.000000",
            "0.000000",
        ]
        fun_group.PlaneOrientationSequence = as_sequence(plane_orientation)

        return as_sequence(fun_group)

    @staticmethod
    def _build_circle_coords(location: Circle) -> List[int]:
        centre = location.centre
        radius = location.radius
        angle = location.start_angle

        # Could do this as a large list comprehension, but that would be less readable
        ret = []
        # Single-degree increments should be fine. Ensure we include 360 (or 0) twice in order to complete the circle
        for theta in range(0, 361):
            # Note: start_angle is measured from the positive x-axis, hence coords are (r * cos(th), r * sin(th))
            theta_f = angle + float(theta) * math.pi / 180
            ret.append(int(centre.x + radius * math.cos(theta_f)))
            ret.append(int(centre.y + radius * math.sin(theta_f)))
        return ret

    def _build_referenced_image(self, data: DicomData, fundus_image: ImageData) -> Dataset:
        referenced_image = Dataset()
        # We always convert fundus images to 8-bit photography SOPs
        referenced_image.ReferencedSOPClassUID = OphthalmicPhotography8BitImageStorage
        referenced_image.ReferencedSOPInstanceUID = self.parent.generate_image_uid(data.parser_result, fundus_image)
        referenced_image.PurposeOfReferenceCodeSequence = code_sequence("DCM", "121311", "Localizer")

        return referenced_image


class MultiFrameDimension(DicomModule):
    # This UID contains no sensitive data so there is no pepper.
    SINGLE_STACK_MULTI_FRAME_UID = generate_uid_from_source(
        pepper=None, source=["DimensionOrganizationUID", "StackID", "StackPosition"]
    )

    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        dimension_org = Dataset()
        dimension_org.DimensionOrganizationUID = self.SINGLE_STACK_MULTI_FRAME_UID
        ds.DimensionOrganizationSequence = as_sequence(dimension_org)

        # These should match DimensionIndexValues from MultiFrameFunctionalGroups
        stack_index = Dataset()
        stack_index.DimensionIndexPointer = 0x00209056  # (0020,9056) Frame Content Stack ID
        stack_index.FunctionalGroupPointer = 0x00209111  # (0020,9111) Frame Content Sequence
        stack_index.DimensionOrganizationUID = self.SINGLE_STACK_MULTI_FRAME_UID
        stack_index.DimensionDescriptionLabel = "Frame Stack ID"
        frame_index = Dataset()
        frame_index.DimensionIndexPointer = 0x00209057  # (0020,9057) In-stack position number
        frame_index.FunctionalGroupPointer = 0x00209111  # (0020,9111) Frame Content Sequence
        frame_index.DimensionOrganizationUID = self.SINGLE_STACK_MULTI_FRAME_UID
        stack_index.DimensionDescriptionLabel = "Frame Index"
        ds.DimensionIndexSequence = Sequence([stack_index, frame_index])

        # We should set DimensionOrganizationType to 3D only if we have (according to the spec):
        # 'Spatial Multi-frame image of equally spaced parallel planes'
        # Given that we only store the positions of individual B-scans, we do not know for certain this will always
        # be the case (e.g. Heidelberg and Topcon can create cross-shaped scans)
        # To be safe, we shall simply not set it.
        # ds.DimensionOrganizationType = "3D"


class OphthalmicTomographyImage(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:

        # https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.html
        ds.ImageType = ["ORIGINAL", "PRIMARY"]

        ds.SamplesPerPixel = 1
        if self.parent.is_anonymised:
            ds.AcquisitionDateTime = DEFAULT_DATETIME
        else:
            scan_datetime = data.parser_result.exam.scan_datetime
            ds.AcquisitionDateTime = map_optional(scan_datetime, format_datetime)
        ds.AcquisitionNumber = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.PresentationLUTShape = "IDENTITY"
        ds.PixelRepresentation = 0
        ds.LossyImageCompression = "00"
        ds.BitsAllocated = data.bits_stored
        ds.BitsStored = data.bits_stored
        ds.HighBit = data.bits_stored - 1
        ds.BurnedInAnnotation = "NO"

        # Offset of the first frame in a multi-frame image of a concatenation.
        # Must be 0 according to the spec
        ds.ConcatenationFrameOffsetNumber = 0

        # Identifier for one SOP Instance belonging to a concatenation. See Section C.7.6.16.2.2.4 for further
        # specification.  The first instance in a concatenation (that with the lowest Concatenation Frame Offset Number
        # (0020,9228) value) shall have an In-concatenation Number (0020,9162) value of 1, and subsequent instances
        # shall have values monotonically increasing by 1.
        # Must be 1 according to the spec
        ds.InConcatenationNumber = 1

        # The number of SOP Instances sharing the same Concatenation UID.
        # Must be 1 according to the spec
        ds.InConcatenationTotalNumber = 1

        # This value is required
        ds.AcquisitionDuration = 0.0


class OphthalmicTomographyAcquisitionParameters(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        ds.RefractiveStateSequence = Sequence()
        ds.EmmetropicMagnification = ""
        ds.IntraOcularPressure = ""
        ds.PupilDilated = ""
        ds.AxialLengthOfTheEye = ""
        ds.HorizontalFieldOfView = ""


class OphthalmicTomographyParameters(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        # See: http://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_CID_4210.html
        ds.AcquisitionDeviceTypeCodeSequence = code_sequence("SCT", "392012008", "Optical Coherence Tomography Scanner")
        ds.LightPathFilterTypeStackCodeSequence = Sequence()
        # This is confirmed for Topcon and Zeiss OCTs
        ds.DetectorType = "CCD"

        # We need info for all scanners, in particular Heidelberg Spectralis machines in order to satisfy the spec.
        # However, finding these values for ALL scanners would be a nightmare so we'll choose to ignore the spec.
        # The DICOM conformance statements the values for SOME models we've seen, but for consistency we'll exclude
        # these values until we need them:
        # https://www.zeiss.com/content/dam/Meditec/downloads/pdf/DICOM/dicom_conformance_statement_cirrus_5000_500_9.5.pdf
        # https://www.topconhealth.com/wp-content/uploads/IMAGEnet-6-DICOM-Conformance-Statement_RevB.pdf
        #
        # ds.DepthSpatialResolution = ?
        # ds.MaximumDepthDistortion = ?
        # ds.AlongScanSpatialResolution = ?
        # ds.MaximumAlongScanDistortion = ?
        # ds.AcrossScanSpatialResolution = ?
        # ds.MaximumAcrossScanDistortion = ?
        # ds.IlluminationWaveLength = ?
        # ds.IlluminationPower = ?
        # ds.IlluminationBandwidth = ?
