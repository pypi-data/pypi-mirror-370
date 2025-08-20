import logging
from pathlib import Path
from typing import Dict, List, Optional, cast

from more_itertools import one
from ....private_eye import BScanImageData, IndividualImageOutputRequest, PhotoImageData, SeriesResult, Size2D, Size3D
from ....private_eye.data import BaseImageDataBytes, ImageProcessingOptions
from ....private_eye.output_formatter.h5.common import H5Content, write_files
from ....private_eye.output_formatter.output_formatter import IndividualImageOutputWriter
from ....private_eye.utils.optional import get_optional

logger = logging.getLogger(__name__)


class OutputStandardH5(IndividualImageOutputWriter):
    def output(
        self, result: SeriesResult, request: IndividualImageOutputRequest
    ) -> List[Dict[ImageProcessingOptions, Path]]:
        try:
            images_section = get_optional(result.images)
        except ValueError as e:
            raise ValueError("Unable to export to H5 without IMAGES section") from e

        image_data = one(
            image_data for image_data in images_section.images if image_data.source_id == request.source_id
        )

        if len(image_data.contents) == 0:
            logger.error("Unable to write out image with no contents")
            return []

        output_path = request.output_path_prefix.with_name(request.output_path_prefix.name + ".h5")
        # We limit h5 outputs to only a single ImageProcessingOptions so can just read the value from
        # one of the images and know that it will be the same.
        if isinstance(image_data.contents[0], BaseImageDataBytes):
            image_processing_options = image_data.contents[0].image_output_params[0].image_processing_options
        else:
            raise ValueError("H5 output only support images not visual fields.")
        if isinstance(image_data.contents[0], PhotoImageData):
            fundus_data = cast(PhotoImageData, one(image_data.contents))
            write_files(
                output_path,
                H5Content(None, cast(Optional[Size2D], image_data.resolutions_mm), [], [fundus_data]),
            )
        else:
            oct_data = cast(List[BScanImageData], image_data.contents)
            write_files(
                output_path,
                H5Content(cast(Optional[Size3D], image_data.resolutions_mm), None, oct_data, []),
            )

        return [{image_processing_options: output_path}]
