"""Background file counting utility that works with any FileSystemIterableSource."""

from __future__ import annotations

import importlib
import logging
import multiprocessing
from multiprocessing import Process, Queue
from multiprocessing.synchronize import Event, Lock
import traceback
from typing import TYPE_CHECKING, Any, Dict, Optional

from bitfount.data.datasources.ophthalmology.ophthalmology_base_source import (
    OphthalmologyDataSourceArgs,
    _OphthalmologySource,
)
from bitfount.data.datasources.utils import FileSystemFilter

if TYPE_CHECKING:
    from bitfount.data.datasources.base_source import FileSystemIterableSource

logger = logging.getLogger(__name__)
DEFAULT_STOP_TIMEOUT = 0.5  # Default timeout for stopping the counting process
DEFAULT_QUEUE_TIMEOUT = 0.1  # Default timeout for getting results from the queue


class BackgroundFileCounter:
    """Non-intrusive background file counter for FileSystemIterableSource.

    Args:
        datasource: The FileSystemIterableSource to count files for.


    The BackgroundFileCounter class allows counting files in a
    FileSystemIterableSource while a task is executing in a different process.
    Using threads instead of processes is discouraged because it can block execution
    within the app, as the Flask server operates in a single-threaded mode, making
    file counting a blocking task.
    """

    def __init__(
        self,
        datasource: FileSystemIterableSource,
    ):
        self.datasource = datasource
        self._process: Optional[Process] = None
        self._stop_event: Event = multiprocessing.Event()
        self._total_count: Optional[int] = None
        self._counting_complete = False
        self._lock: Lock = multiprocessing.Lock()
        self._result_queue: Queue[int] = Queue()

    def start_counting(self) -> None:
        """Start background file counting."""
        if self._process is not None:
            logger.warning("Background counting already started")
            return

        # Serialize the datasource config
        config = serialize_datasource_configs(self.datasource)

        # Start the background process with the serialized config
        self._process = Process(
            target=self._count_files_background,
            args=(config, self._stop_event, self._result_queue),
            daemon=True,
        )
        self._process.start()
        logger.debug("Started background file counting process")

    def stop_counting(self) -> None:
        """Stop background file counting."""
        self._stop_event.set()
        if self._process and self._process.is_alive():
            self._process.join(timeout=DEFAULT_STOP_TIMEOUT)
            if self._process.is_alive():
                logger.warning("Background file counting process did not stop cleanly")
                self._process.terminate()
        logger.debug("Stopped background file counting")

    def get_count(self) -> Optional[int]:
        """Get current file count (None if counting not complete)."""
        if self._process is None:
            return None

        # If process is not alive, it has finished
        if not self._process.is_alive():
            # If we already have the count, return it
            if self._counting_complete:
                return self._total_count

            # Try to get the count from the queue
            try:
                # Use a short timeout to avoid blocking
                count = self._result_queue.get(timeout=DEFAULT_QUEUE_TIMEOUT)
                with self._lock:
                    self._total_count = count
                    self._counting_complete = True
                logger.debug(f"Got count from queue: {count}")
                return count
            except Exception as e:
                logger.error(f"Error getting count from queue: {str(e)}")
                return None

        # Process is still running
        return self._total_count if self._counting_complete else None

    def is_counting_complete(self) -> bool:
        """Check if counting is complete."""
        with self._lock:
            return self._counting_complete

    @staticmethod
    def _count_files_background(
        config: Dict[str, Any], stop_event: Event, result_queue: Queue
    ) -> None:
        """Background process function to count files."""
        try:
            logger.debug("Starting background file counting process...")

            # Recreate filter if it exists
            filter_obj = None
            if config.get("filter"):
                logger.debug("Creating filter object...")
                filter_obj = FileSystemFilter(
                    file_extension=config["filter"]["file_extension"],
                    strict_file_extension=config["filter"]["strict_file_extension"],
                    file_creation_min_date=config["filter"]["file_creation_min_date"],
                    file_modification_min_date=config["filter"][
                        "file_modification_min_date"
                    ],
                    file_creation_max_date=config["filter"]["file_creation_max_date"],
                    file_modification_max_date=config["filter"][
                        "file_modification_max_date"
                    ],
                    min_file_size=config["filter"]["min_file_size"],
                    max_file_size=config["filter"]["max_file_size"],
                )

            # Create datasource with ophthalmology args if they exist
            datasource_kwargs = {
                "path": config["path"],
                "file_pattern": config.get("file_pattern"),
                "filter": filter_obj,
            }

            if config.get("ophthalmology_args"):
                logger.debug("Adding ophthalmology args...")
                datasource_kwargs["ophthalmology_args"] = OphthalmologyDataSourceArgs(
                    **config["ophthalmology_args"]
                )

            # Import and use the original datasource class
            logger.info(f"Importing datasource class from {config['class_module']}...")
            module = importlib.import_module(config["class_module"])
            datasource_class = getattr(module, config["class_type"])
            datasource = datasource_class(**datasource_kwargs)

            if config.get("selected_file_names_override"):
                logger.debug("Setting selected file names override...")
                datasource.selected_file_names_override = config[
                    "selected_file_names_override"
                ]

            logger.info("Starting file iteration...")
            count = 0

            # Use the datasource's file_names_iter which handles all filtering
            for _ in datasource.file_names_iter(as_strs=True):
                if stop_event.is_set():
                    logger.debug("Stop event set, breaking...")
                    break
                count += 1
                if count % 100 == 0:  # Log progress every 100 files
                    logger.debug(f"Counted {count} files so far...")

            logger.info(f"Background file counting complete. Found {count} files.")
            result_queue.put(count)  # Put the result in the queue
            logger.info("Count put in queue")

        except Exception as e:
            logger.error(f"Error in background file counting: {str(e)}")
            logger.error(traceback.format_exc())
            result_queue.put(0)  # Put 0 in case of error
            logger.error("Error count (0) put in queue")


