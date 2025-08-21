"""Schema management utilities for the Pod."""

from __future__ import annotations

import asyncio
from asyncio import Task as AsyncioTask
from dataclasses import asdict
import importlib
import logging
from multiprocessing import Event, Process
from multiprocessing.synchronize import Event as MultiprocessingEventType
from typing import Any, Awaitable, Mapping, Optional, Union, cast

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from prefect import (
    Task,
    flow,
    get_client,
    get_run_logger,
    task,
)
from prefect.cache_policies import NONE as NONE_CACHE_POLICY
from prefect.context import TaskRun
from prefect.futures import PrefectFuture, wait
from prefect.states import State
from prefect.task_runners import ThreadPoolTaskRunner
from requests import HTTPError, RequestException

from bitfount import config
from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSourceInferrable,
)
from bitfount.data.datasources.utils import FileSystemFilter
from bitfount.data.datasplitters import DatasetSplitter, SplitterDefinedInData
from bitfount.data.persistence.base import DataPersister
from bitfount.data.persistence.sqlite import SQLiteDataPersister
from bitfount.data.schema import BitfountSchema, SchemaGenerationFromYieldData
from bitfount.federated.exceptions import PodRegistrationError
from bitfount.federated.types import (
    DatasourceContainer,
    HubConfig,
    MinimalDatasourceConfig,
    MinimalSchemaGenerationConfig,
    MinimalSchemaUploadConfig,
)
from bitfount.hub.api import BitfountHub, PodPublicMetadata
from bitfount.hub.exceptions import SchemaUploadError
from bitfount.hub.helper import _create_bitfounthub
from bitfount.types import _JSONDict
from bitfount.utils import _handle_fatal_error

logger = logging.getLogger(__name__)


