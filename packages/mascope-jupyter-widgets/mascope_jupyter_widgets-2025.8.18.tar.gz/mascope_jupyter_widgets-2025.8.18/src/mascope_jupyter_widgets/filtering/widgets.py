import copy
import pandas as pd
import ipywidgets as wg
import numpy as np
from IPython.display import display
from ipyaggrid import Grid

from .extension import FilteringExtension, filter_decorator

from ..mascope_data.wrapper import MascopeDataWrapper
from ..widgets_config import (
    DEFAULT_WIDGETS_PROPERTIES,
    DEFAULT_BOX_PROPERTIES,
    GRID_OPTIONS,
)
from ..logging_config import logger  # Import the shared logger


class FilteringWidget:
    "Handles dataset subsetting by usings different metrics of the data"

    def __init__(self, dataset: MascopeDataWrapper):
        """Initialize the FilteringWidget class.

        :param dataset: MascopeDataWrapper -dataset
        :type dataset: MascopeDataWrapper
        """

        self.dataset = dataset
        self.dataset.extend(FilteringExtension)
        self.dataset.decorate_properties(filter_decorator)
        self.dataset.add_observer("data_loaded", self.on_data_loaded)

        self.intensity_threshold = 0  # Initialize intensity threshold for the widget
        self.output_widget = wg.Output()
        self.last_filters = None  # Store last used filters
        self.last_displayed_df = None  # Store last displayed DataFrame

        # Set up the filtering widget layout
        self.create_widgets()
        self.create_layout()
        self.display_layout()
        self.setup_event_handlers()

        # Populate widgets with data if data is already loaded
        if self.dataset.data_loaded:
            self.on_data_loaded({"new": True})  # Simulate a change event

    def create_widgets(self) -> None:
        """Create widgets"""

        self.wbx_checkbox_bypass_widgets = wg.Checkbox(
            value=False,
            description="Bypass Filters",
            disabled=False,
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_button_apply_filters = wg.Button(
            description="Apply Filters",
            disabled=False,
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_checkbox_show_df = wg.Checkbox(
            value=False,
            description="Show filtered dataframe",
            disabled=False,
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_dropdown_select_df = wg.Dropdown(
            options=[],
            value=None,
            description="Select Data:",
            disabled=False,
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        # Filtering widgets
        self.wbx_timestart = wg.NaiveDatetimePicker(
            description="Pick a Start time",
            value=None,
            disabled=False,
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_timeend = wg.NaiveDatetimePicker(
            description="Pick an End Time",
            value=None,
            disabled=False,
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_mzrange = wg.IntRangeSlider(
            value=[0, 1000],
            min=0,
            max=1000,
            description="Select mz-range:",
            disabled=False,
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_intensity_threshold_percentage = wg.IntText(
            value=25,
            description="Percentile of smallest intensities to filter out:",
            disabled=False,
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_cumsum_threshold = wg.FloatText(
            value=100,
            description="Percentile of tic to show:",
            disabled=False,
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_samples = wg.SelectMultiple(
            options=[],
            value=[],
            description="Select samples for the analysis",
            disabled=False,
            rows=10,
            style={"description_width": "initial"},
            layout=wg.Layout(width="98%"),
        )
        self.wbx_mass_input = wg.Text(
            value="",
            placeholder="Enter unit masses (integers) to be excluded, separated by commas",
            description="Unit masses:",
            disabled=False,
            style={"description_width": "initial"},
            layout=wg.Layout(width="98%"),
        )
        # Labels for the widgets
        self.wbx_intensity_threshold_label = wg.Label(value="N/A")
        self.wbx_cumsum_threshold_label = wg.Label(
            value=(
                f"Showing highest peaks constituting {self.wbx_cumsum_threshold.value}"
                " percentage of tic (data filtered possible also by mz and intensity)."
            )
        )

    def create_layout(self) -> None:
        """Group all filtering widgets together"""

        self.group = wg.VBox(
            [
                self.wbx_checkbox_bypass_widgets,
                wg.HBox(
                    [
                        wg.VBox(
                            [
                                wg.HBox(
                                    [
                                        self.wbx_timestart,
                                        self.wbx_timeend,
                                    ]
                                ),
                                wg.HBox(
                                    [
                                        self.wbx_intensity_threshold_percentage,
                                        self.wbx_intensity_threshold_label,
                                    ]
                                ),
                                wg.HBox(
                                    [
                                        self.wbx_cumsum_threshold,
                                        self.wbx_cumsum_threshold_label,
                                    ]
                                ),
                                self.wbx_mzrange,
                                self.wbx_checkbox_show_df,
                                self.wbx_dropdown_select_df,
                            ],
                        ),
                        wg.VBox(
                            [self.wbx_samples, self.wbx_mass_input],
                        ),
                    ],
                    **DEFAULT_BOX_PROPERTIES,
                ),
                self.wbx_button_apply_filters,
            ],
        )

    def display_layout(self) -> None:
        """Displays the widget layout."""

        display(self.group)
        display(self.output_widget)

    def setup_event_handlers(self) -> None:
        """Attach observers to widgets"""

        # Attach observers to widgets connected to labels
        widgets = [
            self.wbx_intensity_threshold_percentage,
            self.wbx_cumsum_threshold,
        ]
        for widget in widgets:
            widget.observe(self.update_labels, names="value")
        # Attach observer to the button
        self.wbx_button_apply_filters.on_click(self.update_filters)
        # Observe changes in the enable/disable checkbox
        self.wbx_checkbox_bypass_widgets.observe(
            self.toggle_widgets_state, names="value"
        )
        # Separate observers for UI updates of shown DataFrame
        self.wbx_dropdown_select_df.observe(self.update_display, names="value")
        self.wbx_checkbox_show_df.observe(self.update_display, names="value")

    def update_dropdown_options(self) -> None:
        """
        Update the options in the dropdown to reflect
        the current valid DataFrames in the dataset.
        """
        try:
            logger.debug("Updating dropdown options for DataFrame selection.")
            df_names = [
                "match_samples",
                "match_compounds",
                "match_isotopes",
                "match_ions",
                "match_data",
            ]
            if (
                self.dataset.data_source.sample_batch_multiselect.import_peaks_checkbox.value
            ):
                df_names.append("peaks_matched")
            # Update the dropdown options with valid DataFrame names
            self.wbx_dropdown_select_df.options = df_names
            if df_names:
                self.wbx_dropdown_select_df.value = df_names[0]
                logger.debug(f"Dropdown options updated: {df_names}")
            else:
                self.wbx_dropdown_select_df.value = None
                logger.warning("No valid DataFrames available for selection.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "update_dropdown_options",
                e,
            )

    def is_valid_dataframe(self, name: str) -> bool:
        """
        Check if the given property of the dataset is a valid DataFrame.

        :param name: The name of the property to check.
        :type name: str
        :return: True if the property is a valid DataFrame, False otherwise.
        :rtype: bool
        """
        # Access the dataset's attributes directly using __dict__
        value = self.dataset.__dict__.get(name, None)
        return isinstance(value, pd.DataFrame)

    def update_filters(self, change=None) -> None:  # pylint: disable=unused-argument
        """Update filters according to user selections in widgets
        and apply them to the dataset.

        This method is called when the user clicks the "Apply Filters" button.
        It collects the values from the widgets, constructs a filter dictionary,
        and applies the filters to the dataset.
        It also updates the displayed DataFrame if the checkbox is checked.
        If the filters haven't changed, it skips the update.

        :param change: The change event dictionary.
        :type change: dict
        """
        try:
            if (
                not self.wbx_checkbox_bypass_widgets.value
            ):  # Activate the filtering if not bypassed
                logger.debug("Updating filters based on user selections.")
                selected_ids = self.wbx_samples.value
                new_filters = {
                    "samples": selected_ids,
                    "mz_range": self.wbx_mzrange.value,
                    "intensity_threshold": self.wbx_intensity_threshold_percentage.value,
                    "cumsum_threshold": self.wbx_cumsum_threshold.value,
                    "time_range": [self.wbx_timestart.value, self.wbx_timeend.value],
                    "exclude_masses": self.parse_masses(self.wbx_mass_input.value),
                }
                # No need to filter if the values didn't change
                if new_filters == self.last_filters:
                    logger.debug("No changes in filters. Skipping update.")
                    return
                self.last_filters = new_filters  # Store latest filters
                logger.debug(f"Applying filters: {new_filters}")
                self.dataset.set_filters(**new_filters)  # Apply filters
                self.update_dropdown_options()
                if self.wbx_checkbox_show_df.value:  # Update the displayed DataFrame
                    selected_df_name = self.wbx_dropdown_select_df.value
                    selected_df = self.dataset.__dict__.get(selected_df_name, None)
                    self.display_dataframe(selected_df)
        except (
            AttributeError,
            ValueError,
            TypeError,
        ) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "update_filters",
                e,
            )

    def update_labels(self, change=None) -> None:  # pylint: disable=unused-argument
        """Update labels according to user selections in widgets

        This method is called when the user changes the values in the widgets.
        It updates the labels for the intensity threshold and cumsum threshold
        based on the current values of the corresponding widgets.

        :param change: The change event dictionary.
        :type change: dict
        """

        # Update the intensity threshold label
        new_intensity_threshold = self.collect_and_calculate_intensity_threshold()
        if new_intensity_threshold != self.intensity_threshold:
            self.intensity_threshold = new_intensity_threshold
            self.wbx_intensity_threshold_label.value = f"{self.intensity_threshold}"
        # Update the cumsum threshold label
        new_cumsum_text = (
            f"Showing highest peaks constituting {self.wbx_cumsum_threshold.value} "
            "percentage of TIC."
        )
        if new_cumsum_text != self.wbx_cumsum_threshold_label.value:
            self.wbx_cumsum_threshold_label.value = new_cumsum_text

    def toggle_widgets_state(self, change) -> None:  # pylint: disable=unused-argument
        """Toggle the state of widgets based on checkbox.

        This method is called when the user checks or unchecks the bypass checkbox.
        It enables or disables the filtering widgets based on the checkbox state.

        :param change: The change event dictionary.
        :type change: dict
        """

        # If bypass checked, disable widgets
        for widget in [
            self.wbx_dropdown_select_df,
            self.wbx_checkbox_show_df,
            self.wbx_timestart,
            self.wbx_timeend,
            self.wbx_intensity_threshold_percentage,
            self.wbx_cumsum_threshold,
            self.wbx_mzrange,
            self.wbx_samples,
            self.wbx_mass_input,
            self.wbx_button_apply_filters,
        ]:
            widget.disabled = change["new"]
        # Activate the filtering if the checkbox is not checked
        self.dataset.set_trait(
            "apply_filters", not self.wbx_checkbox_bypass_widgets.value
        )

    def collect_and_calculate_intensity_threshold(self) -> float:
        """
        Collect and calculate the intensity threshold
        from the dataset and set it to the widget by using percentage
        given in corresponding ipywidget IntText.

        To access un-filtered intensity values, need to access protected peaks DataFrame '_peaks'.
        If peaks DataFrame is not accessible, protected '_match_isotopes' DataFrame is used
        to get un-filtered intensity values.

        :return: The calculated intensity threshold.
        :rtype: float
        """

        try:
            intensity_values = (
                self.dataset.data_source._peaks.intensity  # pylint: disable=protected-access
            )
        except KeyError:
            intensity_values = (
                self.dataset.data_source._match_isotopes.sample_peak_intensity  # pylint: disable=protected-access
            )
        intensity_threshold = np.round(
            np.percentile(
                intensity_values,
                self.wbx_intensity_threshold_percentage.value,
            ),
            3,
        )

        return intensity_threshold

    def get_mz_range_from_dataset(self) -> tuple:
        """
        Get the minimum and maximum mz values
        from all DataFrame properties of the dataset.

        If peaks are imported protected '_peaks' DataFrame is used to get the un-filtered mz values.
        If not, the protected '_match_isotopes' DataFrame is used to get un-filtered mz values.

        :return: A tuple containing the minimum and maximum mz values.
        :rtype: tuple
        """
        mz_min, mz_max = float("inf"), float("-inf")
        if (
            self.dataset.data_source.sample_batch_multiselect.import_peaks_checkbox.value
        ):
            if isinstance(
                self.dataset.data_source._peaks,  # pylint: disable=protected-access
                pd.DataFrame,
            ):
                peaks_df = (
                    self.dataset.data_source._peaks  # pylint: disable=protected-access
                )
                mz_min = min(mz_min, peaks_df["mz"].min())
                mz_max = max(mz_max, peaks_df["mz"].max())
            else:
                isotopes_df = (
                    self.dataset.data_source._match_isotopes  # pylint: disable=protected-access
                )
                if "mz" in isotopes_df.columns:
                    mz_min = min(mz_min, isotopes_df["mz"].min())
                    mz_max = max(mz_max, isotopes_df["mz"].max())
                if "sample_peak_mz" in isotopes_df.columns:
                    mz_min = min(mz_min, isotopes_df["sample_peak_mz"].min())
                    mz_max = max(mz_max, isotopes_df["sample_peak_mz"].max())
        if mz_min > mz_max:
            logger.warning(
                f"Invalid mz range detected (mz_min: {mz_min}, mz_max: {mz_max}). "
                "Returning default range (0, 0)."
            )
            return 0, 0

        return mz_min, mz_max

    def parse_masses(self, mass_input: str) -> list:
        """
        Parse the input text and convert it into a list of floats.

        This method takes a string input, splits it by commas,
        and converts each part into a float. It ignores any empty
        or invalid entries. If the input is not a string, it returns an empty list.
        The method also handles any exceptions that may occur during parsing
        and logs a warning message.

        :param mass_input: text input containing comma seperated mz-values from widget
        :type mass_input: str
        :return: List of mz-values OR an empty list if the input is invalid
        :rtype: list
        """
        try:
            masses = []
            for mass in mass_input.split(","):
                mass = mass.strip()
                if not mass:
                    continue
                try:
                    masses.append(int(mass))
                except ValueError:
                    logger.debug(
                        f"Warning: '{mass}' is not an integer and will be ignored."
                    )
            return masses
        except AttributeError:
            logger.warning(
                f"Error: The input '{mass_input}' is not a valid string. "
                "Please enter a comma-separated list of integers."
            )
            return []

    def update_display(self, change=None) -> None:  # pylint: disable=unused-argument
        """Update DataFrame display only if necessary.

        This method is called when the user checks or unchecks the checkbox
        to show the DataFrame or when the selected DataFrame changes.
        It checks if the DataFrame has changed since the last display
        and updates the display accordingly.

        :param change: The change event dictionary.
        :type change: dict
        """
        if self.wbx_checkbox_show_df.value:
            selected_df_name = self.wbx_dropdown_select_df.value
            selected_df = self.dataset.__dict__.get(selected_df_name, None)
            if selected_df is not None and not selected_df.equals(
                self.last_displayed_df
            ):
                self.display_dataframe(selected_df)
                self.last_displayed_df = (
                    selected_df.copy()
                )  # Store the last displayed DataFrame

    def display_dataframe(self, df: pd.DataFrame) -> None:
        """
        Display the given DataFrame in the output widget.

        This method uses the ipyaggrid library to create a grid
        representation of the DataFrame and displays it in the output widget.
        It clears the previous output before displaying the new DataFrame.
        If the DataFrame is not valid, it logs a warning message.

        :param df: Any dataset dataframe
        :type df: pd.DataFrame
        """
        with self.output_widget:
            self.output_widget.clear_output()
            if isinstance(df, pd.DataFrame):
                grid = Grid(
                    grid_data=df,
                    grid_options=copy.deepcopy(GRID_OPTIONS),
                    height=600,
                )
                display(grid)
            else:
                logger.warning("No valid DataFrame to display.")

    def on_apply_filters(self, change):  # pylint: disable=unused-argument
        """
        Observer for apply_filters trait.
        Called automatically when apply_filters is changed.
         - Clear the cache of the dataset.

        :param change: The change event dictionary.
        :type change: dict
        """
        try:
            logger.info("Apply filters triggered. Clearing dataset cache.")
            self.dataset.clear_cache()
            logger.info("Dataset cache cleared successfully.")
        except (
            AttributeError,
            ValueError,
            TypeError,
        ) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "on_apply_filters",
                e,
            )

    def on_data_loaded(self, change) -> None:
        """
        Callback for when `data_loaded` changes.
        React to data being cleared or loaded.
         - If new data is loaded, populate filtering widgets.
         - If data is cleared, reset filtering widgets to default state.

        :param change: The change event dictionary.
        :type change: dict
        """
        try:
            if change["new"]:  # If data_loaded is True
                logger.info("Data loaded. Populating filtering widgets.")
                self.dataset.add_observer("apply_filters", self.on_apply_filters)
                self.populate_widgets_with_data()
                logger.info("Filtering widgets populated successfully.")
            else:
                logger.info(
                    "Data cleared. Resetting filtering widgets to default state."
                )
                self.reset_widgets_to_defaults()
                logger.info("Filtering widgets reset to defaults successfully.")
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

        This method retrieves the necessary data from the dataset
        and updates the widgets accordingly. It sets the time range,
        mz range, sample names, and intensity threshold based on the dataset.
        It also updates the dropdown options for DataFrame selection.
        If any error occurs during the process, it logs an error message.
        """
        try:
            logger.debug("Populating widgets with data from the dataset.")
            logger.debug("Updating dropdown options for DataFrame selection.")
            self.update_dropdown_options()
            logger.debug("Dropdown options updated successfully.")
            logger.debug("Setting time range widgets (start and end).")
            self.wbx_timestart.value = min(
                self.dataset.match_samples.datetime.dt.tz_localize(None)
            )
            logger.debug(f"Start time set to: {self.wbx_timestart.value}")
            self.wbx_timeend.value = max(
                self.dataset.match_samples.datetime.dt.tz_localize(None)
            )
            logger.debug(f"End time set to: {self.wbx_timeend.value}")
            logger.debug("Calculating mz range from the dataset.")
            mz_min, mz_max = self.get_mz_range_from_dataset()
            logger.debug(f"mz range calculated: min={mz_min}, max={mz_max}")
            self.wbx_mzrange.max = mz_max
            self.wbx_mzrange.min = mz_min
            self.wbx_mzrange.value = [mz_min, mz_max]
            logger.debug(f"mz range widget updated: {self.wbx_mzrange.value}")
            # Get unique sample names from protected _match_samples
            #  df which contains always un-filtered data
            logger.debug("Fetching unique sample names from the dataset.")
            samples_df = (
                self.dataset.data_source._match_samples  # pylint: disable=protected-access
            )
            sample_options = [
                (row.sample_item_name_datetime, row.sample_item_id)
                for _, row in samples_df.iterrows()
            ]
            self.wbx_samples.options = sample_options
            # Set default value to all samples
            self.wbx_samples.value = [opt[1] for opt in sample_options]
            logger.debug("Sample selection widget updated.")
            logger.debug("Calculating intensity threshold.")
            self.intensity_threshold = self.collect_and_calculate_intensity_threshold()
            logger.debug(f"Intensity threshold calculated: {self.intensity_threshold}")
            self.wbx_intensity_threshold_label.value = f"{self.intensity_threshold}"
            logger.debug("Intensity threshold widget updated.")
            logger.debug("Widgets populated successfully.")
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

    def reset_widgets_to_defaults(self) -> None:
        """
        Reset widgets to their default or placeholder values
        when `data_loaded` is False.

        This method clears the values of the filtering widgets,
        including time range, mz range, sample names, and intensity threshold.
        It also clears the displayed DataFrame and resets the last filters.
        """
        try:
            logger.debug("Resetting widgets to default values.")
            self.wbx_timestart.value = None
            self.wbx_timeend.value = None
            self.wbx_mzrange.min = 0
            self.wbx_mzrange.max = 100
            self.wbx_mzrange.value = [0, 100]
            self.wbx_samples.options = []
            self.wbx_samples.value = []
            self.intensity_threshold = 0
            self.wbx_intensity_threshold_label.value = "N/A"
            logger.debug("Widgets reset to default values successfully.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error("Error in reset_widgets_to_defaults: %s", e)
