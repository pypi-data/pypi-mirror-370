"""Modules for data sources.

Datasource plugins can also be imported from this package.
"""

from __future__ import annotations

import logging as _logging
import pkgutil as _pkgutil

from bitfount import config
import bitfount.data.datasources as datasources
from bitfount.utils import _import_module_from_file

_logger = _logging.getLogger(__name__)

# Create `datasources` plugin subdir if it doesn't exist
_datasource_plugin_path = config.settings.paths.plugin_path / "datasources"
_datasource_plugin_path.mkdir(parents=True, exist_ok=True)


def _on_import_error(name_of_error_package: str) -> None:
    _logger.warning(f"Error importing datasource module {name_of_error_package}")


# Add datasource plugin modules to the `datasources` namespace alongside the existing
# built-in datasource modules. This is not essential, but it allows users to import
# the entire plugin module as opposed to just the Datasource class which is what is done
# in the `bitfount.data` __init__ module.
_modules_prefix = f"{datasources.__name__}."
for _module_info in _pkgutil.walk_packages(
    path=[str(_datasource_plugin_path)],
    prefix=_modules_prefix,
    onerror=_on_import_error,
):
    # The prefix has been prepended from the walk_packages() call, but this
    # isn't the actual filename in the plugins directory; this is simply the
    # final, unprefixed part of the _module_info.name
    _plugin_module_name = _module_info.name.removeprefix(_modules_prefix)
    try:
        _module, _module_local_name = _import_module_from_file(
            _datasource_plugin_path / f"{_plugin_module_name}.py",
            parent_module=__package__,
        )
        globals().update({_module_local_name: _module})
        _logger.info(
            f"Imported datasource plugin {_plugin_module_name} as {_module.__name__}"
        )
    except ImportError as ex:
        # This is deliberately at DEBUG as we don't care about this being exposed
        # to the user at this level but would be good to mark the failure somewhere.
        _logger.debug(
            f"Error importing datasource plugin {_plugin_module_name}"
            f" under {__name__}: {str(ex)}"
        )
        _logger.debug(ex, exc_info=True)
