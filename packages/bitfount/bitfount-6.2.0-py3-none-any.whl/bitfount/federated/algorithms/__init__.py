"""Algorithms for remote processing of data.

Federated algorithm plugins can also be imported from this package.
"""

from __future__ import annotations

import importlib as _importlib
import inspect as _inspect
import pkgutil as _pkgutil
from types import GenericAlias

from bitfount import config
import bitfount.federated.algorithms as algorithms
from bitfount.federated.algorithms.base import BaseAlgorithmFactory
from bitfount.federated.logging import _get_federated_logger
from bitfount.utils import _import_module_from_file

__all__: list[str] = []

_logger = _get_federated_logger(__name__)


# Create `algorithms` plugin subdir if it doesn't exist
_algorithms_plugin_path = config.settings.paths.federated_plugin_path / "algorithms"
_algorithms_plugin_path.mkdir(parents=True, exist_ok=True)


def _on_import_error(name_of_error_package: str) -> None:
    _logger.warning(f"Error importing algorithm module {name_of_error_package}")


# Import all concrete implementations of BaseAlgorithmFactory in the algorithms
# subdirectory as well as algorithms plugins
_modules_prefix = f"{algorithms.__name__}."
for _module_info in _pkgutil.walk_packages(
    path=algorithms.__path__
    + [str(config.settings.paths.federated_plugin_path / "algorithms")],
    prefix=_modules_prefix,
    onerror=_on_import_error,
):
    if _module_info.ispkg:
        continue

    _plugin_module_name = _module_info.name
    try:
        _module = _importlib.import_module(_plugin_module_name)
    except ImportError:
        # Try to import the module from the plugin directory if it's
        # not found in the algorithms or model_algorithms directories

        # The prefix has been prepended from the walk_packages() call, but this isn't
        # the actual filename in the plugins directory; this is simply the final,
        # unprefixed part of the _module_info.name
        _plugin_module_name = _plugin_module_name.removeprefix(_modules_prefix)
        try:
            _module, _module_local_name = _import_module_from_file(
                config.settings.paths.federated_plugin_path
                / "algorithms"
                / f"{_plugin_module_name}.py",
                parent_module=__package__,
            )
            # Adding the module to the algorithms package so
            # that it can be imported
            globals().update({_module_local_name: _module})
            _logger.info(
                f"Imported algorithm plugin {_plugin_module_name} as {_module.__name__}"
            )
        except ImportError as ex:
            _logger.error(
                f"Error importing module {_plugin_module_name}"
                f" under {__name__}: {str(ex)}"
            )
            _logger.debug(ex, exc_info=True)
            continue

    found_factory = False
    for _, cls in _inspect.getmembers(_module, _inspect.isclass):
        # types.GenericAlias instances (e.g. list[str]) are reported as classes by
        # inspect.isclass() but are not compatible with issubclass() against an
        # abstract class, so we need to exclude.
        # See: https://github.com/python/cpython/issues/101162
        # TODO: [Python 3.11] This issue is fixed in Python 3.11 so can remove
        if isinstance(cls, GenericAlias):
            continue

        if issubclass(cls, BaseAlgorithmFactory) and not _inspect.isabstract(cls):
            # Adding the class to the algorithms package so that it can be imported
            # as well as to the __all__ list so that it can be imported from bitfount
            # directly
            found_factory = True
            globals().update({cls.__name__: getattr(_module, cls.__name__)})
            __all__.append(cls.__name__)
        # There are too many false positives if we don't restrict classes to those
        # that inherit from BaseAlgorithmFactory for it to be a useful log message
        elif (
            issubclass(cls, BaseAlgorithmFactory)
            and cls.__name__ != "BaseAlgorithmFactory"
        ):
            found_factory = True
            _logger.warning(
                f"Found class {cls.__name__} in module {_plugin_module_name} which "
                f"did not fully implement BaseAlgorithmFactory. Skipping."
            )
        elif any(x in _plugin_module_name for x in ("base", "utils", "types")):
            # We don't want to log this because it's expected
            found_factory = True

    if not found_factory:
        _logger.warning(
            f"{_plugin_module_name} did not contain a subclass of BaseAlgorithmFactory."
        )