class PrefectProcessManager:
    """Manages Prefect flows in a separate process."""

    def __init__(self) -> None:
        self._process: Optional[Process] = None
        self._stop_event = Event()

    def start_flow(
        self,
        base_datasources: dict[str, DatasourceContainer],
        hub_config: HubConfig,
        pod_public_key: RSAPublicKey,
        _access_manager_public_key: RSAPublicKey,
    ) -> None:
        """Start Prefect flow in a separate process."""
        if self._process and self._process.is_alive():
            logger.warning("Prefect process already running")
            return
        # Create serializable data from the datasource configs
        datasource_configs = []
        for name, ds_container in base_datasources.items():
            datasource_configs.append(
                {
                    "name": name,
                    "schema": ds_container.schema.to_json(),
                    "data_config": {
                        "force_stypes": ds_container.data_config.force_stypes,
                        "column_descriptions": ds_container.data_config.column_descriptions,  # noqa: E501
                        "description": ds_container.data_config.description,
                        "ignore_cols": ds_container.data_config.ignore_cols,
                        "datasource_args": ds_container.data_config.datasource_args,
                        "file_system_filters": ds_container.data_config.file_system_filters,  # noqa: E501
                        "data_split": ds_container.data_config.data_split,
                    },
                    "datasource_details": {
                        "display_name": ds_container.datasource_details.display_name,  # noqa: E501
                        "description": ds_container.datasource_details.description,
                    },
                    "datasource_cls": type(ds_container.datasource).__name__,
                }
            )
        # Serialize the public keys
        serialized_pod_key = pod_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        serialized_am_key = _access_manager_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        # Ensure that stop event has been cleared if it was previously set
        self._stop_event.clear()
        # Set up the process
        self._process = Process(
            target=self._run_prefect_flow,
            args=(
                datasource_configs,
                hub_config,
                serialized_pod_key,
                serialized_am_key,
                self._stop_event,
            ),
            daemon=True,
        )
        # Start the process
        self._process.start()
        logger.info(f"Started Prefect process (PID: {self._process.pid})")

    def stop(self) -> None:
        """Stop the Prefect process."""
        if not self._process:
            return

        logger.info("Stopping Prefect process...")
        self._stop_event.set()

        self._process.join(timeout=5)
        if self._process.is_alive():
            logger.warning("Force terminating Prefect process")
            self._process.terminate()
            self._process.join()

        self._process = None
        logger.info("Prefect process stopped")

    @staticmethod
    def _run_prefect_flow(
        datasource_configs: list[dict[str, Any]],
        hub_config: HubConfig,
        serialized_pod_key: bytes,
        serialized_am_key: bytes,
        stop_event: MultiprocessingEventType,
    ) -> None:
        """Run Prefect flow in a separate process."""
        # All the configs need to be here so they get picked up by the flow.

        # Deserialize and cast the public keys
        pod_public_key = cast(
            RSAPublicKey, serialization.load_pem_public_key(serialized_pod_key)
        )
        access_manager_public_key = cast(
            RSAPublicKey, serialization.load_pem_public_key(serialized_am_key)
        )
        try:
            # Create new loop at every flow start
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # TODO: [BIT-5709] Remove type ignore once prefect issue is fixed
            @flow(  # type: ignore[arg-type] # reason: broken prefect type hints
                name="schema-manager",
                retries=3,
                retry_delay_seconds=5,
                task_runner=ThreadPoolTaskRunner(  # type: ignore[arg-type] # reason: broken prefect type hints
                    max_workers=config.settings.max_number_of_prefect_workers
                ),
            )
            async def schema_manager() -> None:
                """Main flow to manage background schema generation."""
                try:
                    # Check stop event periodically
                    while not stop_event.is_set():
                        # Get logger
                        _logger = get_run_logger()
                        #  Check stop event before starting
                        if stop_event.is_set():
                            _logger.info("Stop event set, exiting schema manager")
                            return
                        tasks = _submit_schema_gen_tasks(
                            datasource_configs,
                            hub_config,
                            pod_public_key,
                            access_manager_public_key,
                            _logger,
                        )
                        if len(tasks) == 0:
                            _logger.info("No schema generation tasks to submit")
                            return
                        else:
                            _logger.info("All schema generation tasks submitted")

                        # Wait for tasks to complete or to
                        # acknowledge cancellation and finish
                        total_num_tasks_done = 0
                        # Monitor task completion
                        while not stop_event.is_set() and tasks:
                            done, not_done = cast(
                                tuple[set[PrefectFuture], set[PrefectFuture]],
                                wait(tasks, timeout=3),
                            )

                            total_num_tasks_done += len(done)
                            _logger.info(
                                f"Schema generation tasks done: {total_num_tasks_done}"
                            )
                            tasks = list(not_done)

                            # Update schema in local dictionary for datasources
                            # with completed tasks
                            for task in done:
                                try:
                                    datasource_name, schema_str = cast(
                                        tuple[str, str], task.result()
                                    )
                                    _logger.info(
                                        "Schema generation task for "
                                        f"{datasource_name} completed"
                                    )

                                except Exception as e:
                                    _logger.error(f"Schema generation task failed: {e}")

                            await asyncio.sleep(5)
                            # Relinquish event loop to other async tasks
                            if not tasks:
                                _logger.info("All schema generation tasks completed")
                                # Returning here to end the flow. The only way to
                                # start a new flow will be to restart the Pod
                                # e.g. by adding a new dataset.
                                return
                            if stop_event.is_set():
                                logger.info("Stopping schema manager flow")
                                break
                except Exception as e:
                    logger.error(f"Error in schema manager: {e}")
                finally:
                    # Clean up
                    pending_tasks: list[AsyncioTask[Any]] = [
                        t
                        for t in asyncio.all_tasks(loop)
                        if t is not asyncio.current_task() and not t.done()
                    ]
                    for pending_task in pending_tasks:
                        pending_task.cancel()

                    if pending_tasks:
                        try:
                            # Convert to list of Awaitables for gather
                            awaitables: list[Awaitable[Any]] = [
                                t for t in pending_tasks
                            ]
                            await asyncio.gather(*awaitables, return_exceptions=True)
                        except Exception:
                            logger.info("All pending tasks cancelled")

            # TODO: [BIT-5709] Remove type ignore once prefect issue is fixed
            loop.run_until_complete(schema_manager())  # type: ignore[arg-type] # reason: broken prefect type hints
        except Exception as e:
            logger.error(f"Error running schema manager flow: {e}")
        finally:
            try:
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()
            except Exception as e:
                logger.error(f"Error closing event loop: {e}")


