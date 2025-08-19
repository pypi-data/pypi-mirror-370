from typing import Literal
import pandas as pd
import numpy as np
import pandera as pa
import ipywidgets as wg
import matplotlib.colors as mcolors
import plotly.graph_objects as go
from ..plot_tools import hover_string, DEFAULT_SCATTER_TYPE
from .schemas import (
    peaks_mass_defect_scaled_schema,
)
from ..mascope_data.wrapper import MascopeDataWrapper
from ..click_event_handler.click_event_handler import (
    ClickEventHandler,
)


class MassDefectPlotter:
    """
    Class containing functions to build mass-defect related
    plotly figure traces by utlizing
    dataset with MassDefectDataExtension -extension."""

    def __init__(self, dataset: MascopeDataWrapper):
        """
        Initialize mass_defect extended dataset to self

        :param dataset: MascopeDataWrapper -dataset with
        MassDefectDataExtension- extension class.
        :type dataset: MascopeDataWrapper
        """
        self.dataset = dataset
        # Initialize ClickEventHandler with default empty values
        self.click_event_handler = ClickEventHandler(
            fig=None,
            out=None,
            dataset=self.dataset,
            callback_func=None,
            reference_df=None,
            x_axis=None,
            y_axis=None,
        )

        # Ensure grid_data and figure_data return empty DataFrames by default
        self.click_event_handler._grid_data = pd.DataFrame()
        self.click_event_handler._figure = None

    def base_mass_defect_figure(
        self,
        width: float = None,
        height: float = None,
    ) -> go.FigureWidget:
        """
        Build base FigureWidget and
        setup layout for mass defect plot.

        :param width: width of the figure, defaults to None
        :type width: float, optional
        :param height: height of the figure, defaults to None
        :type height: float, optional
        :return: FigureWidget for mass defect traces
        :rtype: go.FigureWidget
        """

        fig = go.FigureWidget()
        layout = self.create_layout(
            xaxis_title="m/z [Th]",
            yaxis_title="mass defect [Th]",
            title="",
            width=width,
            height=height,
        )
        layout["xaxis"]["range"] = [0, 1000]
        layout["yaxis"]["range"] = [-0.5, 0.5]
        fig.update_layout(layout)

        return fig

    def create_layout(
        self,
        xaxis_title: str,
        yaxis_title: str,
        title: str,
        width: float = None,
        height: float = 600,
    ) -> dict:
        """
        Create the layout dictionary for the plot.

        :param xaxis_title : Name for the x-axis.
        :type xaxis_title : str
        :param yaxis_title: Name for the y-axis
        :type yaxis_title: str
        :param title: Title of the plot
        :type title: str
        :param width: figure width, defaults to None
        :type width: float, optional
        :param height: figure height, defaults to None
        :type height: float, optional
        :return: Layout dictionary
        :rtype: dict
        """

        layout = {
            "legend_orientation": "h",
            "title": title,
            "legend_title": "Sample type",
            "autosize": True,
            "width": width,
            "height": height,
            "margin": dict(l=40, r=40, t=40, b=40),
            "plot_bgcolor": "white",
            "yaxis": {
                "title": yaxis_title,
                "dtick": 0.05,
                "showline": True,
                "linecolor": "black",
                "gridcolor": "lightgrey",
                "autorange": True,
            },
            "xaxis": {
                "title": xaxis_title,
                "autorange": True,
                "dtick": 50,
                "showline": True,
                "linecolor": "black",
                "gridcolor": "lightgrey",
            },
        }

        return layout

    @pa.check_input(peaks_mass_defect_scaled_schema, "df")
    def create_mass_defect_trace(
        self,
        df: pd.DataFrame,
        sample_name: str,
        mz: str,
        scaling_method: Literal[
            "intensity",
            "log-normalized/min_max_intensity",
            "norm_intensity",
            "sample_item_id",
        ],
        annotation: str | int | float,
        unit: str,
        symbol: str = "circle",
        show_colorbar: bool = True,
        color: str = None,
    ) -> go.FigureWidget:
        """
        Add a trace to the plot based on the provided DataFrame and parameters.

        :param df: DataFrame containing data for the trace.
        :type df: pd.DataFrame
        :param sample_name: Name of the sample being plotted.
        :type sample_name: str
        :param mz: Column name for mz values ('mz' OR 'mz_round').
        :type mz: str
        :param scaling_method: Scaling -method to be used for dot colors and marker-size
        :type scaling_method: Literal[
            "intensity",
            "log-normalized/min_max_intensity",
            "norm_intensity",
            "sample_item_id",
        ]
        :param annotation: Column name for annotations. Will be turned to 'str'.
        :type annotation: str
        :param unit: Unit for the intensity values.
        :type unit: str
        :param symbol: Symbol for the trace markers, defaults to None
        :type symbol: str, optional
        :param show_colorbar: Should the colorbar be shown, defaults to None
        :type show_colorbar: bool, optional
        :param color: Should the colorbar be shown, defaults to None
        :type color: bool, optional
        :return: Scatter trace for the plot
        :rtype: go.Scattergl (DEFAULT_SCATTER_TYPE)
        """
        # Sort values so that highest intensity values are plotted on top
        df = df.sort_values(by="intensity", ascending=True)
        if scaling_method == "sample_item_id" and color is None:
            raise ValueError(
                "When scaling_method is 'sample_item_id', color must be provided."
            )
        if scaling_method != "sample_item_id" and color is not None:
            raise ValueError(
                "Color can only be provided when scaling_method is 'sample_item_id'."
            )
        # Define Hover box elements
        elements = ["sample_item_id", "sample_item_name", "mz", "intensity", "unit"]
        hover_items = hover_string(df[elements].columns)
        # Select color and size based on the `scaling_method`
        marker_colour_intensity, marker_size_intensity, colorscale = (
            self._determine_marker_properties(df, scaling_method, color)
        )
        # Validate shape_size values
        if marker_size_intensity.empty:
            sizeref = 1
        else:
            sizeref = 2.0 * marker_size_intensity.max() / (40.0**2)
        # Define marker properties
        marker = {
            "symbol": np.repeat(symbol, len(df)),
            "size": marker_size_intensity,
            "line": {"width": 0},
            "color": marker_colour_intensity,
            "colorscale": colorscale,
            "colorbar": (
                {"thickness": 20, "title": f"Intensity ({unit})"}
                if show_colorbar
                else None
            ),
            "sizemode": "area",
            "sizeref": sizeref,
            "sizemin": 4,
        }
        df[annotation] = df[annotation].fillna("").astype("str")
        trace = DEFAULT_SCATTER_TYPE(
            x=df[mz],
            y=df["kendrick_mass_defect"],
            mode="markers+text",
            text=df[annotation],
            textposition="top right",
            textfont=dict(color="black", size=10),
            name=f"{sample_name} (n={len(df)})",
            marker=marker,
            customdata=df[elements],
            hovertemplate=hover_items,
        )

        return trace

    @pa.check_input(peaks_mass_defect_scaled_schema, "df")
    def _determine_marker_properties(
        self,
        df: pd.DataFrame,
        scaling_method: Literal[
            "intensity",
            "log-normalized/min_max_intensity",
            "norm_intensity",
            "sample_item_id",
        ],
        color: str,
    ) -> tuple[pd.Series, pd.Series]:
        """
        Determine the marker color and
        size properties based on `scaling_method`.

        :param df: 'peaks_mass_defect_scaled' - dataframe with 'intensity' and normalized columns:
        'min_max_intensity', 'log1p_min_max_intensity' and 'norm_intensity'.
        :type df: pd.DataFrame
        :param scaling_method: The type of scaling method being plotted.
        :type scaling_method: Literal[
            "intensity",
            "log-normalized/min_max_intensity",
            "norm_intensity",
            "sample_item_id",
        ]
        :param color: Color for the trace markers if
        scaling_method is 'sample_item_id'.
        :type color: str, optional
        :return: Two series of values indicating color - and
        size of marker in each datapoint and str | None for colorscale.
        :rtype: Tuple[pd.Series, pd.Series, str | None]
        """

        log_values = np.log(df["intensity"])
        colorscale = "rainbow"
        match scaling_method:
            case "intensity":
                marker_colour_intensity = df["intensity"]
                marker_size_intensity = (
                    df["min_max_intensity"] if (log_values < 0).any() else log_values
                )
            case "log-normalized/min_max_intensity":
                if (log_values < 0).any():
                    norm_diff_maxmean = max(df["min_max_intensity"]) - np.mean(
                        df["min_max_intensity"]
                    )
                    if norm_diff_maxmean < 0.8:
                        marker_colour_intensity = df["min_max_intensity"]
                        marker_size_intensity = df["min_max_intensity"]
                    else:
                        marker_colour_intensity = df["log1p_min_max_intensity"]
                        marker_size_intensity = df["log1p_min_max_intensity"]
                else:
                    marker_colour_intensity = log_values
                    marker_size_intensity = log_values
            case "norm_intensity":
                marker_colour_intensity = df["norm_intensity"]
                marker_size_intensity = (
                    df["min_max_intensity"]
                    if (df["norm_intensity"].values < 0).any()
                    else df["norm_intensity"]
                )
            case "sample_item_id":
                # Scale marker size based on log1p-intensity
                marker_size_intensity = pd.Series(
                    np.interp(
                        df["log1p_intensity"],
                        (df["log1p_intensity"].min(), df["log1p_intensity"].max()),
                        (3, 30),
                    ),
                    index=df.index,
                )
                marker_colour_intensity = self._generate_scaled_colors(
                    df["intensity"], color
                )
                # Set colorscale to None for different samples
                colorscale = None
            case _:
                raise ValueError(
                    f"Invalid scaling method '{scaling_method}'. "
                    "Please use 'intensity', 'log-normalized/min_max_intensity', 'norm_intensity' "
                    " or 'sample_item_id'."
                )

        return marker_colour_intensity, marker_size_intensity, colorscale

    def _generate_scaled_colors(
        self, marker_size_intensity: pd.Series, base_color: str
    ) -> list[str]:
        """Generate colors with varying opacity
        based on marker size values.

        :param marker_size_intensity: Series of marker size values
        :type marker_size_intensity: pd.Series
        :param base_color: Base color for the markers
        :type base_color: str
        :return: List of hex color values
        :rtype: List[str]
        """
        # Normalize to 0-1 range
        norm_marker_size_intensity = (
            marker_size_intensity - marker_size_intensity.min()
        ) / (marker_size_intensity.max() - marker_size_intensity.min())
        # Scale alpha from 0.1 (faint) to 1 (strong)
        rgba_colors = [
            mcolors.to_rgba(base_color, alpha=0.1 + 0.9 * intensity)
            for intensity in norm_marker_size_intensity
        ]
        # Convert to hex format
        return [mcolors.to_hex(color) for color in rgba_colors]

    def attach_click_callback(
        self,
        fig: go.FigureWidget,
        callback_function: callable,
        click_output: wg.Output,
        reference_df: pd.DataFrame,
        x_axis: str,
        y_axis: str,
    ) -> None:
        """Attach a callback function to the click event handler.

        :param fig: FigureWidget to attach the callback to.
        :type fig: go.FigureWidget
        :param callback_function: Callback function to be executed on click.
        :type callback_function: callable
        :param click_output: Output widget to display clicked data.
        :type click_output: wg.Output
        :param reference_df: Reference DataFrame for clicked data.
        :type reference_df: pd.DataFrame
        :param x_axis: x-axis column name.
        :type x_axis: str
        :param y_axis: y-axis column name.
        :type y_axis: str
        """
        # Initialize ClickEventHandler
        self.click_event_handler = ClickEventHandler(
            fig=fig,
            out=click_output,
            dataset=self.dataset,
            callback_func=callback_function,
            reference_df=reference_df,
            x_axis=x_axis,
            y_axis=y_axis,
        )
        # Attach callback function to traces
        for trace in fig.data:
            trace.on_click(self.click_event_handler.click_callback, append=False)
