from copy import copy
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from matplotlib.collections import PatchCollection
from matplotlib.colors import LogNorm, Normalize
from matplotlib.patches import Polygon as PolygonPatch
from pyproj import CRS
from shapely.geometry import MultiPolygon

from ._misc import X_NAME_CANDIDATES, Y_NAME_CANDIDATES, guess_coord_name, process_crs


class PlotModel:
    """A class for plotting 2D data with geographic borders. Useful for multiple
    plots of the same geographic domain, as it pre-computes geographic borders.

    Args:
        x, y: Coordinates for the plot.
        crs: Coordinate Reference System. Defaults to 4326.
        borders (gpd.GeoDataFrame | gpd.GeoSeries | None): Custom borders to use.
            If None, defaults to world borders from a packaged GeoPackage.

    .. code-block:: python

        import xarray as xr
        from mapflow import PlotModel

        ds = xr.tutorial.open_dataset("era5-2mt-2019-03-uk.grib")
        da = ds["t2m"].isel(time=0)

        p = PlotModel(x=da.longitude, y=da.latitude)
        p(da)

    """

    def __init__(self, x, y, crs=4326, borders=None):
        self.x = np.asarray_chkfinite(x)
        self.y = np.asarray_chkfinite(y)
        if self.x.ndim != self.y.ndim:
            raise ValueError("x and y must have the same dimensionality (both 1D or both 2D)")

        self.crs = CRS.from_user_input(crs)
        if self.crs.is_geographic:
            self.aspect = 1 / np.cos((self.y.mean() * np.pi / 180))
        else:
            self.aspect = 1
        if self.x.ndim == 1:
            self.dx = abs(self.x[1] - self.x[0])
            self.dy = abs(self.y[1] - self.y[0])
        else:
            self.dx = np.diff(self.x, axis=1).max()
            self.dy = np.diff(self.y, axis=0).max()
        bbox = (
            self.x.min() - 10 * self.dx,
            self.y.min() - 10 * self.dy,
            self.x.max() + 10 * self.dx,
            self.y.max() + 10 * self.dy,
        )

        if borders is None:
            borders_ = gpd.read_file(Path(__file__).parent / "_static" / "world.gpkg")
        elif isinstance(borders, (gpd.GeoDataFrame, gpd.GeoSeries)):
            borders_ = borders
        else:
            raise TypeError("borders must be a geopandas GeoDataFrame, GeoSeries, or None.")
        borders_ = borders_.to_crs(self.crs).clip(bbox)
        self.borders = self._shp_to_patches(borders_)

    @staticmethod
    def _shp_to_patches(gdf):
        patches = []
        for poly in gdf.geometry.values:
            if isinstance(poly, MultiPolygon):
                for polygon in poly.geoms:
                    patches.append(PolygonPatch(polygon.exterior.coords))
            else:
                patches.append(PolygonPatch(poly.exterior.coords))
        return PatchCollection(patches, facecolor="none", linewidth=0.5, edgecolor="k")

    @staticmethod
    def _log_norm(data, vmin, vmax, qmin, qmax):
        """Generates a logarithmic normalization."""
        positive_data = data[data > 0]
        if len(positive_data) == 0:
            return Normalize(vmin=1e-1, vmax=1e0)

        vmin = np.nanpercentile(positive_data, q=qmin) if vmin is None else vmin
        vmax = np.nanpercentile(positive_data, q=qmax) if vmax is None else vmax

        if vmin <= 0 or vmax <= 0:
            raise ValueError(f"Normalization range for log scale must be positive. Got vmin={vmin}, vmax={vmax}")
        return LogNorm(vmin=vmin, vmax=vmax)

    @staticmethod
    def _norm(data, vmin, vmax, qmin, qmax, norm, log):
        """Generates a normalization based on the specified parameters.

        Args:
            data (array-like): Data to normalize.
            vmin (float): Minimum value for normalization.
            vmax (float): Maximum value for normalization.
            qmin (float): Minimum quantile for normalization (0-100).
            qmax (float): Maximum quantile for normalization (0-100).
            norm (matplotlib.colors.Normalize): Custom normalization object.
            log (bool): Indicates if a logarithmic scale should be used.

        Returns:
            matplotlib.colors.Normalize: Normalization object.

        Raises:
            ValueError: If qmin/qmax are not between 0-100 or if log=True with no positive values.
        """
        # Validate quantile ranges
        if not (0 <= qmin <= 100):
            raise ValueError(f"qmin must be between 0 and 100, got {qmin}")
        if not (0 <= qmax <= 100):
            raise ValueError(f"qmax must be between 0 and 100, got {qmax}")
        if qmin >= qmax:
            raise ValueError(f"qmin must be less than qmax, got {qmin} and {qmax}")

        if norm is not None:
            return norm

        if log:
            return PlotModel._log_norm(data, vmin, vmax, qmin, qmax)

        vmin = np.nanpercentile(data, q=qmin) if vmin is None else vmin
        vmax = np.nanpercentile(data, q=qmax) if vmax is None else vmax
        return Normalize(vmin=vmin, vmax=vmax)

    def _process_data(self, data):
        if not isinstance(data, np.ndarray):
            data = np.asarray(data)
        data = np.squeeze(data)
        if data.ndim != 2:
            raise ValueError("Data must be a 2D array.")

        if self.x.ndim == 1:
            if data.shape[0] != self.y.size or data.shape[1] != self.x.size:
                raise ValueError("Data shape does not match x and y dimensions.")
        else:
            if data.shape != self.x.shape:
                raise ValueError("Data shape does not match x and y dimensions.")
        return data

    def __call__(
        self,
        data,
        figsize=None,
        qmin=0.01,
        qmax=99.9,
        vmin=None,
        vmax=None,
        log=False,
        cmap="jet",
        norm=None,
        shading="nearest",
        shrink=0.4,
        label=None,
        title=None,
        show=True,
    ):
        """
        Plots a 2D data array using imshow or pcolormesh.

        This method handles the actual plotting of a single frame. It applies
        normalization, colormaps, adds a colorbar, overlays borders, sets the
        aspect ratio, title, and optionally displays the plot.

        Args:
            data (np.ndarray): 2D array of data to plot.
            figsize (tuple[float, float], optional): Figure size (width, height)
                in inches. Defaults to None (matplotlib's default).
            qmin (float, optional): Minimum quantile for color normalization if
                vmin is not set. Defaults to 0.01.
            qmax (float, optional): Maximum quantile for color normalization if
                vmax is not set. Defaults to 99.9.
            vmin (float, optional): Minimum value for color normalization.
                Overrides qmin. Defaults to None.
            vmax (float, optional): Maximum value for color normalization.
                Overrides qmax. Defaults to None.
            log (bool, optional): Whether to use a logarithmic color scale.
                Defaults to False.
            cmap (str, optional): Colormap to use. Defaults to "jet".
            norm (matplotlib.colors.Normalize, optional): Custom normalization object.
                Overrides vmin, vmax, qmin, qmax, log. Defaults to None.
            shading (str, optional): Shading method for pcolormesh.
                Defaults to "nearest".
            shrink (float, optional): Factor by which to shrink the colorbar.
                Defaults to 0.4.
            label (str, optional): Label for the colorbar. Defaults to None.
            title (str, optional): Title for the plot. Defaults to None.
            show (bool, optional): Whether to display the plot using `plt.show()`.
                Defaults to True.
        """
        data = self._process_data(data)
        norm = self._norm(data, vmin, vmax, qmin, qmax, norm, log=log)
        plt.figure(figsize=figsize)
        if (self.x.ndim == 1) and (self.y.ndim == 1):
            plt.imshow(
                X=data,
                cmap=cmap,
                norm=norm,
                origin="lower",
                extent=(
                    self.x.min() - self.dx / 2,
                    self.x.max() + self.dx / 2,
                    self.y.min() - self.dy / 2,
                    self.y.max() + self.dy / 2,
                ),
                interpolation=shading,
            )
        else:
            plt.pcolormesh(
                self.x,
                self.y,
                data,
                cmap=cmap,
                norm=norm,
                shading=shading,
                rasterized=True,
            )
        plt.colorbar(shrink=shrink, label=label)
        plt.xlim(self.x.min() - self.dx / 2, self.x.max() + self.dx / 2)
        plt.ylim(self.y.min() - self.dy / 2, self.y.max() + self.dy / 2)
        plt.gca().add_collection(copy(self.borders))
        plt.gca().set_aspect(self.aspect)
        plt.title(title)
        plt.gca().axis("off")
        plt.tight_layout()
        if show:
            plt.show()


