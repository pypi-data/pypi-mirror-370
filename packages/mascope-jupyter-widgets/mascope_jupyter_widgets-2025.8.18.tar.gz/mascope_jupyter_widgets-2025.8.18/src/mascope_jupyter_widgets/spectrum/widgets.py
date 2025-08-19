import ipywidgets as wg
import pandas as pd
from IPython.display import display

from .plots import SpectrumPlotter
from .extension import SpectrumDataExtension

from ..mascope_data.wrapper import MascopeDataWrapper
from ..plot_tools import extract_figure_data
from ..logging_config import logger  # Import the shared logger


class SpectrumWidget:
    """
    Builds widget selector for spectrum plots.
    """

    def __init__(
        self,
        dataset: MascopeDataWrapper,
    ):
        """
        The widget is designed to work with a dataset that has the
        SpectrumDataExtension extension. It exteds the dataset with this extension
        and uses the SpectrumPlotter class to create a base spectrum figure which
        is updated according selected data.

        The widget is used to display spectrum plots and allows
        users to interactively select different spectra to visualize.
        figure_data -property can be used to get figure data as pandas dataframe.

        :param dataset: MascopeDataWrapper -dataset
        :type dataset: MascopeDataWrapper
        """

        self.dataset = dataset
        self.dataset.extend(SpectrumDataExtension)
        self.spectrum_plots = SpectrumPlotter(dataset=self.dataset)
        self.spectrum_figure = wg.Output()
        # Setup widget-selector
        self.create_figure_output()
        self.display_layout()

        self.dataset.add_observer("data_loaded", self.on_data_loaded)

        # Populate widgets with data if data is already loaded
        if self.dataset.data_loaded:
            self.on_data_loaded({"new": True})  # Simulate a change event

    @property
    def figure_data(self) -> pd.DataFrame:
        """
        Returns the data used to build the traces in the spectrum figure.
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
            self.fig, x_col="mz", y_col="intensity", name_col="name"
        )

    def display_layout(self) -> None:
        """Displays the widget layout."""
        display(self.spectrum_figure)

    def create_figure_output(self) -> None:
        """Build output containing plotly figure layout"""

        try:
            logger.debug("Creating base spectrum figure.")
            self.fig = self.spectrum_plots.base_spectrum_figure()
            with self.spectrum_figure:
                display(self.fig)
            logger.debug("Base spectrum figure created successfully.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "create_figure_output",
                e,
            )

    def update_figures(self, change=None) -> None:  # pylint: disable=unused-argument
        """Updates figure traces based on data.

        This method is called when the data is loaded or cleared.
        It updates the figure traces based on the current state of the dataset.
        If the dataset is not loaded, it resets the figure to its base state.
        If the dataset is loaded, it updates the figure traces with the new data.

        :param change: The change event dictionary.
        :type change: dict
        """

        try:
            logger.debug("Updating spectrum figure traces.")
            match_samples = self.dataset.match_samples

            with self.fig.batch_update():
                self.fig.data = []
                logger.debug("Cleared existing traces from the spectrum figure.")
                for (
                    sample_item_id
                ) in (
                    match_samples.sample_item_id.unique()
                ):  # Loop through unique sample_item_ids
                    logger.debug("Processing sample_item_id: %s", sample_item_id)
                    traces = self.spectrum_plots.get_spectrum_traces(
                        sample_item_id=sample_item_id,
                    )
                    self.fig.add_traces(traces)
                    logger.debug(f"Added traces for sample_item_id: {sample_item_id}")
            logger.debug("Spectrum figure traces updated successfully.")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "update_figures",
                e,
            )

    def on_clear_cache(self, change) -> None:  # pylint: disable=unused-argument
        """
        Callback for when `memory_cleared`
        flag of the dataset changes.
        React to clearing the cache.
        - When the cache is cleared, updates the figure traces.

        :param change: The change event dictionary.
        :type change: dict
        """
        try:
            logger.info("Cache cleared. Updating spectrum figure traces.")
            self.update_figures()
            logger.info(
                "Spectrum figure traces updated successfully after cache clear."
            )
        except (AttributeError, ValueError, TypeError) as e:
            logger.error("Error in on_clear_cache: %s", e)

    def on_data_loaded(self, change) -> None:
        """
        Callback for when `data_loaded`
        flag of the dataset changes.
        React to data being cleared or loaded.
        - If new data is loaded, updates figure traces.
        - If data is cleared, removes traces and reset figure to base.

        :param change: The change event dictionary.
        :type change: dict
        """
        try:
            if change["new"]:  # If data_loaded is True
                logger.info("Data loaded. Preparing to update spectrum figure traces.")
                self.dataset.add_observer("memory_cleared", self.on_clear_cache)
                logger.debug(
                    f"Observer for `memory_cleared` attached to {self.__class__.__name__}"
                    " on_clear_cache"
                )
                self.update_figures()
                logger.info(
                    "Spectrum figure traces updated successfully after data load."
                )
            else:
                logger.info("Data cleared. Resetting spectrum figure to base state.")
                self.reset_figure()
                logger.info("Spectrum figure reset to base state successfully.")
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

        This method clears all traces from the figure and resets the layout
        to its base state. It is called when the data is cleared or not loaded.
        It handles any exceptions that may occur during the reset process
        and logs the error messages.
        """
        try:
            logger.debug("Resetting spectrum figure to base state.")
            with self.spectrum_figure:
                self.fig.data = []
                logger.debug("Cleared all traces from the spectrum figure.")
                layout = self.spectrum_plots.build_layout()
                self.fig.update_layout(layout)
                logger.debug("Spectrum figure layout reset successfully.")
        except (
            AttributeError,
            ValueError,
            TypeError,
        ) as e:
            logger.error(
                "Error in %s.%s: %s",
                self.__class__.__name__,
                "reset_figure",
                e,
            )
