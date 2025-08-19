from __future__ import annotations
import re
from typing import Literal
import ipywidgets as wg
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from IPython.display import display
from .extension import TimeSeriesDataExtension
from .plots import TimeSeriesPlotter

from ..mascope_data.wrapper import MascopeDataWrapper
from ..plot_tools import extract_figure_data
from ..logging_config import logger  # Import the shared logger
from ..widgets_config import DEFAULT_BOX_PROPERTIES


class TimeSeriesWidget:
    """
    Builds widget selector for timeseries plots.
    """

    def __init__(
        self,
        dataset: MascopeDataWrapper,
        on_click: callable | None = None,
        peak_search: bool = False,
    ):
        """
        The widget is designed to work with a dataset that contains
        TimeSeriesExtension -extension.

        It allows users to select different
        time aggregation methods and visualization options
        for time series data.
        It also provides an option to search for untarget peaks
        in the time series data.
        Callback function can be provided to handle click events
        on the figure traces.

        :param dataset: MascopeDataWrapper -dataset.
        :type dataset: MascopeDataWrapper
        :param on_click: callable callback-function for click event handler, defaults to None
        :type on_click: callable | None, optional
        :param peak_search: boolean flag for peak search, defaults to False
        :type peak_search: bool, optional
        :raises ValueError: If peak_search is True and dataset not contain peak_data and
        BinningExtension.
        """
        self.dataset = dataset
        self.dataset.extend(TimeSeriesDataExtension)
        # Initialize on_click functionality if callback function is given
        self.on_click = on_click
        if self.on_click is not None:
            self.click_output = wg.Output()
        # Initialize ClosestPeakSelector if peak_search is enabled
        self.untarget_peak_selector = None
        self.peak_search = peak_search
        if self.peak_search:
            self.add_peak_search()
        self.timeseries_plots = TimeSeriesPlotter(dataset=self.dataset)
        self.ts_figure = wg.Output()
        # Setup widget-selector and display
        self.create_widgets()
        self.create_layout()
        self.setup_event_handlers()
        self.create_figure_output()
        self.display_layout()

        self.dataset.add_observer("data_loaded", self.on_data_loaded)

        # Populate widgets with data if data is already loaded
        if self.dataset.data_loaded:
            self.on_data_loaded({"new": True})  # Simulate a change event

    @property
    def figure_data(self) -> pd.DataFrame:
        """
        Returns the data used to build the traces in the timeseries figure.
        This method extracts the data from the figure and returns it as a pandas DataFrame.
        The DataFrame contains the following columns:
        - mz: The mass-to-charge ratio (m/z) values.
        - intensity: The intensity values corresponding to the m/z values.
        - name: The name of the trace.
        - customdata: Additional data associated with the trace hoverbox.

        :return: A pandas DataFrame containing the data used for the figure.
        :rtype: pd.DataFrame
        """
        return extract_figure_data(
            self.fig,
            x_col="x",  # Universal x-axis name because can be many
            y_col="intensity",
            name_col="name",
        )

    def create_widgets(self) -> None:
        """Create widgets"""

        self.wbx_line = wg.Checkbox(
            value=True, description="Add line to scatterplot", disabled=False
        )
        self.wbx_trendline = wg.Checkbox(
            value=False, description="Add trend line to scatterplot", disabled=False
        )
        self.wbx_timeaggregation = wg.Select(
            options=[None],
            value=None,
            description="Time aggregation: ",
            disabled=False,
            style={"description_width": "initial"},
            rows=6,
            layout=wg.Layout(width="95%"),
        )
        self.wbx_timemethod = wg.Select(
            options=["mean", "median"],
            value="mean",
            description="Aggregation method: ",
            disabled=False,
            style={"description_width": "initial"},
            rows=3,
            layout=wg.Layout(width="95%"),
        )

    def create_layout(self) -> None:
        """Combine widgets to layout"""

        top_row = self.wbx_timeaggregation
        figure_settings = wg.VBox(
            [
                self.wbx_timemethod,
                self.wbx_line,
                self.wbx_trendline,
            ],
        )
        # Accordion for advanced settings
        figure_settings_accordion = wg.Accordion(children=[figure_settings])
        figure_settings_accordion.set_title(0, "Figure settings")
        # Add ClosestPeakSelector accordion if peak_search is enabled
        if self.peak_search:
            untarget_peak_selector_accordion = wg.Accordion(
                children=[self.untarget_peak_selector.widget]
            )
            untarget_peak_selector_accordion.set_title(0, "Add custom target peaks")
            # Combine both accordions
            self.group = wg.VBox(
                [
                    wg.VBox(
                        [
                            top_row,
                            figure_settings_accordion,
                            untarget_peak_selector_accordion,
                        ],
                        **DEFAULT_BOX_PROPERTIES,
                    ),
                    self.ts_figure,
                ]
            )
        else:
            # Only include the figure settings accordion
            self.group = wg.VBox(
                [
                    wg.VBox(
                        [top_row, figure_settings_accordion], **DEFAULT_BOX_PROPERTIES
                    ),
                    self.ts_figure,
                ],
            )

    def display_layout(self) -> None:
        """Displays the widget layout."""

        display(self.group)
        if self.on_click is not None:
            display(self.click_output)

    def setup_event_handlers(self) -> None:
        """
        Generate event handlers which follows widget values
        and updates the figure when value is changed.
        """
        # Attach observer to activate widget-selectors when time aggregation is not None
        self.wbx_timeaggregation.observe(self.update_timemethod, names="value")
        # Attach observers to widgets to update figure when value is changed
        self.wbx_line.observe(self.update_figures, names="value")
        self.wbx_trendline.observe(self.update_figures, names="value")
        self.wbx_timeaggregation.observe(self.update_figures, names="value")
        self.wbx_timemethod.observe(self.update_figures, names="value")

    def update_timemethod(self, change) -> None:
        """
        Changes time summarize method to
        Disabled if time aggregation
        method is None."""

        new_value = change["new"]

        self.wbx_timemethod.disabled = new_value is None

    def create_figure_output(self) -> None:
        """Build output containing plotly figure layout"""

        self.fig = self.timeseries_plots.base_timeseries_figure()
        with self.ts_figure:
            self.ts_figure.clear_output()
            display(self.fig)

    def update_figures(self, change=None) -> None:  # pylint: disable=unused-argument
        """
        Updates figure traces based on current widget selections.

        - This method gathers the current values from various
        control widgets and refresh the plot.
        - It also attaches the `click_callback` method from
        ClickEventHandler -class to the figure traces
        `on_click` event if callable -function is given as 'on_click' -parameter.
        """
        try:
            logger.debug("Updating time series figures based on widget selections.")
            # Update layout
            layout = self.timeseries_plots.build_layout()
            self.fig.update_layout(layout)
            logger.debug("Figure layout updated.")

            timeseries_df = self.dataset.timeseries
            filter_by = "trace_name"

            trace_names = timeseries_df[filter_by].unique().tolist()
            if self.on_click is not None:
                with self.click_output:
                    self.click_output.clear_output()
                logger.debug("Cleared click-event output.")
                for trace in self.fig.data:
                    trace.on_click(None)

            with self.fig.batch_update():
                self.fig.data = []
                logger.debug("Cleared existing traces from time series figure.")

                # Determine the type of figure to build
                time_aggregation = self.wbx_timeaggregation.value
                method = self.wbx_timemethod.value
                trend_line = self.wbx_trendline.value
                lines = self.wbx_line.value

                match time_aggregation:
                    case "Diurnal Cycle":
                        logger.debug("Building diurnal cycle traces.")
                        traces = self.get_diurnal_cycle_traces(
                            trace_names,
                            method,
                            trend_line,
                            lines,
                            filter_by,
                        )
                        x_axis = "hour_of_day"
                    case None:
                        logger.debug("Building raw time series traces.")
                        traces = self.get_timeseries_traces(
                            trace_names,
                            trend_line,
                            lines,
                            filter_by,
                        )
                        x_axis = "datetime"
                    case "Hourly" | "Daily" | "Weekly" | "Monthly":
                        logger.debug(
                            f"Building aggregated time series traces ({time_aggregation})."
                        )
                        traces = self.get_aggregated_timeseries_traces(
                            trace_names,
                            time_aggregation,
                            method,
                            trend_line,
                            lines,
                            filter_by,
                        )
                        x_axis = "datetime"
                    case _:
                        raise ValueError(
                            f"Invalid time_aggregation='{time_aggregation}', expected one of "
                            f"['Diurnal Cycle', None, 'Hourly', 'Daily', 'Weekly', 'Monthly']"
                        )
                # Add traces to the figure
                self.fig.add_traces(traces)
                logger.debug(f"Added {len(traces)} traces to time series figure.")
                self.fig.update_layout(
                    self.timeseries_plots.build_layout(
                        diurnal_cycle=(time_aggregation == "Diurnal Cycle")
                    )
                )
                logger.debug("Time series figure layout updated after adding traces.")
            # Attach the click event handler to the figure traces
            if self.on_click is not None:
                self.timeseries_plots.attach_click_callback(
                    fig=self.fig,
                    callback_function=self.on_click,
                    click_output=self.click_output,
                    reference_df=self.get_reference_data(),
                    x_axis=x_axis,
                    y_axis="intensity",
                )
                logger.debug("Click event handler attached to time series figure.")
        except (
            AttributeError,
            ValueError,
            TypeError,
        ) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "update_figures",
                e,
            )

    def get_diurnal_cycle_traces(
        self,
        target_compound_values: list,
        method: Literal["mean", "median"],
        trend_line: bool,
        lines: bool,
        filter_by: Literal["target_compound_id", "trace_name"] = "trace_name",
    ) -> list[go.FigureWidget]:
        """
        Returns diurnal cycle traces for the given compounds

        The method iterates over the target_compound_values
        and generates traces for each compound using the
        get_compound_diurnal_cycle_trace method of the
        TimeSeriesPlotter class.

        :param target_compound_values: list of compound IDs or formula names.
        :type target_compound_values: list
        :param method: method to use for summarizing diurnal cycle
        :type method: Literal["mean", "median"]
        :param trend_line: if True, add a trend line to the plot
        :type trend_line: bool
        :param lines: if True, add horizontal lines for each compound
        :type lines: bool
        :return: list of figurewidget traces
        :param filter_by: Column to filter by ('target_compound_id' or 'trace_name').
        :type filter_by: Literal["target_compound_id", "trace_name"]
        :rtype: list[go.FigureWidget]
        """
        return [
            trace
            for compound in target_compound_values
            for trace in self.timeseries_plots.get_compound_diurnal_cycle_trace(
                target_compound_value=compound,
                filter_by=filter_by,
                method=method,
                trend_line=trend_line,
                lines=lines,
            )
            if trace is not None
        ]

    def get_timeseries_traces(
        self,
        target_compound_values: list,
        trend_line: bool,
        lines: bool,
        filter_by: Literal["target_compound_id", "trace_name"] = "trace_name",
    ) -> list[go.FigureWidget]:
        """
        Returns time series traces for the given compounds.

        The method iterates over the target_compound_values
        and generates traces for each compound using the
        get_compound_timeseries_trace method of the
        TimeSeriesPlotter class.

        :param target_compound_values: list of compound IDs or formula names.
        :type target_compound_values: list
        :param trend_line: if True, add a trend line to the plot
        :type trend_line: bool
        :param lines: if True, add horizontal lines for each compound
        :type lines: bool
        :param filter_by: Column to filter by ('target_compound_id' or 'trace_name').
        :type filter_by: Literal["target_compound_id", "trace_name"]
        :return: list of figurewidget traces
        :rtype: list[go.FigureWidget]
        """

        return [
            trace
            for compound in target_compound_values
            for trace in self.timeseries_plots.get_compound_timeseries_trace(
                target_compound_value=compound,
                filter_by=filter_by,
                trend_line=trend_line,
                lines=lines,
            )
            if trace is not None
        ]

    def get_aggregated_timeseries_traces(
        self,
        target_compound_values: list,
        freq: Literal["Hourly", "Daily", "Weekly", "Monthly"],
        method: Literal["mean", "median"],
        trend_line: bool,
        lines: bool,
        filter_by: Literal["target_compound_id", "trace_name"] = "trace_name",
    ) -> list:
        """
        Returns aggregated time series traces for the given compounds.

        The method iterates over the target_compound_values
        and generates traces for each compound using the
        get_compound_aggregated_timeseries_trace method of the
        TimeSeriesPlotter class.

        :param target_compound_values: list of compound IDs or formula names.
        :type target_compound_values: list
        :param freq: frequency to aggregate time series
        :type freq: Literal["Hourly", "Daily", "Weekly", "Monthly"]
        :param method: method to use for aggregating time series
        :type method: Literal["mean", "median"]
        :param trend_line: if True, add a trend line to the plot
        :type trend_line: bool
        :param lines: if True, add horizontal lines for each compound
        :type lines: bool
        :param filter_by: Column to filter by ('target_compound_id' or 'trace_name').
        :type filter_by: Literal["target_compound_id", "trace_name"]
        :return: list of figurewidget traces
        :rtype: list
        """

        return [
            trace
            for compound in target_compound_values
            for trace in self.timeseries_plots.get_compound_aggregated_timeseries_trace(
                target_compound_value=compound,
                filter_by=filter_by,
                freq=freq,
                method=method,
                trend_line=trend_line,
                lines=lines,
            )
            if trace is not None
        ]

    def get_reference_data(self) -> pd.DataFrame:
        """
        Returns reference data for the current figure.

        The method checks the current time aggregation setting
        and retrieves the corresponding reference data from the dataset.
        The reference data is used for the click event handler
        to provide additional information about the clicked point.

        :raises ValueError: if time aggregation is not one of
        ['Diurnal Cycle', None, 'Hourly', 'Daily', 'Weekly', 'Monthly']
        :return: reference data for the current figure
        :rtype: pd.DataFrame
        """

        time_aggregation = self.wbx_timeaggregation.value
        method = self.wbx_timemethod.value

        match time_aggregation:
            case "Diurnal Cycle":
                reference_df = self.dataset.get_compound_diurnal_cycle(method=method)
            case None:
                reference_df = self.dataset.get_compound_timeseries()
            case "Hourly" | "Daily" | "Weekly" | "Monthly":
                reference_df = self.dataset.get_compound_aggregated_timeseries(
                    freq=time_aggregation, method=method
                )
            case _:
                raise ValueError(
                    f"Invalid time_aggregation='{time_aggregation}', expected one of "
                    f"['Diurnal Cycle', None, 'Hourly', 'Daily', 'Weekly', 'Monthly']"
                )

        return reference_df

    def add_peak_search(self) -> None:
        """
        Add peaksearch-widget
        to the widget layout if peak_search is enabled.
        """

        if self.untarget_peak_selector is None:
            self.untarget_peak_selector = ClosestPeakSelector(
                peaks=[],
                on_selection_change=self.on_peak_selection_change,
            )

    def on_peak_selection_change(self, peak: str) -> None:
        """
        Callback function for ClosestPeakSelector
        to handle peak selection changes.

        This method is called when a peak is selected
        in the ClosestPeakSelector widget.
        It adds the selected peak to the dataset
        and updates the figure traces.

        :param peak: peak to add.
        :type peak: str
        """
        self.dataset.add_untarget_peak(peak)
        self.update_figures()

    def on_clear_cache(self, change) -> None:  # pylint: disable=unused-argument
        """
        Callback for when `memory_cleared` changes.
        React to clearing the cache.
        When the cache is cleared:
        - Clears the selected peaks in the ClosestPeakSelector.
        - Updates the available peaks in the ClosestPeakSelector.
        - Updates the figure traces.

        :param change: The change event dictionary.
        :type change: dict
        """
        try:
            logger.info(
                "Cache cleared. Resetting peak selector and updating time series traces."
            )
            self.update_figures()
            self.update_closest_peak_selector()
            logger.info("Time series traces updated successfully after cache clear.")
        except (
            AttributeError,
            ValueError,
            TypeError,
        ) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "on_clear_cache",
                e,
            )

    def on_data_loaded(self, change) -> None:
        """
        Callback for when `data_loaded` changes.
        React to data being cleared or loaded.
        - If new data is loaded, updates figure traces.
        - If data is cleared, removes traces and reset figure to base.

        :param change: The change event dictionary.
        :type change: dict
        """
        try:
            if change["new"]:  # If data_loaded is True
                logger.info(
                    "Data loaded. Preparing to populate widgets and update time series figures."
                )
                self.populate_widgets_with_data()
                self.update_figures()
                self.dataset.add_observer("memory_cleared", self.on_clear_cache)
                logger.debug(
                    f"Observer for `memory_cleared` attached to {self.__class__.__name__}"
                    " on_clear_cache"
                )
                logger.info("Time series traces updated successfully after data load.")
            else:
                logger.info("Data cleared. Resetting time series figure to base state.")
                self.reset_figure()
                logger.info("Time series figure reset to base state successfully.")
        except (
            AttributeError,
            ValueError,
            TypeError,
        ) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "on_data_loaded",
                e,
            )

    def populate_widgets_with_data(self) -> None:
        """
        Populate widgets with data from the dataset when `data_loaded` is True.

        This method is called when the dataset is loaded.
        It populates the time aggregation options
        and updates the ClosestPeakSelector widget
        with the latest peaks from the dataset.
        """
        try:
            logger.debug("Populating widgets with data from the dataset.")
            # Populate time aggregation options
            self.wbx_timeaggregation.options = [
                "Diurnal Cycle",
                "Hourly",
                "Daily",
                "Weekly",
                "Monthly",
                None,
            ]
            logger.debug("Time aggregation options populated.")
            if self.peak_search:
                self.update_closest_peak_selector()
        except (
            AttributeError,
            ValueError,
            TypeError,
        ) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "populate_widgets_with_data",
                e,
            )

    def update_closest_peak_selector(self) -> None:
        """
        Update the ClosestPeakSelector widget with the latest peaks from the dataset.
        Clears selected peaks and updates available peaks.

        This method is called when the dataset is loaded
        and when the cache is cleared.
        It validates the dataset requirements for peak search
        and updates the available peaks in the ClosestPeakSelector widget.
        It also checks if the timeseries contains untarget peaks
        and adds them to the selected peaks in the ClosestPeakSelector.
        If the dataset does not contain the required properties
        for peak search, an error is logged.
        """
        try:
            if not self.untarget_peak_selector:
                return

            # Validate dataset requirements for peak search
            self.untarget_peak_selector.validate_peak_search_requirements(self.dataset)

            # Update available peaks
            peaks = self.dataset.peaks_grouped.mz_weighted_mean.unique()
            self.untarget_peak_selector.peaks = np.array(peaks)
            logger.info(
                "Updated available peaks in ClosestPeakSelector. Total peaks: %d",
                len(peaks),
            )
            # Clear selected peaks
            self.untarget_peak_selector.selected_list.options = []
            self.untarget_peak_selector.selected_peaks = []
            # Check if timeseries contains untarget peaks
            untarget_peaks = (
                self.dataset.timeseries["trace_name"]
                .fillna("")  # Replace None with an empty string
                .apply(
                    lambda x: re.findall(r"\b\d+\.\d+\b", x)
                )  # Extract numeric values
                .explode()  # Flatten lists of numbers
                .dropna()  # Remove any NaN values
                .unique()  # Get unique values
            )
            # Add unique peaks to the selector
            self.untarget_peak_selector.selected_peaks = list(
                set(self.untarget_peak_selector.selected_peaks).union(untarget_peaks)
            )
            self.untarget_peak_selector.selected_list.options = [
                f"{p}" for p in self.untarget_peak_selector.selected_peaks
            ]
            logger.debug("Updated selected peaks in ClosestPeakSelector.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "update_closest_peak_selector",
                e,
            )

    def reset_figure(self) -> None:
        """
        Reset the figure to the base plot when data is not loaded.

        This method clears the figure and resets it to the base plot.
        It also clears the click-event output if present.
        If the ClosestPeakSelector widget is present,
        it clears the selected peaks and options.
        Method is called when the dataset is cleared
        or when the data is not loaded.
        """
        try:
            logger.debug("Resetting time series figure to base state.")
            if self.untarget_peak_selector:  # Reset peak-selector
                self.untarget_peak_selector.selected_list.options = []
                self.untarget_peak_selector.selected_peaks = []
            with (
                self.fig.batch_update()
            ):  # Clear the figure and reset it to the base plot
                self.fig.data = []
                logger.debug("Cleared all traces from time series figure.")
                layout = self.timeseries_plots.build_layout()
                self.fig.update_layout(layout)
                logger.debug("Figure layout reset to base state.")
                if self.on_click is not None:  # Clear click-event output if present
                    with self.click_output:
                        self.click_output.clear_output()
                    logger.debug("Cleared click-event output from time series figure.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "reset_figure",
                e,
            )