def plot_da(da: xr.DataArray, x_name=None, y_name=None, crs=4326, **kwargs):
    """Convenience function for quick plotting of an xarray DataArray using PlotModel.

    This is a simplified wrapper around the `PlotModel` class that handles:
    - Automatic coordinate detection
    - CRS processing
    - Data sorting and longitude wrapping (for geographic CRS)
    - Single-call plotting

    For better performance when making multiple plots of the same geographic domain,
    consider using `PlotModel` directly, which pre-computes geographic borders and
    can be reused for multiple plots.

    Args:
        da: xarray DataArray with 2D data to plot. Must have appropriate coordinates.
        x_name: Name of the x-coordinate dimension. If None, will attempt to guess.
        y_name: Name of the y-coordinate dimension. If None, will attempt to guess.
        crs: Coordinate Reference System. Can be:
            - EPSG code (e.g., 4326 for WGS84)
            - PROJ string
            - pyproj.CRS object
            - If the DataArray has a 'crs' attribute, that will be used by default
        **kwargs: Additional arguments passed to PlotModel.__call__(), including:
            - figsize: Tuple (width, height) in inches
            - qmin/qmax: Quantile ranges for color scaling (0-100)
            - vmin/vmax: Explicit value ranges for color scaling
            - log: Whether to use logarithmic color scale
            - cmap: Colormap name
            - norm: Custom normalization
            - shading: Color shading method
            - shrink: Colorbar shrink factor
            - label: Colorbar label
            - title: Plot title
            - show: Whether to display the plot

    Example:
        .. code-block:: python

            import xarray as xr
            from mapflow import plot_da

            ds = xr.tutorial.open_dataset("era5-2mt-2019-03-uk.grib")
            plot_da(da=ds['t2m'].isel(time=0))

    See Also:
        PlotModel: The underlying plotting class used by this function
    """
    actual_x_name = guess_coord_name(da.coords, X_NAME_CANDIDATES, x_name, "x")
    actual_y_name = guess_coord_name(da.coords, Y_NAME_CANDIDATES, y_name, "y")

    if da[actual_x_name].ndim == 1 and da[actual_y_name].ndim == 1:
        da = da.sortby(actual_x_name).sortby(actual_y_name)
    crs_ = process_crs(da, crs)
    if crs_.is_geographic:
        da[actual_x_name] = xr.where(da[actual_x_name] > 180, da[actual_x_name] - 360, da[actual_x_name])

    p = PlotModel(x=da[actual_x_name].values, y=da[actual_y_name].values, crs=crs_)
    data = p._process_data(da.values)
    p(data, **kwargs)


