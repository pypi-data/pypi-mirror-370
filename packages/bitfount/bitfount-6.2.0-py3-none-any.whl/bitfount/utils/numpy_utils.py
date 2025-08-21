"""Utility functions for interacting with numpy."""

from __future__ import annotations

from typing import Optional, TypeVar, Union, cast

import numpy as np

T = TypeVar("T")


def _get_2_dims(
    a: Union[np.ndarray, list[np.ndarray], list[T]],
) -> tuple[int, Optional[int]]:
    """Extract the first two shape dimensions from object.

    If it is a numpy array of >2D, returns the first two.
    If it is a 1D numpy array, returns (the first one, None).

    If it is a list of all numpy arrays, they must all be of the same length, and then
    returns (list len, array len).

    If it is another type of list, returns (list len, None).
    """
    if isinstance(a, np.ndarray):
        if a.ndim >= 2:
            return a.shape[0], a.shape[1]
        else:
            return a.shape[0], None

    # Otherwise, looking at a list that might be of arrays
    if all(isinstance(i, np.ndarray) for i in a):
        a = cast(list[np.ndarray], a)

        # All arrays should be of the same length, make list of the
        # lengths set; should only be one entry if correct
        arr_lens = list(set(len(i) for i in a))
        if len(arr_lens) != 1:
            raise ValueError(
                f"Lengths of arrays in list of arrays must be the same length;"
                f" got lengths {arr_lens}"
            )

        return len(a), arr_lens[0]

    # Otherwise, looking at a list that isn't all arrays
    return len(a), None


def check_for_compatible_lengths(
    a: Union[np.ndarray, list[np.ndarray], list[T]],
    b: Union[np.ndarray, list[np.ndarray], list[T]],
    a_name: str = "the first arg",
    b_name: str = "the second arg",
) -> None:
    """Checks if two numpy-related collections are compatible lengths.

    Compatible lengths here means they are equal in size in the first or second
    dimension.

    Raises:
        ValueError: if the lengths are incompatible
    """
    a_1, a_2 = _get_2_dims(a)
    b_1, b_2 = _get_2_dims(b)

    # If both are 1D, just compare object lengths
    if a_2 is None and b_2 is None:
        if a_1 != b_1:
            raise ValueError(
                f"Mismatch in lengths of {a_name} vs {b_name};"
                f" got {a_1} in {a_name}, {b_1} in {b_name}."
            )

    # If one is 1D, the other 2D, compare against both options
    elif a_2 is None and b_2 is not None:
        if a_1 not in (b_1, b_2):
            raise ValueError(
                f"Mismatch in lengths of {a_name} vs {b_name};"
                f" got {a_1} in {a_name},"
                f" {b_1} elements of length {b_2} in {b_name}."
            )
    elif a_2 is not None and b_2 is None:
        if b_1 not in (a_1, a_2):
            raise ValueError(
                f"Mismatch in lengths of {a_name} vs {b_name};"
                f"got {a_1} elements of length {a_2} in {a_name},"
                f" {b_1} in {b_name}."
            )

    # If 2D, need to compare against all
    else:  # all are non-None
        # See if there is _any_ overlap in the dimensions
        if not {a_1, a_2}.intersection({b_1, b_2}):
            raise ValueError(
                f"Mismatch in lengths of {a_name} vs {b_name};"
                f"got {a_1} elements of length {a_2} in {a_name},"
                f" {b_1} elements of length {b_2} in {b_name}."
            )
