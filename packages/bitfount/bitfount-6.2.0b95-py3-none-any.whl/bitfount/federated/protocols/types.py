"""Batch execution types and data structures for protocols.

This module contains the core data structures and constants used for batch execution
in federated protocols, extracted from the main base.py to improve modularity.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final, Optional

import more_itertools

from bitfount.data.datasources.base_source import FileSystemIterableSource
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.types import DataSplit
from bitfount.types import _StrAnyDict

# Constants for protocol execution
MAXIMUM_SLEEP_TIME: Final = 10
BATCH_ID_RETRY_DELAY: Final = 0.5
MAXIMUM_RETRIES: Final = 60
ERROR_REPORT_FOLDER: Final = "Error report"


class TerminationReason(Enum):
    """Enumeration of protocol termination reasons."""

    LIMITS_EXCEEDED = "limits_exceeded"
    FINAL_BATCH = "final_batch"
    SINGLE_BATCH = "single_batch"


@dataclass
class ProtocolState:
    """Context for managing batch execution state and early termination.

    Args:
        execute_final_step: Whether to execute the final step of the protocol.
            Defaults to False.
        termination_reason: Optional. The reason for terminating the protocol
            execution early. Defaults to None.
        reduce_step_kwargs: Optional. Keyword arguments for the final reduce step.
            Defaults to None.
    """

    execute_final_step: bool = False
    termination_reason: Optional[TerminationReason] = None
    reduce_step_kwargs: Optional[_StrAnyDict] = None


class BatchConfig:
    """Holds batch configuration and state.

    Args:
        batch_size: The size of each batch.
        data_splitter: The dataset splitter to use for splitting the data.
        datasource: The datasource from which to read the data.
        original_file_names_override: Optional. Override for the original file names
            used in the datasource. Used for restoring `selected_file_names_override`
             on the datasource the at the end of the task.
        is_final_batch: Whether this is the final batch. Defaults to False.

    Attributes:
        batch_size: The size of each batch.
        data_splitter: The dataset splitter to use for splitting the data.
        datasource: The datasource from which to read the data.
        original_file_names_override: Optional. Override for the original file names
            used in the datasource. Used for restoring `selected_file_names_override`
            on the datasource at the end of the task.
        current_batch: The current batch number.
        current_files_iterator: An iterator over the filenames for the current batch.
        is_final_batch: Whether this is the final batch.
        current_batch_files: The list of files in the current batch.
        has_new_files: Whether any new files have been found (for run_on_new_data_only).
        total_files_checked: Total number of files checked so far.
        _sent_batch_count_update: Whether we've sent batch count update to modeller.
        failed_batches: Dictionary mapping batch numbers to their failure exceptions.
        consecutive_failures: Count of consecutive batch failures.
        successful_batches: List of batch numbers that processed successfully.
        file_level_errors: Dictionary mapping file paths to their failure exceptions.
        individual_file_results: Dictionary mapping file paths to individual
            test results.
    """

    def __init__(
        self,
        batch_size: int,
        data_splitter: DatasetSplitter,
        datasource: FileSystemIterableSource,
        original_file_names_override: Optional[list[str]],
        is_final_batch: bool = False,
    ):
        self.batch_size = batch_size
        self.data_splitter = data_splitter
        self.datasource = datasource
        self.original_file_names_override = original_file_names_override
        self.current_batch = 0
        self.current_files_iterator = more_itertools.peekable(
            self.data_splitter.iter_filenames(
                datasource=datasource, split=DataSplit.TEST
            )
        )
        self.is_final_batch = is_final_batch
        self.current_batch_files: list[str] = []
        # Track if any new files have been found
        # (for tasks with run_on_new_data_only set to True)
        self.has_new_files = False
        self.total_files_checked = 0
        # Track if we've sent batch count update to modeller
        self._sent_batch_count_update = False

        # Batch state tracking
        self.failed_batches: dict[int, Exception] = {}
        self.consecutive_failures = 0
        self.successful_batches: list[int] = []
        self.file_level_errors: dict[str, Exception] = {}
        # Track which files were in each batch
        self.failed_batch_file_mapping: dict[int, list[str]] = {}
        # file_path -> True/False indicating if the individual
        # file re-run was successful or not
        self.individual_file_results: dict[str, bool] = {}
