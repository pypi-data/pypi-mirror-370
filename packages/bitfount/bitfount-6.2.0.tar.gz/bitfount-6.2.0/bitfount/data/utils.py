"""Utility functions concerning data."""

from __future__ import annotations

import enum
from enum import Enum
from itertools import islice
import logging
from typing import TYPE_CHECKING, Iterable, Optional, Sequence, TypeVar, Union, overload

from bitfount.data.types import SemanticType

if TYPE_CHECKING:
    from bitfount.data.datastructure import DataStructure
    from bitfount.data.schema import BitfountSchema

logger = logging.getLogger(__name__)


class DataStructureSchemaCompatibility(Enum):
    """The level of compatibility between a datastructure and a pod/table schema.

    Denotes 4 different levels of compatibility:
        - COMPATIBLE: Compatible to our knowledge.
        - WARNING: Might be compatible but there might still be runtime
                   incompatibility issues.
        - INCOMPATIBLE: Clearly incompatible.
        - ERROR: An error occurred whilst trying to check compatibility.
    """

    # Compatible to our knowledge
    COMPATIBLE = enum.auto()
    # Might be compatible but there might still be runtime incompatibility issues
    WARNING = enum.auto()
    # Clearly incompatible
    INCOMPATIBLE = enum.auto()
    # An error occurred whilst trying to check compatibility
    ERROR = enum.auto()


def check_datastructure_schema_compatibility(
    datastructure: DataStructure,
    schema: BitfountSchema,
    data_identifier: Optional[str] = None,
) -> tuple[DataStructureSchemaCompatibility, list[str]]:
    """Compare a datastructure from a task and a data schema for compatibility.

    Currently, this checks that requested columns exist in the target schema.

    Query-based datastructures are not supported.

    Args:
        datastructure: The datastructure for the task.
        schema: The overall schema for the pod in question.
        data_identifier: If the datastructure specifies multiple pods then the data
            identifier is needed to identify which part of the datastructure refers
            to the pod in question.

    Returns:
        A tuple of the compatibility level (DataStructureSchemaCompatibility value),
        and a list of strings which are all compatibility warnings/issues found.
    """
    curr_compat_level = DataStructureSchemaCompatibility.COMPATIBLE

    # Extract column names from schema
    schema_columns: dict[Union[str, SemanticType], set[str]] = {
        st: set(schema.get_feature_names(st)) for st in SemanticType
    }
    schema_columns["ALL"] = set(schema.get_feature_names())

    # Collect any missing column details for which we consider the missing column
    # to be an WARNING:
    #   - ignored
    warning_cols: dict[str, list[str]] = {
        col_type: _find_missing_columns(req_cols, schema_columns["ALL"])
        for col_type, req_cols in (("ignore", datastructure.ignore_cols),)
    }
    warnings: list[str] = sorted(
        [
            f'Warning: Expected "{col_type}" column, "{col}",'
            f" but it could not be found in the data schema."
            for col_type, cols in warning_cols.items()
            for col in cols
        ]
    )
    if warnings:
        curr_compat_level = DataStructureSchemaCompatibility.WARNING

    # Collect any missing column details for which we consider the missing column
    # to indicate INCOMPATIBLE:
    #   - target
    #   - selected
    #   - image
    incompatible_cols = {
        col_type: _find_missing_columns(req_cols, schema_columns["ALL"])
        for col_type, req_cols in (
            ("target", datastructure.target),
            ("select", datastructure.selected_cols),
            ("image", datastructure.image_cols),
        )
    }
    incompatible: list[str] = sorted(
        [
            f'Incompatible: Expected "{col_type}" column, "{col}",'
            f" but it could not be found in the data schema."
            for col_type, cols in incompatible_cols.items()
            for col in cols
        ]
    )
    if incompatible:
        curr_compat_level = DataStructureSchemaCompatibility.INCOMPATIBLE

    # TODO: [BIT-3100] Add semantic type checks for additional compatibility
    #       constraints

    return curr_compat_level, incompatible + warnings


def _find_missing_columns(
    to_check: Optional[Union[str, list[str]]], check_against: set[str]
) -> list[str]:
    """Check if requested columns are missing from a set.

    Args:
        to_check: the column name(s) to check for inclusion.
        check_against: the set of columns to check against.

    Returns:
        A sorted list of all column names from `to_check` that _weren't_ found in
        `check_against`.
    """
    # If nothing to check, return empty list
    if to_check is None:
        return []

    # If only one to check, shortcut check it
    if isinstance(to_check, str):
        if to_check not in check_against:
            return [to_check]
        else:
            return []

    # Otherwise, perform full check
    to_check_set: set[str] = set(to_check)
    return sorted(to_check_set.difference(check_against))


_I = TypeVar("_I")


# mypy_reason: The `@overload`s do "overlap" (with the top one being a subset of the
#              lower), but because they are evaluated in order, this doesn't prevent
#              the correct typing from being inferred.
# See: https://mypy.readthedocs.io/en/stable/more_types.html#type-checking-the-variants
@overload
def partition(iterable: list[_I], partition_size: int = ...) -> Iterable[list[_I]]: ...  # type: ignore[overload-overlap] # Reason: See comment # noqa: E501


@overload
def partition(
    iterable: Iterable[_I], partition_size: int = ...
) -> Iterable[tuple[_I]]: ...


def partition(
    iterable: Iterable[_I], partition_size: int = 1
) -> Iterable[Sequence[_I]]:
    """Takes an iterable and yields partitions of size `partition_size`.

    The final partition may be less than size `partition_size` due to the variable
    length of the iterable.

    The partitions will be yielded as tuples of elements from the original iterable,
    unless the original iterable is a list, in which case the partitions are also
    yielded as lists.
    """
    batch_cls = list if isinstance(iterable, list) else tuple

    if partition_size < 1:
        raise ValueError(f"n must be at least one, got {partition_size}")

    iterator = iter(iterable)
    while batch := batch_cls(islice(iterator, partition_size)):
        yield batch
