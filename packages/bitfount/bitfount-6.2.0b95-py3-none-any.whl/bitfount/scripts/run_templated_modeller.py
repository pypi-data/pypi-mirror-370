#!/usr/bin/env python3
"""Run a task from a templated yaml config file.

For Dev usage only. This is not intended to be used in production.

Usage:
```
python -m bitfount.scripts.run_templated_modeller \
    `path-to-yaml-config` --pod_identifier='pod-id' \
    --template_params='{"param_1": "value", "param2": ["v1", "v2"]}'
```

"""

from __future__ import annotations

import ast
import json
from os import PathLike
from pathlib import Path
from typing import Any, Dict, Optional, Union

import desert
import fire
import yaml

from bitfount import config
from bitfount.federated import _Modeller
from bitfount.runners.config_schemas.modeller_schemas import ModellerConfig
from bitfount.runners.modeller_runner import (
    DEFAULT_MODEL_OUT,
    run_modeller,
    setup_modeller_from_config,
)
from bitfount.utils.logging_utils import log_pytorch_env_info_if_available

config._BITFOUNT_CLI_MODE = True


def dict_replace_value(
    dictionary: dict[str, Any],
    old_value: str,
    new_value: Union[str, list[str], dict[str, Any]],
) -> dict[str, Any]:
    """Helper function to replace a value in a dictionary."""
    updated_dict = {}
    for key, value in dictionary.items():
        if isinstance(value, dict):
            value = dict_replace_value(value, old_value, new_value)
        elif isinstance(value, list):
            value = list_replace_value(value, old_value, new_value)
        elif isinstance(value, str):
            if isinstance(new_value, str) and old_value in value:
                value = new_value
            elif isinstance(new_value, list) and old_value in value:
                value = new_value
            elif isinstance(new_value, dict) and old_value in value:
                value = new_value
        updated_dict[key] = value
    return updated_dict


def list_replace_value(
    lst: list[Any], old_value: str, new_value: Union[str, list[str], dict[str, Any]]
) -> list[Any]:
    """Helper function to replace a value in a list."""
    updated_lst = []
    for item in lst:
        if isinstance(item, list):
            item = list_replace_value(item, old_value, new_value)
        elif isinstance(item, dict):
            item = dict_replace_value(item, old_value, new_value)
        elif isinstance(item, str):
            if old_value in item:
                if isinstance(new_value, str):
                    item = new_value
                elif isinstance(new_value, list):
                    item = new_value
                elif isinstance(new_value, dict):
                    item = new_value
        updated_lst.append(item)
    return updated_lst


def parse_defaults(defaults_str: Union[str, list]) -> Any:
    """Parse defaults from string or list input."""
    if isinstance(defaults_str, list):
        return defaults_str

    try:
        # Try to parse as JSON
        return json.loads(defaults_str)
    except json.JSONDecodeError:
        try:
            # Try to parse as Python literal
            return ast.literal_eval(defaults_str)
        except (SyntaxError, ValueError):
            # If it's a single string not in list format
            return [defaults_str]


def parse_template_params(params_str: Union[str, Dict]) -> Any:
    """Parse template parameters from string or dict input."""
    if isinstance(params_str, dict):
        return params_str

    try:
        # Try to parse as JSON
        return json.loads(params_str)
    except json.JSONDecodeError:
        try:
            # Try to parse as Python literal
            return ast.literal_eval(params_str)
        except (SyntaxError, ValueError) as err_parse:
            raise ValueError(
                f"Cannot parse template parameters: {params_str}"
            ) from err_parse


def setup_templated_modeller_from_config_file(
    path_to_config_yaml: Union[str, PathLike],
    defaults: Optional[Union[str, list]] = None,
    pod_identifier: Optional[str] = None,
    template_params: Optional[Union[str, Dict[str, Any]]] = None,
) -> tuple[_Modeller, list[str], Optional[str], bool, bool, bool, bool]:
    """Creates a modeller from a YAML config file.

    Args:
        path_to_config_yaml: the path to the config file
        defaults: list of default values to use for templating the config
        pod_identifier: optional pod identifier to use instead of the one in the config
        template_params: dictionary of template parameter names to values

    Returns:
        A tuple of the created Modeller and the list of pod identifiers to run
    """
    path_to_config_yaml = Path(path_to_config_yaml)

    with open(path_to_config_yaml) as f:
        config_yaml = yaml.safe_load(f)

    # Update pod identifier if provided
    if (
        pod_identifier
        and "pods" in config_yaml
        and "identifiers" in config_yaml["pods"]
    ):
        config_yaml["pods"]["identifiers"] = [pod_identifier]

    parsed_defaults = None
    if defaults:
        parsed_defaults = parse_defaults(defaults)

    parsed_template_params = {}
    if template_params:
        parsed_template_params = parse_template_params(template_params)

    if "template" in config_yaml.keys():
        i = 0
        template = config_yaml["template"]
        del config_yaml["template"]
        for item_to_template, default_value in template.items():
            default = default_value.get("default")
            item_to_template_placeholder = "{{ " + item_to_template + " }}"

            # Priority 1: Use value from template_params if available
            if item_to_template in parsed_template_params:
                value = parsed_template_params[item_to_template]
                config_yaml = dict_replace_value(
                    config_yaml, item_to_template_placeholder, value
                )
            # Priority 2: Use value from ordered defaults list
            elif parsed_defaults and i < len(parsed_defaults):
                config_yaml = dict_replace_value(
                    config_yaml, item_to_template_placeholder, parsed_defaults[i]
                )
                i += 1
            # Priority 3: Use default value from template if available
            elif default is not None:
                config_yaml = dict_replace_value(
                    config_yaml, item_to_template_placeholder, str(default)
                )
            else:
                raise ValueError(
                    f"No value provided for template parameter: {item_to_template}"
                )

    modeller_config_schema = desert.schema(ModellerConfig)
    modeller_config_schema.context["config_path"] = path_to_config_yaml

    config: ModellerConfig = modeller_config_schema.load(config_yaml)
    return setup_modeller_from_config(config)


def run(
    path_to_config_yaml: Union[str, PathLike],
    defaults: Optional[Union[str, list]] = None,
    require_all_pods: bool = False,
    model_out: Path = DEFAULT_MODEL_OUT,
    pod_identifier: Optional[str] = None,
    template_params: Optional[Union[str, Dict[str, Any]]] = None,
) -> None:
    """Runs a modeller from a config file.

    Args:
        path_to_config_yaml: Path to the config YAML file.
        defaults: list of default values to use for templating the config.
        require_all_pods: Whether to require all pods to accept the task before
            continuing.
        model_out: Path to save the model to (if applicable).
        pod_identifier: Optional pod identifier to use instead of the one in the config.
        template_params: Optional dictionary mapping template parameter names to values.
    """
    log_pytorch_env_info_if_available()

    (
        modeller,
        pod_identifiers,
        project_id,
        run_on_new_datapoints,
        batched_execution,
        test_run,
        force_rerun_failed_files,
    ) = setup_templated_modeller_from_config_file(
        path_to_config_yaml, defaults, pod_identifier, template_params
    )

    run_modeller(
        modeller,
        pod_identifiers,
        require_all_pods,
        model_out,
        project_id,
        run_on_new_datapoints,
        batched_execution,
        test_run=test_run,
        force_rerun_failed_files=force_rerun_failed_files,
    )


if __name__ == "__main__":
    fire.Fire(run)
