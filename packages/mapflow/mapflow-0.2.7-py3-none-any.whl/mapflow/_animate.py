import subprocess
from multiprocessing import Pool
from os import cpu_count
from pathlib import Path
from tempfile import TemporaryDirectory

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from pyproj import CRS
from tqdm.auto import tqdm

from ._misc import TIME_NAME_CANDIDATES, X_NAME_CANDIDATES, Y_NAME_CANDIDATES
from ._plot import PlotModel


class Animation:
    """
    Args:
        x (np.ndarray): Array of x-coordinates (e.g., longitudes).
        y (np.ndarray): Array of y-coordinates (e.g., latitudes).
        crs (int | str | CRS, optional): Coordinate Reference System.
            Defaults to 4326 (WGS84).
        verbose (int, optional): Verbosity level. If > 0, progress bars
            will be shown. Defaults to 0.
        borders (gpd.GeoDataFrame | gpd.GeoSeries | None, optional):
            Custom borders to use for plotting. If None, defaults to
            world borders. Defaults to None.

    .. code-block:: python

        import xarray as xr
        from mapflow import Animation

        ds = xr.tutorial.open_dataset("era5-2mt-2019-03-uk.grib")
        da = ds["t2m"].isel(time=slice(120))

        animation = Animation(x=da.longitude, y=da.latitude, verbose=1)
        animation(da, "animation.mp4")

    """

    def __init__(self, x, y, crs=4326, verbose=0, borders=None):
        self.plot = PlotModel(x=x, y=y, crs=crs, borders=borders)
        self.verbose = verbose

    @staticmethod
    def upsample(data, ratio=5):
        if ratio == 1:
            return data
        else:
            nt, ny, nx = data.shape
            ret = np.empty((ratio * (nt - 1) + 1, ny, nx), dtype=data.dtype)
            ret[::ratio] = data
            delta = np.diff(data, axis=0)
            for k in range(1, ratio):
                ret[k::ratio] = ret[::ratio][:-1] + k * delta / ratio
            return ret

    @staticmethod
    def _process_title(title, upsample_ratio):
        if isinstance(title, str):
            return [title] * upsample_ratio
        elif isinstance(title, (list, tuple)):
            return np.repeat(title, upsample_ratio).tolist()
        else:
            raise ValueError("Title must be a string or a list of strings.")

    def __call__(
        self,
        data,
        path,
        figsize: tuple = None,
        title=None,
        fps: int = 24,
        upsample_ratio: int = 2,
        cmap="jet",
        qmin=0.01,
        qmax=99.9,
        vmin=None,
        vmax=None,
        norm=None,
        log=False,
        label=None,
        dpi=180,
        n_jobs=None,
        timeout="auto",
    ):
        """
        Generates an animation from a sequence of 2D data arrays.

        The method processes the input data, optionally upsamples it for smoother
        transitions, generates individual frames in parallel, and then compiles
        these frames into a video file using FFmpeg.

        Args:
            data (np.ndarray): A 3D numpy array where the first dimension is time
                (or frame sequence) and the next two are spatial (y, x).
            path (str | Path): The output path for the generated video file.
                Supported formats are avi, mov and mp4.
            figsize (tuple[float, float], optional): Figure size (width, height)
                in inches. Defaults to None (matplotlib's default).
            title (str | list[str], optional): Title for the plot. If a string,
                it's used for all frames. If a list, each element corresponds to a
                frame's title (before upsampling). Defaults to None.
            fps (int, optional): Frames per second for the output video.
                Defaults to 24.
            upsample_ratio (int, optional): Factor by which to upsample the data
                along the time axis for smoother animations. Defaults to 2.
            cmap (str, optional): Colormap to use for the plot. Defaults to "jet".
            qmin (float, optional): Minimum quantile for color normalization.
                Defaults to 0.01.
            qmax (float, optional): Maximum quantile for color normalization.
                Defaults to 99.9.
            vmin (float, optional): Minimum value for color normalization. Overrides qmin.
            vmax (float, optional): Maximum value for color normalization. Overrides qmax.
            norm (matplotlib.colors.Normalize, optional): Custom normalization object.
            log (bool, optional): Whether to use a logarithmic color scale. Defaults to False.
            label (str, optional): Label for the colorbar. Defaults to None.
            dpi (int, optional): Dots per inch for the saved frames. Defaults to 180.
            n_jobs (int, optional): Number of parallel jobs for frame generation.
                Defaults to 2/3 of CPU cores.
        """
        norm = self.plot._norm(data, vmin, vmax, qmin, qmax, norm, log)
        self._animate(
            data=data,
            path=path,
            frame_generator=self._generate_frame,
            figsize=figsize,
            title=title,
            fps=fps,
            upsample_ratio=upsample_ratio,
            cmap=cmap,
            norm=norm,
            label=label,
            dpi=dpi,
            n_jobs=n_jobs,
            timeout=timeout,
        )

    def quiver(
        self,
        u,
        v,
        path,
        subsample: int = 1,
        figsize: tuple = None,
        title=None,
        fps: int = 24,
        upsample_ratio: int = 2,
        cmap="jet",
        qmin=0.01,
        qmax=99.9,
        vmin=None,
        vmax=None,
        norm=None,
        log=False,
        label=None,
        dpi=180,
        n_jobs=None,
        timeout="auto",
        **kwargs,
    ):
        self._animate(
            data=(u, v),
            path=path,
            frame_generator=self._generate_quiver_frame,
            figsize=figsize,
            title=title,
            fps=fps,
            upsample_ratio=upsample_ratio,
            cmap=cmap,
            norm=norm,
            label=label,
            dpi=dpi,
            n_jobs=n_jobs,
            timeout=timeout,
            subsample=subsample,
            qmin=qmin,
            qmax=qmax,
            vmin=vmin,
            vmax=vmax,
            log=log,
            **kwargs,
        )

    def _animate(
        self,
        data,
        path,
        frame_generator,
        figsize: tuple = None,
        title=None,
        fps: int = 24,
        upsample_ratio: int = 2,
        cmap="jet",
        norm=None,
        label=None,
        dpi=180,
        n_jobs=None,
        timeout="auto",
        **kwargs,
    ):
        titles = self._process_title(title, upsample_ratio)

        # Upsample data
        if isinstance(data, tuple):  # For quiver
            u, v = data
            magnitude = np.sqrt(u**2 + v**2)
            norm = self.plot._norm(
                magnitude.values,
                vmin=kwargs.get("vmin"),
                vmax=kwargs.get("vmax"),
                qmin=kwargs.get("qmin", 0.01),
                qmax=kwargs.get("qmax", 99.9),
                norm=kwargs.get("norm"),
                log=kwargs.get("log", False),
            )
            kwargs["x_name"] = _guess_coord_name(u.coords, X_NAME_CANDIDATES, kwargs.get("x_name"), "x")
            kwargs["y_name"] = _guess_coord_name(u.coords, Y_NAME_CANDIDATES, kwargs.get("y_name"), "y")
            u = self.upsample(u.values, ratio=upsample_ratio)
            v = self.upsample(v.values, ratio=upsample_ratio)
            data = (u, v)
            data_len = len(u)
        else:  # For single field
            norm = self.plot._norm(
                data,
                vmin=kwargs.get("vmin"),
                vmax=kwargs.get("vmax"),
                qmin=kwargs.get("qmin", 0.01),
                qmax=kwargs.get("qmax", 99.9),
                norm=kwargs.get("norm"),
                log=kwargs.get("log", False),
            )
            data = self.upsample(data, ratio=upsample_ratio)
            data_len = len(data)

        with TemporaryDirectory() as tempdir:
            frame_paths = [Path(tempdir) / f"frame_{k:08d}.png" for k in range(data_len)]
            args = []
            for k in range(data_len):
                if isinstance(data, tuple):
                    frame_data = (data[0][k], data[1][k])
                else:
                    frame_data = data[k]

                arg_tuple = (
                    frame_data,
                    frame_paths[k],
                    figsize,
                    titles[k],
                    cmap,
                    norm,
                    label,
                    dpi,
                    kwargs,
                )
                args.append(arg_tuple)

            # Generate frames in parallel
            n_jobs = int(2 / 3 * cpu_count()) if n_jobs is None else n_jobs
            with Pool(processes=n_jobs) as pool:
                list(
                    tqdm(
                        pool.imap(frame_generator, args),
                        total=data_len,
                        disable=(not self.verbose),
                        desc="Frames generation",
                        leave=False,
                    )
                )

            timeout = max(20, 0.1 * data_len) if timeout == "auto" else timeout
            self._create_video(tempdir, path, fps, timeout=timeout)

    def _generate_frame(self, args):
        """Generates a frame and saves it as a PNG."""
        data_frame, frame_path, figsize, title, cmap, norm, label, dpi, _ = args
        self.plot(
            data=data_frame,
            figsize=figsize,
            title=title,
            show=False,
            cmap=cmap,
            norm=norm,
            label=label,
        )
        plt.savefig(frame_path, dpi=dpi, bbox_inches="tight", pad_inches=0.05)
        plt.clf()
        plt.close()

    def _generate_quiver_frame(self, args):
        """Generates a quiver frame and saves it as a PNG."""
        (u_frame, v_frame), frame_path, figsize, title, cmap, norm, label, dpi, kwargs = args
        x_name = kwargs.get("x_name")
        y_name = kwargs.get("y_name")
        coords = {y_name: self.plot.y, x_name: self.plot.x}
        dims = (y_name, x_name)
        u_da = xr.DataArray(u_frame, coords=coords, dims=dims)
        v_da = xr.DataArray(v_frame, coords=coords, dims=dims)
        magnitude = np.sqrt(u_frame**2 + v_frame**2)
        self.plot(
            data=magnitude,
            figsize=figsize,
            title=title,
            show=False,
            cmap=cmap,
            norm=norm,
            label=label,
        )
        subsample = kwargs.get("subsample", 1)
        if subsample > 1:
            u_sub = u_da.isel({y_name: slice(None, None, subsample), x_name: slice(None, None, subsample)})
            v_sub = v_da.isel({y_name: slice(None, None, subsample), x_name: slice(None, None, subsample)})
            x = u_sub[x_name].values
            y = u_sub[y_name].values
            u_sub = u_sub.values
            v_sub = v_sub.values
        else:
            x = u_da[x_name].values
            y = u_da[y_name].values
            u_sub = u_da.values
            v_sub = v_da.values

        if u_da[x_name].ndim == 1:
            x, y = np.meshgrid(x, y)

        arrows_kwgs = kwargs.get("arrows_kwgs")
        if arrows_kwgs is None:
            arrows_kwgs = {}
        plt.quiver(x, y, u_sub, v_sub, **arrows_kwgs)
        plt.savefig(frame_path, dpi=dpi, bbox_inches="tight", pad_inches=0.05)
        plt.clf()
        plt.close()

    @staticmethod
    def _build_ffmpeg_cmd(tempdir, path, fps):
        path = Path(path)
        suffix = path.suffix.lower()
        if suffix not in (".avi", ".mkv", ".mov", ".mp4"):
            raise ValueError("Output format must be either .avi, .mkv, .mov or .mp4")

        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "image2",
            "-framerate",
            str(fps),
            "-i",
            str(Path(tempdir) / "frame_%08d.png"),
        ]
        if suffix in (".mkv", ".mov", ".mp4"):
            cmd.extend(["-vcodec", "libx265", "-crf", "22"])
        elif suffix == ".avi":
            cmd.extend(["-vcodec", "mpeg4", "-q:v", "5"])
        cmd.append(str(path))
        return cmd

    @staticmethod
    def _create_video(tempdir, path, fps, timeout):
        cmd = Animation._build_ffmpeg_cmd(tempdir, path, fps)
        try:
            result = subprocess.run(
                cmd,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
            )
            if result.stdout:  # Only print if there's output
                print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error during video creation: {e}")
            print(f"Command: {' '.join(cmd)}")
            print(f"Standard output: {e.stdout}")
            print(f"Standard error: {e.stderr}")
            raise
        except subprocess.TimeoutExpired:
            print(f"Video creation timed out after {timeout} seconds")
            raise


