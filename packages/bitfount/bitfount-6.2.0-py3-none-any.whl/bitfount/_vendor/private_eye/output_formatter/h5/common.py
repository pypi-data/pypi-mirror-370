import logging
from pathlib import Path
from typing import Dict, List, Optional

import attr
import h5py
import numpy as np
from h5py import Dataset, File
from PIL.Image import Image
from ....private_eye import BScanImageData, PhotoImageData, Size2D, Size3D
from ....private_eye.data import ImageProcessingOptions
from ....private_eye.output_formatter.convert_to_pil_image import get_pil_images

logger = logging.getLogger(__name__)

DEFAULT_RESOLUTIONS_MM: Size3D = Size3D(depth=0.001, height=0.001, width=0.001)


@attr.s(auto_attribs=True, frozen=True)
class H5Content:
    oct_resolutions: Optional[Size3D]
    fundus_resolutions: Optional[Size2D]
    oct: List[BScanImageData]
    fundus: List[PhotoImageData]


class InvalidParserOptionsForH5Output(Exception):
    pass


def write_files(output_path: Path, image_data: H5Content) -> None:
    if len(image_data.oct) == 0 and len(image_data.fundus) == 0:
        raise ValueError("No OCT or fundus data in file")

    with h5py.File(str(output_path), "w") as h5_file:
        # We still want to add empty datasets when there isn't any OCT / fundus data
        _add_oct_to_file(h5_file, image_data)
        _add_fundus_to_file(h5_file, image_data)


def add_segmentation_datasets(h5_file: File, oct_arr: np.ndarray) -> None:
    # The segmentation array needs to be twice the size in the z direction, this is to match the expectations of the
    # Droplet plugin in Fiji which is used for grading OCTs.
    oct_arr_shape = list(oct_arr.shape)
    oct_arr_shape[2] = oct_arr_shape[2] * 2
    blank_arr_shape = tuple(oct_arr_shape)

    blank_arr = np.zeros(blank_arr_shape, dtype=np.uint8)

    dataset_segmentation = _build_dataset(h5_file, "segmentation", blank_arr, 9)
    add_element_size_um(dataset_segmentation, DEFAULT_RESOLUTIONS_MM)

    dataset_uncertainty = _build_dataset(h5_file, "uncertainty", blank_arr, 9)
    add_element_size_um(dataset_uncertainty, DEFAULT_RESOLUTIONS_MM)


def add_element_size_um(dataset: Dataset, resolutions: Size3D) -> None:
    # The element size here is per pixel and needs converting from mm to um
    element_size_um = [elem * 1000 for elem in [resolutions.depth, resolutions.height, resolutions.width]]
    dataset.attrs.create("element_size_um", data=element_size_um, dtype=np.float32)


def _build_dataset(h5_file: File, name: str, img_arr: np.ndarray, compression_opts: int) -> Dataset:
    assert isinstance(img_arr, np.ndarray)
    data_set = h5_file.create_dataset(
        name=name, shape=img_arr.shape, dtype=img_arr.dtype, compression="gzip", compression_opts=compression_opts
    )
    data_set[:] = img_arr
    return data_set


def _add_oct_to_file(h5_file: File, image_data: H5Content) -> None:
    oct_data = image_data.oct
    resolutions: Optional[Size3D] = None
    if len(oct_data) == 0:
        oct_arr = np.empty((1, 1, 1))
    else:
        oct_arr = np.stack(
            [_check_single_image_processing_options(get_pil_images(bscan)) for bscan in oct_data], axis=0
        )

        resolutions = image_data.oct_resolutions

    if resolutions is None:
        resolutions = DEFAULT_RESOLUTIONS_MM

    dataset_oct = _build_dataset(h5_file, "oct", oct_arr, 1)
    add_element_size_um(dataset_oct, resolutions)
    add_segmentation_datasets(h5_file, oct_arr)


def _add_fundus_to_file(h5_file: File, image_data: H5Content) -> None:
    fundus_data = image_data.fundus
    logger.debug("_add_fundus_to_file %s", fundus_data)
    resolutions: Optional[Size3D] = None
    if len(fundus_data) == 0:
        fundus_arr = np.empty((1, 1))
    else:
        fundus_arr = np.stack(
            [
                np.array(_check_single_image_processing_options(get_pil_images(elem)).convert("RGB"))
                for elem in fundus_data
            ],
            axis=0,
        )
        resolutions_mm = image_data.fundus_resolutions
        if resolutions_mm is not None:
            resolutions = Size3D(
                height=resolutions_mm.height, width=resolutions_mm.width, depth=DEFAULT_RESOLUTIONS_MM.depth
            )

    if resolutions is None:
        resolutions = DEFAULT_RESOLUTIONS_MM

    dataset_fundus = _build_dataset(h5_file, "fundus", fundus_arr, 1)
    add_element_size_um(dataset_fundus, resolutions)


def _check_single_image_processing_options(image: Dict[ImageProcessingOptions, Image]) -> Image:
    if len(image) == 1:
        return list(image.values())[0]
    raise InvalidParserOptionsForH5Output("H5 output only supports a single image processing option.")
