from __future__ import annotations
from threading import Timer
import numpy as np
import pandas as pd
import ipywidgets as wg
from IPython.display import display
from .extension import SampleTimeSeriesExtension
from .plots import SampleTimeSeriesPlotter
from ..mascope_data.wrapper import MascopeDataWrapper
from ..logging_config import logger  # Import the shared logger
from ..widgets_config import (
    DEFAULT_WIDGETS_PROPERTIES,
    DEFAULT_BOX_PROPERTIES,
)


class SampleTimeSeriesWidget:
    """
    Builds widget selector for sample-level timeseries data.
    """

    def __init__(self, dataset: MascopeDataWrapper) -> None:
        """
        The widget is designed to work with a dataset that has the
        SampleTimeSeriesExtension -extension.

        - This widget allows users to select a sample and a peak m/z value
        to display the corresponding sample-level timeseries data.
        - It also includes a search box for finding peaks by typing a value,
        as a default 25 nearest peaks for typed value are shown in
        'Peak m/z'
        - Sample-level timeseries(es) will be plotted as plotly figurewidget trace
        for selected sample and peak m/z value.
        - figure_data -property can be used to get figure data as pandas dataframe.
        """

        self.dataset = dataset
        self.dataset.extend(SampleTimeSeriesExtension)
        self.sample_timeseries_plots = SampleTimeSeriesPlotter(dataset=self.dataset)

        self.debounce_timer_peak_search = None  # Timer for debouncing peak search
        self.debounce_timer_mz_tolerance = None  # Timer for debouncing m/z tolerance
        self.sample_ts_figure = wg.Output()
        self.displayed_data = pd.DataFrame()

        # Set up the initial state of the widgets
        self.create_widgets()
        self.create_layout()
        self.create_figure_output()
        self.display_layout()

        # Attach observer for `data_loaded`
        self.dataset.add_observer("data_loaded", self.on_data_loaded)

        # Populate widgets if data is already loaded
        if self.dataset.data_loaded:
            self.on_data_loaded({"new": True})  # Simulate a change event

    @property
    def figure_data(self) -> pd.DataFrame:
        """
        Get the sample-level timeseries figure data as a pandas DataFrame.

        - This method returns copy of the displayed data as a pandas DataFrame
        to prevent unintended modifications to the original data.
        - The displayed data is updated when the user selects a peak
        from the dropdown or when the search box is used to find peaks.
        - If no data is available, it returns an empty DataFrame.

        :return: The displayed data as a pandas DataFrame.
        :rtype: pd.DataFrame
        """

        if self.displayed_data is not None:
            logger.info(
                "The resulting sample-level timeseries DataFrame contains %d rows and %d columns.",
                len(self.displayed_data),
                len(self.displayed_data.columns),
            )
            return self.displayed_data.copy()
        logger.warning("No data available for the sample-level timeseries figure.")
        return pd.DataFrame()  # Return an empty DataFrame if no data is available

    def create_widgets(self) -> None:
        """Create and display the widgets for peak search and sample-level
        timeseries display."""

        self.wbx_sample_dropdown = wg.Dropdown(
            options=[],
            description="Sample ID:",
            layout=wg.Layout(width="50%"),
        )
        self.wbx_mz_tolerance = wg.FloatText(
            value=3.0,
            description="Peak m/z tolerance (ppm):",
            disabled=False,
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_search_box = wg.Text(
            placeholder="Type a value to search peaks...",
            description="Search:",
            layout=wg.Layout(width="50%"),
        )
        self.wbx_peak_selector = wg.Dropdown(
            options=[],
            description="Peak m/z:",
            layout=wg.Layout(width="50%"),
        )

    def setup_event_handlers(self) -> None:
        """Set up event handlers for the widgets."""

        self.wbx_sample_dropdown.observe(self.update_peak_options, names="value")
        self.wbx_search_box.observe(self.handle_search_input, names="value")
        self.wbx_peak_selector.observe(
            self.update_sample_timeseries_figure, names="value"
        )
        self.wbx_mz_tolerance.observe(self.on_mz_tolerance_change, names="value")

    def create_layout(self) -> None:
        """Create the layout for the widgets."""

        self.group = wg.VBox(
            [
                wg.VBox(
                    [
                        wg.HBox([self.wbx_sample_dropdown, self.wbx_mz_tolerance]),
                        self.wbx_search_box,
                        self.wbx_peak_selector,
                    ],
                    **DEFAULT_BOX_PROPERTIES,
                ),
                self.sample_ts_figure,
            ]
        )

    def display_layout(self) -> None:
        """Displays the widget layout."""
        display(self.group)

    def create_figure_output(self) -> None:
        """Build output containing plotly figure layout"""

        self.fig = self.sample_timeseries_plots.base_timeseries_figure()
        with self.sample_ts_figure:
            self.sample_ts_figure.clear_output()
            display(self.fig)

    def update_peak_options(self, change) -> None:
        """
        Update peak options based on selected sample_item_id.

        This method is called when the (sample_item_name_datetime,
        sample_item_id) dropdown value changes.
        It updates the peak selector dropdown with the peaks corresponding
        to the selected sample_item_name_datetime
        (sample_item_id).

        :param change: The change event dictionary.
        :type change: dict
        """
        sample_item_id = change["new"]
        # Enable or disable mz_tolerance based on dropdown value
        self.wbx_mz_tolerance.disabled = sample_item_id is not None
        # Temporarily disable the observer for wbx_peak_selector to avoid recursion
        self.wbx_peak_selector.unobserve(
            self.update_sample_timeseries_figure, names="value"
        )
        top_peaks = (
            self.get_top_peaks()
            if sample_item_id is None
            else self.get_top_peaks(sample_item_id)
        )

        self.wbx_peak_selector.options = [(f"{peak:.4f}", peak) for peak in top_peaks]
        self.wbx_peak_selector.value = (
            None  # Clear the value to wait for user selection
        )
        # Re-enable the observer for wbx_peak_selector
        self.wbx_peak_selector.observe(
            self.update_sample_timeseries_figure, names="value"
        )
        # Clear previous data from the figure
        with self.fig.batch_update():
            self.fig.data = []
            self.fig.update_layout(title="")

    def get_top_peaks(self, sample_item_id: str | None = None, n: int = 100) -> list:
        """
        Get the top n peaks based on intensity.

        This method retrieves the top n peaks from the dataset based on
        their intensity values. If sample_item_id is provided, it filters
        the peaks for that specific sample. Otherwise, it retrieves the
        top peaks from all samples.

        :param sample_item_id: The ID of the sample item to filter peaks.
        :type sample_item_id: str | None, optional
        :param n: The number of top peaks to retrieve.
        :type n: int, optional
        :return: A list of top n peaks based on intensity.
        :rtype: list
        """

        if sample_item_id is None:
            df = self.dataset.peaks_matched
        else:
            df = self.dataset.peaks_matched[
                self.dataset.peaks_matched.sample_item_id == sample_item_id
            ]
        top_peaks_df = (
            df.sort_values("intensity", ascending=False)
            .drop_duplicates(subset=["mz"])
            .head(n)
        )
        return top_peaks_df["mz"].tolist()

    def find_nearest_peaks(
        self, typed_value: str, peaks: list, num_results: int = 25
    ) -> list:
        """
        Find the nearest peaks to the user's input.

        This method takes the user's input and finds the nearest peaks
        from the provided list of peaks. It returns a list of the nearest peaks.
        The search is performed by calculating the absolute difference
        between the typed value and each peak, and sorting the results.
        The number of nearest peaks to return is specified by the num_results parameter.

        :param typed_value: The value typed by the user.
        :type typed_value: str
        :param peaks: The list of peaks to search from.
        :type peaks: list
        :param num_results: The number of nearest peaks to return.
        :type num_results: int, Defaults to 25.
        :return: A list of nearest peaks.
        :rtype: list
        """
        try:
            typed_value = float(typed_value)
            logger.debug("Finding nearest peaks to typed value: %s", typed_value)
            peaks = np.array(peaks, dtype=float)
            # Calculate the absolute difference and sort by proximity
            nearest_indices = np.argsort(np.abs(peaks - typed_value))[:num_results]
            nearest_peaks = peaks[nearest_indices]
            logger.debug(
                "Nearest peaks found for typed value %s: %s",
                typed_value,
                nearest_peaks,
            )
            nearest_peaks = sorted(nearest_peaks)
            return [(f"{peak:.4f}", peak) for peak in nearest_peaks]
        except ValueError:
            logger.warning(
                "Invalid input for peak search: %s. Expected a float value.",
                typed_value,
            )
            return []

    def handle_search_input(self, change) -> None:
        """
        Handle user input in the search box with debounce.

        This method is called when the user types in the search box.
        It uses a timer to debounce the input, meaning it waits for a short period
        before performing the search. This prevents excessive calls to the search
        function while the user is still typing.

        :param change: The change event dictionary.
        :type change: dict
        """
        if self.debounce_timer_peak_search is not None:
            self.debounce_timer_peak_search.cancel()

        def perform_search():
            """Perform the search for nearest peaks."""
            typed_value = change["new"]
            sample_item_id = self.wbx_sample_dropdown.value

            if typed_value == "":
                # If search box is empty, show all peaks for the selected sample
                self.update_peak_options({"new": sample_item_id})
                return

            peaks = (
                self.dataset.peaks_matched["mz"].tolist()
                if sample_item_id is None
                else self.dataset.peaks_matched.loc[
                    self.dataset.peaks_matched.sample_item_id == sample_item_id,
                    "mz",
                ].tolist()
            )

            logger.debug("Finding nearest peaks for typed value: %s", typed_value)
            nearest_peaks = self.find_nearest_peaks(typed_value, peaks, num_results=25)
            logger.debug("Nearest peaks found for typed value %s.", typed_value)
            # Update the wbx_peak_selector with the nearest peaks
            self.wbx_peak_selector.options = nearest_peaks

            if nearest_peaks:
                # Try to find an exact match
                try:
                    typed_float = float(typed_value)
                    match = next(
                        (peak for _, peak in nearest_peaks if peak == typed_float),
                        None,
                    )
                except (AttributeError, ValueError, TypeError):
                    match = None
                # If no exact match, use the closest (by absolute difference)
                if match is not None:
                    self.wbx_peak_selector.value = match
                else:
                    # Find the peak with minimum absolute difference to typed_value
                    closest_peak = min(
                        (peak for _, peak in nearest_peaks),
                        key=lambda p: abs(p - float(typed_value)),
                    )
                    self.wbx_peak_selector.value = closest_peak
                logger.debug("Nearest peaks found")
            else:
                self.wbx_peak_selector.value = None
                logger.debug("No nearest peaks found. Clearing peak selector value.")

        # Set the debounce delay (e.g., 1 seconds)
        self.debounce_timer_peak_search = Timer(1, perform_search)
        self.debounce_timer_peak_search.start()

    def update_sample_timeseries_figure(self, change) -> None:
        """
        Updates figure traces based on current widget selections.

        This method is called when the user selects a peak from the dropdown.
        It fetches the sample-level timeseries data for the selected peak and sample,
        and add traces to figure.
        If no data is found, it prints a warning message to logger
        indicating that no data is available for the selected peak and sample.

        :param change: The change event dictionary.
        :type change: dict
        """
        peak_mz = change["new"]
        sample_item_id = self.wbx_sample_dropdown.value
        if peak_mz:
            with self.fig.batch_update():
                self.fig.data = []
                logger.debug(
                    "Clearing previous data from the sample-level timeseries figure "
                    "and updating with new data."
                )

                if sample_item_id is None:
                    # Combine timeseries data for all sample_item_id
                    self.displayed_data = self.dataset.get_sample_peak_timeseries(
                        peak_mz=float(peak_mz),
                        sample_item_id=None,
                        peak_mz_tolerance_ppm=self.wbx_mz_tolerance.value,
                    )
                    # Loop through each unique (sample_item_id, sample_item_name_datetime) and add traces
                    for (sample_id, sample_name), _ in self.displayed_data.groupby(
                        ["sample_item_id", "sample_item_name_datetime"]
                    ):
                        trace = (
                            self.sample_timeseries_plots.get_sample_timeseries_traces(
                                peak_mz=float(peak_mz),
                                sample_item_id=sample_id,
                                peak_mz_tolerance_ppm=self.wbx_mz_tolerance.value,
                            )
                        )
                        self.fig.add_traces(trace)
                        logger.debug(
                            "Adding traces to the sample-level timeseries figure for "
                            "peak m/z: %s and sample_item_name_datetime: %s",
                            peak_mz,
                            sample_name,
                        )
                else:
                    # Fetch timeseries data for the selected sample_item_id
                    self.displayed_data = self.dataset.get_sample_peak_timeseries(
                        peak_mz=float(peak_mz), sample_item_id=sample_item_id
                    )
                    trace = self.sample_timeseries_plots.get_sample_timeseries_traces(
                        peak_mz=float(peak_mz),
                        sample_item_id=sample_item_id,
                        peak_mz_tolerance_ppm=1.0,  # Use default tolerance (mascope_sdk)
                    )
                    self.fig.add_traces(trace)
                    logger.debug(
                        "Adding traces to the sample-level timeseries figure for peak "
                        "m/z: %s and sample_item_id: %s",
                        peak_mz,
                        sample_item_id,
                    )
                # Update the figure title
                self.fig.update_layout(
                    title=f"Sample Timeseries for Peak m/z: {peak_mz:.4f}"
                )
                logger.debug(
                    f"Figure title updated to 'Sample Timeseries for Peak m/z: {peak_mz:.4f}'."
                )
        else:
            logger.warning(
                f"No data found for peak {peak_mz} in sample {sample_item_id}."
            )

    def on_mz_tolerance_change(self, change) -> None:  # pylint: disable=unused-argument
        """
        Update the figure when the m/z tolerance value changes.
        Only update if a peak is selected and sample is 'All'.

        This method is called when the user changes the m/z tolerance value
        in the corresponding widget. It updates the figure with the new
        m/z tolerance value for the selected peak and sample.

        :param change: The change event dictionary.
        :type change: dict
        """

        # Use a separate debounce timer for tolerance
        if (
            hasattr(self, "debounce_timer_mz_tolerance")
            and self.debounce_timer_mz_tolerance is not None
        ):
            self.debounce_timer_mz_tolerance.cancel()

        def perform_update() -> None:
            """Perform the update for m/z tolerance change."""
            if (
                self.wbx_sample_dropdown.value is None
                and self.wbx_peak_selector.value is not None
            ):
                # Simulate a change event for the peak selector to trigger figure update
                self.update_sample_timeseries_figure(
                    {"new": self.wbx_peak_selector.value}
                )

        # Set the debounce delay (e.g., 0.5 seconds)
        self.debounce_timer_mz_tolerance = Timer(0.5, perform_update)
        self.debounce_timer_mz_tolerance.start()

    def on_clear_cache(self, change=None) -> None:  # pylint: disable=unused-argument
        """
        Callback for when `memory_cleared` changes.
        React to clearing the cache.
        When the cache is cleared:
        - Clears the selected peaks in the peak selector.
        - Updates the available peaks in the peak selector.
        - Clears the displayed data and resets the output.

        :param change: The change event dictionary.
        :type change: dict
        """
        try:
            logger.info(
                "Cache cleared. Resetting peak selector and output for sample-level "
                "timeseries."
            )
            # Temporarily disable observers
            self.wbx_sample_dropdown.unobserve(self.update_peak_options, names="value")
            self.wbx_search_box.unobserve(self.handle_search_input, names="value")
            self.wbx_peak_selector.unobserve(
                self.update_sample_timeseries_figure, names="value"
            )
            logger.debug("Observers removed.")
            logger.debug("Resetting sample-level timeseries widgets to default state.")
            self._reset_selectors()
            # Update the available peaks in the peak selector
            logger.info("Peak selector and output reset successfully.")
            self.populate_widgets_with_data()
            logger.info(
                "Sample-level timeseries widgets populated successfully after cache clear."
            )
            self.create_figure_output()
            logger.debug("Sample-level timeseries figure output recreated.")
        except (AttributeError, ValueError, TypeError) as e:
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
        - If new data is loaded, populate widgets and enable lazy loading.
        - If data is cleared, reset widgets to their default state.

        :param change: The change event dictionary.
        :type change: dict
        """
        try:
            if change["new"]:  # If data_loaded is True
                logger.info(
                    "Data loaded. Populating widgets and enabling lazy loading."
                )
                self.populate_widgets_with_data()
                self.create_figure_output()
                self.dataset.add_observer("memory_cleared", self.on_clear_cache)
                logger.info("Widgets populated successfully after data load.")
            else:
                logger.info("Data cleared. Resetting widgets to default state.")
                self.reset_widgets()
                logger.info("Widgets reset to default state successfully.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "on_data_loaded",
                e,
            )

    def populate_widgets_with_data(self) -> None:
        """
        Populate widgets with data from the dataset when `data_loaded` is True.

        This method is called when the dataset is loaded and the `data_loaded`
        attribute changes to True. It populates the sample dropdown with
        (sample_item_name_datetime, sample_item_id) values and the peak selector with unique
        peak m/z values. It also sets up event handlers for the widgets.
        """
        try:
            logger.debug(
                "Populating sample-level timeseries widgets with data from the dataset."
            )
            self.wbx_sample_dropdown.options = [("All", None)] + [
                (name, sid)
                for name, sid in zip(
                    self.dataset.match_samples.sample_item_name_datetime,
                    self.dataset.match_samples.sample_item_id,
                )
            ]
            self.wbx_sample_dropdown.value = None
            logger.debug(
                "Sample item ID dropdown populated using (sample_item_name_datetime,"
                " sample_item_id)."
            )
            # Populate wbx_peak_selector dropdown
            top_peaks = self.get_top_peaks()
            self.wbx_peak_selector.options = [
                (f"{peak:.4f}", peak) for peak in top_peaks
            ]
            self.wbx_peak_selector.value = None
            logger.debug("Peak selector dropdown populated.")

            logger.debug("Attaching observers to widgets.")
            self.setup_event_handlers()
            logger.debug("Observers attached successfully.")

        except (AttributeError, ValueError, TypeError) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "populate_widgets_with_data",
                e,
            )

    def reset_widgets(self) -> None:
        """
        Reset widgets to their default state when data is cleared.

        This method is called when the dataset is cleared and the `data_loaded`
        attribute changes to False. It removes observers from the widgets,
        resets the sample dropdown and peak selector to their default values,
        and clears the output. It also recreates the figure output.
        This ensures that the widgets are in a clean state and ready for new data
        to be loaded. The observers are removed to prevent any unwanted callbacks
        when the widgets are reset.
        """
        try:
            logger.debug("Removing observers and resetting widgets.")
            # Temporarily disable observers
            self.wbx_sample_dropdown.unobserve(self.update_peak_options, names="value")
            self.wbx_search_box.unobserve(self.handle_search_input, names="value")
            self.wbx_peak_selector.unobserve(
                self.update_sample_timeseries_figure, names="value"
            )
            logger.debug("Observers removed.")
            logger.debug("Resetting sample-level timeseries widgets to default state.")
            self._reset_selectors()
            logger.debug("Output cleared.")

            self.create_figure_output()
            logger.debug("Sample-level timeseries figure output recreated.")

        except (AttributeError, ValueError, TypeError) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "reset_widgets",
                e,
            )

    def _reset_selectors(self) -> None:
        """
        Reset the sample-level timeseries selectors to their default state.

        This method clears the selected values in the sample dropdown and
        peak selector, resets the search box, and clears the displayed data.

        It is called when the dataset is cleared or when the cache is cleared.
        """

        # Reset sample_item_id dropdown
        self.wbx_sample_dropdown.options = [("All", None)]
        self.wbx_sample_dropdown.value = None
        logger.debug("Sample file ID dropdown reset.")
        # Reset the search box
        self.wbx_search_box.value = ""
        logger.debug("Search box reset.")
        # Reset wbx_peak_selector dropdown
        self.wbx_peak_selector.options = []
        self.wbx_peak_selector.value = None
        logger.debug("Peak selector dropdown reset.")

        # Clear output
        with self.sample_ts_figure:
            self.sample_ts_figure.clear_output()
            self.displayed_data = pd.DataFrame()
        logger.debug("Displayed data cleared and output reset.")
