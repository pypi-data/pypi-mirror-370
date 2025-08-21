"""Module containing BaseSource class.

BaseSource is the abstract data source class from which all concrete data sources
must inherit.
"""

from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod
from collections.abc import Iterable, Iterator, Sequence, Sized
import contextlib
from datetime import datetime
from functools import cached_property
import logging
from logging.handlers import QueueHandler
import os
from pathlib import Path
import traceback
from typing import (
    TYPE_CHECKING,
    Any,
    Final,
    List,
    Literal,
    Optional,
    Protocol,
    TypeVar,
    Union,
    cast,
    overload,
)
import warnings

import pandas as pd
import psutil
from typing_extensions import override

from bitfount import config
from bitfount.data.datasources.types import DataSourceFileFilter
from bitfount.data.datasources.utils import (
    FILE_SYSTEM_ITERABLE_METADATA_COLUMNS,
    LAST_MODIFIED_METADATA_COLUMN,
    ORIGINAL_FILENAME_METADATA_COLUMN,
    FileSystemFilter,
    _modify_column,
)
from bitfount.data.exceptions import IterableDataSourceError
from bitfount.data.persistence.base import DataPersister
from bitfount.data.persistence.sqlite import SQLiteDataPersister
from bitfount.data.types import (
    DataPathModifiers,
    SingleOrMulti,
)
from bitfount.data.utils import partition
from bitfount.hooks import DataSourceHook, HookType, get_hooks
from bitfount.types import _JSONDict
from bitfount.utils import delegates, seed_all
from bitfount.utils.fs_utils import scantree
from bitfount.utils.logging_utils import (
    SampleFilter,
    _get_bitfount_console_handler,
    _get_bitfount_log_file_handler,
)

if TYPE_CHECKING:
    from queue import Queue

    from bitfount.data.datasplitters import DatasetSplitter

logger = logging.getLogger(__name__)
logger.addFilter(SampleFilter())


class _BaseSourceMeta(ABCMeta):
    """Metaclass for BaseSource that enforces schema consistency.

    Ensures that if a class has has_predefined_schema = True, then it must
    properly override the get_schema() method.
    """

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> type:
        # Create the class first
        new_class = super().__new__(cls, name, bases, namespace, **kwargs)

        # Skip validation for the base BaseSource class itself
        if name == "BaseSource":
            return new_class

        # Check if this class has predefined schema
        has_predefined_schema = getattr(new_class, "has_predefined_schema", False)

        if has_predefined_schema:
            # Check if get_schema is properly implemented
            get_schema_method = getattr(new_class, "get_schema", None)

            # Check if the method exists and is not the base implementation
            if get_schema_method is None:
                raise TypeError(
                    f"Class {name} has has_predefined_schema = True but does not define get_schema() method"  # noqa: E501
                )

            # Check if it's the base implementation (which raises NotImplementedError)
            # We do this by checking the method resolution order
            for base in new_class.__mro__:
                if hasattr(base, "get_schema") and "get_schema" in base.__dict__:
                    # Found the class that defines get_schema
                    if base.__name__ == "BaseSource":
                        # If the defining class is BaseSource, then it's not overridden
                        raise TypeError(
                            f"Class {name} has has_predefined_schema = True but does "
                            f"not override get_schema() method from BaseSource. Please "
                            f"implement get_schema() to return the pre-defined schema."
                        )
                    break

        return new_class


# This is used for annotating the data in the datasource with
# the inferred label
BITFOUNT_INFERRED_LABEL_COLUMN: str = "BITFOUNT_INFERRED_LABEL"

# This determines the maximum number of multiprocessing workers that can be used
# for file processing parallelisation.
MAX_NUM_MULTIPROCESSING_WORKERS: Final[int] = 5

# TypeVar for iterable elements
_I = TypeVar("_I")


class _LockType(contextlib.AbstractContextManager, Protocol):
    """Protocol for the Multiprocessing Manager Lock class."""

    def acquire(self, block: bool, timeout: float) -> bool:
        """Acquire the lock."""

    def release(self) -> None:
        """Release the lock."""


