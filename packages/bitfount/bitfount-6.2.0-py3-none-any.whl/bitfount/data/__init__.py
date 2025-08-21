"""Modules for handling model data flow.

Data plugins can also be imported from this package.
"""

from __future__ import annotations

import importlib as _importlib
import inspect as _inspect
import logging as _logging
import pkgutil as _pkgutil
from types import GenericAlias, ModuleType

from bitfount import config
from bitfount.data import datasources as datasources
from bitfount.data.dataloaders import BitfountDataLoader
from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datasplitters import PercentageSplitter, SplitterDefinedInData
from bitfount.data.datastructure import DataStructure
from bitfount.data.exceptions import (
    BitfountSchemaError,
    DataNotLoadedError,
    DataStructureError,
    DuplicateColumnError,
)
from bitfount.data.schema import BitfountSchema
from bitfount.data.types import (
    CategoricalRecord,
    ContinuousRecord,
    DataPathModifiers,
    DataSplit,
    ImageRecord,
    SemanticType,
    TextRecord,
)
from bitfount.data.utils import (
    check_datastructure_schema_compatibility,
)
from bitfount.utils import _import_module_from_file

_logger = _logging.getLogger(__name__)
__all__: list[str] = [
    "BitfountDataLoader",
    "BitfountSchema",
    "BitfountSchemaError",
    "CategoricalRecord",
    "ContinuousRecord",
    "DataNotLoadedError",
    "DataPathModifiers",
    "DataSplit",
    "DataStructure",
    "DataStructureError",
    "DuplicateColumnError",
    "ImageRecord",
    "PercentageSplitter",
    "SemanticType",
    "SplitterDefinedInData",
    "TextRecord",
    "check_datastructure_schema_compatibility",
]


def _load_datasource_classes(
    classes: list, module: ModuleType, module_name: str
) -> None:
    found_datasource = False

    for cls in classes:
        # types.GenericAlias instances (e.g. list[str]) are reported as classes by
        # inspect.isclass() but are not compatible with issubclass() against an
        # abstract class, so we need to exclude.
        # See: https://github.com/python/cpython/issues/101162
        # TODO: [Python 3.11] This issue is fixed in Python 3.11 so can remove
        if isinstance(cls, GenericAlias):
            continue

        if issubclass(cls, BaseSource) and not _inspect.isabstract(cls):
            found_datasource = True
            globals().update({cls.__name__: getattr(module, cls.__name__)})
            __all__.append(cls.__name__)
        # There are too many false positives if we don't restrict classes to those
        # that inherit from BaseSource for it to be a useful log message
        elif (
            issubclass(cls, BaseSource)
            and not cls.__name__.startswith("_")
            and cls.__name__
            not in (
                "BaseSource",
                "FileSystemIterableSource",
                "FileSystemIterableSourceInferrable",
            )
        ):
            found_datasource = True
            _logger.warning(
                f"Found class {cls.__name__} in module {module_name} which "
                f"did not fully implement BaseSource. Skipping."
            )
        elif any(x in module_name for x in ("base", "utils", "types")):
            # We don't want to log this because it's expected
            found_datasource = True

    if not found_datasource:
        _logger.warning(f"{module_name} did not contain a subclass of BaseSource.")


def _on_import_error(name_of_error_package: str) -> None:
    _logger.warning(f"Error importing datasource module {name_of_error_package}")


# Import all concrete implementations of BaseSource in the datasources subdirectory
# as well as datasource plugins.
_modules_prefix = f"{datasources.__name__}."
for _module_info in _pkgutil.walk_packages(
    path=datasources.__path__
    + [str(config.settings.paths.plugin_path / "datasources")],
    prefix=_modules_prefix,
    onerror=_on_import_error,
):
    if _module_info.ispkg:
        continue

    _plugin_module_name = _module_info.name
    try:
        _module = _importlib.import_module(_plugin_module_name)
    # Also catches `ModuleNotFoundError` which subclasses `ImportError`
    except ImportError:
        # These modules have extra requirements that are not installed by default
        if _plugin_module_name in ("dicom_source"):
            _logger.debug(
                f"Error importing module {_plugin_module_name}. Please make "
                "sure that all required packages are installed if "
                "you are planning to use that specific module"
            )
            continue
        else:
            # Try to import the module from the plugin directory if it's not found in
            # the datasources directory

            # The prefix has been prepended from the walk_packages() call, but this
            # isn't the actual filename in the plugins directory; this is simply the
            # final, unprefixed part of the _module_info.name
            _plugin_module_name = _plugin_module_name.removeprefix(_modules_prefix)
            try:
                _module, _ = _import_module_from_file(
                    config.settings.paths.plugin_path
                    / "datasources"
                    / f"{_plugin_module_name}.py",
                    parent_module=datasources.__package__,
                )
                _logger.info(
                    f"Imported datasource plugin {_plugin_module_name}"
                    f" as {_module.__name__}"
                )
            except ImportError as ex:
                _logger.error(
                    f"Error importing datasource plugin {_plugin_module_name}"
                    f" under {__name__}: {str(ex)}"
                )
                _logger.debug(ex, exc_info=True)
                continue

    # Extract classes in loaded module
    _classes = [cls for _, cls in _inspect.getmembers(_module, _inspect.isclass)]

    # Check for datasource classes
    _load_datasource_classes(_classes, _module, _plugin_module_name)

# See top level `__init__.py` for an explanation
__pdoc__ = {}
for _obj in __all__:
    __pdoc__[_obj] = False
