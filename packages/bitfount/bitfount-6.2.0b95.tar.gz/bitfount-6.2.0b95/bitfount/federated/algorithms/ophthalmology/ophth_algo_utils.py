"""Utilities for ophthalmology plugins."""

from __future__ import annotations

from collections.abc import Collection, Iterable
from functools import partial
import re
import typing
from typing import Mapping, Optional, Union

import cv2
import numpy as np
import pandas as pd
import PIL
from PIL import Image, ImageDraw, ImageFont

from bitfount.data.datasources.base_source import BaseSource, FileSystemIterableSource
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.data.datasplitters import DatasetSplitter, _InferenceSplitter
from bitfount.data.types import DataSplit
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    COLOR_NOT_DETECTED,
    DEFAULT_COLUMNS_TO_RENAME,
    DICOM_COLUMNS_TO_RENAME,
    GA_SEGMENTATION_LABELS,
    HEIDELBERG_COLUMNS_TO_RENAME,
    LABELS_SEG_FORMATTED,
    MARKER_NOT_DETECTED_TEXT,
    PATH_FONT_NO_MARKER,
    SEGMENTATION_COLORS,
    TEXT_TO_IMAGE_RATIO_NO_MARKERS,
    GAMetrics,
    GAMetricsWithFovea,
    OCTImageMetadataColumns,
    SLOImageMetadataColumns,
    SLOSegmentationLocationPrefix,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.models.types import (
    MaskAltrisBiomarker,
    MaskInstance,
    MaskInstanceEllipse,
    MaskInstancePolygon,
    MaskInstancePolyline,
    MaskSegmentationModel,
)
from bitfount.types import PredictReturnType
from bitfount.visualisation.utils import draw_registered_segmentation

logger = _get_federated_logger("bitfount.federated")


