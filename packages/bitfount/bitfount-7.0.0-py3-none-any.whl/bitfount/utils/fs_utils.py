"""Utility functions to interact with the filesystem."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from datetime import date, datetime
from functools import wraps
import logging
import os
from pathlib import Path, PureWindowsPath
import platform
import stat as st
import sys
import time
from typing import (
    Final,
    Optional,
    ParamSpec,
    Protocol,
    TypeVar,
    Union,
)
import uuid

from bitfount import config
from bitfount.persistence.caching import get_cache
from bitfount.utils.retry_utils import MaxRetriesExceededError, compute_backoff

_logger = logging.getLogger(__name__)

MAX_FILE_NUM = 100

# Assuming a _DEFAULT_MAX_BACKOFF of 60 seconds each retry after the 6th will take 1
# minute to complete. So this value (default 360) means about 6 hours of retries.
_NETWORK_DRIVE_RETRY_ATTEMPTS: Final[int] = (
    config.settings.network_drive_robustness_retries
)

R = TypeVar("R")


def safe_write_to_file(func: Callable[[Path], R], initial_path: Path) -> tuple[R, Path]:
    """Handle PermissionError when writing to a file.

    Execute some function that writes to a file and if it's not possible
    to write due to a PermissionError (e.g. the user has opened the file
    in Windows so can't be appended to) try to write to a new file instead.

    Args:
        func: Function to execute, that takes in the destination file path.
        initial_path: The desired destination file path.

    Returns:
        A tuple of the result of the function and the actual path finally written to.
    """
    try:
        r = func(initial_path)
        return r, initial_path
    except PermissionError as error:
        if initial_path.exists():
            i = 1
            new_path = (
                initial_path.parent / f"{initial_path.stem}{i}{initial_path.suffix}"
            )
            while new_path.exists() and i < MAX_FILE_NUM:
                i += 1
                new_path = (
                    initial_path.parent / f"{initial_path.stem}{i}{initial_path.suffix}"
                )
            _logger.warning(
                f"Error whilst writing to path {initial_path},"
                f" will try {new_path}: {error}"
            )
            if new_path.exists():
                raise error
            r = func(new_path)
            return r, new_path
        else:
            raise error


def get_file_last_modification_date(
    path: Union[str, os.PathLike], stat: Optional[os.stat_result] = None
) -> date:
    """Get the last modification date of a file.

    If the `stat` object is provided, then the information will be extracted from
    this in preference to getting a new one from the filesystem. Note that there is
    no checking that the stat object is up-to-date or even corresponds to the same
    file as `path`, so care should be taken to pass through the correct object.

    Args:
        path: The path to the file.
        stat: An optional `stat_result` object for the file, as returned by
            `os.stat(path)`. This can be used to avoid making a new filesystem query.

    Returns:
        The last modification date of the file.
    """
    if stat is None:
        stat = os.stat(path)

    timestamp = stat.st_mtime
    return datetime.fromtimestamp(timestamp).date()


def get_file_creation_date(
    path: Union[str, os.PathLike], stat: Optional[os.stat_result] = None
) -> date:
    """Get the creation date of a file with consideration for different OSs.

    If the `stat` object is provided, then the information will be extracted from
    this in preference to getting a new one from the filesystem. Note that there is
    no checking that the stat object is up-to-date or even corresponds to the same
    file as `path`, so care should be taken to pass through the correct object.

    :::caution

    It is not possible to get the creation date of a file on Linux. This method
    will return the last modification date instead. This will impact filtering of
    files by date.

    :::

    Args:
        path: The path to the file.
        stat: An optional `stat_result` object for the file, as returned by
            `os.stat(path)`. This can be used to avoid making a new filesystem query.

    Returns:
        The creation date of the file.
    """
    if stat is None:
        stat = os.stat(path)

    if sys.platform == "win32":
        timestamp = stat.st_ctime
    elif sys.platform == "darwin":
        timestamp = stat.st_birthtime
    else:
        # We're probably on Linux. No easy way to get creation dates here,
        # so we'll settle for when its content was last modified.
        timestamp = stat.st_mtime

    return datetime.fromtimestamp(timestamp).date()


def get_file_size(
    path: Union[str, os.PathLike], stat: Optional[os.stat_result] = None
) -> int:
    """Get the size, in bytes, of a file on the filesystem.

    If the `stat` object is provided, then the information will be extracted from
    this in preference to getting a new one from the filesystem. Note that there is
    no checking that the stat object is up-to-date or even corresponds to the same
    file as `path`, so care should be taken to pass through the correct object.

    Args:
        path: The path to the file.
        stat: An optional `stat_result` object for the file, as returned by
            `os.stat(path)`. This can be used to avoid making a new filesystem query.

    Returns:
        The size of the file, in bytes.
    """
    if stat is None:
        stat = os.stat(path)

    return stat.st_size


def is_file(
    path: Union[str, os.PathLike, os.DirEntry], stat: Optional[os.stat_result] = None
) -> bool:
    """Determine if a path is a file or not.

    If the `stat` object is provided, then the information will be extracted from
    this in preference to getting a new one from the filesystem. Note that there is
    no checking that the stat object is up-to-date or even corresponds to the same
    file as `path`, so care should be taken to pass through the correct object.

    Args:
        path: The path to check. Can also be an os.DirEntry as from scandir() or
            scantree().
        stat: An optional `stat_result` object for the path, as returned by
            `os.stat(path)`. This can be used to avoid making a new filesystem query.

    Returns:
        The size of the file, in bytes.
    """
    path_or_entry: Union[Path, os.DirEntry]
    if not isinstance(path, os.DirEntry):
        path_or_entry = Path(path)
    else:
        path_or_entry = path

    # If `stat` isn't provided, then defer to built-in methods (which will make an
    # `os.stat()` call
    if stat is None:
        return path_or_entry.is_file()
    # Otherwise, determine it using the provided details
    # This is copied from genericpath.py
    else:
        return st.S_ISREG(stat.st_mode)


def _is_windows_network_drive(file_path: Union[str, os.PathLike]) -> bool:
    """Check if a file path appears to be on a Windows network drive."""
    # This currently only checks for network drive inaccessibility on Windows.
    # Network drives on Unix systems are harder to detect due to the nature of
    # mounting in Unix systems.
    if (detected_system := platform.system()) != "Windows":
        _logger.debug(
            f"Currently, network drive checks"
            f" are only supported on Windows."
            f' Got platform of "{detected_system}"'
        )
        return False

    # Need to enforce absolute so that we can access the drive elements correctly.
    #
    # `.is_absolute()` is a PurePath method, so won't need filesystem access; we only
    # need filesystem access if the path is not absolute and we need to try and
    # convert it to such.
    absolute_file_path = Path(file_path)
    if not absolute_file_path.is_absolute():
        try:
            absolute_file_path = absolute_file_path.absolute()
        except OSError:
            _logger.debug(
                f"Failed to convert {str(absolute_file_path)} to absolute path,"
                f" unable to check if network drive."
            )
            return False

    # Check if the path appears to be on a network drive
    #
    # This check is based on the assumption that network drives are specified in UNC
    # style (e.g. `\\\\host\\share`) rather than a mapped network drive (e.g. `Z:`)
    if _check_if_non_network_drive_path(absolute_file_path):
        _logger.debug(
            f"Path {str(absolute_file_path)} does not appear to be on a network drive:"
            f" drive is {absolute_file_path.drive}, expected UNC style."
        )
        return False

    # Otherwise, seems to be a network drive
    return True


def _check_if_non_network_drive_path(absolute_file_path: Path) -> bool:
    """Returns True if the path does not appear to be on a network drive."""
    # Need to enforce absolute so that we can access the drive elements correctly.
    return absolute_file_path.drive.endswith(":")


def _windows_network_drive_inaccessible(file_path: Union[str, os.PathLike]) -> bool:
    """Try to determine if a network drive is inaccessible.

    This tries to determine if, for a file path on a Windows network drive, is that
    network drive currently inaccessible.
    """
    file_path_ = PureWindowsPath(file_path)

    # Check if the drive is currently inaccessible
    #
    # We do this by checking the accessibility of all the parents of the file path;
    # if _one_ of them is accessible then it's likely that the network drive is more
    # generally available
    for p in file_path_.parents:
        try:
            Path(p).stat()
        except OSError:
            pass
        else:
            # We found a parent that is accessible, so the drive is probably accessible
            return False
    else:
        # Couldn't access any of the parents, so the drive is likely inaccessible
        return True


_R = TypeVar("_R", covariant=True)
_P = ParamSpec("_P")


class _NetworkDriveRobustableFunc(Protocol[_P, _R]):
    """Call protocol for network drive-related scantree-related functions."""

    def __call__(
        self,
        path_to_check_network_drive: str | os.PathLike,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R: ...


def _network_drive_function_robustness(
    func: _NetworkDriveRobustableFunc[_P, _R],
) -> _NetworkDriveRobustableFunc[_P, _R]:
    """Scantree-related decorator that adds retry logic for network drive issues.

    This decorator adds retry logic to non-iterator/non-generator functions,
    i.e. those that have a standard `return`.

    The decorated function will, if an OSError is raised, test whether the path in
    question seems to be on a (currently) inaccessible Windows network drive. If so,
    it will retry, with increasing backoffs, until the network drive becomes
    accessible or maximum retries are reached.

    One retry (minimum) will always occur for network drive paths to avoid a
    momentary blip edge-case where the drive is inaccessible briefly, raising an
    exception, but is found to be accessible again by the time the check is made to
    determine if the whole drive is inaccessible or just that file.
    """

    @wraps(func)
    def _wrapper(
        path_to_check_network_drive: str | os.PathLike,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R:
        retry_count = 0
        is_windows_network_drive: Optional[bool] = None
        have_attempted_post_accessible = False

        while retry_count <= _NETWORK_DRIVE_RETRY_ATTEMPTS:
            try:
                return func(path_to_check_network_drive, *args, **kwargs)
            except OSError:
                # Check for this path (once) if it appears to be on a Windows network
                # drive
                if is_windows_network_drive is None:
                    is_windows_network_drive = _is_windows_network_drive(
                        path_to_check_network_drive
                    )

                # If not a Windows network drive, raise the exception immediately
                if not is_windows_network_drive:
                    raise

                # If the drive is inaccessible, wait for a while and try again
                if _windows_network_drive_inaccessible(path_to_check_network_drive):
                    retry_count += 1
                    backoff = compute_backoff(retry_count)
                    _logger.warning(
                        f"Network drive inaccessible: {path_to_check_network_drive}."
                        f" Retrying (attempt {retry_count})."
                        f" Sleeping for {backoff} seconds."
                    )
                    time.sleep(backoff)
                # If the drive is (now) accessible, and we have tried once already
                # since it seems to have become accessible, this is an actual issue
                # and we should re-raise the exception
                elif have_attempted_post_accessible:
                    raise
                # Otherwise, the drive appears to (now) be accessible, so we should
                # retry at least once in case this was just a temporary blip between
                # the initial scantree() call and the accessibility check
                else:
                    have_attempted_post_accessible = True
                    continue
        else:
            # If we've reached the maximum number of retries, give it one last try
            # and let the exception propagate if needed
            try:
                return func(path_to_check_network_drive, *args, **kwargs)
            except OSError as e:
                raise MaxNetworkDriveRetriesExceededError(
                    f"Max network drive retries"
                    f" ({_NETWORK_DRIVE_RETRY_ATTEMPTS} attempts)"
                    f" exceeded for {str(path_to_check_network_drive)}"
                ) from e

    return _wrapper


def _network_drive_generator_robustness(
    func: Callable[[str | os.PathLike], Iterator[_R]],
) -> Callable[[str | os.PathLike], Iterator[_R]]:
    """Scantree-related decorator that adds retry logic for network drive issues.

    This decorator is designed to work with iterators and will wrap the `yield from`
    logic in a retry loop so that if an error occurs in the underlying generator (
    which exhausts the generator and makes it unable to continue) it will start again
    with a new generator.

    The decorated generator will, if an OSError is raised, test whether the path in
    question seems to be on a (currently) inaccessible Windows network drive. If so,
    it will retry, with increasing backoffs, until the network drive becomes
    accessible or maximum retries are reached.

    One retry (minimum) will always occur for network drive paths to avoid a
    momentary blip edge-case where the drive is inaccessible briefly, raising an
    exception, but is found to be accessible again by the time the check is made to
    determine if the whole drive is inaccessible or just that file.
    """

    @wraps(func)
    def _wrapper(root: Union[str, os.PathLike]) -> Iterator[_R]:
        retry_count = 0
        is_windows_network_drive: Optional[bool] = None
        have_attempted_post_accessible = False

        while retry_count <= _NETWORK_DRIVE_RETRY_ATTEMPTS:
            try:
                yield from func(root)
            except OSError:
                # Check for this path (once) if it appears to be on a Windows network
                # drive
                if is_windows_network_drive is None:
                    is_windows_network_drive = _is_windows_network_drive(root)

                # If not a Windows network drive, raise the exception immediately
                if not is_windows_network_drive:
                    raise

                # If the drive is inaccessible, wait for a while and try again
                if _windows_network_drive_inaccessible(root):
                    retry_count += 1
                    backoff = compute_backoff(retry_count)
                    _logger.warning(
                        f"Network drive inaccessible: {root}."
                        f" Retrying (attempt {retry_count})."
                        f" Sleeping for {backoff} seconds."
                    )
                    time.sleep(backoff)
                # If the drive is (now) accessible, and we have tried once already
                # since it seems to have become accessible, this is an actual issue
                # and we should re-raise the exception
                elif have_attempted_post_accessible:
                    raise
                # Otherwise, the drive appears to (now) be accessible, so we should
                # retry at least once in case this was just a temporary blip between
                # the initial scantree() call and the accessibility check
                else:
                    have_attempted_post_accessible = True
                    continue
            else:
                # If no error occurs then we've successfully completed the iteration,
                # break out
                break
        else:
            # If we've reached the maximum number of retries, give it one last try
            # and let the exception propagate if needed
            try:
                yield from func(root)
            except OSError as e:
                raise MaxNetworkDriveRetriesExceededError(
                    f"Max network drive retries"
                    f" ({_NETWORK_DRIVE_RETRY_ATTEMPTS} attempts)"
                    f" exceeded for {str(root)}"
                ) from e

    return _wrapper


class MaxNetworkDriveRetriesExceededError(MaxRetriesExceededError):
    """Exception raised when the max number of network drive retries exceeded."""

    pass


@_network_drive_generator_robustness
def _robust_scandir_iterator(root: Union[str, os.PathLike]) -> Iterator[os.DirEntry]:
    """Robust scandir iteration with retry logic for network drive issues.

    Note that if an error occurs during the iteration, the whole iteration will start
    again. This is because the original iterator will be marked as exhausted
    following the exception.

    Thus it is possible for this generator to yield the same file multiple times and
    this should be handled by the caller.
    """
    with os.scandir(Path(root)) as it:
        yield from it


@_network_drive_function_robustness
def _robust_is_entry_dir(
    path_to_check_network_drive: str | os.PathLike, entry: os.DirEntry
) -> bool:
    """Robust check if an entry from scandir iteration is a directory."""
    # follow_symlinks=False as per https://peps.python.org/pep-0471/#examples
    return entry.is_dir(follow_symlinks=False)


def _scantree_robust_inner(root: Union[str, os.PathLike]) -> Iterator[os.DirEntry]:
    """Robust, recursive scandir-based iteration.

    Note that if an error occurs during the iteration, even if it is successfully
    handled and retried, the same file may be yielded multiple times. This should be
    handled by the caller.
    """
    # DEV: The following calls actually interact with the filesystem and so could
    # fail due to network drive issues:
    #   - os.scandir(): potentially getting initial directory info
    #   - _ScandirIterator.__next__(): makes syscall to get next file info
    #   - DirEntry.is_X(): _might_ make a syscall (but usually not)
    #
    # https://peps.python.org/pep-0471/#notes-on-exception-handling
    # https://docs.python.org/3/library/os.html#os.scandir
    for entry in _robust_scandir_iterator(root):
        # Recurse into subdirectories
        if _robust_is_entry_dir(entry.path, entry):
            yield from _scantree_robust_inner(entry.path)
        else:
            yield entry


def _scantree_robust(root: Union[str, os.PathLike]) -> Iterator[os.DirEntry]:
    """Recursively iterate through a folder as in scandir(), yielding file entries.

    This function contains additional robustness to handle network drive issues,
    primarily retries and backoffs. This additional resilience comes at the cost of
    slowdowns in the iteration of files and so should only be used if needed.
    """
    # Underlying calls in _scantree_robust_inner() may result in the same file being
    # yielded multiple times. We want to avoid this, providing the same experience as
    # will happen if _no_ network exceptions happen, and so we must keep track of
    # what has already been yielded.
    #
    # To avoid this list being held in memory (which would defeat one of the main
    # benefits of using iteration), we instead must persist it.

    # Use a UUID so that this is cache is unique for each specific call to scantree()
    already_yielded_cache = get_cache(
        cache_name=f"scantree_{uuid.uuid4()}", use_tmp_dir=True
    )

    try:
        for entry in _scantree_robust_inner(root):
            if entry.path not in already_yielded_cache:
                already_yielded_cache.add(entry.path)
                yield entry
    finally:
        # After processing all files, remove the cache
        already_yielded_cache.delete_cache()


def _scantree(root: Union[str, os.PathLike]) -> Iterator[os.DirEntry]:
    """Recursively iterate through a folder as in scandir(), yielding file entries."""
    with os.scandir(Path(root)) as it:
        for entry in it:
            # Recurse into subdirectories
            # follow_symlinks=False as per https://peps.python.org/pep-0471/#examples
            if entry.is_dir(follow_symlinks=False):
                yield from _scantree(entry.path)
            else:
                yield entry


def scantree(root: Union[str, os.PathLike]) -> Iterator[os.DirEntry]:
    """Recursively iterate through a folder as in scandir(), yielding file entries."""
    # Robustness is currently only supported on Windows, as it relies on being able
    # to identify network drives
    if config.settings.network_drive_robustness and platform.system() == "Windows":
        return _scantree_robust(root)
    else:
        return _scantree(root)
