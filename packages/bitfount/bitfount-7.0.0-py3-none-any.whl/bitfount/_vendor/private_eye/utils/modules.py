from importlib import import_module
from typing import Any


def load_from_module(module_path: str, class_name: str) -> Any:
    try:
        module = import_module(module_path)
        return getattr(module, class_name)
    except (AttributeError, ModuleNotFoundError) as e:
        raise ValueError(f"{module_path}.{class_name} cannot be loaded") from e
