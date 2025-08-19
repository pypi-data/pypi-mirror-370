from __future__ import annotations
from typing import List
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from colorcet import glasbey as colorvector

colorvector = colorvector[1:]  # Skip the first color (red)

from .extension import PeakVisualizationExtension
from ..mascope_data.wrapper import MascopeDataWrapper
from ..logging_config import logger
from ..plot_tools import hover_string, DEFAULT_SCATTER_TYPE
from ..spectrum.extension import SpectrumDataExtension
from ..spectrum.plots import SpectrumPlotter
from ..sample_timeseries.extension import SampleTimeSeriesExtension
from ..sample_timeseries.plots import (
    SampleTimeSeriesPlotter,
)


class PeakVisualizationPlotter:
    """
    PeakVisualizationPlotter is a class for plotting multiple spectra and sample timeseries
    from a MascopeDataWrapper dataset for given mz-range.
    It allows plotting spectra for multiple m/z
    values with specified ppm tolerances in a single figure with subplots.
    Sample timeseries can also be plotted for each m/z value in the same subplot.
    """

    def __init__(self, dataset: MascopeDataWrapper):
        self.dataset = dataset
        # Extend dataset if necessary
        if not hasattr(self.dataset, "get_spectrum_data"):
            self.dataset.extend(SpectrumDataExtension)
        if not hasattr(self.dataset, "get_sample_peak_timeseries"):
            self.dataset.extend(SampleTimeSeriesExtension)
        # Initialize plotters
        self.spectrum_plotter = SpectrumPlotter(dataset=self.dataset)
        self.sample_timeseries_plotter = SampleTimeSeriesPlotter(dataset=self.dataset)

        self.fig = self.build_base_plot()
        self.spectrum_subplot_ydata = {}
        self.trace_cache_spectrum = {}
        self.trace_cache_timeseries = {}

    def build_base_plot(
        self, n: int = 1, subplot_titles: list[str] = None
    ) -> go.Figure:
        """
        Build an empty base plot with 2 rows:
        - Row 1: placeholder for spectra subplots (to be added later)
        - Row 2: one wide subplot for sample time-series

        :param n: Number of m/z subplots to create in the first row.
        :type n: int
        :param subplot_titles: List of titles for each m/z subplot.
        :type subplot_titles: list[str] | None
        :return: A Plotly Figure object with the base layout.
        :rtype: go.Figure
        """
        # Start with 1 column, will add more with .add_subplot()
        # or .add_trace() as needed
        specs = [
            [{} for _ in range(n)],
            [{"colspan": n, "type": "xy"}] + [None] * (n - 1),
        ]
        if subplot_titles is None:
            subplot_titles = ["Spectra"] * n + ["Sample Time-Series"]
        fig = make_subplots(
            rows=2,
            cols=n,
            shared_xaxes=False,
            vertical_spacing=0.1,
            specs=specs,
            subplot_titles=subplot_titles,
            row_heights=[0.5, 0.5],
        )
        # Set subplot title font size
        for annotation in fig.layout.annotations:
            annotation.font.size = 10

        return fig

    def get_spectrum_traces(
        self,
        sample_item_id: str,
        mz_list: list,
        dmz_list: list,
        rel_ab_list: list | None = None,
        label_list: list | None = None,
        color_map: dict = None,
    ) -> List[go.Scattergl]:
        """
        Get spectrum traces for multiple m/z values with specified ppm tolerances.
        Each trace will be labeled with the m/z value and ppm tolerance.

        This method retrieves spectra for each m/z value within the specified ppm tolerance
        and returns a list of Plotly Scatter traces that can be added to a figure.

        :param sample_item_id: ID of the sample file to plot spectra from.
        :type sample_item_id: str
        :param mz_list: List of m/z values to plot.
        :type mz_list: list
        :param dmz_list: List of ppm tolerances for each m/z value.
        :type dmz_list: list
        :param color_map: Optional dictionary mapping m/z values to colors.
        :type color_map: dict, optional
        :return: List of Plotly Scatter traces for the spectra (DEFAULT_SCATTER_TYPE).
        :rtype: List[go.Scattergl]
        """
        all_traces = []
        subplot_col = 1

        for i, (mz, dmz) in enumerate(zip(mz_list, dmz_list)):
            if rel_ab_list is not None and label_list is not None:
                rel_ab = rel_ab_list[i]
                label = label_list[i]
                info_str = f"{label} ({rel_ab:.2%})"
            else:
                info_str = f"(m/z={mz:.4f}±{dmz}ppm)"
            cache_key = (sample_item_id, mz, dmz)
            if cache_key in self.trace_cache_spectrum:
                traces = self.trace_cache_spectrum[cache_key]
            else:
                traces = self.spectrum_plotter.get_spectrum_traces(
                    sample_item_id=sample_item_id,
                    mz_min=mz - dmz,
                    mz_max=mz + dmz,
                    color_map=color_map,
                )
                self.trace_cache_spectrum[cache_key] = traces
            # Only add a subplot if there are real traces
            for trace in traces:
                if trace is None:
                    continue
                if info_str not in trace.name:
                    trace.name += f" {info_str}"
                trace._subplot_row = 1  # pylint:disable=protected-access
                trace._subplot_col = subplot_col  # pylint:disable=protected-access
                trace.showlegend = False
                self.spectrum_subplot_ydata[subplot_col].extend(trace.y)
                all_traces.append(trace)
            subplot_col += 1  # This was cause of the bug

        return all_traces

    def get_sample_timeseries_traces(
        self,
        sample_item_id: str,
        mz_list: list,
        peak_mz_tolerance_ppm: float = 3,
        color_map: dict | None = None,
    ) -> List[go.Scattergl]:
        """
        Get sample time-series traces for multiple m/z values with specified ppm tolerances.
        Each trace will be labeled with the m/z value and ppm tolerance.
        This method retrieves sample time-series data for each m/z value within the specified
        ppm tolerance and returns a list of Plotly Scatter traces that can be added to a figure.

        :param sample_item_id: ID of the sample item to plot time-series from.
        :type sample_item_id: str
        :param mz_list: List of m/z values to plot.
        :type mz_list: list
        :param color_map: Optional dictionary mapping m/z values to colors.
        :type color_map: dict, optional
        :return: List of Plotly Scatter traces for the sample time-series.
        :rtype: List[go.Scattergl] (DEFAULT_SCATTER_TYPE)
        """
        all_traces = []
        # List of Plotly dash styles
        dash_styles = [
            "solid",
            "dot",
            "dash",
            "longdash",
            "dashdot",
            "longdashdot",
        ]
        for i, mz in enumerate(mz_list):
            info_str = f"(m/z={mz:.4f}±{peak_mz_tolerance_ppm}ppm)"
            # Find best cache match: same sample, same mz, and tolerance <= requested
            best_key = None
            best_tolerance = None
            for sid, mz_cached, tol_cached in self.trace_cache_timeseries:
                if (
                    sid == sample_item_id
                    and mz_cached == mz
                    and tol_cached <= peak_mz_tolerance_ppm
                ):
                    if best_tolerance is None or tol_cached > best_tolerance:
                        best_key = (sid, mz_cached, tol_cached)
                        best_tolerance = tol_cached
            if best_key is not None:
                timeseries_traces = self.trace_cache_timeseries[best_key]
            else:
                timeseries_traces = (
                    self.sample_timeseries_plotter.get_sample_timeseries_traces(
                        peak_mz=mz,
                        sample_item_id=sample_item_id,
                        peak_mz_tolerance_ppm=peak_mz_tolerance_ppm,
                        color_map=color_map,
                    )
                )
                self.trace_cache_timeseries[
                    (sample_item_id, mz, peak_mz_tolerance_ppm)
                ] = timeseries_traces
            for trace in timeseries_traces:
                if trace is None:
                    continue
                if info_str not in trace.name:
                    trace.name += f" {info_str}"
                trace._subplot_row = 2  # pylint:disable=protected-access
                trace._subplot_col = 1  # pylint:disable=protected-access
                # If no color_map, assign a unique marker symbol
                if color_map is None:
                    trace.line.dash = dash_styles[i % len(dash_styles)]
                all_traces.append(trace)

        return all_traces

    def get_peaks_traces(
        self,
        sample_item_id: str,
        mz_list: list,
        dmz_list: list,
        legend_names: list,
        peak_mz_tolerance_ppm: float = 3,
        color_map: dict | None = None,
    ) -> List[go.Scattergl]:
        """
        Get traces for peaks in the dataset for multiple m/z values with specified tolerances.

        Each trace will be labeled with the m/z value and tolerance.
        This method retrieves peaks for each m/z value within the specified tolerances
        and returns a list of Plotly Scatter traces that can be added to a figure.

        :param sample_item_id: ID of the sample item to plot peaks from.
        :type sample_item_id: str
        :param mz_list: List of m/z values to plot.
        :type mz_list: list
        :param dmz_list: List of Δm/z values for each m/z value.
        :type dmz_list: list
        :param legend_names: List of legend names for the peaks.
        :type legend_names: list
        :param peak_mz_tolerance_ppm: PPM tolerance for peak m/z matching.
        :type peak_mz_tolerance_ppm: float
        :param color_map: Optional dictionary mapping sample_item_id to colors.
        :type color_map: dict, optional
        :return: List of Plotly Scattergl traces for the peaks (DEFAULT_SCATTER_TYPE).
        :rtype: List[go.Scattergl]
        """

        traces = []
        if not hasattr(self.dataset, "peaks_matched"):
            logger.warning(
                "Dataset does not have peaks_matched attribute. "
                "Please import peaks first. "
            )
            return []
        # Assign colors to each sample_item_id
        if color_map is None:
            sample_item_ids = sorted(
                self.dataset.match_samples["sample_item_id"].unique()
            )
            color_map = {
                sample_item_id: colorvector[i % len(colorvector)]
                for i, sample_item_id in enumerate(sample_item_ids)
            }

        def make_bar_and_dot(
            peaks: pd.DataFrame,
            subplot_col: int,
            color: str,
            legend_name: str,
            hover_elements: list[str],
        ) -> List[go.Scattergl]:
            """
            Create a vertical bar and a dot at the top for a peak.

            :param peaks: DataFrame containing peaks information (mz, intensity)
            in specific range.
            :type peaks: pd.DataFrame
            :param subplot_col: Subplot column index to place the traces.
            :type subplot_col: int
            :param color: Color for the bar and dot.
            :type color: str
            :param legend_name: Name for the legend entry.
            :type legend_name: str
            :param hover_elements: List of elements to include in the hover template.
            :type hover_elements: list[str]
            :return: List of Plotly Scatter traces (bar and dot).
            :rtype: List[go.Scattergl] (DEFAULT_SCATTER_TYPE)
            """
            # Define Hover box elements
            hovertemplate = hover_string(hover_elements)

            # Prepare vertical lines: for each x, a line from (x, 0) to (x, y), separated by None
            x_lines = []
            y_lines = []
            for xi, yi in zip(peaks["mz"], peaks["intensity"]):
                x_lines += [xi, xi, None]
                y_lines += [0, yi, None]
            bar_line = DEFAULT_SCATTER_TYPE(
                x=x_lines,
                y=y_lines,
                mode="lines",
                line=dict(color=color, width=2),
                name=f"{legend_name}_Stem",
                showlegend=False,
                hoverinfo="skip",  # This hides the hoverbox
                legendgroup=legend_name,  # Link with main trace
            )
            bar_line._subplot_row = 1  # pylint:disable=protected-access
            bar_line._subplot_col = subplot_col  # pylint:disable=protected-access
            # Dot at the top
            dot = DEFAULT_SCATTER_TYPE(
                x=peaks["mz"],
                y=peaks["intensity"],
                mode="markers",
                marker=dict(color=color, size=8),
                name=legend_name,
                showlegend=False,
                customdata=peaks[hover_elements],
                hovertemplate=hovertemplate,
                legendgroup=legend_name,  # Link with main trace
            )
            dot._subplot_row = 1  # pylint:disable=protected-access
            dot._subplot_col = subplot_col  # pylint:disable=protected-access

            return [bar_line, dot]

        for i, (mz, dmz, legend_name) in enumerate(
            zip(mz_list, dmz_list, legend_names)
        ):
            # Get peaks in ppm tolerance
            hoverbox_ppm = [
                "sample_item_id",
                "intensity",
                "unit",
                "sample_item_name",
                "target_compound_name",
                "target_compound_formula",
                "match_score_isotope",
                "instrument",
            ]
            peaks_in_ppm = self.dataset.get_peaks_in_ppm(
                sample_item_id, mz, peak_mz_tolerance_ppm
            )
            traces_ppm = make_bar_and_dot(
                peaks_in_ppm,
                i + 1,
                color_map[sample_item_id],
                legend_name,
                hoverbox_ppm,
            )
            traces.extend(traces_ppm)

            # Get peaks in Δm/z tolerance
            hoverbox_dmz = [
                "sample_item_id",
                "sample_item_name",
                "mz",
                "intensity",
                "unit",
            ]
            peaks_in_dmz = self.dataset.get_peaks_in_dmz(sample_item_id, mz, dmz)
            # Remove ppm peaks from dmz peaks (by mz)
            peaks_in_dmz_unique = peaks_in_dmz[~peaks_in_dmz.mz.isin(peaks_in_ppm.mz)]
            traces_in_dmz = make_bar_and_dot(
                peaks_in_dmz_unique, i + 1, "grey", legend_name, hoverbox_dmz
            )
            traces.extend(traces_in_dmz)

        return traces

    def build_multi_figure(
        self,
        mz_list: list,
        dmz_list: list,
        selected_samples: str | list,
        rel_ab_list: list | None = None,
        label_list: list | None = None,
        peak_mz_tolerance_ppm: float = 3,
    ) -> go.Figure:
        """Build a multi-sample figure with spectra and sample time-series.

        This method creates a Plotly Figure with subplots for each m/z value in `mz_list`
        and adds traces for the spectra and sample time-series for the specified samples.
        Each subplot will contain:
        - Spectrum traces for the m/z values within the specified Δm/z tolerances.
        - Sample time-series traces for the specified samples, showing the intensity
        over time for the m/z values.
        Each trace will be labeled with the m/z value and ppm tolerance.
        The figure will have red vertical lines at each theoretical m/z value for reference.
        The figure contains also measured peaks for each m/z value,
        both in Δm/z (grey) and ppm tolerances (same color as spectrum).


        :param mz_list: List of m/z values for the target isotopes.
        :type mz_list: list
        :param dmz_list: List of Δm/z values for each target isotopes.
        :type dmz_list: list
        :param rel_ab_list: List of relative abundances for each target isotopes.
        :type rel_ab_list: list
        :param label_list: List of labels for each target formula.
        :type label_list: list
        :param selected_samples: Sample file ID or List of selected sample IDs.
        :type selected_samples: str | list
        :param peak_mz_tolerance_ppm: PPM tolerance for peak m/z matching.
        :type peak_mz_tolerance_ppm: float
        :return: A Plotly Figure object containing the multi-sample plot.
        :rtype: go.Figure
        """

        if isinstance(selected_samples, str):
            selected_samples = [selected_samples]

        if (
            mz_list is None
            or len(mz_list) == 0
            or dmz_list is None
            or len(dmz_list) == 0
            or selected_samples is None
            or len(selected_samples) == 0
        ):
            logger.warning(
                "Cannot build multi-sample figure: "
                "m/z list, dmz list, or selected samples are empty."
            )
            return go.Figure()

        if rel_ab_list is not None and label_list is not None:
            subplot_titles = [
                f"{label} ({rel_ab:.2%})"
                for label, rel_ab in zip(label_list, rel_ab_list)
            ]
        else:
            subplot_titles = [
                f"m/z={float(mz):.4f} ± {dmz}" for mz, dmz in zip(mz_list, dmz_list)
            ]
        subplot_titles += ["Sample Time-Series"]

        fig = self.build_base_plot(n=len(mz_list), subplot_titles=subplot_titles)
        # Assign a color for each sample
        sample_colors = {
            sample: colorvector[i % len(colorvector)]
            for i, sample in enumerate(selected_samples)
        }
        self.spectrum_subplot_ydata = {i + 1: [] for i in range(len(mz_list))}
        for sample in selected_samples:
            sample_str = f"[{sample}]"
            # Sample spectrum traces
            traces_spectrum = self.get_spectrum_traces(
                sample_item_id=sample,
                mz_list=mz_list,
                dmz_list=dmz_list,
                rel_ab_list=rel_ab_list,
                label_list=label_list,
                color_map=None,
            )
            trace_names = []
            for trace in traces_spectrum:
                if sample_str not in trace.name:
                    trace.name += f" {sample_str}"
                    trace.legendgroup = trace.name
                trace_names.append(trace.name)
                trace.line.color = sample_colors[sample]
                fig.add_trace(
                    trace,
                    row=trace._subplot_row,  # pylint:disable=protected-access
                    col=trace._subplot_col,  # pylint:disable=protected-access
                )
            # Add peak traces to spectrum subplots
            peak_traces = self.get_peaks_traces(
                sample_item_id=sample,
                mz_list=mz_list,
                dmz_list=dmz_list,
                peak_mz_tolerance_ppm=peak_mz_tolerance_ppm,
                legend_names=trace_names,
                color_map=sample_colors,
            )
            for trace in peak_traces:
                fig.add_trace(
                    trace,
                    row=trace._subplot_row,  # pylint:disable=protected-access
                    col=trace._subplot_col,  # pylint:disable=protected-access
                )
            # Sample time-series traces
            traces_sample_ts = self.get_sample_timeseries_traces(
                sample, mz_list, peak_mz_tolerance_ppm, color_map=None
            )
            for trace in traces_sample_ts:
                if sample_str not in trace.name:
                    trace.name += f" {sample_str}"
                trace.line.color = sample_colors[sample]
                trace.marker.color = sample_colors[sample]
                fig.add_trace(
                    trace,
                    row=trace._subplot_row,  # pylint:disable=protected-access
                    col=trace._subplot_col,  # pylint:disable=protected-access
                )
        # Add vertical lines for each theoretical m/z value
        self._add_vertical_lines(fig, mz_list)
        self._update_layout_and_fonts(fig, mz_list)

        return fig

    def _add_vertical_lines(self, fig: go.Figure, mz_list: list) -> None:
        """
        Add vertical lines for each theoretical m/z value in the first row of subplots.

        This method iterates over the m/z values and adds a vertical line
        to each subplot in the first row, spanning the full y-range of the subplot.

        :param fig: The Plotly Figure object to add the lines to.
        :type fig: go.Figure
        :param mz_list: List of m/z values to add vertical lines for.
        :type mz_list: list
        """

        for i, mz in enumerate(mz_list):
            yaxis = getattr(fig.layout, f"yaxis{i+1}", None)
            y_min, y_max = None, None
            if yaxis and yaxis.range:
                y_min, y_max = yaxis.range
            else:
                y_data = self.spectrum_subplot_ydata.get(i + 1, [])
                if y_data:
                    y_min = min(y_data)
                    y_max = max(y_data)
                else:
                    y_min, y_max = 0, 1
            fig.add_shape(
                type="line",
                x0=mz,
                x1=mz,
                y0=y_min,
                y1=y_max,
                xref=f"x{i+1}",
                yref=f"y{i+1}",
                line=dict(color="red", width=2, dash="solid"),
                layer="above",
                row=1,
                col=i + 1,
            )

    def _update_layout_and_fonts(self, fig: go.Figure, mz_list: list) -> None:
        """
        Update the layout and fonts of the figure.

        This method adjusts the height, legend, and font sizes of the figure
        based on the number of m/z values and traces in the figure.

        :param fig: The Plotly Figure object to update.
        :type fig: go.Figure
        :param mz_list: List of m/z values to determine layout adjustments.
        :type mz_list: list
        """

        n_legend_items = len(fig.data)
        legend_height_per_row = 20
        legend_rows = (n_legend_items // 5) + 1
        bottom_margin = 60 + legend_rows * legend_height_per_row
        fig.update_layout(
            height=1000,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.45,  # Position legend below the plot, IF OVERLAPPING SET EVEN LOWER
                xanchor="center",
                x=0.2,
                traceorder="normal",
                font=dict(size=10),
            ),
            margin=dict(b=bottom_margin),
        )
        # Set subplot title font size
        for annotation in fig.layout.annotations:
            annotation.font.size = 8

        # Set all x/y axis title and tick font sizes to 8
        for i in range(1, len(mz_list) + 2):
            xaxis = f"xaxis{i}"
            yaxis = f"yaxis{i}"
            if hasattr(fig.layout, xaxis):
                getattr(fig.layout, xaxis).title.font.size = 8
                getattr(fig.layout, xaxis).tickfont.size = 8
            if hasattr(fig.layout, yaxis):
                getattr(fig.layout, yaxis).title.font.size = 8
                getattr(fig.layout, yaxis).tickfont.size = 8


