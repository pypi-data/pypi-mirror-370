from pathlib import Path
from typing import List, Optional, cast

import numpy as np
from ...private_eye import ImagesData, SectionName, read_sections_from_local_file
from ...private_eye.data import BaseImageDataBytes, ImageData


def dump_contours(parser: str, input_file: str, output_path: str) -> None:

    output_folder = Path(output_path)
    output_folder.mkdir(exist_ok=True)

    parser_result = read_sections_from_local_file(parser, Path(input_file), [SectionName.IMAGES])
    for result in parser_result.results:
        _dump_contours(result.images, output_folder)


def _dump_contours(images: Optional[ImagesData], output_folder: Path) -> None:
    # If one image and one image processing has a contour on an ImageData object all images will have contours
    images_with_contours: List[ImageData] = []
    for image in cast(ImagesData, images).images:
        if isinstance(image.contents[0], BaseImageDataBytes):
            if image.contents[0].image_output_params[0].contour:
                images_with_contours.append(image)

    for image in images_with_contours:
        if not isinstance(image.contents[0], BaseImageDataBytes):
            raise ValueError("Image does not contain contours")
        for frame_index, scan in enumerate(cast(List[BaseImageDataBytes], image.contents)):
            for image_output_params in scan.image_output_params:
                contour = image_output_params.contour
                if not contour:
                    raise ValueError("Image does not contain contours")

                output_file = (
                    output_folder / f"{image_output_params.image_processing_options.identifier()}"
                    f"-{image.source_id}-{frame_index}.csv"
                )

                layers = contour.contour_layers
                all_layers = np.array(list(zip(*[c.data for c in layers])))

                # Convert to string and blank out all NaN values
                all_layers = all_layers.astype(str)
                all_layers[all_layers == "nan"] = ""

                np.savetxt(
                    output_file,
                    all_layers,
                    delimiter=",",
                    header=",".join([c.layer_name for c in layers]),
                    fmt="%s",
                    comments="",
                )
