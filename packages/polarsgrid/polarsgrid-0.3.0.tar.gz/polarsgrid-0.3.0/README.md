# Polarsgrid

[![Continuous integration](https://github.com/vankesteren/polarsgrid/actions/workflows/main.yml/badge.svg)](https://github.com/vankesteren/polarsgrid/actions/workflows/main.yml) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/polarsgrid)

Tidyverse-style [`expand_grid()`](https://tidyr.tidyverse.org/reference/expand_grid.html) in a fast and efficient way using [Polars](https://pola.rs).

## Installation 

Install the package as follows:
```sh
pip install polarsgrid
```

or add it to your project using [uv](https://docs.astral.sh/uv) as follows:
```sh
uv add polarsgrid
```

## Usage

This package contains only a single function: `expand_grid()`.

```py
from polarsgrid import expand_grid
expand_grid(a=[1, 2], b=["x", "y"])
```
```
shape: (4, 2)
┌─────┬─────┐
│ a   ┆ b   │
│ --- ┆ --- │
│ i64 ┆ str │
╞═════╪═════╡
│ 1   ┆ x   │
│ 2   ┆ x   │
│ 1   ┆ y   │
│ 2   ┆ y   │
└─────┴─────┘
```

Note that the first argument iteratest fastest, and the last argument iterates slowest in the cartesian product.

Should the grid become too big to hold in memory, you can choose to return a lazy table which can be stored on a disk efficiently:

```py
from polarsgrid import expand_grid_lazy
lgrid = expand_grid_lazy(
    sample_size=list(range(1000)), 
    condition=["a", "b", "c"], 
    iteration=list(range(500)), 
)
lgrid.sink_parquet("grid.parquet")
```

Additionally, for certain operations it might be nice to return the string columns as a categorical data type, and to add a row id:

```py
expand_grid(
    fruit=["apple", "banana", "pear"], 
    color=["red", "green", "blue"], 
    check=[True, False], 
    _categorical=True,
    _row_id=True,
)
```
```
shape: (18, 4)
┌────────┬────────┬───────┬───────┐
│ row_id ┆ fruit  ┆ color ┆ check │
│ ---    ┆ ---    ┆ ---   ┆ ---   │
│ i64    ┆ cat    ┆ cat   ┆ bool  │
╞════════╪════════╪═══════╪═══════╡
│ 0      ┆ apple  ┆ red   ┆ true  │
│ 1      ┆ banana ┆ red   ┆ true  │
│ 2      ┆ pear   ┆ red   ┆ true  │
│ 3      ┆ apple  ┆ green ┆ true  │
│ 4      ┆ banana ┆ green ┆ true  │
│ …      ┆ …      ┆ …     ┆ …     │
│ 13     ┆ banana ┆ green ┆ false │
│ 14     ┆ pear   ┆ green ┆ false │
│ 15     ┆ apple  ┆ blue  ┆ false │
│ 16     ┆ banana ┆ blue  ┆ false │
│ 17     ┆ pear   ┆ blue  ┆ false │
└────────┴────────┴───────┴───────┘
```