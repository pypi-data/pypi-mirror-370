# LOFAR Python ParameterSet

![Build status](https://git.astron.nl/lofar2.0/lofar_pyparameterset/badges/main/pipeline.svg)
![Test coverage](https://git.astron.nl/lofar2.0/lofar_pyparameterset/badges/main/coverage.svg)
<!-- ![Latest release](https://git.astron.nl/lofar2.0/lofar_pyparameterset/badges/main/release.svg) -->

## Overview

This package contains a pure-python drop-in replacement for the python wrapper around the original LOFAR ParameterSet that is written in C++. It supports only the basic features of the original.

The following, more fancy, features are not supported:

* Vector expansion, e.g., `foo=['bar'*4]` and `foo=[1..5]`
* Most value interpretations, including booleans
* Multi-line values
* String escaping beyond either `"` or `'` in the string
* Modellng of ParameterValue as a separate class
* Case-insensitivity
* Tracking unused keys

## Installation

Installation can be done in a number of ways. In order of preference (read:
ease of use):

1. Install the latest release from PyPI:

    ```
    pip install lofar-parameterset
    ```

2. Install directly from the Git repository. This option is useful if you want to use one or more features that have not yet been released:

    ```
    pip install --upgrade pip
    pip install git+https://git.astron.nl/lofar2.0/lofar_pyparameterset.git[@<branch|tag|hash>]
    ```
    If the optional `@<branch|tag|hash>` is omitted, `HEAD` of the `master` branch will used.

3. Clone the git repository, and install from your working copy. This option is mostly used by developers who want to make local changes:

    ```
    pip install --upgrade pip
    git clone https://git.astron.nl/lofar2.0/lofar_pyparameterset.git
    cd lofar_pyparameterset
    git checkout [<branch|tag|hash>]  #optionally
    pip install .
    ```

## Usage
Here is a example of how one could read attenuation settings from a parset file:
```python
from lofar_parameterset.parameterset import parameterset
with open("settings.parset") as f:
    parset = parameterset(parameterset.fromString(f.read()))
attenuations = parset.getDoubleVector("attenuations")
```

## Development

### Development environment

To setup and activte the develop environment run ```source ./setup.sh``` from within the source directory.

If PyCharm is used, this only needs to be done once.
Afterward the Python virtual env can be setup within PyCharm.

### Contributing
To contribute, please create a feature branch and a "Draft" merge request.
Upon completion, the merge request should be marked as ready and a reviewer
should be assigned.

Verify your changes locally and be sure to add tests. Verifying local
changes is done through `tox`.

```pip install tox```

With tox the same jobs as run on the CI/CD pipeline can be ran. These
include unit tests and linting.

```tox```

To automatically apply most suggested linting changes execute:

```tox -e format```

The configuration for linting and tox can be found in `pyproject.toml`

## License and copyright
This project is licensed under the GNU General Public License v3.0 or later.

Copyright &copy; 2024 - 2025, ASTRON (Netherlands Institute for Radio Astronomy)
