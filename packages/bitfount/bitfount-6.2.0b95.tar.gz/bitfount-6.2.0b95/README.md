<div align="center">
<img src="https://hub.bitfount.com/_auth/static/bitfount_logo_horizontal.png" width="600px">

**Federated learning and data analytics that just works**

---

</br>
<!-- Github workflow badges are case sensitive - the name must match the name of the workflow exactly -->

![Python versions](https://img.shields.io/pypi/pyversions/bitfount)
[![PyPI Latest Release](https://img.shields.io/pypi/v/bitfount.svg)](https://pypi.org/project/bitfount/)
[![PyPI Downloads](https://pepy.tech/badge/bitfount)](https://pepy.tech/project/bitfount)
![](https://github.com/bitfount/bitfount/workflows/CI/badge.svg?branch=develop)
![](https://github.com/bitfount/bitfount/workflows/tutorials/badge.svg?branch=develop)
[![codecov](https://codecov.io/gh/bitfount/bitfount/branch/develop/graph/badge.svg?token=r1hulrgehK)](https://codecov.io/gh/bitfount/bitfount)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![mypy type checked](https://img.shields.io/badge/mypy-checked-blue)](https://github.com/python/mypy)
[![flake8](https://img.shields.io/badge/linter-flake8-success)](https://github.com/PyCQA/flake8)
[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/bitfount/bitfount/blob/develop/LICENSE)

<!-- ![docs-coverage](interrogate.svg) -->

</div>

## Table of Contents

- [Using the Docker images](#using-the-docker-images)
- [Running the Python code](#running-the-python-code)
  - [Installation](#installation)
  - [Getting started (Tutorials)](#getting-started-tutorials)
  - [Federated training scripts](#federated-training-scripts)
- [License](#license)

## Using the Docker images

There is a docker image for running a pod (`ghcr.io/bitfount/pod:stable`).

The image requires a `config.yaml` file to be provided to them,
by default it will try to load it from `/mount/config/config.yaml` inside the docker container.
You can provide this file easily by mounting/binding a volume to the container,
how you do this may vary depending on your platform/environment (Docker/docker-compose/ECS),
if you have any problems doing this then feel free to reach out to us.

Alternative you could copy a config file into a stopped container using [docker cp](https://docs.docker.com/engine/reference/commandline/cp/).

If you're using a CSV data source then you'll also need to mount your data to the container,
this will need to be mounted at the path specified in your config, for simplicity it's easiest
put your config and your CSV in the same directory and then mount it to the container.

Once your container is running you will need to check the logs and complete the login step,
allowing your container to authenticate with Bitfount.
The process is the same as when running locally (e.g. the tutorials),
except that we can't open the login page automatically for you.

## Running the Python code

### Installation

#### Where to get it

Binary installers for the latest released version are available at the [Python
Package Index (PyPI)](https://pypi.org/project/bitfount).

`pip install bitfount`

If you are planning on using the `bitfount` package with Jupyter Notebooks, we recommend you install the splinter package `bitfount[tutorials]` which will make sure you are running compatible jupyter dependencies.

`pip install 'bitfount[tutorials]'`

#### Installation from sources

To install `bitfount` from source you need to create a python virtual environment.

In the `bitfount` directory (same one where you found this file after cloning the git repo), execute:

`pip install -r requirements/requirements.in`

These requirements are set to permissive ranges but are not guaranteed to work for all releases, especially the latest versions. For a pinned version of these requirements which are guaranteed to work, run the following command instead:

```bash
#!/bin/bash
PYTHON_VERSION=$(python -c "import platform; print(''.join(platform.python_version_tuple()[:2]))")
pip install -r requirements/${PYTHON_VERSION}/requirements.txt
```

For MacOS you may also need to install `libomp`:

`brew install libomp`

### Getting started (Tutorials)

In order to run the tutorials, you also need to install the tutorial requirements:

```bash
#!/bin/bash
PYTHON_VERSION=$(python -c "import platform; print(''.join(platform.python_version_tuple()[:2]))")
pip install -r requirements/${PYTHON_VERSION}/requirements-tutorial.txt
```

To get started using the Bitfount package in a federated setting, we recommend
that you start with our tutorials. Run `jupyter notebook`and open up the first
tutorial in the "Connecting Data & Creating Pods folder: `running_a_pod.ipynb`

### Federated training scripts

Some simple scripts have been provided to run a Pod or Modelling job from a config file.

> ⚠️ If you are running from a source install (such as from `git clone`) you will
> need to use <span style="white-space: nowrap">`python -m scripts.<script_name>`</span>
> rather than use `bitfount <script_name>` directly.

To run a pod:

`bitfount run_pod --path_to_config_yaml=<CONFIG_FILE>`

To run a modelling job:

`bitfount run_modeller --path_to_config_yaml=<CONFIG_FILE>`

## License

The license for this software is available in the `LICENSE` file.
This can be found in the Github Repository, as well as inside the Docker image.
