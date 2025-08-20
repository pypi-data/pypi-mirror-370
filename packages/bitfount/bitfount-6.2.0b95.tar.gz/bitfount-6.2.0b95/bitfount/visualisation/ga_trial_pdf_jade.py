"""Generate a PDF report from a template."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import math
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Final, Optional, Union

from fpdf import FPDF, XPos
from fpdf.enums import Align
import PIL
from PIL.Image import Image

from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    TOTAL_GA_AREA_LOWER_BOUND,
    TOTAL_GA_AREA_UPPER_BOUND,
    GAMetrics,
    GAMetricsWithFovea,
)
from bitfount.hub.helper import get_hub_url
from bitfount.visualisation import ASSETS_DIR
from bitfount.visualisation.utils import generate_slider

BITFOUNT_BLUE: tuple[int, int, int] = (25, 33, 77)
GREY: tuple[int, int, int] = (118, 134, 158)
BLACK: int = 0

_LOGO_PATH: Final[Path] = ASSETS_DIR / "bitfount_logo_horizontal.png"
_ALTRIS_LOGO_PATH: Final[Path] = ASSETS_DIR / "Altris_600x300.svg"
_REGULAR_FONT_PATH: Final[Path] = ASSETS_DIR / "Inter-Regular.ttf"
_SEMIBOLD_FONT_PATH: Final[Path] = ASSETS_DIR / "Inter-SemiBold.ttf"
GA_DICT_KEYS_TO_LABELS = {
    "total_ga_area": "Total GA area",
    "smallest_lesion_size": "Smallest lesion size",
    "largest_lesion_size": "Largest lesion size",
    "num_bscans_with_ga": "Slices with GA",
    "num_ga_lesions": "Number of GA lesions",
    "distance_from_image_centre": "Distance from image centre",
    "distance_from_fovea_centre": "Distance from fovea",
    "subfoveal_indicator": "Subfoveal lesion",
}
GA_METRICS_UNITS = {
    "total_ga_area": "mm\u00b2",
    "smallest_lesion_size": "mm\u00b2",
    "largest_lesion_size": "mm\u00b2",
    "distance_from_image_centre": "mm",
    "distance_from_fovea_centre": "mm",
}
SUMMARY_TABLE_COLUMN_COUNT = 2
SUMMARY_TABLE_KEYS = [
    "total_ga_area",
    "smallest_lesion_size",
    "largest_lesion_size",
    "distance_from_image_centre",
    "distance_from_fovea_centre",
    "subfoveal_indicator",
]

HUB_TASK_URL_PATH_PREFIX = "tasks/task/"


@dataclass
class AltrisRecordInfo:
    """Patient/scan information for the report.

    Args:
        text_fields: A list of tuples of heading and value for the pdf top table.
        heading: The heading for the pdf. Defaults to None.
    """

    text_fields: list[tuple[str, str]]
    heading: Optional[str] = "GA OCT REPORT"


@dataclass
class AltrisScan:
    """Scan information for the report.

    Args:
        name: Name of the scan.
        en_face_image_path: Path to the en-face image.
        bscan_image_path: Path to the B-scan image. This should be the bscan that
            corresponds to the location of the fovea.
    """

    bscan_image: Union[str, os.PathLike, Image]
    bscan_idx: int
    bscan_total: int
    bscan_w_mask: Union[str, os.PathLike, Image]
    legend2color: dict[str, tuple[int, int, int]]
    laterality: Optional[str] = None
    bscan_en_face: Optional[Union[str, os.PathLike, Image]] = None
    # Placeholder for en face image


class ReportJade(FPDF):
    """Generate a PDF report from a template.

    Args:
        report_info: Patient/scan information for the report.
        scan: List of scans to include in the report.
        metrics: List of GA metrics to include in the report.
        total_ga_area_lower_bound: The lower bound for the GA area. This is used to
            generate the slider. Defaults to 2.5.
        total_ga_area_upper_bound: The upper bound for the GA area. This is used to
            generate the slider. Defaults to 17.5.
        task_id: The task ID. Defaults to None.
        **kwargs: Keyword arguments to pass to the FPDF
            class. See https://pyfpdf.github.io/fpdf2.
    """

    def __init__(
        self,
        record_info: AltrisRecordInfo,
        scan: Union[AltrisScan, list[AltrisScan]],
        metrics: Union[GAMetrics, list[GAMetrics]],
        total_ga_area_lower_bound: float = TOTAL_GA_AREA_LOWER_BOUND,
        total_ga_area_upper_bound: float = TOTAL_GA_AREA_UPPER_BOUND,
        task_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.add_font(
            "Inter",
            "",
            f"{_REGULAR_FONT_PATH}",
            uni=True,
        )
        self.add_font(
            "Inter",
            style="B",
            fname=f"{_SEMIBOLD_FONT_PATH}",
        )
        self.report_info = record_info.text_fields
        self.heading = record_info.heading
        self.scan = scan if isinstance(scan, list) else [scan]
        self.metrics = metrics if isinstance(metrics, list) else [metrics]
        self.total_ga_area_lower_bound = total_ga_area_lower_bound
        self.total_ga_area_upper_bound = total_ga_area_upper_bound
        self.task_id = task_id

        # Helper attributes
        self._right_x = self.w - self.r_margin
        self._left_x = self.l_margin
        self._top_y = self.t_margin
        self._bottom_y = self.h - self.b_margin
        self.laterality_added = False
        self._summary_heading_added = False

    def header(self) -> None:
        """Adds the header to the report.

        Adds the Bitfount logo to the top right of every page. This is called
        automatically by the FPDF class.
        """
        self.image(
            name=str(_ALTRIS_LOGO_PATH),
            x=self._right_x - 39,
            y=self._top_y - 10,
            w=40,
        )

        self.ln(20)

    def generate(self) -> None:
        """Generates the report.

        This should be called by the user.
        """
        self.add_page()
        self.set_font("Inter", size=20, style="B")
        self.set_text_color(*BITFOUNT_BLUE)
        y = 20
        self.set_y(y)
        link = ""
        if self.task_id:
            hub_url = get_hub_url()
            link = f"{hub_url}/{HUB_TASK_URL_PATH_PREFIX}/{self.task_id}"
        if self.heading:
            self.cell(
                w=0,
                h=5,
                text=self.heading,
                border=False,
                align=Align.L,
                link=link,
            )
            y += 8

        self.set_line_width(0.35)
        self.set_draw_color(*GREY)
        y = self._details_table(y + 6)
        y += 4
        self.line(x1=self._left_x, y1=y, x2=self._right_x, y2=y)
        for metric, scan in zip(
            self.metrics,
            self.scan,
        ):
            _scan_details_table_added = False
            # summary table is only added if the scan has a mask
            y = self._summary_table(y, metric=metric, scan=scan)
            y = self._add_slider(y, ga_metric=metric.total_ga_area)
            y = self._add_scans(y, scan)
            if not _scan_details_table_added:
                # If summary table was not added, then we add it now under the scans
                y = self._scan_details_table(y + 3, metric=metric, scan=scan)

        self.line(
            x1=self._left_x,
            y1=self._bottom_y,
            x2=self._right_x,
            y2=self._bottom_y,
        )

    def footer(self) -> None:
        """Adds the footer to the report.

        Adds 'Bitfount' and the page number to every report. This is called
        automatically by the FPDF class.
        """
        self.set_xy(70, self._bottom_y + 5)
        self.set_font("Inter", size=8)
        self.image(
            name=str(_LOGO_PATH),
            x=self._left_x,
            y=self._bottom_y + 7,
            w=20,
        )
        self.multi_cell(
            w=50,
            h=10,
            text="Research Use Only",
            border=False,
            align=Align.C,
        )
        self.set_xy(self._right_x - 50, self._bottom_y + 5)
        self.set_font("Inter", size=8)

        self.multi_cell(
            w=50,
            h=10,
            text=datetime.now().strftime("%d %B %Y %I:%M")
            + datetime.now().strftime("%p").lower(),
            border=False,
            align=Align.R,
        )

    def _add_slider(self, y: int, ga_metric: float) -> int:
        """Adds the slider to the report.

        Args:
            y: The y-coordinate of the top left corner of the table.
            ga_metric: The GA metric.
        """
        slider_height = 30

        # To ensure that the location for the slider PNG is writeable, we use a temp
        # directory. We use this in preference to (Named)TemporaryFile as we cannot
        # guarantee that calls further down the stack will not close the file
        # prematurely.
        with TemporaryDirectory() as tmpdir:
            slider_file: str = str(Path(tmpdir) / "slider.png")
            generate_slider(
                ga_metric,
                filename=slider_file,
                total_ga_area_lower_bound=self.total_ga_area_lower_bound,
                total_ga_area_upper_bound=self.total_ga_area_upper_bound,
            )
            self.image(
                name=slider_file,
                x=self._left_x + 1,
                y=y,
                h=slider_height,
                w=self._right_x - self._left_x - 1,
            )

        y += slider_height
        return y

    def _scan_details_table(self, y: int, metric: GAMetrics, scan: AltrisScan) -> int:
        """Adds the scan details table to the report.

        This is the part of the report that includes the slice number,
        number of total slices, and slices with GA.

        Args:
            y: The y-coordinate of the top left corner of the table.
            metric: The GA metrics.
            scan: The scan.
        """
        x = self._left_x
        self.set_y(y)
        self.set_font("Inter", size=8)
        self.set_text_color(BLACK)

        if metric.total_ga_area > 0:
            ga_bscan_text = (
                f"Slice with largest amount of GA: "
                f"{scan.bscan_idx + 1}/{scan.bscan_total}"
            )
        else:
            ga_bscan_text = f"Central slice: {scan.bscan_idx + 1}/{scan.bscan_total}"
        self.multi_cell(
            w=60,
            h=5,
            text=ga_bscan_text,
            border=False,
            align=Align.L,
        )
        x = x + len(ga_bscan_text) + 20
        self.set_xy(x, y)
        analysed_slices_text = f"Analysed slices: {scan.bscan_total}/{scan.bscan_total}"
        self.multi_cell(
            w=40,
            h=5,
            text=analysed_slices_text,
            border=False,
        )
        x = x + len(analysed_slices_text) + 15
        self.set_xy(x, y)
        self.multi_cell(
            w=40,
            h=5,
            text=f"Slices with GA: {metric.num_bscans_with_ga}",
            border=False,
        )
        self._scan_details_table_added = True
        return y

    def _add_scans(self, y: int, scan: AltrisScan) -> int:
        """Adds the scans to the report.

        Returns:
            The y value after all scans added.

        """
        x = self._left_x
        self.set_xy(x=x, y=y)
        new_y = self._add_scan(scan=scan, x=x, y=y)
        return new_y

    def _add_scan(self, scan: AltrisScan, x: float, y: int) -> int:
        """Adds a single scan to the report.

        Args:
            scan: The scan to add.
            x: x-coordinate of the top left corner of the scan.
            y: y-coordinate of the top left corner of the scan.

        Returns:
            The y value after all scans added.
        """
        img_params = self.image(name=scan.bscan_image, x=x, y=y, w=55)
        img_height = math.ceil(img_params["rendered_height"]) + 1
        img_params = self.image(name=scan.bscan_w_mask, x=x + 60, y=y, w=55)
        self._image_colour_legend(x=x + 120, y=y + 3, legend2color=scan.legend2color)
        if img_params["rendered_height"] + 1 > img_height:
            img_height = math.ceil(img_params["rendered_height"]) + 1
        y += img_height
        return y

    def _add_cell(
        self,
        header: str,
        body: str,
        x: float,
        y: float,
        horizontal_distance: int,
        font_sizes: tuple[int, int] = (8, 10),
        fixed_spacing: Optional[int] = None,
    ) -> None:
        """Add a cell to the report.

        Args:
            header: The header of the cell.
            body: The body of the cell.
            x: x-coordinate of the top left corner of the cell.
            y: y-coordinate of the top left corner of the cell.
            horizontal_distance: The horizontal distance to the next cell.
            font_sizes: The font sizes for the label and text.
            fixed_spacing: The fixed spacing between the label and text.
        """
        self.set_xy(x=x, y=y)
        self.set_font(size=font_sizes[0], style="B")
        self.set_text_color(*GREY)
        self.multi_cell(w=horizontal_distance, h=5, text=header, border=False)
        if fixed_spacing:
            spacing = fixed_spacing
        else:
            spacing = len(header) * 2
        self.set_xy(x=x + spacing, y=y)
        self.set_font(size=font_sizes[1])
        self.set_text_color(BLACK)
        self.multi_cell(
            w=horizontal_distance, h=5, text=body, border=False, new_x=XPos.LMARGIN
        )

    def _details_table(self, y: int) -> int:
        """Adds the top table to the report.

        Returns:
            The y value where the table finishes.
        """
        table_vertical_distance = 6
        table_horizontal_distance = 200

        for index in range(len(self.report_info)):
            if self.report_info[index][0].isupper():
                cell_header = self.report_info[index][0]
            else:
                cell_header = self.report_info[index][0].title()
            self._add_cell(
                cell_header,
                self.report_info[index][1],
                x=self._left_x,
                y=y,
                horizontal_distance=table_horizontal_distance,
                fixed_spacing=32,
            )
            y += table_vertical_distance
        return y

    def _add_laterality(self, y: int, scan: AltrisScan) -> int:
        """Add the laterality to the report.

        Args:
            y: The y-coordinate of the top left corner of the table.
            scan: The scan.
        """
        self.set_font("Inter", style="B", size=10)
        self.set_text_color(*BITFOUNT_BLUE)
        self.set_y(y)
        if scan.laterality in ["right", "r", "Right", "R"]:
            laterality = "Right eye"
        elif scan.laterality in ["left", "l", "Left", "L"]:
            laterality = "Left eye"
        else:
            # If nothing is found, still print a header
            laterality = "Eye Scans"
        self.multi_cell(w=40, h=5, text=laterality, border=False, align=Align.L)
        y += 6
        self.laterality_added = True
        return y

    def _summary_table(
        self, y: int, metric: Union[GAMetrics, GAMetricsWithFovea], scan: AltrisScan
    ) -> int:
        """Generate Summary table for the report.

        Args:
            y: The y-coordinate of the top left corner of the table.
            metric: The GA metrics.
            scan: The scan.
        """
        table_vertical_distance = 6
        table_horizontal_distance = 80
        y += 4
        self.set_y(y)
        y = self._add_laterality(y, scan)
        y += 2
        index = 0
        for key in SUMMARY_TABLE_KEYS:
            # Skip if the key is not in the metric
            if not hasattr(metric, key):
                continue
            if key == "subfoveal_indicator":
                if getattr(metric, key, None) is None:
                    continue
            if index % SUMMARY_TABLE_COLUMN_COUNT == 0:
                x = self._left_x
                fixed_spacing = 32

            else:
                x = self._left_x + table_horizontal_distance
                fixed_spacing = 42
            if index > 0 and index % SUMMARY_TABLE_COLUMN_COUNT == 0:
                y += table_vertical_distance
            if (
                key
                in (
                    "distance_from_fovea_centre",
                    "distance_from_image_centre",
                    "smallest_lesion_size",
                    "largest_lesion_size",
                    "subfoveal_indicator",
                )
                and metric.total_ga_area == 0
            ):
                self._add_cell(
                    GA_DICT_KEYS_TO_LABELS[key],
                    "N/A",
                    x=x,
                    y=y,
                    horizontal_distance=table_horizontal_distance,
                    fixed_spacing=fixed_spacing,
                )
            else:
                if key == "subfoveal_indicator":
                    # If the subfoveal lesion is not detected, we show "Not detected"
                    if getattr(metric, key, None) is None:
                        self._add_cell(
                            GA_DICT_KEYS_TO_LABELS[key],
                            "N/A",
                            x=x,
                            y=y,
                            horizontal_distance=table_horizontal_distance,
                            fixed_spacing=fixed_spacing,
                        )
                        index += 1
                        continue
                    else:
                        self._add_cell(
                            GA_DICT_KEYS_TO_LABELS[key],
                            str(getattr(metric, key)),
                            # ),
                            x=x,
                            y=y,
                            horizontal_distance=table_horizontal_distance,
                            fixed_spacing=fixed_spacing,
                        )
                else:
                    self._add_cell(
                        GA_DICT_KEYS_TO_LABELS[key],
                        (
                            str(round(float(getattr(metric, key)), 3))
                            + GA_METRICS_UNITS.get(key, "")
                            if getattr(metric, key, None) is not None
                            and not math.isnan(getattr(metric, key))
                            else "Not detected"
                        ),
                        x=x,
                        y=y,
                        horizontal_distance=table_horizontal_distance,
                        fixed_spacing=fixed_spacing,
                    )
            index += 1

        y += table_vertical_distance
        return y

    def _image_colour_legend(
        self, x: float, y: int, legend2color: dict[str, tuple[int, int, int]]
    ) -> None:
        """Draws the colour legend for the image.

        Args:
            x: x-coordinate of the top left corner of the legend.
            y: y-coordinate of the top left corner of the legend.
            legend2color: A dictionary mapping legend to colour.
        """
        self.set_font("Inter", size=8)
        self.set_text_color(*GREY)
        for legend, colour in legend2color.items():
            self.set_xy(x=x, y=y)
            width = 3
            colour_img = PIL.Image.new("RGB", (width, width), color=colour)
            self.image(name=colour_img, x=x, y=y, w=width)
            self.set_xy(x=x + width, y=y + 1)
            self.multi_cell(
                w=len(legend) * 2,
                h=width - 2,
                text=legend,
                border=False,
            )
            y += width * 2


def generate_pdf(
    file_name: Union[str, os.PathLike],
    report_info: AltrisRecordInfo,
    scans: Union[AltrisScan, list[AltrisScan]],
    metrics: Union[GAMetrics, list[GAMetrics]],
    total_ga_area_lower_bound: float = TOTAL_GA_AREA_LOWER_BOUND,
    total_ga_area_upper_bound: float = TOTAL_GA_AREA_UPPER_BOUND,
    task_id: Optional[str] = None,
) -> None:
    """Generates a PDF report.

    Args:
        file_name: The name of the file to save the report to.
        report_info: The report info.
        scans: The scans.
        metrics: The GA metrics.
        total_ga_area_lower_bound: The lower bound for the GA area. This is used to
            generate the slider. Defaults to 2.5.
        total_ga_area_upper_bound: The upper bound for the GA area. This is used to
            generate the slider. Defaults to 17.5.
        task_id: The task ID. Defaults to None.
    """
    pdf = ReportJade(
        report_info,
        scans,
        metrics,
        total_ga_area_lower_bound=total_ga_area_lower_bound,
        total_ga_area_upper_bound=total_ga_area_upper_bound,
        task_id=task_id,
    )
    pdf.generate()
    pdf.output(str(file_name))