def process_crs(da, crs):
    if crs is None:
        if "spatial_ref" in da.coords:
            crs = da.spatial_ref.attrs.get("crs_wkt", 4326)
        else:
            crs = 4326
    ret = CRS.from_user_input(crs)
    return ret


def check_da(da: xr.DataArray, time_name, x_name, y_name, crs):
    if not isinstance(da, xr.DataArray):
        raise TypeError(f"Expected xarray.DataArray, got {type(da)}")
    for dim in (x_name, y_name, time_name):
        if dim not in da.coords:
            raise ValueError(f"Dimension '{dim}' not found in DataArray coordinates: {da.dims}")
    crs_ = process_crs(da, crs)
    if crs_.is_geographic:
        da[x_name] = xr.where(da[x_name] > 180, da[x_name] - 360, da[x_name])

    # For non-rectilinear grids (2D coordinates), sorting by spatial dimensions is not possible.
    if da[x_name].ndim == 1 and da[y_name].ndim == 1:
        da = da.sortby(x_name).sortby(y_name)

    da = da.sortby(time_name).squeeze()

    if da.ndim != 3:
        raise ValueError(
            f"DataArray must have 3 dimensions ({time_name}, {y_name}, {x_name}), got {da.ndim} dimensions."
        )

    # Ensure time is the first dimension
    if da[x_name].ndim == 1 and da[y_name].ndim == 1:
        da = da.transpose(time_name, y_name, x_name)
    elif list(da.dims)[0] != time_name:
        current_dims = list(da.dims)
        current_dims.remove(time_name)
        new_order = [time_name] + current_dims
        da = da.transpose(*new_order)
    return da, crs_


