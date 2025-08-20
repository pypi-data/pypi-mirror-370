"""Types related to monitoring modules."""

from __future__ import annotations

from enum import Enum
from typing import Optional, Protocol, TypedDict, runtime_checkable

from typing_extensions import NotRequired


@runtime_checkable
class HasTaskID(Protocol):
    """Protocol for describing objects that contain task IDs."""

    _task_id: Optional[str]


class MonitorRecordPrivacy(Enum):
    """Privacy options for monitor record.

    Note that these are primarily interpreted from the point of view of the
    pod owner.
    """

    PRIVATE = "PRIVATE"  # only the pod owner
    OWNER = PRIVATE  # alias to PRIVATE
    OWNER_MODELLER = "MODELLER"  # pod owner plus the modeller
    ALL_PARTICIPANTS = "ALL_PARTICIPANTS"  # everyone in the task


class AdditionalMonitorMessageTypes(Enum):
    """Additional monitoring message types.

    These are explicit message types in addition to the full set of
    _BitfountMessageType types being supported.
    """

    TASK_CONFIG = "TASK_CONFIG"
    TASK_STATUS_UPDATE = "TASK_STATUS_UPDATE"


class ProgressCounterDict(TypedDict):
    """Form of the progress counter dictionaries."""

    value: float
    total: NotRequired[float]
    estimated_total: NotRequired[float]
    unit: NotRequired[str]
