"""General retry utilities."""

from typing import Final

from bitfount.exceptions import BitfountError

DEFAULT_BACKOFF_FACTOR: Final = 1
_DEFAULT_MAX_BACKOFF: Final = 60


def compute_backoff(
    retry_count: int,
    backoff_factor: int = DEFAULT_BACKOFF_FACTOR,
    max_backoff: int = _DEFAULT_MAX_BACKOFF,
) -> int:
    """Computes the backoff time for a retry.

    Backoff is increased using standard exponential backoff formula
    For standard backoff factor of one this results in backoffs of
    [1, 2, 4, 8, ...] seconds.

    Args:
        retry_count: The number of retries attempted.
        backoff_factor: The backoff factor to use.
        max_backoff: The maximum backoff time.

    Returns:
        The backoff time.
    """
    return int(min(max_backoff, backoff_factor * (2 ** (retry_count - 1))))


class MaxRetriesExceededError(BitfountError):
    """Exception raised when the maximum number of retries is exceeded."""

    pass
