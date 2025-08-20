"""Algorithm for computing ETDRS subfields.

Not currently used in the project but may be useful in the future.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Union, cast

import desert
from marshmallow import fields
import numpy as np
import pandas as pd
from PIL import Image

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
    OCTImageMetadataColumns,
    SLOImageMetadataColumns,
    SLOSegmentationLocationPrefix,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_utils import (
    get_data_for_files,
    get_dataframe_iterator_from_datasource,
    get_imgs_with_segmentation_from_enface_slo,
    is_file_iterable_source,
)
from bitfount.federated.exceptions import DataProcessingError
from bitfount.federated.logging import _get_federated_logger
from bitfount.metrics.etdrs import compute_subfields, compute_subfields_oct
from bitfount.metrics.types import Laterality
from bitfount.visualisation.utils import overlay_with_alpha_layer

if TYPE_CHECKING:
    from PIL.Image import Image as Image_T

    from bitfount.federated.privacy.differential import DPPodConfig
    from bitfount.metrics.types import Coordinates, MaculaSubFields
    from bitfount.types import T_FIELDS_DICT

logger = _get_federated_logger("bitfount.federated")


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side of the algorithm."""

    def __init__(
        self,
        laterality: str,
        slo_photo_location_prefixes: Optional[SLOSegmentationLocationPrefix] = None,
        slo_image_metadata_columns: Optional[SLOImageMetadataColumns] = None,
        oct_image_metadata_columns: Optional[OCTImageMetadataColumns] = None,
        threshold: float = 0.7,
        calculate_on_oct: bool = False,
        slo_mm_width: float = 8.8,
        slo_mm_height: float = 8.8,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.slo_photo_location_prefixes = slo_photo_location_prefixes
        self.slo_image_metadata_columns = slo_image_metadata_columns
        self.oct_image_metadata_columns = oct_image_metadata_columns
        self.threshold = threshold
        self.laterality = laterality
        self.calculate_on_oct = calculate_on_oct
        self.slo_mm_width = slo_mm_width
        self.slo_mm_height = slo_mm_height

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
        predictions: list[np.ndarray],
        fovea_coordinates: Optional[list[Coordinates]] = None,
        fovea_idxs: Optional[Sequence[int]] = None,
        filenames: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """Run the algorithm to compute ETDRS subfields from the predictions.

        Args:
            predictions: The predictions from model inference. If `filenames` is
                provided, these must be ordered the same as filenames.
            fovea_coordinates: The coordinates of the fovea in each image. If this
                is provided and `filenames` is provided, the order must be the same.
            fovea_idxs: The indices of the images which contain the fovea in each
                set of images. If this is provided and `filenames` is provided,
                the order must be the same.
            filenames: The list of files that the results correspond to. If not
                provided, will iterate through all files in the dataset to find
                the corresponding ones.

        Returns:
            A dataframe of the ETDRS calculations for each set of predictions. If
            `filenames` is provided, this dataframe will contain an
            "_original_filename" column to map each row to the file.
        """
        # First, we need to extract the appropriate data from the datasource by
        # combining it with the predictions and fovea coordinates supplied (i.e.
        # joining on the identifiers).
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
                    f" while computing ETDRS subfields."
                )
        else:
            logger.warning(
                "Iterating over all files to find prediction/fovea coords<->file match;"
                " this may take a long time."
            )
            test_data_dfs = get_dataframe_iterator_from_datasource(
                self.datasource, self.data_splitter
            )

        # GA Model outputs a list of 4 predictions arrays, extract these into
        # meaningful variables
        if len(predictions) == 4:
            bscans: np.ndarray = predictions[0]
            binarised_predictions: np.ndarray = predictions[1]
            enface_output: np.ndarray = predictions[2]
            # GA Model returns a 0-dim array for `slos` if slo is set to false
            slos: np.ndarray = predictions[3]
        else:
            raise ValueError("Cannot compute ETDRS from model predictions.")

        # Check that we have the expected number of results for the number of files
        if filenames:
            if len(filenames) != len(bscans):
                raise DataProcessingError(
                    f"Length of bscans ({len(bscans)}"
                    f" does not match the number of files ({len(filenames)})"
                    f" while computing ETDRS."
                )
            if len(filenames) != len(binarised_predictions):
                raise DataProcessingError(
                    f"Length of binarised_predictions ({len(binarised_predictions)}"
                    f" does not match the number of files ({len(filenames)})"
                    f" while computing ETDRS."
                )
            if len(filenames) != len(enface_output):
                raise DataProcessingError(
                    f"Length of enface_output ({len(enface_output)}"
                    f" does not match the number of files ({len(filenames)})"
                    f" while computing ETDRS."
                )
            # GA Model returns a 0-dim array for `slos` if slo is set to false
            if slos.ndim != 0:
                if len(filenames) != len(slos):
                    raise DataProcessingError(
                        f"Length of slos ({len(slos)}"
                        f" does not match the number of files ({len(filenames)})"
                        f" while computing ETDRS."
                    )

        predictions_idx: int = 0
        etdrs: list[MaculaSubFields] = []
        for test_data in test_data_dfs:
            # We need a column that matches the laterality associated with this
            # algorithm, otherwise we cannot proceed
            if self.laterality not in test_data.columns:
                raise ValueError(
                    "Datasource missing laterality column "
                    f"'{self.laterality}'. Cannot compute ETDRS."
                )

            # Extract prediction information relevant to this chunk of the data
            len_curr_data = len(test_data)
            end_predictions_idx = predictions_idx + len_curr_data

            bscans_curr = bscans[predictions_idx:end_predictions_idx]
            binarised_predictions_curr = binarised_predictions[
                predictions_idx:end_predictions_idx
            ]
            enface_output_curr = enface_output[predictions_idx:end_predictions_idx]
            # GA Model returns a 0-dim array for `slos` if slo is set to false
            if slos.ndim != 0:
                slos_curr = slos[predictions_idx:end_predictions_idx]
            else:
                slos_curr = None

            fovea_coordinates_curr: Optional[list[Coordinates]] = (
                fovea_coordinates[predictions_idx:end_predictions_idx]
                if fovea_coordinates is not None
                else None
            )
            fovea_idxs_curr: Optional[Sequence[int]] = (
                fovea_idxs[predictions_idx:end_predictions_idx]
                if fovea_idxs is not None
                else None
            )

            predictions_idx = end_predictions_idx

            # Determine processing path to take, depending on if we are working
            # with SLOs or OCTs
            etdrs_curr: list[MaculaSubFields]
            if slos_curr is not None and not self.calculate_on_oct:
                etdrs_curr = self._etdrs_from_slos(
                    test_data,
                    enface_output_curr,
                    slos_curr,
                    fovea_coordinates_curr,
                )
            elif self.oct_image_metadata_columns is not None:
                etdrs_curr = self._etdrs_from_octs(
                    test_data,
                    bscans_curr,
                    binarised_predictions_curr,
                    fovea_coordinates_curr,
                    fovea_idxs_curr,
                    width_mm_column=self.oct_image_metadata_columns.width_mm_column,
                    depth_mm_column=self.oct_image_metadata_columns.depth_mm_column,
                )
            else:
                # if no slo for the model and no oct information provided
                raise ValueError(
                    "Cannot compute ETDRS from the OCT image only without"
                    " column metadata."
                )
            etdrs.extend(etdrs_curr)

        # TODO: [BIT-3486] As this list/dataframe can contain entries for every
        #       element in the datasource, it may be too large to process in memory.
        #       Consider switching this to be a Generator for output.
        #       Workaround is to use batch_execution to constrain input size to
        #       each pass.
        df = pd.json_normalize(etdrs)  # type: ignore[arg-type] # reason: MaculaSubFields is a TypedDict # noqa: E501

        # If we have the filenames for these, append them to the dataframe
        if filenames:
            if len(filenames) != len(df):
                raise ValueError(
                    f"Mismatch in number of calculated results and filenames;"
                    f" got {len(df)} ETDRS calculations,"
                    f" but {len(filenames)} filenames"
                )
            df[ORIGINAL_FILENAME_METADATA_COLUMN] = filenames

        # NOTE: The orders of these should match the input order of the predictions,
        # even if the filenames are not appended
        return df

    def _etdrs_from_slos(
        self,
        slo_data: pd.DataFrame,
        enface_output: np.ndarray,
        slos: np.ndarray,
        fovea_coordinates: Optional[list[Coordinates]],
    ) -> list[MaculaSubFields]:
        """Compute ETDRS from SLO images."""
        etdrs: list[MaculaSubFields] = []

        imgs = get_imgs_with_segmentation_from_enface_slo(
            data=slo_data,
            enface_output=enface_output,
            slos=slos,
            slo_photo_location_prefixes=self.slo_photo_location_prefixes,
            slo_image_metadata_columns=self.slo_image_metadata_columns,
            threshold=self.threshold,
        )

        items: Union[Iterable[tuple[Image_T, Coordinates]], Iterable[Image_T]]
        if fovea_coordinates is not None:
            items = zip(
                imgs,
                fovea_coordinates,
            )
        else:
            items = imgs

        for row_index, item in enumerate(items):
            # mypy is unable to correctly establish complex types from enumerate(),
            # so we must reassure it here.
            #
            # See: https://github.com/python/mypy/issues/11934
            if TYPE_CHECKING:
                item = cast(Union[tuple[Image_T, Coordinates], Image_T], item)

            img_: Image_T
            fovea_coordinates_: Optional[Coordinates]
            if isinstance(item, tuple):
                img_, fovea_coordinates_ = item
            else:
                img_ = item
                fovea_coordinates_ = None

            laterality: Laterality = Laterality(slo_data[self.laterality][row_index])

            # Determine the SLO location and size, using either information in the
            # data or default location information
            if (
                self.slo_image_metadata_columns is not None
                and self.slo_image_metadata_columns.width_mm_column in slo_data.columns
                and self.slo_image_metadata_columns.height_mm_column in slo_data.columns
            ):
                slo_pixel_dim_width, slo_pixel_dim_height = img_.size
                slo_mm_width: float = round(
                    slo_data[self.slo_image_metadata_columns.width_mm_column].iloc[
                        row_index
                    ],
                    2,
                )
                slo_mm_height: float = round(
                    slo_data[self.slo_image_metadata_columns.height_mm_column].iloc[
                        row_index
                    ],
                    2,
                )
            else:
                logger.warning("Calculating ETDRS from default locations and sizes.")
                slo_pixel_dim_width, slo_pixel_dim_height = img_.size
                slo_mm_width = self.slo_mm_width
                slo_mm_height = self.slo_mm_height

            img_array = np.array(img_)

            etdrs_subfields = compute_subfields(
                img_array=img_array,
                laterality=laterality,
                slo_num_pixels_height=slo_pixel_dim_height,
                slo_num_pixels_width=slo_pixel_dim_width,
                slo_dimension_mm_width=slo_mm_width,
                slo_dimension_mm_height=slo_mm_height,
                fovea_coordinates=fovea_coordinates_,
            )
            etdrs.append(etdrs_subfields)
        return etdrs

    def _etdrs_from_octs(
        self,
        data: pd.DataFrame,
        bscans: np.ndarray,
        binarised_predictions: np.ndarray,
        fovea_coordinates: Optional[list[Coordinates]],
        fovea_idxs: Optional[Sequence[int]],
        width_mm_column: str,
        depth_mm_column: str,
    ) -> list[MaculaSubFields]:
        """Compute ETDRS from OCT images."""
        etdrs = []

        items: Union[np.ndarray, Iterable[tuple[np.ndarray, Coordinates]]]
        if fovea_coordinates is not None:
            items = zip(
                bscans,
                fovea_coordinates,
            )
        else:
            items = bscans

        for row_index, item in enumerate(items):
            laterality: Laterality = Laterality(data[self.laterality][row_index])
            try:
                oct_width_mm: float = data[width_mm_column].iloc[row_index]
                oct_depth_mm: float = data[depth_mm_column].iloc[row_index]
            except KeyError as e:
                raise KeyError(
                    "Datasource missing provided OCT image metadata columns: "
                    f"{e}. Cannot compute ETDRS."
                ) from e

            bscan_3d: np.ndarray
            fovea_coordinates_: Optional[Coordinates]
            if isinstance(item, tuple):
                bscan_3d, fovea_coordinates_ = item
            else:
                bscan_3d = item
                fovea_coordinates_ = None

            fovea_idx: int
            bscan: np.ndarray
            if fovea_idxs is not None:
                fovea_idx = fovea_idxs[row_index]
                bscan = bscan_3d[fovea_idx]
            else:
                # take the middle image
                fovea_idx = int(bscan_3d.shape[0] / 2)
                bscan = bscan_3d[fovea_idx]

            bscan_w_alpha: Image_T = overlay_with_alpha_layer(
                Image.fromarray(bscan),
                binarised_predictions[row_index][fovea_idx].squeeze(),
            )
            oct_pixel_dim_height, oct_pixel_dim_width = bscan_w_alpha.size

            etdrs_subfields = compute_subfields_oct(
                img_array=np.array(bscan_w_alpha),
                laterality=laterality,
                oct_width_mm=oct_width_mm,
                oct_depth_mm=oct_depth_mm,
                oct_num_pixels_width=oct_pixel_dim_width,
                oct_num_pixels_height=oct_pixel_dim_height,
                fovea_coordinates=fovea_coordinates_,
            )
            etdrs.append(etdrs_subfields)
        return etdrs


