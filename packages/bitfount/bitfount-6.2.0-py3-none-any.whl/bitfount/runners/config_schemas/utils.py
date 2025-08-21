"""Utility functions related to config YAML specification classes."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional, Union, overload

import marshmallow
from marshmallow.decorators import POST_LOAD
import pydash

from bitfount.types import _JSON
from bitfount.utils import invert_dict, str_is_int

_logger = logging.getLogger(__name__)


@overload
def _deserialize_path(path: str, context: dict[str, Any]) -> Path: ...


@overload
def _deserialize_path(path: None, context: dict[str, Any]) -> None: ...


def _deserialize_path(path: Optional[str], context: dict[str, Any]) -> Optional[Path]:
    """Converts a str into a Path.

    If the input is None, the output is None.

    If the path to the config file is supplied in the `context` dict (in the
    "config_path" key) then any relative paths will be resolved relative to the
    directory containing the config file.
    """
    if path is None:
        return None

    ppath = Path(path)

    # If relative path, use relative to config file if present
    if not ppath.is_absolute() and "config_path" in context:
        config_dir = Path(context["config_path"]).parent
        orig_ppath = ppath
        ppath = config_dir.joinpath(ppath).resolve()
        _logger.debug(
            f"Making relative paths relative to {config_dir}: {orig_ppath} -> {ppath}"
        )

    return ppath.expanduser()


def _deserialize_model_ref(ref: str) -> Union[Path, str]:
    """Deserializes a model reference.

    If the reference is a path to a file (and that file exists), return a Path
    instance. Otherwise, returns the str reference unchanged.
    """
    path = Path(ref).expanduser()
    if path.is_file():  # also returns False if path doesn't exist
        return path
    else:
        return ref


def keep_desert_output_as_dict(
    clazz: type[marshmallow.Schema],
) -> type[marshmallow.Schema]:
    """Make a desert schema deserialize as a dict.

    Normally `desert` will deserialize back into the dataclass that was used to
    generate the schema in the first place. However, there are times when we want to
    _specify_ the schema via a dataclass (for simplicity), but _use_ the schema as a
    dict. We could simply call `asdict()` on the deserialized dataclass but if the
    instance is nested deep within an object this may be tricky or not preferable.

    This function works by modifying the registered hooks on the schema class to
    remove the "make_data_class" `post_load` hook that `desert` has added.
    """
    # Find the index of the @post_load hook that desert added
    match_idx = -1
    for idx, (attr_name, _hook_many, _processor_kwargs) in enumerate(
        clazz._hooks[POST_LOAD]
    ):
        if attr_name == "make_data_class":
            match_idx = idx
            break
    else:
        # If it wasn't found, log out details. It may be that something internal to
        # desert has changed, or perhaps this just wasn't a desert schema?
        post_load_hooks: list[str] = [
            name for name, hook_many, processor_kwargs in clazz._hooks[POST_LOAD]
        ]
        post_load_hooks_names: str = (
            ", ".join('"' + s + '"' for s in post_load_hooks)
            if post_load_hooks
            else "no @post_load hooks"
        )
        _logger.warning(
            f"Passed class {clazz} did not have the @post_load hook expected"
            f" for desert-created schema classes;"
            f' expected "make_data_class",'
            f" got {post_load_hooks_names}"
        )
    # Remove the hook, if found
    if match_idx != -1:
        clazz._hooks[POST_LOAD].pop(match_idx)
    return clazz


def get_pydash_deep_paths(
    obj: _JSON,
) -> dict[str, str | int | float | bool | None]:
    """Produce a map of pydash deep path strings to values for a given JSON object.

    Output keys will be deep path strings per
    https://pydash.readthedocs.io/en/stable/deeppath.html.
    """

    def _recursive_pydash_deep_paths(
        obj_: _JSON,
        curr_path_: tuple[str, ...],
        root_dict_: dict[tuple[str, ...], str | int | float | bool | None],
    ) -> None:
        # Recurse into dict values, with their keys appended to path
        if isinstance(obj_, dict):
            for k, v in obj_.items():
                # k is a string, but if it could be ambiguously misunderstood as an int
                # we need to wrap it in square brackets per
                # https://pydash.readthedocs.io/en/stable/deeppath.html
                k_entry = k
                if str_is_int(k):
                    k_entry = f"[{k_entry}]"

                _recursive_pydash_deep_paths(v, curr_path_ + (k_entry,), root_dict_)
        # Recurse into list values, with their index appended to path
        elif isinstance(obj_, list):
            for i, v in enumerate(obj_):
                i_entry = str(i)
                _recursive_pydash_deep_paths(v, curr_path_ + (i_entry,), root_dict_)
        # Otherwise, we are at a base object, so just add this entry to the dict
        else:
            root_dict_[curr_path_] = obj_

    root_dict: dict[tuple[str, ...], str | int | float | bool | None] = {}
    _recursive_pydash_deep_paths(obj, tuple(), root_dict)

    # Join tuple-representation of the paths into deep string paths,
    # per https://pydash.readthedocs.io/en/stable/deeppath.html
    return {
        ".".join(k_i.replace(".", r"\.") for k_i in k): v for k, v in root_dict.items()
    }


def replace_template_variables(
    config: _JSON, replace_map: dict[str, _JSON], error_on_absence: bool = False
) -> _JSON:
    """Replace template variables in a JSON object with intended replacements.

    Only replaces template variables which are _values_ within the (nested) JSON
    object, not keys, etc.
    """
    # Work on copy
    config = pydash.clone_deep(config)

    # Generate a map of variable values to pydash-esque paths
    pydash_deep_paths = get_pydash_deep_paths(config)
    values_to_path_map = invert_dict(pydash_deep_paths)

    # Replace template values
    for replacement_key, replacement_value in replace_map.items():
        deep_paths = values_to_path_map.get(replacement_key)

        if deep_paths is None:
            err_str = f'No entry with value "{replacement_key}" found in passed object'
            if error_on_absence:
                raise ValueError(err_str)
            else:
                _logger.warning(err_str)
        else:
            for deep_path in deep_paths:
                # Sanity check that path already exists
                if pydash.has(config, deep_path):
                    pydash.set_(config, deep_path, replacement_value)
                else:
                    raise ValueError(
                        f'No deep path "{deep_path}" exists on passed object'
                    )

    return config
