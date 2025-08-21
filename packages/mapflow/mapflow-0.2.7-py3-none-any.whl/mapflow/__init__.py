from importlib.metadata import version

from ._animate import Animation, animate, animate_quiver
from ._misc import check_ffmpeg
from ._plot import PlotModel, plot_da, plot_da_quiver

check_ffmpeg()

__all__ = ["Animation", "PlotModel", "animate", "plot_da", "plot_da_quiver", "animate_quiver"]

__version__ = version("mapflow")
