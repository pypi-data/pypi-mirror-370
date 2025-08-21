import warnings
from typing import Union

from matplotlib.axes import Axes

from mitoolspro.plotting.plots.plotter import Plotter
from mitoolspro.plotting.plots.validation.models import BoolParam
from mitoolspro.plotting.plots.validation.types import (
    ColormapSequence,
    ColormapType,
    ColorSequence,
    ColorSequences,
    ColorType,
    EdgeColorSequence,
    EdgeColorSequences,
    EdgeColorType,
    MarkerSequence,
    MarkerSequences,
    MarkerType,
    NormalizationSequence,
    NormalizationType,
    NumericSequence,
    NumericSequences,
    NumericType,
)


class ScatterPlotterException(Exception):
    pass


class ScatterPlotter(Plotter):
    def __init__(
        self,
        x_data: Union[NumericSequences, NumericSequence],
        y_data: Union[NumericSequences, NumericSequence],
        ax: Axes = None,
        **kwargs,
    ):
        super().__init__(x_data, y_data, ax=ax, **kwargs)
        self._scatter_params = {
            # General Axes.scatter Parameters that are independent of the number of data sequences
            "plot_non_finite": False,
            "hover": False,
            # Specific Parameters that are based on the number of data sequences
            "size": None,
            "marker": "o",
            "linewidth": None,
            "edgecolor": None,
            "facecolor": None,
            "colormap": None,
            "normalization": None,
            "vmin": None,
            "vmax": None,
        }
        self._init_params.update(self._scatter_params)
        self._set_init_params(**kwargs)

    def set_plot_non_finite(self, plot_non_finite: bool):
        BoolParam(value=plot_non_finite)
        self.plot_non_finite = plot_non_finite
        return self

    def set_hover(self, hover: bool):
        BoolParam(value=hover)
        self.hover = hover
        return self

    def set_size(self, size: Union[NumericSequences, NumericSequence, NumericType]):
        return self.set_numeric_sequences(size, param_name="size")

    def set_marker(self, markers: Union[MarkerSequences, MarkerSequence, MarkerType]):
        return self.set_marker_sequences(
            markers, param_name="marker", multi_param=False
        )

    def set_linewidth(
        self, linewidths: Union[NumericSequences, NumericSequence, NumericType]
    ):
        return self.set_numeric_sequences(linewidths, param_name="linewidth")

    def set_edgecolor(
        self, edgecolors: Union[EdgeColorSequences, EdgeColorSequence, EdgeColorType]
    ):
        return self.set_edgecolor_sequences(edgecolors, param_name="edgecolor")

    def set_facecolor(self, facecolor: Union[ColorSequences, ColorSequence, ColorType]):
        return self.set_color_sequences(facecolor, param_name="facecolor")

    def set_colormap(self, colormaps: Union[ColormapSequence, ColormapType]):
        return self.set_colormap_sequence(colormaps, param_name="colormap")

    def set_normalization(
        self, normalization: Union[NormalizationSequence, NormalizationType]
    ):
        return self.set_norm_sequence(normalization, param_name="normalization")

    def set_vmin(self, vmin: Union[NumericSequence, NumericType]):
        return self.set_numeric_sequences(vmin, "vmin")

    def set_vmax(self, vmax: Union[NumericSequence, NumericType]):
        return self.set_numeric_sequences(vmax, "vmax")

    def set_normalization_range(
        self,
        vmin: Union[NumericSequence, NumericType],
        vmax: Union[NumericSequence, NumericType],
    ):
        self.set_vmin(vmin)
        self.set_vmax(vmax)
        return self

    def _create_scatter_kwargs(self, n_sequence: int):
        scatter_kwargs = {
            "x": self.x_data[n_sequence],
            "y": self.y_data[n_sequence],
            "s": self.get_sequences_param("size", n_sequence),
            "c": self.get_sequences_param("color", n_sequence),
            "marker": self.get_sequences_param("marker", n_sequence),
            "cmap": self.get_sequences_param("colormap", n_sequence),
            "norm": self.get_sequences_param("normalization", n_sequence),
            "vmin": self.get_sequences_param("vmin", n_sequence),
            "vmax": self.get_sequences_param("vmax", n_sequence),
            "alpha": self.get_sequences_param("alpha", n_sequence),
            "linewidth": self.get_sequences_param("linewidth", n_sequence),
            "edgecolor": self.get_sequences_param("edgecolor", n_sequence),
            "facecolor": self.get_sequences_param("facecolor", n_sequence),
            "label": self.get_sequences_param("label", n_sequence),
            "zorder": self.get_sequences_param("zorder", n_sequence),
            "plotnonfinite": self.plot_non_finite,
        }
        if (
            not isinstance(scatter_kwargs.get("alpha", []), NumericType)
            and len(scatter_kwargs.get("alpha", [])) == 1
        ):
            scatter_kwargs["alpha"] = scatter_kwargs["alpha"][0]
        return scatter_kwargs

    def _create_plot(self):
        for n_sequence in range(self.n_sequences):
            scatter_kwargs = self._create_scatter_kwargs(n_sequence)
            scatter_kwargs = {k: v for k, v in scatter_kwargs.items() if v is not None}
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    self.ax.scatter(**scatter_kwargs)
            except Exception as e:
                raise ScatterPlotterException(f"Error while creating scatter plot: {e}")
        if self.hover and self.label is not None:
            pass
        return self.ax