class ClosestPeakSelector:
    """
    A widget for selecting the closest peaks from a list of peaks.
    """

    def __init__(self, peaks: list, on_selection_change: callable | None = None):
        """
        The ClosestPeakSelector widget allows users to search for
        the closest peak from a given list of peaks.
        It provides a search box for entering a peak value,
        an "Add Peak" button to add the closest peak to a selected list,
        and a list to display the selected peaks.
        The widget also includes a callback function that is triggered
        when the selection changes.
        The widget is designed to work with a list of float numbers
        representing peaks.

        :param peaks: list of float numbers representing peaks.
        :type peaks: list
        :param on_selection_change: Callback function when selection changes.
        :type on_selection_change: callable | None, optional
        """
        self.peaks = np.array(peaks)
        self.selected_peaks = []
        self.on_selection_change = on_selection_change

        # Set up the widget layout
        self.create_widgets()
        self.create_layout()
        self.setup_event_handlers()

    def create_widgets(self) -> None:
        """Create widgets"""

        self.search_box = wg.FloatText(
            placeholder="Enter a peak value...",
            description="Search:",
            style={"description_width": "initial"},
            layout=wg.Layout(width="300px"),
        )
        self.add_button = wg.Button(
            description="Add Peak",
            button_style="success",
            layout=wg.Layout(width="150px"),
        )
        self.selected_list = wg.Select(
            options=[],
            description="Added Peaks:",
            style={"description_width": "initial"},
            layout=wg.Layout(width="300px", height="200px"),
        )

    def create_layout(self) -> None:
        """Combine widgets to layout"""

        self.widget = wg.VBox([self.search_box, self.add_button, self.selected_list])

    def setup_event_handlers(self) -> None:
        """Setup event handlers for widgets"""

        self.search_box.observe(self.find_closest_peak, names="value")
        self.add_button.on_click(self.add_peak)

    def find_closest_peak(self, change: dict) -> None:
        """Find the closest peak to the entered value.

        This method is called when the value in the search box changes.
        It calculates the closest peak from the list of peaks
        and updates the search box with the closest peak value.
        The closest peak is determined by finding the peak
        with the minimum absolute difference from the entered value.

        :param change: The change event dictionary containing the new value.
        :type change: dict
        :return: None
        """
        if change["new"] is not None:
            value = change["new"]
            closest_peak = self.peaks[np.abs(self.peaks - value).argmin()]
            self.search_box.value = (
                closest_peak  # Update the input field with the closest peak
            )

    def add_peak(self, _) -> None:
        """
        Add the closest peak to the selected list.

        This method is called when the "Add Peak" button is clicked.
        It adds the closest peak to the selected list
        and updates the selected peaks list.
        If a callback function is provided, it is called
        with the selected peak value.
        """
        peak = self.search_box.value
        if peak not in self.selected_peaks:
            self.selected_peaks.append(peak)
            self.selected_list.options = self.selected_list.options + (f"{peak:.4f}",)
            if self.on_selection_change:  # Trigger the on_selection_change callback
                self.on_selection_change(float(peak))

    def display_layout(self) -> None:
        """Display the widget."""
        display(self.widget)

    def validate_peak_search_requirements(self, dataset: MascopeDataWrapper) -> None:
        """
        Validate that the dataset contains
        the required properties for peak search
        and that they return valid DataFrames.

        This method checks if the dataset contains the required properties
        for peak search, including 'peaks_matched' and 'binning_intensity'.
        If any of the required properties are missing or invalid,
        a ValueError is raised with an appropriate message.

        :param dataset: The dataset to validate.
        :type dataset: MascopeDataWrapper
        :raises ValueError: If the required properties are missing
        or invalid.
        """
        dataset_attributes = dataset.__dict__

        def validate_attribute(attr):
            if attr not in dataset_attributes:
                # Trigger building the attribute only if not already cached
                if not hasattr(dataset, attr):
                    raise ValueError(
                        f"Peak search is enabled, but the dataset does not contain "
                        f"the required property: '{attr}'."
                    )
                dataset_attributes[attr] = getattr(dataset, attr)

            # Validate the attribute
            df = dataset_attributes[attr]
            if not isinstance(df, pd.DataFrame) or df.empty:
                raise ValueError(
                    f"The '{attr}' property does not return a valid DataFrame or is empty."
                )

        required_attributes = ["peaks_matched", "binning_intensity"]

        for attr in required_attributes:
            validate_attribute(attr)
