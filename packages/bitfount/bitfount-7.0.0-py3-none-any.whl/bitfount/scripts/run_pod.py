#!/usr/bin/env python3
"""Run a Pod from a yaml config file."""

from __future__ import annotations

from os import PathLike
from typing import Union

import fire

from bitfount import config
from bitfount.runners.pod_runner import setup_pod_from_config_file
from bitfount.utils.logging_utils import log_pytorch_env_info_if_available

config._BITFOUNT_CLI_MODE = True


def run(path_to_config_yaml: Union[str, PathLike]) -> None:
    """Runs a pod from a config file.

    Args:
        path_to_config_yaml: Path to the config YAML file.
    """
    log_pytorch_env_info_if_available()

    pod = setup_pod_from_config_file(path_to_config_yaml)
    pod.start()


if __name__ == "__main__":
    fire.Fire(run)
