"""Utility functions for visualisation."""

from __future__ import annotations

import gc
import os
from pathlib import Path
from typing import Final, Optional, Union

import cv2
import matplotlib as mpl
from matplotlib import font_manager, pyplot as plt
import numpy as np
from numpy.typing import NDArray
from PIL import Image

from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    TOTAL_GA_AREA_LOWER_BOUND,
    TOTAL_GA_AREA_UPPER_BOUND,
)
from bitfount.metrics.types import Coordinates
from bitfount.visualisation import ASSETS_DIR

_SLIDER_DEFAULT_PATH: Final[Path] = ASSETS_DIR / "slider.png"
_REGULAR_FONT_PATH: Final[Path] = ASSETS_DIR / "Inter-Regular.ttf"
# Force matplotlib to not use any interactive backend.
mpl.use("Agg")


def overlay_with_alpha_layer(
    img: Image.Image,
    overlay: np.ndarray,
    colour: Union[str, tuple[int, int, int]] = (255, 0, 0),
    alpha: float = 0.3,
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


def resize_and_threshold_enface(
    enface: np.ndarray, smoothing: int = 1, threshold: float = 0.7
) -> NDArray[np.floating]:
    """Resize en-face image prior to drawing segmentation and apply thresholding.

    Resizes the input enface array to the expected size, applying smoothing to the
    width as desired.

    Then applies thresholding to the array to produce an array of 1.0 or 0.0
    indicating where the elements were greater than the threshold value.
    """
    h, w = enface.shape
    resized_enface: NDArray[Union[np.integer, np.floating]] = cv2.resize(
        enface.astype(np.float32), (w // smoothing, h)
    )
    enface_1_0: NDArray[np.floating] = (resized_enface > threshold) * 1.0
    return enface_1_0


def draw_registered_segmentation(
    background: Image.Image,
    segmentation: np.ndarray,
    metadata: np.ndarray,
    colour: Union[str, tuple[int, int, int]] = (255, 0, 0),
    alpha: float = 0.3,
    threshold: float = 0.7,
) -> Image.Image:
    """Visualise en-face image."""
    segmentation = resize_and_threshold_enface(segmentation, threshold=threshold)
    # Calculate Registration Matrix from OCT Coordinates to Enface OCT Volume
    input_pts = np.asarray(
        [[0, 0], [segmentation.shape[1] - 1, 0], [0, segmentation.shape[0] - 1]],
        dtype=np.float32,
    )
    output_pts = np.resize(metadata, (3, 2)).astype("float32")
    M = cv2.getAffineTransform(input_pts, output_pts)

    # Apply Transformation
    transformed = cv2.warpAffine(segmentation, M, background.size[:2])

    # Colour Transformed Image
    background = overlay_with_alpha_layer(background, transformed, colour, alpha)

    return background


def get_fovea_planar_coords(
    x: int, bscan_width: int, x_start: int, y_start: int, x_end: int, y_end: int
) -> Coordinates:
    """Returns the planar coordinates of the fovea in the en-face image.

    Args:
        x: The x coordinate of the fovea in the B-Scan.
        bscan_width: The width of the bscan.
        x_start: The x coordinate of the start of the bscan image.
        y_start: The y coordinate of the start of the bscan image.
        x_end: The x coordinate of the end of the bscan image.
        y_end: The y coordinate of the end of the bscan image.

    Returns:
        The planar coordinates of the fovea in the en-face image.
    """
    fovea_x = (x / bscan_width * (x_end - x_start)) + x_start
    fovea_y = (x / bscan_width * (y_end - y_start)) + y_start
    return Coordinates(fovea_x, fovea_y)


def generate_slider(
    ga_metric: float,
    filename: Optional[Union[str, os.PathLike]] = None,
    total_ga_area_lower_bound: float = TOTAL_GA_AREA_LOWER_BOUND,
    total_ga_area_upper_bound: float = TOTAL_GA_AREA_UPPER_BOUND,
) -> None:
    """Generates a slider for the GA metric.

    Args:
        ga_metric: The value of the GA metric.
        filename: The name of the file to save the slider to. Optional, defaults
            to "slider.png".
        total_ga_area_lower_bound: The lower bound of the GA area. Optional, defaults
            to 2.5.
        total_ga_area_upper_bound: The upper bound of the GA area. Optional, defaults
            to 17.5.
    """
    if filename is None:
        filename = _SLIDER_DEFAULT_PATH

    # Color mappings for the slider, matplotlib requires RGB values between 0 and 1
    bf_dark = (0 / 255, 143 / 255, 214 / 255)
    bf_dark_text = (0 / 255, 94 / 255, 141 / 255)
    bf_light = (235 / 255, 249 / 255, 255 / 255)

    # Import fonts
    font_manager.fontManager.addfont(_REGULAR_FONT_PATH)
    font_manager.FontProperties(fname=_REGULAR_FONT_PATH)
    mpl.rcParams["font.family"] = "Inter"

    # Make x & y numpy arrays for drawing the slider
    x = 0.1 + np.arange(total_ga_area_upper_bound * 100)
    y = [0.5] * int(total_ga_area_upper_bound * 100)

    # Get the integer value of the GA metric.
    # This is used for generating the light blue bars
    int_ga_metric = int(ga_metric * 100)

    # Axis for the black line and the markers in the bottom of the plot,
    # x_line start if dynamically defined
    x_line_end = x[-1]
    y_line = 0

    # Plot visualisation configurations - set figure size and disable axis
    plt.rcParams["figure.figsize"] = (38, 6)
    fig, ax = plt.subplots()
    plt.axis("off")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    if (
        ga_metric >= total_ga_area_lower_bound
        and ga_metric <= total_ga_area_upper_bound
    ):
        # The slider should appear blue only if the GA metric is greater than the lower
        # bound
        # The start line will be at the lower bound + the integer value of the GA metric
        x_line_start = (total_ga_area_lower_bound * 100) + x[0]
        # Plot light blue bars up to the value of the GA metric and white for the rest
        ax.bar(
            x,
            y,
            width=1,
            color=[bf_light] * int_ga_metric + ["white"] * (len(x) - int_ga_metric),
        )
        ax.set(
            xlim=(total_ga_area_lower_bound * 100, total_ga_area_upper_bound * 100),
            ylim=(-1, 0.5),
            yticks=np.arange(1, 2),
        )
        # Add the dark blue bar on top of the light blue bars marking
        # the value of the GA metric
        ax.arrow(
            x[int_ga_metric],
            0,
            0,
            y[16],
            color=bf_dark,
            length_includes_head=False,
            lw=2,
            head_width=0,
            head_length=0.00,
            width=1.5,
            fc=bf_dark,
            ec=bf_dark,
        )
        # Add the marker on top of the dark blue bar to match the designs
        plt.plot(
            x[int_ga_metric],
            y[16] - 0.165,
            marker=7,
            color=bf_dark,
            markersize=40,
            markeredgecolor=bf_dark,
            markerfacecolor=bf_dark,
        )

        # Add the text on top of the dark blue bar. We have two different
        # cases for the text placement as we don't want the text to go
        # out of the plot for small GA values.
        if ga_metric < total_ga_area_lower_bound + 0.1:
            ax.text(
                ga_metric * 100 - 10,
                0.55,
                f"{np.round(ga_metric, decimals=3)}mm\u00b2",
                color=bf_dark_text,
                fontname="Inter",
                fontsize=35,
            )
        else:
            ax.text(
                ga_metric * 100 - 20,
                0.55,
                f"{np.round(ga_metric, decimals=3)}mm\u00b2",
                color=bf_dark_text,
                fontname="Inter",
                fontsize=35,
            )
    else:
        # The slider should appear white if the GA metric is out of bounds
        x_line_start = x[0]
        ax.bar(x, y, width=1, color=["white"])
        ax.set(
            xlim=(0, total_ga_area_upper_bound * 100),
            ylim=(-1, 0.5),
            yticks=np.arange(1, 2),
        )

    # Add the black line and the markers at the bottom of the plot
    x_line = ax.add_line(mpl.lines.Line2D([x_line_start, x_line_end], [y_line, y_line]))
    x_line.set_color("black")
    plt.plot(
        x_line_start,
        y_line,
        marker=">",
        color="black",
        markersize=20,
        markeredgecolor="black",
        markerfacecolor="black",
    )
    plt.plot(
        x_line_end,
        y_line,
        marker="<",
        color="black",
        markersize=20,
        markeredgecolor="black",
        markerfacecolor="black",
    )
    # Add the text at the bottom of the plot
    plt.text(
        0,
        0.35,
        f"{total_ga_area_lower_bound}mm\u00b2",
        transform=ax.transAxes,
        fontname="Inter",
        fontsize=37,
    )
    plt.text(
        0.925,
        0.35,
        f"{total_ga_area_upper_bound}mm\u00b2",
        transform=ax.transAxes,
        fontname="Inter",
        fontsize=37,
    )
    plt.text(
        0.335,
        0.35,
        "GA area (mm\u00b2) trial inclusion range",
        transform=ax.transAxes,
        fontsize=37,
    )
    # Save the plot as a transparent png, so we can use it in the report
    plt.savefig(filename, format="png", transparent=True, bbox_inches="tight")
    # Clear the current axes.
    plt.cla()
    # Clear the current figure.
    plt.clf()
    # Closes all the figure windows.
    plt.close("all")
    # Garbage collect to free up memory used by the plot
    gc.collect()
