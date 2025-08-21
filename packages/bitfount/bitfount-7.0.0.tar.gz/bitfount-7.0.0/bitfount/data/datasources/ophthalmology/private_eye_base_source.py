"""Data source for loading ophthalmology files using private-eye."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Mapping
from datetime import date, datetime
from enum import Enum
import json
import logging
import os
from pathlib import Path
import shutil
from typing import Any, Optional, TextIO, Union, cast

import numpy as np
import pandas as pd
from pandas.errors import OutOfBoundsDatetime

from bitfount import config
from bitfount._vendor import private_eye
from bitfount.data.datasources.ophthalmology.ophth_ds_types import (
    PRIVATE_EYE_PATIENT_DOB_ATTRIBUTE,
    Metadata,
    ProcessedDataRequiredTypes,
    ProcessedDataTypes,
    _ImageSequence,
    _PrivateEyeImage,
)
from bitfount.data.datasources.ophthalmology.ophth_ds_utils import (
    NoParserForFileExtension,
)
from bitfount.data.datasources.ophthalmology.ophthalmology_base_source import (
    IMAGE_COLUMN_PREFIX,
    SLO_IMAGE_ATTRIBUTE,
    _OphthalmologySource,
)
from bitfount.data.persistence.base import BulkResult
from bitfount.utils import delegates

logger = logging.getLogger(__name__)

RAW_IMAGE_FILE_EXTENSION: str = ".png"
RAW_METADATA_FILE_EXTENSION: str = ".json"

# Suffix used for caching images in the file system.
FILE_SYSTEM_ITERABLE_IMAGE_CACHE_SUFFIX: str = "-cache"


class PrivateEyeParser(Enum):
    """PrivateEye parser options."""

    HEIDELBERG = "heidelberg"


class SLOModality(Enum):
    """SLO modalities for private eye."""

    INFRARED = "SLO - Infrared"
    PHOTO = "Infrared Photo"


class SeriesProtocol(Enum):
    """OCT series protocols for private eye."""

    OCT_ART_VOLUME = "OCT ART Volume"
    RECTANGULAR_VOLUME = "Rectangular volume"
    OCT_B_SCAN = "OCT B-Scan"  # We currently are not supporting this protocol
    IMAGES = "Images"  # We currently are not supporting this protocol


PARSER_CONFIG: dict[str, dict[str, list[str]]] = {
    PrivateEyeParser.HEIDELBERG.value: {
        "SLO_MODALITY": [SLOModality.INFRARED.value],
        "OCT_SERIES_PROTOCOL": [
            SeriesProtocol.OCT_ART_VOLUME.value,
            SeriesProtocol.OCT_B_SCAN.value,
        ],
    },
}

OCT_MODALITY: str = "OCT"
PIXEL_DIVISION_CONSTANT: float = 0.011458333333333334


@delegates()
class _PrivateEyeSource(_OphthalmologySource, ABC):
    """Data source for loading ophthalmology files via private-eye.

    Args:
        path: Path to the directory which contains the data files. Subdirectories
            will be searched recursively.
        private_eye_parser: Private-eye supported machine type(s). Can either be
            a single parser to use for all files or a mapping of file extension
            to the desired parser type. If private_eye_parser is a mapping of file
            extensions to parsers, there must be a parser for each file extension
            specified. If no file extensions are specified then mapping can exist
            in whatever form (warnings will be logged if we encounter an extension
            for which no parser is specified). If private_eye_parser is a _single_
            parser, file_extension can be anything, we simply try to use this
            parser against any extension.
        **kwargs: Keyword arguments passed to the superclass constructors.
    """

    def __init__(
        self,
        path: Union[str, os.PathLike],
        private_eye_parser: Union[PrivateEyeParser, Mapping[str, PrivateEyeParser]],
        **kwargs: Any,
    ) -> None:
        # If file_extensions provided, need to check parsers provided
        super().__init__(path=path, **kwargs)
        if (
            isinstance(private_eye_parser, Mapping)
            and self.filter.file_extension is not None
        ):
            file_extensions: set[str] = set(
                [i.lower() for i in self.filter.file_extension]
            )

            # If private_eye_parser is multiple parsers then there should be a parser
            # for each file extension.
            # Find any file extensions that are _NOT_ in the parser list.
            if missing_parsers := file_extensions.difference(private_eye_parser.keys()):
                raise ValueError(
                    f"No parsers specified for file extensions:"
                    f" {', '.join(sorted(missing_parsers))}."
                )

        self._parsers: Union[PrivateEyeParser, Mapping[str, PrivateEyeParser]] = (
            private_eye_parser
        )

    def _recreate_file_structure(self, file_path: str, exist_ok: bool) -> Path:
        """Recreates the file structure in the output directory.

        This is used to ensure that the output directory has the same structure as the
        input directory. This is useful for when the input data is partitioned into
        subdirectories.

        Args:
            file_path: The file name to recreate the structure for.
            exist_ok: Whether to raise an error if the directory already exists.

        Returns:
            The path to the recreated file structure.

        Raises:
            FileExistsError: If the subdir already exists in the output directory and
                `exist_ok` is False.
        """
        path = Path(file_path)
        file_id = path.stem + FILE_SYSTEM_ITERABLE_IMAGE_CACHE_SUFFIX
        parent_path = path.parent.absolute()
        # Relative path gets the path of the original file relative to the specified
        # input path. This relative path is then used to recreate the file structure
        # in the output directory with the original filename being used as a
        # subdirectory instead containing any relevant extracted files.
        relative_path = parent_path.relative_to(self.path)
        save_prefix = self.out_path / relative_path / file_id
        save_prefix.mkdir(parents=True, exist_ok=exist_ok)
        return save_prefix

    def _get_parser(self, file_extension: str) -> PrivateEyeParser:
        """Retrieve the appropriate parser for a given file extension.

        Args:
            file_extension: The file extension to retrieve the parser for.

        Raises:
            NoParserForFileExtension: If an appropriate parser can not be found.
        """
        if isinstance(self._parsers, Mapping):
            try:
                return self._parsers[file_extension.lower()]
            except KeyError as ke:
                raise NoParserForFileExtension(
                    f"No private eye parser found for file extension"
                    f' "{file_extension}".'
                ) from ke
        else:
            return self._parsers

    def _get_config(self, file_extension: str) -> dict[str, list[str]]:
        """Retrieve the appropriate config for a given file extension.

        Raises:
            NoParserForFileExtension: If an appropriate parser (and hence config)
                can not be found.
        """
        return PARSER_CONFIG[self._get_parser(file_extension).value]

    @abstractmethod
    def _post_process_file(
        self, data: dict[str, Any], filename_path: Path
    ) -> dict[str, Any]:
        """Apply any post-processing to the data found in _process_file.

        This is mainly aimed at subclasses.
        """
        raise NotImplementedError

    def _get_tag_from_file(self, filename: str, category: str, tag: str) -> Any:
        """Get a specific tag from a file.

        Args:
            filename: The name of the file to process.
            category: The category of the tag to retrieve.
            tag: The tag to retrieve.

        Returns:
            The first value encountered for the tag in the file.
        """
        save_prefix = self._recreate_file_structure(filename, exist_ok=True)
        file_path = Path(filename)
        log_filename = file_path.name  # ensures as short as possible
        logger.debug(f"Reading file {log_filename} with private eye")
        json_file_paths, _ = self._run_private_eye(
            file_path, save_prefix, stop_before_pixels=True
        )
        for idx, json_file_path in enumerate(json_file_paths, start=1):
            logger.debug(
                f"Processing part {idx} of {len(json_file_paths)}"
                f" for file {log_filename}"
            )
            with open(json_file_path) as json_file:
                metadata = json.load(json_file)
                try:
                    return metadata[category][tag]
                except KeyError:
                    continue

    def _get_num_bscans_from_image_sequence(
        self, images_sequence: _ImageSequence
    ) -> int:
        """Get the number of B-scans from an image sequence.

        Args:
            images_sequence: The image sequence to process.

        Returns:
            The number of B-scans in the image sequence.
        """
        for img in images_sequence:
            if (
                "OCT" in img["modality"]
                or "Optical Coherence Tomography" in img["modality"]
            ):
                return len(img["contents"])

        return 0

    def _get_num_slos_from_image_sequence(self, images_sequence: _ImageSequence) -> int:
        """Get the number of SLOs from an image sequence.

        Args:
            images_sequence: The image sequence to process.

        Returns:
            The number of SLOs in the image sequence.
        """
        for img in images_sequence:
            if (
                "SLO" in img["modality"]
                or "Scanning Laser Ophthalmoscope" in img["modality"]
            ):
                return len(img["contents"])

        return 0

    def _get_num_bscans(self, file_name: str) -> Optional[int]:
        """Get the number of B-scans from the DICOM file.

        Args:
            file_name: The filename of the file to be processed.

        Returns:
            The number of B-scans in the file or None if the field is missing.
        """
        num_bscans = None
        try:
            images_sequence = self._get_tag_from_file(file_name, "images", "images")
            num_bscans = self._get_num_bscans_from_image_sequence(images_sequence)
        except Exception as e:
            logger.warning(
                f"Error reading number of B-scans from file '{file_name}': {e}"
            )
            # [LOGGING-IMPROVEMENTS]
            if config.settings.logging.log_private_eye_fixes:
                logger.debug(e, exc_info=True)

        return num_bscans

    def _get_num_bscans_from_cache(self, file_names: list[str]) -> dict[str, int]:
        """Get the number of B-scans from the cache.

        Args:
            file_names: The filenames of the files to be processed.

        Returns:
            The number of B-scans in the file or None if the field is missing.
        """
        cached_data: Optional[BulkResult] = None

        # If the cache is enabled, then we check the cache for the file
        if self.data_cache:
            if config.settings.enable_data_cache:
                logger.info(f"Checking cache for DICOM files '{file_names}'.")
            cache_results = self.data_cache.bulk_get(list(file_names))
            if cache_results.cached is not None:
                cached_data = cache_results

        file_to_num_bscans: dict[str, int] = {}
        for file_name in file_names:
            # If the file is in the cache, then we can extract the required fields
            # from the cache. If the cache is missing the field, then we read
            # the file.
            num_bscans: Optional[int] = None
            if cached_data is not None:
                cached_file_data = cached_data.get_cached_by_filename(file_name)
                if cached_file_data is not None:
                    try:
                        num_bscans = cast(int, cached_file_data["num_bscans"].iloc[0])
                    except Exception as e:
                        logger.warning(
                            f"Error reading cache for file '{file_name}': {e}"
                        )
                        # [LOGGING-IMPROVEMENTS]
                        if config.settings.logging.log_private_eye_fixes:
                            logger.debug(e, exc_info=True)

            # If the DOB is not in the cache, then we read the file
            if num_bscans is None:
                if config.settings.logging.log_private_eye_fixes:
                    logger.info(
                        f"Reading file properties of '{file_name}' to get number "
                        "of B-scans."
                    )
                num_bscans = self._get_num_bscans(file_name)

            if num_bscans is not None:
                file_to_num_bscans[file_name] = num_bscans

        return file_to_num_bscans

    def _get_dob(self, file_name: str) -> Optional[str]:
        """Get the date of birth from a file.

        Args:
            file_name: The name of the file to process.

        Returns:
            The date of birth of the patient.
        """
        dob: Optional[str] = None
        try:
            dob = self._get_tag_from_file(
                file_name, "patient", PRIVATE_EYE_PATIENT_DOB_ATTRIBUTE
            )
        except Exception as e:
            logger.warning(f"Error reading date of birth from file '{file_name}': {e}")
            # [LOGGING-IMPROVEMENTS]
            if config.settings.logging.log_private_eye_fixes:
                logger.debug(e, exc_info=True)

        if dob is not None:
            return str(dob)

        return dob

    def _get_dob_from_cache(self, file_names: list[str]) -> dict[str, date]:
        """Get the date of birth from a list of files.

        Args:
            file_names: The names of the files to process.

        Returns:
            A dictionary mapping the file names to the date of birth of the patient.
        """
        cached_data: Optional[BulkResult] = None

        # If the cache is enabled, then we check the cache for the file
        if self.data_cache:
            if config.settings.logging.log_private_eye_fixes:
                logger.info(f"Checking cache for DICOM files '{file_names}'.")
            cache_results = self.data_cache.bulk_get(list(file_names))
            if cache_results.cached is not None:
                cached_data = cache_results

        file_to_dob: dict[str, date] = {}
        for file_name in file_names:
            # If the file is in the cache, then we can extract the required fields
            # from the cache. If the cache is missing any of the fields, then we read
            # the file.
            file_dob_str: Optional[str] = None
            if cached_data is not None:
                logger.debug(f"Checking cache for file '{file_name}'.")
                cached_file_data = cached_data.get_cached_by_filename(file_name)
                if cached_file_data is not None:
                    try:
                        file_dob_str = str(
                            cached_file_data[PRIVATE_EYE_PATIENT_DOB_ATTRIBUTE].iloc[0]
                        )
                    except Exception as e:
                        logger.warning(
                            f"Error reading cache for file '{file_name}': {e}"
                        )
                        # [LOGGING-IMPROVEMENTS]
                        if config.settings.logging.log_private_eye_fixes:
                            logger.debug(e, exc_info=True)

            # If the DOB is not in the cache, then we read the file
            if file_dob_str is None:
                if config.settings.logging.log_private_eye_fixes:
                    logger.info(f"Reading file properties of '{file_name}' to get DOB.")
                file_dob_str = self._get_dob(file_name)

            if file_dob_str is not None:
                file_to_dob[file_name] = self._convert_string_to_datetime(
                    file_dob_str, fmt="%Y-%m-%d"
                ).date()

        return file_to_dob

    def _process_file(
        self,
        filename: str,
        skip_non_tabular_data: bool = False,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Process each file through private-eye.

        This will load each file via private eye and store it in a non-proprietary
        format for use with other parts of the Bitfount ecosystem.

        This takes place in two stages: first, the files are parsed and written
        out in the non-proprietary format. Second, they are processed to access
        the needed metadata, etc., which is placed into the `rows` object provided.

        Args:
            filename: The name of the file to process.
            skip_non_tabular_data: Whether we can avoid loading non-tabular data,
                e.g. image data (can be set to True when generating schemas).
            kwargs: Additional keyword arguments (ignored).

        Returns:
            The processed Heidelberg file as a list of dictionaries. The list will have
            either 1 or 2 elements depending on whether the file contained data for
            just one eye or both eyes.
        """
        save_prefix = self._recreate_file_structure(filename, exist_ok=True)

        try:
            # Running a file through private-eye will output 1+ JSON files which
            # describe the various distinct image sequences found in the image file.
            file_path = Path(filename)
            log_filename = file_path.name  # ensures as short as possible
            logger.debug(f"Reading file {log_filename} with private eye")
            json_file_paths, image_arrays = self._run_private_eye(
                file_path, save_prefix, stop_before_pixels=skip_non_tabular_data
            )
            logger.debug(f"Finished reading file {log_filename}")
            rows = []
            series_index = 0
            for idx, json_file_path in enumerate(json_file_paths, start=1):
                logger.debug(
                    f"Processing part {idx} of {len(json_file_paths)}"
                    f" for file {log_filename}"
                )
                with open(json_file_path) as json_file:
                    data = self._process_ophthalmology_file(
                        json_file,
                        save_prefix,
                        file_path,
                        series_index,
                        image_arrays,
                        skip_non_tabular_data,
                    )

                # Perform post-processing on data
                logger.debug(
                    f"Post-processing part {idx} of {len(json_file_paths)}"
                    f" for file {log_filename}"
                )
                if data:
                    series_index += 1
                    rows.append(
                        self._post_process_file(cast(dict[str, Any], data), file_path)
                    )
            logger.debug(f"Finished processing file {log_filename}")

        except NoParserForFileExtension as e:
            logger.warning(f"{str(e)}: {str(filename)}. Skipping processing.")
            # Delete the directory we created for this file
            try:
                shutil.rmtree(save_prefix)
            except FileNotFoundError as e:
                logger.warning(
                    f"Error whilst trying to delete {save_prefix} directory: {e}"
                )
            rows = []
        except Exception as e:
            # Just in case there is an unexpected error that we didn't
            # catch, we will log it here and skip the file.
            logger.warning(f"Unexpected error when processing file {filename}: {e}.")
            logger.debug(e, exc_info=True)
            # Delete the directory we created for this file
            try:
                shutil.rmtree(save_prefix)
            except FileNotFoundError as e:
                logger.warning(
                    f"Error whilst trying to delete {save_prefix} directory: {e}"
                )

            rows = []

        # Skip file if specified or empty
        if not rows:
            # There should already be another logger message explaining why the file
            # was skipped, so we don't need to log anything extra here.
            logger.warning(f"Skipping file {filename}.")
            self.skipped_files.add(filename)
            return []
        return rows

    def _run_private_eye(
        self, filename: Path, output_path: Path, stop_before_pixels: bool = False
    ) -> tuple[list[Path], list[Mapping[str, np.ndarray]]]:
        """Run private eye on a single file.

        Private eye will extract the OCT and SLO images from the file and
        save them to the output path as png files whilst also extracting
        the metadata as a json file.

        To avoid unnecessary latency, we will only write the raw images/metadata json
        file to disk if they do not already exist.

        Args:
            filename: The path to the Heidelberg file.
            output_path: The path to the output directory.
            stop_before_pixels: If True, the image data will not be loaded.

        Returns:
            The list of JSON file paths for the output.

        Raises:
            NoParserForFileExtension: If no parser has been specified for the given
                file extension.
        """
        output_formats: set[
            Union[
                private_eye.EntireFileOutputFormat,
                private_eye.IndividualImageOutputFormat,
            ]
        ] = set()
        images_exist = any(output_path.glob(f"*{RAW_IMAGE_FILE_EXTENSION}"))
        metadata_exists = any(output_path.glob(f"*{RAW_METADATA_FILE_EXTENSION}"))
        # We only want to write the raw images and metadata if they don't already
        # exist. If they do, we can just load them from disk. This could be optimised
        # further to avoid certain circumstances where we don't need to write the images
        # to disk even if they don't exist, such as if a task isn't running and fast
        # load is True, but this is a good start.
        if not metadata_exists:
            logger.debug("Writing metadata to disk")
            output_formats.add(private_eye.EntireFileOutputFormat.METADATA_JSON)
        if not stop_before_pixels and (not images_exist or not self.cache_images):
            logger.debug("Outputting raw images")
            output_formats.add(private_eye.IndividualImageOutputFormat.RAW_IMAGES)

        json_files: list[Path] = []
        # If cache_images is True, this will remain an empty list.
        # If it is False, it will contain a dictionaries mapping
        # the modality code and image idx to the corresponding numpy array.
        image_arrays: list[Mapping[str, np.ndarray]] = []

        # We want to process the files if either the images/metadata don't already
        # exist _OR_ if we are explicitly ignoring those (i.e. self.cache_images=False)
        if output_formats:
            file_extension = filename.suffix
            parser = self._get_parser(file_extension)

            options = private_eye.ParserOptions(
                heidelberg_skip_pdb=False, skip_image_data=stop_before_pixels
            )
            input_file = private_eye.InputFile.local_file(filename)
            parser_results = private_eye.read_all_from_local_file(
                input_file=input_file,
                parser=parser.value,
                options=options,
            )
            num_series = len(parser_results.results)
            logger.info(f"Detected {num_series} series in {filename.name}")
            for i, result in enumerate(parser_results.results, start=1):
                logger.debug(f"Series Number: {i}\n\t{result.series}")
                filename_prefix = f"{filename.stem}_Series_{i}"
                logger.info(f"Writing output for series {i} of {num_series}")
                output = private_eye.output_all_data(
                    output_formats=output_formats,
                    output_directory=output_path.absolute(),
                    filename_prefix=filename_prefix,
                    result=result,
                    output_sensitive_data=False,
                    pepper=None,
                    save_to_file=self.cache_images,
                )

                if (
                    private_eye.IndividualImageOutputFormat.RAW_IMAGES in output_formats
                    and not self.cache_images
                ):
                    for out in output:
                        if isinstance(out, dict):
                            image_arrays.append(out)

                logger.debug(f"Finished writing output for series {i}")
                json_files.append(
                    output_path.absolute()
                    / f"{filename_prefix}{RAW_METADATA_FILE_EXTENSION}"
                )
        else:
            logger.debug("Not running private eye as files already exist.")
            json_files.extend(list(output_path.glob(f"*{RAW_METADATA_FILE_EXTENSION}")))
        return json_files, image_arrays

    def _process_dataset(self, dataframe: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
        """Process any ophthalmology images."""
        if "images" in dataframe:
            images_df = self._process_cached_images(dataframe)
            bscans_locations_df = self._process_bscans_and_locations(dataframe)
            return pd.concat([dataframe, images_df, bscans_locations_df], axis=1)
        elif f"{IMAGE_COLUMN_PREFIX} 0" in dataframe:
            bscans_locations_df = self._process_bscans_and_locations(dataframe)
            return pd.concat([dataframe, bscans_locations_df], axis=1)
        else:
            logger.warning(
                "No image paths or image arrays could be found in dataframe."
                " Doing no processing."
            )

        return dataframe

    @staticmethod
    def _process_slo_sequence(
        image_sequence: _PrivateEyeImage, image_attrs: dict[str, list[Any]]
    ) -> dict[str, list[Any]]:
        """Process the SLO sequence.

        Args:
            image_sequence: The image sequence to process.
            image_attrs: The attributes of the images.

        Returns:
            The attributes of the images.
        """
        image_attrs["slo_size_width"].append(int(image_sequence["size"]["width"]))
        image_attrs["slo_size_height"].append(int(image_sequence["size"]["height"]))
        image_attrs["slo_dimensions_mm_width"].append(
            float(image_sequence["dimensions_mm"]["width"])
        )
        image_attrs["slo_dimensions_mm_height"].append(
            float(image_sequence["dimensions_mm"]["height"])
        )
        return image_attrs

    @staticmethod
    def _process_oct_sequence(
        image_sequence: _PrivateEyeImage, image_attrs: dict[str, list[Any]]
    ) -> dict[str, list[Any]]:
        """Process the OCT sequence.

        Args:
            image_sequence: The image sequence to process.
            image_attrs: The attributes of the images.

        Returns:
            The attributes of the images.
        """
        group_id = (
            int(image_sequence["group_id"])
            if image_sequence["group_id"]
            else image_sequence["group_id"]
        )
        image_attrs["group_ids"].append(group_id)
        image_attrs["size_width"].append(int(image_sequence["size"]["width"]))
        image_attrs["size_height"].append(int(image_sequence["size"]["height"]))
        image_attrs["dimensions_mm_width"].append(
            float(image_sequence["dimensions_mm"]["width"])
        )
        image_attrs["dimensions_mm_height"].append(
            float(image_sequence["dimensions_mm"]["height"])
        )
        image_attrs["dimensions_mm_depth"].append(
            float(image_sequence["dimensions_mm"]["depth"])
        )
        image_attrs["resolutions_mm_width"].append(
            float(image_sequence["resolutions_mm"]["width"])
        )
        image_attrs["resolutions_mm_depth"].append(
            float(image_sequence["resolutions_mm"]["depth"])
        )
        image_attrs["resolutions_mm_height"].append(
            float(image_sequence["resolutions_mm"]["height"])
        )
        for image_info in image_sequence["contents"]:
            if image_info["image_output_params"][0]["contour"] is not None:
                image_attrs["bscan_index"].append(
                    int(image_info["image_output_params"][0]["contour"]["bscan_index"])
                )
            first_photo_location = image_info["photo_locations"][0]
            if "start" in first_photo_location:
                image_attrs["photo_locations_start_x"].append(
                    float(first_photo_location["start"]["x"])
                )
                image_attrs["photo_locations_start_y"].append(
                    float(first_photo_location["start"]["y"])
                )
                image_attrs["photo_locations_end_x"].append(
                    float(first_photo_location["end"]["x"])
                )
                image_attrs["photo_locations_end_y"].append(
                    float(first_photo_location["end"]["y"])
                )
            else:
                # Try to use centre and radius to derive locations
                # This is 'centre' or 'center' based on protocol.
                centre_string = None
                if "center" in first_photo_location:
                    centre_string = "center"
                elif "centre" in first_photo_location:
                    centre_string = "centre"
                if (
                    (centre_string is not None)
                    and (centre_string in first_photo_location)
                    and ("radius" in first_photo_location)
                ):
                    center_x = float(first_photo_location[centre_string]["x"])
                    center_y = float(first_photo_location[centre_string]["y"])
                    radius = float(first_photo_location["radius"])
                    image_attrs["photo_locations_start_x"].append(center_x - radius)
                    image_attrs["photo_locations_start_y"].append(center_y + radius)
                    image_attrs["photo_locations_end_x"].append(center_x + radius)
                    image_attrs["photo_locations_end_y"].append(center_y - radius)
                else:
                    logger.debug("Could not find photo location information.")

        return image_attrs

    def _get_images_from_private_eye_image_sequences(
        self,
        image_sequences: _ImageSequence,
        skip_non_tabular_data: bool,
        save_path: Path,
        num_frames: int,
        json_file: TextIO,
        image_arrays: list[Mapping[str, np.ndarray]],
    ) -> Mapping[str, Union[np.ndarray, str, list[str]]]:
        """Get the images from the private eye image sequences.

        Args:
            image_sequences: The image sequences to process.
            skip_non_tabular_data: Whether we can avoid loading non-tabular data,
                e.g. image data (can be set to True when generating schemas).
            save_path: The path to save the images to.
            num_frames: The number of frames in the file.
            json_file: The path to the JSON file.
            image_arrays: The image arrays to process.

        Returns:
            The images from the private eye image sequences.
        """
        images: Mapping[str, Union[np.ndarray, str, list[str]]]
        if skip_non_tabular_data:
            images = {}
            for frame_num in range(num_frames):
                image_col_name = f"{IMAGE_COLUMN_PREFIX} {frame_num}"
                self.image_columns.add(image_col_name)
                images[image_col_name] = "<SKIPPED>"

            num_slos = self._get_num_slos_from_image_sequence(image_sequences)
            for slo_num in range(num_slos):
                slo_col_name = f"{SLO_IMAGE_ATTRIBUTE} {slo_num}"
                self.image_columns.add(slo_col_name)
                images[slo_col_name] = "<SKIPPED>"

        else:
            file_prefix = Path(json_file.name).stem
            if len(image_arrays) == 0:
                oct_images = self._get_oct_images_from_paths(save_path, file_prefix)
                slo_images = self._get_slo_images_from_paths(save_path, file_prefix)
                # There is special handling for these keys in this dictionary which
                # will be unpacked by `_process_cached_images`
                images = {
                    "images": [str(save_path / x.name) for x in oct_images],
                    "slo_images": [str(save_path / x.name) for x in slo_images],
                }
            else:
                images = self._get_images_from_dict(image_arrays)

        return images

    def _create_processed_data(
        self,
        image_attrs: dict[str, list[Any]],
        metadata: Metadata,
        filename_path: Path,
        num_frames: int,
        series_index: int,
        image_sequences: _ImageSequence,
    ) -> ProcessedDataRequiredTypes:
        """Create the processed data for the file.

        Args:
            image_attrs: The attributes of the images.
            metadata: The metadata of the file.
            filename_path: The path to the file.
            num_frames: The number of frames in the file.
            series_index: The index of the series.
            image_sequences: The image sequences in the file.

        Returns:
            The processed data for the file.
        """
        # Convert the date of birth to a datetime
        dob = self._convert_datetime_string_to_datetime(
            metadata["patient"]["date_of_birth"]
        )
        study_date = self._convert_datetime_string_to_datetime(
            metadata["exam"]["scan_datetime"]
        )
        processed_data: ProcessedDataRequiredTypes = {
            "source_info": f"{filename_path.stem}",
            "group_id": image_attrs["group_ids"][0],
            "slo_size_width": image_attrs["slo_size_width"][0],
            "slo_size_height": image_attrs["slo_size_height"][0],
            "slo_dimensions_mm_width": image_attrs["slo_dimensions_mm_width"][0],
            "slo_dimensions_mm_height": image_attrs["slo_dimensions_mm_height"][0],
            "size_width": image_attrs["size_width"][0],
            "size_height": image_attrs["size_height"][0],
            "dimensions_mm_width": image_attrs["dimensions_mm_width"][0],
            "dimensions_mm_height": image_attrs["dimensions_mm_height"][0],
            "dimensions_mm_depth": image_attrs["dimensions_mm_depth"][0],
            "resolutions_mm_width": image_attrs["resolutions_mm_width"][0],
            "resolutions_mm_depth": image_attrs["resolutions_mm_depth"][0],
            "resolutions_mm_height": image_attrs["resolutions_mm_height"][0],
            "photo_locations_start_x": image_attrs["photo_locations_start_x"],
            "photo_locations_start_y": image_attrs["photo_locations_start_y"],
            "photo_locations_end_x": image_attrs["photo_locations_end_x"],
            "photo_locations_end_y": image_attrs["photo_locations_end_y"],
            "patient_key": metadata["patient"]["patient_key"],
            "first_name": metadata["patient"]["first_name"],
            "last_name": metadata["patient"]["last_name"],
            "gender": metadata["patient"]["gender"],
            "date_of_birth": metadata["patient"]["date_of_birth"],
            "scan_datetime": metadata["exam"]["scan_datetime"],
            "scanner_model": metadata["exam"]["scanner_model"],
            "laterality": metadata["series"]["laterality"],
            "fixation": metadata["series"]["fixation"],
            "protocol": metadata["series"]["protocol"],
            "num_bscans": num_frames,
            "num_modalities": len(image_sequences),
            # Aliases of existing columns added for DICOM compatibility
            "Manufacturer": metadata["exam"]["manufacturer"],
            "Manufacturer's Model Name": metadata["exam"]["scanner_model"],
            "Columns": image_attrs["size_width"][0],
            "Rows": image_attrs["size_height"][0],
            "Pixel Spacing Row": image_attrs["resolutions_mm_height"][0],
            "Pixel Spacing Column": image_attrs["resolutions_mm_width"][0],
            "Slice Thickness": image_attrs["resolutions_mm_depth"][0],
            "Number of Frames": num_frames,
            "Patient's Birth Date": dob,
            "Patient's Sex": metadata["patient"]["gender"],
            "Patient's Name": "{first_name} {last_name}".format(
                first_name=metadata["patient"]["first_name"],
                last_name=metadata["patient"]["last_name"],
            ),
            "Scan Laterality": metadata["series"]["laterality"],
            "Acquisition DateTime": study_date,
            "Study Date": study_date,
            # Metadata
            "_original_filename": str(filename_path),
            "_last_modified": datetime.fromtimestamp(os.path.getmtime(filename_path)),
            "_series_index": int(series_index),
        }
        return processed_data

    def _process_ophthalmology_file(
        self,
        json_file: TextIO,
        save_path: Path,
        filename_path: Path,
        series_index: int,
        image_arrays: list[Mapping[str, np.ndarray]],
        skip_non_tabular_data: bool = False,
    ) -> Optional[ProcessedDataTypes]:
        """Process the ophthalmology file.

        Returns:
            The processed file data as a dictionary of records. If there was no
            relevant data, returns None.

        Raises:
            NoParserForFileExtension: If no parser has been specified for the given
                file extension.
        """
        # We only want to concern ourselves with files that correspond to the defined
        # OCT_SERIES_PROTOCOL, so if this metadata doesn't relate to that, fast exit.
        file_extension = filename_path.suffix
        metadata: Metadata = json.load(json_file)
        if (series := metadata["series"]["protocol"]) not in self._get_config(
            file_extension
        )["OCT_SERIES_PROTOCOL"]:
            logger.warning(
                f"Series {series} does not match the specified OCT series protocol. "
                "Ignoring this series."
            )
            return None

        # Otherwise, we are at least looking at the right metadata
        image_sequences = metadata["images"]["images"]
        # TODO: [BIT-3487] Add support for re-sizing OCT images
        # Create a temporary dictionary to store image metadata
        image_attrs: dict[str, list[Any]] = defaultdict(list)
        # Now we run through each of the image sequences that are defined in
        # the metadata and process them according to their modality
        for image_sequence in image_sequences:
            # Process sequences of SLO images
            if (
                image_sequence["modality"]
                in self._get_config(file_extension)["SLO_MODALITY"]
            ):
                image_attrs = self._process_slo_sequence(image_sequence, image_attrs)

            # Process sequences of OCT images
            elif image_sequence["modality"] == OCT_MODALITY:
                image_attrs = self._process_oct_sequence(image_sequence, image_attrs)

        # If we got _any_ sequences out that matched our modalities then we
        # can compress this down to a single data row
        if len(image_attrs["group_ids"]) > 0:
            num_frames = self._get_num_bscans_from_image_sequence(image_sequences)
            processed_data = self._create_processed_data(
                image_attrs,
                metadata,
                filename_path,
                num_frames,
                series_index,
                image_sequences,
            )

            # Add images to the processed data
            images = self._get_images_from_private_eye_image_sequences(
                image_sequences,
                skip_non_tabular_data,
                save_path,
                num_frames,
                json_file,
                image_arrays,
            )

            images = {key: value for key, value in sorted(images.items())}
            data = {**processed_data, **images}
            return data

        return None

    @staticmethod
    def _convert_datetime_string_to_datetime(
        datetime_string: str,
    ) -> Union[str, pd.Timestamp]:
        """Converts the datetime string to datetime.

        Args:
            datetime_string: The birth date string.

        Returns:
            The converted birth date.
        """
        try:
            return pd.to_datetime(datetime_string)
        except Exception as e:
            # if not a 'standard' date, get the first 8 characters,
            # assuming it is in the format %Y%m%d. If this doesn't work
            # ignore errors and pass-through the original string.
            logger.debug(
                "Field 'date_of_birth' not in a standard date format. "
                f"Raised error: `{e}`"
            )
            try:
                return pd.to_datetime(datetime_string[:10], format="%Y-%m-%d")
            except OutOfBoundsDatetime:
                logger.warning(
                    "The value of field 'date_of_birth' is out bounds, "
                    "defaulting to minimum date."
                )
                return pd.Timestamp.min + pd.Timedelta(days=1)
            except Exception as e:
                logger.debug(f"Error when converting to datetime: {e}")
                logger.warning(
                    "Field 'date_of_birth' cannot be loaded as datetime, "
                    "loading as string."
                )

        return datetime_string

    def _process_cached_images(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process ophthalmology images.

        This will extract the images from the relevant column of the dataframe and
        place them into a new dataframe with individual columns for each image slice
        for both the OCT and SLO image sequences. It will also extract the bscan
        indices and photo locations for each image.

        Args:
            df: The dataframe containing the images to process.

        Returns:
            A dataframe containing the processed images.
        """
        # Extract the OCT images
        images_series = df.pop("images")
        modified_images_series = []
        max_col = -1
        for j in range(0, len(images_series)):
            row = cast(list[str], images_series[j])
            row.sort(
                key=lambda x: (
                    x[x.rfind("_") + 1 : x.find("-")],
                    int(x[x.rfind("-") + 1 : x.find(RAW_IMAGE_FILE_EXTENSION)]),
                )
            )
            modified_images_series.append(row)
            if len(row) > max_col:
                max_col = len(row)
        images_df = pd.DataFrame(
            modified_images_series,
            index=df.index,
            columns=[f"{IMAGE_COLUMN_PREFIX} {i}" for i in range(max_col)],
        )

        # Extract the SLO images
        slo_images_series = df.pop("slo_images")
        # Determine how many SLO columns there need to be
        max_num_slos = 0
        for j in range(0, len(slo_images_series)):
            if len(slo_images_series[j]) > max_num_slos:
                max_num_slos = len(slo_images_series[j])
        slo_images_df = pd.DataFrame(
            slo_images_series.tolist(),
            index=df.index,
            columns=[f"{SLO_IMAGE_ATTRIBUTE} {i}" for i in range(max_num_slos)],
        )
        return pd.concat([images_df, slo_images_df], axis=1)

    def _process_bscans_and_locations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process bscans and locations of images."""
        # Get the number of bscans to create an index
        max_col = -1
        for j in range(0, len(df["photo_locations_start_x"])):
            if len(df["photo_locations_start_x"][j]) > max_col:
                max_col = len(df["photo_locations_start_x"][j])
        bscan_df = pd.DataFrame(
            [[i for i in range(max_col)]],
            index=df.index,
            columns=[f"bscan_index_image_{i}" for i in range(max_col)],
        )

        # Extract the photo locations
        location_dfs: list[pd.DataFrame] = []
        for dim_ in ["x", "y"]:
            for loc_ in ["start", "end"]:
                df_loc_ = pd.DataFrame(
                    df.pop(f"photo_locations_{loc_}_{dim_}").tolist(),
                    index=df.index,
                    columns=[f"loc_{loc_}_{dim_}_image_{i}" for i in range(max_col)],
                )
                location_dfs.append(df_loc_)
        return pd.concat([bscan_df] + location_dfs, axis=1)
