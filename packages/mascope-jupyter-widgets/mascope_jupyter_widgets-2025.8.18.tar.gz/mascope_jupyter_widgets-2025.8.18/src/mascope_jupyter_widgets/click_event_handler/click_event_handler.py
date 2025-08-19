from __future__ import annotations
from typing import Any, Dict, Optional, TypedDict
import ipywidgets as wg
import pandas as pd
import plotly.graph_objects as go
from ipyaggrid import Grid
from IPython.display import display

from .helpers import restore_original_markers
from ..mascope_data.wrapper import MascopeDataWrapper
from ..plot_tools import extract_figure_data
from ..widgets_config import GRID_OPTIONS
from ..logging_config import logger  # Import the shared logger


class CallbackContext(TypedDict):
    """TypedDict for storing callback context attributes"""

    fig: go.FigureWidget  # FigureWidget to be used for click events
    click_output: wg.Output  # Output widget for displaying outputs
    dataset: MascopeDataWrapper  # Dataset containing wider set of dataframes
    reference_df: pd.DataFrame | None  # Reference DataFrame used for figure building
    x_axis: str | None  # Name of the x-axis column in the reference DataFrame
    y_axis: str | None  # Name of the y-axis column in the reference DataFrame
    clicked_dots_data: dict  # Clicked data points from reference DataFrame
    marker_points_idx: dict  # Clicked data points indices
    original_symbols: dict  # Original marker symbols
    original_colors: dict  # Original marker colors
    figure_stash: dict  # Cache for figures


