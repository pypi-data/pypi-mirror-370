# luts.py

Multidimensional labeled arrays and datasets in Python. This module provides objects whose design is close to [xarray](http://xarray.pydata.org/).

Provides the following objects:

- LUT (look-up table): a multidimensional array with labeled axes.
The equivalent of this object in xarray is [`xarray.DataArray`](http://xarray.pydata.org/en/stable/generated/xarray.DataArray.html)
- MLUT (multi-look-up table): a set of LUTs
The equivalent of this object in xarray is [`xarray.Dataset`](http://xarray.pydata.org/en/stable/generated/xarray.Dataset.html)


## Installation

This module is managed by [python-poetry](https://python-poetry.org/). It can be installed in your current python environment, including its dependencies, using:

1) A git repository: `pip install git+https://github.com/hygeos/luts.git`

2) A directory: `pip install luts/` or in editable mode: `pip install -e luts/`

## Testing

    $ pytest tests