class BaseSource(Sized, ABC, metaclass=_BaseSourceMeta):
    """Abstract Base Source from which all other data sources must inherit.

    This is used for streaming data in batches as opposed to loading the entire dataset
    into memory.

    Args:
        data_splitter: Deprecated argument, will be removed in a future release.
            Defaults to None. Not used.
        seed: Random number seed. Used for setting random seed for all libraries.
            Defaults to None.
        ignore_cols: Column/list of columns to be ignored from the data.
            Defaults to None.
        modifiers: Dictionary used for modifying paths/ extensions in the dataframe.
            Defaults to None.
        partition_size: The size of each partition when iterating over the data in a
            batched fashion.

    Attributes:
        seed: Random number seed. Used for setting random seed for all libraries.
    """

    # Indicates whether this datasource has a pre-defined schema that should be used
    # instead of generating one from the data. Subclasses can override this.
    has_predefined_schema: bool = False

    # TODO: [BIT-3722] Method Resolution Order appears to be broken such that if methods
    # that are defined in a base class are overridden in a subclass, the base class
    # implementation is preferentially called over the subclass implementation. Be
    # mindful of this when overriding methods.

    def __init__(
        self,
        data_splitter: Optional[DatasetSplitter] = None,
        seed: Optional[int] = None,
        ignore_cols: Optional[Union[str, Sequence[str]]] = None,
        iterable: bool = True,
        modifiers: Optional[dict[str, DataPathModifiers]] = None,
        partition_size: int = config.settings.task_batch_size,
        required_fields: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        if data_splitter is not None:
            warnings.warn(
                "data_splitter is deprecated and will be removed in a future release."
                " Data splitting is now handled externally to the datasource.",
                DeprecationWarning,
            )
        if not iterable:
            warnings.warn(
                "iterable=False is deprecated and will be removed in a future release."
                " All datasources are now iterable.",
                DeprecationWarning,
            )

        self._base_source_init = True

        self.seed = seed
        seed_all(self.seed)

        self._modifiers = modifiers
        self._is_task_running: bool = False

        # TODO: [BIT-3486] Make partition size configurable?
        self.partition_size = partition_size
        self._hooks: List[DataSourceHook] = []

        self._table_hashes: set[str] = set()

        self._ignore_cols: list[str] = []
        if isinstance(ignore_cols, str):
            self._ignore_cols = [ignore_cols]
        elif ignore_cols is not None:
            self._ignore_cols = list(ignore_cols)

        self.image_columns: set[str] = set()
        self.required_fields = required_fields
        for unexpected_kwarg in kwargs:
            logger.warning(f"Ignoring unexpected keyword argument {unexpected_kwarg}")

        super().__init__()

    ####################
    # Datasource State #
    ####################
    @property
    def is_task_running(self) -> bool:
        """Returns True if a task is running."""
        return self._is_task_running

    @is_task_running.setter
    def is_task_running(self, value: bool) -> None:
        """Sets `_is_task_running` to `value`."""
        self._is_task_running = value

    @property
    def is_initialised(self) -> bool:
        """Checks if `BaseSource` was initialised."""
        if hasattr(self, "_base_source_init"):
            return True
        else:
            return False

    #########
    # Hooks #
    #########
    def add_hook(self, hook: DataSourceHook) -> None:
        """Add a hook to the datasource."""
        self._hooks.append(hook)
        hook.register()  # Register the hook when added

    def remove_hook(self, hook: DataSourceHook) -> None:
        """Remove a hook from the datasource."""
        if hook in self._hooks:
            self._hooks.remove(hook)
            hook.deregister()  # Deregister the hook when removed

    ############################
    # Data output modification #
    ############################
    def apply_modifiers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply column modifiers to the dataframe.

        If no modifiers are specified, returns the dataframe unchanged.
        """
        if self._modifiers is not None:
            for col_name in self._modifiers.keys():
                column = df[col_name]
                column = _modify_column(column, self._modifiers[col_name])  # type: ignore[assignment] # Reason: Mypy complains that column not Union[np.ndarray, pd.Series]. #noqa: E501
                df[col_name] = column
        return df

    def apply_ignore_cols(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply ignored columns to dataframe, dropping columns as needed.

        Returns:
            A copy of the dataframe with ignored columns removed, or the original
            dataframe if this datasource does not specify any ignore columns.
        """
        if self._ignore_cols:
            return df.drop(columns=self._ignore_cols, errors="ignore")
        else:
            return df

    def apply_ignore_cols_iter(
        self, dfs: Iterator[pd.DataFrame]
    ) -> Iterator[pd.DataFrame]:
        """Apply ignored columns to dataframes from iterator.

        Yields:
            A copy of dataframes from the iterator with ignored columns removed,
            or the original dataframes from the iterator if this datasource does not
            specify any ignore columns.
        """
        if not self._ignore_cols:
            yield from dfs
        else:
            for df in dfs:
                yield df.drop(columns=self._ignore_cols, errors="ignore")

    def get_schema(self) -> _JSONDict:
        """Get the pre-defined schema for this datasource.

        This method should be overridden by datasources that have pre-defined schemas
        (i.e., those with has_predefined_schema = True).

        Returns:
            The schema as a dictionary.

        Raises:
            NotImplementedError: If the datasource doesn't have a pre-defined schema.
        """
        raise NotImplementedError(
            f"Datasource {type(self).__name__} does not implement get_schema(). "
            f"This method should only be called on datasources with "
            f"has_predefined_schema = True."
        )

    ############################
    # Map-style Data Retrieval #
    ############################
    def get_data(
        self,
        data_keys: SingleOrMulti[str],
        *,
        use_cache: bool = True,
        **kwargs: Any,
    ) -> Optional[pd.DataFrame]:
        """Get data corresponding to the provided data key(s).

        Can be used to return data for a single data key or for multiple at once. If
        used for multiple, the order of the output dataframe must match the order of
        the keys provided.

        Args:
            data_keys: Key(s) for which to get the data of. These may be things such as
                file names, UUIDs, etc.
            use_cache: Whether the cache should be used to retrieve data for these
                keys. Note that cached data may have some elements, particularly
                image-related fields such as image data or file paths, replaced
                with placeholder values when stored in the cache. If data_cache is
                set on the instance, data will be _set_ in the cache, regardless of
                this argument.
            **kwargs: Additional keyword arguments.

        Returns:
            A dataframe containing the data, ordered to match the order of keys
            in `data_keys`, or None if no data for those keys was available.
        """
        data = self._get_data(data_keys, use_cache=use_cache, **kwargs)

        for hook in self._hooks:
            try:
                hook.on_datasource_get_data(data)
            except NotImplementedError:
                logger.debug(
                    f"{hook.hook_name} does not implement `on_datasource_get_data`."
                )
            except Exception as e:
                logger.error(f"Error in hook {hook.hook_name}: {e}")

        if not data.empty:
            return data
        else:
            return None

    @abstractmethod
    def _get_data(
        self,
        data_keys: SingleOrMulti[str],
        *,
        use_cache: bool = True,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Get data corresponding to the provided data key(s).

        :::note

        Implementation method for `get_data()`. See that method as the "source of
        truth" for the docstring.

        :::

        Can be used to return data for a single data key or for multiple at once. If
        used for multiple, the order of the output dataframe must match the order of
        the keys provided.

        Args:
            data_keys: Key(s) for which to get the data of. These may be things such as
                file names, UUIDs, etc.
            use_cache: Whether the cache should be used to retrieve data for these
                keys. Note that cached data may have some elements, particularly
                image-related fields such as image data or file paths, replaced
                with placeholder values when stored in the cache. If data_cache is
                set on the instance, data will be _set_ in the cache, regardless of
                this argument.
            **kwargs: Additional keyword arguments.

        Returns:
            A dataframe containing the data, ordered to match the order of keys
            in `data_keys`
        """
        raise NotImplementedError

    #################################
    # Iterable-style Data Retrieval #
    #################################
    def __iter__(self) -> Iterator[pd.DataFrame]:
        """Iterate through the data, one data point at a time."""
        return self.yield_data(partition_size=1)

    def yield_data(
        self,
        data_keys: Optional[SingleOrMulti[str]] = None,
        *,
        use_cache: bool = True,
        partition_size: Optional[int] = None,
        **kwargs: Any,
    ) -> Iterator[pd.DataFrame]:
        """Yields data in batches from this source.

        If data_keys is specified, only yield from that subset of the data.
        Otherwise, iterate through the whole datasource.

        Args:
            data_keys: An optional list of data keys to use for yielding data.
                Otherwise, all data in the datasource will be considered.
                `data_keys` is always provided when this method is called from the
                Dataset as part of a task.
            use_cache: Whether the cache should be used to retrieve data for these
                data points. Note that cached data may have some elements, particularly
                image-related fields such as image data or file paths, replaced
                with placeholder values when stored in the cache. If data_cache is
                set on the instance, data will be _set_ in the cache, regardless of
                this argument.
            partition_size: The number of data elements to load/yield in each
                iteration. If not provided, defaults to the partition size configured
                in the datasource.
            **kwargs: Additional keyword arguments.

        Yields:
            Dataframes that contain the data related to each batch of data points,
            in `partition_size` batches. Any batches that are empty will be skipped.
        """
        for data in self._yield_data(
            data_keys, use_cache=use_cache, partition_size=partition_size, **kwargs
        ):
            for hook in self._hooks:
                try:
                    hook.on_datasource_yield_data(data)
                except NotImplementedError:
                    logger.warning(
                        f"{hook.hook_name} does not implement "
                        "`on_datasource_yield_data`."
                    )
                except Exception as e:
                    logger.error(f"Error in hook {hook.hook_name}: {e}")

            if not data.empty:
                yield data

    @abstractmethod
    def _yield_data(
        self,
        data_keys: Optional[SingleOrMulti[str]] = None,
        *,
        use_cache: bool = True,
        partition_size: Optional[int] = None,
        **kwargs: Any,
    ) -> Iterator[pd.DataFrame]:
        """Yields data in batches from this source.

        :::note

        Implementation method for `yield_data()`. See that method as the "source of
        truth" for the docstring.

        :::

        If data_keys is specified, only yield from that subset of the data.
        Otherwise, iterate through the whole datasource.

        Args:
            data_keys: An optional list of data keys to use for yielding data.
                Otherwise, all data in the datasource will be considered.
                `data_keys` is always provided when this method is called from the
                Dataset as part of a task.
            use_cache: Whether the cache should be used to retrieve data for these
                data points. Note that cached data may have some elements, particularly
                image-related fields such as image data or file paths, replaced
                with placeholder values when stored in the cache. If data_cache is
                set on the instance, data will be _set_ in the cache, regardless of
                this argument.
            partition_size: The number of data elements to load/return in each
                iteration. If not provided,
            **kwargs: Additional keyword arguments.

        Yields:
            Dataframes that contain the data related to each batch of data points,
            in `partition_size` batches.
        """
        raise NotImplementedError

    def partition(
        self, iterable: Iterable[_I], partition_size: int = 1
    ) -> Iterable[Sequence[_I]]:
        """Takes an iterable and yields partitions of size `partition_size`.

        The final partition may be less than size `partition_size` due to the variable
        length of the iterable.
        """
        yield from partition(iterable, partition_size)

    def __len__(self) -> int:
        """Get len for iterable datasource."""
        chunk_lens: Iterable[int] = map(len, self.yield_data())
        return sum(chunk_lens)

    ############################
    # Project Database Methods #
    ############################
    @property
    def supports_project_db(self) -> bool:
        """Whether the datasource supports the project database.

        Each datasource needs to implement its own methods to define how what its
        project database table should look like. If the datasource does not implement
        the methods to get the table creation query and columns, it does not support the
        projectdatabase.
        """
        try:
            self.get_project_db_sqlite_create_table_query()
            self.get_project_db_sqlite_columns()
            return True
        except NotImplementedError:
            return False
        except Exception as e:
            logger.warning(
                f"Unexpected error in determining if {self.__class__.__name__} supports the project database: {e}"  # noqa: E501
            )
            return False

    def get_project_db_sqlite_create_table_query(self) -> str:
        """Implement this method to return the required columns and types.

        This is used by the "run on new data only" feature. This should be in the format
        that can be used after a "CREATE TABLE" statement and is used to create the task
        table in the project database.
        """
        raise NotImplementedError

    def get_project_db_sqlite_columns(self) -> list[str]:
        """Implement this method to get the required columns.

        This is used by the "run on new data only" feature. This is used to add data to
        the task table in the project database.
        """
        raise NotImplementedError

    ###################
    # Utility Methods #
    ###################
    @staticmethod
    def _convert_to_multi(som: SingleOrMulti[str]) -> list[str]:
        # If already list, return unchanged
        if isinstance(som, list):
            return som
        elif isinstance(som, str):
            return [som]
        else:
            return list(som)


class MultiProcessingMixIn:
    """MixIn class for multiprocessing of `_get_data`."""

    skipped_files: set[str]
    image_columns: set[str]
    data_cache: Optional[DataPersister]

    @abstractmethod
    def _get_data(
        self,
        data_keys: SingleOrMulti[str],
        *,
        use_cache: bool = True,
        skip_non_tabular_data: bool = False,
        **kwargs: Any,
    ) -> pd.DataFrame: ...

    @staticmethod
    def get_num_workers(file_names: Sequence[str]) -> int:
        """Gets the number of workers to use for multiprocessing.

        Ensures that the number of workers is at least 1 and at most equal to
        MAX_NUM_MULTIPROCESSING_WORKERS. If the number of files is less than
        MAX_NUM_MULTIPROCESSING_WORKERS, then we use the number of files as the
        number of workers. Unless the number of machine cores is also less than
        MAX_NUM_MULTIPROCESSING_WORKERS, in which case we use the lower of the
        two.

        Args:
            file_names: The list of file names to load.

        Returns:
            The number of workers to use for multiprocessing.
        """
        cpu_count = psutil.cpu_count(logical=False) or 1
        return min(
            max(1, len(file_names)),
            # Make sure we don't use all the available cores
            max(1, cpu_count - 1),
            MAX_NUM_MULTIPROCESSING_WORKERS,
        )

    def use_file_multiprocessing(self, file_names: Sequence[str]) -> bool:
        """Check if file multiprocessing should be used.

        Returns True if file multiprocessing has been enabled by the environment
        variable and the number of workers would be greater than 1, otherwise False.
        There is no need to use file multiprocessing if we are just going to use one
        worker - it would be slower than just loading the data in the main process.

        Returns:
            True if file multiprocessing should be used, otherwise False.
        """
        if config.settings.file_multiprocessing_enabled:
            return self.get_num_workers(file_names) > 1
        return False

    @staticmethod
    def _mp_configure_listener_logger(log_file_name: str) -> None:
        """Configure the logger for the listener process.

        Adds the same handlers as the main process logger to the listener process
        logger. This requires passing the name of the log file to use to the listener
        because otherwise it can't be found because it has a timestamp in the name.

        Args:
            log_file_name: The name of the log file to use.
        """
        logger = logging.getLogger()
        logger.addHandler(_get_bitfount_log_file_handler(log_file_name=log_file_name))
        logger.addHandler(_get_bitfount_console_handler())
        logger.propagate = False

    @classmethod
    def _mp_listener_process(cls, queue: Queue, log_file_name: str) -> None:
        """Process that listens for log messages from the worker processes.

        Whenever a log message is received, it is handled by the logger.

        Args:
            queue: The queue to listen on.
            log_file_name: The name of the log file to use.
        """
        cls._mp_configure_listener_logger(log_file_name)
        while True:
            try:
                record = queue.get()
                if record is None:  # Sentinel to tell the listener to quit
                    break
                logger.handle(record)
            except Exception:
                import traceback

                traceback.print_exc()

    @staticmethod
    def _mp_configure_worker_logger(queue: Queue) -> None:
        """Configure the logger for the worker processes.

        Adds a QueueHandler to the logger to send log messages to the listener process.

        Args:
            queue: The queue to send log messages to.
        """
        h = QueueHandler(queue)
        bf_logger = logging.getLogger("bitfount")
        bf_logger.setLevel(logging.DEBUG)
        plugins_logger = logging.getLogger("plugins")
        plugins_logger.setLevel(logging.DEBUG)
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.WARNING)
        for _logger in (bf_logger, plugins_logger, root_logger):
            _logger.handlers.clear()  # Clear existing handlers
            _logger.addHandler(h)
            _logger.propagate = False

    def _mp_worker_get_data_process(
        self,
        queue: Queue,
        sqlite_path: Optional[Path],
        lock: _LockType,
        file_names: list[str],
        use_cache: bool = True,
        **kwargs: Any,
    ) -> tuple[pd.DataFrame, list[str], list[str]]:
        """Process that calls `_get_data` to load data.

        This is called by the main process to load data in parallel. This method
        configures the logger for the worker process and calls `_get_data`.

        Args:
            queue: The queue to send log messages to.
            sqlite_path: The path to the SQLite file to use for recreating the data
                cache.
            lock: The lock to use for accessing the data cache.
            file_names: The list of file names to load.
            use_cache: Whether the cache should be used to retrieve data for these
                files. Note that cached data may have some elements, particularly
                image-related fields such as image data or file paths, replaced
                with placeholder values when stored in the cache.

                If data_cache is set on the instance, data will be _set_ in the
                cache, regardless of this argument.
            kwargs: Keyword arguments to pass to `_get_data`.

        Returns:
            The loaded data as a dataframe, a list of skipped files and a list of image
            columns. The skipped files and image columns are returned so that they can
            be added to the `skipped_files` and `image_columns` sets respectively
            in the main process - otherwise this information would be lost when the
            worker process is terminated. The skipped files and images columns are
            returned as a list rather than a set because sets are not pickleable.
        """
        logger.debug(f"Using cache: {use_cache}")
        if sqlite_path:
            logger.debug(f"Recreating data cache from {sqlite_path}.")
            self.data_cache = SQLiteDataPersister(sqlite_path, lock=lock)
        self._mp_configure_worker_logger(queue)
        data = self._get_data(data_keys=file_names, use_cache=use_cache, **kwargs)
        return data, list(self.skipped_files), list(self.image_columns)

    def _mp_get_data(
        self, data_keys: Sequence[str], use_cache: bool = True, **kwargs: Any
    ) -> pd.DataFrame:
        """Call `_get_data` in parallel.

        This method sets up the multiprocessing queue and processes and calls
        `_get_data` in parallel. It also sets up the listener process to handle log
        messages from the worker processes.

        Args:
            data_keys: The list of file names to load.
            use_cache: Whether the cache should be used to retrieve data for these
                files. Note that cached data may have some elements, particularly
                image-related fields such as image data or file paths, replaced
                with placeholder values when stored in the cache.

                If data_cache is set on the instance, data will be _set_ in the
                cache, regardless of this argument.
            kwargs: Keyword arguments to pass to `_get_data`.

        Returns:
            The loaded data as a dataframe.
        """
        from concurrent.futures import Future, ProcessPoolExecutor, as_completed
        from multiprocessing import Manager, Process

        # If there is more than one file, we use multiprocessing to load the data
        logger.info("Loading data in parallel using multiprocessing.")
        log_file_name: str = ""
        for handler in logging.getLogger("bitfount").handlers:
            if isinstance(handler, logging.FileHandler):
                # Already have a file handler, so return it
                log_file_name = Path(handler.baseFilename).stem
                break

        if not log_file_name:
            # If there is no file handler, then there is no need for this message
            # to be logged any higher than debug anyway
            logger.debug("No existing file handler found for logger.")

        log_queue: Optional[Queue] = None
        log_listener: Optional[Process] = None
        executor: Optional[ProcessPoolExecutor] = None
        try:
            # Set environment variable to indicate that the spawned processes are
            # child processes since they will inherit the environment from the parent
            os.environ["_BITFOUNT_CHILD_PROCESS"] = "True"

            # Initialization must be done before creating the process
            data_cache_sqlite_path: Optional[Path] = None
            data_cache: Optional[DataPersister] = self.data_cache
            if self.data_cache and isinstance(self.data_cache, SQLiteDataPersister):
                data_cache_sqlite_path = self.data_cache._sqlite_path
                # TODO: [BIT-3723] There may be a better way to pass the data cache to
                # the worker processes by disposing of the connection pool rather than
                # having to recreate the cache in each worker process
                self.data_cache = None

            manager = Manager()
            log_queue = manager.Queue(-1)
            log_listener = Process(
                target=self._mp_listener_process, args=(log_queue, log_file_name)
            )
            log_listener.start()

            # Create a pool of worker processes
            max_workers = self.get_num_workers(data_keys)
            logger.info(f"Multiprocessing max workers: {max_workers}")
            executor = ProcessPoolExecutor(max_workers=max_workers)
            lock = manager.Lock()
            futures: list[Future] = [
                executor.submit(
                    self._mp_worker_get_data_process,
                    log_queue,
                    data_cache_sqlite_path,
                    lock,
                    [i],
                    use_cache,
                    **kwargs,
                )
                for i in data_keys
            ]

            total_num_files = len(data_keys)
            dfs: list[pd.DataFrame] = []
            # Wait for the results to come in one by one as they complete
            for i, future in enumerate(as_completed(futures)):
                # Signal file finished processing
                for hook in get_hooks(HookType.POD):
                    hook.on_file_process_end(
                        cast(FileSystemIterableSource, self),
                        file_num=i + 1,
                        total_num_files=total_num_files,
                    )
                data, skipped_files, image_columns = future.result()
                self.skipped_files.update(set(cast(list[str], skipped_files)))
                self.image_columns.update(set(cast(list[str], image_columns)))
                dfs.append(cast(pd.DataFrame, data))

            logger.debug("Finished loading data in parallel using multiprocessing.")
        finally:
            logger.debug("Cleaning up multiprocessing environment.")

            # Reset environment variable to indicate that this is not a child process
            os.environ["_BITFOUNT_CHILD_PROCESS"] = "False"

            # Reset the data cache if it was set in the first place
            if data_cache:
                logger.debug("Reverting data cache to original state.")
                self.data_cache = data_cache

            if log_queue:
                log_queue.put_nowait(None)  # Send sentinel to tell listener to quit

            if log_listener:
                # Wait for listener to quit. Must be done before terminating the process
                # to ensure all the log messages continue to get processed
                log_listener.join()
                # Terminate listener process
                log_listener.terminate()

            # Shutdown the executor. We don't wait for it to finish as we have already
            # waited for the results to come in one by one as they complete
            if executor:
                executor.shutdown(wait=False)

        # If no data was loaded, return an empty dataframe as `pd.concat` will fail
        # if no dataframes are passed to it
        return pd.concat(dfs, axis=0, ignore_index=True) if dfs else pd.DataFrame()


@delegates()
class FileSystemIterableSource(BaseSource, MultiProcessingMixIn, ABC):
    """Abstract base source that supports iterating over file-based data.

    This is used for Iterable data sources that whose data is stored as files on disk.

    Args:
        path: Path to the directory which contains the data files. Subdirectories
            will be searched recursively.
        output_path: The path where to save intermediary output files. Defaults to
            'preprocessed/'.
        iterable: Whether the data source is iterable. This is used to determine
            whether the data source can be used in a streaming context during a task.
            Defaults to True.
        fast_load: Whether the data will be loaded in fast mode. This is used to
            determine whether the data will be iterated over during set up for schema
            generation and splitting (where necessary). Only relevant if `iterable` is
            True, otherwise it is ignored. Defaults to True.
        cache_images: Whether to cache images in the file system. Defaults to False.
            This is ignored if `fast_load` is True.

    Raises:
        ValueError: If `iterable` is False or `fast_load` is False or `cache_images`
            is True.
    """

    def __init__(
        self,
        path: Union[os.PathLike, str],
        output_path: Optional[Union[os.PathLike, str]] = None,
        iterable: bool = True,
        fast_load: bool = True,
        cache_images: bool = False,
        filter: Optional[FileSystemFilter] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        if not iterable:
            raise ValueError("FileSystemIterableSource must be iterable.")

        if not fast_load:
            raise ValueError("FileSystemIterableSource must use fast_load.")

        if cache_images:
            raise ValueError("FileSystemIterableSource must not cache images.")

        self._iterable = iterable
        self.fast_load = fast_load
        self.cache_images = cache_images

        # Path related attributes
        self._unsanitized_path = path
        self.out_path: Path
        if output_path is None:
            self.out_path = config.settings.paths.cache_dir
        else:
            self.out_path = Path(output_path).expanduser().absolute().resolve()
        logger.debug(f"File output path set to {self.out_path}")
        self.out_path.mkdir(exist_ok=True, parents=True)  # create if not exists
        self.filter = filter or FileSystemFilter()

        # This is used to select a subset of file names by the data splitter rather than
        # every file that has been loaded or that is in the directory. In particular,
        # this is used to subset the files for batched execution of a task.
        self.selected_file_names_override: list[str] = []
        # This is used to filter the file names to only new records.
        # In particular, this is used only when pod database exists and task
        # is set with `run_on_new_data_only` flag.
        self.new_file_names_only_set: Union[set[str], None] = None
        # A list of files that have previously been skipped either because of errors or
        # because they don't contain any image data and `images_only` is True. This
        # allows us to skip these files again more quickly if they are still present in
        # the directory.
        self.skipped_files: set[str] = set()

        # A list of image column names, so we can keep track of them when
        # cache_images is False.
        self.image_columns: set[str] = set()

        # Placeholder for datasource-specific filters

        # All filters should take a list of filenames and return
        # a list of file names or an empty list if no files
        # matching the filters are found.
        self._datasource_filters_to_apply: list[DataSourceFileFilter] = []

        # Placeholder for counting files processed and skipped
        self._num_files_processed = 0
        self._num_files_skipped = 0

    def get_project_db_sqlite_create_table_query(self) -> str:
        """Returns the required columns and types to identify a data point.

        The file name is used as the primary key and the last modified date is used to
        determine if the file has been updated since the last time it was processed. If
        there is a conflict on the file name, the row is replaced with the new data to
        ensure that the last modified date is always up to date.
        """
        return (
            f"{ORIGINAL_FILENAME_METADATA_COLUMN} TEXT PRIMARY KEY, "
            f"'{LAST_MODIFIED_METADATA_COLUMN}' VARCHAR(30), "
            f"UNIQUE({ORIGINAL_FILENAME_METADATA_COLUMN}) ON CONFLICT REPLACE"
        )

    def get_project_db_sqlite_columns(self) -> list[str]:
        """Returns the required columns to identify a data point."""
        return [ORIGINAL_FILENAME_METADATA_COLUMN, LAST_MODIFIED_METADATA_COLUMN]

    def _perform_max_file_check(self, file_names: list[str]) -> None:
        """Check if the number of files in the directory exceeds the maximum allowed.

        This check is performed after filtering the files by date and size. If the
        number of files in the directory exceeds the maximum allowed, an error is
        raised.

        Raises:
            IterableDataSourceError: If the number of files in the directory exceeds the
                maximum allowed.
        """
        num_files = len(file_names)
        if num_files > config.settings.max_number_of_datasource_files:
            raise IterableDataSourceError(
                f"Too many files in the directory match the criteria. Found "
                f"{num_files} files, but the maximum number of files "
                f"allowed is {config.settings.max_number_of_datasource_files}."
            )

    ####################
    # Other Properties #
    ####################
    @property
    def path(self) -> Path:
        """Resolved absolute path to data.

        Provides a consistent version of the path provided by the user
        which should work throughout regardless of operating system
        and of directory structure.
        """
        return Path(self._unsanitized_path).expanduser().absolute().resolve()

    ####################
    # File Properties #
    ####################
    @overload
    def file_names_iter(self, as_strs: Literal[False] = False) -> Iterator[Path]: ...

    @overload
    def file_names_iter(self, as_strs: Literal[True]) -> Iterator[str]: ...

    @overload
    def file_names_iter(
        self, as_strs: bool
    ) -> Union[Iterator[Path], Iterator[str]]: ...

    def file_names_iter(
        self, as_strs: bool = False
    ) -> Union[Iterator[Path], Iterator[str]]:
        """Iterate over files in a directory, yielding those that match the criteria.

        Args:
            as_strs: By default the files yielded will be yielded as Path objects.
                If this is True, yield them as strings instead.
        """
        if not self.path.exists():
            logger.warning(
                "The specified path for the datasource was not found. "
                "No files can be loaded."
            )
            return

        for file in self._file_names_iter_with_fs_filter():
            self._num_files_processed += 1
            # Check datasource filters to see if file is allowed
            if self._apply_datasource_specific_filters_to_file(file) is None:
                logger.info(f"File {file} filtered due to datasource filters")
                self.skipped_files.add(str(file))
                self._num_files_skipped += 1
                # Track progress after datasource filter skip
                for hook in get_hooks(HookType.POD):
                    hook.on_file_filter_progress(
                        total_files=self._num_files_processed,
                        total_skipped=self._num_files_skipped,
                    )
                continue

            logger.info(
                f"Datasource filtering: {self._num_files_skipped} filtered out of"
                f" {self._num_files_processed} considered after file-system filters.",
                extra={"sample": True},
            )

            if as_strs:
                yield str(file)
            else:
                yield file

    def _file_names_iter_with_fs_filter(self) -> Iterator[Path]:
        """Iterate over files and apply filesystem filtering."""
        # Counters/sets for logging details
        num_skipped_files: int = 0
        num_found_files: int = 0

        # We need to be careful to avoid any method that _isn't_ a generator,
        # as otherwise this method will not benefit from actual iteration over the
        # files.
        #
        # Additionally, we want to avoid repeated `os.stat()` calls where possible,
        # as these provide overhead.
        for i, entry in enumerate(scantree(self.path.resolve())):
            # Stop iteration early if we have reached the maximum number of files to
            # consider
            if num_found_files >= config.settings.max_number_of_datasource_files:
                logger.warning(
                    f"Directory exceeds maximum number of files matching criteria;"
                    f" maximum is {config.settings.max_number_of_datasource_files},"
                    f" found {num_found_files}."
                    f" Further files will not be iterated over."
                )
                break

            # Log out some progress details. These are sampled using the
            # SampleFilter, so won't output every loop.
            logger.info(
                f"File-system filters in progress: {num_skipped_files} skipped,"
                f" {i + 1} considered so far"
                f" (cause: filtering, disallowed type, processing error)",
                extra={"sample": True},
            )
            self.filter.log_files_found_with_extension(num_found_files, interim=True)
            logger.debug(
                f"File-system filters in progress: Checking file {i + 1}"
                f" against file-system criteria",
                extra={"sample": True},
            )

            try:
                # This is the fully resolved path of the entry
                path: Path = Path(entry.path)

                # - is this file already marked as skipped?
                if str(path) in self.skipped_files:
                    continue

                skip = self.filter.check_skip_file(entry)
                if skip:
                    self.skipped_files.add(str(path))
                    num_skipped_files += 1
                    continue

                # Otherwise, has passed all filters
                num_found_files += 1

                yield path
            except Exception as e:
                logger.warning(
                    f"Error whilst iterating through filenames on {path}, skipping."
                    f" Error was: {e}"
                )
                self.skipped_files.add(str(path))
                num_skipped_files += 1

        # Do some final logging
        self.filter.log_files_found_with_extension(num_found_files, interim=False)
        logger.info(f"Skipping {num_skipped_files} files.")

    @cached_property
    def _file_names(self) -> list[str]:
        """Returns a cached list of file names in the directory."""
        try:
            logger.debug(
                "A call was made to `.file_names`. This should be avoided and"
                " `file_names_iter` should be used instead:\n"
                + "".join(traceback.format_stack())
            )

            # TODO: [BIT-3721] This method should probably return a sorted list, to
            #       enable consistency in ordering.
            file_names = list(self.file_names_iter(as_strs=True))
            return file_names
        finally:
            # Reset counters after complete iteration
            self._num_files_processed = 0
            self._num_files_skipped = 0

    @property
    def file_names(self) -> list[str]:
        """Returns a list of file names in the specified directory.

        .. deprecated::
        The `file_names` property is deprecated and will be removed in a future release.
        Use `file_names_iter(as_strs=True)` for memory-efficient iteration, or
        `list(file_names_iter(as_strs=True))` if you need a list.

        This property accounts for files skipped at runtime by filtering them out of
        the list of cached file names. Files may get skipped at runtime due to errors
        or because they don't contain any image data and `images_only` is True. This
        allows us to skip these files again more quickly if they are still present in
        the directory.
        """

        warnings.warn(
            "The `file_names` property is deprecated and will be removed "
            "in a future release. Use `file_names_iter(as_strs=True)` for "
            "memory-efficient iteration, or `list(file_names_iter(as_strs=True))` "
            "if you need a list.",
            DeprecationWarning,
            stacklevel=2,
        )
        # TODO: [BIT-3721] This method should probably return a sorted list, to
        #       enable consistency in ordering.
        file_names = [i for i in self._file_names if i not in self.skipped_files]
        self._perform_max_file_check(file_names)
        return file_names

    def _get_file_names_iterable(self) -> Iterable[str]:
        """Retrieve a cached or non-cached file names iterable as possible.

        If cached property `_file_names` is set, it will return the output of the
        `file_names` property, otherwise it will return the iterable from
        `file_names_iter()`.

        This allows us to avoid re-iterating through files when it has already been
        done and cached.
        """
        # Check if we need to apply selection logic (overrides or filters)
        if self.selected_file_names_differ:
            # Use the efficient iterator that respects selection logic
            return self.selected_file_names_iter()

        try:
            # @cached_property works by setting the results from the first property
            # call as an attribute on __dict__, so we use that to check if it has
            # been set.
            if "_file_names" in self.__dict__:
                return self.file_names
            else:
                raise KeyError("_file_names not cached yet")
        # Otherwise we use the iterator instead
        except (AttributeError, KeyError):
            return self.file_names_iter(as_strs=True)

    def clear_file_names_cache(self) -> None:
        """Clears the list of selected file names.

        This allows the datasource to pick up any new files that have been added to the
        directory since the last time it was cached.
        """
        # This is the specified way to clear the cache on a cached_property
        # https://docs.python.org/3/library/functools.html#functools.cached_property
        try:
            del self._file_names
        except AttributeError:
            # If the file_names property hasn't been accessed yet, it will raise an
            # AttributeError. We can safely ignore this.
            pass

    def get_all_cached_file_paths(self) -> list[str]:
        """Get all file paths that are currently stored in the cache.

        Returns:
            A list of file paths that have cache entries, or an empty list if
            there is no cache or the cache hasn't been initialized.
        """
        if not hasattr(self, "data_cache") or self.data_cache is None:
            logger.debug("No data cache available.")
            return []

        if not isinstance(self.data_cache, SQLiteDataPersister):
            logger.debug("Data cache is not an SQLiteDataPersister instance.")
            return []

        # Call the method on the SQLiteDataPersister instance
        return self.data_cache.get_all_cached_files()

    def has_uncached_files(self) -> bool:
        """Returns True if there are any files in the datasource not yet cached."""
        cached_files = set(self.get_all_cached_file_paths())
        for file_path in self.file_names_iter(as_strs=True):
            if file_path not in cached_files:
                return True
        return False

    @property
    def selected_file_names_differ(self) -> bool:
        """Returns True if selected_file_names will differ from default.

        In particular, returns True iff there is a selected file names override in
        place and/or there is filtering for new file names only present.
        """
        # DEV: Compare the logic here to any conditions in `selected_file_names` that
        # could change it away from just returning `self.file_names` or equivalent.
        return (
            bool(self.selected_file_names_override)
            or self.new_file_names_only_set is not None
        )

    @property
    def selected_file_names(self) -> list[str]:
        """Returns a list of selected file names as strings.

        Selected file names are affected by the
        `selected_file_names_override` and `new_file_names_only` attributes.

        WARNING: This method loads all filenames into memory. For large datasets,
        consider using `selected_file_names_iter()` instead.
        """
        warnings.warn(
            "The `selected_file_names` property is deprecated and will be removed "
            "in a future release. Use `selected_file_names_iter()` for "
            "memory-efficient iteration, or `list(selected_file_names_iter())` "
            "if you need a list.",
            DeprecationWarning,
            stacklevel=2,
        )
        logger.debug(
            "selected_file_names loads all filenames into memory. "
            "Consider using selected_file_names_iter() for better memory efficiency."
            + "".join(traceback.format_stack())
        )

        # Convert iterator to list
        return list(self.selected_file_names_iter())

    def selected_file_names_iter(self) -> Iterator[str]:
        """Returns an iterator over selected file names.

        Selected file names are affected by the
        `selected_file_names_override` and `new_file_names_only` attributes.

        Returns:
            Iterator over selected file names.
        """
        # First, get the base iterator
        if self.selected_file_names_override:
            # If we have an override, iterate through that list
            base_iter = iter(self.selected_file_names_override)
        else:
            # Use the file_names_iter which is iterable
            base_iter = self.file_names_iter(as_strs=True)

        # Apply new_file_names_only filter if needed (
        if self.new_file_names_only_set is not None:
            new_file_names_str_set = set(str(f) for f in self.new_file_names_only_set)
            filtered_count = 0
            for filename in base_iter:
                filename_str = str(filename)
                if filename_str in new_file_names_str_set:
                    filtered_count += 1
                    yield filename_str
            logger.debug(f"Filtered {filtered_count} files as new entries.")
        else:
            for filename in base_iter:
                yield str(filename)

    ##################
    # Data Retrieval #
    ##################
    def _apply_datasource_specific_filters_to_file(
        self, file_name: str | os.PathLike
    ) -> Optional[Path]:
        """Apply datasource specific filters to the file name.

        Args:
            file_name: The name of the file we need to check the filters against.

        Returns:
            The file_name if the file matches all filters or None otherwise.
        """
        file_list = [str(file_name)]
        for filter_func in self._datasource_filters_to_apply:
            file_list = filter_func(file_list)
            if len(file_list) == 0:
                return None
        return Path(file_name)

    @abstractmethod
    def _get_data(
        self,
        data_keys: SingleOrMulti[str],
        *,
        use_cache: bool = True,
        skip_non_tabular_data: bool = False,
        **kwargs: bool,
    ) -> pd.DataFrame:
        """Get data corresponding to the provided file name(s).

        Can be used to return data for a single file or for multiple at once. If
        used for multiple, the order of the output dataframe must match the order of
        the file names provided in `data_keys`.

        This method must return a dataframe with the columns `_original_filename` and
        `_last_modified` containing the original file name of each row, and the
        timestamp when the file was last modified in ISO 8601 format, respectively.

        Args:
            data_keys: File(s) to load, as paths.
            use_cache: Whether the cache should be used to retrieve data for these
                files. Note that cached data may have some elements, particularly
                image-related fields such as image data or file paths, replaced
                with placeholder values when stored in the cache. If data_cache is
                set on the instance, data will be _set_ in the cache, regardless of
                this argument.
            skip_non_tabular_data: Whether we can avoid loading non-tabular data,
                e.g. image data (can be set to True when generating schemas).
            **kwargs: Additional keyword arguments.

        Returns:
            A dataframe containing the data, ordered to match the order of file names
            in `data_keys`
        """
        raise NotImplementedError

    def _yield_data(
        self,
        data_keys: Optional[SingleOrMulti[str]] = None,
        *,
        use_cache: bool = True,
        partition_size: Optional[int] = None,
        **kwargs: Any,
    ) -> Iterator[pd.DataFrame]:
        """Yields data in batches from files.

        If data_keys is specified, only yield from that subset of files. Otherwise,
        iterate through the whole datasource.

        Args:
            data_keys: An optional list of file names to use for yielding data.
                Otherwise, all files that have already been found will be used.
                `data_keys` is always provided when this method is called from the
                Dataset as part of a task.
            use_cache: Whether the cache should be used to retrieve data for these
                files. Note that cached data may have some elements, particularly
                image-related fields such as image data or file paths, replaced
                with placeholder values when stored in the cache. If data_cache is
                set on the instance, data will be _set_ in the cache, regardless of
                this argument.
            partition_size: The number of files to load/yield in each iteration.
                If not provided, defaults to the partition size configured in the
                datasource.
            **kwargs: Additional keyword arguments.

        Raises:
            ValueError: If no file names provided and no files have been found.
        """
        if data_keys is not None:
            data_keys = self._convert_to_multi(data_keys)

        file_names: Iterable[str]
        if data_keys is not None:
            # if data_keys (i.e. file names) are provided, then we load files from
            # that list
            file_names = data_keys
        else:
            # See if we can use self.file_names (rather than having to re-iterate
            # through)
            file_names = self._get_file_names_iterable()
        # See if iterable has a length we can use
        try:
            len_file_names = len(file_names)  # type: ignore[arg-type] # Reason: in try-except # noqa: E501
        except TypeError:
            len_file_names = None

        partition_size_: int = partition_size or self.partition_size
        for idx, file_names_partition in enumerate(
            self.partition(file_names, partition_size_)
        ):
            logger.debug(f"Yielding partition {idx} from {self}")
            if self.use_file_multiprocessing(file_names_partition):
                # TODO: [BIT-4590] This should be auto-applied at any data
                #       yielding/returning rather than having to explicitly do it in
                #       every appropriate call.
                yield self.apply_ignore_cols(
                    self._mp_get_data(
                        data_keys=file_names_partition, use_cache=use_cache, **kwargs
                    )
                )
            else:
                # TODO: [BIT-4590] This should be auto-applied at any data
                #       yielding/returning rather than having to explicitly do it in
                #       every appropriate call.
                yield self.apply_ignore_cols(
                    self._get_data(
                        data_keys=file_names_partition, use_cache=use_cache, **kwargs
                    )
                )

                file_num = idx * partition_size_ + len(file_names_partition)
                for pod_hook in get_hooks(HookType.POD):
                    pod_hook.on_file_process_end(
                        self,
                        file_num=file_num,
                        total_num_files=len_file_names,
                    )

    @override
    def partition(
        self, iterable: Iterable[_I], partition_size: int = 1
    ) -> Iterable[Sequence[_I]]:
        # See if iterable has a length we can use
        try:
            len_iterable = len(iterable)  # type: ignore[arg-type] # Reason: in try-except # noqa: E501
        except TypeError:
            len_iterable = None

        for hook in get_hooks(HookType.POD):
            # Signal files partition
            hook.on_files_partition(
                self, total_num_files=len_iterable, batch_size=partition_size
            )

        yield from super().partition(iterable, partition_size)

    def __len__(self) -> int:
        # Try complete cache first
        if self.data_cache is not None:
            try:
                if not self.has_uncached_files():
                    # Cache is complete, use it
                    cached_files = self.get_all_cached_file_paths()
                    return len(cached_files)
            except Exception:
                logger.info(
                    "Failed to get cached file count, falling back to iteration."
                )
        # if not use selected_file_names
        try:
            return len(self.selected_file_names)
        except Exception:
            logger.warning(
                "Failed to get selected file names length, falling back to iteration."
            )

        # Finally, fallback to iteration count (slowest but always works)
        # This matches the BaseSource implementation
        chunk_lens: Iterable[int] = map(len, self.yield_data())
        return sum(chunk_lens)


@delegates()
class FileSystemIterableSourceInferrable(FileSystemIterableSource, ABC):
    """Base source that supports iterating over folder-labelled, file-based data.

    This is used for data sources whose data is stored as files on disk, and for
    which the folder structure (potentially) contains labelling information (e.g.
    the files are split into "test/", "train/", and "validate/" folders).

    Args:
        path: Path to the directory which contains the data files. Subdirectories
            will be searched recursively.
        data_cache: A DataPersister instance to use for data caching.
        infer_class_labels_from_filepaths: Whether class labels should be
            added to the data based on the filepath of the files.
            Defaults to the first directory within `self.path`,
            but can go a level deeper if the datasplitter is provided
            with `infer_data_split_labels` set to true
    """

    _first_directory_in_path: Final[str] = "_first_directory"
    _second_directory_in_path: Final[str] = "_second_directory"
    _unused_directory_in_path: Final[str] = "_unused_path_segment"

    def __init__(
        self,
        path: Union[os.PathLike, str],
        data_cache: Optional[DataPersister] = None,
        infer_class_labels_from_filepaths: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(path=path, **kwargs)
        self.data_cache = data_cache
        self.infer_class_labels_from_filepaths = infer_class_labels_from_filepaths
        # The below should be populated at the worker level if required
        self.infer_data_split_column_name: Union[str, Literal[False]] = False
        self.datasplitter_labels: Optional[List[str]] = None

    def _get_data(
        self,
        data_keys: SingleOrMulti[str],
        *,
        use_cache: bool = True,
        skip_non_tabular_data: bool = False,
        **kwargs: bool,
    ) -> pd.DataFrame:
        """Get data for the provided data key(s) with additional metadata.

        See parent `_get_data()` for details on wider functionality.

        This method performs the same, whilst also (potentially) adding labels to the
        data based on the folder structure the files are located in to infer class
        labels, and data split.
        """
        data_keys = self._convert_to_multi(data_keys)

        bulk_cached_data: Optional[pd.DataFrame] = None
        num_files_loaded_from_cache: int = 0
        file_names_to_be_processsed = data_keys

        if self.data_cache and use_cache:
            cache_results = self.data_cache.bulk_get(data_keys)
            # Data stored in the cache will already be in the form that is output
            # post-`_process_dataset()` so we can simply skip processing and append
            # it to a separate list (to be joined after all processing is done)
            bulk_cached_data = cache_results.data
            file_names_to_be_processsed = [str(f) for f in cache_results.misses]
            files_loaded_from_cache = set()
            if cache_results.hits is not None:
                files_loaded_from_cache = set(cache_results.hits.to_list())
            num_files_loaded_from_cache = len(files_loaded_from_cache)
            logger.info(
                "Retrieved cached data for "
                f"{num_files_loaded_from_cache} files: {files_loaded_from_cache}"
            )

        processed_data_list: list[dict[str, Any]] = []
        num_files_loaded: int = 0
        for filename in file_names_to_be_processsed:
            # If data was not in the cache (or was invalid) we will need to process
            # the file
            logger.info(f"Processing file {filename}...")
            processed_data = self._process_file(
                filename,
                skip_non_tabular_data=skip_non_tabular_data,
                **kwargs,
            )

            if processed_data:
                num_files_loaded += 1
                # File has not been skipped and is not empty,
                # so we can add some metadata
                # columns and append it to the list of data points.
                for row in processed_data:
                    processed_data_with_metadata = self._add_metadata_to_data(
                        row, filename
                    )
                    processed_data_list.append(processed_data_with_metadata)

        # Log out details about the number of files loaded/from where
        num_files_expected = len(data_keys)
        total_files_loaded = num_files_loaded + num_files_loaded_from_cache
        if num_files_expected == 1:
            if total_files_loaded == 0:
                logger.warning("File could not be loaded.")
        elif num_files_expected > 1:
            if total_files_loaded == 0:
                logger.warning("No files could be loaded.")
            # We don't want to log when we're just loading a single file because this is
            # not a meaningful log message as sometimes we iterate through all the files
            # one by one calling this method.
            if total_files_loaded > 1:
                if total_files_loaded < num_files_expected:
                    logger.warning(
                        f"{total_files_loaded} files loaded successfully out of"
                        f" {num_files_expected} files."
                    )
                else:
                    logger.info(f"{total_files_loaded} files loaded successfully.")

                logger.info(
                    f"{num_files_loaded} file(s) freshly processed,"
                    f" {num_files_loaded_from_cache} file(s) loaded from cache."
                )

        # Create the (processed items) dataframe
        # Note: if everything was loaded from cache this could be empty
        df = pd.DataFrame.from_records(processed_data_list)

        # Add metadata columns if they were not added (e.g. if no files where
        # processed).
        # This is because we want to ensure that the metadata columns are always
        # present in the dataframe as they are relied upon downstream even if
        # they are empty.
        # If df is empty, this doesn't invalidate that, it simply adds columns to
        # the metadata.
        for col in FILE_SYSTEM_ITERABLE_METADATA_COLUMNS:
            if col not in df.columns:
                df[col] = None

        if not df.empty:
            # Perform any subclass defined processing of the dataframe
            df = self._process_dataset(df, **kwargs)

            # Infer the data split and class labels if necessary
            df = self._infer_data_split_and_class_labels(df, **kwargs)

            # Save any new processed data to the cache
            if self.data_cache:
                # We need to avoid caching anything that cannot/should not be placed
                # in the cache, such as image data or image filepaths that won't be
                # relevant after this pass
                try:
                    cacheable_df = self.data_cache.prep_data_for_caching(
                        df, image_cols=self.image_columns
                    )
                    self.data_cache.bulk_set(cacheable_df)
                except Exception as e:
                    logger.warning(
                        f"Error whilst attempting to bulk set new cache entries: {e}"
                    )

        # Combine newly processed data with the data retrieved from the cache (which
        # was already in the format needed post-`_process_dataset()`)
        if bulk_cached_data is not None:
            df = pd.concat(
                [df, bulk_cached_data], axis="index", join="outer", ignore_index=True
            )

        # TODO: [BIT-4590] This should be auto-applied at any data yielding/returning
        #       rather than having to explicitly do it in every appropriate call.
        return self.apply_ignore_cols(df)

    def _infer_data_split_and_class_labels(
        self,
        df: pd.DataFrame,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Infers the data split and class labels from the file paths.

        Args:
            df: The dataframe to infer the data split and class labels for.
            **kwargs: Additional keyword arguments to pass to the `load_data` method
                if the data is stale.

        Returns:
            The dataframe with the data split and class labels inferred.
        """
        # We now can infer the various labels of the data from the folder structure
        # if needed.
        unique_first_directory_column_values: list[str] = []
        unique_second_directory_column_values: list[str] = []

        if self.infer_class_labels_from_filepaths or self.infer_data_split_column_name:
            # We need to extract unique values from the first and second directories
            # so we can differentiate between the data split and the class label
            # directories.
            first_directory_col_in_df: bool = (
                self._first_directory_in_path in df.columns
            )

            if first_directory_col_in_df:
                unique_first_directory_column_values = (
                    df[self._first_directory_in_path].unique().tolist()
                )

            second_directory_col_in_df: bool = (
                self._second_directory_in_path in df.columns
            )

            if second_directory_col_in_df:
                unique_second_directory_column_values = (
                    df[self._second_directory_in_path].unique().tolist()
                )

            inferred_class_label_column_name: str = (
                BITFOUNT_INFERRED_LABEL_COLUMN
                if self.infer_class_labels_from_filepaths
                else self._unused_directory_in_path
            )

            if (
                self.infer_data_split_column_name
                and self.datasplitter_labels is not None
            ):
                # infer_data_split_column_name will *only* be
                # truthy for SplitterDefinedInData

                datasplitter_labels: list[str] = [
                    label.lower() for label in self.datasplitter_labels
                ]

                # We then identify which column is the data split labels. We then
                # mark the other column as the inferred class labels.
                if unique_first_directory_column_values and set(
                    i.lower() for i in unique_first_directory_column_values
                ).issubset(datasplitter_labels):
                    logger.info(
                        f"`{self._first_directory_in_path}` column contains"
                        f" data split labels."
                        " Inferring class labels from second directory."
                    )

                    df = df.rename(
                        columns={
                            self._first_directory_in_path: self.infer_data_split_column_name,  # noqa: E501
                            self._second_directory_in_path: inferred_class_label_column_name,  # noqa: E501
                        },
                        # "ignore" as we may not have the second directory/class labels
                        errors="ignore",
                    )
                elif unique_second_directory_column_values and set(
                    i.lower() for i in unique_second_directory_column_values
                ).issubset(datasplitter_labels):
                    logger.info(
                        f"`{self._second_directory_in_path}` column contains"
                        f" data split labels."
                        " Inferring class labels from first directory."
                    )

                    df = df.rename(
                        columns={
                            self._first_directory_in_path: inferred_class_label_column_name,  # noqa: E501
                            self._second_directory_in_path: self.infer_data_split_column_name,  # noqa: E501
                        },
                        # "raise" as if we have the second directory we _must_ have
                        # the first
                        errors="raise",
                    )
                else:
                    # If we reach here, either the appropriate columns aren't in
                    # the dataframe or the columns don't contain the expected values.
                    #
                    # Either way, we cannot proceed with the requested label inference.
                    datasplitter_labels_str: str = ", ".join(datasplitter_labels)

                    logger.debug(
                        f"Neither directory column seemed to contain"
                        f" datasplitter labels ({datasplitter_labels_str}):"
                        f" {first_directory_col_in_df=},"
                        f" {unique_first_directory_column_values=},"
                        f" {second_directory_col_in_df=},"
                        f" {unique_second_directory_column_values=}"
                    )
                    raise ValueError(
                        f"Neither the '{self._first_directory_in_path}' column"
                        f" nor the '{self._second_directory_in_path}' column"
                        f" seem to contain only datasplit labels"
                        f" ({datasplitter_labels_str}),"
                        f" or are not present;"
                        f" unable to infer datasplits."
                    )

                # Finally, we convert the datasplitter labels (i.e. train, test,
                # validation) to match the case expected by the datasplitter.
                #
                # This is needed as we perform a case-insensitive matching above
                # (see the `.lower()` usages), but the datasplitter is very much
                # case-sensitive.
                #
                # We convert all the labels to lowercase, then replace them with
                # the actual version of the label.
                df[self.infer_data_split_column_name] = df[
                    self.infer_data_split_column_name
                ].str.lower()
                df[self.infer_data_split_column_name].replace(
                    {label.lower(): label for label in self.datasplitter_labels},
                    inplace=True,
                )
            else:  # self.infer_class_labels_from_filepaths is True
                # We only need the class labels
                df = df.rename(
                    columns={
                        self._first_directory_in_path: inferred_class_label_column_name,
                    },
                    # We use raise here as there's _only_ the one column we care
                    # about so it _needs_ to be present
                    errors="raise",
                )

        # Drop any intermediate columns that aren't needed
        df = df.drop(
            columns=[
                self._first_directory_in_path,
                self._second_directory_in_path,
                self._unused_directory_in_path,
            ],
            errors="ignore",
        )
        return df

    @abstractmethod
    def _process_file(
        self,
        filename: str,
        skip_non_tabular_data: bool = False,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Process a single file.

        Files may contain more than one datapoint, so this function can return a list
        of dictionaries.

        The return format should be such that it can be treated as a list of records
        and converted into a dataframe.

        Args:
            filename: The name of the file to process.
            skip_non_tabular_data: Whether we can avoid loading non-tabular data,
                e.g. image data (can be set to True when generating schemas).
            **kwargs: Additional keyword arguments.

        Returns:
            A list of dictionaries where each dictionary is the data mapping for a
            single datapoint. The return format should be such that it can be treated
            as a list of records and converted into a dataframe.
        """
        raise NotImplementedError

    @abstractmethod
    def _process_dataset(self, dataframe: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
        """Perform any post-processing on dataframes.

        Called once all data for a collection of files has been combined into a
        single dataframe.
        """
        raise NotImplementedError

    def _add_metadata_to_data(
        self, data: dict[str, Any], filename: str
    ) -> dict[str, Any]:
        """Adds metadata to the data for a single datapoint.

        Args:
            data: The data to add metadata to.
            filename: The filename of the file to be processed.

        Returns:
            The data with metadata added.
        """
        data[ORIGINAL_FILENAME_METADATA_COLUMN] = filename
        data[LAST_MODIFIED_METADATA_COLUMN] = self._get_file_m_time(filename)

        # Track the first two directory levels so that we can easily
        # process the possible labels later on as needed
        relative_filepath = Path(filename).relative_to(self.path).parts
        if len(relative_filepath) > 1:
            data[self._first_directory_in_path] = relative_filepath[0]
        if len(relative_filepath) > 2:
            data[self._second_directory_in_path] = relative_filepath[1]

        return data

    def _get_file_m_time(self, filename: str) -> str:
        """Gets the file mtime in isoformat."""
        modify_time = os.path.getmtime(filename)
        return datetime.fromtimestamp(modify_time).isoformat()