def _submit_schema_gen_tasks(
    datasource_configs: list[dict[str, Any]],
    hub_config: HubConfig,
    pod_public_key: RSAPublicKey,
    access_manager_public_key: RSAPublicKey,
    _logger: Union[logging.Logger, logging.LoggerAdapter],
) -> list[PrefectFuture[tuple[str, str]]]:
    """Submit schema generation tasks to Prefect."""
    tasks: list[PrefectFuture[tuple[str, str]]] = []
    # Iterate through all datasources and submit
    # schema generation tasks
    schema_generation_processes = 0
    for ds_config in datasource_configs:
        try:
            schema_type = ds_config["schema"]["metadata"]["schema_type"]
        except KeyError:
            # Old schemas (without metadata) are considered to be partial
            schema_type = "partial"
        datasource_config = _get_minimal_datasource_config_from_dict(ds_config)
        # Check if the file list has changed since the last schema generation or
        # if the schema had no features and set the schema type to partial if so
        if schema_type == "full":
            datasource = _setup_direct_datasource(datasource_config)
            if len(ds_config["schema"]["features"]) == 0:
                # If no features in the data, try to re-generate the schema.
                schema_type = "partial"
            elif isinstance(datasource, FileSystemIterableSourceInferrable):
                # Check if there are any uncached files that would
                # require schema regeneration
                if datasource.has_uncached_files():
                    _logger.info(
                        "New files detected, schema re-generation "
                        f"required for {ds_config['name']}"
                    )
                    schema_type = "partial"
        if schema_type != "full":
            schema_generation_processes += 1
            _logger.info(
                f"Submitting schema generation task for {ds_config['name']}"  # noqa: E501
            )
            schema_generation_config = MinimalSchemaGenerationConfig(
                datasource_name=ds_config["name"],
                force_stypes=ds_config["data_config"]["force_stypes"],
                column_descriptions=ds_config["data_config"]["column_descriptions"],
                description=ds_config["data_config"]["description"],
                ignore_cols=ds_config["data_config"]["ignore_cols"],
            )
            public_metadata = PodPublicMetadata(
                ds_config["name"],
                ds_config["datasource_details"]["display_name"],
                ds_config["datasource_details"]["description"],
                ds_config["schema"],
            )
            public_metadata.schema = {}
            schema_upload_config = MinimalSchemaUploadConfig(
                public_metadata=public_metadata,
                pod_public_key=pod_public_key,
                access_manager_public_key=access_manager_public_key,
            )
            schema_task = SchemaManagement.schema_worker.submit(
                datasource_config=datasource_config,
                schema_generation_config=schema_generation_config,
                schema_upload_config=schema_upload_config,
                hub_config=hub_config,
            )
            # TODO: [BIT-5709] Remove type ignore once prefect issue is fixed
            tasks.append(schema_task)  # type: ignore[arg-type] # reason: broken prefect type hints
    _logger.info(f"{schema_generation_processes} schema tasks submitted.")
    return tasks


def _get_minimal_datasource_config(
    datasource_container: DatasourceContainer,
) -> MinimalDatasourceConfig:
    """Get minimal datasource configuration from a datasource container."""
    return MinimalDatasourceConfig(
        datasource_cls_name=type(datasource_container.datasource).__name__,
        name=datasource_container.name,
        datasource_args=datasource_container.data_config.datasource_args,
        file_system_filters=datasource_container.data_config.file_system_filters,
        data_split=datasource_container.data_config.data_split,
    )


def _get_minimal_datasource_config_from_dict(
    ds_config: dict[str, Any],
) -> MinimalDatasourceConfig:
    """Get minimal datasource configuration from a dictionary."""
    return MinimalDatasourceConfig(
        datasource_cls_name=ds_config["datasource_cls"],
        name=ds_config["name"],
        datasource_args=ds_config["data_config"]["datasource_args"],
        file_system_filters=ds_config["data_config"]["file_system_filters"],
        data_split=ds_config["data_config"]["data_split"],
    )


