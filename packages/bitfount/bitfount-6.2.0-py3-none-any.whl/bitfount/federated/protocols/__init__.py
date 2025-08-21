"""Protocols for inter-machine communication.

Federated protocol plugins can also be imported from this package.
"""

from __future__ import annotations

import importlib as _importlib
import inspect as _inspect
import pkgutil as _pkgutil
from types import GenericAlias

from bitfount import config
from bitfount.federated.logging import _get_federated_logger
import bitfount.federated.protocols as protocols
from bitfount.federated.protocols.base import BaseProtocolFactory
from bitfount.utils import _import_module_from_file

__all__: list[str] = ["BaseProtocolFactory"]

_logger = _get_federated_logger(__name__)


# Create `protocols` plugin subdir if it doesn't exist
_protocols_plugin_path = config.settings.paths.federated_plugin_path / "protocols"
_protocols_plugin_path.mkdir(parents=True, exist_ok=True)


def _on_import_error(name_of_error_package: str) -> None:
    _logger.warning(f"Error importing protocol module {name_of_error_package}")


# Import all concrete implementations of BaseProtocolFactory in the protocols
# subdirectory as well as protocols plugins
_modules_prefix = f"{protocols.__name__}."
for _module_info in _pkgutil.walk_packages(
    path=protocols.__path__
    + [str(config.settings.paths.federated_plugin_path / "protocols")],
    prefix=_modules_prefix,
    onerror=_on_import_error,
):
    if _module_info.ispkg:
        continue

    _plugin_module_name = _module_info.name
    try:
        _module = _importlib.import_module(_plugin_module_name)
    except ImportError as ex1:
        # Try to import the module from the plugin directory if it's not found in the
        # protocols or model_protocols directories

        # The prefix has been prepended from the walk_packages() call, but this isn't
        # the actual filename in the plugins directory; this is simply the final,
        # unprefixed part of the _module_info.name
        _plugin_module_name = _plugin_module_name.removeprefix(_modules_prefix)
        try:
            _module, _module_local_name = _import_module_from_file(
                config.settings.paths.federated_plugin_path
                / "protocols"
                / f"{_plugin_module_name}.py",
                parent_module=__package__,
            )
            # Adding the module to the protocols package so that it can be imported
            globals().update({_module_local_name: _module})
            _logger.info(
                f"Imported protocol plugin {_plugin_module_name} as {_module.__name__}"
            )
        except ImportError as ex2:
            _logger.error(
                f"Error importing module {_plugin_module_name}"
                f" under {__name__}: {str(ex2)}"
            )
            _logger.debug(ex2, exc_info=True)
            continue
        else:
            _logger.debug(ex1, exc_info=True)

    found_factory = False
    for _, cls in _inspect.getmembers(_module, _inspect.isclass):
        # types.GenericAlias instances (e.g. list[str]) are reported as classes by
        # inspect.isclass() but are not compatible with issubclass() against an
        # abstract class, so we need to exclude.
        # See: https://github.com/python/cpython/issues/101162
        # TODO: [Python 3.11] This issue is fixed in Python 3.11 so can remove
        if isinstance(cls, GenericAlias):
            continue

        if issubclass(cls, BaseProtocolFactory) and not _inspect.isabstract(cls):
            # Adding the class to the protocols package so that it can be imported
            # as well as to the __all__ list so that it can be imported from bitfount
            # directly
            found_factory = True
            globals().update({cls.__name__: getattr(_module, cls.__name__)})
            __all__.append(cls.__name__)
        # There are too many false positives if we don't restrict classes to those
        # that inherit from BaseProtocolFactory for it to be a useful log message
        elif (
            issubclass(cls, BaseProtocolFactory)
            and cls.__name__ != "BaseProtocolFactory"
        ):
            found_factory = True
            _logger.warning(
                f"Found class {cls.__name__} in module {_plugin_module_name} which "
                f"did not fully implement BaseProtocolFactory. Skipping."
            )
        elif any(x in _plugin_module_name for x in ("base", "utils", "types")):
            # We don't want to log this because it's expected
            found_factory = True

    if not found_factory:
        _logger.warning(
            f"{_plugin_module_name} did not contain a subclass of BaseProtocolFactory."
        )
