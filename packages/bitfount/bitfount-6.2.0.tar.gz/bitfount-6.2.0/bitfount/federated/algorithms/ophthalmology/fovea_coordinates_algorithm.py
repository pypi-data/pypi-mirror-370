"""Computes the Fovea coordinates from the Fovea detection model predictions.

Not currently used in the project but may be useful in the future.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict
from typing import TYPE_CHECKING, Any, ClassVar, Optional, cast

import desert
from marshmallow import fields
import numpy as np
import pandas as pd

from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
)
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.federated.algorithms.base import (
    BaseNonModelAlgorithmFactory,
    BaseWorkerAlgorithm,
    NoResultsModellerAlgorithm,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    SLOSegmentationLocationPrefix,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_utils import (
    get_data_for_files,
    get_dataframe_iterator_from_datasource,
    is_file_iterable_source,
)
from bitfount.federated.exceptions import DataProcessingError
from bitfount.federated.logging import _get_federated_logger
from bitfount.metrics.types import Coordinates
from bitfount.visualisation.utils import get_fovea_planar_coords

if TYPE_CHECKING:
    from bitfount.federated.privacy.differential import DPPodConfig
    from bitfount.types import T_FIELDS_DICT


logger = _get_federated_logger("bitfount.federated")


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side of the algorithm."""

    def __init__(
        self,
        bscans_width_col: str,
        location_prefixes: Optional[SLOSegmentationLocationPrefix] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.bscans_width_col = bscans_width_col
        self.location_prefixes = (
            location_prefixes if location_prefixes else SLOSegmentationLocationPrefix()
        )

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
        filenames: Optional[list[str]] = None,
    ) -> tuple[list[int], list[Coordinates]]:
        """Computes the Fovea coordinates from the Fovea detection model predictions.

        Args:
            predictions: The predictions from model inference. If `filenames` is
                provided, these must be ordered the same as filenames.
            filenames: The list of files that the results correspond to. If not
                provided, will iterate through all files in the dataset to find
                the corresponding ones.
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
                    f"Length of results ({len(test_data_dfs[0])}"
                    f" does not match the number of files ({len(filenames)})"
                    f" while processing fovea coordinates."
                )
        else:
            logger.warning(
                "Iterating over all files to find prediction<->file match;"
                " this may take a long time."
            )
            test_data_dfs = get_dataframe_iterator_from_datasource(
                self.datasource, self.data_splitter
            )

        # predictions from fovea model are a list with one numpy array
        # They are in the form: index, x, y, probability, where:
        # index, x = self.max_pixel(np.max(pred, axis=1).squeeze())[0]
        # y = np.argmax(pred[index, :, x])
        # probability = np.max(pred[index, :, x])
        if len(predictions) != 1:
            raise DataProcessingError(
                f"Shape of fovea predictions are not as expected."
                f" Length of predictions = {len(predictions)}"
            )
        predictions_: np.ndarray = predictions[0]

        # Check that we have the expected number of results for the number of files
        if filenames:
            if len(filenames) != len(predictions_):
                raise DataProcessingError(
                    f"Length of predictions ({len(predictions_)}"
                    f" does not match the number of files ({len(filenames)})"
                    f" while processing fovea calculations."
                )

        fovea_coordinates: list[Coordinates] = []
        bscan_idxs: list[int] = []
        predictions_idx: int = 0
        for test_data in test_data_dfs:
            if self.bscans_width_col not in test_data.columns:
                raise ValueError(
                    f"Column {self.bscans_width_col} not found in data, "
                    f"cannot compute Fovea coordinates."
                )

            # Extract prediction information relevant to this chunk of the data
            len_curr_data = len(test_data)
            end_predictions_idx = predictions_idx + len_curr_data
            predictions_curr: np.ndarray = predictions_[
                predictions_idx:end_predictions_idx
            ]
            predictions_idx = end_predictions_idx

            for i, pred in enumerate(predictions_curr):
                bscan_idx: int = int(
                    pred[0]
                )  # this is the row location of the max pixel
                bscan_idxs.append(bscan_idx)
                bscan_width: int = test_data[self.bscans_width_col][i]
                for value in asdict(self.location_prefixes).values():
                    if f"{value}{bscan_idx}" not in test_data.columns:
                        raise ValueError(
                            f"Column {value}{bscan_idx} not found in data, "
                            f"cannot compute Fovea coordinates."
                        )

                x_start: int = test_data[
                    f"{self.location_prefixes.start_x_image}{bscan_idx}"
                ][i]
                y_start: int = test_data[
                    f"{self.location_prefixes.start_y_image}{bscan_idx}"
                ][i]
                x_end: int = test_data[
                    f"{self.location_prefixes.end_x_image}{bscan_idx}"
                ][i]
                y_end: int = test_data[
                    f"{self.location_prefixes.end_y_image}{bscan_idx}"
                ][i]

                coords = get_fovea_planar_coords(
                    x=pred[1],  # this is the column location of the max pixel
                    bscan_width=bscan_width,
                    x_start=x_start,
                    y_start=y_start,
                    x_end=x_end,
                    y_end=y_end,
                )
                fovea_coordinates.append(coords)

        # TODO: [BIT-3486] As these lists can contain entries for every
        #       element in the datasource, it may be too large to process in memory.
        #       Consider switching this to be a Generator for output.
        #       Workaround is to use batch_execution to constrain input size to
        #       each pass.

        # NOTE: The orders of these should match the input order of the predictions
        return bscan_idxs, fovea_coordinates


class FoveaCoordinatesAlgorithm(
    BaseNonModelAlgorithmFactory[NoResultsModellerAlgorithm, _WorkerSide]
):
    """Computes the Fovea coordinates from the Fovea detection model predictions.

    Args:
        datastructure: The data structure to use for the algorithm.
        bscan_width_col: The column name that contains the bscan width.
            Defaults to "size_width".
        location_prefixes: A dataclass that contains the
            prefixes for the start and end of the images along
            both X and Y axis.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "bscan_width_col": fields.Str(),
        "location_prefixes": fields.Nested(
            desert.schema_class(SLOSegmentationLocationPrefix), allow_none=True
        ),
    }

    def __init__(
        self,
        datastructure: DataStructure,
        bscan_width_col: str = "size_width",
        location_prefixes: Optional[SLOSegmentationLocationPrefix] = None,
        **kwargs: Any,
    ) -> None:
        self.bscan_width_col = bscan_width_col
        self.location_prefixes = (
            location_prefixes
            if location_prefixes is not None
            else SLOSegmentationLocationPrefix()
        )
        super().__init__(datastructure=datastructure, **kwargs)

    def modeller(self, **kwargs: Any) -> NoResultsModellerAlgorithm:
        """Modeller-side of the algorithm."""
        return NoResultsModellerAlgorithm(
            log_message="Running Fovea Coordinates Algorithm",
            **kwargs,
        )

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Worker-side of the algorithm."""
        return _WorkerSide(
            bscans_width_col=self.bscan_width_col,
            location_prefixes=self.location_prefixes,
            **kwargs,
        )