def _setup_direct_datasource(datasource_config: MinimalDatasourceConfig) -> BaseSource:
    """Creates a BaseSource instance from a class and arguments."""
    # Get the class from the name
    try:
        datasource_cls: type[BaseSource] = getattr(
            importlib.import_module("bitfount.data"),
            datasource_config.datasource_cls_name,
        )
    except AttributeError as e:
        raise ImportError(
            f"Unable to import {datasource_config.datasource_cls_name} from bitfount."
        ) from e

    # Create datasource instance
    # For non-FileSystemIterableSourceInferrable classes, we construct as normal...
    if not issubclass(datasource_cls, FileSystemIterableSourceInferrable):
        datasource = datasource_cls(**datasource_config.datasource_args)
    # For FileSystemIterableSourceInferrable (and all subclasses), we additionally
    # ensure that data caching support is available
    else:
        data_persister: Optional[DataPersister]
        if "data_cache" in datasource_config.datasource_args:
            data_persister = datasource_config.datasource_args["data_cache"]
            logger.warning(
                f"Found existing data cache in datasource_args, will not override."
                f" data_cache={data_persister}"
            )
        elif config.settings.enable_data_cache:
            config.settings.paths.dataset_cache_dir.mkdir(parents=True, exist_ok=True)
            data_persister_path = (
                config.settings.paths.dataset_cache_dir
                / f"{datasource_config.name}_cache.sqlite"
            ).resolve()

            logger.info(
                f'Creating/retrieving cache for dataset "{datasource_config.name}"'
                f" at {data_persister_path}"
            )
            data_persister = SQLiteDataPersister(data_persister_path)
        else:
            logger.info(
                f"Data caching has been disabled; {config.settings.enable_data_cache}"
            )
            data_persister = None

        if datasource_config.file_system_filters is not None:
            logger.info("Applying file system filters to datasource")
            filter = FileSystemFilter(**asdict(datasource_config.file_system_filters))
            datasource_config.datasource_args.update({"filter": filter})
        datasource = datasource_cls(
            data_cache=data_persister, **datasource_config.datasource_args
        )
        if (
            datasource_config.data_split
            and datasource_config.data_split.data_splitter == "predefined"
        ):
            data_split = datasource_config.data_split.data_splitter
            data_split_args = datasource_config.data_split.args

            data_splitter = DatasetSplitter.create(data_split, **data_split_args)
            if (
                isinstance(data_splitter, SplitterDefinedInData)
                and data_splitter.infer_data_split_labels is True
            ):
                # The folder structure may provide labels for the data split
                # (i.e. train,test, validation), the class labels for the
                # data, or both.
                datasource.infer_data_split_column_name = data_splitter.column_name
                # We extract the split labels from the data splitter for
                # SplitterDefinedInData
                datasource.datasplitter_labels = [
                    data_splitter.training_set_label,
                    data_splitter.validation_set_label,
                    data_splitter.test_set_label,
                ]
            else:
                datasource.infer_data_split_column_name = False
                datasource.datasplitter_labels = None

    # Check that the instance has correctly instantiated BaseSource
    if not datasource.is_initialised:
        raise ValueError(
            f"The configured datasource {datasource_config.datasource_cls_name}"
            f" does not extend BaseSource"
        )

    return datasource


def _register_dataset(
    hub_upload_config: MinimalSchemaUploadConfig, hub: BitfountHub
) -> None:
    """Register dataset with Bitfount Hub.

    If dataset is already registered, will update dataset details if anything has
    changed.

    Args:
        hub_upload_config: Configuration for uploading schema to hub.
        hub: Bitfount Hub to register the pod with.

    Raises:
        PodRegistrationError: if registration fails for any reason
    """
    try:
        logger.info("Registering/Updating details on Bitfount Hub.")
        hub.register_pod(
            hub_upload_config.public_metadata,
            hub_upload_config.pod_public_key,
            hub_upload_config.access_manager_public_key,
        )
    except (HTTPError, SchemaUploadError) as ex:
        logger.critical(f"Failed to register with hub: {ex}")
        raise PodRegistrationError("Failed to register with hub") from ex
    except RequestException as ex:
        logger.critical(f"Could not connect to hub: {ex}")
        raise PodRegistrationError("Could not connect to hub") from ex


class SchemaGenerationHooks:
    """Prefect hooks for schema generation."""

    @staticmethod
    def on_schema_worker_completion(tsk: Task, run: TaskRun, state: State) -> None:
        """Log completion of schema worker task."""
        logger = get_run_logger()
        logger.info(f"Task {tsk.name} completed")

    @staticmethod
    def on_schema_worker_failure(tsk: Task, run: TaskRun, state: State) -> None:
        """Log failure of schema worker task."""
        logger = get_run_logger()
        logger.error(f"Task {tsk.name} failed")


