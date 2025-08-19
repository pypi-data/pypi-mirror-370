from __future__ import annotations
import re
import numpy as np
import pandas as pd
from IPython.display import display
import ipywidgets as wg
from colorcet import glasbey as colorvector

from .extension import MassDefectDataExtension
from .plots import MassDefectPlotter

from ..mascope_data.wrapper import MascopeDataWrapper
from ..widgets_config import (
    DEFAULT_WIDGETS_PROPERTIES,
    DEFAULT_BOX_PROPERTIES,
)
from ..plot_tools import fetch_plotly_symbols
from ..logging_config import logger  # Import the shared logger


class MassDefectWidget:
    """Builds interactive Kendrick mass defect -figure."""

    def __init__(
        self,
        dataset: MascopeDataWrapper,
        figure_width: float = None,
        figure_height: float = None,
        on_click: callable | None = None,
    ):
        """
        The widget is designed to work with a dataset that has the
        MassDefectDataExtension extension.
        - This widget is designed to create an interactive
        Kendrick mass defect -figure using the provided dataset.
        - It allows users to select various parameters
        for the mass defect calculation and visualization.
        - The widget also supports a click event handler
        for further interaction with the figure.
        - figure_data -property can be used to get figure data as pandas dataframe.

        :param dataset: MascopeDataWrapper -dataset
        :type dataset: MascopeDataWrapper
        :param figure_width: Width of the figure, defaults to None
        :type figure_width: float, optional
        :param figure_height: Height of the figure, defaults to None
        :type figure_height: float, optional
        :param on_click: callable callback-function for click event handler, defaults to None
        :type on_click: callable | None, optional
        """

        self.dataset = dataset
        self.dataset.extend(MassDefectDataExtension)
        self.figure_width = figure_width
        self.figure_height = figure_height
        self.on_click = on_click
        if self.on_click is not None:
            self.click_output = wg.Output()
        self.massdefect_plotter = MassDefectPlotter(dataset=self.dataset)
        self.mass_defect_figure = wg.Output()
        self._peaks_mass_defect_km_updated = None
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
        Returns the data used to build the traces in the mass defect -figure.

        The data is stored in the `_peaks_mass_defect_km_updated` attribute,
        which is updated when the plot is created or updated.
        - This property returns a copy of the DataFrame to prevent
        unintended modifications to the original data.
        - If no data is available, it returns an empty DataFrame.

        :return: A pandas DataFrame containing the data used for the figure.
        :rtype: pd.DataFrame
        """
        if self._peaks_mass_defect_km_updated is not None:
            logger.info(
                "The resulting mass defect DataFrame contains %d rows and %d columns.",
                len(self._peaks_mass_defect_km_updated),
                len(self._peaks_mass_defect_km_updated.columns),
            )
            return self._peaks_mass_defect_km_updated.copy()
        else:
            logger.warning("No data available for the figure.")
            return pd.DataFrame()  # Return an empty DataFrame if no data is available

    def create_widgets(self) -> None:
        """
        Create and configure interactive controls
        for the Kendrick Marker Plot.
        """

        self.wbx_mass_defect_method = wg.Dropdown(
            options=["KMD", "KMD_base", "REKMD", "SKMD"],
            value="KMD",
            description="Scaling method:",
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_xaxis = wg.Dropdown(
            options=["mz", "mz_round"],
            value="mz",
            description="Select x-axis value: ",
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_scaling_method = wg.Dropdown(
            options=[
                "intensity",
                "log-normalized/min_max_intensity",
                "norm_intensity",
                "sample_item_id",
            ],
            value="log-normalized/min_max_intensity",
            description="Select scaling method for colour: ",
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_annotation = wg.Dropdown(
            options=[
                "target_compound_name",
                "target_compound_formula",
                "target_ion_formula",
                "ionization_mechanism",
                "match_score_isotope",
            ],
            value="target_compound_formula",
            description="Annotation column:",
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_integer_scaling_factor = wg.FloatText(
            value=48,
            description="Integer scaling factor X",
            disabled=True,
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_base_unit = wg.Dropdown(
            options=list(self.dataset.base_units.keys()),
            value="cNO2",
            description="Base unit:",
            disabled=True,
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_mz_normalization_method = wg.Dropdown(
            options=["floor", "ceil", "round"],
            value="round",
            description="Rounding:",
            **DEFAULT_WIDGETS_PROPERTIES,
        )
        self.wbx_binned_checkbox = wg.Checkbox(
            value=False,
            description="Binned data",
            disabled=False,
            **DEFAULT_WIDGETS_PROPERTIES,
        )

    def create_layout(self) -> None:
        """
        Create the layout for
        the widget-selector and figure.
        """

        figure_settings = wg.VBox(
            [
                self.wbx_binned_checkbox,
                self.wbx_mass_defect_method,
                self.wbx_xaxis,
                self.wbx_scaling_method,
                self.wbx_annotation,
                self.wbx_integer_scaling_factor,
                self.wbx_base_unit,
                self.wbx_mz_normalization_method,
            ]
        )
        # Create an Accordion with a single section
        accordion = wg.Accordion(children=[figure_settings])
        accordion.set_title(0, "Figure settings")
        # Arrange controls in a layout
        self.group = wg.VBox(
            [
                wg.VBox(
                    [
                        accordion,
                    ],
                    **DEFAULT_BOX_PROPERTIES,
                ),
                self.mass_defect_figure,
            ]
        )

    def display_layout(self) -> None:
        """Displays the widget layout."""

        display(self.group)
        if self.on_click is not None:
            display(self.click_output)

    def setup_event_handlers(self) -> None:
        """
        Attach observers to a list of widget controls.
        This method adds observers to a predefined set of widgets,
        enabling them to call the`update_plot_from_controls` method
        whenever their values change.
        """
        widgets_to_observe = [
            self.wbx_binned_checkbox,
            self.wbx_xaxis,
            self.wbx_scaling_method,
            self.wbx_annotation,
            self.wbx_integer_scaling_factor,
            self.wbx_base_unit,
            self.wbx_mz_normalization_method,
            self.wbx_mass_defect_method,
        ]
        for widget in widgets_to_observe:
            widget.observe(self.update_plot_from_controls, names="value")

        self.wbx_mass_defect_method.observe(
            self.handle_mass_defect_method_change, names="value"
        )

    def create_figure_output(self) -> None:
        """
        Build output containing
        plotly figure layout.
        """
        try:
            logger.debug("Creating base mass defect figure.")
            self.fig = self.massdefect_plotter.base_mass_defect_figure(
                width=self.figure_width,
                height=self.figure_height,
            )
            with self.mass_defect_figure:
                display(self.fig)
            logger.debug("Base mass defect figure created successfully.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "create_figure_output",
                e,
            )

    def handle_mass_defect_method_change(self, change) -> None:
        """
        Define the event handler for
        the Kendrick method dropdown.

        If the Kendrick method is set to 'KMD',
        the integer scaling and base unit widgets are disabled.
        Otherwise, they are enabled.
        """
        try:
            logger.debug(f"Mass defect method changed to: {change['new']}")
            if change["new"] == "KMD":
                self.wbx_integer_scaling_factor.disabled = True
                self.wbx_base_unit.disabled = True
                logger.debug("Disabled integer scaling factor and base unit widgets.")
            else:
                self.wbx_integer_scaling_factor.disabled = False
                self.wbx_base_unit.disabled = False
                logger.debug("Enabled integer scaling factor and base unit widgets.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "handle_mass_defect_method_change",
                e,
            )

    def update_plot_from_controls(
        self, change=None  # pylint: disable=unused-argument
    ) -> None:
        """
        Update the plot based on the values from the control widgets.

        - This method gathers the current values from various
        control widgets and refresh the plot.
        - It also attaches the `click_callback` method from
        ClickEventHandler -class to the figure traces
        `on_click` event if callable -function is given as 'on_click' -parameter.
        """
        try:
            logger.debug("Updating Mass defect -figure from control widgets.")
            if self.on_click is not None:
                with self.click_output:
                    self.click_output.clear_output()
                logger.debug("Cleared click-event output.")
                for (
                    trace
                ) in self.fig.data:  # Temporarily remove the `on_click` callback
                    trace.on_click(None)
            mz_normalization_method = {"floor": np.floor, "ceil": np.ceil}.get(
                self.wbx_mz_normalization_method.value, np.round
            )
            logger.debug(
                f"Using rounding method: {self.wbx_mz_normalization_method.value}"
            )
            self._peaks_mass_defect_km_updated = (
                self.dataset.calculate_scaled_mass_defect(
                    mass_defect_method=self.wbx_mass_defect_method.value,
                    mz_normalization_method=mz_normalization_method,
                    base_unit=self.wbx_base_unit.value,
                    integer_scaling_factor=self.wbx_integer_scaling_factor.value,
                    binned_data=self.wbx_binned_checkbox.value,
                )
            )
            logger.debug("Scaled mass defect calculated successfully.")
            marker_symbols = fetch_plotly_symbols()
            # Update traces to figure
            with self.fig.batch_update():
                self.fig.data = []  # Removes all existing traces
                logger.debug("Cleared existing traces from the figure.")
                for i, sample_item_id in enumerate(
                    self._peaks_mass_defect_km_updated.sample_item_id.unique()
                ):
                    logger.info(f"Adding trace for sample_item_id: {sample_item_id}")
                    # Conditionally set colorscale, color and symbol based on scaling method
                    if self.wbx_scaling_method.value == "sample_item_id":
                        show_colorbar = (
                            False  # Hide colorbar as it's not needed for static color
                        )
                        color = colorvector[i]  # Set own color for each trace
                        symbol = "circle"  # Set symbol to be same for all traces
                    else:
                        show_colorbar = (
                            True if i == 0 else False
                        )  # Show colorbar only for the first trace, same for all traces
                        color = (
                            None  # Set color to None, 'rainbow' colorscale will be used
                        )
                        symbol = marker_symbols[i]  # Set own symbol for each trace
                    # Filter data for the current sample
                    df_plot = self._peaks_mass_defect_km_updated[
                        self._peaks_mass_defect_km_updated.sample_item_id
                        == sample_item_id
                    ]
                    trace = self.massdefect_plotter.create_mass_defect_trace(
                        df=df_plot,
                        sample_name=df_plot.sample_item_name_datetime.iloc[0],
                        mz=self.wbx_xaxis.value,
                        scaling_method=self.wbx_scaling_method.value,
                        annotation=self.wbx_annotation.value,
                        unit=self.dataset.intensity_unit,
                        symbol=symbol,
                        show_colorbar=show_colorbar,
                        color=color,
                    )
                    self.fig.add_trace(trace)
                logger.info("All traces added to the mass defect figure.")
                # Layout
                title, xaxis_title, yaxis_title = self.get_figure_labels()
                layout = self.massdefect_plotter.create_layout(
                    xaxis_title=xaxis_title,
                    yaxis_title=yaxis_title,
                    title=title,
                    width=self.figure_width,
                    height=self.figure_height,
                )
                self.fig.update_layout(layout)
            # Attach the click event handler to the figure traces
            if self.on_click is not None:
                self.massdefect_plotter.attach_click_callback(
                    fig=self.fig,
                    callback_function=self.on_click,
                    click_output=self.click_output,
                    reference_df=self._peaks_mass_defect_km_updated,
                    x_axis=self.wbx_xaxis.value,
                    y_axis="kendrick_mass_defect",
                )
                logger.debug("Click event handler attached to mass defect figure.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "update_plot_from_controls",
                e,
            )

    def get_figure_labels(self) -> tuple[str, str, str]:
        """Set titles for the figure.

        :return: title, y-axis title, x-axis title
        :rtype: tuple[str, str, str]
        """

        title = f"n={len(self._peaks_mass_defect_km_updated)}"
        xaxis_title = "m/z [Th]" if self.wbx_xaxis.value == "mz" else "nominal m/z [Th]"
        # Set y-axis names according selected factors
        if self.wbx_mass_defect_method.value == "MD":
            yaxis_title = "mass defect [Th]"
        else:
            yaxis_title = (
                str(self.wbx_mass_defect_method.value)
                + "(m/z, "
                + re.sub("c", "", self.wbx_base_unit.value)
                + ", "
                + str(int(self.wbx_integer_scaling_factor.value))
                + ")"
            )
        return title, xaxis_title, yaxis_title

    def on_clear_cache(self, change) -> None:  # pylint: disable=unused-argument
        """
        Callback for when `memory_cleared` changes.
        React to clearing the cache.
        - When the cache is cleared, updates the figure traces.
        """
        try:
            logger.info("Cache cleared. Updating figure traces.")
            self.update_plot_from_controls()
            logger.info("Figure traces updated successfully after cache clear.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error("Error in on_clear_cache: %s", e)

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
                    "Data loaded. Preparing to update mass defect figure traces."
                )
                # Attach observer to `memory_cleared`
                self.dataset.add_observer("memory_cleared", self.on_clear_cache)
                logger.debug(
                    f"Observer for `memory_cleared` attached to {self.__class__.__name__}"
                    " on_clear_cache"
                )
                self.update_plot_from_controls()
                logger.info("Mass defect traces updated successfully after data load.")
            else:
                logger.info("Data cleared. Resetting mass defect figure to base state.")
                self.reset_figure()
                logger.info("Mass defect figure reset to base state successfully.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "on_data_loaded",
                e,
            )

    def reset_figure(self) -> None:
        """
        Reset the figure to its base state when data is not loaded.
        """
        try:
            logger.debug("Resetting mass defect figure to base state.")
            with self.mass_defect_figure:
                self.fig.data = []
                logger.debug("Cleared all traces from mass defect figure.")
                if self.on_click is not None:
                    with self.click_output:
                        self.click_output.clear_output()
                    logger.debug("Cleared click-event output from mass defect figure.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error("Error in reset_figure: %s", e)
