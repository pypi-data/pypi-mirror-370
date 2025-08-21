"""Main script to run others as subcommands."""

from __future__ import annotations

import fire

from bitfount import __version__
from bitfount.scripts.generate_yaml_specs import generate_yaml_specs
from bitfount.scripts.run_modeller import run as modeller_run
from bitfount.scripts.run_pod import run as pod_run


def _version() -> None:
    """Prints the bitfount version."""
    print(__version__)


def main() -> None:
    """Main script entry point."""
    fire.Fire(
        {
            "run_modeller": modeller_run,
            "run_pod": pod_run,
            "generate_yaml_specs": generate_yaml_specs,
            "version": _version,
        },
        name="bitfount",
    )


if __name__ == "__main__":
    main()