def _guess_coord_name(da_coords, candidates, provided_name, coord_type_for_error):
    """
    Guesses the coordinate name if not provided.
    Iterates through da_coords, compares lowercased names with candidates.
    """
    if provided_name is not None:
        return provided_name

    for coord_name_key in da_coords:
        # Convert coord_name_key to string before lower() in case it's not already a string
        coord_name_str = str(coord_name_key).lower()
        if coord_name_str in candidates:
            return str(coord_name_key)  # Return original case name

    raise ValueError(
        f"Could not automatically detect {coord_type_for_error}-coordinate. "
        f"Please specify '{coord_type_for_error}_name' from available coordinates: {list(da_coords.keys())}. "
        f"Tried to guess from candidates: {candidates}."
    )


def animate(
    da: xr.DataArray,
    path: str,
    time_name: str = None,
    x_name: str = None,
    y_name: str = None,
    crs=None,
    borders: gpd.GeoDataFrame | gpd.GeoSeries | None = None,
    verbose: int = 0,
    **kwargs,
):
    """
    Creates an animation from an xarray DataArray.

    This function prepares data from an xarray DataArray (e.g., handling
    geographic coordinates, extracting time information for titles) and
    then uses the `Animation` class to generate and save the animation.

    Args:
        da (xr.DataArray): Input DataArray with at least time, x, and y dimensions.
        path (str): Output path for the video file. Supported formats are avi, mov
            and mp4.
        time_name (str, optional): Name of the time coordinate in `da`. If None,
            it's guessed from ['time', 't', 'times']. Defaults to None.
        x_name (str, optional): Name of the x-coordinate (e.g., longitude) in `da`.
            If None, it's guessed from ['x', 'lon', 'longitude']. Defaults to None.
        y_name (str, optional): Name of the y-coordinate (e.g., latitude) in `da`.
            If None, it's guessed from ['y', 'lat', 'latitude']. Defaults to None.
        crs (int | str | CRS, optional): Coordinate Reference System of the data.
            Defaults to 4326 (WGS84).
        borders (gpd.GeoDataFrame | gpd.GeoSeries | None, optional):
            Custom borders to use for plotting. If None, defaults to
            world borders. Defaults to None.
        verbose (int, optional): Verbosity level for the Animation class.
            Defaults to 0.
        **kwargs: Additional keyword arguments passed to the Animation class, including:
            - cmap (str): Colormap for the plot. Defaults to "jet".
            - norm (matplotlib.colors.Normalize): Custom normalization object.
            - log (bool): Use logarithmic color scale. Defaults to False.
            - qmin (float): Minimum quantile for color normalization. Defaults to 0.01.
            - qmax (float): Maximum quantile for color normalization. Defaults to 99.9.
            - vmin (float): Minimum value for color normalization. Overrides qmin.
            - vmax (float): Maximum value for color normalization. Overrides qmax.
            - time_format (str): Strftime format for time in titles. Defaults to "%Y-%m-%dT%H".
            - upsample_ratio (int): Factor to upsample data temporally. Defaults to 4.
            - fps (int): Frames per second for the video. Defaults to 24.
            - n_jobs (int): Number of parallel jobs for frame generation.
            - dpi (int): Dots per inch for the saved frames. Defaults to 180.
            - timeout (str | int): Timeout for video creation. Defaults to 'auto'.


    .. code-block:: python

        import xarray as xr
        from mapflow import animate

        ds = xr.tutorial.open_dataset("era5-2mt-2019-03-uk.grib")
        animate(da=ds['t2m'].isel(time=slice(120)), path='animation.mp4')

    """
    # Guess coordinate names if not provided
    actual_time_name = _guess_coord_name(da.coords, TIME_NAME_CANDIDATES, time_name, "time")
    actual_x_name = _guess_coord_name(da.coords, X_NAME_CANDIDATES, x_name, "x")
    actual_y_name = _guess_coord_name(da.coords, Y_NAME_CANDIDATES, y_name, "y")

    da, crs_ = check_da(da, actual_time_name, actual_x_name, actual_y_name, crs)

    animation = Animation(
        x=da[actual_x_name].values,
        y=da[actual_y_name].values,
        crs=crs_,
        verbose=verbose,
        borders=borders,
    )
    output_path = Path(path)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    unit = da.attrs.get("unit", None) or da.attrs.get("units", None)
    time_format = kwargs.get("time_format", "%Y-%m-%dT%H")
    time = da[actual_time_name].dt.strftime(time_format).values
    field = da.name or da.attrs.get("long_name")
    titles = [f"{field} · {t}" for t in time]
    animation(
        data=da.values,
        path=output_path,
        title=titles,
        label=unit,
        **kwargs,
    )


