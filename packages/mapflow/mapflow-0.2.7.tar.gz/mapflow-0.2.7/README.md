<div align="center">
<img src="_static/logo.svg" alt="mapflow logo" width="200" height="200">

# mapflow

[![PyPI version](https://badge.fury.io/py/mapflow.svg)](https://badge.fury.io/py/mapflow)
[![Conda version](https://anaconda.org/conda-forge/mapflow/badges/version.svg)](https://anaconda.org/conda-forge/mapflow)
[![CI](https://github.com/CyrilJl/mapflow/actions/workflows/CI.yaml/badge.svg)](https://github.com/CyrilJl/mapflow/actions/workflows/CI.yaml)
[![Documentation Status](https://readthedocs.org/projects/mapflow/badge/?version=latest)](https://mapflow.readthedocs.io/en/latest/?badge=latest)
</div>

``mapflow`` transforms 3D ``xr.DataArray`` in video files in one code line.

## Documentation

The full documentation is available at [mapflow.readthedocs.io](https://mapflow.readthedocs.io).

## Installation

```bash
pip install mapflow
```

Or:

```bash
conda install -c conda-forge -y mapflow
```

## Features

- **Automatic Coordinate Detection**: Identifies x, y, and time coordinates in xarray DataArrays, with fallback options for manual input if needed.  
- **CRS Handling**: Detects the Coordinate Reference System (CRS) of the data or accepts user-defined CRS when unavailable.  
- **Robust Colorbar**: Generates a colorbar that handles outliers effectively while allowing customization.  
- **Built-in World Borders**: Includes default world border data but supports user-provided GeoSeries or GeoDataFrames.  
- **Simplified Visualization**: The ``plot_da`` function provides a one-line alternative to cartopy for quick plotting.  

## Animate

```python
import xarray as xr
from mapflow import animate

ds = xr.tutorial.open_dataset("era5-2mt-2019-03-uk.grib")
animate(da=ds['t2m'].isel(time=slice(120)), path='animation.mp4')
```

https://github.com/user-attachments/assets/3cf05957-dd9c-49b1-9452-2e18e950ddcd

## Static plot

```python
import xarray as xr
from mapflow import plot_da

ds = xr.tutorial.open_dataset("era5-2mt-2019-03-uk.grib")
plot_da(da=ds['t2m'].isel(time=0))
```

<img src="https://raw.githubusercontent.com/CyrilJl/mapflow/main/_static/plot_da.png" alt="plot_da" width="500">
