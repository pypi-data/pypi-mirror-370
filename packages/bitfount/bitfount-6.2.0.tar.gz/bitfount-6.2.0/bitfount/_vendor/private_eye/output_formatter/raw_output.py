import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Union, cast, Optional

from more_itertools import one
from PIL import Image
from ...private_eye import ImageData
from ...private_eye.data import (
    BaseImageDataBytes,
    BScanImageData,
    EntireFileOutputRequest,
    ImageProcessingOptions,
    IndividualImageOutputRequest,
    PhotoImageData,
    SeriesResult,
    VisualFieldData,
)
from ...private_eye.output_formatter.convert_to_pil_image import apply_transforms, decompress_image
from ...private_eye.output_formatter.output_formatter import EntireFileOutputWriter, IndividualImageOutputWriter
from ...private_eye.utils.optional import get_optional

logger = logging.getLogger(__name__)


class OutputRawImages(IndividualImageOutputWriter):
    def output(
        self, result: SeriesResult, request: IndividualImageOutputRequest, save_to_file: bool = True
    ) -> List[Union[Dict[ImageProcessingOptions, Path], Dict[str, np.ndarray]]]:
        source_id = request.source_id
        output_path_prefix = request.output_path_prefix
        try:
            images_section = get_optional(result.images)
        except ValueError as e:
            raise ValueError("Image section required to export raw images") from e

        image_to_export: ImageData = one(image for image in images_section.images if image.source_id == source_id)

        if len(image_to_export.contents) == 0:
            logger.error("Unable to export image without contents")
            return []

        if isinstance(image_to_export.contents[0], VisualFieldData):
            logger.error("Unable to export non-image content")
            return []
        if len(image_to_export.contents) == 1:
            image = cast(Union[PhotoImageData, BScanImageData], one(image_to_export.contents))
            return [
                self.output_raw_image(
                    image=image,
                    idx=0,
                    output_path_prefix=output_path_prefix,
                    save_to_file=request.save_to_file,
                    image_modality_code=request.image_modality_code
                )
                ]
        output_paths = []
        for idx, image_data in enumerate(image_to_export.contents):
            image = cast(Union[PhotoImageData, BScanImageData], image_data)
            output_paths.append(
                self.output_raw_image(
                    image=image,
                    idx=idx,
                    output_path_prefix=output_path_prefix,
                    save_to_file=request.save_to_file,
                    image_modality_code=request.image_modality_code
)
            )
        return output_paths

    def output_raw_image(
        self,  image: BaseImageDataBytes, idx: int, output_path_prefix: Optional[Path]=None, save_to_file: bool = True, image_modality_code: Optional[str]=None
    ) -> Union[Dict[ImageProcessingOptions, Path], Dict[str, np.ndarray]]:
        if save_to_file is True and output_path_prefix is None:
            raise ValueError("Output path prefix required to save to file")
        output = {}
        if image.image:
            image_array = decompress_image(image)
            for image_output_params in image.image_output_params:
                # If save_to_file is True, we need to save the image to a file and return the path
                if save_to_file is True:
                    output_path = output_path_prefix.with_name(
                        image_output_params.image_processing_options.identifier()
                        + output_path_prefix.name
                        + f"-{idx}"
                        + ".png"
                    )
                    pil_image = Image.fromarray(
                        apply_transforms(image_array, image_output_params.image_transform_functions)
                    )

                    pil_image.save(output_path)
                    output[image_output_params.image_processing_options] = output_path
                else:
                    # If save_to_file is False, we return a dictionary mapping
                    # the modality and image id to the image as a numpy array
                    output_key = image_modality_code + f"-{idx}"
                    output[output_key] = apply_transforms(image_array, image_output_params.image_transform_functions)
        else:
            logger.error("Unable to export non-image content")
        return output


class OutputRawFiles(EntireFileOutputWriter):
    def output(self, result: SeriesResult, request: EntireFileOutputRequest) -> List[Path]:
        try:
            debug_section = get_optional(result.debug)
        except ValueError as e:
            raise ValueError("Debug section required to export raw files") from e

        output_path_prefix = request.output_path_prefix
        output_paths = []
        for file_name, data in debug_section.get_files().items():
            output_path = output_path_prefix.with_name(f"{output_path_prefix.name}-{file_name}")
            output_path.write_bytes(data)
            output_paths.append(output_path)
        return output_paths


class OutputDebugImages(EntireFileOutputWriter):
    def output(self, result: SeriesResult, request: EntireFileOutputRequest) -> List[Path]:
        try:
            debug_section = get_optional(result.debug)
        except ValueError as e:
            raise ValueError("Debug section required to export debug images") from e

        output_path_prefix = request.output_path_prefix
        output_paths = []
        for file_name, image in debug_section.get_images().items():
            output_path = output_path_prefix.with_name(f"{output_path_prefix.name}-{file_name}.png")
            image.save(output_path)
            output_paths.append(output_path)
        return output_paths
