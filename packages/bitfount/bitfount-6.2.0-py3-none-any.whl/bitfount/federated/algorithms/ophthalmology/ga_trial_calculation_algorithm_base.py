"""Algorithm for calculating the GA area."""

from __future__ import annotations

from bisect import bisect_left
from collections import defaultdict
import json
import math
from typing import TYPE_CHECKING, Any, ClassVar, ItemsView, Iterable, Optional, cast

from marshmallow import fields
import numpy as np
from numpy.typing import NDArray
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
    FOVEA_CENTRE_LANDMARK_INDEX,
    GA_EXCLUDE_SEGMENTATION_LABELS,
    GA_INCLUDE_SEGMENTATION_LABELS,
    GA_SEGMENTATION_LABELS,
    GAMetrics,
    GAMetricsWithFovea,
    ParsedBScanPredictions,
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
    AltrisBiomarkerEntry,
    AltrisBiomarkerOutput,
    AltrisGASegmentationModelEntry,
    AltrisGASegmentationModelPostV11Output,
    AltrisGASegmentationModelPreV11Output,
    ClassesAltrisBiomarker,
    FoveaLandmarks,
    MaskAltrisBiomarker,
    MaskInstance,
    MaskSegmentationModel,
)

if TYPE_CHECKING:
    from bitfount.federated.privacy.differential import DPPodConfig
    from bitfount.types import T_FIELDS_DICT


