"""Monitor module and per-task context handling."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import threading
from typing import TYPE_CHECKING, Final, Optional, Union

from requests import RequestException

from bitfount.federated.monitoring.exceptions import (
    ExistingMonitorModuleError,
    NoMonitorModuleError,
)
from bitfount.federated.monitoring.types import (
    AdditionalMonitorMessageTypes,
    MonitorRecordPrivacy,
    ProgressCounterDict,
)
from bitfount.federated.transport.message_service import _BitfountMessageType
from bitfount.types import _JSONDict

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountHub
    from bitfount.hub.types import _MonitorPostJSON

_logger = logging.getLogger(__name__)


@dataclass
class _MonitorPostContent:
    """Python representation of a monitor POST body.

    Before sending the request use the `json()` method to convert it to the required
    format for sending.
    """

    task_id: str
    sender_id: str
    timestamp: datetime
    privacy: MonitorRecordPrivacy
    type: Union[_BitfountMessageType, AdditionalMonitorMessageTypes]

    # Not required fields
    recipient_id: Optional[str] = None
    message: Optional[str] = None
    metadata: Optional[_JSONDict] = None
    progress: Optional[dict[str, ProgressCounterDict]] = None
    resource_usage: Optional[dict[str, float]] = None

    def json(self) -> _MonitorPostJSON:
        """Converts this object into the equivalent JSON representation."""
        # Extract type as a string dependent on form
        type_str: str
        if isinstance(self.type, _BitfountMessageType):
            type_str = self.type.name
        else:  # AdditionalMonitorMessageTypes
            type_str = self.type.value

        json_dict: _MonitorPostJSON = {
            "senderId": self.sender_id,
            "timestamp": self.timestamp.isoformat(),
            "privacy": self.privacy.value,
            "type": type_str,
            "taskId": self.task_id,
        }

        # Not required fields
        if self.recipient_id:
            json_dict["recipientId"] = self.recipient_id
        if self.message:
            json_dict["message"] = self.message
        if self.metadata:
            json_dict["metadata"] = self.metadata
        if self.progress:
            json_dict["progress"] = self.progress
        if self.resource_usage:
            json_dict["resourceUsage"] = self.resource_usage

        return json_dict


class _MonitorModule:
    """Class for interacting with monitoring service endpoints."""

    def __init__(
        self,
        hub: BitfountHub,
        task_id: str,
        sender_id: str,
        recipient_id: Optional[str] = None,
    ):
        """Create a new monitoring service interface.

        Args:
            hub: The hub to send monitoring details to.
            task_id: The ID of the task that monitor updates are associated with.
            sender_id: The mailbox ID of this end of the task (i.e. worker mailbox
                ID for the worker, modeller mailbox ID for the modeller).
            recipient_id: Optional. The mailbox ID for the other end of the task
                if appropriate.
        """
        self._hub = hub
        self._task_id = task_id
        self._sender_id = sender_id
        self._recipient_id = recipient_id

    @property
    def task_id(self) -> str:
        """Task ID for this monitor module."""
        return self._task_id

    def _send_to_monitor_service(self, update: _MonitorPostContent) -> None:
        """Send updates to the monitoring service.

        Logs out if an error is encountered.
        """
        try:
            self._hub.send_monitor_update(update.json())
        except RequestException as exc:
            _logger.warning(
                f"Unable to send monitoring update of type {update.type.value};"
                f" error was: {str(exc)}"
            )

    def send_to_monitor_service(
        self,
        event_type: Union[_BitfountMessageType, AdditionalMonitorMessageTypes],
        privacy: MonitorRecordPrivacy,
        message: Optional[str] = None,
        metadata: Optional[_JSONDict] = None,
        progress: Optional[dict[str, ProgressCounterDict]] = None,
        resource_usage: Optional[dict[str, float]] = None,
    ) -> None:
        """Send updates to the monitoring service.

        Logs out if an error is encountered.
        """
        # Set timestamp to current UTC
        timestamp = datetime.now(timezone.utc)

        self._send_to_monitor_service(
            _MonitorPostContent(
                task_id=self._task_id,
                sender_id=self._sender_id,
                timestamp=timestamp,
                privacy=privacy,
                type=event_type,
                recipient_id=self._recipient_id,
                message=message,
                metadata=metadata,
                progress=progress,
                resource_usage=resource_usage,
            )
        )


# ###################################### #
# Global monitor module maintenance code #
# ###################################### #
# Global monitor module instance, to be set when task ID is known,
# removed at end of task
_MONITOR_MODULE: Optional[_MonitorModule] = None
# Lock to ensure atomic creation/access to monitoring module
# We use a reentrant lock here because we're happy for a single thread to acquire
# the lock multiple times (as these methods are all sync they can't interfere with
# themselves/each other).
# NOTE: If we make these async at any point then this lock will need to be revisited
#       as we will lose the guarantee that a single thread is safe from trying to
#       acquire it from multiple locations "simultaneously".
_MONITOR_MODULE_LOCK: Final[threading.RLock] = threading.RLock()


def _set_task_monitor(
    hub: BitfountHub, task_id: str, sender_id: str, recipient_id: Optional[str] = None
) -> None:
    """Sets the global monitor module instance.

    Raises:
        ExistingMonitorModuleError: If a monitor module is already set.
    """
    global _MONITOR_MODULE
    with _MONITOR_MODULE_LOCK:
        if _MONITOR_MODULE is not None:
            raise ExistingMonitorModuleError(
                f"A monitor module already exists,"
                f" associated with {_MONITOR_MODULE.task_id}"
            )
        else:
            _MONITOR_MODULE = _MonitorModule(hub, task_id, sender_id, recipient_id)


def _unset_task_monitor() -> None:
    """Removes the global monitor module instance."""
    global _MONITOR_MODULE
    with _MONITOR_MODULE_LOCK:
        _MONITOR_MODULE = None


def _get_task_monitor() -> _MonitorModule:
    """Returns the current monitor module instance.

    Raises:
        NoMonitorModuleError: If no monitor module has been created yet.
    """
    global _MONITOR_MODULE
    with _MONITOR_MODULE_LOCK:
        if _MONITOR_MODULE is None:
            raise NoMonitorModuleError(
                "No monitor module available,"
                " please create one using task_monitor_context()."
            )
        else:
            return _MONITOR_MODULE


@contextmanager
def task_monitor_context(
    hub: BitfountHub, task_id: str, sender_id: str, recipient_id: Optional[str] = None
) -> Generator[None, None, None]:
    """Context manager that handles monitor module instance creation and removal.

    Used to provide "task context" in which updates can be sent to the monitor
    service which are related to that task.
    """
    _set_task_monitor(hub, task_id, sender_id, recipient_id)
    try:
        yield
    finally:
        _unset_task_monitor()


def task_status_update(
    message: str,
    privacy: MonitorRecordPrivacy = MonitorRecordPrivacy.ALL_PARTICIPANTS,
    metadata: Optional[_JSONDict] = None,
    progress: Optional[dict[str, ProgressCounterDict]] = None,
    resource_usage: Optional[dict[str, float]] = None,
) -> None:
    """Send a task status update to the monitor service.

    Args:
        message: The update message to send.
        privacy: The privacy level of the status update. Defaults to all participants.
        metadata: Optional. Any metadata about the status update.
        progress: Optional. Any progress counter information about the status update.
        resource_usage: Optional. Any resource usage information about the status
            update.
    """
    try:
        with _MONITOR_MODULE_LOCK:
            monitor = _get_task_monitor()
            monitor.send_to_monitor_service(
                event_type=AdditionalMonitorMessageTypes.TASK_STATUS_UPDATE,
                privacy=privacy,
                message=message,
                metadata=metadata,
                progress=progress,
                resource_usage=resource_usage,
            )
        _logger.debug("Sent task status update")
    except NoMonitorModuleError as exc:
        _logger.warning(f"Unable to send task status update: {str(exc)}")


def task_config_update(
    task_config: _JSONDict,
    privacy: MonitorRecordPrivacy = MonitorRecordPrivacy.OWNER_MODELLER,
) -> None:
    """Send the final task config to the monitor service.

    Args:
        task_config: The task configuration as a JSON-compatible dictionary.
        privacy: The privacy level of the update. Defaults to all participants.
    """
    try:
        with _MONITOR_MODULE_LOCK:
            monitor = _get_task_monitor()
            monitor.send_to_monitor_service(
                event_type=AdditionalMonitorMessageTypes.TASK_CONFIG,
                privacy=privacy,
                metadata=task_config,
            )
        _logger.debug("Sent task config update")
    except NoMonitorModuleError as exc:
        _logger.warning(f"Unable to send task config update: {str(exc)}")
