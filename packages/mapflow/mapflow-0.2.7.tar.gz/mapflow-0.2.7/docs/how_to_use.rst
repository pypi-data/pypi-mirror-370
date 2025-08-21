.. _how_to_use:

How to use
==========

This page provides examples of how to use ``mapflow`` for creating animations and static plots.

Animating a DataArray
---------------------

The main function of ``mapflow`` is ``animate``, which creates a video from an ``xarray.DataArray``.

.. code-block:: python

   import xarray as xr
   from mapflow import animate

   ds = xr.tutorial.open_dataset("era5-2mt-2019-03-uk.grib")
   animate(da=ds['t2m'].isel(time=slice(120)), path='animation.mp4')

.. raw:: html

    <video width="640" height="480" controls>
      <source src="_static/animation.mp4" type="video/mp4">
    </video>

Creating a static plot
----------------------

``mapflow`` also provides a simple way to create static plots of 2D ``xarray.DataArray`` objects using the ``plot_da`` function.

.. code-block:: python

   import xarray as xr
   from mapflow import plot_da

   ds = xr.tutorial.open_dataset("era5-2mt-2019-03-uk.grib")
   plot_da(da=ds['t2m'].isel(time=0))

.. image:: /_static/plot_da.png
   :alt: Sample output of plot_da function
   :align: center
   :width: 75%

Key Features
------------

``mapflow`` is designed to be intuitive and requires minimal user input. Here are some of the key features that make it easy to use:

* **Automatic Coordinate Detection**: ``mapflow`` automatically detects the names of the x, y, and time coordinates in your ``xarray.DataArray``. If it fails to find them, you can specify them using the ``x``, ``y``, and ``time_name`` arguments.

* **Automatic CRS Detection**: The library automatically tries to determine the Coordinate Reference System (CRS) from your data. If no CRS is found, you can pass it directly using the ``crs`` argument.

* **Robust Colorbars**: ``mapflow`` generates a colorbar that is robust to outliers, ensuring that your data is visualized clearly. You can also customize the colorbar using the ``vmin``, ``vmax``, and ``cmap`` arguments.

* **Integrated World Borders**: ``mapflow`` includes a built-in set of world borders for plotting. If you need to use custom borders, you can provide them as a ``geopandas.GeoSeries`` or ``geopandas.GeoDataFrame`` using the ``borders`` argument.

* **One-line Alternative to Cartopy**: The ``plot_da`` function provides a simple, one-line alternative to creating maps with ``cartopy``, making it quick and easy to visualize your geospatial data.
