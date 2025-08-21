import subprocess
import warnings

from pyproj import CRS

X_NAME_CANDIDATES = ("x", "lon", "longitude")
Y_NAME_CANDIDATES = ("y", "lat", "latitude")
TIME_NAME_CANDIDATES = ("time", "t", "times")


def check_ffmpeg():
    """Checks if ffmpeg is available on the system and outputs a warning if not."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        warnings.warn("ffmpeg is not found. Some functionalities might be limited.")


def guess_coord_name(da_coords, candidates, provided_name, coord_type_for_error) -> str:
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


def process_crs(da, crs):
    if crs is None:
        if "spatial_ref" in da.coords:
            crs = da.spatial_ref.attrs.get("crs_wkt", 4326)
        else:
            crs = 4326
    return CRS.from_user_input(crs)