def build_peak_visualization_figs(plot_data: pd.DataFrame, context: dict) -> dict:
    """
    Build peak visualization figures based on the provided plot data.

    This function processes the plot data to create figures for isotopocule
    visualization using the IsoSpecPy library. It retrieves m/z values for
    formulas and builds figures for each unique formula
    or m/z value. The figures are stored in the context's figure stash for
    efficient reuse.

    :param plot_data: DataFrame containing the plot data grouped by trace and m/z.
    :type plot_data: pd.DataFrame
    :param context: Dictionary containing the callback context, including the dataset.
    :type context: dict
    :return: Dictionary containing FigureWidget objects for each formula or m/z value.
    :rtype: dict
    """

    # Prepare plotters and figures
    if not hasattr(context["dataset"], "get_mz_list_for_target_formula"):
        context["dataset"].extend(PeakVisualizationExtension)
    peak_plotter = PeakVisualizationPlotter(context["dataset"])

    figures = {}
    if "figure_stash" not in context:
        context["figure_stash"] = {}
    for (trace_name, mz_val), merged_dfs in plot_data.items():

        for df in merged_dfs:
            if "target_ion_formula" not in df.columns:
                logger.warning(
                    f"No 'target_ion_formula' column found in DataFrame for trace '{trace_name}'."
                )
                return
            target_ion_formulas = df["target_ion_formula"].unique()
            # Remove None, NaN, and empty strings from target_ion_formulas
            clean_formulas = [
                f
                for f in target_ion_formulas
                if f not in (None, "", float("nan")) and pd.notna(f)
            ]
            if clean_formulas:
                for target_ion_formula in clean_formulas:
                    cache_key = (
                        "isospecpy",
                        str(target_ion_formula),
                        tuple(sorted(df.sample_item_id.unique())),
                    )
                    if cache_key in context["figure_stash"]:
                        fig = context["figure_stash"][cache_key]
                    else:
                        isotopocules_theoretical_df = context[
                            "dataset"
                        ].get_mz_list_for_target_formula(
                            formula=target_ion_formula,
                            isotope_abundance_threshold=0.001,
                        )
                        if isotopocules_theoretical_df.empty:
                            logger.warning(
                                f"No m/z values found for formula '{target_ion_formula}'."
                            )
                            return
                        mz_list = isotopocules_theoretical_df["mz"].tolist()
                        rel_ab_list = isotopocules_theoretical_df[
                            "relative_abundance"
                        ].tolist()
                        label_list = isotopocules_theoretical_df["label"].tolist()
                        dmz_list = np.repeat(0.01, len(mz_list)).tolist()
                        fig = peak_plotter.build_multi_figure(
                            mz_list=mz_list,
                            dmz_list=dmz_list,
                            rel_ab_list=rel_ab_list,
                            label_list=label_list,
                            selected_samples=df.sample_item_id.unique().tolist(),
                            peak_mz_tolerance_ppm=3,
                        )

                        context["figure_stash"][cache_key] = fig
                    figures[
                        f"{str(target_ion_formula)}_{tuple(sorted(df.sample_item_id.unique()))}"
                    ] = fig
            else:
                logger.warning(
                    f"No valid 'target_ion_formula' found in DataFrame for trace '{trace_name}'."
                )
                cache_key = (
                    "isospecpy",
                    f"mz={mz_val:.4f}",
                    tuple(sorted(df.sample_item_id.unique())),
                )
                if cache_key in context["figure_stash"]:
                    fig = context["figure_stash"][cache_key]
                else:
                    fig = peak_plotter.build_multi_figure(
                        mz_list=[mz_val],
                        dmz_list=[0.01],
                        selected_samples=df.sample_item_id.unique().tolist(),
                        peak_mz_tolerance_ppm=3,
                    )
                    context["figure_stash"][cache_key] = fig
                figures[f"mz={mz_val:.4f}"] = fig

    return figures
