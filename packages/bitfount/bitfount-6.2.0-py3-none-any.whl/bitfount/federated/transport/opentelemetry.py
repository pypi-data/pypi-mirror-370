"""OpenTelemetry Task Metrics Setup."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path
from threading import Lock as ThreadingLock
from typing import Optional, Union
from uuid import UUID, uuid4

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc import _OTLP_GRPC_HEADERS
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    MetricExportResult,
    MetricReader,
    MetricsData,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan

from bitfount import config
from bitfount.exceptions import BitfountError
from bitfount.federated.algorithms.base import (
    _BaseAlgorithm,
    module_registry as algorithmRegistry,
)
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseWorkerModelAlgorithm,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.transport.config import MessageServiceConfig
from bitfount.hub.authentication_flow import BitfountSession

logger = _get_federated_logger(__name__)


class _ObservationStore:
    """Thread-safe storage for observations, designed for gauge callbacks.

    Allows adding observations thread-safe and clearing the storage
    when they are retrieved.
    """

    def __init__(self, name: str) -> None:
        self._name: str = name
        self._store: list[metrics.Observation] = []
        self._lock: ThreadingLock = ThreadingLock()

    def add(self, observation: metrics.Observation) -> None:
        """Thread-safe add an observation to the store."""
        with self._lock:
            self._store.append(observation)

    def get(self, clear: bool = True) -> list[metrics.Observation]:
        """Thread-safe retrieve all stored observations.

        Args:
            clear: If True, clear the store after retrieval.
        """
        with self._lock:
            observations = self._store.copy()
            if clear:
                self._store.clear()
            return observations

    def callback(
        self, options: metrics.CallbackOptions
    ) -> Iterable[metrics.Observation]:
        """Callback to return and clear observations thus far."""
        observations = self.get(clear=True)
        logger.debug(f"Returning {self._name} observations {observations}")
        return observations


class TaskMeter:
    """Meter that can be used to report task metrics."""

    # DEV: We currently make use of "observable gauges", i.e. asynchronous gauges.
    #      This is because the support for Synchronous Gauge metrics is currently
    #      experimental in the opentelemetry Python SDK. Once support has been
    #      finalised, we can consider changing these to be synchronous gauges.
    #      See:
    #      - https://github.com/open-telemetry/opentelemetry-python/pull/3462
    #      - https://github.com/open-telemetry/opentelemetry-python/issues/3363

    def __init__(self) -> None:
        # Creates a meter from the global meter provider
        meter = metrics.get_meter("TaskMeter")

        # Create mechanisms for recording number of algorithm records returned
        self._algorithm_records_returned_store = _ObservationStore(
            "algorithm_records_returned"
        )
        meter.create_observable_gauge(
            name="algorithm_records_returned",
            callbacks=[self._algorithm_records_returned_store.callback],
            description="The number of records returned by the algorithm",
        )

        # Create mechanisms for recording number of unique patients found
        self._unique_patient_count_store = _ObservationStore("unique_patient_count")
        meter.create_observable_gauge(
            name="unique_patient_count",
            callbacks=[self._unique_patient_count_store.callback],
            description=(
                "The number of unique patients found thus far."
                " Represents the current total."
            ),
        )

    def submit_algorithm_records_returned(
        self,
        *,
        records_count: int,
        task_id: str,
        algorithm: Union[_BaseAlgorithm, str],
        protocol_batch_num: Optional[int] = None,
        project_id: Optional[str] = None,
    ) -> None:
        """Submit algorithm_records_returned observation."""
        attributes = self._build_attributes(
            task_id=task_id,
            algorithm=algorithm,
            protocol_batch_num=protocol_batch_num,
            project_id=project_id,
        )
        self._algorithm_records_returned_store.add(
            metrics.Observation(
                records_count,
                attributes,
            )
        )

    def submit_algorithm_records_per_class_returned(
        self,
        *,
        records_count_per_class: dict[str, int],
        task_id: str,
        algorithm: Union[_BaseAlgorithm, str],
        protocol_batch_num: Optional[int] = None,
        project_id: Optional[str] = None,
    ) -> None:
        """Submit an algorithm_records_returned observation per class."""
        attributes = self._build_attributes(
            task_id=task_id,
            algorithm=algorithm,
            protocol_batch_num=protocol_batch_num,
            project_id=project_id,
        )

        if len(records_count_per_class.keys()) > 0:
            for class_name, class_count in records_count_per_class.items():
                attributes_with_class = attributes.copy()
                attributes_with_class["records_class_name"] = class_name
                self._algorithm_records_returned_store.add(
                    metrics.Observation(
                        class_count,
                        attributes_with_class,
                    )
                )
        else:
            self._algorithm_records_returned_store.add(
                metrics.Observation(
                    0,
                    attributes,
                )
            )

    def submit_unique_patient_count(
        self,
        *,
        patient_count: int,
        project_id: str,
    ) -> None:
        """Submit metric of unique eligible patients found for a project."""
        attributes: dict[str, str | bool] = {
            "project_id": project_id,
            # DEV: Currently only reporting eligible patient counts from this metric
            #      but future-proofing for if we want to report ineligible as well
            "eligible": True,
        }
        self._unique_patient_count_store.add(
            metrics.Observation(
                patient_count,
                attributes,
            )
        )

    def _build_attributes(
        self,
        *,
        task_id: str,
        algorithm: Union[_BaseAlgorithm, str],
        protocol_batch_num: Optional[int],
        project_id: Optional[str],
    ) -> dict[str, Union[str, int]]:
        algorithm_fqn: str
        model: Optional[str] = None
        if isinstance(algorithm, _BaseAlgorithm):
            algorithm_fqn, model = self._get_algorithm_properties(algorithm)
        else:
            algorithm_fqn = algorithm

        attributes: dict[str, Union[str, int]] = {
            "task_id": task_id,
            "algorithm": algorithm_fqn,
        }

        if protocol_batch_num is not None:
            attributes["protocol_batch_num"] = protocol_batch_num

        if project_id is not None:
            attributes["project_id"] = project_id

        if model is not None:
            attributes["model"] = model

        return attributes

    def _get_algorithm_properties(
        self,
        algorithm: _BaseAlgorithm,
    ) -> tuple[str, Optional[str]]:
        fqn = algorithm.__class__.__module__

        name: Optional[str] = algorithmRegistry.get(algorithm.__class__.__module__)
        if name is not None:
            fqn = f"{algorithm.__class__.__module__}.{name}"
        else:
            logger.debug("Algorithm name found in registry.")

        model: Optional[str] = None
        if isinstance(algorithm, _BaseWorkerModelAlgorithm):
            model = algorithm.model.class_name

        return fqn, model


task_meter: Optional[TaskMeter] = None
"""The OpenTelemetry Python SDK doesn't seem to have a way to unregister callbacks,
   (https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/api.md#asynchronous-gauge-operations)
   so to avoid creating a new gauge and registering a new callback that will have a
   reference kept my OpenTelemetry (memory leak) every time we instantiate a Protocol
   we have this global Meter that can be used by all Protocol instances."""

_task_meter_lock = ThreadingLock()


def _setup_metric_reader(session: BitfountSession) -> MetricReader:
    logger.debug("Setting metric reader")
    ms_config = MessageServiceConfig()
    logger.debug(f"Message service config: {ms_config}")
    logger.info("Setting up OpenTelemetry metrics exporter")
    exporter = BitfountOLTPMetricsExporter(
        session=session,
        endpoint=f"{ms_config.url}:{ms_config.port}",
        insecure=not ms_config.tls,
    )
    logger.debug(f"Metrics exporter config: {vars(exporter)}")
    metric_reader = PeriodicExportingMetricReader(exporter)
    logger.debug(f"Metric reader config: {vars(metric_reader)}")
    return metric_reader


def setup_opentelemetry_metrics(
    *,
    session: BitfountSession,
) -> None:
    """Setup Open Telemetry metrics exporter and TaskMeter."""
    global task_meter, _task_meter_lock
    with _task_meter_lock:
        if task_meter is None:
            metric_reader = _setup_metric_reader(session)
            installation_uuid = get_installation_uuid()
            logger.info(f"Installation UUID: {installation_uuid}")

            resource = Resource(attributes={"installation_uuid": installation_uuid})
            provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
            logger.debug(f"Provider: {vars(provider)}")

            # Sets the global default meter provider
            metrics.set_meter_provider(provider)
            logger.debug(f"Metrics: {vars(metrics)}")

            # Sets the global TaskMeter
            task_meter = TaskMeter()


def get_task_meter() -> TaskMeter:
    """Fetch global TaskMeter."""
    if task_meter is not None:
        return task_meter

    raise BitfountError(
        "Global TaskMeter not found - "
        "need to call setup_opentelemetry_metrics once before"
    )


def get_installation_uuid(
    storage_path: Optional[Path] = None,
) -> str:
    """Return the installation UUID.

    Uses config.settings.paths.storage_path by default.
    """
    if storage_path is None:
        storage_path = config.settings.paths.storage_path

    uuid_path = storage_path / ".uuid"
    if uuid_path.exists():
        with open(uuid_path, encoding="utf-8") as f:
            uuid = f.read()
            try:
                UUID(uuid)
                return uuid
            except ValueError:
                logger.warning(
                    f"Could not parse contents of {uuid_path} as UUID: {uuid}"
                )
    uuid = str(uuid4())
    logger.info(
        f"Installation UUID not found at {uuid_path} - "
        f"generated new UUID ({uuid}) and will store it there"
    )
    with open(uuid_path, mode="w", encoding="utf-8") as f:
        f.write(uuid)

    return uuid


class BitfountOLTPMetricsExporter(OTLPMetricExporter):
    """OTLPMetricExporter that sends Bitfount session headers.

    The BitfountSession message_service_metadata property may change over time
    so we need to ensure we have it fresh when we export metrics.
    """

    _session: BitfountSession

    def __init__(self, *, session: BitfountSession, endpoint: str, insecure: bool):
        super().__init__(
            endpoint,
            insecure,
        )
        self._session = session

    def _export(
        self, data: Union[Sequence[ReadableSpan], MetricsData]
    ) -> MetricExportResult:
        self._headers = tuple(self._session.message_service_metadata) + tuple(
            _OTLP_GRPC_HEADERS
        )
        logger.debug(f"Metric Export data to export:{data}")
        return super()._export(data)
