"""Base class and implementations for GA Trial PDF algorithms."""

from __future__ import annotations

from abc import ABC
from collections.abc import Iterable
import datetime
import json
import math
import os
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Mapping,
    Optional,
    Protocol,
    Union,
    cast,
    runtime_checkable,
)

import desert as desert
from marshmallow import fields
import numpy as np
import pandas as pd
import PIL

from bitfount import config
from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
)
from bitfount.data.datasources.dicom_source import DICOM_SCAN_LATERALITY_ATTRIBUTE
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.federated.algorithms.base import (
    BaseNonModelAlgorithmFactory,
    BaseWorkerAlgorithm,
    NoResultsModellerAlgorithm,
    T_WorkerSide,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    DATASOURCE_IMAGE_PREFIX_COLUMNS,
    ELIGIBILITY_COL,
    FILTER_MATCHING_COLUMN,
    GA_SEGMENTATION_LABELS,
    NAME_COL,
    NUMBER_OF_FRAMES_COLUMN,
    RESULTS_IMAGE_PREFIX,
    RESULTS_SUFFIX,
    TOTAL_GA_AREA_LOWER_BOUND,
    TOTAL_GA_AREA_UPPER_BOUND,
    GAMetrics,
    GAMetricsWithFovea,
    ReportMetadata,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_utils import (
    draw_segmentation_mask_on_orig_image,
    get_data_for_files,
    get_dataframe_iterator_from_datasource,
    is_file_iterable_source,
    parse_mask_json,
)
from bitfount.federated.algorithms.ophthalmology.trial_inclusion_filters import (
    ColumnFilter,
)
from bitfount.federated.exceptions import AlgorithmError, DataProcessingError
from bitfount.federated.logging import _get_federated_logger
from bitfount.models.types import (
    AltrisBiomarkerEntry,
    AltrisBiomarkerOutput,
    AltrisGASegmentationModelEntry,
    AltrisGASegmentationModelPostV11Output,
    AltrisGASegmentationModelPreV11Output,
    MaskAltrisBiomarker,
    MaskSegmentationModel,
)
from bitfount.utils.pandas_utils import dataframe_iterable_join
from bitfount.visualisation.ga_trial_pdf_jade import (
    AltrisRecordInfo,
    AltrisScan,
    generate_pdf,
)

if TYPE_CHECKING:
    from bitfount.federated.privacy.differential import DPPodConfig
    from bitfount.types import T_FIELDS_DICT

logger = _get_federated_logger("bitfount.federated")

# Constants used by both classes
ELIGIBLE_PATIENTS = "Eligible"
NON_ELIGIBLE_PATIENTS = "Not-eligible"


@runtime_checkable
class PDFGeneratorRunProtocol(Protocol):
    """Protocol defining the run method for PDF generators."""

    def run(
        self,
        *,
        results_df: pd.DataFrame,
        ga_dict: Any,  # Use Any to accommodate both signatures
        task_id: Optional[str] = None,
        filenames: Optional[list[str]] = None,
        **kwargs: Any,  # Use **kwargs to handle additional parameters
    ) -> pd.DataFrame:
        """Generate PDF reports for the GA model results."""
        ...


class _BasePDFWorkerSide(BaseWorkerAlgorithm):
    """Base worker side implementation for GA Trial PDF algorithms."""

    def __init__(
        self,
        *,
        path: Union[str, os.PathLike],
        report_metadata: ReportMetadata,
        filename_prefix: Optional[str] = None,
        filter: Optional[list[ColumnFilter]] = None,
        pdf_filename_columns: Optional[list[str]] = None,
        total_ga_area_lower_bound: float = TOTAL_GA_AREA_LOWER_BOUND,
        total_ga_area_upper_bound: float = TOTAL_GA_AREA_UPPER_BOUND,
        trial_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.report_metadata = report_metadata
        self.filter = filter
        self.path = Path(path)
        self.pdf_filename_columns: list[str] = (
            pdf_filename_columns if pdf_filename_columns is not None else [NAME_COL]
        )
        self.filename_prefix = filename_prefix
        self.total_ga_area_lower_bound = total_ga_area_lower_bound
        self.total_ga_area_upper_bound = total_ga_area_upper_bound
        self.trial_name = trial_name

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
        if not pod_identifier:
            raise ValueError("Pod_identifier must be provided.")

    def set_column_filters(self, filters: list[ColumnFilter]) -> None:
        """Sets the column filters for the worker.

        If filters already exist, the new filters will be appended to the existing ones.
        """
        if self.filter is None:
            self.filter = filters
        else:
            self.filter.extend(filters)

    def _get_ga_metric_from_dictionary(
        self,
        ga_dict: Mapping[str, Optional[Union[GAMetrics, GAMetricsWithFovea]]],
        original_filename: str,
    ) -> Optional[Union[GAMetrics, GAMetricsWithFovea]]:
        """Get the GA metrics from the dictionary from the original filename."""
        try:
            return ga_dict[original_filename]
        except KeyError:
            return None

    def _get_record_info(self, datasource_row: pd.Series) -> AltrisRecordInfo:
        """Extract required text fields for report."""
        # For each of the text fields we need the value to be a string
        record_info_text_fields: list[tuple[str, str]] = []
        if self.report_metadata.text_fields is not None:
            for text_field in self.report_metadata.text_fields:
                # Get the field's value in the appropriate format
                field_value: str

                # If the record metadata just references an explicit value, use that
                if text_field.value:
                    field_value = text_field.value
                # Otherwise, it will be referencing data stored in a column
                else:
                    # Post_init check verifies that one of `column` or `value` is set.
                    # If `value` is not set, then `column` must be set.
                    text_field.column = cast(str, text_field.column)

                    # Apply various parsing attempts to the column value to try and
                    # get it in the most meaningful format.
                    # The parsing is attempted in the following order:
                    #   - DateTime
                    #   - Date
                    #   - float
                    #   - int
                    #   - raw

                    if (
                        text_field.column == "Eligibility"
                        and text_field.column not in datasource_row
                    ):
                        datasource_row = self._add_eligibility(datasource_row)

                    try:
                        datasource_entry: Union[
                            datetime.datetime, datetime.date, float, int, str
                        ] = datasource_row[text_field.column]

                        # If NaN, NaT
                        if pd.isna(datasource_entry):
                            field_value = "Not found"  # type: ignore[unreachable] # Reason: entry could always be NaN so need to handle that case, even if not represented in typing # noqa: E501
                            continue

                        # Parse DateTime fields
                        if isinstance(datasource_entry, datetime.datetime):
                            # Find the explicit format, or use default
                            if text_field.datetime_format:
                                dt_format = text_field.datetime_format
                            else:
                                dt_format = "%Y-%m-%d %H:%M:%S.%f"

                            field_value = datasource_entry.strftime(dt_format)

                        # Parse Date fields
                        elif isinstance(datasource_entry, datetime.date):
                            # Find the explicit format, or use default
                            if text_field.datetime_format:
                                date_format = text_field.datetime_format
                            else:
                                date_format = "%Y-%m-%d"

                            field_value = datasource_entry.strftime(date_format)

                        # Parse float fields - round to two DP
                        elif isinstance(datasource_entry, float):
                            field_value = str(round(datasource_entry, 2))

                        # Parse int fields
                        elif isinstance(datasource_entry, int):
                            field_value = str(datasource_entry)

                        # Parse anything else as raw
                        else:
                            field_value = str(datasource_entry)
                    except (KeyError, ValueError, TypeError) as e:
                        logger.info(f"Error getting field {text_field}: {e}")
                        field_value = "Not found"

                record_info_text_fields.append((text_field.heading, field_value))

        return AltrisRecordInfo(
            text_fields=record_info_text_fields,
            heading=self.report_metadata.heading,
        )

    def _add_eligibility(self, datasource_row: pd.Series) -> pd.Series:
        if (
            "Eligibility" not in datasource_row
            and FILTER_MATCHING_COLUMN in datasource_row
        ):
            if datasource_row[FILTER_MATCHING_COLUMN] is True:
                datasource_row["Eligibility"] = "Eligible"
            elif datasource_row[FILTER_MATCHING_COLUMN] is False:
                datasource_row["Eligibility"] = "Not Eligible"
            else:
                datasource_row["Eligibility"] = datasource_row[FILTER_MATCHING_COLUMN]
        return datasource_row

    def _get_scan(
        self,
        datasource_row: pd.Series,
        results_df: pd.DataFrame,
        idx: pd.Index,
        bscan_idx: Optional[int],
    ) -> AltrisScan:
        """Get the scans from the datasource row and the results dataframe."""
        # Extract images and metadata about the images
        if NUMBER_OF_FRAMES_COLUMN in datasource_row.index:
            total_frames = datasource_row[NUMBER_OF_FRAMES_COLUMN]
            middle_frame_idx = int(math.floor(total_frames // 2))
        else:
            # We assume that there is only one frame
            total_frames = 1
            middle_frame_idx = 0

        # If the total GA area is 0, then we set the bscan_idx to the middle frame
        if bscan_idx is None:
            bscan_idx = middle_frame_idx

        frame = datasource_row[f"{DATASOURCE_IMAGE_PREFIX_COLUMNS} {bscan_idx}"]
        # TODO: [NO_TICKET: Imported from ophthalmology] Revisit for the protocol
        #       after matching
        # Try to parse mask from results
        try:
            # Ensure that the bscan prediction is in the right form for
            # `json.loads()`
            bscan_prediction_str = str(
                results_df.loc[idx][
                    f"{RESULTS_IMAGE_PREFIX}_{bscan_idx}{RESULTS_SUFFIX}"
                ]
            )
            bscan_prediction_str = bscan_prediction_str.replace("'", '"')

            # Load model output JSON
            prediction_output_json: (
                AltrisBiomarkerEntry | AltrisGASegmentationModelEntry
            )
            try:
                # Older AltrisGASegmentationModel versions return a list of lists
                loaded_json_pre_v11: AltrisGASegmentationModelPreV11Output = json.loads(
                    bscan_prediction_str
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

            mask_json: MaskAltrisBiomarker | MaskSegmentationModel = (
                prediction_output_json["mask"]
            )
            mask = parse_mask_json(mask_json, GA_SEGMENTATION_LABELS)
        except Exception as e:
            # if mask is not found in the results_df, then we create an empty mask
            logger.error(
                "Error parsing mask for "
                f"{datasource_row[ORIGINAL_FILENAME_METADATA_COLUMN]}. Skipping"
            )
            logger.debug(f"Error details: {e}", exc_info=True)
            mask = np.zeros((1, 1, 1))

        # PDF algorithm is only compatible with fileiterable sources
        if not isinstance(self.datasource, FileSystemIterableSource):
            raise AlgorithmError(
                f"Datasource supplied is not an instance of FileSystemIterableSource."
                f" Supplied datasource {type(self.datasource).__name__}"
                f" is incompatible with current PDF algorithm."
            )

        # If filepaths are not cached, then we get image from numpy array
        orig_bscan = PIL.Image.fromarray(frame)

        # Get the laterality of the scan
        try:
            laterality = datasource_row[DICOM_SCAN_LATERALITY_ATTRIBUTE]
        except KeyError:
            laterality = None

        img_w_mask, legend2color = draw_segmentation_mask_on_orig_image(
            mask, orig_bscan
        )
        scan = AltrisScan(
            bscan_image=orig_bscan,
            bscan_idx=bscan_idx,
            bscan_total=total_frames,
            bscan_w_mask=img_w_mask,
            legend2color=legend2color,
            laterality=laterality,
        )
        return scan

    def _get_pdf_output_path(
        self,
        orig_filename: Path,
        row: pd.Series,
        task_id: Optional[str],
        eligibility: Optional[str] = None,
    ) -> tuple[Path, str]:
        """Get the output path to save report PDF to."""
        pdf_filename_extension = ".pdf"
        filename_prefix = f"{self.filename_prefix}-" if self.filename_prefix else ""
        filename_prefix = (
            f"{filename_prefix}{eligibility}-"
            if eligibility is not None
            else filename_prefix
        )
        filename_prefix = (
            f"{filename_prefix}{self.trial_name}"
            if self.trial_name is not None
            else filename_prefix
        )

        # Extract the values from the columns for the pdf name.
        pdf_filename = filename_prefix
        for col in self.pdf_filename_columns:
            try:
                pdf_filename = pdf_filename + "-" + str(row[col])
            except KeyError:
                logger.warning(
                    f"Column {col} not found in the data. "
                    "Skipping this column for the PDF filename."
                )
                continue

        # If no columns are found in the data, then save the
        # pdf under original filename stem
        if pdf_filename == filename_prefix:
            logger.warning(
                "Column values for PDF filename are empty. "
                "Saving pdf under original filename."
            )
            pdf_filename = (
                f"{filename_prefix}-{orig_filename.stem}{pdf_filename_extension}"
            )
        else:
            pdf_filename = f"{pdf_filename}{pdf_filename_extension}"

        if task_id is not None:
            Path(self.path / f"{task_id}").mkdir(parents=True, exist_ok=True)
            pdf_path = self.path / f"{task_id}" / pdf_filename
        else:
            Path(self.path).mkdir(parents=True, exist_ok=True)
            pdf_path = self.path / pdf_filename

        # If the filename already exists, then add a version suffix to the filename
        original_stem = pdf_path.stem
        i = 1
        while pdf_path.exists():
            pdf_path = pdf_path.with_name(f"{original_stem} ({i}){pdf_path.suffix}")
            i += 1

        return pdf_path, original_stem

    def _generate_pdf_for_datasource_row(
        self,
        datasource_row: pd.Series,
        results_df: pd.DataFrame,
        index: pd.Index,
        ga_metrics: Union[GAMetrics, GAMetricsWithFovea],
        task_id: Optional[str],
        original_filename: str,
        pdf_output_paths: list[tuple[str, Optional[Path]]],
        eligibility: Optional[str] = None,
    ) -> list[tuple[str, Optional[Path]]]:
        """Generate PDF report for a single entry."""
        scan = self._get_scan(
            datasource_row,
            results_df,
            index,
            bscan_idx=ga_metrics.max_ga_bscan_index,
        )
        record_info = self._get_record_info(datasource_row)
        # TODO: [NO_TICKET: Imported from ophthalmology] Matching of
        #       same patient eye
        # Get the output path for the PDF report
        (
            pdf_output_path,
            _,
        ) = self._get_pdf_output_path(
            Path(original_filename),
            datasource_row,
            task_id,
            eligibility,
        )
        # Generate the PDF report and return whether generation was successful
        success = self._generate_pdf_for_entry(
            pdf_output_path=pdf_output_path,
            record_info=record_info,
            scan=scan,
            ga_metrics=ga_metrics,
            total_ga_area_lower_bound=self.total_ga_area_lower_bound,
            total_ga_area_upper_bound=self.total_ga_area_upper_bound,
            task_id=task_id,
            original_filename=original_filename,
            pdf_output_paths=pdf_output_paths,
        )
        if success:
            pdf_output_paths.append(
                (
                    original_filename,
                    pdf_output_path,
                )
            )
        return pdf_output_paths

    def _append_results_to_orig_data(
        self,
        results_df: pd.DataFrame,
        test_data_dfs: Iterable[pd.DataFrame],
        filenames: Optional[list[str]] = None,
    ) -> Iterable[pd.DataFrame]:
        # Append the results to the original data
        # Merge the test data Dataframes and results dataframes.
        # The manner in which they are merged depends on if the data is keyed or not
        # (i.e. if we have filenames)
        logger.debug("Appending results to the original data.")
        if filenames:
            test_data_dfs = cast(list[pd.DataFrame], test_data_dfs)

            # Check that both dataframes have the required key column
            if ORIGINAL_FILENAME_METADATA_COLUMN not in test_data_dfs[0].columns:
                raise ValueError(
                    f"Retrieved file data dataframe is missing"
                    f" the required key column: {ORIGINAL_FILENAME_METADATA_COLUMN}"
                )
            if ORIGINAL_FILENAME_METADATA_COLUMN not in results_df.columns:
                raise ValueError(
                    f"Results dataframe is missing"
                    f" the required key column: {ORIGINAL_FILENAME_METADATA_COLUMN}"
                )

            test_data_dfs = [
                test_data_dfs[0].merge(results_df, on=ORIGINAL_FILENAME_METADATA_COLUMN)
            ]
        else:
            logger.warning(
                "Joining results and original data iteratively;"
                " data must be provided in the same order in both"
            )
            test_data_dfs = dataframe_iterable_join(test_data_dfs, results_df)
        return test_data_dfs

    def _get_test_data_from_data_source(
        self, metrics_df: pd.DataFrame, filenames: Optional[list[str]]
    ) -> Iterable[pd.DataFrame]:
        """Extract test data from datasource by joining with predictions."""
        # First, we need to extract the appropriate data from the datasource by
        # combining it with the predictions supplied (i.e. joining on the identifiers).
        test_data_dfs: Iterable[pd.DataFrame]
        if filenames and is_file_iterable_source(self.datasource):
            logger.debug(f"Retrieving data for: {filenames}")
            # use_cache is False as we need the image data
            # to produce the images in the PDF
            df: pd.DataFrame = get_data_for_files(
                cast(FileSystemIterableSource, self.datasource),
                filenames,
                use_cache=False,
            )
            # Merge the metrics with the data
            df = df.merge(metrics_df, on=ORIGINAL_FILENAME_METADATA_COLUMN)

            test_data_dfs = [df]

            # Check that we have the expected number of results for the number of files
            if len(filenames) != len(test_data_dfs[0]):
                raise DataProcessingError(
                    f"Length of results ({len(test_data_dfs[0])}"
                    f" does not match the number of files ({len(filenames)})"
                    f" while processing PDF report."
                )
        else:
            logger.warning(
                "Iterating over all files to find results<->file match;"
                " this may take a long time."
            )
            # use_cache is False as we need the image data to produce the images
            # in the PDF
            test_data_dfs = get_dataframe_iterator_from_datasource(
                self.datasource, data_splitter=self.data_splitter, use_cache=False
            )
        return test_data_dfs

    def _generate_pdf_for_entry(
        self,
        pdf_output_path: Path,
        record_info: AltrisRecordInfo,
        scan: AltrisScan,
        ga_metrics: Union[GAMetrics, GAMetricsWithFovea],
        total_ga_area_lower_bound: float,
        total_ga_area_upper_bound: float,
        task_id: Optional[str],
        original_filename: str,
        pdf_output_paths: list[tuple[str, Optional[Path]]],
        eligibility: Optional[str] = None,
    ) -> bool:
        """Generate PDF report for a single entry."""
        try:
            # Show the debug logs time taken to generate the pdf
            start = datetime.datetime.now()
            if eligibility is not None:
                record_info.text_fields.insert(0, (ELIGIBILITY_COL, eligibility))
            generate_pdf(
                pdf_output_path,
                record_info,
                scan,
                ga_metrics,
                total_ga_area_lower_bound=total_ga_area_lower_bound,
                total_ga_area_upper_bound=total_ga_area_upper_bound,
                task_id=task_id,
            )

            end = datetime.datetime.now()
            logger.debug(
                f"Generated PDF {str(pdf_output_path)}"
                f" in {(end - start).total_seconds()} seconds"
            )
            return True
        except Exception as e:
            logger.error(
                f"Error generating PDF report for {original_filename}. Skipping"
            )
            pdf_output_paths.append((original_filename, None))
            logger.debug(e, exc_info=True)
            return False


class BaseGATrialPDFGeneratorAlgorithm(
    BaseNonModelAlgorithmFactory[NoResultsModellerAlgorithm, T_WorkerSide], ABC
):
    """Base algorithm factory for GA Trial PDF report generation.

    Args:
        datastructure: The data structure to use for the algorithm.
        report_metadata: A ReportMetadata for the pdf report metadata fields.
        filter: A list of ColumnFilter objects to filter the data by.
        save_path: The folder path where the pdf report should be saved.
        filename_prefix: The prefix for the pdf filename. Defaults to None.
        pdf_filename_columns: The columns from the datasource that should
             be used for the pdf filename. If not provided, the filename will
             be saved as "Patient_index_i.pdf" where `i` is the index in the
             filtered datasource. Defaults to None.
        total_ga_area_lower_bound: The lower bound for the total GA area.
            Defaults to 2.5.
        total_ga_area_upper_bound: The upper bound for the total GA area.
            Defaults to 17.5.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "report_metadata": fields.Nested(desert.schema_class(ReportMetadata)),
        "filter": fields.Nested(
            desert.schema_class(ColumnFilter), many=True, allow_none=True
        ),
        "save_path": fields.Str(),
        "filename_prefix": fields.Str(allow_none=True),
        "pdf_filename_columns": fields.List(fields.Str(), allow_none=True),
        "total_ga_area_lower_bound": fields.Float(allow_none=True),
        "total_ga_area_upper_bound": fields.Float(allow_none=True),
        "trial_name": fields.Str(allow_none=True),
    }

    def __init__(
        self,
        *,
        datastructure: DataStructure,
        report_metadata: ReportMetadata,
        filter: Optional[list[ColumnFilter]] = None,
        save_path: Optional[Union[str, os.PathLike]] = None,
        filename_prefix: Optional[str] = None,
        pdf_filename_columns: Optional[list[str]] = None,
        total_ga_area_lower_bound: float = TOTAL_GA_AREA_LOWER_BOUND,
        total_ga_area_upper_bound: float = TOTAL_GA_AREA_UPPER_BOUND,
        trial_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.save_path: Path
        if save_path is None:
            self.save_path = config.settings.paths.output_dir
        else:
            self.save_path = Path(save_path)
        self.filter = filter
        self.report_metadata = report_metadata
        self.filename_prefix = filename_prefix
        self.pdf_filename_columns = pdf_filename_columns
        self.total_ga_area_lower_bound = total_ga_area_lower_bound
        self.total_ga_area_upper_bound = total_ga_area_upper_bound
        self.trial_name = trial_name
        super().__init__(datastructure=datastructure, **kwargs)

    def modeller(self, **kwargs: Any) -> NoResultsModellerAlgorithm:
        """Modeller-side of the algorithm."""
        return NoResultsModellerAlgorithm(
            log_message="Running GA Trial PDF Generator Algorithm",
            **kwargs,
        )
