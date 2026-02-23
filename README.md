# stitchmeta

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/thomasisensee/stitchmeta/ci.yml?branch=main)](https://github.com/thomasisensee/stitchmeta/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/stitchmeta/badge/)](https://stitchmeta.readthedocs.io/)
[![codecov](https://codecov.io/gh/thomasisensee/stitchmeta/branch/main/graph/badge.svg)](https://codecov.io/gh/thomasisensee/stitchmeta)
![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13%20|%203.14-blue)

Extract metadata from microscopy image tiles and write FEABAS-compatible
coordinate files for stitching pipelines.

## Installation from source

Clone this repository and install from the local source tree:

```bash
git clone https://github.com/thomasisensee/stitchmeta.git
cd stitchmeta
python -m pip install .
```

## Development installation

For development, use an editable install:

```bash
python -m pip install --editable .[tests]
```

Having done so, the test suite can be run using `pytest`:

```
python -m pytest
```

## Quick start

Expected input layout:

```text
dataset_root/
  001/
    tile_a.tif
    tile_b.tif
  002/
    ...
```

Run extraction:

```bash
stitchmeta extract \
  --input-root dataset_root \
  --output-dir feabas_coords
```

The command writes one [FEABAS](https://github.com/YuelongWu/feabas) text file per section (`001.txt`, `002.txt`, ...).

## Python API

```python
from stitchmeta import extract

summary = extract(
    input_root="dataset_root",
    output_dir="feabas_coords",
    reader_name="fibics_tiff",
    invert_y=True,
    error_policy="partial",
)
```

## Extending to other datasets

Register a new reader class implementing the `TileReader` interface and use it
through `reader_name` in the API or CLI.

## Acknowledgments

This repository was set up using the [SSC Cookiecutter for Python Packages](https://github.com/ssciwr/cookiecutter-python-package).
