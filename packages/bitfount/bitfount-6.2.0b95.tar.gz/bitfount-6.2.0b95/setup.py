"""This file enables the github repo to be packaged into a wheel using `setuptools`."""

from __future__ import annotations

from collections import defaultdict
from os import PathLike
import platform
from pprint import pprint
import re
import runpy
from typing import Optional, Union

from setuptools import find_packages, setup

# The order of the operations is important because we want to check for "<="
# before "< etc.
_REQ_OPERATIONS = ("<=", ">=", "<", ">", "~=", "!=", "==")
_REQ_OP_REGEX = re.compile("|".join(re.escape(op) for op in _REQ_OPERATIONS))
# supported versions are 3.10
_PYTHON_VERSION: str = "".join(platform.python_version_tuple()[:2])
_PLATFORM_PROCESSOR: str = platform.processor()


def _load_reqs(file: Union[str, PathLike]) -> list[str]:
    """Load a requirements or constraints file.

    Will remove comments, -c and -r lines and return a list of solely the
    requirements and version constraints.
    """
    with open(file) as f:
        return [
            line.split("#")[0].strip()
            for line in f.read().splitlines()
            if not line.startswith(("#", "-c", "-r")) and line != ""
        ]


def _extract_package_info(line: str) -> tuple[str, list[str], Optional[str]]:
    """Extract package and constraint info from requirements line.

    Will extract the package name, list of version constraints and any environment
    markers if present.

    For example:
        `ipython>=5,<10,!=8.5`
    becomes:
        `("ipython", [">=5", "<10", "!=8.5"])`

    """
    package_name: str
    constraints: list[str]

    # First, extract any environment markers (platform_system, etc) from the line
    package_reqs: str
    environment_markers: Optional[str]
    try:
        package_reqs, environment_markers = line.split(";")
        package_reqs.strip()
        environment_markers.strip()
    except ValueError:
        # If no environment markers are present
        package_reqs = line
        environment_markers = None

    # Split on commas to handle multiple version constraints
    first_constraint: str
    rest: list[str]
    first_constraint, *rest = package_reqs.split(",")

    # Extract package name (string before first operation)
    package_name, _ = re.split(_REQ_OP_REGEX, first_constraint)
    first_constraint = first_constraint.lstrip(package_name)

    constraints = [first_constraint] + rest
    return package_name.strip(), [c.strip() for c in constraints], environment_markers


def _combine_reqs(*reqs: list[str]) -> list[str]:
    """Combines the package version constraints from several sources together.

    For a group of requirements (each a list of raw requirement lines), this function
    will produce a single line per package which contains all the constraints applied.

    Note, it does not do any condensing (e.g. <5,<8 becoming <5) or validity checking
    (e.g. <4,>5 being impossible). These are deferred to pip to handle.
    """
    # Find duplicated package names and their version constraints. These must be
    # combined into a single line.
    # Keys are either just the package name or, if environment markers are present,
    # a tuple of package name and environment markers.
    packages: defaultdict[Union[str, tuple[str, str]], list[str]] = defaultdict(list)

    for r in reqs:
        for line in r:
            # Raise an error if the line doesn't contain any of the operations
            if not any(op in line for op in _REQ_OPERATIONS):
                raise ValueError(f"Unknown version constraint: {line}")

            (
                package_name,
                package_constraints,
                environment_markers,
            ) = _extract_package_info(line)
            if not environment_markers:
                packages[package_name].extend(package_constraints)
            else:
                packages[(package_name, environment_markers)].extend(
                    package_constraints
                )

    # Combine the lists of constraints into a single constrained string for each package
    pure_reqs = [
        f"{key}{','.join(p_constraints)}"
        for key, p_constraints in packages.items()
        if isinstance(key, str)
    ]
    env_marked_reqs = [
        f"{key[0]}{','.join(p_constraints)} ; {key[1]}"
        for key, p_constraints in packages.items()
        if isinstance(key, tuple)
    ]
    return sorted(pure_reqs + env_marked_reqs)


# Import version information into current namespace
file_globals = runpy.run_path("bitfount/__version__.py")

# Get constraints
compat_constraints = _load_reqs("requirements/constraints-compatibility.txt")
direct_constraints = _load_reqs("requirements/constraints-direct.txt")
security_constraints = _load_reqs("requirements/constraints-security.txt")

# Get install requirements
install_reqs_in = _load_reqs("requirements/requirements.in")
# Combine requirements with relevant constraints
install_reqs = _combine_reqs(
    install_reqs_in, compat_constraints, direct_constraints, security_constraints
)
# These will only be shown if pip installed with `-v` option, but helpful for debug
print("## INSTALL REQS ##")
pprint(install_reqs)

extras_require = {}

# Get other requirements where we can be more strict and just use the compiled
# .txt files
tutorial_reqs = _load_reqs(f"requirements/{_PYTHON_VERSION}/requirements-tutorial.txt")
tests_reqs = _load_reqs(f"requirements/{_PYTHON_VERSION}/requirements-test.txt")
# This is temporarily removed whilst we rely on a mypy fork
# dev_reqs = _load_reqs(f"requirements/{_PYTHON_VERSION}/requirements-dev.txt")

extras_require["tests"] = tests_reqs
extras_require["tutorials"] = tutorial_reqs
# This is temporarily removed whilst we rely on a mypy fork
# extras_require["dev"] = dev_reqs


with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    author=file_globals["__author__"],
    author_email=file_globals["__author_email__"],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Security :: Cryptography",
        "Topic :: System :: Distributed Computing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    description=file_globals["__description__"],
    entry_points={
        "console_scripts": [
            "bitfount=bitfount.scripts.script_runner:main",
        ]
    },
    extras_require=extras_require,
    include_package_data=True,
    install_requires=install_reqs,
    keywords=["federated learning", "privacy", "AI", "machine learning"],
    license="Apache License 2.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    name=file_globals["__title__"],
    packages=find_packages(
        exclude=["data", "data.*", "models", "models.*", "tests", "tests.*"]
    ),
    package_data={
        "bitfount": ["py.typed", "assets/**/*", "schemas/omop/omop_schema_*.json"]
    },
    project_urls={
        "Documentation": "https://docs.bitfount.com/",
        "Homepage": "https://bitfount.com",
        "Source Code": "https://github.com/bitfount/bitfount/",
        "Hub": "https://hub.bitfount.com",
    },
    python_requires=">=3.10,<3.11",
    url=file_globals["__url__"],
    version=file_globals["__version__"],
)