def get_imgs_with_segmentation_from_enface_slo(
    data: pd.DataFrame,
    enface_output: np.ndarray,
    slos: np.ndarray,
    slo_photo_location_prefixes: Optional[SLOSegmentationLocationPrefix] = None,
    slo_image_metadata_columns: Optional[SLOImageMetadataColumns] = None,
    oct_image_metadata_columns: Optional[OCTImageMetadataColumns] = None,
    colour: Union[str, tuple[int, int, int]] = (0, 255, 255),
    alpha: float = 0.75,
    threshold: float = 0.7,
) -> list[Image.Image]:
    """Get images with segmentation on SLO image from enfaces."""
    imgs: list[Image.Image] = []
    if slo_photo_location_prefixes is not None:
        for row_index, (enface, slo) in enumerate(zip(enface_output, slos)):
            IR = Image.fromarray(slo[0]).convert("RGB")
            try:
                start_x_img_0 = data[
                    f"{slo_photo_location_prefixes.start_x_image}0"
                ].iloc[row_index]
                start_y_img_0 = data[
                    f"{slo_photo_location_prefixes.start_y_image}0"
                ].iloc[row_index]
                end_x_img_0 = data[f"{slo_photo_location_prefixes.end_x_image}0"].iloc[
                    row_index
                ]
                end_y_img_0 = data[f"{slo_photo_location_prefixes.end_y_image}0"].iloc[
                    row_index
                ]
                start_x_last_img = data[
                    f"{slo_photo_location_prefixes.start_x_image}{enface.shape[0] - 1}"
                ].iloc[row_index]
                start_y_last_img = data[
                    f"{slo_photo_location_prefixes.start_y_image}{enface.shape[0] - 1}"
                ].iloc[row_index]
                metadata = np.array(
                    [
                        start_x_img_0,
                        start_y_img_0,
                        end_x_img_0,
                        end_y_img_0,
                        start_x_last_img,
                        start_y_last_img,
                    ]
                )

                img = draw_registered_segmentation(
                    IR,
                    enface,
                    metadata,
                    colour=colour,
                    alpha=alpha,
                    threshold=threshold,
                )

                imgs.append(img)
            except KeyError as err:
                logger.warning(
                    f"Location column {err} was not found in the data. "
                    "Will use default pixel location values."
                )

    # if provided locations not found or no locations provided
    if len(imgs) == 0 or slo_photo_location_prefixes is None:
        if (
            slo_image_metadata_columns is not None
            and oct_image_metadata_columns is not None
        ):
            # if no location prefixes given but the images
            # metadata is provided, we compute the start
            # location of the OCT on the SLO assuming the
            # 3d OCT image is centered on the 2d SLO image
            # using the width and length of the slo and
            # the width and depth of the OCT images
            try:
                for row_index, (enface, slo) in enumerate(zip(enface_output, slos)):
                    IR = Image.fromarray(slo[0]).convert("RGB")

                    slo_mm_width = round(
                        data[slo_image_metadata_columns.width_mm_column].iloc[
                            row_index
                        ],
                        2,
                    )
                    slo_mm_height = round(
                        data[slo_image_metadata_columns.height_mm_column].iloc[
                            row_index
                        ],
                        2,
                    )
                    slo_pixel_dim_height, slo_pixel_dim_width = np.squeeze(slo).shape

                    oct_width = data[oct_image_metadata_columns.width_mm_column].iloc[
                        row_index
                    ]
                    oct_depth = data[oct_image_metadata_columns.depth_mm_column].iloc[
                        row_index
                    ]
                    # since the width of both SLO and OCT should be
                    # matching, we can compute the start of the first
                    # image on the x-axis as
                    # (slo_mm_width - oct_mm_width)/2 / slo_mm_width * slo_pixel_dim_width, # noqa: E501
                    # where the slo_pixel_dim_width is the number
                    # of pixels found on the width of the SLO.
                    # Note that the start of the images on the
                    # x-axis should be the same for all images.
                    start_x_img_0 = (
                        (slo_mm_width - oct_width)
                        / 2
                        / (slo_mm_width)
                        * slo_pixel_dim_width
                    )
                    # for the y-axis, the slo height aligns with the OCT
                    # depth, so we compute the start of the image on the
                    # y-axis on these two dimensions similar to the x-axis
                    start_y_img_0 = (
                        (slo_mm_height - (slo_mm_height - oct_depth) / 2)
                        / (slo_mm_height)
                        * slo_pixel_dim_height
                    )
                    end_x_img_0 = (
                        (slo_mm_width - (slo_mm_width - oct_width) / 2)
                        / (slo_mm_width)
                        * slo_pixel_dim_width
                    )
                    end_y_img_0 = (
                        (slo_mm_height - (slo_mm_height - oct_depth) / 2)
                        / (slo_mm_height)
                        * slo_pixel_dim_height
                    )
                    start_x_last_img = (
                        (slo_mm_width - oct_width)
                        / 2
                        / (slo_mm_width)
                        * slo_pixel_dim_width
                    )
                    start_y_last_img = (
                        (slo_mm_height - oct_depth)
                        / 2
                        / (slo_mm_height)
                        * slo_pixel_dim_height
                    )

                    metadata = np.array(
                        [
                            start_x_img_0,
                            start_y_img_0,
                            end_x_img_0,
                            end_y_img_0,
                            start_x_last_img,
                            start_y_last_img,
                        ]
                    )

                    img = draw_registered_segmentation(
                        IR,
                        enface,
                        metadata,
                        colour=colour,
                        alpha=alpha,
                        threshold=threshold,
                    )
                    imgs.append(img)
            except KeyError as err:
                logger.warning(
                    f"Column {err} was not found in the data. "
                    "Will use default pixel location values."
                )
    # if still no images then use defaults
    if len(imgs) == 0:
        logger.info("Using default pixel image locations.")
        for enface, slo in zip(enface_output, slos):
            IR = Image.fromarray(slo[0]).convert("RGB")
            # We are only concerned with the first 6 continuous
            # variables from the metadata here.

            # when we don't have all the information,
            # we assign default values for the metadata.
            metadata = np.array([128, 640, 640, 640, 128, 128])
            img = draw_registered_segmentation(
                IR,
                enface,
                metadata,
                colour=colour,
                alpha=alpha,
                threshold=threshold,
            )
            imgs.append(img)
    return imgs


