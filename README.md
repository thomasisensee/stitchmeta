# Welcome to stitchmeta

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/thomasisensee/stitchmeta/ci.yml?branch=main)](https://github.com/thomasisensee/stitchmeta/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/stitchmeta/badge/)](https://stitchmeta.readthedocs.io/)
[![codecov](https://codecov.io/gh/thomasisensee/stitchmeta/branch/main/graph/badge.svg)](https://codecov.io/gh/thomasisensee/stitchmeta)

## Installation

The Python package `stitchmeta` can be installed from PyPI:

```
python -m pip install stitchmeta
```

## Development installation

If you want to contribute to the development of `stitchmeta`, we recommend
the following editable installation from this repository:

```
git clone git@github.com:thomasisensee/stitchmeta.git
cd stitchmeta
python -m pip install --editable .[tests]
```

Having done so, the test suite can be run using `pytest`:

```
python -m pytest
```

## Acknowledgments

This repository was set up using the [SSC Cookiecutter for Python Packages](https://github.com/ssciwr/cookiecutter-python-package).