logger = _get_federated_logger("bitfount.federated")


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side of the algorithm."""

    def __init__(
        self,
        ga_area_include_segmentations: Optional[list[str]] = None,
        ga_area_exclude_segmentations: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        self.ga_area_include_segmentations = (
            ga_area_include_segmentations
            if ga_area_include_segmentations
            else GA_INCLUDE_SEGMENTATION_LABELS
        )
        self.ga_area_exclude_segmentations = (
            ga_area_exclude_segmentations
            if ga_area_exclude_segmentations
            else GA_EXCLUDE_SEGMENTATION_LABELS
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
        """Sets Datasource."""
        self.initialise_data(datasource=datasource, data_splitter=data_splitter)

    def run(
        self,
        predictions: pd.DataFrame,
        filenames: Optional[list[str]] = None,
    ) -> dict[str, Optional[GAMetrics]]:
        """Calculates the GA area and associated metrics from the model predictions.

        Args:
            predictions: The predictions from model inference. If `filenames` is
                provided, these must be ordered the same as filenames.
            filenames: The list of files that the results correspond to. If not
                provided, will iterate through all files in the dataset to find
                the corresponding ones.

        Returns:
            Dictionary of original filenames to GAMetrics.
        """
        # Fail fast if there are no predictions
        if predictions.empty:
            return {}

        # First, we need to extract the appropriate data from the datasource by
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
                "Iterating over all files to find prediction<->file match;"
                " this may take a long time."
            )
            test_data_dfs = get_dataframe_iterator_from_datasource(
                self.datasource, data_splitter=self.data_splitter
            )

        required_columns = [
            "Slice Thickness",
            "Pixel Spacing Column",
            ORIGINAL_FILENAME_METADATA_COLUMN,
        ]
        # Concatenate the DataFrames, ensuring all required columns are present
        # If required columns are missing, they will be filled with NaN.
        combined_test_data_df = pd.concat(
            [df.reindex(columns=required_columns) for df in test_data_dfs],
            axis=0,
            ignore_index=True,
        )

        if len(combined_test_data_df) != len(predictions):
            raise ValueError(
                f"Number of predictions ({len(predictions)})"
                f" does not match number of test rows ({len(combined_test_data_df)})."
            )

        # Check that we have the expected number of results for the number of files
        if filenames:
            if len(filenames) != len(predictions):
                raise DataProcessingError(
                    f"Length of predictions ({len(predictions)}"
                    f" does not match the number of files ({len(filenames)})"
                    f" while processing trial calculations."
                )

        output: dict[str, Optional[GAMetrics]] = {}

        # Predictions may contain the keys; if so, drop them (as have the keys in
        # filenames already and _parse_bscan_predictions() is expecting _only_ the
        # predictions in the rows)
        if ORIGINAL_FILENAME_METADATA_COLUMN in predictions.columns:
            predictions = predictions.drop(
                ORIGINAL_FILENAME_METADATA_COLUMN, axis="columns"
            )

        # Iterate over the rows of the combined dataframe and the predictions
        for (
            slice_thickness,
            pixel_spacing_column,
            original_filename,
        ), bscan_predictions in zip(
            combined_test_data_df.itertuples(index=False),
            predictions.itertuples(index=False),
        ):
            logger.debug(f"Calculating GA metrics for {original_filename}")

            # Check if any of the required values are NaN
            if (
                pd.isna(slice_thickness)
                or pd.isna(pixel_spacing_column)
                or pd.isna(original_filename)
            ):
                logger.warning(
                    f"Skipping {original_filename} due to missing required values:"
                    f" {slice_thickness=}, {pixel_spacing_column=}."
                )
                output[original_filename] = None
                continue

            try:
                # Convert the predictions to a numpy array mask
                parsed_bscan_predictions = self._parse_bscan_predictions(
                    bscan_predictions, slice_thickness, pixel_spacing_column
                )
                column_masks_arr = parsed_bscan_predictions.column_masks
                cnv_probabilities = parsed_bscan_predictions.class_probabilities["cnv"]
                class_areas_by_bscan = parsed_bscan_predictions.class_areas

                # Calculate the GA area and number of B-scans with GA
                total_ga_area = (
                    np.sum(column_masks_arr) * slice_thickness * pixel_spacing_column
                )
                num_bscans_with_ga = np.sum(np.any(column_masks_arr, axis=1))

                # Compute the separate lesions in the columnar mask
                labeled_array, num_lesions = label(column_masks_arr)

                # Get the sizes of the separate lesions in mm^2
                lesion_sizes = self._get_lesion_sizes(
                    num_lesions=num_lesions,
                    labeled_array=labeled_array,
                    slice_thickness=slice_thickness,
                    pixel_spacing_column=pixel_spacing_column,
                )

                # Calculate the distance from the image centre to the nearest lesion
                distance_from_image_centre = (
                    self._get_shortest_distance_from_image_centre(
                        column_masks_arr=column_masks_arr,
                        labeled_array=labeled_array,
                        num_lesions=num_lesions,
                        slice_thickness=slice_thickness,
                        pixel_spacing_column=pixel_spacing_column,
                    )
                )
            except Exception as e:
                logger.error(
                    f"Error calculating GA metrics for {original_filename}. Skipping"
                )
                logger.debug(e, exc_info=True)
                output[original_filename] = None
                continue

            # Add the metrics to the output
            total_ga_area = self._convert_nan_to_zero(total_ga_area)
            metrics = GAMetrics(
                total_ga_area=total_ga_area,
                num_bscans_with_ga=int(num_bscans_with_ga),
                num_ga_lesions=int(num_lesions),
                smallest_lesion_size=float(min(lesion_sizes, default=np.nan)),
                largest_lesion_size=float(max(lesion_sizes, default=np.nan)),
                distance_from_image_centre=distance_from_image_centre,
                max_cnv_probability=float(
                    np.round(np.max(cnv_probabilities), decimals=3),
                ),
                max_ga_bscan_index=self._get_max_ga_bscan_index(
                    column_masks_arr, total_ga_area
                ),
                segmentation_areas={
                    k: np.round(np.sum(v), decimals=2)
                    for k, v in class_areas_by_bscan.items()
                },
                max_pathology_probabilities={
                    k: float(
                        np.round(np.max(v), decimals=3),
                    )
                    for k, v in parsed_bscan_predictions.class_probabilities.items()
                },
            )
            output[original_filename] = metrics

        # NOTE: The insertion-order (and hence iteration order) of this dict should
        # match the input order of the predictions (true for Python 3.7+)
        return output

    def _get_max_ga_bscan_index(
        self, column_masks_arr: np.ndarray, ga_area: float
    ) -> Optional[int]:
        """Returns the index of the B-scan with the largest GA area.

        Args:
            column_masks_arr: Numpy array mask of shape (num_bscans, num_cols) where
                num_bscans is the number of B-scans in the tuple and num_cols is the
                number of columns in each B-scan.
            ga_area: Total GA area in mm^2.

        Returns:
            Index of the B-scan with the largest GA area if there is GA in the image,
            otherwise None.
        """
        if ga_area:
            return int(np.argmax(np.sum(column_masks_arr, axis=1)))

        return None

    def _convert_nan_to_zero(self, value: Any) -> float:
        """Converts NaN values to 0."""
        return float(value) if not math.isnan(value) else 0.0

    def _parse_bscan_predictions(
        self,
        bscan_prediction_strs: tuple[str],
        slice_thickness: float,
        pixel_spacing_column: float,
    ) -> ParsedBScanPredictions:
        """Converts the predictions for a tuple of bscans to a tuple of numpy arrays.

        NOTE: The bscan predictions are parsed from JSON one by one rather than all
              at once to avoid memory issues.

        Args:
            bscan_prediction_strs: Tuple of predictions for a single B-scan.
            slice_thickness: Thickness of each B-scan in mm.
            pixel_spacing_column: Spacing between columns in mm.

        Returns:
            A ParsedBScanPredictions instance containing, for each B-Scan, columnar
            masks for GA, probabilities for various pathologies, and areas for
            various pathologies.
        """
        column_masks: list[np.ndarray] = []
        cnv_probabilities: list[float] = []
        class_probabilities: dict[str, list[float]] = defaultdict(list)
        class_areas_by_bscan: dict[str, list[float]] = {
            class_name: [] for class_name in GA_SEGMENTATION_LABELS
        }

        # Iterate over the predictions for each B-scan and aggregate over the class
        # and row dimensions to get a single columnar mask for each B-scan
        for bscan_prediction_str in bscan_prediction_strs:
            if bscan_prediction_str is not pd.NA and bscan_prediction_str is not np.nan:
                # Ensure that the bscan prediction is in the right form for
                # `json.loads()`
                bscan_prediction_str = str(bscan_prediction_str)
                bscan_prediction_str = bscan_prediction_str.replace("'", '"')

                # Load model output JSON
                prediction_output_json: (
                    AltrisBiomarkerEntry | AltrisGASegmentationModelEntry
                )
                try:
                    # Older AltrisGASegmentationModel versions return a list of lists
                    loaded_json_pre_v11: AltrisGASegmentationModelPreV11Output = (
                        json.loads(bscan_prediction_str)
                    )
                    prediction_output_json = loaded_json_pre_v11[0][0]
                except KeyError:
                    # From AltrisGASegmentationModel version 11 onwards and in the
                    # AltrisConfigurablePathologyModel, the output is list with a
                    # dictionary
                    loaded_json: (
                        AltrisBiomarkerOutput | AltrisGASegmentationModelPostV11Output
                    ) = json.loads(bscan_prediction_str)
                    prediction_output_json = loaded_json[0]

                # Extract CNV probability
                cnv_probabilities.append(
                    prediction_output_json.get("cnv_probability", 0.0)
                )

                # Extract other classification probabilities
                classification_probs: Optional[ClassesAltrisBiomarker] = cast(
                    # https://github.com/python/mypy/issues/7981
                    Optional[ClassesAltrisBiomarker],
                    prediction_output_json.get("classes", None),
                )
                if classification_probs is not None:
                    for class_name, probability in cast(
                        # https://github.com/python/mypy/issues/7981
                        ItemsView[str, float],
                        classification_probs.items(),
                    ):
                        # CNV is handled separately, so skip over
                        if class_name in ("cnv", "choroidal_neovascularization"):
                            continue
                        class_probabilities[class_name].append(probability)

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

                # Mask of shape (num_classes, num_rows, num_cols)
                mask = parse_mask_json(
                    prediction_output_json_mask, GA_SEGMENTATION_LABELS
                )

                # Sum over the rows to get a 2D array of shape (num_classes, num_cols)
                mask = np.any(mask, axis=1) * 1

                # Iterate over the classes and save areas purely for logging purposes
                for class_name, mask_ in zip(GA_SEGMENTATION_LABELS.keys(), mask):
                    class_areas_by_bscan[class_name].append(
                        # Calculate area in mm^2 from columnar mask
                        np.sum(mask_) * slice_thickness * pixel_spacing_column
                    )

                # Keep only the inclusion and exclusion segmentations
                inclusion_indices = [
                    i
                    for name, i in GA_SEGMENTATION_LABELS.items()
                    if name in self.ga_area_include_segmentations
                ]
                exclusion_indices = [
                    i
                    for name, i in GA_SEGMENTATION_LABELS.items()
                    if name in self.ga_area_exclude_segmentations
                ]

                # Create inclusion mask
                inclusion_mask = (
                    np.all(np.take(mask, inclusion_indices, axis=0), axis=0) * 1
                )

                # Create exclusion mask
                exclusion_mask = np.any(
                    np.take(mask, exclusion_indices, axis=0), axis=0
                )

                # Combine inclusion and exclusion masks
                mask = np.where(exclusion_mask, 0, inclusion_mask)
                column_masks.append(mask)

        # Sum the areas over all the bscans for each class and log them for debugging
        for class_name, areas_by_bscan in class_areas_by_bscan.items():
            total_area_across_bscans = np.round(np.sum(areas_by_bscan), decimals=2)
            logger.debug(f"Area of {class_name}: {total_area_across_bscans} mm^2")

        # Combine CNV and class_probabilities, convert to np arrays for probabilities
        class_probabilities["cnv"] = cnv_probabilities
        # remove "choroidal_neovascularization" if it has somehow snuck in
        class_probabilities.pop("choroidal_neovascularization", None)
        class_probabilities_array: dict[str, NDArray[np.floating]] = {
            k: np.asarray(v) for k, v in class_probabilities.items()
        }

        return ParsedBScanPredictions(
            column_masks=np.asarray(column_masks),
            class_probabilities=class_probabilities_array,
            class_areas=class_areas_by_bscan,
        )

    @staticmethod
    def _get_lesion_sizes(
        num_lesions: int,
        labeled_array: np.ndarray,
        slice_thickness: float,
        pixel_spacing_column: float,
    ) -> list[float]:
        """Calculates the size of each lesion in the image in mm^2.

        Args:
            num_lesions: Number of lesions in the image.
            labeled_array: Numpy array of shape (num_bscans, num_cols) where each
                pixel is labelled with the lesion number it belongs to.
            slice_thickness: Thickness of each B-scan in mm.
            pixel_spacing_column: Spacing between columns in mm.

        Returns:
            List of lesion sizes in mm^2.
        """
        lesion_sizes: list[float] = []
        for i in range(1, num_lesions + 1):
            num_pixels = np.sum(labeled_array == i)
            lesion_sizes.append(num_pixels * slice_thickness * pixel_spacing_column)

        return lesion_sizes

    @staticmethod
    def _get_shortest_distance_from_image_centre(
        column_masks_arr: np.ndarray,
        labeled_array: np.ndarray,
        num_lesions: int,
        slice_thickness: float,
        pixel_spacing_column: float,
    ) -> float:
        """Calculates the distance from the image centre to the nearest lesion.

        Image centre is used as a proxy for the fovea.

        Args:
            column_masks_arr: Numpy array mask of shape (num_bscans, num_cols) where
                num_bscans is the number of B-scans in the tuple and num_cols is the
                number of columns in each B-scan.
            labeled_array: Numpy array of shape (num_bscans, num_cols) where each
                pixel is labelled with the lesion number it belongs to.
            num_lesions: Number of lesions in the image.
            slice_thickness: Thickness of each B-scan in mm.
            pixel_spacing_column: Spacing between columns in mm.

        Returns:
            Distance from the image centre to the nearest lesion in mm.
        """
        image_centre_coordinates: np.ndarray = (
            np.subtract(column_masks_arr.shape, 1) / 2
        )
        # Distance from the image centre to each lesion in mm
        distances_mm: list[float] = []
        for i in range(1, num_lesions + 1):
            lesion_mask = labeled_array == i
            # Get the coordinates of the lesion pixels
            coordinates = np.argwhere(lesion_mask)
            # Calculate the distance from the image centre to the lesion
            distances = np.absolute(coordinates - image_centre_coordinates)
            # Convert coordinates to mm. The slice thickness is used for
            # the distance between rows. The pixel spacing is used for
            # the distance between columns.
            distances = distances * np.array([slice_thickness, pixel_spacing_column])
            # Take the minimum distance from the image centre to the lesion using
            # Pythagoras' theorem
            distances_mm.append(np.min(np.linalg.norm(distances, axis=1)))

        return float(min(distances_mm, default=np.nan))


class GATrialCalculationAlgorithmBase(
    BaseNonModelAlgorithmFactory[NoResultsModellerAlgorithm, _WorkerSide]
):
    """Algorithm for calculating the GA Area and associated metrics.

    Args:
        datastructure: The data structure to use for the algorithm.
        ga_area_include_segmentations: List of segmentation labels to be used for
            calculating the GA area. The logical AND of the masks for these labels will
            be used to calculate the GA area. If not provided, the default inclusion
            labels for the GA area will be used.
        ga_area_exclude_segmentations: List of segmentation labels to be excluded from
            calculating the GA area. If any of these segmentations are present in the
            axial segmentation masks, that axis will be excluded from the GA area
            calculation. If not provided, the default exclusion labels for the GA area
            will be used.

    Raises:
        ValueError: If an invalid segmentation label is provided.
        ValueError: If a segmentation label is provided in both the include and exclude
            lists.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "ga_area_include_segmentations": fields.List(fields.Str(), allow_none=True),
        "ga_area_exclude_segmentations": fields.List(fields.Str(), allow_none=True),
    }

    def __init__(
        self,
        datastructure: DataStructure,
        ga_area_include_segmentations: Optional[list[str]] = None,
        ga_area_exclude_segmentations: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        segmentations: list[str] = []
        if ga_area_include_segmentations:
            segmentations.extend(ga_area_include_segmentations)

        if ga_area_exclude_segmentations:
            segmentations.extend(ga_area_exclude_segmentations)

        if not all(label in GA_SEGMENTATION_LABELS for label in segmentations):
            raise ValueError(
                "Invalid segmentation label provided. Labels must be one of "
                f"{GA_SEGMENTATION_LABELS.keys()}"
            )

        if len(segmentations) != len(set(segmentations)):
            raise ValueError(
                "Segmentation label provided in both include and exclude lists"
            )

        self.ga_area_include_segmentations = ga_area_include_segmentations
        self.ga_area_exclude_segmentations = ga_area_exclude_segmentations
        super().__init__(datastructure=datastructure, **kwargs)

    def modeller(self, **kwargs: Any) -> NoResultsModellerAlgorithm:
        """Modeller-side of the algorithm."""
        return NoResultsModellerAlgorithm(
            log_message="Running GA Trial Calculation Algorithm",
            **kwargs,
        )

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Worker-side of the algorithm."""
        return _WorkerSide(
            ga_area_include_segmentations=self.ga_area_include_segmentations,
            ga_area_exclude_segmentations=self.ga_area_exclude_segmentations,
            **kwargs,
        )


class _BaseWorkerSideWithFovea(BaseWorkerAlgorithm):
    """Worker side of the algorithm."""

    def __init__(
        self,
        ga_area_include_segmentations: Optional[list[str]] = None,
        ga_area_exclude_segmentations: Optional[list[str]] = None,
        fovea_landmark_idx: int = 1,
        **kwargs: Any,
    ) -> None:
        self.ga_area_include_segmentations = (
            ga_area_include_segmentations
            if ga_area_include_segmentations
            else GA_INCLUDE_SEGMENTATION_LABELS
        )
        self.ga_area_exclude_segmentations = (
            ga_area_exclude_segmentations
            if ga_area_exclude_segmentations
            else GA_EXCLUDE_SEGMENTATION_LABELS
        )
        self.fovea_landmark_idx = fovea_landmark_idx

        super().__init__(**kwargs)

    def initialise(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Sets Datasource."""
        self.initialise_data(datasource=datasource, data_splitter=data_splitter)

    def run(
        self,
        predictions: pd.DataFrame,
        fovea_predictions: pd.DataFrame,
        filenames: Optional[list[str]] = None,
    ) -> dict[str, Optional[GAMetricsWithFovea]]:
        """Calculates the GA area and associated metrics from the model predictions.

        Args:
            predictions: The predictions from model inference. If `filenames` is
                provided, these must be ordered the same as filenames.
            fovea_predictions: The predictions from fovea model inference.
                If `filenames` is provided, these must be ordered the same as filenames.
            filenames: The list of files that the results correspond to. If not
                provided, will iterate through all files in the dataset to find
                the corresponding ones.

        Returns:
            Dictionary of original filenames to GAMetricsWithFovea.
        """
        # First, we need to extract the appropriate data from the datasource by
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
                    f"Length of results ({test_data_dfs[0]}"
                    f" does not match the number of files ({len(filenames)})"
                    f" while processing trial calculations with Fovea."
                )

        else:
            logger.warning(
                "Iterating over all files to find prediction<->file match;"
                " this may take a long time."
            )
            test_data_dfs = get_dataframe_iterator_from_datasource(
                self.datasource, data_splitter=self.data_splitter
            )

        required_columns = [
            "Slice Thickness",
            "Pixel Spacing Column",
            ORIGINAL_FILENAME_METADATA_COLUMN,
        ]
        # Concatenate the DataFrames, ensuring all required columns are present
        # If required columns are missing, they will be filled with NaN.
        combined_test_data_df = pd.concat(
            [df.reindex(columns=required_columns) for df in test_data_dfs],
            axis=0,
            ignore_index=True,
        )

        if len(combined_test_data_df) != len(predictions):
            raise ValueError(
                f"Number of predictions ({len(predictions)})"
                f" does not match number of test rows ({len(combined_test_data_df)})."
            )

        # Merge the fovea predictions to the combined test data dataframe on the
        # _original_filename column
        if ORIGINAL_FILENAME_METADATA_COLUMN in fovea_predictions.columns:
            merged_data_df = combined_test_data_df.merge(
                fovea_predictions,
                on=ORIGINAL_FILENAME_METADATA_COLUMN,
                how="left",
                suffixes=("", "_fovea"),
            )
        else:
            # Unable to perform merge, unable to proceed
            logger.error(
                f"`fovea_predictions` dataframe did not contain expected filename"
                f' column, "{ORIGINAL_FILENAME_METADATA_COLUMN}".'
                f" Unable to proceed with GA calculations."
                f" Empty dict will be returned for this batch."
            )
            return {}

        # Check that we have the expected number of results for the number of files
        if filenames:
            if len(filenames) != len(predictions):
                raise DataProcessingError(
                    f"Length of predictions ({len(predictions)}"
                    f" does not match the number of files ({len(filenames)})"
                    f" while processing trial calculations with Fovea."
                )

        output: dict[str, Optional[GAMetricsWithFovea]] = {}

        # Predictions may contain the keys; if so, drop them (as have the keys in
        # filenames already and _parse_bscan_predictions() is expecting _only_ the
        # predictions in the rows)
        if ORIGINAL_FILENAME_METADATA_COLUMN in predictions.columns:
            predictions = predictions.drop(
                ORIGINAL_FILENAME_METADATA_COLUMN, axis="columns"
            )

        # Iterate over the rows of the combined dataframe and the predictions
        for (
            slice_thickness,
            pixel_spacing_column,
            original_filename,
            central_slice_fovea,
            landmarks_fovea,
        ), bscan_predictions in zip(
            merged_data_df.itertuples(index=False),
            predictions.itertuples(index=False),
        ):
            logger.debug(f"Calculating GA metrics for {original_filename}")

            # Check if any of the required values are NaN
            if (
                pd.isna(slice_thickness)
                or pd.isna(pixel_spacing_column)
                or pd.isna(original_filename)
            ):
                logger.warning(
                    f"Skipping {original_filename} due to missing required values:"
                    f" {slice_thickness=}, {pixel_spacing_column=}."
                )
                output[original_filename] = None
                continue

            try:
                # Convert the predictions to a numpy array mask
                parsed_bscan_predictions = self._parse_bscan_predictions(
                    bscan_predictions, slice_thickness, pixel_spacing_column
                )
                column_masks_arr = parsed_bscan_predictions.column_masks
                cnv_probabilities = parsed_bscan_predictions.class_probabilities["cnv"]
                class_areas_by_bscan = parsed_bscan_predictions.class_areas

                # Calculate the GA area and number of B-scans with GA
                total_ga_area = (
                    np.sum(column_masks_arr) * slice_thickness * pixel_spacing_column
                )
                num_bscans_with_ga = np.sum(np.any(column_masks_arr, axis=1))

                # Compute the separate lesions in the columnar mask
                labeled_array, num_lesions = label(column_masks_arr)

                lesion_sizes = self._get_lesion_sizes(
                    num_lesions=num_lesions,
                    labeled_array=labeled_array,
                    slice_thickness=slice_thickness,
                    pixel_spacing_column=pixel_spacing_column,
                )

                # Calculate the distance from the image centre to the nearest lesion
                distance_from_image_centre = (
                    self._get_shortest_distance_from_image_centre(
                        column_masks_arr=column_masks_arr,
                        labeled_array=labeled_array,
                        num_lesions=num_lesions,
                        slice_thickness=slice_thickness,
                        pixel_spacing_column=pixel_spacing_column,
                    )
                )

                # Get the central slice middle point from the fovea prediction
                # Format of the coordinate is (slice, x, y)
                fovea_centre_coordinates = self._get_central_slice_landmark_point(
                    central_slice_fovea,
                    landmarks_fovea,
                    landmark_idx=self.fovea_landmark_idx,
                )

                # Calculate the distance from the fovea centre
                distance_from_fovea_centre = self._get_shortest_distance_from_fovea(
                    fovea_coordinates=fovea_centre_coordinates,
                    labeled_array=labeled_array,
                    num_lesions=num_lesions,
                    slice_thickness=slice_thickness,
                    pixel_spacing_column=pixel_spacing_column,
                )

                # Get the distance metric to use for the output
                if distance_from_fovea_centre is None:
                    logger.warning(
                        "Distance from fovea centre is not available."
                        "Using distance from image centre as a fallback."
                    )
                    distance_metric = distance_from_image_centre
                    distance_metric_type = "image_centre"
                else:
                    distance_metric = distance_from_fovea_centre
                    distance_metric_type = "fovea_centre_model"
            except Exception as e:
                logger.error(
                    f"Error calculating GA metrics for {original_filename}. Skipping"
                )
                logger.debug(e, exc_info=True)
                output[original_filename] = None
                continue

            # Add the metrics to the output
            total_ga_area = self._convert_nan_to_zero(total_ga_area)
            metrics = GAMetricsWithFovea(
                total_ga_area=total_ga_area,
                num_bscans_with_ga=int(num_bscans_with_ga),
                num_ga_lesions=int(num_lesions),
                smallest_lesion_size=float(min(lesion_sizes, default=np.nan)),
                largest_lesion_size=float(max(lesion_sizes, default=np.nan)),
                distance_from_image_centre=distance_from_image_centre,
                distance_from_fovea_centre=distance_from_fovea_centre,
                est_fovea_distance=distance_metric,
                distance_metric_type=distance_metric_type,
                fovea_centre=(
                    tuple(fovea_centre_coordinates.tolist())
                    if fovea_centre_coordinates is not None
                    else None
                ),
                fovea_landmarks=(landmarks_fovea if landmarks_fovea else None),
                max_cnv_probability=float(
                    np.round(np.max(cnv_probabilities), decimals=3),
                ),
                max_ga_bscan_index=self._get_max_ga_bscan_index(
                    column_masks_arr, total_ga_area
                ),
                segmentation_areas={
                    k: np.round(np.sum(v), decimals=2)
                    for k, v in class_areas_by_bscan.items()
                },
                max_pathology_probabilities={
                    k: float(
                        np.round(np.max(v), decimals=3),
                    )
                    for k, v in parsed_bscan_predictions.class_probabilities.items()
                },
                # This gets populated later by the df extensions
                subfoveal_indicator=None,
            )
            output[original_filename] = metrics

        # NOTE: The insertion-order (and hence iteration order) of this dict should
        # match the input order of the predictions (true for Python 3.7+)
        return output

    def _get_max_ga_bscan_index(
        self, column_masks_arr: np.ndarray, ga_area: float
    ) -> Optional[int]:
        """Returns the index of the B-scan with the largest GA area.

        Args:
            column_masks_arr: Numpy array mask of shape (num_bscans, num_cols) where
                num_bscans is the number of B-scans in the tuple and num_cols is the
                number of columns in each B-scan.
            ga_area: Total GA area in mm^2.

        Returns:
            Index of the B-scan with the largest GA area if there is GA in the image,
            otherwise None.
        """
        if ga_area:
            return int(np.argmax(np.sum(column_masks_arr, axis=1)))

        return None

    def _convert_nan_to_zero(self, value: Any) -> float:
        """Converts NaN values to 0."""
        return float(value) if not math.isnan(value) else 0.0

    def _parse_bscan_predictions(
        self,
        bscan_predictions_strs: tuple[str],
        slice_thickness: float,
        pixel_spacing_column: float,
    ) -> ParsedBScanPredictions:
        """Converts the predictions for a tuple of bscans to a tuple of numpy arrays.

        NOTE: The bscan predictions are parsed from JSON one by one rather than all
              at once to avoid memory issues.

        Args:
            bscan_predictions_strs: Tuple of predictions for a single B-scan.
            slice_thickness: Thickness of each B-scan in mm.
            pixel_spacing_column: Spacing between columns in mm.

        Returns:
            A ParsedBScanPredictions instance containing, for each B-Scan, columnar
            masks for GA, probabilities for various pathologies, and areas for
            various pathologies.
        """
        column_masks: list[np.ndarray] = []
        cnv_probabilities: list[float] = []
        class_probabilities: dict[str, list[float]] = defaultdict(list)
        class_areas_by_bscan: dict[str, list[float]] = {
            class_name: [] for class_name in GA_SEGMENTATION_LABELS
        }

        # Iterate over the predictions for each B-scan and aggregate over the class
        # and row dimensions to get a single columnar mask for each B-scan
        for bscan_prediction_str in bscan_predictions_strs:
            if bscan_prediction_str is not pd.NA and bscan_prediction_str is not np.nan:
                # Ensure that the bscan prediction is in the right form for
                # `json.loads()`
                bscan_prediction_str = str(bscan_prediction_str)
                bscan_prediction_str = bscan_prediction_str.replace("'", '"')

                # Load model output JSON
                prediction_output_json: (
                    AltrisBiomarkerEntry | AltrisGASegmentationModelEntry
                )
                try:
                    # Older AltrisGASegmentationModel versions return a list of lists
                    loaded_json_pre_v11: AltrisGASegmentationModelPreV11Output = (
                        json.loads(bscan_prediction_str)
                    )
                    prediction_output_json = loaded_json_pre_v11[0][0]
                except KeyError:
                    # From AltrisGASegmentationModel version 11 onwards and in the
                    # AltrisConfigurablePathologyModel, the output is list with a
                    # dictionary
                    loaded_json: (
                        AltrisBiomarkerOutput | AltrisGASegmentationModelPostV11Output
                    ) = json.loads(bscan_prediction_str)
                    prediction_output_json = loaded_json[0]

                # Extract CNV probability
                cnv_probabilities.append(
                    prediction_output_json.get("cnv_probability", 0.0)
                )

                # Extract other classification probabilities
                classification_probs: Optional[ClassesAltrisBiomarker] = cast(
                    # https://github.com/python/mypy/issues/7981
                    Optional[ClassesAltrisBiomarker],
                    prediction_output_json.get("classes", None),
                )
                if classification_probs is not None:
                    for class_name, probability in cast(
                        # https://github.com/python/mypy/issues/7981
                        ItemsView[str, float],
                        classification_probs.items(),
                    ):
                        # CNV is handled separately, so skip over
                        if class_name in ("cnv", "choroidal_neovascularization"):
                            continue
                        class_probabilities[class_name].append(probability)

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

                # Mask of shape (num_classes, num_rows, num_cols)
                mask = parse_mask_json(
                    prediction_output_json_mask, GA_SEGMENTATION_LABELS
                )

                # Sum over the rows to get a 2D array of shape (num_classes, num_cols)
                mask = np.any(mask, axis=1) * 1

                # Iterate over the classes and save areas purely for logging purposes
                for class_name, mask_ in zip(GA_SEGMENTATION_LABELS.keys(), mask):
                    class_areas_by_bscan[class_name].append(
                        # Calculate area in mm^2 from columnar mask
                        np.sum(mask_) * slice_thickness * pixel_spacing_column
                    )

                # Keep only the inclusion and exclusion segmentations
                inclusion_indices = [
                    i
                    for name, i in GA_SEGMENTATION_LABELS.items()
                    if name in self.ga_area_include_segmentations
                ]
                exclusion_indices = [
                    i
                    for name, i in GA_SEGMENTATION_LABELS.items()
                    if name in self.ga_area_exclude_segmentations
                ]

                # Create inclusion mask
                inclusion_mask = (
                    np.all(np.take(mask, inclusion_indices, axis=0), axis=0) * 1
                )

                # Create exclusion mask
                exclusion_mask = np.any(
                    np.take(mask, exclusion_indices, axis=0), axis=0
                )

                # Combine inclusion and exclusion masks
                mask = np.where(exclusion_mask, 0, inclusion_mask)
                column_masks.append(mask)

        # Sum the areas on the bscans for each class and log them for debugging
        for class_name, areas_by_bscan in class_areas_by_bscan.items():
            total_area_across_bscans = np.round(np.sum(areas_by_bscan), decimals=2)
            logger.debug(f"Area of {class_name}: {total_area_across_bscans} mm^2")

        # Combine CNV and class_probabilities, convert to np arrays for probabilities
        class_probabilities["cnv"] = cnv_probabilities
        # remove "choroidal_neovascularization" if it has somehow snuck in
        class_probabilities.pop("choroidal_neovascularization", None)
        class_probabilities_array: dict[str, NDArray[np.floating]] = {
            k: np.asarray(v) for k, v in class_probabilities.items()
        }

        return ParsedBScanPredictions(
            column_masks=np.asarray(column_masks),
            class_probabilities=class_probabilities_array,
            class_areas=class_areas_by_bscan,
        )

    def _get_central_slice_landmark_point(
        self,
        central_slice: Optional[int],
        landmarks_list: Optional[FoveaLandmarks],
        landmark_idx: Optional[int] = FOVEA_CENTRE_LANDMARK_INDEX,
    ) -> Optional[np.ndarray]:
        """Gets the central slice middle point from the fovea preiction.

        Args:
            central_slice: Central slice of the fovea prediction.
            landmarks_list: List of 3-element lists of landmarks (slice, x, y).
            landmark_idx: index of the middle landmark in the tuple.

        Returns:
            Numpy array of the middle point of the central slice.
        """
        # If the prediction data is missing, log a warning and return None
        if central_slice is None or pd.isna(central_slice):
            logger.warning(
                "Central slice prediction missing. Skipping distance calculation."
            )
            return None

        # If the landmarks are missing, log a warning and return None
        if landmarks_list is None or len(landmarks_list) == 0:
            logger.warning("Landmarks missing. Skipping distance calculation.")
            return None

        # If the landmark index is missing, log a warning and use the default value
        if landmark_idx is None:
            logger.warning(
                f"Landmark index missing."
                f"Using the default value of {FOVEA_CENTRE_LANDMARK_INDEX}."
            )
            landmark_idx = FOVEA_CENTRE_LANDMARK_INDEX

        # Get the index of the central slice in the landmarks
        central_slice_column_idx = bisect_left(
            landmarks_list, central_slice, key=lambda x: x[0]
        )
        # If the central slice is not found in the landmarks, log a warning and skip
        if central_slice_column_idx == len(landmarks_list):
            logger.warning(
                "Central slice not found in landmarks. Skipping distance calculation."
            )
            return None
        # If the landmark index is out of bounds, log a warning and skip
        if central_slice_column_idx + landmark_idx >= len(landmarks_list):
            logger.warning(
                "Landmark not found in central slice. Skipping distance calculation."
            )
            return None
        # Return the requested point of the central slice
        return np.asarray(landmarks_list[central_slice_column_idx + landmark_idx])

    @staticmethod
    def _get_lesion_sizes(
        num_lesions: int,
        labeled_array: np.ndarray,
        slice_thickness: float,
        pixel_spacing_column: float,
    ) -> list[float]:
        """Calculates the size of each lesion in the image in mm^2.

        Args:
            num_lesions: Number of lesions in the image.
            labeled_array: Numpy array of shape (num_bscans, num_cols) where each
                pixel is labelled with the lesion number it belongs to.
            slice_thickness: Thickness of each B-scan in mm.
            pixel_spacing_column: Spacing between columns in mm.

        Returns:
            List of lesion sizes in mm^2.
        """
        lesion_sizes: list[float] = []
        for i in range(1, num_lesions + 1):
            num_pixels = np.sum(labeled_array == i)
            lesion_sizes.append(num_pixels * slice_thickness * pixel_spacing_column)

        return lesion_sizes

    @staticmethod
    def _get_shortest_distance_from_image_centre(
        column_masks_arr: np.ndarray,
        labeled_array: np.ndarray,
        num_lesions: int,
        slice_thickness: float,
        pixel_spacing_column: float,
    ) -> float:
        """Calculates the distance from the image centre to the nearest lesion.

        Image centre is used as a proxy for the fovea.

        Args:
            column_masks_arr: Numpy array mask of shape (num_bscans, num_cols) where
                num_bscans is the number of B-scans in the tuple and num_cols is the
                number of columns in each B-scan.
            labeled_array: Numpy array of shape (num_bscans, num_cols) where each
                pixel is labelled with the lesion number it belongs to.
            num_lesions: Number of lesions in the image.
            slice_thickness: Thickness of each B-scan in mm.
            pixel_spacing_column: Spacing between columns in mm.

        Returns:
            Distance from the image centre to the nearest lesion in mm.
        """
        image_centre_coordinates: np.ndarray = (
            np.subtract(column_masks_arr.shape, 1) / 2
        )
        # Distance from the image centre to each lesion in mm
        distances_mm: list[float] = []
        for i in range(1, num_lesions + 1):
            lesion_mask = labeled_array == i
            # Get the coordinates of the lesion pixels
            coordinates = np.argwhere(lesion_mask)
            # Calculate the distance from the image centre to the lesion
            distances = np.absolute(coordinates - image_centre_coordinates)
            # Convert coordinates to mm. The slice thickness is used for
            # the distance between rows. The pixel spacing is used for
            # the distance between columns.
            distances = distances * np.array([slice_thickness, pixel_spacing_column])
            # Take the minimum distance from the image centre to the lesion using
            # Pythagoras' theorem
            distances_mm.append(np.min(np.linalg.norm(distances, axis=1)))

        return float(min(distances_mm, default=np.nan))

    @staticmethod
    def _get_shortest_distance_from_fovea(
        fovea_coordinates: Optional[np.ndarray],
        labeled_array: np.ndarray,
        num_lesions: int,
        slice_thickness: float,
        pixel_spacing_column: float,
    ) -> Optional[float]:
        """Calculates the distance from the fovea to the nearest and largest lesions.

        If fovea_coordinates is None, returns None.

        Args:
            fovea_coordinates: Numpy array of fovea coordinates in the image.
            labeled_array: Numpy array of shape (num_bscans, num_cols) where each
                pixel is labelled with the lesion number it belongs to.
            num_lesions: Number of lesions in the image.
            slice_thickness: Thickness of each B-scan in mm.
            pixel_spacing_column: Spacing between columns in mm.

        Returns:
            Distance from the fovea to the nearest lesion in mm,
            Optional distance from the fovea to the largest lesion in mm.
        """
        if fovea_coordinates is None or fovea_coordinates.size == 0:
            logger.warning("Fovea coordinates missing. Skipping distance calculation.")
            return None

        # Get the fovea centre slice and column coordinates
        fovea_centre_scan_column: np.ndarray = fovea_coordinates[:2]
        # Distance from the fovea to each lesion in mm
        distances_mm: list[float] = []
        # Filter the lesions if a filter is provided
        # If no filter is provided, go over all lesions
        for i in range(1, num_lesions + 1):
            lesion_mask = labeled_array == i
            # Get the coordinates of the lesion pixels
            coordinates = np.argwhere(lesion_mask)
            # Calculate the distance from the fovea to the lesion
            distances = np.absolute(coordinates - fovea_centre_scan_column)
            # Convert coordinates to mm. The slice thickness is used for
            # the distance between rows. The pixel spacing is used for
            # the distance between columns.
            distances = distances * np.array([slice_thickness, pixel_spacing_column])
            # Take the minimum distance from the fovea to the lesion using
            # Pythagoras' theorem
            distances_mm.append(np.min(np.linalg.norm(distances, axis=1)))

        return float(min(distances_mm, default=np.nan))


