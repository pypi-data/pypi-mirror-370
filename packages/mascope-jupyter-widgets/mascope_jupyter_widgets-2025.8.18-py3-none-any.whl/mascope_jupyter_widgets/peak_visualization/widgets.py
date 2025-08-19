from __future__ import annotations
import warnings
import pandas as pd
import ipywidgets as wg

from IPython.display import display

from .extension import PeakVisualizationExtension
from .plots import PeakVisualizationPlotter
from ..mascope_data.wrapper import MascopeDataWrapper
from ..logging_config import logger  # Import the shared logger
from ..widgets_config import DEFAULT_WIDGETS_PROPERTIES
from ..plot_tools import extract_figure_data

warnings.filterwarnings(
    "ignore", category=FutureWarning, module="pandas"
)  # TODO, Think later groupby deprecation warning


class PeakVisualizationWidget:
    """
    This class provides a Jupyter widget for visualizing multiple spectra
    and sample timeseries from a MascopeDataWrapper dataset.
    """

    def __init__(self, dataset: MascopeDataWrapper):

        self.dataset = dataset
        self.dataset.extend(PeakVisualizationExtension)
        self.plotter = PeakVisualizationPlotter(self.dataset)
        self.default_dmz = 0.01
        self.debounce_timer_formula = None
        self._mz_dmz_widgets = None
        self._fig = None

        # Setup widget-selector and display
        self.create_widgets()
        self.create_layout()
        self.create_figure_output()
        self.display_layout()

        self.dataset.add_observer("data_loaded", self.on_data_loaded)

        # Populate widgets with data if data is already loaded
        if self.dataset.data_loaded:
            self.on_data_loaded({"new": True})  # Simulate a change event

    @property
    def figure_data(self) -> pd.DataFrame:
        """
        Get the multifig figure data as a pandas DataFrame.

        - This method returns copy of the displayed data as a pandas DataFrame
        to prevent unintended modifications to the original data.
        - It extracts the x-axis, y-axis, name and customdata (hoverbox)
          columns from the figure data.
        - The x-axis is universally named "x" to accommodate various x-axis types
          (e.g., Time, m/z, hour_of_day).


        :return: The displayed data as a pandas DataFrame.
        :rtype: pd.DataFrame
        """

        return extract_figure_data(
            self._fig,
            x_col="x",  # Universal x-axis name because can be many e.g. Time, mz, hour_of_day
            y_col="intensity",
            name_col="name",
        )

    def create_widgets(self) -> None:
        """
        Create the necessary widgets for the PeakVisualizationWidget.
        This includes m/z sliders, a button to plot spectra, and a button to plot sample timeseries.
        """
        # Widgets (empty/disabled initially)
        self.wbx_formula_box = wg.Text(
            description="Formula:", disabled=True, **DEFAULT_WIDGETS_PROPERTIES
        )
        self.wbx_isotope_abundance_threshold = wg.FloatText(
            description="Isotope abundance threshold (fraction):",
            value=0.001,
            disabled=True,
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_mz_tol_box = wg.FloatText(
            description="m/z tol (ppm):",
            value=3.0,
            disabled=True,
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_sample_selector = wg.SelectMultiple(
            description="Samples:",
            options=[],
            disabled=True,
            row=7,
            layout=wg.Layout(width="95%"),
        )
        self.wbx_use_first_dmz = wg.Checkbox(
            value=False,
            description="Use first Δm/z for all",
            indent=False,
            layout=wg.Layout(width="95%"),
        )
        dmz_title = wg.HTML("<b>Δm/z for each target isotopes:</b>")
        self.wbx_dmz_boxes = wg.VBox([])
        self.wbx_dmz_section = wg.VBox([dmz_title, self.wbx_dmz_boxes])

        self.wbx_search_mz_button = wg.Button(description="Search mzs", disabled=True)
        self.wbx_plot_button = wg.Button(description="Plot", disabled=True)
        self.multifig_output = wg.Output()

    def create_layout(self) -> None:
        """
        Create the layout for the PeakVisualizationWidget.
        """
        self.group = wg.VBox(
            [
                wg.VBox(
                    [
                        wg.HBox(
                            [
                                wg.VBox(
                                    [
                                        self.wbx_formula_box,
                                        self.wbx_isotope_abundance_threshold,
                                        self.wbx_search_mz_button,
                                        self.wbx_mz_tol_box,
                                        self.wbx_sample_selector,
                                        self.wbx_use_first_dmz,
                                    ],
                                    layout=wg.Layout(width="auto"),
                                ),
                                self.wbx_dmz_section,
                            ],
                            layout=wg.Layout(width="100%"),
                        ),
                        self.wbx_plot_button,
                    ],
                    layout=wg.Layout(width="auto"),
                ),
                self.multifig_output,
            ],
        )

    def setup_event_handlers(self) -> None:
        """
        Set up event handlers for the PeakVisualizationWidget.

        This method connects the widget events to their respective handlers.
        It includes:
        - Button click handlers for searching m/z values and plotting spectra.
        - Button click handlers for plotting sample timeseries.
        """

        # Button handlers
        self.wbx_search_mz_button.on_click(self.on_search_mz_clicked)
        self.wbx_plot_button.on_click(self.on_plot_clicked)
        # Checkbox handler for using first dmz
        self.wbx_use_first_dmz.observe(self.on_use_first_dmz_changed, names="value")

    def on_use_first_dmz_changed(self, change: dict) -> None:
        use_first = change["new"]
        # Skip if no dmz widgets yet
        if not self._mz_dmz_widgets:
            return
        # Enable only the first, disable the rest if checked
        for idx, (cb, ft, mz, label, rel_ab) in enumerate(self._mz_dmz_widgets):
            if idx == 0:
                ft.disabled = False
            else:
                ft.disabled = use_first

    def create_figure_output(self) -> None:
        """
        Create the figure output for the PeakVisualizationWidget.

        This method initializes the figure output area where the plots will be displayed.
        It builds the base plot using the PeakVisualizationPlotter and displays it
        in the multifig_output area. The figure is created with no data initially,
        allowing it to be populated later when the user interacts with the widgets.
        It also ensures that the output area is cleared before displaying the new figure.
        """

        self._fig = self.plotter.build_base_plot()
        with self.multifig_output:
            self.multifig_output.clear_output()
            display(self._fig)

    def display_layout(self) -> None:
        """Displays the widget layout."""
        display(self.group)

    def on_data_loaded(self, change: dict) -> None:
        """
        Callback method to handle data loaded events.
        This method is called when the `data_loaded` attribute of the dataset changes.
        It populates the widgets with data, sets up event handlers, and creates the figure output.
        If the data is cleared, it resets the widgets to their default state.

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
                self.setup_event_handlers()
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

    def on_clear_cache(
        self, change: dict = None  # pylint: disable=unused-argument
    ) -> None:
        """
        Callback for when `memory_cleared` changes.
        This method is called when the dataset's memory is cleared.
        It resets the widget selectors, clears the output, and repopulates the widgets
        with data from the dataset. It also recreates the figure output.

        :param change: The change event dictionary.
        :type change: dict
        """

        try:
            logger.info(
                "Cache cleared. Resetting widget selector and output for "
                "multi-figure module."
            )
            self._reset_selectors()
            logger.debug("Output cleared.")
            # Update the available peaks in the peak selector
            logger.info("Multifig reset successfully.")
            self.populate_widgets_with_data()
            logger.info(
                "Multifig module widgets populated successfully after cache clear."
            )
            self.create_figure_output()
            logger.debug("Multifig module" " figure output recreated.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "on_clear_cache",
                e,
            )

    def on_search_mz_clicked(
        self, change: dict  # pylint: disable=unused-argument
    ) -> None:
        """
        Callback for when the search button is clicked.

        This method retrieves the m/z values for the selected formula
        and updates the dmz boxes with the theoretical m/z values and their labels.
        It is called when the user clicks the "Search mzs" button.

        :param change: The change event dictionary.
        :type change: dict
        """
        self.wbx_plot_button.disabled = (
            True  # Disable plot button until dmz boxes are updated
        )
        try:
            logger.info("Search mzs button clicked, updating dmz boxes.")
            # Strip whitespace and newlines from formula
            formula = self.wbx_formula_box.value.strip()
            if not formula:
                logger.warning("Formula input is empty after stripping whitespace.")
                self.wbx_dmz_boxes.children = []
                return
            # Check if the formula is a float value and handle it
            if self._is_float_value(formula):
                mz = float(formula)
                cb = wg.Checkbox(value=True, description="", indent=False)
                ft = wg.FloatText(
                    description=f"{mz:.4f}",
                    value=0.01,
                    tooltip=f"{mz:.4f}",
                    layout=wg.Layout(width="95%"),
                    style={"description_width": "initial"},
                )
                row = wg.HBox([ft, cb])
                self._mz_dmz_widgets = [(cb, ft, mz, "", 1.0)]
                self.wbx_dmz_boxes.children = [row]
                self.wbx_plot_button.disabled = False
                logger.info("Single m/z float value detected, dmz box updated.")
                return
            # Get mz/label pairs for the formula
            isotopocules_theoretical_df = self.dataset.get_mz_list_for_target_formula(
                formula=formula,
                isotope_abundance_threshold=self.wbx_isotope_abundance_threshold.value,
            )
            if isotopocules_theoretical_df.empty:
                logger.warning(f"No m/z values found for formula '{formula}'.")
                self.wbx_dmz_boxes.children = []
                return
            logger.debug(
                f"Found {len(isotopocules_theoretical_df)} m/z values for formula '{formula}'."
            )
            self._mz_dmz_widgets = (
                []
            )  # Store tuples of (checkbox, floattext, mz, label)
            self.wbx_dmz_boxes.children = []
            for mz, label, rel_ab in zip(
                isotopocules_theoretical_df["mz"],
                isotopocules_theoretical_df["label"],
                isotopocules_theoretical_df["relative_abundance"],
            ):
                cb = wg.Checkbox(value=True, description="", indent=False)
                ft = wg.FloatText(
                    description=f"{mz:.4f} {label} ({rel_ab:.2%})",
                    value=0.01,
                    tooltip=f"{mz:.4f} {label}",
                    layout=wg.Layout(width="95%"),
                    style={"description_width": "initial"},
                )
                row = wg.HBox([ft, cb])
                self._mz_dmz_widgets.append((cb, ft, mz, label, rel_ab))
                self.wbx_dmz_boxes.children += (row,)
            self.wbx_plot_button.disabled = False
            logger.info(
                f"Updated dmz boxes with {len(self.wbx_dmz_boxes.children)}"
                f" entries for formula '{formula}'."
            )
        except (AttributeError, ValueError, TypeError) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "on_search_mz_clicked",
                e,
            )

    def on_plot_clicked(self, change: dict) -> None:  # pylint: disable=unused-argument
        """
        Callback for when the plot button is clicked.

        - This method retrieves the selected m/z values and their corresponding
        dmz values from the checkboxes and float text widgets.
        - It then builds a multi-figure plot containing spectrum and
        sample timeseries figures using the selected samples and
        the specified m/z tolerance.
        - The plot is displayed in the output area.

        :param change: The change event dictionary.
        :type change: dict
        """

        # Gather values
        selected_samples = list(self.wbx_sample_selector.value)
        if selected_samples is None or not selected_samples:
            logger.warning("No samples selected for multifig plotting.")
            return
        mz_list = []
        dmz_list = []
        rel_ab_list = []
        label_list = []
        use_first_dmz = getattr(self, "wbx_use_first_dmz", None)
        use_first = use_first_dmz.value if use_first_dmz else False

        for idx, (cb, ft, mz, label, rel_ab) in enumerate(self._mz_dmz_widgets):
            if cb.value:
                logger.debug(
                    f"Selected m/z: {mz:.4f} with label '{label}' and dmz value {ft.value}"
                )
                if use_first and idx > 0:
                    # Use first's value for all if checkbox is checked
                    dmz_val = self._mz_dmz_widgets[0][1].value
                else:
                    dmz_val = ft.value
                mz_list.append(mz)
                dmz_list.append(dmz_val)
                rel_ab_list.append(rel_ab)
                label_list.append(label)
            else:
                logger.debug(
                    f"Skipped m/z: {mz:.4f} with label '{label}' (checkbox not selected)"
                )
        with self.multifig_output:
            self.multifig_output.clear_output()
            self._fig = self.plotter.build_multi_figure(
                mz_list=mz_list,
                dmz_list=dmz_list,
                selected_samples=selected_samples,
                rel_ab_list=rel_ab_list,
                label_list=label_list,
                peak_mz_tolerance_ppm=self.wbx_mz_tol_box.value,
            )
            display(self._fig)

    def populate_widgets_with_data(self) -> None:
        """
        Populate the widgets with data from the dataset.

        - This method enables the widgets, populates the sample selector
        with available samples, and sets up event handlers for the widgets.
        - It ensures that the widgets are ready for user interaction and
        that the data is displayed correctly.
        - It is called when the dataset is loaded or when the `data_loaded`
        attribute changes to True.
        """

        try:
            logger.debug("Populating multifig widgets with data from the dataset.")
            # Enable widgets and populate options
            self.wbx_formula_box.disabled = False
            self.wbx_isotope_abundance_threshold.disabled = False
            self.wbx_mz_tol_box.disabled = False
            self.wbx_sample_selector.options = [
                (f"{row.sample_item_name_datetime}", row.sample_item_id)
                for _, row in self.dataset.match_samples.iterrows()
            ]
            logger.debug(
                "Sample item ID dropdown populated using "
                "(sample_item_name_datetime, sample_item_id)."
            )
            self.wbx_sample_selector.disabled = False
            self.wbx_plot_button.disabled = False
            self.wbx_search_mz_button.disabled = False
            logger.debug("Widgets enabled and populated with options.")
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

        This method resets the widget selectors to their default state,
        clears the output, and recreates the figure output. It is called
        when the dataset is cleared or when the `data_loaded` attribute
        changes to False. It ensures that the widget is in a clean state
        for new data and that the user can start fresh without any previous
        selections or data lingering in the widgets.
        """

        try:
            logger.debug("Resetting multifig widgets to default state.")
            self._reset_selectors()
            logger.debug("Output cleared.")

            self.create_figure_output()
            logger.debug("Multifig figure output recreated.")

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

        This method clears the sample selector, resets the formula box,
        and disables the m/z tolerance and isotope abundance threshold boxes.
        It also clears the dmz boxes and disables the search m/z button.
        It is called when the dataset is cleared or when the data is loaded
        to ensure that the widget is in a clean state for new data.
        """
        self.wbx_formula_box.value = ""
        self.wbx_formula_box.disabled = True

        self.wbx_mz_tol_box.value = 3.0
        self.wbx_mz_tol_box.disabled = True

        self.wbx_isotope_abundance_threshold.value = 0.001
        self.wbx_isotope_abundance_threshold.disabled = True

        self.wbx_sample_selector.options = []
        self.wbx_sample_selector.value = ()
        self.wbx_sample_selector.disabled = True

        self.wbx_dmz_boxes.children = []

        self.wbx_search_mz_button.disabled = True

    def _is_float_value(self, value: str) -> bool:
        """
        Check if the given value can be converted to a float.

        This helper method attempts to convert the input value to a float.
        If the conversion is successful, it returns True; otherwise, it returns False.

        :param value: The value to check.
        :type value: str
        :return: True if the value can be converted to a float, False otherwise.
        :rtype: bool
        """
        try:
            float(value)
            return True
        except ValueError:
            return False
