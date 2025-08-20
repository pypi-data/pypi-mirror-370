"""Resilience handling for batch execution in federated protocols.

This module handles batch resilience, individual file retry logic, error reporting,
and failure recovery mechanisms extracted from the main ProtocolExecution class.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Optional

import pandas as pd

from bitfount import config
from bitfount.federated.exceptions import BatchResilienceAbortError
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.protocols.types import ERROR_REPORT_FOLDER, BatchConfig
from bitfount.federated.protocols.utils import add_patient_metadata_columns
from bitfount.federated.transport.types import Reason
from bitfount.hooks import HookType, get_hooks

if TYPE_CHECKING:
    from bitfount.federated.protocols.base import BaseWorkerProtocol

logger = _get_federated_logger(__name__)


class ResilienceHandler:
    """Handles batch resilience, retry logic, and error reporting."""

    def __init__(
        self,
        protocol: BaseWorkerProtocol,
        hook_kwargs: dict,
        execute_run_func: Callable,
    ) -> None:
        self.protocol = protocol
        self.hook_kwargs = hook_kwargs
        self.execute_run_func = execute_run_func

    async def handle_batch_resilience_and_reporting(
        self, batch_config: BatchConfig
    ) -> None:
        """Handle batch resilience reporting and individual file retry logic.

        Args:
            batch_config: The batch configuration containing success/failure info.
        """
        if (
            not config.settings.enable_batch_resilience
            or not batch_config.failed_batches
        ):
            return

        logger.info(
            f"Batch processing completed. Summary: "
            f"{len(batch_config.successful_batches)} successful batches, "
            f"{len(batch_config.failed_batches)} failed batches"
        )

        if config.settings.individual_file_retry_enabled:
            failed_files = set()
            for batch_num in batch_config.failed_batches:
                files_in_batch = batch_config.failed_batch_file_mapping.get(
                    batch_num, []
                )
                failed_files.update(files_in_batch)
            if failed_files:
                for hook in get_hooks(HookType.POD):
                    hook.on_resilience_start(
                        task_id=getattr(self.protocol.mailbox, "task_id", None),
                        modeller_username=getattr(
                            self.protocol.mailbox, "modeller_name", ""
                        ),
                        total_failed_files=len(failed_files),
                    )
            logger.info("Starting individual file diagnosis phase...")

            await self.retry_failed_files_individually(batch_config)
            successful_files = sum(
                1 for result in batch_config.individual_file_results.values() if result
            )
            failed_files_count = (
                len(batch_config.individual_file_results) - successful_files
            )

            for hook in get_hooks(HookType.POD):
                hook.on_resilience_complete(
                    task_id=getattr(self.protocol.mailbox, "task_id", None),
                    modeller_username=getattr(
                        self.protocol.mailbox, "modeller_name", ""
                    ),
                    total_attempted=len(batch_config.individual_file_results),
                    total_succeeded=successful_files,
                    total_failed=failed_files_count,
                )
            # Check if we need to abort after individual file diagnosis
            await self.check_and_handle_zero_successful_files(batch_config)
        else:
            logger.debug(
                "Batch resilience enabled, but individual file retry disabled. "
                "Skipping individual file diagnosis."
            )
            # Check if we need to abort if all batches failed
            await self.check_and_handle_zero_successful_batches(batch_config)

        # Write report if resilience was enabled and there were failures
        self.write_failed_batches_report(batch_config)

    async def handle_batch_failure(
        self,
        error: Exception,
        batch_num: int,
        batch_config: BatchConfig,
    ) -> None:
        """Handle a batch failure with resilience logic.

        Args:
            error: The exception that caused the batch to fail
            batch_num: The batch number that failed
            batch_config: The batch configuration object

        Raises:
            The original exception if batch resilience is disabled
            BatchResilienceAbortError if consecutive failure threshold is reached
        """
        # If batch resilience is disabled, re-raise the original error
        if not config.settings.enable_batch_resilience:
            raise error

        # Track this batch failure and files in the batch
        batch_config.failed_batches[batch_num] = error
        batch_config.failed_batch_file_mapping[batch_num] = (
            batch_config.current_batch_files.copy()
        )
        batch_config.consecutive_failures += 1

        logger.warning(
            f"Batch {batch_num} failed with error: {error}. "
            f"Consecutive failures: {batch_config.consecutive_failures}",
            exc_info=True,
        )

        # Check if we should abort due to consecutive failures
        if (
            batch_config.consecutive_failures
            >= config.settings.max_consecutive_batch_failures
        ):
            error_msg = (
                f"Aborting task after {batch_config.consecutive_failures} "
                f"consecutive batch failures. Last error: {str(error)}"
            )
            logger.error(error_msg)

            # Send abort message to modeller
            await self.protocol.mailbox.send_task_abort_message(
                error_msg, Reason.WORKER_ERROR
            )

            # Raise the abort error
            raise BatchResilienceAbortError(
                error_msg,
                batch_config.consecutive_failures,
                batch_config.failed_batches,
            )
        # Continue with next batch
        logger.info(f"Continuing with next batch after failure in batch {batch_num}")
        return

    async def check_and_handle_zero_successful_batches(
        self, batch_config: BatchConfig
    ) -> None:
        """Check if all batches failed and handle task abort.

        Args:
            batch_config: The batch configuration object

        Raises:
            BatchResilienceAbortError: If all batches failed and no successful
                processing occurred, and individual file retry is not enabled
                or not applicable.
        """
        # Only check if batch resilience is enabled and we have failures
        # but no successes
        if not (
            config.settings.enable_batch_resilience
            and len(batch_config.successful_batches) == 0
            and len(batch_config.failed_batches) > 0
        ):
            return

        if config.settings.individual_file_retry_enabled:
            logger.info(
                f"All {len(batch_config.failed_batches)} batches failed, "
                f"but individual file retry is enabled. Will attempt "
                f"individual file diagnosis before aborting."
            )
            return

        # If individual file retry is not enabled, send a task abort message
        await self.abort_task_all_batches_failed(batch_config)

    async def abort_task_all_batches_failed(self, batch_config: BatchConfig) -> None:
        """Abort the task when all batches failed and no recovery is possible.

        Args:
            batch_config: The batch configuration object

        Raises:
            BatchResilienceAbortError: Always raised to abort the task
        """
        # Extract and deduplicate error messages
        error_messages = set()
        for _, error in batch_config.failed_batches.items():
            error_messages.add(str(error))

        # Create detailed error message
        if len(error_messages) == 1:
            # Single error type
            error_detail = f"Error: {list(error_messages)[0]}"
        else:
            # Multiple error types
            error_detail = "Errors: " + " | ".join(sorted(error_messages))

        error_msg = (
            f"Aborting task: All {len(batch_config.failed_batches)} batches failed. "
            f"No successful processing occurred. {error_detail}"
        )
        logger.error(error_msg)

        # Send abort message to modeller
        await self.protocol.mailbox.send_task_abort_message(
            error_msg, Reason.WORKER_ERROR
        )

        # Raise the abort error
        raise BatchResilienceAbortError(error_msg)

    async def check_and_handle_zero_successful_files(
        self, batch_config: BatchConfig
    ) -> None:
        """Check if both all batches failed AND all individual files failed.

        This is called after individual file diagnosis to determine if we should abort.

        Args:
            batch_config: The batch configuration object

        Raises:
            BatchResilienceAbortError: If no files succeeded in either batch
                or individual processing
        """
        # Check if we had no successful batches
        if len(batch_config.successful_batches) > 0:
            return  # We had some successful batches

        # Check if we had any successful individual files
        successful_individual_files = sum(
            1 for result in batch_config.individual_file_results.values() if result
        )

        if successful_individual_files > 0:
            logger.info(
                f"All batches failed, but {successful_individual_files} "
                f"{'file' if successful_individual_files == 1 else 'files'} "
                f"succeeded individually. Task will be marked as complete."
            )
            return  # We had some successful individual files

        # Both batches and individual files all failed - abort the task
        error_msg = (
            f"Aborting task: All {len(batch_config.failed_batches)} batches failed AND "
            f"all individual file retries failed. No successful processing occurred."
        )
        logger.error(error_msg)

        # Send abort message to modeller & raise error
        await self.protocol.mailbox.send_task_abort_message(
            error_msg, Reason.WORKER_ERROR
        )
        raise BatchResilienceAbortError(error_msg)

    async def retry_failed_files_individually(self, batch_config: BatchConfig) -> None:
        """Retry files from failed batches individually to identify problematic files.

        Test each file from failed batches individually to determine if the file itself
        is problematic or if the issue was batch-level (e.g., resource constraints).

        This runs as part of the batch execution flow, before the batch complete message
        is sent.

        Args:
            batch_config: The batch configuration for the worker.
        """
        # Collect all files from failed batches
        failed_files = set()
        for batch_num in batch_config.failed_batches:
            files_in_batch = batch_config.failed_batch_file_mapping.get(batch_num, [])
            failed_files.update(files_in_batch)

        if not failed_files:
            logger.info("No files to retry individually.")
            return

        logger.info(f"Individual file diagnosis: testing {len(failed_files)} files...")

        # Save current datasource state
        original_override = batch_config.datasource.selected_file_names_override.copy()

        successful_individual_files = 0
        failed_individual_files = 0

        for i, file_path in enumerate(failed_files, 1):
            try:
                # Set datasource to process only this file
                batch_config.datasource.selected_file_names_override = [file_path]

                # Reinitialize algorithms with single-file datasource
                for algo in self.protocol.algorithms:
                    algo.initialise_data(
                        datasource=batch_config.datasource,
                        data_splitter=batch_config.data_splitter,
                    )

                # Run the protocol on this single file
                logger.debug(
                    f"Testing individual file {i}/{len(failed_files)}: {file_path}"
                )
                # Only mark as final batch if this is the LAST file being retried
                is_final_individual_file = i == len(failed_files)

                await self.execute_run_func(final_batch=is_final_individual_file)

                # If we get here, the file processed successfully
                successful_individual_files += 1
                batch_config.individual_file_results[file_path] = True
                logger.debug(f"File processed successfully individually: {file_path}")
                # Call resilience progress hook for success
                for hook in get_hooks(HookType.POD):
                    hook.on_resilience_progress(
                        task_id=getattr(self.protocol.mailbox, "task_id", None),
                        modeller_username=getattr(
                            self.protocol.mailbox, "modeller_name", ""
                        ),
                        current_file=i,
                        total_files=len(failed_files),
                        file_name=file_path,
                        success=True,
                    )
            except Exception as e:
                # This file failed individually - it's genuinely problematic
                failed_individual_files += 1
                batch_config.file_level_errors[file_path] = e
                batch_config.individual_file_results[file_path] = False
                logger.debug(f"File failed individually: {file_path} - {str(e)}")
                for hook in get_hooks(HookType.POD):
                    hook.on_resilience_progress(
                        task_id=getattr(self.protocol.mailbox, "task_id", None),
                        modeller_username=getattr(
                            self.protocol.mailbox, "modeller_name", ""
                        ),
                        current_file=i,
                        total_files=len(failed_files),
                        file_name=file_path,
                        success=False,
                    )
        # Restore original datasource state
        batch_config.datasource.selected_file_names_override = original_override

        # Log summary
        logger.info(
            f"Individual file diagnosis completed: "
            f"{successful_individual_files} files succeeded individually, "
            f"{failed_individual_files} files failed individually"
        )

        # Log diagnostic insights
        if successful_individual_files > 0:
            logger.info(
                f"{successful_individual_files} files work individually but "
                f"failed in batch - this suggests resource constraints "
                f"or batch-level issues."
            )

        if failed_individual_files > 0:
            logger.info(
                f"{failed_individual_files} files are genuinely problematic and "
                f"should be investigated or removed from the dataset"
            )

    def get_algorithm_save_path(self) -> Path:
        """Find save_path from algorithms or return current directory.

        Returns:
            Path object for where to save the batch resilience report
        """
        # Get task_id for subdirectory creation (like CSV algorithm does)
        task_id: Optional[str] = None
        if hasattr(self.protocol.mailbox, "task_id"):
            task_id = self.protocol.mailbox.task_id
        # Check all algorithms for save_path attributes
        for algorithm in self.protocol.algorithms:
            # Check if the algorithm has a save_path attribute
            if hasattr(algorithm, "save_path"):
                save_path = algorithm.save_path
                if save_path:  # Not None or empty string
                    if task_id:
                        path = Path(save_path) / task_id / ERROR_REPORT_FOLDER
                    else:
                        path = Path(save_path) / ERROR_REPORT_FOLDER
                    # Create directory if it doesn't exist
                    path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Using algorithm save_path for batch report: {path}")
                    return path
            # Check for path attribute (worker-side algorithm instances)
            elif hasattr(algorithm, "path"):
                path_value = algorithm.path
                if path_value:  # Not None or empty string
                    if task_id:
                        path = Path(path_value) / task_id / ERROR_REPORT_FOLDER
                    else:
                        path = Path(path_value) / ERROR_REPORT_FOLDER
                    # Create directory if it doesn't exist
                    path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Using algorithm path for batch report: {path}")
                    return path
        # Fallback to current directory
        if task_id:
            current_path = Path.cwd() / task_id / ERROR_REPORT_FOLDER
        else:
            current_path = Path.cwd() / ERROR_REPORT_FOLDER
        current_path.mkdir(parents=True, exist_ok=True)
        logger.info(
            f"No algorithm save_path found, using current directory: {current_path}"
        )
        return current_path

    def write_failed_batches_report(self, batch_config: BatchConfig) -> None:
        """Write CSV report for all failed batches and their files.

        If individual file retry is enabled, creates a detailed file-level report.
        Otherwise, creates a batch-level report.
        """
        if not batch_config.failed_batches:
            return  # No failures to report

        # Find save path from algorithms or use current directory
        save_path = self.get_algorithm_save_path()

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Choose report type based on whether individual file retry was enabled
        if (
            config.settings.individual_file_retry_enabled
            and batch_config.individual_file_results
        ):
            # Create detailed file-level report
            output_file = save_path / f"File_error_report_{timestamp}.csv"
            data = self.build_file_level_report_data(batch_config, report_timestamp)
            report_type = "file-level diagnosis"
        else:
            # Create batch-level report (original behavior)
            output_file = save_path / f"Batch_error_report_{timestamp}.csv"
            data = self.build_batch_level_report_data(batch_config, report_timestamp)
            report_type = "batch failure"

        try:
            # Create DataFrame and write to CSV
            df = pd.DataFrame(data)
            df.to_csv(output_file, index=False)
            logger.info(f"{report_type.title()} CSV report written to: {output_file}")

        except Exception as e:
            logger.error(f"Failed to write {report_type} CSV report: {e}")

        hook_kwargs = self.hook_kwargs.copy()
        hook_kwargs["batch_config"] = batch_config
        if (
            config.settings.individual_file_retry_enabled
            and config.settings.enable_batch_resilience
        ):
            try:
                for hook in get_hooks(HookType.PROTOCOL):
                    hook.on_resilience_end(self.protocol, **hook_kwargs)
            except Exception as e:
                logger.error(f"`on_resilience_end` hook failed: {e}")

    def build_file_level_report_data(
        self, batch_config: BatchConfig, report_timestamp: str
    ) -> list[dict]:
        """Build data for file-level diagnosis report.

        Args:
            batch_config: The batch configuration object
            report_timestamp: Timestamp for the report

        Returns:
            List of dictionaries containing file-level diagnosis data
        """
        data = []

        # Collect all files from failed batches
        all_failed_batch_files = set()
        for batch_num in batch_config.failed_batches:
            files_in_batch = batch_config.failed_batch_file_mapping.get(batch_num, [])
            all_failed_batch_files.update(files_in_batch)

        # Create a row for each file that was in a failed batch
        for file_path in sorted(all_failed_batch_files):
            # Determine the individual test result
            individual_result = batch_config.individual_file_results.get(
                file_path, "Not tested"
            )

            if individual_result is True:
                individual_status = "Success"
                individual_error = "No error. File processed successfully on retry."
                diagnosis = "Batch-level issue (resource constraints, timing, etc.)"
            elif individual_result is False:
                individual_status = "Failed"
                individual_error = str(
                    batch_config.file_level_errors.get(file_path, "Unknown error")
                )
                diagnosis = "File-level issue (corrupted file, processing error, etc.)"
            else:
                individual_status = "Not tested"
                individual_error = "Individual file diagnosis was not performed"
                diagnosis = "Unknown - file not tested individually"

            # Find which batch(es) this file was in
            batch_numbers = []
            for (
                batch_num,
                files_in_batch,
            ) in batch_config.failed_batch_file_mapping.items():
                if file_path in files_in_batch:
                    batch_numbers.append(str(batch_num))

            batch_info = ", ".join(batch_numbers) if batch_numbers else "Unknown"
            row_data: dict[str, Any] = {}
            # Add patient metadata columns if available
            add_patient_metadata_columns(row_data, batch_config.datasource, file_path)
            row_data.update(
                {
                    "File path": file_path,
                    "Batch number": batch_info,
                    "Retry result": individual_status,
                    "Error": individual_error,
                    "Diagnosis": diagnosis,
                    "Report generated": report_timestamp,
                }
            )
            data.append(row_data)

        return data

    def build_batch_level_report_data(
        self, batch_config: BatchConfig, report_timestamp: str
    ) -> list[dict]:
        """Build data for batch-level failure report (original behavior).

        Args:
            batch_config: The batch configuration object
            report_timestamp: Timestamp for the report

        Returns:
            List of dictionaries containing batch-level failure data
        """
        data = []

        for batch_num, error in sorted(batch_config.failed_batches.items()):
            files_in_batch = batch_config.failed_batch_file_mapping.get(batch_num, [])
            for file_path in files_in_batch:
                row_data: dict[str, Any] = {}
                # Add patient metadata columns if available
                add_patient_metadata_columns(
                    row_data, batch_config.datasource, file_path
                )
                row_data.update(
                    {
                        "Batch number": batch_num,
                        "Error": str(error),
                        "File path": file_path,
                        "Report generated": report_timestamp,
                        "Total number of successful batches": len(
                            batch_config.successful_batches
                        ),
                        "Total number of failed batches": len(
                            batch_config.failed_batches
                        ),
                    }
                )
                data.append(row_data)

        return data
