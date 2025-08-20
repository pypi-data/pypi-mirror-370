from __future__ import print_function

import argparse
import os
import sys
from typing import Any, List, cast

import h5py
import numpy as np
from PIL import Image
from ..private_eye.output_formatter.h5.common import (
    DEFAULT_RESOLUTIONS_MM,
    add_element_size_um,
    add_segmentation_datasets,
)


def main() -> None:
    """
    This script will combine a folder of TIFF files as exported by Heyex 1 into H5 files suitable for consumption by
    Deepmind.  This was first created by Dan C for the original Deepmind export back in 2016.

    To have the script behave as it did for the first deepmind transfer, use only the --sourcefolder and --h5 flags.
    """
    options = check_args()

    converter = HeidelbergToHdf5(
        source_folder_path=options.sourcefolder,
        hdf5_path=options.h5,
        with_segmentation=options.with_segmentation,
        greyscale_oct=options.greyscale_oct,
    )
    converter.heidelberg_to_hdf5()
    sys.exit(0)


def check_args() -> Any:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sourcefolder", help="Path to image folder")
    parser.add_argument("--h5", help="Path to output HDF5 file")
    parser.add_argument(
        "--with-segmentation",
        action="store_true",
        default=False,
        help="Add segmentation and uncertainty datasets.  This is needed to open the image with the Fiji's Droplet "
        "segmentation plugin",
    )
    parser.add_argument(
        "--greyscale-oct",
        action="store_true",
        default=False,
        help="Convert OCTs to greyscale before saving as H5.  This is needed to open the image with the Fiji's Droplet "
        "segmentation plugin",
    )

    options = parser.parse_args()
    if not options.sourcefolder:
        parser.print_help()
        parser.error("Path to TIF files not given.")
    if not options.h5:
        parser.print_help()
        parser.error("Path to HDF5 output not given.")
    return options


class HeidelbergToHdf5:
    def __init__(self, source_folder_path: str, hdf5_path: str, with_segmentation: bool, greyscale_oct: bool) -> None:
        self.source_folder_path = os.path.abspath(source_folder_path)
        self.hdf5_path = os.path.abspath(hdf5_path)
        self.with_segmentation = with_segmentation
        self.greyscale_oct = greyscale_oct

    def heidelberg_to_hdf5(self) -> None:
        # We have a folder of TIF files as an input.
        # We take the OCT part of each image and combine them into a single H5
        tif_files = self._get_tif_files()
        h5_oct_array = None
        tif_fundus_array = None

        for index, file_path in enumerate(tif_files):
            tif_image = Image.open(file_path)

            tif_colour_arrays = None
            if index == 0:
                tif_colour_arrays = self._extract_and_validate_colour_tif_arrays(file_path, tif_image)
                tif_fundus_array = tif_colour_arrays[0]

            if not self.greyscale_oct:
                if not tif_colour_arrays:
                    tif_colour_arrays = self._extract_and_validate_colour_tif_arrays(file_path, tif_image)

                tif_oct_array = tif_colour_arrays[1]
            else:
                tif_greyscale_arrays = self._extract_and_validate_greyscale_tiff_arrays(file_path, tif_image)
                tif_oct_array = tif_greyscale_arrays[1]

            # Initialise the H5 OCT array to the correct shape depending on the TIF size and number
            if h5_oct_array is None:
                h5_oct_array = np.zeros(shape=((len(tif_files),) + tif_oct_array.shape))

            h5_oct_array[index] = tif_oct_array

        self._write_h5(cast(np.ndarray, h5_oct_array), cast(np.ndarray, tif_fundus_array))

    def _get_tif_files(self) -> List[str]:
        directory_contents = os.listdir(self.source_folder_path)
        tif_files = [
            os.path.join(self.source_folder_path, f)
            for f in directory_contents
            if (os.path.isfile(os.path.join(self.source_folder_path, f)) and f.endswith(".tif"))
        ]
        tif_files.sort()
        return tif_files

    @staticmethod
    def _extract_and_validate_greyscale_tiff_arrays(file_path: str, tif_image: Image) -> np.ndarray:
        tif_array = np.array(tif_image.convert("L"))
        HeidelbergToHdf5._verify_known_greyscale_image_shape(file_path, tif_array)
        return cast(np.ndarray, np.array_split(tif_array, [496], axis=1))

    @staticmethod
    def _extract_and_validate_colour_tif_arrays(file_path: str, tif_image: Image) -> np.ndarray:
        tif_array = np.array(tif_image)
        HeidelbergToHdf5._verify_known_colour_image_shape(file_path, tif_array)
        return cast(np.ndarray, np.array_split(tif_array, [496], axis=1))

    @staticmethod
    def _verify_known_colour_image_shape(file_path: str, tif_array: np.ndarray) -> None:
        """Check that this is an image shape we know about so that we can chop it up successfully.

        The tif contains a fundus image which is 496 x 496 next to the OCT image which can be:
        -  384 x 496
        -  512 x 496
        -  768 x 496
        - 1024 x 496
        """
        tif_shape = tif_array.shape
        if len(tif_shape) != 3:
            raise ValueError(f"TIF {file_path} has {len(tif_shape):d} dimensions instead of 3.")
        if tif_shape[0] != 496:
            raise ValueError(f"TIF {file_path} has an unexpected height: {tif_shape[0]:d}.")
        if tif_shape[1] != 880 and tif_shape[1] != 1008 and tif_shape[1] != 1264 and tif_shape[1] != 1520:
            raise ValueError(f"TIF {file_path} has an unexpected width: {tif_shape[1]:d}.", 5)
        if tif_shape[2] != 3:
            raise ValueError(f"TIF {file_path} has an unexpected bytes per pixel: {tif_shape[2]:d}.", 6)

    @staticmethod
    def _verify_known_greyscale_image_shape(file_path: str, tif_array: np.ndarray) -> None:
        tif_shape = tif_array.shape
        if len(tif_shape) != 2:
            raise ValueError(f"TIF {file_path} has {len(tif_shape):d} dimensions instead of 3.")
        if tif_shape[0] != 496:
            raise ValueError(f"TIF {file_path} has an unexpected height: {tif_shape[0]:d}.")
        if tif_shape[1] != 880 and tif_shape[1] != 1008 and tif_shape[1] != 1264 and tif_shape[1] != 1520:
            raise ValueError(f"TIF {file_path} has an unexpected width: {tif_shape[1]:d}.", 5)

    def _write_h5(self, h5_oct_array: np.ndarray, tif_fundus_array: np.ndarray) -> None:
        with h5py.File(self.hdf5_path, "w") as f:
            if tif_fundus_array is None:
                raise ValueError("tif_fundus_array unset")
            if h5_oct_array is None:
                raise ValueError("h5_oct_array unset")

            # Create datasets to hold the image data.
            # Higher compression makes almost zero difference in size while taking longer to generate.
            dataset_fundus = f.create_dataset(
                "fundus", tif_fundus_array.shape, dtype=np.uint8, compression="gzip", compression_opts=1
            )
            dataset_oct = f.create_dataset(
                "oct", h5_oct_array.shape, dtype=np.uint8, compression="gzip", compression_opts=1
            )

            # Copy the data.
            dataset_fundus[:] = tif_fundus_array
            dataset_oct[:] = h5_oct_array

            if self.with_segmentation:
                add_element_size_um(dataset_fundus, DEFAULT_RESOLUTIONS_MM)
                add_element_size_um(dataset_oct, DEFAULT_RESOLUTIONS_MM)
                add_segmentation_datasets(f, dataset_oct)
