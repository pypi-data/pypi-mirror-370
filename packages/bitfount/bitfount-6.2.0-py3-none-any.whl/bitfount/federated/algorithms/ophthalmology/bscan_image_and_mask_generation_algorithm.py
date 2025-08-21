"""Algorithms and related functionality for simply outputting data to CSV."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
import json
import math
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Union, cast

import desert
from marshmallow import fields
import marshmallow_enum
import numpy as np
import pandas as pd
import PIL

from bitfount import config
from bitfount.data.datasources.base_source import BaseSource, FileSystemIterableSource
from bitfount.data.datasources.dicom_source import DICOM_SCAN_LATERALITY_ATTRIBUTE
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.federated.algorithms.base import (
    BaseNonModelAlgorithmFactory,
    BaseWorkerAlgorithm,
    NoResultsModellerAlgorithm,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    DATASOURCE_IMAGE_PREFIX_COLUMNS,
    NUMBER_OF_FRAMES_COLUMN,
    RESULTS_IMAGE_PREFIX,
    RESULTS_SUFFIX,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_utils import (
    draw_segmentation_mask_on_orig_image,
    get_data_for_files,
    parse_mask_json,
)
from bitfount.federated.exceptions import AlgorithmError
from bitfount.federated.logging import _get_federated_logger
from bitfount.models.types import (
    AltrisBiomarkerOutput,
    AltrisGASegmentationModelPostV11Output,
    MaskAltrisBiomarker,
    MaskSegmentationModel,
)
from bitfount.types import T_FIELDS_DICT, UsedForConfigSchemas
from bitfount.visualisation.ga_trial_pdf_jade import AltrisScan

if TYPE_CHECKING:
    from bitfount.federated.privacy.differential import DPPodConfig


logger = _get_federated_logger("bitfount.federated")


@dataclass
class SegmentationConfig(UsedForConfigSchemas):
    """Configuration for a segmentation mask."""

    id: str
    color: tuple[int, int, int]
    label: Optional[str] = None

    def __post_init__(self) -> None:
        """Post-initialization to ensure the label is set correctly."""
        if self.label is None:
            self.label = self.id
        self.validate_args()

    def validate_args(self) -> None:
        """Validate a segmentation configuration.

        Ensures that given config complies with the expected structure and types.
        If label is not provided, it defaults to the ID.
        Checks for color values that adhere to the RGB format.
        """
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("Segmentation ID must be a non-empty string.")
        if not isinstance(self.color, tuple) or len(self.color) != 3:
            raise ValueError("Segmentation color must be a tuple of three integers.")
        if self.label is not None and not isinstance(self.label, str):
            raise ValueError("Segmentation label must be a string.")
        r, g, b = self.color
        if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
            raise ValueError(
                "Segmentation color values must be in the range 0-255 for RGB."
            )


@dataclass
class SegmentationConfigList:
    """Configuration for a list of segmentation masks."""

    segmentation_config_list: list[SegmentationConfig]

    def __post_init__(self) -> None:
        """Ensure the list is not empty and all elements are SegmentationConfig."""
        self.validate_args()

    def validate_args(self) -> None:
        """Validate the arguments in the segmentation config list."""
        if not self.segmentation_config_list:
            raise ValueError("Segmentation config list cannot be empty.")

    def get_segmentation_config(
        self,
    ) -> tuple[dict[str, int], dict[str, tuple[int, int, int]], dict[str, str]]:
        """Get the segmentation configuration as a tuple of dictionaries.

        Returns:
            Tuple of dictionaries containing segmentation labels and colors.
        """
        segmentation_labels: dict[str, int] = {}
        segmentation_colors: dict[str, tuple[int, int, int]] = {}
        formatted_segmentation_labels: dict[str, str] = {}

        for idx, segmentation_config in enumerate(self.segmentation_config_list):
            segmentation_labels[segmentation_config.id] = idx
            segmentation_colors[segmentation_config.id] = segmentation_config.color
            formatted_segmentation_labels[segmentation_config.id] = (
                segmentation_config.label
                if segmentation_config.label is not None
                else segmentation_config.id
            )

        return (
            segmentation_labels,
            segmentation_colors,
            formatted_segmentation_labels,
        )


class ImageFormats(Enum):
    """Supported image formats for saving images."""

    JPEG = "JPEG"
    PNG = "PNG"


@dataclass
class ImageSaveOptions:
    """Options for saving images.

    Note: 'image_subsampling' and 'image_progressive' only
    apply to JPEG format and are ignored for PNG.
    Note: 'image_transparency' only applies
    to PNG format and is ignored for JPEG.
    """

    image_format: ImageFormats = ImageFormats.JPEG
    image_optimize: bool = True
    image_quality: int = 90
    image_subsampling: int = 0
    image_progressive: bool = True
    image_transparency: bool = False

    def __post_init__(self) -> None:
        allowed_formats = {fmt.value for fmt in ImageFormats}
        if self.image_format.value not in allowed_formats:
            raise ValueError(f"image_format must be one of {allowed_formats}.")
        if not (0 <= self.image_quality <= 100):
            raise ValueError("image_quality must be between 0 and 100.")
        allowed_subsampling = {0, 1, 2}
        if self.image_subsampling not in allowed_subsampling:
            raise ValueError(f"image_subsampling must be one of {allowed_subsampling}.")
        # Only JPEG supports subsampling and progressive
        if self.image_format != ImageFormats.JPEG:
            if self.image_subsampling != 0:
                self.image_subsampling = 0
            if self.image_progressive:
                self.image_progressive = False
        # Only PNG supports transparency
        if self.image_format != ImageFormats.PNG and self.image_transparency:
            self.image_transparency = False


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side for generating and saving B-scan images and masks."""

    segmentation_configs: list[SegmentationConfig]
    save_path: Union[str, os.PathLike]
    output_original_bscans: bool
    image_save_options: ImageSaveOptions

    def __init__(
        self,
        segmentation_configs: list[SegmentationConfig],
        save_path: Union[str, os.PathLike],
        output_original_bscans: bool = False,
        image_format: ImageFormats = ImageFormats.JPEG,
        image_optimize: bool = True,
        image_quality: int = 90,
        image_subsampling: int = 0,
        image_progressive: bool = True,
        image_transparency: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initializes the worker side algorithm.

        Args:
            segmentation_configs: List of segmentation configurations.
            save_path: Path to save output images and masks.
            output_original_bscans: Flag to save original B-scans.
            image_format: Format for saving images, JPEG and PNG are supported.
            image_optimize: Flag to optimize images.
            image_quality: Quality of saved images.
            image_subsampling: Subsampling for saved images.
            image_progressive: Flag for progressive saving.
            image_transparency: Flag for transparency in PNG images.
            **kwargs: Additional keyword arguments for the base class.

        Note:
            'image_subsampling' and 'image_progressive' only
            apply to JPEG format and are ignored for PNG.
            'image_transparency' only applies to PNG
            format and is ignored for JPEG.
        """
        super().__init__(**kwargs)
        if not save_path:
            raise ValueError("Save path is not set. Please provide a valid path.")

        segmentation_config_list = SegmentationConfigList(
            segmentation_config_list=list(segmentation_configs)
        )
        (
            self.segmentation_labels,
            self.segmentation_colors,
            self.formatted_segmentation_labels,
        ) = segmentation_config_list.get_segmentation_config()
        self.save_path = save_path
        self.output_original_bscans = output_original_bscans
        self.image_save_options = ImageSaveOptions(
            image_format=image_format,
            image_optimize=image_optimize,
            image_quality=image_quality,
            image_subsampling=image_subsampling,
            image_progressive=image_progressive,
            image_transparency=image_transparency,
        )

    def initialise(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Sets the datasource and checks for pod identifier.

        Args:
            datasource: The data source to use.
            data_splitter: Optional data splitter.
            pod_dp: Optional differential privacy pod config.
            pod_identifier: Identifier for the pod.
            **kwargs: Additional keyword arguments.
        """
        self.initialise_data(datasource=datasource, data_splitter=data_splitter)

    def _get_test_data_from_data_source(
        self, filenames: list[str]
    ) -> Iterable[pd.DataFrame]:
        """Extract test data from datasource by joining with predictions.

        Args:
            filenames: List of filenames to retrieve data for.

        Returns:
            Iterable of DataFrames containing the test data.
        """
        test_data_dfs: Iterable[pd.DataFrame]
        logger.debug(f"Retrieving data for: {filenames}")
        # use_cache is False as we need the image data to produce the outputs
        df: pd.DataFrame = get_data_for_files(
            cast(FileSystemIterableSource, self.datasource),
            filenames,
            use_cache=False,
        )
        test_data_dfs = [df]
        if not len(filenames) == len(test_data_dfs[0]):
            raise AlgorithmError(
                "The number of files does not match the number of records in the "
                "retrieved data."
            )
        return test_data_dfs

    def _append_results_to_orig_data(
        self,
        results_df: pd.DataFrame,
        test_data_dfs: Iterable[pd.DataFrame],
        filenames: list[str],
    ) -> Iterable[pd.DataFrame]:
        """Append the results to the original data by merging DataFrames.

        Args:
            results_df: DataFrame with model results.
            test_data_dfs: Iterable of DataFrames with test data.
            filenames: List of filenames for keyed merge.

        Returns:
            Iterable of merged DataFrames.

        Raises:
            ValueError: If required key columns are missing.
        """
        logger.debug("Appending results to the original data.")
        test_data_dfs = cast(list[pd.DataFrame], test_data_dfs)
        if ORIGINAL_FILENAME_METADATA_COLUMN not in test_data_dfs[0].columns:
            raise ValueError(
                "Retrieved file data dataframe is missing the required "
                f"key column: {ORIGINAL_FILENAME_METADATA_COLUMN}"
            )
        if ORIGINAL_FILENAME_METADATA_COLUMN not in results_df.columns:
            raise ValueError(
                "Results dataframe is missing the required key column: "
                f"{ORIGINAL_FILENAME_METADATA_COLUMN}"
            )
        test_data_dfs = [
            test_data_dfs[0].merge(results_df, on=ORIGINAL_FILENAME_METADATA_COLUMN)
        ]
        return test_data_dfs

    def _extract_scan_data(
        self, datasource_row: pd.Series
    ) -> tuple[int, Optional[str], Optional[str]]:
        """Get the scan data from the datasource row.

        Args:
            datasource_row: Row from the datasource DataFrame.

        Returns:
            Tuple of (total_bscans, laterality, original_filename).
        """
        try:
            total_bscans = int(datasource_row[NUMBER_OF_FRAMES_COLUMN])
        except KeyError as e:
            logger.error(
                f"Unable to extract number of frames from the datasource row: {e}",
                exc_info=True,
            )
            total_bscans = 1
        except Exception as e:
            logger.error(
                f"Unexpected error extracting number of frames: {e}",
                exc_info=True,
            )
            total_bscans = 1
        try:
            laterality = str(datasource_row[DICOM_SCAN_LATERALITY_ATTRIBUTE])
        except KeyError as e:
            logger.error(
                f"Unable to extract laterality from the datasource row: {e}",
                exc_info=True,
            )
            laterality = None
        except Exception as e:
            logger.error(
                f"Unexpected error extracting laterality: {e}",
                exc_info=True,
            )
            laterality = None
        try:
            original_filename = str(datasource_row[ORIGINAL_FILENAME_METADATA_COLUMN])
        except KeyError as e:
            logger.error(
                f"Unable to extract original filename from the datasource row: {e}",
                exc_info=True,
            )
            original_filename = None
        except Exception as e:
            logger.error(
                f"Unexpected error extracting original filename: {e}",
                exc_info=True,
            )
            original_filename = None
        return total_bscans, laterality, original_filename

    def _extract_bscan_data(
        self, datasource_row: pd.Series, bscan_idx: int
    ) -> Optional[np.ndarray]:
        """Extract the bscan data from the datasource row.

        Args:
            datasource_row: Row from the datasource DataFrame.
            bscan_idx: Index of the B-scan.

        Returns:
            Numpy array of the B-scan data, or None if not found.
        """
        bscan_data: Optional[np.ndarray]
        try:
            bscan_data = datasource_row[
                f"{DATASOURCE_IMAGE_PREFIX_COLUMNS} {bscan_idx}"
            ]
        except KeyError as e:
            logger.error(
                f"Unable to extract bscan {bscan_idx} data from the datasource "
                f"row: {e}",
                exc_info=True,
            )
            bscan_data = None
        except Exception as e:
            logger.error(
                f"Unexpected error extracting bscan {bscan_idx} data: {e}",
                exc_info=True,
            )
            bscan_data = None
        return bscan_data

    def _extract_bscan_predictions(
        self, results_df: pd.DataFrame, idx: pd.Index, bscan_idx: int
    ) -> Optional[AltrisBiomarkerOutput | AltrisGASegmentationModelPostV11Output]:
        """Extract the bscan predictions from the results dataframe.

        Args:
            results_df: DataFrame with model results.
            idx: Index of the row.
            bscan_idx: Index of the B-scan.

        Returns:
            List with predictions, or None if not found.
        """
        predictions: Optional[
            AltrisBiomarkerOutput | AltrisGASegmentationModelPostV11Output
        ]
        try:
            predictions_str = str(
                results_df.loc[idx][
                    f"{RESULTS_IMAGE_PREFIX}_{bscan_idx}{RESULTS_SUFFIX}"
                ]
            ).replace("'", '"')
            predictions = json.loads(predictions_str)
        except KeyError as e:
            logger.error(
                f"Unable to extract bscan {bscan_idx} predictions from the results "
                f"dataframe: {e}",
                exc_info=True,
            )
            predictions = None
        except Exception as e:
            logger.error(
                f"Unexpected error extracting bscan {bscan_idx} predictions: {e}",
                exc_info=True,
            )
            predictions = None
        return predictions

    def _extract_mask_from_predictions(
        self,
        predictions: AltrisBiomarkerOutput | AltrisGASegmentationModelPostV11Output,
    ) -> MaskAltrisBiomarker | MaskSegmentationModel:
        """Validate predictions format and extract the mask dict.

        Expects the predictions to be a list of JSONs, with each JSON being
        in the following format:
        {"mask": {"instances": [], "metadata": {"height": float, "width": float}}}

        Args:
            predictions: The predictions from the model.

        Returns:
            The mask data extracted from the predictions.

        Raises:
            ValueError: If the predictions format is not as expected.
        """
        if not isinstance(predictions, list):
            raise ValueError(
                f"Predictions are not a list as expected: {type(predictions)}"
            )

        if not predictions:
            raise ValueError("Predictions list is empty.")

        if not isinstance(predictions[0], dict):
            raise ValueError(
                f"First element of predictions is not a dict: {type(predictions[0])}"
            )

        if "mask" not in predictions[0]:
            raise ValueError(
                f"'mask' key not found in predictions[0]. "
                f"Keys: {list(predictions[0].keys())}"
            )
        return predictions[0]["mask"]

    def _get_bscan_image_with_mask(
        self,
        bscan_idx: int,
        bscan_data: np.ndarray,
        total_bscans: int,
        mask_data: MaskAltrisBiomarker | MaskSegmentationModel,
        laterality: Optional[str] = None,
    ) -> AltrisScan:
        """Get the scan object with the original image and segmentation mask overlay.

        Args:
            bscan_idx: Index of the B-scan.
            bscan_data: Numpy array of the B-scan image.
            total_bscans: Total number of B-scans.
            mask_data: Dictionary with mask data.
            laterality: Optional laterality string.

        Returns:
            AltrisScan object containing the image and mask.
        """
        bscan_image = PIL.Image.fromarray(bscan_data)
        mask = parse_mask_json(mask_data, self.segmentation_labels)
        img_w_mask, legend2color = draw_segmentation_mask_on_orig_image(
            mask=mask,
            image=bscan_image,
            segmentation_labels=self.segmentation_labels,
            segmentation_colors=self.segmentation_colors,
            formatted_segmentation_labels=self.formatted_segmentation_labels,
        )
        scan = AltrisScan(
            bscan_image=bscan_image,
            bscan_idx=bscan_idx,
            bscan_total=total_bscans,
            bscan_w_mask=img_w_mask,
            legend2color=legend2color,
            laterality=laterality,
        )
        return scan

    def _create_output_directory(
        self, original_filename: Optional[str] = None, task_id: Optional[str] = None
    ) -> Path:
        """Create the output directory for saving images and masks.

        If `task_id` is provided, it will create a subdirectory for that task.
        Otherwise, the main `save_path` will be used directly.
        If `original_filename` is provided, it will create a subdirectory for the
        original filename (without extension) to maintain a structured directory layout.
        Otherwise, it will create a subdirectory of the current datetime.

        Args:
            original_filename: Optional original filename for directory structure.
            task_id: Optional task ID for directory structure.

        Returns:
            Path to the created directory.
        """
        directory_path = Path(self.save_path)
        if task_id:
            directory_path = directory_path / task_id

        if original_filename:
            base_filename = Path(original_filename).stem
            directory_path = directory_path / base_filename
        else:
            timestamp = math.floor(pd.Timestamp.now().timestamp())
            directory_path = directory_path / str(timestamp)

        directory_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Output directory created at: {directory_path}")
        return directory_path

    def _save_original_bscan(
        self,
        scan: AltrisScan,
        original_filename: str,
        bscan_idx: int,
        output_directory: Path,
    ) -> None:
        """Save the original B-scan image."""
        ext = f".{self.image_save_options.image_format.value.lower()}"
        base_filename = Path(original_filename).stem
        bscans_directory_path = output_directory / "bscans"
        bscans_directory_path.mkdir(parents=True, exist_ok=True)
        bscan_filename = f"{base_filename}_{bscan_idx}{ext}"
        bscan_filepath = bscans_directory_path / bscan_filename
        if bscan_filepath.exists():
            timestamp = math.floor(pd.Timestamp.now().timestamp())
            bscan_filename = f"{base_filename}_{bscan_idx}_{timestamp}{ext}"
            bscan_filepath = bscans_directory_path / bscan_filename
        img = cast(PIL.Image.Image, scan.bscan_image)
        if self.image_save_options.image_transparency:
            if img.mode != "RGBA":
                img = img.convert("RGBA")
        else:
            if img.mode != "RGB":
                img = img.convert("RGB")
        img.save(
            str(bscan_filepath),
            format=self.image_save_options.image_format.value,
            optimize=self.image_save_options.image_optimize,
            quality=self.image_save_options.image_quality,
            subsampling=self.image_save_options.image_subsampling,
            progressive=self.image_save_options.image_progressive,
        )

    def _save_bscan_mask(
        self,
        scan: AltrisScan,
        original_filename: str,
        bscan_idx: int,
        output_directory: Path,
    ) -> None:
        """Save the B-scan mask image."""
        ext = f".{self.image_save_options.image_format.value.lower()}"
        base_filename = Path(original_filename).stem
        masks_directory_path = output_directory / "masks"
        masks_directory_path.mkdir(parents=True, exist_ok=True)
        mask_filename = f"{base_filename}_{bscan_idx}{ext}"
        mask_filepath = masks_directory_path / mask_filename
        if mask_filepath.exists():
            timestamp = math.floor(pd.Timestamp.now().timestamp())
            mask_filename = f"{base_filename}_{bscan_idx}_{timestamp}{ext}"
            mask_filepath = masks_directory_path / mask_filename
        mask_img = cast(PIL.Image.Image, scan.bscan_w_mask)
        if self.image_save_options.image_transparency:
            if mask_img.mode != "RGBA":
                mask_img = mask_img.convert("RGBA")
        else:
            if mask_img.mode != "RGB":
                mask_img = mask_img.convert("RGB")
        mask_img.save(
            str(mask_filepath),
            format=self.image_save_options.image_format.value,
            optimize=self.image_save_options.image_optimize,
            quality=self.image_save_options.image_quality,
            subsampling=self.image_save_options.image_subsampling,
            progressive=self.image_save_options.image_progressive,
        )

    def _save_scan_output(
        self,
        scan: AltrisScan,
        original_filename: str,
        bscan_idx: int,
        output_directory: Path,
    ) -> None:
        """Save the B-scan image and mask to the specified path."""
        if self.output_original_bscans:
            self._save_original_bscan(
                scan, original_filename, bscan_idx, output_directory
            )
        self._save_bscan_mask(scan, original_filename, bscan_idx, output_directory)

    def run(
        self,
        results_df: pd.DataFrame,
        filenames: list[str],
        task_id: Optional[str] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Outputs scan bscan images and masks.

        Args:
            results_df: The DataFrame containing the predictions from the GA model.
                This DataFrame doesn't contain the full set of file details, but
                rather just the model outputs for each file.
                If `filenames` is provided, each dataframe must contain a
                ORIGINAL_FILENAME_METADATA_COLUMN which describes which file each
                row is associated with.
            task_id: The ID of the task run, if present.
            filenames: The list of files that the results correspond to.
                If not provided, will iterate through all files in the
                dataset to find the corresponding ones.
            **kwargs: Additional arguments for the algorithm.

        Raises:
            AlgorithmError:
                - If the datasource is not a FileSystemIterableSource
                - If the number of results does not match the number of files
                - If the number of predictions does not match the number of
                retrieved records
            ValueError:
                - If required key columns are missing from the dataframes
                - If unable to find data keys/filenames in the predictions dataframe
            KeyError:
                - If columns needed for extraction are missing
            TypeError:
                - If unexpected types are encountered during processing

        Returns:
            A DataFrame with the orignial filename and the path to the saved images.
        """
        if not isinstance(self.datasource, FileSystemIterableSource):
            # Check that the datasource is a FileSystemIterableSource
            raise AlgorithmError(
                "The algorithm is only compatible with "
                "FileSystemIterableSource. Selected dataset"
                " is not compatible."
            )
        if not len(filenames) == len(results_df):
            # Check that we have the expected number of results for the number of files
            raise AlgorithmError(
                "The results dataframe does not match provided filenames."
            )
        test_data_dfs = self._get_test_data_from_data_source(filenames=filenames)
        test_data_dfs = self._append_results_to_orig_data(
            test_data_dfs=test_data_dfs,
            results_df=results_df,
            filenames=filenames,
        )

        len_test_data_dfs = 0
        image_output_paths: list[tuple[str, Optional[Path]]] = []
        for test_df in test_data_dfs:
            len_test_data_dfs += len(test_df)
            for idx, datasource_row in test_df.iterrows():
                # Iterrows() iterates over DataFrame rows as (index, Series) pairs.
                index = cast(pd.Index, idx)
                try:
                    total_bscans, laterality, original_filename = (
                        self._extract_scan_data(datasource_row=datasource_row)
                    )

                    logger.debug(f"Processing bscan data for file: {original_filename}")
                    output_directory = self._create_output_directory(
                        original_filename=original_filename, task_id=task_id
                    )
                except Exception as e:
                    logger.error(f"Error processing bscan data for index {index}.")
                    logger.error(f"Error details: {e}", exc_info=True)
                    continue

                # Generate image with mask for all bscans
                for bscan_idx in range(total_bscans):
                    try:
                        logger.debug(
                            f"Processing bscan {bscan_idx} out of {total_bscans}"
                        )
                        bscan_data = self._extract_bscan_data(
                            datasource_row=datasource_row, bscan_idx=bscan_idx
                        )
                        if bscan_data is None:
                            logger.error(
                                f"Failed to extract bscan data for "
                                f"{original_filename} (bscan_idx={bscan_idx})"
                            )
                            continue
                        predictions = self._extract_bscan_predictions(
                            results_df=results_df, idx=index, bscan_idx=bscan_idx
                        )
                        if predictions is None:
                            logger.error(
                                f"Failed to extract predictions for "
                                f"{original_filename} (bscan_idx={bscan_idx})"
                            )
                            continue
                        mask_data = self._extract_mask_from_predictions(predictions)
                        scan = self._get_bscan_image_with_mask(
                            bscan_idx=bscan_idx,
                            bscan_data=bscan_data,
                            total_bscans=total_bscans,
                            mask_data=mask_data,
                            laterality=laterality,
                        )
                        # TODO: [BIT-5567] - Ability to output bscans with masks, legend
                        self._save_scan_output(
                            scan=scan,
                            original_filename=original_filename or "",
                            bscan_idx=bscan_idx,
                            output_directory=output_directory,
                        )
                        image_output_paths.append(
                            (str(original_filename), output_directory)
                        )
                    except Exception as e:
                        logger.error(
                            f"Error processing bscan data for {original_filename}."
                        )
                        logger.error(
                            f"Error details: {e}",
                            exc_info=True,
                        )
                        continue

        if len(results_df) != len_test_data_dfs:
            # Check that the number of predictions (results_df) matched the number
            # of retrieved records (test_data_dfs) (found during iteration);
            # in the case where filenames was supplied we should _only_ be iterating
            # through that number
            raise AlgorithmError(
                "The number of predictions does not match the number "
                "of retrieved records."
            )

        # NOTE: The order of this should match the input order of the predictions
        return pd.DataFrame(
            image_output_paths,
            columns=[ORIGINAL_FILENAME_METADATA_COLUMN, "pdf_output_path"],
        )


class BscanImageAndMaskGenerationAlgorithm(
    BaseNonModelAlgorithmFactory[NoResultsModellerAlgorithm, _WorkerSide]
):
    """Algorithm that outputs images of B-scans alongside their segmentation masks."""

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "segmentation_configs": fields.List(
            fields.Nested(desert.schema_class(SegmentationConfig), required=True)
        ),
        "save_path": fields.Str(allow_none=True),
        "output_original_bscans": fields.Bool(allow_none=True),
        "image_format": marshmallow_enum.EnumField(
            ImageFormats, by_value=True, missing=ImageFormats.JPEG
        ),
        "image_optimize": fields.Bool(missing=True),
        "image_quality": fields.Int(missing=90),
        "image_subsampling": fields.Int(missing=0),
        "image_progressive": fields.Bool(missing=True),
        "image_transparency": fields.Bool(missing=False),
    }

    save_path: Path

    def __init__(
        self,
        datastructure: DataStructure,
        segmentation_configs: list[SegmentationConfig],
        save_path: Optional[Union[str, os.PathLike]] = None,
        output_original_bscans: bool = False,
        image_format: ImageFormats = ImageFormats.JPEG,
        image_optimize: bool = True,
        image_quality: int = 90,
        image_subsampling: int = 0,
        image_progressive: bool = True,
        image_transparency: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initializes the BscanImageAndMaskGenerationAlgorithm.

        Args:
            datastructure: DataStructure object describing the data.
            segmentation_configs: List of segmentation configurations.
            save_path: Optional path to save output images and masks.
            output_original_bscans: Flag to save original B-scans.
            image_format: Format for saving images, JPEG and PNG are supported.
            image_optimize: Flag to optimize images.
            image_quality: Quality of saved images.
            image_subsampling: Subsampling for saved images.
            image_progressive: Flag for progressive saving.
            image_transparency: Flag for transparency in PNG images.
            **kwargs: Additional keyword arguments for the base class.

        Note:
            'image_subsampling' and 'image_progressive' only
            apply to JPEG format and are ignored for PNG.
            'image_transparency' only applies to PNG
            format and is ignored for JPEG.
        """
        super().__init__(datastructure=datastructure, **kwargs)
        self.segmentation_configs = segmentation_configs
        self.output_original_bscans = output_original_bscans
        self.image_format = image_format
        self.image_optimize = image_optimize
        self.image_quality = image_quality
        self.image_subsampling = image_subsampling
        self.image_progressive = image_progressive
        self.image_transparency = image_transparency
        if save_path is None:
            self.save_path = config.settings.paths.output_dir
        else:
            self.save_path = Path(save_path)
        if not self.save_path:
            raise ValueError(
                "Worker save_path is not set. Please provide a valid path."
            )

    def modeller(self, **kwargs: Any) -> NoResultsModellerAlgorithm:
        """Returns the modeller-side of the algorithm.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            NoResultsModellerAlgorithm instance.
        """
        return NoResultsModellerAlgorithm(
            log_message="Running Bscan Image and Mask Generation Algorithm",
            **kwargs,
        )

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker-side of the algorithm.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            _WorkerSide instance.
        """
        return _WorkerSide(
            segmentation_configs=self.segmentation_configs,
            save_path=self.save_path,
            output_original_bscans=self.output_original_bscans,
            image_format=self.image_format,
            image_optimize=self.image_optimize,
            image_quality=self.image_quality,
            image_subsampling=self.image_subsampling,
            image_progressive=self.image_progressive,
            image_transparency=self.image_transparency,
            **kwargs,
        )
