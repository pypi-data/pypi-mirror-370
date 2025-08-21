import os
from tempfile import TemporaryDirectory

import geopandas as gpd
import numpy as np
import pytest
import rioxarray as rio
import xarray as xr
from shapely.geometry import box

from mapflow import animate, animate_quiver


@pytest.fixture
def air_data():
    ds = xr.tutorial.open_dataset("air_temperature")
    return ds["air"].isel(time=slice(0, 8))


@pytest.fixture
def air_temperature_gradient_data() -> xr.Dataset:
    ds = xr.tutorial.load_dataset("air_temperature_gradient").isel(time=slice(0, 12))
    ds.rio.set_spatial_dims("lon", "lat", inplace=True)
    ds.rio.write_crs("EPSG:4326", inplace=True)
    return ds


@pytest.fixture
def air_data_2d_coordinates():
    ntime = 24
    ny = 50
    nx = 50
    # Create a basic rectilinear grid first
    x = np.linspace(-10, 10, nx)
    y = np.linspace(-10, 10, ny)
    xx, yy = np.meshgrid(x, y)

    # Warp the grid to make it non-rectilinear
    # Using some arbitrary distortion functions
    lon = xx + 2 * np.sin(yy / 5)  # longitude varies with y position
    lat = yy + 1.5 * np.cos(xx / 4)  # latitude varies with x position

    # Create random data
    time_coords = np.arange(np.datetime64("2020-01-01"), np.datetime64("2020-01-01") + ntime)
    data = np.random.rand(ntime, ny, nx)

    # Create DataArray
    da = xr.DataArray(
        data,
        dims=("time", "yc", "xc"),
        coords={
            "time": time_coords,
            "lon": (("yc", "xc"), lon),
            "lat": (("yc", "xc"), lat),
        },
    )

    # Add coordinate metadata
    da["lon"].attrs = {"units": "degrees_east", "standard_name": "longitude"}
    da["lat"].attrs = {"units": "degrees_north", "standard_name": "latitude"}
    da["time"].attrs = {"standard_name": "time"}

    return da


def test_animate_2d(air_data_2d_coordinates):
    with TemporaryDirectory() as tmpdir:
        path = f"{tmpdir}/test_animation.mp4"
        animate(
            da=air_data_2d_coordinates,
            path=path,
            x_name="lon",
            y_name="lat",
            verbose=True,
        )
        assert os.path.exists(path)


def test_animate_quiver(air_temperature_gradient_data):
    with TemporaryDirectory() as tmpdir:
        path = f"{tmpdir}/test_animation_quiver.mp4"
        animate_quiver(
            u=air_temperature_gradient_data["dTdx"],
            v=air_temperature_gradient_data["dTdy"],
            path=path,
            field_name="Temperature Gradient",
            cmap="Reds",
            verbose=True,
        )
        assert os.path.exists(path)


def test_animate_quiver_subsample(air_data):
    with TemporaryDirectory() as tmpdir:
        path = f"{tmpdir}/test_animation_quiver_subsample.mp4"
        animate_quiver(
            u=air_data,
            v=air_data,
            path=path,
            x_name="lon",
            y_name="lat",
            subsample=5,
            verbose=True,
        )
        assert os.path.exists(path)


def test_animate(air_data):
    with TemporaryDirectory() as tmpdir:
        path = f"{tmpdir}/test_animation.mp4"
        animate(
            da=air_data,
            path=path,
            x_name="lon",
            y_name="lat",
            verbose=True,
        )
        assert os.path.exists(path)


def test_animate_log(air_data):
    with TemporaryDirectory() as tmpdir:
        path = f"{tmpdir}/test_animation_log.mp4"
        animate(
            da=air_data,
            path=path,
            x_name="lon",
            y_name="lat",
            log=True,
            verbose=True,
        )
        assert os.path.exists(path)


def test_animate_vmin_vmax(air_data):
    with TemporaryDirectory() as tmpdir:
        path = f"{tmpdir}/test_animation_vmin_vmax.mp4"
        animate(
            da=air_data,
            path=path,
            x_name="lon",
            y_name="lat",
            vmin=250,  # Example value
            vmax=300,  # Example value
            verbose=True,
        )
        assert os.path.exists(path)


def test_animate_qmin_qmax(air_data):
    with TemporaryDirectory() as tmpdir:
        path = f"{tmpdir}/test_animation_qmin_qmax.mp4"
        animate(
            da=air_data,
            path=path,
            x_name="lon",
            y_name="lat",
            qmin=10,  # Example value
            qmax=90,  # Example value
            verbose=True,
        )
        assert os.path.exists(path)


def test_animate_cmap(air_data):
    with TemporaryDirectory() as tmpdir:
        path = f"{tmpdir}/test_animation_cmap.mp4"
        animate(
            da=air_data,
            path=path,
            x_name="lon",
            y_name="lat",
            cmap="viridis",  # Example colormap
            verbose=True,
        )
        assert os.path.exists(path)


def test_animate_upsample_ratio(air_data):
    with TemporaryDirectory() as tmpdir:
        path = f"{tmpdir}/test_animation_upsample_ratio.mp4"
        # Use fewer frames for upsampling test to keep it fast
        animate(
            air_data.isel(time=slice(0, 10)),
            path=path,
            x_name="lon",
            y_name="lat",
            upsample_ratio=10,  # Example ratio
            verbose=True,
        )
        assert os.path.exists(path)


def test_animate_fps(air_data):
    with TemporaryDirectory() as tmpdir:
        path = f"{tmpdir}/test_animation_fps.mp4"
        animate(
            da=air_data,
            path=path,
            x_name="lon",
            y_name="lat",
            fps=10,  # Example fps
            verbose=True,
        )
        assert os.path.exists(path)


def test_animate_borders(air_data):
    borders = gpd.GeoSeries([box(-2, 42, 8, 50)], crs=4326)
    with TemporaryDirectory() as tmpdir:
        path = f"{tmpdir}/test_animation_fps.mp4"
        animate(
            da=air_data,
            path=path,
            x_name="lon",
            y_name="lat",
            borders=borders,
            verbose=True,
        )
        assert os.path.exists(path)


def test_animate_mkv(air_data):
    with TemporaryDirectory() as tmpdir:
        path = f"{tmpdir}/test_animation.mkv"
        animate(
            da=air_data,
            path=path,
            x_name="lon",
            y_name="lat",
            verbose=True,
        )
        assert os.path.exists(path)


def test_animate_mov(air_data):
    with TemporaryDirectory() as tmpdir:
        path = f"{tmpdir}/test_animation.mov"
        animate(
            da=air_data,
            path=path,
            x_name="lon",
            y_name="lat",
            verbose=True,
        )
        assert os.path.exists(path)


def test_animate_avi(air_data):
    with TemporaryDirectory() as tmpdir:
        path = f"{tmpdir}/test_animation.avi"
        animate(
            da=air_data,
            path=path,
            x_name="lon",
            y_name="lat",
            verbose=True,
        )
        assert os.path.exists(path)
