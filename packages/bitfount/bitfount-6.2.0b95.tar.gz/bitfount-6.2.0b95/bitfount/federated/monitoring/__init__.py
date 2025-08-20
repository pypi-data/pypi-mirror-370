"""Contains functionality for interacting with the task monitoring service.

A monitor module is available globally when running within a task's context (created
by task_monitor_context()); outside of this context calls to the monitor module
will fail as no task is in progress and hence no task ID is available.

Attempting to instantiate a second monitor module (i.e. running a second task context)
will raise an exception.

Interacting with the monitor module is achieved by utilising the appropriate functions
to send a desired update. These will only work within a task context.

Decorator versions of stateless functions are available in monitoring.decorators;
these can be applied to functions/methods and will make the appropriate monitor
service update when those functions or methods are called.
"""

from __future__ import annotations

from bitfount.federated.monitoring.exceptions import (
    ExistingMonitorModuleError,
    MonitorModuleError,
    NoMonitorModuleError,
)
from bitfount.federated.monitoring.monitor import (
    task_config_update,
    task_monitor_context,
    task_status_update,
)
from bitfount.federated.monitoring.types import (
    AdditionalMonitorMessageTypes,
    HasTaskID,
    MonitorRecordPrivacy,
    ProgressCounterDict,
)

__all__ = [
    "ExistingMonitorModuleError",
    "MonitorModuleError",
    "NoMonitorModuleError",
    "task_config_update",
    "task_monitor_context",
    "task_status_update",
    "AdditionalMonitorMessageTypes",
    "HasTaskID",
    "MonitorRecordPrivacy",
    "ProgressCounterDict",
]

__pdoc__ = {}
for _obj in __all__:
    __pdoc__[_obj] = False
