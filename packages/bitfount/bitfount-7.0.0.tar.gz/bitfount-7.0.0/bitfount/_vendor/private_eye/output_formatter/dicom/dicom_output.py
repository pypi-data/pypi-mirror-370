import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from more_itertools import one
from ....private_eye import SectionName
from ....private_eye.consts import ImageModality
from ....private_eye.data import ImageData, ImageProcessingOptions, IndividualImageOutputRequest, SeriesResult
from ....private_eye.output_formatter.dicom.classes.common import DicomClass
from ....private_eye.output_formatter.dicom.classes.ophthalmic_photography import OphthalmicPhotographyClass
from ....private_eye.output_formatter.dicom.classes.ophthalmic_tomography import OphthalmicTomographyImageClass
from ....private_eye.output_formatter.output_formatter import IndividualImageOutputWriter
from ....private_eye.utils.optional import get_optional

logger = logging.getLogger(__name__)

REQUIRED_SECTIONS = {SectionName.EXAM, SectionName.IMAGES, SectionName.PATIENT, SectionName.SERIES}


class OutputDICOM(IndividualImageOutputWriter):
    def output(
        self, parser_result: SeriesResult, request: IndividualImageOutputRequest
    ) -> List[Dict[ImageProcessingOptions, Path]]:
        output_path_prefix = request.output_path_prefix
        source_id = request.source_id
        image_data = one(
            image_data for image_data in get_optional(parser_result.images).images if image_data.source_id == source_id
        )

        if len(image_data.contents) == 0:
            logger.info("File %s contains no image content", source_id)
            return []

        if not request.pepper:
            logger.warning(
                "No pepper set for DICOM extraction. The images produced will not be psuedonymous. File: %s", source_id
            )

        converter = self._get_converter(
            image_data,
            is_anonymous=not request.output_sensitive_data,
            uid_entropy=request.extra_entropy,
            pepper=request.pepper,
        )
        if converter is None:
            logger.warning("File %s contains an image with an unsupported modality: %s", source_id, image_data.modality)
            return []

        return [converter.write_to_output(output_path_prefix, parser_result, image_data)]

    @staticmethod
    def _get_converter(
        image: ImageData, is_anonymous: bool, uid_entropy: List[Any], pepper: Optional[str]
    ) -> Optional[DicomClass]:
        if image.modality == ImageModality.OCT:
            return OphthalmicTomographyImageClass(pepper, is_anonymous, uid_entropy)
        if image.is_2d:
            return OphthalmicPhotographyClass(pepper, is_anonymous, uid_entropy)
        return None