# Global registry for background file counters
_active_counters: Dict[int, BackgroundFileCounter] = {}


def start_background_file_counting(datasource: "FileSystemIterableSource") -> None:
    """Start background file counting for a datasource."""
    datasource_id = id(datasource)

    # Stop any existing counter for this datasource
    if datasource_id in _active_counters:
        _active_counters[datasource_id].stop_counting()

    # Create and start new counter
    counter = BackgroundFileCounter(datasource)
    counter.start_counting()
    _active_counters[datasource_id] = counter


def stop_background_file_counting(datasource: "FileSystemIterableSource") -> None:
    """Stop background file counting for a datasource."""
    datasource_id = id(datasource)
    if datasource_id in _active_counters:
        counter = _active_counters.pop(datasource_id)
        counter.stop_counting()


def get_background_file_count(datasource: "FileSystemIterableSource") -> Optional[int]:
    """Get the background file count for a datasource."""
    datasource_id = id(datasource)
    if datasource_id in _active_counters:
        return _active_counters[datasource_id].get_count()
    return None


def serialize_datasource_configs(
    datasource: "FileSystemIterableSource",
) -> Dict[str, Any]:
    """Create serializable data from datasource configuration.

    Args:
        datasource: The datasource to serialize

    Returns:
        Serialized datasource configuration
    """
    # Get filter config if it exists
    filter_config = None
    if hasattr(datasource, "filter") and datasource.filter is not None:
        filter_config = {
            "file_extension": datasource.filter.file_extension,
            "strict_file_extension": datasource.filter.strict_file_extension,
            "file_creation_min_date": datasource.filter.file_creation_min_date,
            "file_modification_min_date": datasource.filter.file_modification_min_date,
            "file_creation_max_date": datasource.filter.file_creation_max_date,
            "file_modification_max_date": datasource.filter.file_modification_max_date,
            "min_file_size": datasource.filter.min_file_size,
            "max_file_size": datasource.filter.max_file_size,
        }

    # Get ophthalmology args only if it's an ophthalmology source
    ophthalmology_args = None
    if isinstance(datasource, _OphthalmologySource) and hasattr(
        datasource, "ophthalmology_args"
    ):
        ophthalmology_args = {
            "modality": datasource.ophthalmology_args.modality,
            "match_slo": datasource.ophthalmology_args.match_slo,
            "drop_row_on_missing_slo": datasource.ophthalmology_args.drop_row_on_missing_slo,  # noqa: E501
            "minimum_dob": datasource.ophthalmology_args.minimum_dob,
            "maximum_dob": datasource.ophthalmology_args.maximum_dob,
            "minimum_num_bscans": datasource.ophthalmology_args.minimum_num_bscans,
            "maximum_num_bscans": datasource.ophthalmology_args.maximum_num_bscans,
        }

    return {
        "class_type": datasource.__class__.__name__,
        "class_module": datasource.__class__.__module__,
        "path": str(datasource.path),
        "selected_file_names_override": datasource.selected_file_names_override
        if hasattr(datasource, "selected_file_names_override")
        else [],
        "filter": filter_config,
        "ophthalmology_args": ophthalmology_args,
    }