def animate_quiver(
    u: xr.DataArray,
    v: xr.DataArray,
    path: str,
    time_name: str = None,
    x_name: str = None,
    y_name: str = None,
    crs=None,
    field_name: str = None,
    borders: gpd.GeoDataFrame | gpd.GeoSeries | None = None,
    verbose: int = 0,
    subsample: int = 1,
    arrows_kwgs: dict = None,
    **kwargs,
):
    """
    Creates a quiver animation from two xarray DataArrays.

    Args:
        u (xr.DataArray): Input DataArray for the U-component with at least time, x, and y dimensions.
        v (xr.DataArray): Input DataArray for the V-component with at least time, x, and y dimensions.
        path (str): Output path for the video file. Supported formats are avi, mov and mp4.
        time_name (str, optional): Name of the time coordinate in `da`. If None,
            it's guessed from ['time', 't', 'times']. Defaults to None.
        x_name (str, optional): Name of the x-coordinate (e.g., longitude) in `da`.
            If None, it's guessed from ['x', 'lon', 'longitude']. Defaults to None.
        y_name (str, optional): Name of the y-coordinate (e.g., latitude) in `da`.
            If None, it's guessed from ['y', 'lat', 'latitude']. Defaults to None.
        crs (int | str | CRS, optional): Coordinate Reference System of the data.
            Defaults to 4326 (WGS84).
        borders (gpd.GeoDataFrame | gpd.GeoSeries | None, optional):
            Custom borders to use for plotting. If None, defaults to
            world borders. Defaults to None.
        verbose (int, optional): Verbosity level for the Animation class.
            Defaults to 0.
        subsample (int, optional): The subsampling factor for the quiver arrows.
            For example, a value of 10 will plot one arrow for every 10 grid points.
            Defaults to 1.
        arrows_kwgs (dict, optional): Additional keyword arguments passed to
            `matplotlib.pyplot.quiver`. Defaults to None.
        **kwargs: Additional keyword arguments passed to the Animation class, including:
            - cmap (str): Colormap for the plot. Defaults to "jet".
            - norm (matplotlib.colors.Normalize): Custom normalization object.
            - log (bool): Use logarithmic color scale. Defaults to False.
            - qmin (float): Minimum quantile for color normalization. Defaults to 0.01.
            - qmax (float): Maximum quantile for color normalization. Defaults to 99.9.
            - vmin (float): Minimum value for color normalization. Overrides qmin.
            - vmax (float): Maximum value for color normalization. Overrides qmax.
            - time_format (str): Strftime format for time in titles. Defaults to "%Y-%m-%dT%H".
            - upsample_ratio (int): Factor to upsample data temporally. Defaults to 4.
            - fps (int): Frames per second for the video. Defaults to 24.
            - n_jobs (int): Number of parallel jobs for frame generation.
            - dpi (int): Dots per inch for the saved frames. Defaults to 180.
            - timeout (str | int): Timeout for video creation. Defaults to 'auto'.

    Example:
        .. code-block:: python

            import xarray as xr
            from mapflow import animate_quiver

            ds = xr.tutorial.load_dataset("air_temperature_gradient")
            animate_quiver(u=ds["dTdx"], v=ds["dTdy"], path='animation.mkv', subsample=3)
    """
    actual_time_name = _guess_coord_name(u.coords, TIME_NAME_CANDIDATES, time_name, "time")
    actual_x_name = _guess_coord_name(u.coords, X_NAME_CANDIDATES, x_name, "x")
    actual_y_name = _guess_coord_name(u.coords, Y_NAME_CANDIDATES, y_name, "y")

    u, crs_ = check_da(u, actual_time_name, actual_x_name, actual_y_name, crs)
    v, _ = check_da(v, actual_time_name, actual_x_name, actual_y_name, crs)

    animation = Animation(
        x=u[actual_x_name].values,
        y=u[actual_y_name].values,
        crs=crs_,
        verbose=verbose,
        borders=borders,
    )
    output_path = Path(path)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    unit = u.attrs.get("unit", None) or u.attrs.get("units", None)
    time_format = kwargs.get("time_format", "%Y-%m-%dT%H")
    time = u[actual_time_name].dt.strftime(time_format).values
    if field_name is None:
        titles = [f"{t}" for t in time]
    else:
        titles = [f"{field_name} · {t}" for t in time]

    animation.quiver(
        u=u,
        v=v,
        path=output_path,
        title=titles,
        label=unit,
        subsample=subsample,
        arrows_kwgs=arrows_kwgs,
        **kwargs,
    )
