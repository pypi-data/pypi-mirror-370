"""Useful objects/functions for federated learning.

This is primarily intended for use by modules outside of the `federated` package.
It cannot be imported by most modules in the `federated` package because it would
introduce circular imports.
"""

from __future__ import annotations

from collections.abc import Mapping
import inspect
import threading
from types import GenericAlias, ModuleType
from typing import Any

import bitfount.federated.aggregators.base as aggregators
import bitfount.federated.algorithms.base as algorithms
from bitfount.federated.logging import _get_federated_logger
import bitfount.federated.protocols.base as protocols
from bitfount.models.base_models import _BaseModel

logger = _get_federated_logger(__name__)

# This is a read-only dictionary mapping the name of an aggregator to the class itself
_AGGREGATORS: Mapping[str, type[aggregators._BaseAggregatorFactory]] = (
    aggregators.registry
)


# This is a read-only dictionary mapping the name of an algorithm to the class itself
_ALGORITHMS: Mapping[str, type[algorithms.BaseAlgorithmFactory]] = algorithms.registry


# This is a read-only dictionary mapping the name of a protocol to the class itself
_PROTOCOLS: Mapping[str, type[protocols.BaseProtocolFactory]] = protocols.registry


def _load_models_from_module(module: ModuleType) -> dict[str, type[_BaseModel]]:
    """Load all concrete classes subclassing _BaseModel from a module.

    Args:
        module (ModuleType): The module to load models from.

    Returns:
        dict[str, type[_BaseModel]]: A dict of class name to class for all models found
    """
    found_models: dict[str, type[_BaseModel]] = {}

    # Load any concrete classes that extend DistributedModelMixIn and _BaseModel
    for cls_name, class_ in vars(module).items():
        if (
            inspect.isclass(class_)
            # types.GenericAlias instances (e.g. list[str]) are reported as classes by
            # inspect.isclass() but are not compatible with issubclass() against an
            # abstract class, so we need to exclude.
            # See: https://github.com/python/cpython/issues/101162
            # TODO: [Python 3.11] This issue is fixed in Python 3.11 so can remove
            and not isinstance(class_, GenericAlias)
            and issubclass(class_, _BaseModel)
            and not inspect.isabstract(class_)
        ):
            found_models[cls_name] = class_

    return found_models


class _StoppableThead(threading.Thread):
    """Stoppable thread by using a stop `threading.Event`.

    Args:
        stop_event: This is a `threading.Event` which when set, should stop the thread.
            The function that is being executed in the thread is required to regularly
            check the status of this event.
        **kwargs: Keyword arguments passed to parent constructor.
    """

    def __init__(self, stop_event: threading.Event, **kwargs: Any):
        self._stop_event = stop_event
        super().__init__(**kwargs)

    @property
    def stopped(self) -> bool:
        """Returns whether or not the stop event has been set."""
        return self._stop_event.is_set()

    def stop(self) -> None:
        """Sets the stop event."""
        self._stop_event.set()
