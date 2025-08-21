"""Algorithm for outputting results to CSV on the pod-side."""

from __future__ import annotations

from dataclasses import dataclass
import operator
import os
from pathlib import Path
import typing
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Optional, Union

import desert
from marshmallow import fields
from marshmallow.validate import OneOf
from marshmallow_union import Union as M_Union
import more_itertools
import pandas as pd

import bitfount.config
from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
)
from bitfount.data.datasources.utils import (
    ORIGINAL_FILENAME_METADATA_COLUMN,
)
from bitfount.data.datasplitters import DatasetSplitter, _InferenceSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.data.exceptions import DataSourceError
from bitfount.data.types import DataSplit
from bitfount.federated.algorithms.base import (
    BaseNonModelAlgorithmFactory,
    BaseWorkerAlgorithm,
    NoResultsModellerAlgorithm,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    FILTER_MATCHING_COLUMN,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.utils.pandas_utils import (
    append_dataframe_to_csv,
    dataframe_iterable_join,
)

if TYPE_CHECKING:
    from bitfount.types import T_FIELDS_DICT

logger = _get_federated_logger(__name__)


_FilterOperatorTypes = Literal[
    "equal",
    "==",
    "equals",
    "not equal",
    "!=",
    "less than",
    "<",
    "less than or equal",
    "<=",
    "greater than",
    ">",
    "greater than or equal",
    ">=",
]

_OperatorMapping = {
    "less than": operator.lt,
    "<": operator.lt,
    "less than or equal": operator.le,
    "<=": operator.le,
    "greater than": operator.gt,
    ">": operator.gt,
    "greater than or equal": operator.ge,
    ">=": operator.ge,
    "equal": operator.eq,
    "==": operator.eq,
    "equals": operator.eq,
    "not equal": operator.ne,
    "!=": operator.ne,
}


@dataclass
class ColumnFilter:
    """Dataclass for column filtering.

    Args:
        column: The column name on which the filter will be applied.
            The filtering ignores capitalization or spaces for the
            column name.
        operator: The operator for the filtering operation. E.g.,
            "less than", ">=", "not equal", "==".
        value: The value for the filter. This is allowed to be a
            string only for `equals` or `not equal` operators,
            and needs to be a float or integer for all other operations.

    Raises:
        ValueError: If an inequality comparison operation is given
        with a value which cannot be converted to a float.
    """

    column: str = desert.field(fields.String())
    operator: str = desert.field(
        fields.String(validate=OneOf(typing.get_args(_FilterOperatorTypes)))
    )
    value: typing.Union[str, int, float] = desert.field(
        M_Union([fields.String(), fields.Integer(), fields.Float()])
    )

    def __post_init__(self) -> None:
        # check that the operator is valid:
        try:
            op = _OperatorMapping[self.operator]
            if op != operator.eq and op != operator.ne:
                try:
                    float(self.value)
                except ValueError as e:
                    raise ValueError(
                        f"Filter value `{self.value}` incompatible with "
                        f"operator type `{self.operator}`. "
                        f"Raised ValueError: {str(e)}"
                    ) from e
        except KeyError as ke:
            raise KeyError(
                f"Given operator `{self.operator}` is not valid."
                "Make sure your operator is one of the following : "
                f"{typing.get_args(_FilterOperatorTypes)}"
            ) from ke


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side of the algorithm."""

    def __init__(
        self,
        path: Union[os.PathLike, str],
        original_cols: Optional[list[str]] = None,
        filter: Optional[list[ColumnFilter]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.path = Path(path)
        self.original_cols = original_cols
        self.filter = filter

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

    def _add_filtering_to_df(
        self, df: pd.DataFrame, filter: ColumnFilter
    ) -> pd.DataFrame:
        """Applies the filter to the given dataframe.

        An extra column will be added to the dataframe indicating which
        rows match a given filter.

        Args:
            df: The dataframe on which the filter is applied.
            filter: A ColumnFilter instance.

        Returns:
            A dataframe with additional column added which
            indicates whether a datapoint matches the given
            condition in the ColumnFilter.
        """
        columns = [
            col
            for col in df.columns
            if filter.column.lower().replace(" ", "") == col.lower().replace(" ", "")
        ]

        if len(columns) == 0:
            raise KeyError(f"No column {filter.column} found in the data.")
        else:
            # dataframe cannot have duplicate columns, so
            # it's safe to assume it will only be one column
            matching_col = columns[0]
            value: typing.Union[str, float] = filter.value

        op = _OperatorMapping[filter.operator]
        if op != operator.eq and op != operator.ne:
            value = float(value)

        # Produce a meaningful column name for the filtering output
        filter_column_name: str = f"{matching_col} {filter.operator} {filter.value}"
        df[filter_column_name] = op(df[matching_col], value)

        # Update column containing "All Criteria Matched" information
        df[FILTER_MATCHING_COLUMN] = df[filter_column_name] & df[FILTER_MATCHING_COLUMN]

        # Update the expected output columns that we want in the dataframe
        if self.original_cols:
            if filter_column_name not in self.original_cols:
                self.original_cols.append(filter_column_name)
            if FILTER_MATCHING_COLUMN not in self.original_cols:
                self.original_cols.append(FILTER_MATCHING_COLUMN)

        return df

    def run(
        self,
        results_df: Union[pd.DataFrame, list[pd.DataFrame]],
        task_id: Optional[str] = None,
    ) -> str:
        """Saves the results of an inference task on the pod.

        The results are saved in a CSV file, at the user specified path.

        Args:
            results_df: The results of the previous inference task.
            task_id: The ID of the task.
        """
        # Get the path to the CSV file.
        if task_id is not None:
            Path(self.path / f"{task_id}").mkdir(parents=True, exist_ok=True)
            csv_path = self.path / f"{task_id}" / "results.csv"
        else:
            Path(self.path).mkdir(parents=True, exist_ok=True)
            csv_path = self.path / "results.csv"
            i = 1
            while csv_path.exists():
                csv_path = self.path / f"results ({i}).csv"
                i += 1
        logger.debug(f"CSV path for report output is: {str(csv_path)}")
        # First, we need to extract the appropriate data from the datasource by
        # combining it with the output from the previous inference (i.e. joining
        # on the identifiers).
        #
        # To enable working with both iterable- and non-iterable-datasources, we
        # work with the assumption of processing the dataset in an iterable manner,
        # with a non-iterable-dataset simply being converted into a one-element
        # iterable.
        dfs: typing.Iterable[pd.DataFrame]

        # This first if-entry is a temporary fix to allow for the case where the
        # results dataframe from the previous algorithm has been run on the entire
        # dataset rather than just the test set. Specifically this was done to
        # accommodate the transformer text generation and perplexity algorithms.
        logger.debug(f"{len(results_df)=}, {len(self.datasource)=}")
        if isinstance(results_df, pd.DataFrame) and len(results_df) == len(
            self.datasource
        ):
            if self.original_cols and not all(
                res_col in self.original_cols for res_col in results_df.columns.tolist()
            ):
                self.original_cols += [
                    res_col
                    for res_col in results_df.columns.tolist()
                    if res_col not in self.original_cols
                ]
            logger.debug("Joining datasource dataframe to results dataframe")

            # Reset indexes to avoid issues with joining and then concatenate/join
            results_df = results_df.reset_index(drop=True)

            # Handle the case where the results_df already contains the filenames we
            # need to retrieve
            if isinstance(self.datasource, FileSystemIterableSource):
                if ORIGINAL_FILENAME_METADATA_COLUMN in results_df:
                    file_names: list[str] = results_df[
                        ORIGINAL_FILENAME_METADATA_COLUMN
                    ].tolist()
                    logger.debug(f"Getting data for: {file_names}")
                    file_df = self.datasource.get_data(file_names)

                    if file_df is not None:
                        merged = file_df.merge(
                            results_df, on=ORIGINAL_FILENAME_METADATA_COLUMN
                        )
                        dfs = [merged]
                    else:
                        # Otherwise create an empty iterable with the expected column
                        dfs = [
                            pd.DataFrame(columns=[ORIGINAL_FILENAME_METADATA_COLUMN])
                        ]
                else:
                    dfs = dataframe_iterable_join(
                        self.datasource.yield_data(
                            data_keys=self.datasource.selected_file_names
                        ),
                        results_df,
                        reset_joiners_index=True,
                    )
            else:
                dfs = dataframe_iterable_join(
                    self.datasource.yield_data(),
                    results_df,
                    reset_joiners_index=True,
                )
        # Otherwise we need to determine how to extract the datasource data and
        # how to join it to the results_df.
        else:
            # If we have a list of results_dfs, we combine them into one.
            aux_results_df: pd.DataFrame
            if isinstance(results_df, list):
                aux_results_df = results_df[0]
                for index in range(1, len(results_df)):
                    # TODO: [NO_TICKET: Potential improvement] Can we just concat
                    #       without the for loop?
                    aux_results_df = pd.concat(
                        [aux_results_df, results_df[index]], axis=1
                    )
            else:
                aux_results_df = results_df

            # Add any additional columns from the combined results_dfs to the list of
            # original columns for this datasource.
            if self.original_cols and not all(
                res_col in self.original_cols
                for res_col in aux_results_df.columns.tolist()
            ):
                self.original_cols += [
                    res_col
                    for res_col in aux_results_df.columns.tolist()
                    if res_col not in self.original_cols
                ]

            # Handle the case where the results_df already contains the filenames we
            # need to retrieve
            if (
                isinstance(self.datasource, FileSystemIterableSource)
                and ORIGINAL_FILENAME_METADATA_COLUMN in aux_results_df
            ):
                file_names: list[str] = aux_results_df[  # type: ignore[no-redef] # Reason: this is in a separate flow branch # noqa: E501
                    ORIGINAL_FILENAME_METADATA_COLUMN
                ].tolist()
                logger.debug(f"Getting data for: {file_names}")
                file_df = self.datasource.get_data(file_names)

                if file_df is not None:
                    merged = file_df.merge(
                        aux_results_df, on=ORIGINAL_FILENAME_METADATA_COLUMN
                    )
                    dfs = [merged]
                else:
                    # Otherwise create an empty iterable with the expected column
                    dfs = [pd.DataFrame(columns=[ORIGINAL_FILENAME_METADATA_COLUMN])]

            # If there are no test rows, this is only okay if the datasource is iterable
            # Otherwise, we raise an error.
            else:
                data_splitter = (
                    self.data_splitter if self.data_splitter else _InferenceSplitter()
                )

                dfs = data_splitter.iter_dataset_split(self.datasource, DataSplit.TEST)
                dfs = more_itertools.peekable(dfs)
                try:
                    dfs.peek()
                except StopIteration as si:
                    raise DataSourceError(
                        "Datasource has no test set, cannot produce CSV."
                    ) from si

                # Append the results to the original data
                logger.debug("Appending results to the original data.")
                dfs = dataframe_iterable_join(dfs, aux_results_df)

        # Work through each dataframe in the collection, filtering and removing
        # unneeded columns
        for df in dfs:
            # Filter the data if a filter is provided
            if self.filter is not None:
                logger.debug("Filtering data.")
                df[FILTER_MATCHING_COLUMN] = True
                for i, col_filter in enumerate(self.filter):
                    logger.debug(f"Running filter {i + 1}")
                    try:
                        df = self._add_filtering_to_df(df, col_filter)

                    except (KeyError, TypeError) as e:
                        if isinstance(e, KeyError):
                            logger.warning(
                                f"No column `{col_filter.column}` found in the data. Filtering only on remaining given columns"  # noqa: E501
                            )
                        else:
                            # if TypeError
                            logger.warning(
                                f"Filter column {col_filter.column} is incompatible with "  # noqa: E501
                                f"operator type {col_filter.operator}. "
                                f"Raised TypeError: {str(e)}"
                            )
                        logger.info(
                            f"Filtering will skip `{col_filter.column} "
                            f"{col_filter.operator} {col_filter.value}`."
                        )

            if (
                isinstance(self.datasource, FileSystemIterableSource)
                and self.datasource.cache_images is False
            ):
                img_columns = list(self.datasource.image_columns)
                # Find the intersection of image_cols and data.columns
                existing_img_columns = list(set(img_columns) & set(df.columns))
                missing_img_columns = set(img_columns) - set(df.columns)

                if missing_img_columns:
                    logger.warning(
                        f"DataFrame has {len(existing_img_columns)} out of"
                        f" {len(img_columns)} image columns."
                        f"Missing {len(missing_img_columns)} image columns."
                    )
                    logger.debug(
                        "The following image columns are missing from"
                        f" the DataFrame: {missing_img_columns}"
                    )

                # Add True/None to indicate the number of frame based
                # on the pixel data columns if images are not cached.
                if existing_img_columns:
                    img_df = df[existing_img_columns]
                    # Replace non-NA elements with True
                    img_df = img_df.mask(img_df.notna(), other=True)
                    # Replace NA elements with False
                    img_df = img_df.mask(img_df.isna(), other=None)
                    df[existing_img_columns] = img_df

            # Drop any columns that were not in the original data if specified.
            if self.original_cols is not None:
                report_cols = [col for col in self.original_cols if col in df.columns]
                if len(report_cols) != 0:
                    csv_df = df[report_cols].copy()
                else:
                    csv_df = df.copy()
                    logger.warning(
                        "No columns from the original_cols list were found "
                        "in the data. Saving the whole dataframe to csv."
                    )
            else:
                csv_df = df.copy()

            # Write the dataframe to CSV, handling appending to existing CSV
            csv_path = append_dataframe_to_csv(csv_path, csv_df.round(decimals=2))

        return csv_path.read_text(encoding="utf-8")


class CSVReportAlgorithm(
    BaseNonModelAlgorithmFactory[NoResultsModellerAlgorithm, _WorkerSide]
):
    """Algorithm for generating the CSV results reports.

    Args:
        datastructure: The data structure to use for the algorithm.
        save_path: The folder path where the csv report should be saved.
            The CSV report will have the same name as the taskID.
        original_cols: The tabular columns from the datasource to include
            in the report. If not specified it will include all
            tabular columns from the datasource.
        filter: A list of `ColumnFilter` instances on which
            we will filter the data on. Defaults to None. If supplied,
            columns will be added to the output csv indicating the
            records that match the specified criteria. If more than one
            `ColumnFilter` is given, and additional column will be added
            to the output csv indicating the datapoints that match all
            given criteria (as well as the individual matches)
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "save_path": fields.Str(),
        "original_cols": fields.List(fields.Str(), allow_none=True),
        "filter": fields.Nested(
            desert.schema_class(ColumnFilter), many=True, allow_none=True
        ),
    }

    def __init__(
        self,
        datastructure: DataStructure,
        save_path: Optional[Union[str, os.PathLike]] = None,
        original_cols: Optional[list[str]] = None,
        filter: Optional[list[ColumnFilter]] = None,
        **kwargs: Any,
    ) -> None:
        self.save_path: Path
        if save_path is None:
            self.save_path = bitfount.config.settings.paths.output_dir
        else:
            self.save_path = Path(save_path)

        self.original_cols = original_cols
        self.filter = filter
        super().__init__(datastructure=datastructure, **kwargs)

    def modeller(self, **kwargs: Any) -> NoResultsModellerAlgorithm:
        """Modeller-side of the algorithm."""
        return NoResultsModellerAlgorithm(
            log_message="CSV saved to the pod.", save_path=self.save_path, **kwargs
        )

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Worker-side of the algorithm."""
        return _WorkerSide(
            path=self.save_path,
            filter=self.filter,
            original_cols=self.original_cols,
            **kwargs,
        )