class SchemaManagement:
    """Schema management utilities for the Pod."""

    _process = None
    _stop_event = None
    _prefect_manager: Optional[PrefectProcessManager] = PrefectProcessManager()

    @classmethod
    def start_prefect_flow(
        cls,
        base_datasources: dict[str, DatasourceContainer],
        hub_config: HubConfig,
        pod_public_key: RSAPublicKey,
        _access_manager_public_key: RSAPublicKey,
    ) -> None:
        """Start Prefect flow in a separate process."""

        if not cls._prefect_manager:
            cls._prefect_manager = PrefectProcessManager()

        if base_datasources:
            cls._prefect_manager.start_flow(
                base_datasources=base_datasources,
                hub_config=hub_config,
                pod_public_key=pod_public_key,
                _access_manager_public_key=_access_manager_public_key,
            )
        else:
            logger.info(
                "No datasources to generate schema for, skipping schema generation"
            )

    @classmethod
    def stop_prefect_flow(cls) -> None:
        """Stop Prefect flow process."""
        if cls._prefect_manager:
            cls._prefect_manager.stop()
            cls._prefect_manager = None
            logger.info("Stopped Prefect schema generation process")

    @staticmethod
    def is_prefect_server_healthy() -> bool:
        """Check if the Prefect server is up and running."""
        try:
            with get_client(sync_client=True) as client:
                response = client.api_healthcheck()
                if isinstance(response, Exception):
                    raise response
        except Exception:
            return False

        return True

    @staticmethod
    @task(
        name="schema-worker",
        retries=3,
        retry_delay_seconds=5,
        on_completion=[SchemaGenerationHooks.on_schema_worker_completion],
        on_failure=[SchemaGenerationHooks.on_schema_worker_failure],
        cache_policy=NONE_CACHE_POLICY,
    )
    async def schema_worker(
        datasource_config: MinimalDatasourceConfig,
        schema_generation_config: MinimalSchemaGenerationConfig,
        schema_upload_config: MinimalSchemaUploadConfig,
        hub_config: HubConfig,
    ) -> tuple[str, str]:
        """Process each record in the dataset with the ability to cancel.

        Args:
            datasource_config: The datasource config to generate schema for.
            schema_generation_config: The schema generation config.
            schema_upload_config: The schema upload config.
            hub_config: The hub config.

        Returns:
            The datasource name and the schema as a JSON string.
        """
        # Get logger
        _logger = get_run_logger()
        _logger.info("Prefect Task started")
        hub = _create_bitfounthub(
            username=hub_config.username,
            secrets=hub_config.secrets,
        )
        # Create datasource from config
        datasource = _setup_direct_datasource(datasource_config)
        # Create schema
        schema = BitfountSchema(
            name=schema_generation_config.datasource_name,
            description=schema_generation_config.description,
            column_descriptions=cast(
                Optional[Mapping[str, str]],
                schema_generation_config.column_descriptions,
            ),
        )

        # Add hook to generate schema from data
        hook = SchemaGenerationFromYieldData(
            schema,
            schema_generation_config.ignore_cols,
            schema_generation_config.force_stypes,
        )
        schema.force_stypes = schema_generation_config.force_stypes
        datasource.add_hook(hook)

        # Process each record in the dataset
        for i, _ in enumerate(datasource.yield_data()):
            _logger.info(
                (
                    f"Processing batch {i} from "
                    f"{schema_generation_config.datasource_name}"
                )
            )
            # Iterate through all the data to populate the schema.
            try:
                # Schema is now only uploaded to the hub only,
                # the worker will check the hub schema before
                # starting task to see if the latest matches
                # the schema requirements.
                schema.schema_type = "partial"
                old_schema = schema_upload_config.public_metadata.schema
                schema_upload_config.public_metadata.schema = schema.to_json()
                if SchemaManagement._has_differences(
                    old_schema,
                    schema_upload_config.public_metadata.schema,
                ):
                    _register_dataset(schema_upload_config, hub)
            except PodRegistrationError as pre:
                _handle_fatal_error(pre, logger=logger)

        schema.schema_type = "full"
        _logger.info("Schema generation task completed")
        try:
            schema_upload_config.public_metadata.schema = schema.to_json()
            _register_dataset(schema_upload_config, hub)
            _logger.info("Full schema uploaded to hub successfully.")
        except PodRegistrationError as pre:
            _handle_fatal_error(pre, logger=logger)

        return schema_generation_config.datasource_name, schema.dumps()

    @staticmethod
    def _has_differences(first_schema: _JSONDict, second_schema: _JSONDict) -> bool:
        """Compares schemas to determine if there are meaningful differences.

        Ignores the number_of_records in the comparison.
        """
        all_keys = set(first_schema.keys()).union(second_schema.keys())
        for key in all_keys:
            if key == "number_of_records":
                continue
            if first_schema.get(key) != second_schema.get(key):
                return True

        return False
