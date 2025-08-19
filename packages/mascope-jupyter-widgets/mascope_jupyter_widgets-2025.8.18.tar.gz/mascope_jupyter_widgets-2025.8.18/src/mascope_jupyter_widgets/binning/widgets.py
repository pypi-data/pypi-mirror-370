import warnings
import ipywidgets as wg
import numpy as np
from IPython.display import display

from .extension import BinningExtension
from .plots import BinningPlotter
from .plots_utils import calculate_outliers

from ..widgets_config import (
    DEFAULT_WIDGETS_PROPERTIES,
    DEFAULT_BOX_PROPERTIES,
)
from ..mascope_data.wrapper import MascopeDataWrapper
from ..logging_config import logger  # Import the shared logger

warnings.filterwarnings(
    "ignore", message="Precision loss occurred in moment calculation"
)
BINNING_METHOD_OPTIONS = ["Basic", "Dynamic"]
DYNAMIC_BINNING_ALGO_OPTIONS = ["log", "sqrt", "log_alpha", "exp"]
AGG_FUNCTION_OPTIONS = [
    "sum",
    "mean",
    "min",
    "max",
    "median",
    "std",
    "var",
    "count",
    "first",
    "last",
    "prod",
]


class BinningWidget:
    """Handles widgets related to binning method selection."""

    def __init__(
        self,
        dataset: MascopeDataWrapper,
    ):
        """
        Set up interactive widget-selector
        for binning method selection.

        :param dataset: MascopeDataWrapper -dataset
        :type dataset: MascopeDataWrapper
        """
        # Initialize and extend the dataset
        self.dataset = dataset
        self.dataset.extend(BinningExtension)
        self.binning_plots = BinningPlotter(dataset=self.dataset)
        # Set output layout components
        self.output_widgets = {
            "heatmap": wg.Output(),
            "binning_count": wg.Output(),
            "histogram": wg.Output(),
            "top_n_alignment": wg.Output(),
            "mascope_targets": wg.Output(),
            "sparsity_density": wg.Output(),
            "zscore_analysis": wg.Output(),
            "random_spec_check": wg.Output(),
        }
        self.tabs = wg.Tab()  # Initialize tabs for the main categories
        self.group = wg.VBox()  # Initialize group for the binning widgets

        self.dataset.add_observer("data_loaded", self.on_data_loaded)

        # Set up the widget layout and event handlers
        self.create_widgets()
        self.update_binning_parameters()
        self.create_tabs()
        self.create_layout()
        self.setup_event_handlers()
        self.display_layout()

        # Populate widgets with data if data is already loaded
        if self.dataset.data_loaded:
            self.on_data_loaded({"new": True})  # Simulate a change event

    def create_widgets(self) -> None:
        """Create widgets specific to binning"""

        self.wbx_binning_method = wg.Dropdown(
            options=BINNING_METHOD_OPTIONS,
            value="Basic",
            description="Select binning method: ",
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_dyn_binning_algo = wg.Dropdown(
            options=DYNAMIC_BINNING_ALGO_OPTIONS,
            description="Dynamic binning algorithm:",
            disabled=True,
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_rtol = wg.FloatText(
            value=3,
            description="Select ppm-error (rtol): ",
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_scale_factor = wg.FloatText(
            value=1,
            description="Select scale factor for Dynamic binning:",
            disabled=True,
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_alpha_value = wg.FloatText(
            value=1,
            description="Select Alpha value:",
            disabled=True,
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_aggfunction = wg.Dropdown(
            options=AGG_FUNCTION_OPTIONS,
            value="max",
            description="Select aggregation function:",
            **DEFAULT_WIDGETS_PROPERTIES,
        )  # Aggreagation function for the pivoting process
        self.update_button = wg.Button(
            description="Update Binning",
            button_style="primary",
            tooltip="Click to update binning parameters and refresh plots",
            icon="refresh",
        )

    def create_tabs(self) -> None:
        """
        Create the main tabs for the widget.

        This method initializes the main tabs for the widget, including
        placeholders for figures that will be dynamically populated later.
        """
        # Create tabs for main categories
        tabs = wg.Tab()
        # Create sub-tabs or accordions for each sub-category
        top_features_tab = self.create_empty_tab()
        sparsity_density_tab = self.create_empty_tab()
        zscore_tab = self.create_empty_tab()
        random_spec_check_tab = self.create_empty_tab()

        tabs.children = [
            top_features_tab,
            sparsity_density_tab,
            zscore_tab,
            random_spec_check_tab,
        ]
        tabs.set_title(0, "Top Features")
        tabs.set_title(1, "Sparsity & Density")
        tabs.set_title(2, "Z-Score Analysis")
        tabs.set_title(3, "Random Spectrum Check")

        self.tabs = tabs

    def create_empty_tab(self) -> None:
        """
        Create an empty tab as a placeholder.

        :return: An empty VBox widget.
        :rtype: wg.VBox
        """
        return wg.VBox([wg.Label("Content will be loaded when the tab is opened.")])

    def create_layout(self) -> None:
        """Create layout for the widget."""

        # Create a group for the binning widgets
        self.group = wg.VBox(
            [
                wg.VBox(
                    [
                        wg.HBox(
                            [
                                self.wbx_binning_method,
                                self.wbx_dyn_binning_algo,
                                self.wbx_aggfunction,
                            ]
                        ),
                        self.wbx_rtol,
                        self.wbx_scale_factor,
                        self.wbx_alpha_value,
                    ],
                    **DEFAULT_BOX_PROPERTIES,
                ),
                self.update_button,
            ]
        )
        # Create accordion for the figure tabs
        self.figure_accordion = wg.Accordion(
            children=[self.tabs],
            selected_index=None,
        )
        # Set titles for each section
        self.figure_accordion.set_title(0, "Analysis figures")

    def populate_tabs(self) -> None:
        """
        Populate the tabs with figures.

        This method is called when the accordion is opened
        or when the data is loaded. It generates and displays
        the figures in the respective tabs based on the current dataset.
        It also handles any exceptions that may occur during the process.
        """
        try:
            if self.dataset.data_loaded:  # Only populate if data is loaded
                logger.debug("Populating tabs with figures.")
                self.tabs.children[0].children = [self.figure_tab_top_features()]
                logger.debug("Top Features tab populated.")
                self.tabs.children[1].children = [self.figure_tab_sparsity_density()]
                logger.debug("Sparsity & Density tab populated.")
                self.tabs.children[2].children = [self.figure_tab_zscore_outliers()]
                logger.debug("Z-Score Analysis tab populated.")
                self.tabs.children[3].children = [self.figure_tab_random_spec_check()]
                logger.debug("Random Spectrum Check tab populated.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error("Error in populate_tabs: %s", e)

    def display_layout(self) -> None:
        """Displays the widget layout."""

        display(self.group)
        display(self.figure_accordion)

    def setup_event_handlers(self) -> None:
        """Setup event handler for interactivity"""

        # Observe changes in all relevant widgets
        self.wbx_binning_method.observe(self.update_widget_states, names="value")
        self.wbx_dyn_binning_algo.observe(self.update_widget_states, names="value")
        self.wbx_rtol.observe(self.update_widget_states, names="value")
        self.wbx_scale_factor.observe(self.update_widget_states, names="value")
        self.wbx_alpha_value.observe(self.update_widget_states, names="value")
        self.wbx_aggfunction.observe(self.update_widget_states, names="value")
        # Observe changes in the accordion (to detect when it is opened)
        self.figure_accordion.observe(self.on_accordion_change, names="selected_index")
        # Attach the button click event handler
        self.update_button.on_click(self.update_binning_parameters)

    def on_accordion_change(self, change) -> None:
        """
        Update figures in the tabs when the accordion is opened.

        This method is called when the accordion is opened or closed.
        It checks if the accordion is opened and populates the tabs
        with the appropriate figures. If the accordion is closed,
        it does not populate the tabs.

        :param change: The change event from the accordion.
        :type change: dict
        """
        try:
            if change["new"] is not None and self.dataset.data_loaded:
                logger.info(f"Accordion section {change['new']} opened.")
                self.populate_tabs()
        except (AttributeError, ValueError, TypeError) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "on_accordion_change",
                e,
            )

    def update_widget_states(
        self, change=None  # pylint: disable=unused-argument
    ) -> None:
        """
        Update the enabled/disabled state of widgets based on the selected binning method
        and dynamic binning algorithm.

        This method is called whenever the value of the binning method
        or dynamic binning algorithm changes. It enables or disables
        the relevant widgets based on the current selection.

        :param change: The change event from the widget.
        :type change: dict
        """
        # Disable/enable widgets based on the selected binning method
        if self.wbx_binning_method.value == "Basic":
            self.wbx_rtol.disabled = False
            self.wbx_dyn_binning_algo.disabled = True
            self.wbx_scale_factor.disabled = True
            self.wbx_alpha_value.disabled = True
        elif self.wbx_binning_method.value == "Dynamic":
            self.wbx_rtol.disabled = False
            self.wbx_dyn_binning_algo.disabled = False
            self.wbx_scale_factor.disabled = False

            # Enable/disable alpha value based on the selected dynamic algorithm
            if self.wbx_dyn_binning_algo.value == "log_alpha":
                self.wbx_alpha_value.disabled = False
            else:
                self.wbx_alpha_value.disabled = True
        else:
            # Default: Disable all widgets (shouldn't happen unless an invalid value is set)
            self.wbx_rtol.disabled = True
            self.wbx_dyn_binning_algo.disabled = True
            self.wbx_scale_factor.disabled = True
            self.wbx_alpha_value.disabled = True

    def update_binning_parameters(
        self, change=None  # pylint: disable=unused-argument
    ) -> None:
        """
        Run the binning process based on
        the widget-selector values.

        This method is called when the update button is clicked.
        It retrieves the values from the widgets and updates
        the binning parameters in the dataset. It also handles
        any exceptions that may occur during the process.

        :param change: The change event from the button.
        :type change: dict
        """
        try:
            if self.wbx_binning_method.value == "Dynamic":
                self.dataset.set_binning_parameters(
                    binning_method="groupby_isclose_dynamic",
                    aggfunc=self.wbx_aggfunction.value,
                    base_rtol=self.wbx_rtol.value,
                    scale_factor=self.wbx_scale_factor.value,
                    method=self.wbx_dyn_binning_algo.value,
                    alpha=self.wbx_alpha_value.value,
                )
                logger.debug(
                    "Dynamic binning parameters set: "
                    f"aggfunc={self.wbx_aggfunction.value}, "
                    f"base_rtol={self.wbx_rtol.value}, "
                    f"scale_factor={self.wbx_scale_factor.value}, "
                    f"method={self.wbx_dyn_binning_algo.value}, "
                    f"alpha={self.wbx_alpha_value.value}"
                )
            elif self.wbx_binning_method.value == "Basic":
                self.dataset.set_binning_parameters(
                    binning_method="groupby_isclose",
                    aggfunc=self.wbx_aggfunction.value,
                    rtol=self.wbx_rtol.value,
                )
                logger.debug(
                    "Basic binning parameters set: "
                    f"aggfunc={self.wbx_aggfunction.value}, "
                    f"rtol={self.wbx_rtol.value}"
                )
            else:
                raise ValueError("Binning method not recognized.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error("Error in update_binning_parameters: %s", e)

    def figure_tab_top_features(self) -> wg.Tab:
        """
        Build the Top Features tab with sub-tabs for different plots.

        This tab includes a heatmap, matrix count, histogram,
        top N alignment, and mascope targets.
        Each plot is displayed in its own sub-tab.

        :return: wg.Tab - The tab containing the sub-tabs for top features.
        Each sub-tab contains a specific plot related to the dataset.
        :rtype: wg.Tab
        """
        sub_tabs = wg.Tab()

        # Add plots to sub-tabs
        sub_tabs.children = [
            self.output_widgets["heatmap"],
            self.output_widgets["binning_count"],
            self.output_widgets["histogram"],
            self.output_widgets["top_n_alignment"],
            self.output_widgets["mascope_targets"],
        ]
        sub_tabs.set_title(0, "Heatmap")
        sub_tabs.set_title(1, "Matrix Count")
        sub_tabs.set_title(2, "Histogram")
        sub_tabs.set_title(3, "Top N Alignment")
        sub_tabs.set_title(4, "Mascope Targets")

        # Generate plots
        with self.output_widgets["heatmap"]:
            self.output_widgets["heatmap"].clear_output()
            fig_heatmap, _ = self.binning_plots.plot_heatmap_mzfeatures(
                matrix=self.dataset.binning_intensity,
                title="Intensity Heatmap of Binned mz-features",
                xlabel="Timesteps",
                ylabel="Binned mz-features",
                cbar_label=f"Intensity ({self.dataset.intensity_unit})",
            )
            display(fig_heatmap)
        with self.output_widgets["binning_count"]:
            self.output_widgets["binning_count"].clear_output()
            fig_mcount, _ = self.binning_plots.plot_binning_count(
                self.dataset.binning_count,
                title="Discrete Heatmap of mz Value Counts per mz_weighted_mean and datetime",
                xlabel="Timesteps",
                ylabel="Binned mz-features",
            )
            display(fig_mcount)
        with self.output_widgets["histogram"]:
            self.output_widgets["histogram"].clear_output()
            fig_hist, _ = self.binning_plots.plot_histogram_with_unique_datetimes(
                num_bins=len(self.dataset.peaks_grouped.mz_weighted_mean.unique()),
                peaks_grouped=self.dataset.peaks_grouped,
                top_feature_count=30,
            )
            display(fig_hist)
        with self.output_widgets["top_n_alignment"]:
            self.output_widgets["top_n_alignment"].clear_output()
            fig_top_n = self.binning_plots.plot_top_n_heatmap(
                peaks_grouped=self.dataset.peaks_grouped,
                matrix=self.dataset.binning_count,
                n=10,
                title="Top 10 intensity per mz-feature HeatMap, Count",
            )
            display(fig_top_n)
        with self.output_widgets["mascope_targets"]:
            self.output_widgets["mascope_targets"].clear_output()
            fig_targets = self.binning_plots.plot_mascope_targets_heatmap(
                peaks_grouped=self.dataset.peaks_grouped,
                match_isotopes=self.dataset.match_isotopes,
                matrix=self.dataset.binning_count,
                title="Mascope Targets HeatMap, Count",
            )
            display(fig_targets)

        return sub_tabs

    def figure_tab_sparsity_density(self) -> wg.Output:
        """
        Build the Sparsity & Density tab.

        :return: wg.Output - The output widget containing
        the sparsity and density plots.
        :rtype: wg.Output
        """
        with self.output_widgets["sparsity_density"]:
            self.output_widgets["sparsity_density"].clear_output()
            fig_sd, _ = self.binning_plots.plot_sparsity_density(
                self.dataset.binning_intensity
            )
            display(fig_sd)

        return self.output_widgets["sparsity_density"]

    def figure_tab_zscore_outliers(self) -> wg.Tab:
        """
        Build the Z-Score Analysis tab.

        This tab includes sub-tabs for skewness and kurtosis,
        histogram, outlier ratio, box plot, and top outliers table.

        :return: wg.Tab - The tab containing the sub-tabs for Z-Score analysis.
        Each sub-tab contains a specific plot or table related to outlier analysis.
        :rtype: wg.Tab
        """

        # Calculate Z-scores and outlier ratios
        z_threshold = 3
        z_scores, outlier_ratio = calculate_outliers(
            matrix=self.dataset.binning_mz, z_threshold=z_threshold
        )
        z_scores = z_scores.droplevel("sample_item_id", axis=1)
        # Create outlier table
        outlier_data = z_scores[(z_scores.abs() > z_threshold)].stack().reset_index()
        outlier_data.columns = ["Bin", "Datetime", "Z-score"]
        outlier_data = outlier_data.sort_values(by="Z-score", ascending=False)
        # Create individual plots
        fig_skewkur, _ = self.binning_plots.plot_skewness_kurtosis(
            self.dataset.binning_intensity
        )
        fig_hist, _ = self.binning_plots.plot_outliers_histogram(z_scores)
        fig_ratio, _ = self.binning_plots.plot_outliers_ratio(
            outlier_ratio, z_threshold
        )
        fig_box, _ = self.binning_plots.plot_outliers_boxplot(z_scores)
        # Create tabs for each plot
        tab = wg.Tab()
        tab.children = [
            wg.Output(),  # Tab 1: skewness and kurtosis figure
            wg.Output(),  # Tab 2: Histogram
            wg.Output(),  # Tab 3: Outlier Ratio
            wg.Output(),  # Tab 4: Box Plot
            wg.Output(),  # Tab 5: Top Outliers table
        ]

        # Set tab titles
        tab.set_title(0, "Skewness and kurtosis")
        tab.set_title(1, "Histogram")
        tab.set_title(2, "Outlier Ratio")
        tab.set_title(3, "Box Plot")
        tab.set_title(4, "Top Outliers")

        # Display each figure in its respective tab
        with tab.children[0]:
            tab.children[0].clear_output()
            display(fig_skewkur)
        with tab.children[1]:
            tab.children[1].clear_output()
            display(fig_hist)
        with tab.children[2]:
            tab.children[2].clear_output()
            display(fig_ratio)
        with tab.children[3]:
            tab.children[3].clear_output()
            display(fig_box)
        with tab.children[4]:
            tab.children[4].clear_output()
            display(outlier_data)

        with self.output_widgets["zscore_analysis"]:
            self.output_widgets["zscore_analysis"].clear_output()
            display(tab)

        return self.output_widgets["zscore_analysis"]

    def figure_tab_random_spec_check(self) -> wg.Tab:
        """
        Build the Random Spectrum Check tab.

        This tab displays a random selection of spectra
        from the dataset for visual inspection.

        :return: wg.Tab - The tab containing the random spectrum check plots.
        Each sub-tab contains a plot for a randomly selected sample.
        :rtype: wg.Tab
        """

        # Extract only the 'datetime' level from the MultiIndex columns
        datetime_values = self.dataset.binning_intensity.columns.get_level_values(
            "datetime"
        ).unique()
        # Check that there are enough datetime values
        count = min(5, len(datetime_values))  # Limit to 5 samples
        sample_indices = np.random.choice(datetime_values, size=count, replace=False)
        # Create tabs for each sample
        tab = wg.Tab()
        tab.children = [wg.Output() for _ in sample_indices]
        # Set tab titles
        for i, sample_idx in enumerate(sample_indices):
            tab.set_title(i, f"Sample {sample_idx}")
        # Generate and display plots for each sample
        for i, sample_idx in enumerate(sample_indices):
            with tab.children[i]:
                tab.children[i].clear_output()
                fig, _ = self.binning_plots.plot_sample_comparison(
                    sample_idx=sample_idx,
                    binning_intensity=self.dataset.binning_intensity,
                    binning_mz=self.dataset.binning_mz,
                    peaks_grouped=self.dataset.peaks_grouped,
                    unit=self.dataset.intensity_unit,
                )
                display(fig)
        # Display the tabs
        with self.output_widgets["random_spec_check"]:
            self.output_widgets["random_spec_check"].clear_output()
            display(tab)

        return self.output_widgets["random_spec_check"]

    def on_clear_cache(self, change):
        """
        Callback for when `memory_cleared` changes.
        - If the accordion is open, update the figures in the tabs.
        - If the accordion is closed, reset the tabs to their default state.
        :param change: The change event dictionary.
        :type change: dict
        """
        try:
            logger.debug(
                "Binning parameters changed. Old value: %s, New value: %s",
                change["old"],
                change["new"],
            )
            # Check if the accordion is open
            if self.figure_accordion.selected_index is not None:
                logger.info("Updating binning analysis figures in binning module tabs.")
                self.populate_tabs()  # Refresh data and plots
                logger.info("Binning analysis figures updated successfully.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error(f"Error in on_binning_parameters_changed: {e}")

    def on_data_loaded(self, change) -> None:
        """
        Callback for when `data_loaded` changes.
        React to data being cleared or loaded.
        - If new data is loaded, populate tabs with new data
        if "Analysis figures"-accordion is open.
        - If data is cleared, reset tabs to default state.

        :param change: The change event dictionary.
        :type change: dict
        """
        try:
            if change["new"]:  # If data_loaded is True
                logger.info("Data loaded. Preparing to populate tabs with new data.")
                if self.figure_accordion.selected_index is not None:
                    logger.info("Accordion is open. Populating tabs with valid data.")
                    self.populate_tabs()  # Repopulate tabs with valid data
                else:
                    logger.info("Accordion is closed. Tabs will not be populated yet.")
                self.dataset.add_observer(
                    "memory_cleared", self.on_clear_cache
                )  # Attach observer to `memory_cleared`
            else:  # If data_loaded is False
                logger.info("Data cleared. Resetting tabs to default state.")
                self.reset_tabs()  # Clear the tabs
                logger.info("Tabs reset to default state successfully.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "on_data_loaded",
                e,
            )

    def reset_tabs(self) -> None:
        """
        Reset the tabs to their default state when data is not loaded.
        """
        try:
            if (
                self.figure_accordion.selected_index is not None
            ):  # Check if tabs are open
                logger.debug("Resetting tabs to default state.")
                for index, tab in enumerate(self.tabs.children):
                    tab_name = self.tabs.get_title(index)
                    if isinstance(tab, wg.Output):
                        with tab:
                            tab.clear_output()
                        logger.debug("Cleared Output tab: %s", tab_name)
                    elif isinstance(tab, wg.VBox):
                        tab.children = [
                            wg.Label("Content will be loaded when data is available.")
                        ]
                        logger.debug("Reset VBox tab to default state.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error("Error in reset_tabs: %s", e)
