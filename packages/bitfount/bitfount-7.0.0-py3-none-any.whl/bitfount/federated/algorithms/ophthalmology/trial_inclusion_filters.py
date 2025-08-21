"""This module contains the trial inclusion filters used in Ophthalmology."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import operator
import typing
from typing import Optional, Union

import desert
from marshmallow import fields
from marshmallow.validate import OneOf
from marshmallow_union import Union as M_Union
import pandas as pd

from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    FILTER_FAILED_REASON_COLUMN,
    FILTER_MATCHING_COLUMN,
    PartialMatchingType,
    _FilterOperatorTypes,
    _OperatorMapping,
    _OperatorOppositeMapping,
)
from bitfount.types import UsedForConfigSchemas

_logger = logging.getLogger(__name__)


@dataclass
class ColumnFilter(UsedForConfigSchemas):
    """Dataclass for basic single column filtering.

    Args:
        column: The column name on which the filter will be applied.
            Capitalization or spaces for the column name will be
            ignored.
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
    value: Union[str, int, float] = desert.field(
        M_Union([fields.String(), fields.Integer(), fields.Float()])
    )
    how: PartialMatchingType = desert.field(
        fields.String(validate=OneOf(["any", "all"])), default="all"
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

    def apply_filter(
        self,
        df: pd.DataFrame,
        rename_columns: Optional[typing.Mapping[str, str]] = None,
    ) -> pd.DataFrame:
        """Apply self filter to a dataframe.

        An extra column will be added to the dataframe indicating which
        rows match a given filter. Reasons will be appended in the existing
        FILTER_FAILED_REASON_COLUMN column.

        Input dataframe must contain a FILTER_FAILED_REASON_COLUMN column.
        """
        columns = [
            col
            for col in df.columns
            if self.column.lower().replace(" ", "") == col.lower().replace(" ", "")
        ]
        if len(columns) == 0:
            raise KeyError(f"No column {self.column} found in the data.")
        else:
            # dataframe cannot have duplicate columns, so
            # it's safe to assume it will only be one column
            matching_col = columns[0]
            value: Union[str, float] = self.value

        op = _OperatorMapping[self.operator]
        if op != operator.eq and op != operator.ne:
            value = float(value)

        # Determine whether current filter matches each row in df
        #   NaN values should always be marked as non-matching
        filter_match = op(df[matching_col], value) & df[matching_col].notnull()

        current_filter_column = f"{matching_col} {self.operator} {self.value}"
        df[current_filter_column] = filter_match

        # Update overall match results
        df[FILTER_MATCHING_COLUMN] = df[current_filter_column] & df.get(
            FILTER_MATCHING_COLUMN, True
        )

        # Create the reason messages
        # Determine the column name to use in the reason message
        display_col_name = self.column
        # If rename_columns is provided and the matching column is in it,
        # use the renamed version for display
        if rename_columns is not None:
            # Check if the matching column is in the rename_columns dictionary
            for orig_col, renamed_col in rename_columns.items():
                if orig_col.lower().replace(" ", "") == matching_col.lower().replace(
                    " ", ""
                ):
                    display_col_name = renamed_col
                    break
        op_opposite = _OperatorOppositeMapping[op]
        normal_reason = f"{display_col_name} {op_opposite} {self.value}, "

        # Update reason for value not meeting criteria
        normal_update_mask = (
            ~filter_match
            & ~df[matching_col].isna()
            & ~df[FILTER_FAILED_REASON_COLUMN].str.contains(normal_reason, regex=False)
        )
        df.loc[normal_update_mask, FILTER_FAILED_REASON_COLUMN] = (
            df.loc[normal_update_mask, FILTER_FAILED_REASON_COLUMN] + normal_reason
        )

        # Update reason for NaN values (only if not already present)
        nan_reason = f"{display_col_name} not found, "
        nan_update_mask = df[matching_col].isna() & ~df[
            FILTER_FAILED_REASON_COLUMN
        ].str.contains(nan_reason, regex=False)
        df.loc[nan_update_mask, FILTER_FAILED_REASON_COLUMN] = (
            df.loc[nan_update_mask, FILTER_FAILED_REASON_COLUMN] + nan_reason
        )
        return df

    def _add_partial_filtering_to_df(
        self,
        df: pd.DataFrame,
        drop_filtered_cols: bool = False,
        add_new_col_for_filter: bool = True,
        rename_columns: Optional[typing.Mapping[str, str]] = None,
    ) -> pd.DataFrame:
        """Applies the filter to the given dataframe.

        Partial filtering looks at all columns that start with a certain
        string and applies the given filter to all of them. An extra
        column will be added to the dataframe indicating which
        rows match a given partial filter.

        Args:
            df: The dataframe on which the filter is applied.
            filter: A ColumnFilter instance.
            drop_filtered_cols: Whether to drop filtered columns.
            add_new_col_for_filter: Whether to add a new column representing the filter
                criteria and responses.
            rename_columns: A dictionary mapping original column names to renamed ones.

        Returns:
            A dataframe with additional column added which indicates
            whether a datapoint matches the given condition in
            the ColumnFilter.
        """
        columns = [
            col
            for col in df.columns
            if col.lower()
            .replace(" ", "")
            .startswith(self.column.lower().replace(" ", ""))
        ]
        if len(columns) == 0:
            raise KeyError(f"No column {self.column} found in the data.")

        value: Union[str, float] = self.value
        op = _OperatorMapping[self.operator]
        if op != operator.eq and op != operator.ne:
            value = float(value)

        currently_matched = None
        for matching_col in columns:
            # Get the comparison result
            comparison_result = op(df[matching_col], value)

            # Handle NaN values - they should always be marked as non-matching
            nan_mask = df[matching_col].isna()
            if nan_mask.any():
                comparison_result = comparison_result & ~nan_mask

            # Initialize truth_val with the first comparison result and update
            # based on self.how
            if currently_matched is None:
                currently_matched = comparison_result
            elif self.how == "any":  # type: ignore[unreachable] # Reason: mypy error
                currently_matched = currently_matched | comparison_result
            else:
                currently_matched = currently_matched & comparison_result

            if drop_filtered_cols:
                df = df.drop(columns=matching_col)
            if add_new_col_for_filter:
                df[f"{matching_col} {self.operator} {self.value}"] = comparison_result

        if currently_matched is not None:
            df[FILTER_MATCHING_COLUMN] = currently_matched & df[FILTER_MATCHING_COLUMN]
            false_val = ~currently_matched
            op_opposite = _OperatorOppositeMapping[op]

            # Create a scope variable that switches "any" to "all" and "all" to "some"
            scope = "all" if self.how == "any" else "some"

            # Determine the display column names to use in the reason message
            display_columns = []
            for col in columns:
                display_col = col
                if rename_columns is not None:
                    # Check if the column is in the rename_columns dictionary
                    for orig_col, renamed_col in rename_columns.items():
                        if orig_col.lower().replace(" ", "") == col.lower().replace(
                            " ", ""
                        ):
                            display_col = renamed_col
                            break
                display_columns.append(display_col)

            # Join column names with commas
            column_list = ", ".join(display_columns)

            # Create a single failure reason for all columns
            failed_reason = f"{scope} columns {column_list} {op_opposite} {self.value}"

            # Add the NA reason part
            failed_reason += " or not found, "

            # Update reason for non-matching values
            df.loc[false_val, FILTER_FAILED_REASON_COLUMN] = (
                df.loc[false_val, FILTER_FAILED_REASON_COLUMN] + failed_reason
            )

        return df


@dataclass
class MethodFilter:
    """Dataclass for filtering using a python method.

    Generally used for more complex filter logic using values
    across several columns.
    Note: This should not be serialised. NOT used for config schemas.

    Args:
        method: Filter method for determining if a row in a dataframe
          is eligible for trial.
        required_columns: Columns required in the df in order for
          filter to be applied.
        filter_name: Name of filter, to be used in added column and
          descriptions.
        filter_failed_message: Message to explain patient ineligibility.
    """

    method: typing.Callable[[pd.Series], bool]
    required_columns: set[str]
    filter_name: str
    filter_failed_message: str

    def apply_filter(self, df: pd.DataFrame, **kwargs: typing.Any) -> pd.DataFrame:
        """Apply self filter to a dataframe.

        An extra column will be added to the dataframe indicating which
        rows match a given filter. Reasons will be appended in the existing
        FILTER_FAILED_REASON_COLUMN column.

        Input dataframe must contain a FILTER_FAILED_REASON_COLUMN column.
        """
        missing_columns = self.required_columns - set(df.columns)
        if missing_columns:
            _logger.debug(
                f"Missing required columns {missing_columns} for"
                f" filter {self.filter_name}"
            )
            df[self.filter_name] = (
                f"Missing required column(s) {missing_columns} to calculate this filter"
            )
            df[FILTER_FAILED_REASON_COLUMN] = df[FILTER_FAILED_REASON_COLUMN] + (
                f"unable to determine {self.filter_name} filter, "
            )
            return df

        # Apply matching method
        df[self.filter_name] = df.apply(self.method, axis=1)

        # Update overall match results
        df[FILTER_MATCHING_COLUMN] = df[self.filter_name] & df.get(
            FILTER_MATCHING_COLUMN, True
        )

        nan_update_mask = df[list(self.required_columns)].isna().any(axis=1)

        # Update reason for value not meeting criteria
        df.loc[
            (~df[self.filter_name] & ~nan_update_mask),
            FILTER_FAILED_REASON_COLUMN,
        ] = (
            df.loc[~df[self.filter_name], FILTER_FAILED_REASON_COLUMN]
            + self.filter_failed_message
            + ", "
        )
        # Update reason for nan values
        df.loc[
            (~df[self.filter_name] & nan_update_mask),
            FILTER_FAILED_REASON_COLUMN,
        ] = (
            df.loc[~df[self.filter_name], FILTER_FAILED_REASON_COLUMN]
            + f"missing values for {self.filter_name} filter, "
        )

        return df

    def _add_partial_filtering_to_df(
        self, df: pd.DataFrame, **kwargs: typing.Any
    ) -> pd.DataFrame:
        # Currently not required for MethodFilter, hence not implemented
        return df