def plot_da_quiver(
    u,
    v,
    x_name=None,
    y_name=None,
    crs=4326,
    subsample: int = 1,
    show=True,
    arrows_kwgs: dict = None,
    **kwargs,
):
    """
    Plots a quiver plot from two xarray DataArrays, representing the U and V
    components of a vector field.

    The magnitude of the vector field is represented by a color mesh, and the
    direction is shown with quiver arrows.

    Args:
        u (xr.DataArray): DataArray for the U-component of the vector field.
        v (xr.DataArray): DataArray for the V-component of the vector field.
        x_name (str, optional): Name of the x-coordinate dimension.
            If None, will attempt to guess.
        y_name (str, optional): Name of the y-coordinate dimension.
            If None, will attempt to guess.
        crs: Coordinate Reference System. Can be:
            - EPSG code (e.g., 4326 for WGS84)
            - PROJ string
            - pyproj.CRS object
            - If the DataArray has a 'crs' attribute, that will be used by default
        subsample (int, optional): The subsampling factor for the quiver arrows.
            For example, a value of 10 will plot one arrow for every 10 grid points.
            Defaults to 1.
        show: Whether to display the plot
        arrows_kwgs (dict, optional): Additional keyword arguments passed to
            `matplotlib.pyplot.quiver`. Defaults to None.
        **kwargs: Additional arguments passed to PlotModel.__call__(), including:
            - figsize: Tuple (width, height) in inches
            - qmin/qmax: Quantile ranges for color scaling (0-100)
            - vmin/vmax: Explicit value ranges for color scaling
            - log: Whether to use logarithmic color scale
            - cmap: Colormap name
            - norm: Custom normalization
            - shading: Color shading method
            - shrink: Colorbar shrink factor
            - label: Colorbar label
            - title: Plot title

    Example:
        .. code-block:: python

            import xarray as xr
            from mapflow import plot_da_quiver

            ds = xr.tutorial.load_dataset("air_temperature_gradient").isel(time=0)
            plot_da_quiver(u=ds["dTdx"], v=ds["dTdy"], subsample=4)

    See Also:
        PlotModel: The underlying plotting class used by this function.
    """
    actual_x_name = guess_coord_name(u.coords, X_NAME_CANDIDATES, x_name, "x")
    actual_y_name = guess_coord_name(u.coords, Y_NAME_CANDIDATES, y_name, "y")

    if u[actual_x_name].ndim == 1 and u[actual_y_name].ndim == 1:
        u = u.sortby(actual_x_name).sortby(actual_y_name)
        v = v.sortby(actual_x_name).sortby(actual_y_name)

    crs_ = process_crs(u, crs)
    if crs_.is_geographic:
        u[actual_x_name] = xr.where(u[actual_x_name] > 180, u[actual_x_name] - 360, u[actual_x_name])
        v[actual_x_name] = xr.where(v[actual_x_name] > 180, v[actual_x_name] - 360, v[actual_x_name])

    magnitude = np.sqrt(u**2 + v**2)
    p = PlotModel(x=u[actual_x_name].values, y=u[actual_y_name].values, crs=crs_)
    data = p._process_data(magnitude.values)
    p(data, show=False, **kwargs)

    if subsample > 1:
        u_subsampled = u.isel(
            {actual_y_name: slice(None, None, subsample), actual_x_name: slice(None, None, subsample)}
        )
        v_subsampled = v.isel(
            {actual_y_name: slice(None, None, subsample), actual_x_name: slice(None, None, subsample)}
        )
        x = u_subsampled[actual_x_name].values
        y = u_subsampled[actual_y_name].values
        u_subsampled = u_subsampled.values
        v_subsampled = v_subsampled.values
    else:
        x = u[actual_x_name].values
        y = u[actual_y_name].values
        u_subsampled = u.values
        v_subsampled = v.values

    if u[actual_x_name].ndim == 1:
        x, y = np.meshgrid(x, y)

    if arrows_kwgs is None:
        arrows_kwgs = {}
    plt.quiver(x, y, u_subsampled, v_subsampled, **arrows_kwgs)
    if show:
        plt.show()