def get_dataframe_iterator_from_datasource(
    datasource: BaseSource,
    data_splitter: Optional[DatasetSplitter] = None,
    use_cache: bool = True,
) -> Iterable[pd.DataFrame]:
    """Get dataframe iterator from datasource.

    Args:
        datasource: The datasource to get the dataframe iterator from.
        data_splitter: The data splitter to use when getting the dataframes.
        use_cache: Whether to use the cache when getting the dataframes.

    Returns:
        An iterable of dataframes from the datasource.
    """
    data_splitter = data_splitter if data_splitter else _InferenceSplitter()

    # To enable working with both iterable- and non-iterable-datasources, we
    # work with the assumption of processing the dataset in an iterable manner,
    # with a non-iterable-dataset simply being converted into a one-element
    # iterable.
    test_data_dfs: Iterable[pd.DataFrame]

    test_data_dfs = data_splitter.iter_dataset_split(
        datasource, DataSplit.TEST, use_cache=use_cache
    )

    return test_data_dfs


def _split_points(points: np.ndarray) -> list[np.ndarray]:
    """Split points into separate arrays of maximum length 2."""
    return [np.asarray(np.array_split(points, len(points) // 2), dtype=np.int32)]


def _draw_instance(
    img: np.ndarray,
    instance: MaskInstance,
) -> np.ndarray:
    """Draw instance/segmentation details on an image.

    Args:
        img: Array representation of the image data.
        instance: Segmentation details dict from model output. Supported segmentation
            types are "polyline", "polygon", and "ellipse".

    Returns:
        An array representing the image data with pixels that fell under the
        segmentation coloured.
    """
    if instance["type"] == "polyline":
        instance = typing.cast(MaskInstancePolyline, instance)
        img = cv2.polylines(  # type: ignore[call-overload] # Reason: Issue with CV2 typing # noqa: E501
            img=img,
            pts=_split_points(np.asarray(instance["points"])),
            isClosed=False,
            color=1,
            thickness=3,
        )
    elif instance["type"] == "polygon":
        instance = typing.cast(MaskInstancePolygon, instance)
        img = cv2.fillPoly(
            img=img, pts=_split_points(np.asarray(instance["points"])), color=1
        )  # type: ignore[call-overload] # Reason: Issue with CV2 typing # noqa: E501
    elif instance["type"] == "ellipse":
        instance = typing.cast(MaskInstanceEllipse, instance)
        img = cv2.ellipse(  # type: ignore[call-overload] # Reason: Issue with CV2 typing # noqa: E501
            img=img,
            center=(int(instance["cx"]), int(instance["cy"])),
            axes=(int(instance["rx"]), int(instance["ry"])),
            angle=int(instance["angle"]),
            startAngle=0,
            endAngle=360,
            color=255,
            thickness=-1,
        )
    else:
        logger.warning(f"Met unknown previously instance type: {instance['type']}")

    return img


def parse_mask_json(
    json_data: MaskAltrisBiomarker | MaskSegmentationModel, labels: dict[str, int]
) -> np.ndarray:
    """Parse segmentation mask(s) from JSON.

    Args:
        json_data: The model output JSON data for the masks.
        labels: The segmentation classes to generate masks for mapped to their index in
            the mask data.

    Returns:
        A `(num_segmentations, image_height, image_width)` array where each
        `(image_height, image_width)` subarray is the mask for a different segmentation
        class.
    """
    n_labels_seg = len(labels)
    image_height, image_width = (
        int(json_data["metadata"]["height"]),
        int(json_data["metadata"]["width"]),
    )

    # Create empty masks
    mask = np.zeros((n_labels_seg, image_height, image_width), dtype=np.float32)

    # Create empty holder for "instances" (i.e. "segmentation classes") to draw be
    # drawn on
    instances = np.zeros(
        (
            # `json_data["instances"]` is the list of segmentation class output dicts
            # (ordered by the segmentation index)
            len(json_data["instances"]),
            image_height,
            image_width,
        ),
        dtype=np.float32,
    )

    for i, instance in enumerate(json_data["instances"]):
        # Do not handle segmentation outputs of type "point"
        if instance["type"] == "point":
            continue

        # For the segmentation type, draw the instance output and then calculate the
        # mask
        attribute_name = instance["className"]

        # Fix attribute name format if needed
        attribute_name = re.sub(r"[^\w]", "_", attribute_name).lower()

        # Draw the instance output shape and set it on the holder array
        instances[i] = _draw_instance(instances[i], instance=instance)

        try:
            attribute_idx = labels[attribute_name]
            # Find the element-wise maximum of the current mask and the drawn
            # instance shape and set this as the new mask.
            mask[attribute_idx] = np.maximum(mask[attribute_idx], instances[i])
        except KeyError:
            continue

    return mask


def draw_segmentation_mask_on_orig_image(
    mask: np.ndarray,
    image: PIL.Image.Image,
    segmentation_labels: dict[str, int] = GA_SEGMENTATION_LABELS,
    segmentation_colors: dict[str, tuple[int, int, int]] = SEGMENTATION_COLORS,
    formatted_segmentation_labels: dict[str, str] = LABELS_SEG_FORMATTED,
    color_not_detected: tuple[int, int, int] = COLOR_NOT_DETECTED,
) -> tuple[Image.Image, dict[str, tuple[int, int, int]]]:
    """Draw segmentation mask on original image.

    Args:
        mask (np.ndarray): Segmentation mask of shape (n_classes, height, width).
        image (PIL.Image): Original image.
        segmentation_labels (dict): Mapping of segmentation labels to class IDs.
        segmentation_colors (dict): Mapping of class IDs to colors.
        formatted_segmentation_labels (dict): Mapping of class IDs to formatted labels.
        color_not_detected (tuple): Color for not detected classes.

    Returns:
        tuple: Tuple containing the image with segmentation mask and a legend
            mapping class names to colors.
    """
    id_labels_seg = {v: k for k, v in segmentation_labels.items()}
    num_classes, height, width = mask.shape
    legend2color: dict[str, tuple[int, int, int]] = {}
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    canvas[:, :] = (0, 0, 0)  # Black background canvas

    for key, value in id_labels_seg.items():
        try:
            class_mask = mask[key, :, :]
        except IndexError:
            logger.warning(
                f"Missing mask for {formatted_segmentation_labels[value]}. Skipping."
            )
            continue

        if len(np.unique(class_mask)) > 1:
            legend2color[formatted_segmentation_labels[value]] = segmentation_colors[
                value
            ]
        else:
            legend2color[formatted_segmentation_labels[value] + " (not detected)"] = (
                color_not_detected
            )
        image = overlay_with_alpha_layer_ga_trial(
            image, mask[key, :, :], segmentation_colors[value]
        )

    if len(set(legend2color.values())) == 1:
        image = overlay_with_grey_mask_ga_trial(image)
    return image, legend2color


def overlay_with_alpha_layer_ga_trial(
    img: Image.Image,
    overlay: np.ndarray,
    colour: Union[str, tuple[int, int, int]] = (255, 0, 0),
    alpha: float = 0.8,
) -> Image.Image:
    """Overlay an image with a segmentation."""
    # Colour Transformed Image
    overlay_ = np.ones([overlay.shape[0], overlay.shape[1], 4])
    if not isinstance(colour, tuple):
        color = tuple(int(colour[i : i + 2], 16) for i in (0, 2, 4))
    else:
        color = colour
    for i, c in enumerate(color):
        overlay_[:, :, i] *= c
    overlay_[:, :, 3] = overlay * 255 * alpha
    # Convert to Uint8
    overlay = overlay_.astype(np.uint8)
    overlay_img = Image.fromarray(overlay)
    # Superimpose the Transformation
    img = img.convert("RGBA")
    img.paste(overlay_img, (0, 0), overlay_img)
    return img


def overlay_with_grey_mask_ga_trial(
    img: Image.Image,
    alpha: float = 0.3,
) -> Image.Image:
    """Overlay an image with a segmentation."""
    width, height = (img.size[0], img.size[1])
    # Colour Transformed Image
    overlay_ = np.ones([height, width, 4])
    overlay = np.ones([height, width])
    for i, c in enumerate(COLOR_NOT_DETECTED):
        overlay_[:, :, i] *= c
    overlay_[:, :, 3] = overlay * 255 * alpha
    # Convert to Uint8
    overlay = overlay_.astype(np.uint8)

    # Superimpose the Transformation
    overlay_img = Image.fromarray(overlay)
    img = img.convert("RGBA")
    img.paste(overlay_img, (0, 0), overlay_img)

    # Draw the strip with text
    try:
        img = draw_no_markers_detected_on_image_strip(img, height, width)
    except Exception:
        logger.warning(
            "Failed to draw the strip with text for no marker detected."
            "Returning original image with a grey mask instead."
        )
    else:
        logger.debug("Successfully drew the strip with text for no marker detected.")

    return img


def center_text_on_strip(
    img: Image.Image,
    font: ImageFont.FreeTypeFont,
    text_width: int,
    text_height: int,
    text: str,
    strip_width: int,
    strip_height: int,
    color: tuple[int, int, int] = (0, 0, 0),
) -> Image.Image:
    """Center text on image.

    Args:
        img: The image to draw the text on.
        font: The font to use for the text.
        text_width: The width of the text.
        text_height: The height of the text.
        text: The text to draw on the image.
        strip_width: The width of the strip.
        strip_height: The height of the strip.
        color: The color of the text. Defaults to black.
    """
    draw = ImageDraw.Draw(img)
    position = ((strip_width - text_width) // 2, (strip_height - text_height) // 2)
    draw.text(position, text, color, font=font)
    return img


def draw_no_markers_detected_on_image_strip(
    img: Image.Image, height: int, width: int
) -> Image.Image:
    """Draw the "No markers detected" strip on the image.

    Args:
        img: The image to draw the strip on.
        height: The height of the image.
        width: The width of the image.
    """
    # First we find the strip and font sizes based on the image size
    # Set how much of the image you want to be filled with the text
    img_fraction = TEXT_TO_IMAGE_RATIO_NO_MARKERS
    font_size = min(int(height / 25), int(width / 25))
    # Enable drawing on the image
    img_draw = ImageDraw.Draw(img)
    # Custom font style and font size
    # Iterate until the text size is just larger than the criteria so
    # that the strip fits the size of the image
    myFont = ImageFont.truetype(PATH_FONT_NO_MARKER, font_size)
    strip_width, strip_height = (0, 0)
    while (
        myFont.getbbox(MARKER_NOT_DETECTED_TEXT)[0] < img_fraction * width
        and strip_width < width * img_fraction
        and strip_height < height * 0.15
    ):
        # iterate until the text size is just larger than the criteria
        font_size += 1
        myFont = ImageFont.truetype(PATH_FONT_NO_MARKER, font_size)
        # Get the width and height of the text from the font
        text_left, text_top, text_right, text_bottom = img_draw.textbbox(
            xy=(0, 0), text=MARKER_NOT_DETECTED_TEXT, font=myFont
        )
        text_width = abs(text_right - text_left)
        text_height = abs(text_top - text_bottom)
        # Define strip width and height
        strip_width, strip_height = (text_width + font_size, text_height + font_size)

    myFont = ImageFont.truetype(PATH_FONT_NO_MARKER, font_size - 1)

    text_left, text_top, text_right, text_bottom = img_draw.textbbox(
        xy=(0, 0), text=MARKER_NOT_DETECTED_TEXT, font=myFont
    )
    text_width = abs(text_right - text_left)
    text_height = abs(text_top - text_bottom)
    # Define strip width and height
    strip_width, strip_height = (text_width + font_size, text_height + font_size)
    background = Image.new("RGB", (strip_width, strip_height), color=COLOR_NOT_DETECTED)
    strip = center_text_on_strip(
        background,
        myFont,
        text_width,
        text_height,
        MARKER_NOT_DETECTED_TEXT,
        strip_width,
        strip_height,
    )

    # Center the strip and paste it on the original image
    offset = (
        (width - strip_width) // 2,
        (height - strip_height) // 2,
        (width + strip_width) // 2,
        (height + strip_height) // 2,
    )
    img.paste(strip, offset)

    return img


def is_file_iterable_source(datasource: BaseSource) -> bool:
    """True iff datasource is a file iterable source (or subclass)."""
    return isinstance(datasource, FileSystemIterableSource)


def _sort_col_by_list(col: pd.Series, sort_by: list[str]) -> pd.Series:
    """Produce a Series that is the sort-values to sort col to match sort_by."""
    return col.map(lambda i: sort_by.index(i))


def get_data_for_files(
    datasource: FileSystemIterableSource,
    filenames: list[str],
    file_key_col: str = ORIGINAL_FILENAME_METADATA_COLUMN,
    use_cache: bool = True,
) -> pd.DataFrame:
    """Retrieve data from a datasource for a given list of files.

    The dataframe returned will be sorted to match the ordering of the files in
    `filenames`.
    """
    df: Optional[pd.DataFrame] = datasource.get_data(filenames, use_cache=use_cache)

    # If no data, return an empty dataframe but with the expected col.
    if df is None:
        return pd.DataFrame(columns=[file_key_col])

    df = df.sort_values(
        by=file_key_col,
        axis="index",
        key=partial(_sort_col_by_list, sort_by=filenames),
    )
    df = df.reset_index(drop=True)
    return df


def _convert_predict_return_type_to_dataframe(
    predictions: Union[PredictReturnType, pd.DataFrame],
) -> pd.DataFrame:
    """Convert PredictReturnType to DataFrame if necessary.

    Args:
        predictions: The predictions from the model algorithm.

    Returns:
        The predictions as a DataFrame.
    """
    predictions_df: pd.DataFrame
    if isinstance(predictions, PredictReturnType):
        if isinstance(predictions.preds, pd.DataFrame):
            predictions_df = predictions.preds
        else:
            predictions_df = pd.DataFrame(predictions.preds)

        # Add keys to DataFrame
        if predictions.keys is not None:
            predictions_df[ORIGINAL_FILENAME_METADATA_COLUMN] = predictions.keys
    else:  # is DataFrame
        predictions_df = predictions

    return predictions_df


def use_default_rename_columns(
    datasource: BaseSource,
    rename_columns: Optional[typing.Mapping[str, str]] = None,
) -> Optional[typing.Mapping[str, str]]:
    """Sets the default columns to include based on the datasource."""
    # Add the relevant columns for the datasources
    if type(datasource).__name__ == "HeidelbergSource":
        if rename_columns is None:
            rename_columns = dict(
                HEIDELBERG_COLUMNS_TO_RENAME, **DEFAULT_COLUMNS_TO_RENAME
            )
    elif type(datasource).__name__ == "DICOMOphthalmologySource":
        if rename_columns is None:
            rename_columns = dict(DICOM_COLUMNS_TO_RENAME, **DEFAULT_COLUMNS_TO_RENAME)
    return rename_columns


def _convert_ga_metrics_to_df(
    ga_metrics: Mapping[str, Optional[GAMetrics]]
    | Mapping[str, Optional[GAMetricsWithFovea]],
    additional_pathology_prob_cols: Optional[Collection[str]] = None,
) -> pd.DataFrame:
    """Convert a dict of GAMetrics objects into a dataframe.

    Args:
        ga_metrics: The mapping of filename to GAMetrics instances to convert into a
            dataframe.
        additional_pathology_prob_cols: Any additional pathology names
            (e.g. "hard_drusen") that should be extracted into distinct
            "max_<X>_probability" columns in the dataframe.

    Returns:
        A dataframe with each row representing the GAMetrics information for a single
        file.
    """
    metrics_df = pd.DataFrame.from_records(
        ga_d.to_record(additional_pathology_prob_cols=additional_pathology_prob_cols)
        if ga_d is not None
        else dict()
        for ga_d in ga_metrics.values()
    )
    metrics_df[ORIGINAL_FILENAME_METADATA_COLUMN] = list(ga_metrics.keys())

    # Ensure that all expected columns are present, even if they are empty
    expected_cols: list[str]
    exemplar_value: Optional[GAMetrics | GAMetricsWithFovea] = next(
        iter(ga_metrics.values()), None
    )
    if exemplar_value is None:
        logger.warning(
            "There were no values in `ga_metrics` mapping,"
            " treating as though GAMetrics instances"
        )
        expected_cols = GAMetrics.expected_cols()
    elif isinstance(exemplar_value, GAMetricsWithFovea):
        expected_cols = GAMetricsWithFovea.expected_cols()
    else:  # isinstance(exemplar_value, GAMetrics)
        expected_cols = GAMetrics.expected_cols()
    existing_cols: list[str] = metrics_df.columns.to_list()

    if missing_cols := sorted(list(set(expected_cols) - set(existing_cols))):
        logger.warning(
            f"Columns were missing from the GA Metrics DataFrame:"
            f" {', '.join(missing_cols)}."
            f" Adding empty columns for these."
        )
        metrics_df = metrics_df.reindex(columns=existing_cols + expected_cols)

    return metrics_df