class ETDRSAlgorithm(
    BaseNonModelAlgorithmFactory[NoResultsModellerAlgorithm, _WorkerSide]
):
    """Algorithm for computing ETDRS subfields.

    Args:
        datastructure: The data structure to use for the algorithm.
        laterality: The column name of the column that contains the
            laterality of the scans.
        oct_image_metadata_columns: A list of column names for the OCT image.
            Should include the width and depth size in mm. Defaults to None.
        slo_photo_location_prefixes: The list of column names for the locations
             of the OCT segmentation on the SLO. Should include the
            location and end of the first image on both x and y-axis
            as well as the start location of the last image on both
            x and y-axis. Defaults to None.
        slo_image_metadata_columns: A list of column names for the SLO image.
            Should include the width and height in mm. Defaults to None.
        threshold: The threshold for the segmentation. Defaults to None.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "laterality": fields.Str(),
        "threshold": fields.Float(allow_none=True, default=0.7),
        "calculate_on_oct": fields.Bool(allow_none=True),
        "slo_mm_width": fields.Float(allow_none=True, default=8.8),
        "slo_mm_height": fields.Float(allow_none=True, default=8.8),
        "slo_photo_location_prefixes": fields.Nested(
            desert.schema_class(SLOSegmentationLocationPrefix), allow_none=True
        ),
        "slo_image_metadata_columns": fields.Nested(
            desert.schema_class(SLOImageMetadataColumns), allow_none=True
        ),
        "oct_image_metadata_columns": fields.Nested(
            desert.schema_class(OCTImageMetadataColumns), allow_none=True
        ),
    }

    def __init__(
        self,
        datastructure: DataStructure,
        laterality: str,
        slo_photo_location_prefixes: Optional[SLOSegmentationLocationPrefix] = None,
        slo_image_metadata_columns: Optional[SLOImageMetadataColumns] = None,
        oct_image_metadata_columns: Optional[OCTImageMetadataColumns] = None,
        threshold: float = 0.7,
        calculate_on_oct: bool = False,
        slo_mm_width: float = 8.8,
        slo_mm_height: float = 8.8,
        **kwargs: Any,
    ) -> None:
        self.laterality = laterality
        self.slo_photo_location_prefixes = slo_photo_location_prefixes
        self.slo_image_metadata_columns = slo_image_metadata_columns
        self.oct_image_metadata_columns = oct_image_metadata_columns
        self.threshold = threshold
        self.calculate_on_oct = calculate_on_oct
        self.slo_mm_width = slo_mm_width
        self.slo_mm_height = slo_mm_height

        super().__init__(datastructure=datastructure, **kwargs)

    def modeller(self, **kwargs: Any) -> NoResultsModellerAlgorithm:
        """Modeller-side of the algorithm."""
        return NoResultsModellerAlgorithm(
            log_message="Running ETDRS calculation algorithm.",
            **kwargs,
        )

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Worker-side of the algorithm."""
        return _WorkerSide(
            laterality=self.laterality,
            slo_photo_location_prefixes=self.slo_photo_location_prefixes,
            slo_image_metadata_columns=self.slo_image_metadata_columns,
            oct_image_metadata_columns=self.oct_image_metadata_columns,
            threshold=self.threshold,
            calculate_on_oct=self.calculate_on_oct,
            slo_mm_width=self.slo_mm_width,
            slo_mm_height=self.slo_mm_height,
            **kwargs,
        )
