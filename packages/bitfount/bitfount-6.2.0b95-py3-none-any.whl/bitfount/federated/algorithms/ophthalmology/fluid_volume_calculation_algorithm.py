"""Algorithm for calculating the Fluid Volume."""

from __future__ import annotations

from collections import defaultdict
import json
import math
from typing import TYPE_CHECKING, Any, ClassVar, Iterable, Optional, cast

from marshmallow import fields
import numpy as np
import pandas as pd
from scipy.ndimage import label

from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
)
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.federated.algorithms.base import (
    BaseNonModelAlgorithmFactory,
    BaseWorkerAlgorithm,
    NoResultsModellerAlgorithm,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    FLUID_VOLUME_INCLUDE_SEGMENTATION_LABELS,
    FV_SEGMENTATION_LABELS,
    FluidVolumeMetrics,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_utils import (
    get_data_for_files,
    get_dataframe_iterator_from_datasource,
    is_file_iterable_source,
    parse_mask_json,
)
from bitfount.federated.exceptions import DataProcessingError
from bitfount.federated.logging import _get_federated_logger
from bitfount.models.types import (
    MaskAltrisBiomarker,
    MaskInstance,
    MaskSegmentationModel,
)

if TYPE_CHECKING:
    from bitfount.federated.privacy.differential import DPPodConfig
    from bitfount.types import T_FIELDS_DICT


logger = _get_federated_logger("bitfount.federated")


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side of the algorithm for Fluid Volume calculation."""

    def __init__(
        self,
        fluid_volume_include_segmentations: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        self.fluid_volume_include_segmentations = (
            fluid_volume_include_segmentations
            if fluid_volume_include_segmentations
            else FLUID_VOLUME_INCLUDE_SEGMENTATION_LABELS
        )
        super().__init__(**kwargs)

    def initialise(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.initialise_data(datasource=datasource, data_splitter=data_splitter)

    def run(
        self,
        predictions: pd.DataFrame,
        filenames: Optional[list[str]] = None,
    ) -> dict[str, Optional[FluidVolumeMetrics]]:
        """Calculates the Fluid Volume metrics for each file from model predictions.

        Args:
            predictions: The predictions from model inference. If `filenames` is
                provided, these must be ordered the same as filenames.
            filenames: The list of files that the results correspond to. If not
                provided, will iterate through all files in the dataset to find
                the corresponding ones.

        Returns:
            Dictionary of original filenames to a dict of {pathology: volume_nL}.
        """
        # Fail fast if there are no predictions
        if predictions.empty:
            return {}

        # Step 1: Extract the appropriate data from the datasource by
        # combining it with the predictions supplied (i.e. joining on the identifiers).
        test_data_dfs: Iterable[pd.DataFrame]
        if filenames and is_file_iterable_source(self.datasource):
            logger.debug(f"Retrieving data for: {filenames}")
            df: pd.DataFrame = get_data_for_files(
                cast(FileSystemIterableSource, self.datasource), filenames
            )
            test_data_dfs = [df]

            # Check that we have the expected number of results for the number of files
            if len(filenames) != len(test_data_dfs[0]):
                raise DataProcessingError(
                    f"Length of results ({len(test_data_dfs[0])}"
                    f" does not match the number of files ({len(filenames)})"
                    f" while processing trial calculations."
                )
        else:
            logger.warning(
                "Iterating over all files to find prediction<->file match; "
                " this may take a long time."
            )
            test_data_dfs = get_dataframe_iterator_from_datasource(
                self.datasource, data_splitter=self.data_splitter
            )

        required_columns = [
            "Slice Thickness",
            "Pixel Spacing Column",
            "Pixel Spacing Row",
            ORIGINAL_FILENAME_METADATA_COLUMN,
        ]
        # Step 2: Concatenate the DataFrames, ensuring all required columns are present
        # If required columns are missing, they will be filled with NaN.
        combined_test_data_df = pd.concat(
            [df.reindex(columns=required_columns) for df in test_data_dfs],
            axis=0,
            ignore_index=True,
        )

        # Step 3: Check that the number of predictions matches the number
        # of metadata rows
        if len(combined_test_data_df) != len(predictions):
            raise ValueError(
                f"Number of predictions ({len(predictions)})"
                f" does not match number of test rows ({len(combined_test_data_df)})."
            )

        # Step 4: If filenames are provided, check that their count matches predictions
        if filenames:
            if len(filenames) != len(predictions):
                raise DataProcessingError(
                    f"Length of predictions ({len(predictions)}"
                    f" does not match the number of files ({len(filenames)})"
                    f" while processing trial calculations."
                )

        output: dict[str, Optional[FluidVolumeMetrics]] = {}

        # Step 5: Predictions may contain the keys; if so, drop them
        # (as have the keys in filenames already and _parse_bscan_predictions()
        # is expecting _only_ the predictions in the rows)
        if ORIGINAL_FILENAME_METADATA_COLUMN in predictions.columns:
            predictions = predictions.drop(
                ORIGINAL_FILENAME_METADATA_COLUMN, axis="columns"
            )

        # Step 6: Iterate over each file's metadata and predictions
        for (
            slice_thickness,
            pixel_spacing_column,
            pixel_spacing_row,
            original_filename,
        ), bscan_predictions in zip(
            combined_test_data_df.itertuples(index=False),
            predictions.itertuples(index=False),
        ):
            logger.debug(f"Calculating Fluid Volume metrics for {original_filename}")

            # Step 6a: Skip files with missing required values
            if (
                pd.isna(slice_thickness)
                or pd.isna(pixel_spacing_column)
                or pd.isna(pixel_spacing_row)
                or pd.isna(original_filename)
            ):
                logger.warning(
                    f"Skipping {original_filename} due to missing required values:"
                    f" {slice_thickness=},"
                    f" {pixel_spacing_column=},"
                    f" {pixel_spacing_row=}."
                )
                output[original_filename] = None
                continue

            try:
                # Step 6b: Parse model predictions into fluid masks for each pathology
                # and extract CNV probabilities
                fluid_masks, cnv_probabilities = (
                    self._parse_bscan_fluid_predictions_with_cnv(bscan_predictions)
                )
                # Step 6c: Calculate the volume of a single voxel (in mm^3)
                voxel_volume = (
                    float(slice_thickness)
                    * float(pixel_spacing_column)
                    * float(pixel_spacing_row)
                )
                # Convert voxel_volume to nL (1 mm^3 = 1000 nL)
                voxel_volume_nl = voxel_volume * 1000.0
                # Step 6d: Combine all included fluid masks into a single binary mask
                all_fluid_mask = None
                segmentation_volumes = {}
                mask_shape = None
                for pathology, mask_stack in fluid_masks.items():
                    num_voxels = np.sum(mask_stack)
                    segmentation_volumes[pathology] = self._convert_nan_to_zero(
                        float(num_voxels) * voxel_volume_nl
                    )
                    mask_bin = (mask_stack > 0).astype(np.uint8)
                    if mask_shape is None:
                        mask_shape = mask_bin.shape
                        all_fluid_mask = np.zeros(mask_shape, dtype=np.uint8)
                    all_fluid_mask = np.logical_or(all_fluid_mask, mask_bin).astype(
                        np.uint8
                    )
                all_fluid_mask = (
                    (all_fluid_mask > 0).astype(np.uint8)
                    if all_fluid_mask is not None
                    else None
                )
                # Step 6e: Skip if no mask was created
                if all_fluid_mask is None:
                    logger.info(
                        f"No fluid mask created for {original_filename}. "
                        "No fluid metrics will be recorded."
                    )
                    output[original_filename] = None
                    continue
                # Step 6f: Calculate total fluid volume
                total_fluid_volume = self._convert_nan_to_zero(
                    float(np.sum(all_fluid_mask)) * voxel_volume_nl
                )
                # Step 6g: Skip if no fluid was detected
                if total_fluid_volume == 0.0:
                    logger.info(
                        f"No fluid volume detected in {original_filename}. "
                        "No fluid metrics will be recorded."
                    )
                    output[original_filename] = None
                    continue
                # Step 6h: Calculate number of B-scans with fluid
                num_bscans_with_fluid = int(np.sum(np.any(all_fluid_mask, axis=(1, 2))))
                # Step 6i: Find connected fluid lesions and calculate their volumes
                collapsed_mask = np.any(all_fluid_mask, axis=1).astype(np.uint8)
                labeled_array, num_lesions = label(collapsed_mask)
                lesion_volumes = self._get_lesion_volumes(
                    labeled_array, num_lesions, voxel_volume_nl
                )
                # Step 6j: Find smallest and largest lesion volumes
                smallest_lesion_volume = self._convert_nan_to_zero(
                    float(min(lesion_volumes, default=np.nan))
                )
                largest_lesion_volume = self._convert_nan_to_zero(
                    float(max(lesion_volumes, default=np.nan))
                )
                # Step 6k: Calculate distance from image centre to nearest lesion
                distance_from_image_centre = (
                    self._get_shortest_distance_from_image_centre(
                        all_fluid_mask,
                        (1, float(slice_thickness), float(pixel_spacing_column)),
                    )
                )
                distance_from_image_centre = self._convert_nan_to_zero(
                    distance_from_image_centre
                )
                # Step 6l: Find the B-scan with the largest fluid volume
                max_fluid_volume_bscan_index = self._get_max_bscan_index(
                    all_fluid_mask, total_fluid_volume
                )
                # Step 6m: Calculate max CNV probability
                max_cnv_probability = (
                    float(np.round(np.max(cnv_probabilities), decimals=3))
                    if cnv_probabilities
                    else 0.0
                )
                # Step 6n: Package all metrics into FluidVolumeMetrics dataclass
                metrics = FluidVolumeMetrics(
                    total_fluid_volume=total_fluid_volume,
                    smallest_lesion_volume=smallest_lesion_volume,
                    largest_lesion_volume=largest_lesion_volume,
                    num_bscans_with_fluid=num_bscans_with_fluid,
                    num_fluid_lesions=int(num_lesions),
                    distance_from_image_centre=distance_from_image_centre,
                    max_cnv_probability=max_cnv_probability,
                    max_fluid_volume_bscan_index=max_fluid_volume_bscan_index,
                    segmentation_volumes=segmentation_volumes,
                )
                output[original_filename] = metrics
            except Exception as e:
                # Step 7: On error, log and skip this file
                logger.error(
                    f"Error calculating Fluid Volume metrics for {original_filename}."
                    " Skipping"
                )
                logger.error(e, exc_info=True)
                output[original_filename] = None
                continue
        # Step 8: Return the results for all files
        return output

    def _get_max_bscan_index(
        self, mask: np.ndarray, total_volume: float
    ) -> Optional[int]:
        """Returns the index of the B-scan with the largest fluid volume.

        The fluid volume is calculated for each B-scan individually (by summing
        over rows and columns for each B-scan), and the index of the B-scan with the
        largest value is returned. If no fluid is present, returns None.

        Args:
            mask: The binary mask of the fluid volume across B-scans
                (shape: num_bscans, num_rows, num_cols).
            total_volume: The total fluid volume across all B-scans
                (used to check if any fluid is present).

        Returns:
            The index of the B-scan with the largest fluid volume if present,
            otherwise None.
        """
        if total_volume > 0:
            bscan_sums = np.sum(np.sum(mask, axis=2), axis=1)
            return int(np.argmax(bscan_sums))
        return None

    def _convert_nan_to_zero(self, value: Any) -> float:
        """Converts NaN values to 0. Logs and re-raises for non-numeric input."""
        try:
            float_value = float(value)
        except (TypeError, ValueError) as e:
            logger.error(f"Cannot convert {value!r} to float: {e}")
            raise
        return float_value if not math.isnan(float_value) else 0.0

    def _parse_bscan_fluid_predictions_with_cnv(
        self,
        bscan_prediction_strs: tuple[str],
    ) -> tuple[dict[str, np.ndarray], list[float]]:
        """Converts the predictions for a tuple of B-scans to a dictionary.

        Extracts CNV probabilities and fluid masks for each pathology.
        The dictionary includes stacked binary masks for each fluid pathology.

        NOTE: The bscan predictions are parsed from JSON one by one rather than all
              at once to avoid memory issues.

        Args:
            bscan_prediction_strs: Tuple of predictions for a single B-scan.

        Returns:
            A tuple containing:
                - A dictionary where keys are pathology names and values are
                  numpy arrays of shape (num_bscans, num_rows, num_cols) containing
                  binary masks for each pathology.
                - A list of CNV probabilities for each B-scan.
        """
        # Initialize the masks and probabilities
        pathology_masks: dict[str, list[np.ndarray]] = defaultdict(list)
        class_probabilities: dict[str, list[float]] = defaultdict(list)
        cnv_probabilities: list[float] = []
        # Iterate over the predictions for each B-scan and aggregate over the class
        # and row dimensions to get a single columnar mask for each B-scan
        for bscan_prediction_str in bscan_prediction_strs:
            if bscan_prediction_str is not pd.NA and bscan_prediction_str is not np.nan:
                # Ensure that the bscan prediction is in the right form for
                # `json.loads()`
                bscan_prediction_str = str(bscan_prediction_str)
                bscan_prediction_str = bscan_prediction_str.replace("'", '"')

                # Load model output JSON
                loaded_json = json.loads(bscan_prediction_str)
                if not isinstance(loaded_json, list) or not loaded_json:
                    continue  # Skip if not a list or empty
                prediction_output_json = loaded_json[0]

                # Extract CNV probability if present
                cnv_probabilities.append(
                    prediction_output_json.get("cnv_probability", 0.0)
                )

                # Extract biomarker segmentation probabilities
                prediction_output_json_mask: (
                    MaskAltrisBiomarker | MaskSegmentationModel
                ) = prediction_output_json["mask"]
                prediction_output_json_instances: list[MaskInstance] = (
                    prediction_output_json_mask["instances"]
                )
                for instance_details in prediction_output_json_instances:
                    class_name = instance_details["className"]
                    probability = instance_details["probability"]
                    class_probabilities[class_name].append(probability)

                # mask shape: (num_classes, num_rows, num_cols)
                mask = parse_mask_json(
                    prediction_output_json_mask, FV_SEGMENTATION_LABELS
                )

                # For each included segmentation, stack the mask for this B-scan
                for pathology in self.fluid_volume_include_segmentations:
                    idx = FV_SEGMENTATION_LABELS.get(pathology)
                    if idx is not None:
                        pathology_mask = mask[idx]  # shape: (num_rows, num_cols)
                        # Ensure binary mask
                        pathology_masks[pathology].append(
                            (pathology_mask > 0).astype(np.uint8)
                        )
        # Stack masks along the first axis (B-scan axis)
        result_masks: dict[str, np.ndarray] = {}
        for pathology in self.fluid_volume_include_segmentations:
            if pathology_masks[pathology]:
                result_masks[pathology] = np.stack(pathology_masks[pathology], axis=0)
            else:
                # Return a zero array with shape (0, 0, 0) and dtype uint8
                result_masks[pathology] = np.zeros((0, 0, 0), dtype=np.uint8)
        return result_masks, cnv_probabilities

    @staticmethod
    def _get_lesion_volumes(
        labeled_array: np.ndarray,
        num_lesions: int,
        voxel_volume: float,
    ) -> list[float]:
        """Calculates the volume of each lesion in the image in nL.

        Args:
            labeled_array: Numpy array of shape (num_bscans, num_rows, num_cols)
                where each voxel is labelled with the lesion number it belongs to.
            num_lesions: Number of lesions in the image.
            voxel_volume: Volume of a single voxel in nL.

        Returns:
            List of lesion volumes in nL.
        """
        lesion_volumes: list[float] = []
        for i in range(1, num_lesions + 1):
            num_voxels = np.sum(labeled_array == i)
            lesion_volumes.append(num_voxels * voxel_volume)
        return lesion_volumes

    @staticmethod
    def _get_shortest_distance_from_image_centre(
        mask: np.ndarray,
        voxel_sizes: tuple[float, float, float],
    ) -> float:
        """Calculates the distance from the image centre to the nearest lesion voxel.

        Image centre is used as a proxy for the fovea.

        Args:
            mask: Numpy array mask of shape (num_bscans, num_rows, num_cols) where
                each voxel is 1 if part of a lesion, 0 otherwise.
            voxel_sizes: Tuple of voxel sizes (slice_thickness, pixel_spacing_column,
                pixel_spacing_row) in mm.

        Returns:
            Distance from the image centre to the nearest lesion voxel in mm.
        """
        image_centre_coordinates = np.subtract(mask.shape, 1) / 2
        lesion_coords = np.argwhere(mask)
        if lesion_coords.size > 0:
            # Calculate the distance from the image centre to each lesion voxel
            distances = np.absolute(lesion_coords - image_centre_coordinates)
            # Convert coordinates to mm
            distances = distances * np.array(voxel_sizes)
            # Take the minimum distance using Pythagoras' theorem
            return float(np.min(np.linalg.norm(distances, axis=1)))
        return float("nan")


class FluidVolumeCalculationAlgorithm(
    BaseNonModelAlgorithmFactory[NoResultsModellerAlgorithm, _WorkerSide]
):
    """Algorithm for calculating the Fluid Volume and associated metrics.

    Args:
        datastructure: The data structure to use for the algorithm.
        fluid_volume_include_segmentations: List of segmentation labels to be used for
            calculating the Fluid Volume. The logical AND of the masks for these labels
            will be used to calculate the Fluid Volume. If not provided, the default
            inclusion labels for the Fluid Volume will be used.

    Raises:
        ValueError: If an invalid segmentation label is provided.
        ValueError: If a segmentation label is provided in both the include and exclude
            lists.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "fluid_volume_include_segmentations": fields.List(
            fields.Str(), allow_none=True
        ),
    }

    def __init__(
        self,
        datastructure: DataStructure,
        fluid_volume_include_segmentations: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        segmentations: list[str] = []
        if fluid_volume_include_segmentations:
            segmentations.extend(fluid_volume_include_segmentations)

        if not all(label in FV_SEGMENTATION_LABELS for label in segmentations):
            raise ValueError(
                "Invalid segmentation label provided. Labels must be one of "
                f"{FV_SEGMENTATION_LABELS.keys()}"
            )

        self.fluid_volume_include_segmentations = fluid_volume_include_segmentations
        super().__init__(datastructure=datastructure, **kwargs)

    def modeller(self, **kwargs: Any) -> NoResultsModellerAlgorithm:
        """Modeller-side of the algorithm."""
        return NoResultsModellerAlgorithm(
            log_message="Running Fluid Volume Calculation Algorithm",
            **kwargs,
        )

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Worker-side of the algorithm."""
        return _WorkerSide(
            fluid_volume_include_segmentations=self.fluid_volume_include_segmentations,
            **kwargs,
        )