class ClickEventHandler:
    """
    Class to handle click events in given figure.
    """

    def __init__(
        self,
        fig: go.FigureWidget,
        out: wg.Output,
        dataset: MascopeDataWrapper,
        callback_func: callable | None = None,
        reference_df: pd.DataFrame | None = None,
        x_axis: str | None = None,
        y_axis: str | None = None,
    ) -> None:
        """
        Initialize ClickEventHandler with given figure and output widget.

        This class is designed to handle click events on a Plotly figure and execute
        a callback function when a point is clicked.
        It also provides a context for the callback function,
        including the figure, dataset, and reference DataFrame.

        :param fig: go.FigureWidget which traces contains marker-points.
        :type fig: go.FigureWidget
        :param out: Output widget for displaying outputs.
        :type out: Output
        :param dataset: Dataset to be used for the click event.
        :type dataset: MascopeDataWrapper
        :param callback_func: Callback function to execute when a point is clicked.
        :type callback_func: callable | None
        :param reference_df: Optional reference DataFrame for additional data.
        :type reference_df: pd.DataFrame | None
        :param x_axis: Name of the x-axis column in the dataset.
        :type x_axis: str | None
        :param y_axis: Name of the y-axis column in the dataset.
        :type y_axis: str | None
        :raises TypeError: if callback_func is not callable or is None
        """

        self.callback_func = callback_func
        self.out = out
        if not callable(self.callback_func):
            logger.warning("callback_func is not callable or is None.")
        # Set the callback context for click events
        self.callback_context: CallbackContext = {
            "fig": fig,
            "click_output": out,
            "reference_df": reference_df,
            "dataset": dataset,
            "x_axis": x_axis,
            "y_axis": y_axis,
            "clicked_dots_data": {},  # {trace_name: [clicked_data_points]}
            "marker_points_idx": {},  # {trace_name: [clicked_data_points_indices]}
            "original_symbols": {},  # {trace_name: original_marker_symbols}
            "original_colors": {},  # {trace_name: original_marker_colors}
            "figure_stash": {},  # {trace_name: figure_stash}
        }
        self._figure: go.FigureWidget | None = None
        self._grid_data: pd.DataFrame | None = None
        self._figures_dict: dict | None = None
        self._annotation_box: wg.HTML | None = None
        self.reset_button = wg.Button(description="Reset Clicks")
        self.reset_button.on_click(self.reset_clicked_dots)

    @property
    def grid_data(self) -> pd.DataFrame:
        """
        Get the grid table data.

        This method returns the grid table data result from the callback function.
        If the grid data is not set, it returns an empty DataFrame.
        If the callback function is not set, it returns an empty DataFrame.

        :return: DataFrame containing the grid data.
        :rtype: pd.DataFrame"""

        if self._grid_data is None:
            logger.warning("Callback Grid data is not set.")
            return pd.DataFrame()

        return self._grid_data

    @property
    def figure_data(self) -> pd.DataFrame:
        """
        Get the figure data.

        This method extracts the data from the figure and returns it as a DataFrame.
        If the figure is not set, it returns an empty DataFrame.
        If the callback function is not set, it returns an empty DataFrame.

        :return: DataFrame containing the figure data.
        :rtype: pd.DataFrame
        """

        if hasattr(self, "_figures_dict") and self._figures_dict:
            # Concatenate data from all figures in the dict
            dfs = []
            for key, fig in self._figures_dict.items():
                df = extract_figure_data(
                    fig,
                    x_col="x",
                    y_col="intensity",
                    name_col="name",
                )
                if not df.empty:
                    df["formula_or_mz"] = key
                    dfs.append(df)
            if dfs:
                return pd.concat(dfs, ignore_index=True)
            else:
                return pd.DataFrame()
        elif self._figure is not None:
            return extract_figure_data(
                self._figure,
                x_col="x",
                y_col="intensity",
                name_col="name",
            )
        else:
            logger.warning("No figure data available.")
            return pd.DataFrame()

    def click_callback(
        self,
        trace: go.Trace,
        points: dict,
        selector: Optional[Dict[str, Any]],  # pylint: disable=unused-argument
    ) -> None:
        """
        Set a callback function to be executed when a point is clicked.

        This method is called when a point in the figure is clicked.
        It collects the clicked point data and executes the callback function
        with the clicked point data and the callback context.
        The callback function should return either a DataFrame or a FigureWidget.
        The output of the callback function is displayed in the output widget.
        If the callback function is not set, a warning is logged.
        If the clicked point data is not valid, a warning is logged.
        If the callback function returns a DataFrame, it is displayed
        in a grid at the output widget.
        If the callback function returns a FigureWidget, it is displayed
        in the output widget.

        :param trace: clicked trace
        :type trace: go.Trace
        :param points: clicked points
        :type points: dict
        :param selector: A dictionary used to filter which traces trigger the event.
        :type selector: Optional[Dict[str, Any]]
        """

        if not callable(self.callback_func):
            logger.warning("Callback function is not callable.")
            return
        if not points or not points.xs or not points.point_inds:
            logger.warning("No valid points were clicked.")
            return
        # Collect points from the clicked data
        point_index = points.point_inds[0]
        clicked_point = {
            "trace_name": trace.name if hasattr(trace, "name") else "unknown_trace",
            "point_index": point_index,
            "x_value": trace.x[point_index],
            "y_value": trace.y[point_index],
        }
        logger.debug("Clicked point: %s", clicked_point)
        # Check if all required optional inputs are provided
        missing_inputs = []
        if self.callback_context.get("reference_df") is None:
            missing_inputs.append("reference_df")
        if self.callback_context.get("x_axis") is None:
            missing_inputs.append("x_axis")
        if self.callback_context.get("y_axis") is None:
            missing_inputs.append("y_axis")
        with self.out:
            self.out.clear_output()
            if missing_inputs:
                logger.warning(
                    "Missing inputs: %s. Provide these inputs for additional functionality.",
                    ", ".join(missing_inputs),
                )
                return
            # If all inputs are provided, call the callback function
            callback_output = self.callback_func(
                clicked_point=clicked_point, callback_context=self.callback_context
            )
            # Check the type of callback_output and display accordingly
            if isinstance(callback_output, pd.DataFrame):
                self._figures_dict = None
                logger.debug(
                    "Callback returned a DataFrame with %d rows and %d columns.",
                    callback_output.shape[0],
                    callback_output.shape[1],
                )
                display(
                    Grid(
                        grid_data=callback_output,
                        grid_options=GRID_OPTIONS,
                        height=600,
                    )
                )
                self._grid_data = callback_output
            if isinstance(callback_output, go.FigureWidget):
                self._figures_dict = None
                logger.debug("Callback returned a FigureWidget.")
                self._figure = callback_output
                display(self.reset_button)
                display(self._figure)
            if isinstance(callback_output, dict):
                self._figures_dict = callback_output
                # Each key is a formula (or mz), each value is a FigureWidget
                tabs = []
                titles = []
                for key, fig in callback_output.items():
                    fig.update_layout(width=1200)
                    out = wg.Output()
                    with out:
                        display(fig)
                    tabs.append(out)
                    titles.append(str(key))
                if tabs:
                    tab_widget = wg.Tab(children=tabs)
                    for i, title in enumerate(titles):
                        tab_widget.set_title(i, title)
                    display(tab_widget)
                else:
                    logger.warning("Callback returned an empty dict.")
                return
            else:
                logger.warning(
                    "Callback output is neither a DataFrame nor a FigureWidget."
                )

    def reset_clicked_dots(
        self, change=None  # pylint: disable=unused-argument
    ) -> None:
        """
        Reset the clicked dots data and marker points index.

        This method clears the clicked dots data and marker points index
        in the callback context. It is called when the reset button is clicked.
        It restores the original markers for all traces in the figure.
        It clears the new figure and resets the annotation box.

        :param change: The change event dictionary.
        :type change: dict
        """
        # Restore original markers for all traces
        fig = self.callback_context["fig"]
        original_symbols = self.callback_context["original_symbols"]
        original_colors = self.callback_context["original_colors"]
        for trace in fig.data:
            trace_name = trace.name
            if trace_name in original_symbols and trace_name in original_colors:
                restore_original_markers(
                    trace_name,
                    trace,
                    fig,
                    original_symbols,
                    original_colors,
                )
        # Clear clicked dots data and marker points index
        for trace_name in self.callback_context["clicked_dots_data"]:
            self.callback_context["clicked_dots_data"][trace_name] = (
                {}
                if isinstance(
                    self.callback_context["clicked_dots_data"][trace_name], dict
                )
                else []
            )
        for trace_name in self.callback_context["marker_points_idx"]:
            self.callback_context["marker_points_idx"][trace_name] = (
                {}
                if isinstance(
                    self.callback_context["marker_points_idx"][trace_name], dict
                )
                else []
            )
        # Clear the new figure if it exists and is not the original
        if self._figure is not None and self._figure is not fig:
            with self._figure.batch_update():
                self._figure.data = []
                self._figure.layout.annotations = []
                self._figure.layout.title = ""
                self._figure.layout = {}
                self._annotation_box.value = ""