class GATrialCalculationAlgorithmWithFoveaBase(
    BaseNonModelAlgorithmFactory[NoResultsModellerAlgorithm, _BaseWorkerSideWithFovea]
):
    """Algorithm for calculating the GA Area and associated metrics.

    Args:
        ga_area_include_segmentations: List of segmentation labels to be used for
            calculating the GA area. The logical AND of the masks for these labels will
            be used to calculate the GA area. If not provided, the default inclusion
            labels for the GA area will be used.
        ga_area_exclude_segmentations: List of segmentation labels to be excluded from
            calculating the GA area. If any of these segmentations are present in the
            axial segmentation masks, that axis will be excluded from the GA area
            calculation. If not provided, the default exclusion labels for the GA area
            will be used.
        fovea_landmark_idx: index of the fovea landmark in the tuple.
            0 for fovea start, 1 for fovea middle, 2 for fovea end. Default is 1.

    Raises:
        ValueError: If an invalid segmentation label is provided.
        ValueError: If a segmentation label is provided in both the include and exclude
            lists.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "ga_area_include_segmentations": fields.List(fields.Str(), allow_none=True),
        "ga_area_exclude_segmentations": fields.List(fields.Str(), allow_none=True),
        "fovea_landmark_idx": fields.Int(allow_none=True),
    }

    def __init__(
        self,
        datastructure: DataStructure,
        ga_area_include_segmentations: Optional[list[str]] = None,
        ga_area_exclude_segmentations: Optional[list[str]] = None,
        fovea_landmark_idx: int = 1,
        **kwargs: Any,
    ) -> None:
        segmentations: list[str] = []
        if ga_area_include_segmentations:
            segmentations.extend(ga_area_include_segmentations)

        if ga_area_exclude_segmentations:
            segmentations.extend(ga_area_exclude_segmentations)

        if not all(label in GA_SEGMENTATION_LABELS for label in segmentations):
            raise ValueError(
                "Invalid segmentation label provided. Labels must be one of "
                f"{GA_SEGMENTATION_LABELS.keys()}"
            )

        if len(segmentations) != len(set(segmentations)):
            raise ValueError(
                "Segmentation label provided in both include and exclude lists"
            )

        self.ga_area_include_segmentations = ga_area_include_segmentations
        self.ga_area_exclude_segmentations = ga_area_exclude_segmentations
        self.fovea_landmark_idx = fovea_landmark_idx
        super().__init__(datastructure=datastructure, **kwargs)

    def modeller(self, **kwargs: Any) -> NoResultsModellerAlgorithm:
        """Modeller-side of the algorithm."""
        return NoResultsModellerAlgorithm(
            log_message="Running GA Trial Calculation Algorithm",
            **kwargs,
        )

    def worker(self, **kwargs: Any) -> _BaseWorkerSideWithFovea:
        """Worker-side of the algorithm."""
        return _BaseWorkerSideWithFovea(
            ga_area_include_segmentations=self.ga_area_include_segmentations,
            ga_area_exclude_segmentations=self.ga_area_exclude_segmentations,
            fovea_landmark_idx=self.fovea_landmark_idx,
            **kwargs,
        )
