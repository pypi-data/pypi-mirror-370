from typing import Literal
import plotly.graph_objects as go
import plotly.express as px
import ipywidgets as wg
import pandas as pd
import numpy as np
from colorcet import glasbey as colorvector
from ..plot_tools import hover_string, ensure_rgba, DEFAULT_SCATTER_TYPE
from ..mascope_data.wrapper import MascopeDataWrapper
from ..click_event_handler.click_event_handler import (
    ClickEventHandler,
)

pd.set_option(
    "future.no_silent_downcasting", True
)  # TODO Annoying warning according fillna for object, seems not to be solved easily
# Started when not using pandera


class TimeSeriesPlotter:
    """
    Class containing functions to build time-series related traces by utlizing
    dataset with TimeSeriesDataExtension -extension."""

    def __init__(self, dataset: MascopeDataWrapper):
        """
        Initialize timeseries extended dataset to self

        :param dataset: MascopeDataWrapper -dataset with
        TimeSeriesDataExtension- extension.
        :type dataset: MascopeDataWrapper
        """
        self.dataset = dataset
        self.hoverbox_columns = [
            "sample_item_id",
            "intensity",
            "intensity_std",  # depending on the data, this might be dropped or replaced with MAD
            "unit",
            "datetime",  # depending on the data, this might be dropped
            "hour_of_day",  # depending on the data, this might be dropped
            "sample_item_name",
            "target_compound_name",
            "target_compound_formula",
            "target_compound_id",
            "match_score",
            "match_score_std",  # depending on the data, this might be dropped or replaced with MAD
            "match_category",
            "sample_item_type",
            "instrument",
        ]
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

    def get_compound_timeseries_trace(
        self,
        target_compound_value: str,
        filter_by: Literal["target_compound_id", "trace_name"] = "target_compound_id",
        trend_line: bool = False,
        lines: bool = True,
    ) -> list[go.Scattergl]:
        """
        Returns list of time-series figure related traces.

        :param target_compound_value: Value to filter by in the specified column.
        :type target_compound_value: str
        :param filter_by: Column to filter by ('target_compound_id' or 'trace_name').
        :type filter_by: Literal["target_compound_id", "trace_name"]
        :param trend_line: Whether to include a trend-line trace, defaults to False.
        :type trend_line: bool, optional
        :param lines: Whether to include lines in the scatter plot, defaults to True.
        :type lines: bool, optional
        :return: List of time-series figure related traces.
        :rtype: list[go.Scattergl]
        """
        # Collect and set data
        round_df = self.dataset.get_compound_timeseries(
            target_compound_value=target_compound_value, filter_by=filter_by
        ).sort_values("datetime")
        compound, compound_order = self._get_compound_name_and_order_number(
            target_compound_value=target_compound_value, filter_by=filter_by
        )
        traces = []
        # Edit HoverBox columns, drop std columns and hour_of_day
        hoverbox_columns = [
            col
            for col in self.hoverbox_columns
            if "_std" not in col and col != "hour_of_day"
        ]
        ts_trace = self.timeseries_trace(
            df_group=round_df,
            group_name=compound,
            col_x="datetime",
            color=colorvector[compound_order],
            hoverbox_columns=hoverbox_columns,
            add_lines=lines,
        )
        traces.append(ts_trace)
        if trend_line:
            trace_trendline = self.build_trend_line(
                df_group=round_df,
                group_name=compound,
                col_x="datetime",
                color=colorvector[compound_order],
            )
            traces.append(trace_trendline)

        return traces

    def get_compound_aggregated_timeseries_trace(
        self,
        target_compound_value: str,
        filter_by: Literal["target_compound_id", "trace_name"] = "target_compound_id",
        freq: Literal["Hourly", "Daily", "Weekly", "Monthly"] = "Daily",
        method: Literal["mean", "median"] = "mean",
        trend_line: bool = False,
        lines: bool = True,
        dispersion_shadows: bool = True,
    ) -> list[go.Scattergl]:
        """
        Returns list of aggregated time-series figure related traces.

        :param target_compound_value: Value to filter by in the specified column.
        :type target_compound_value: str
        :param filter_by: Column to filter by ('target_compound_id' or 'trace_name').
        :type filter_by: Literal["target_compound_id", "trace_name"]
        :param freq: Frequency for aggregation, defaults to "Daily".
        :type freq: Literal["Hourly", "Daily", "Weekly", "Monthly"], optional
        :param method: Aggregation method, defaults to "mean".
        :type method: Literal["mean", "median"], optional
        :param trend_line: Whether to include a trend-line trace, defaults to False.
        :type trend_line: bool, optional
        :param lines: Whether to include lines in the scatter plot, defaults to True.
        :type lines: bool, optional
        :param dispersion_shadows: Whether to include dispersion shadows, defaults to True.
        :type dispersion_shadows: bool, optional
        :return: List of aggregated time-series figure related traces.
        :rtype: list[go.Scattergl]
        """
        # Get aggregated data and sort by datetime
        time_aggregated_df = self.dataset.get_compound_aggregated_timeseries(
            target_compound_value=target_compound_value,
            filter_by=filter_by,
            freq=freq,
            method=method,
        ).sort_values("datetime")
        compound, compound_order = self._get_compound_name_and_order_number(
            target_compound_value=target_compound_value, filter_by=filter_by
        )
        dispersion_col = self._get_dispersion_column(
            aggregation_method=method,
        )
        traces = list()
        # Edit HoverBox columns, drop hour_of_day column
        hoverbox_columns = [
            col for col in self.hoverbox_columns if col != "hour_of_day"
        ]
        # Replace std with mad in hoverbox columns
        if method == "median":
            hoverbox_columns = [
                col.replace("_std", "_mad") if col.endswith("_std") else col
                for col in hoverbox_columns
            ]
        trace_ts = self.timeseries_trace(
            df_group=time_aggregated_df,
            group_name=compound,
            col_x="datetime",
            color=colorvector[compound_order],
            hoverbox_columns=hoverbox_columns,
            add_lines=lines,
        )
        traces.append(trace_ts)
        if dispersion_shadows:
            trace_shadows_upper, trace_shadows_lower = self.build_dispersion_shadows(
                df_group=time_aggregated_df,
                group_name=compound,
                col_x="datetime",
                color=colorvector[compound_order],
                dispersion_col=dispersion_col,
            )
            traces.extend([trace_shadows_upper, trace_shadows_lower])
        if trend_line:
            trace_trendline = self.build_trend_line(
                df_group=time_aggregated_df,
                group_name=compound,
                col_x="datetime",
                color=colorvector[compound_order],
            )
            traces.append(trace_trendline)

        return traces

    def get_compound_diurnal_cycle_trace(
        self,
        target_compound_value: str,
        filter_by: Literal["target_compound_id", "trace_name"] = "target_compound_id",
        method: Literal["mean", "median"] = "mean",
        trend_line: bool = False,
        lines: bool = True,
        dispersion_shadows: bool = True,
    ) -> list[go.Scattergl]:
        """
        Returns list of diurnal cycle related traces.

        :param target_compound_value: Value to filter by in the specified column.
        :type target_compound_value: str
        :param filter_by: Column to filter by ('target_compound_id' or 'trace_name').
        :type filter_by: Literal["target_compound_id", "trace_name"]
        :param method: Aggregation method, defaults to "mean".
        :type method: Literal["mean", "median"], optional
        :param trend_line: Whether to include a trend-line trace, defaults to False.
        :type trend_line: bool, optional
        :param lines: Whether to include lines in the scatter plot, defaults to True.
        :type lines: bool, optional
        :param dispersion_shadows: Whether to include dispersion shadows, defaults to True.
        :type dispersion_shadows: bool, optional
        :return: List of diurnal cycle related traces.
        :rtype: list[go.Scattergl] (DEFAULT_SCATTER_TYPE)
        """
        # Get diurnal cycle data and sort by hour_of_day
        diurnal_cycle_df = self.dataset.get_compound_diurnal_cycle(
            target_compound_value=target_compound_value,
            filter_by=filter_by,
            method=method,
        ).sort_values("hour_of_day")
        compound, compound_order = self._get_compound_name_and_order_number(
            target_compound_value=target_compound_value, filter_by=filter_by
        )
        dispersion_col = self._get_dispersion_column(aggregation_method=method)
        traces = list()
        # Edit HoverBox columns, drop datetime column
        hoverbox_columns = [col for col in self.hoverbox_columns if col != "datetime"]
        # Replace std with mad in hoverbox columns
        if method == "median":
            hoverbox_columns = [
                col.replace("_std", "_mad") if col.endswith("_std") else col
                for col in hoverbox_columns
            ]
        trace_ts = self.timeseries_trace(
            df_group=diurnal_cycle_df,
            group_name=compound,
            col_x="hour_of_day",
            color=colorvector[compound_order],
            hoverbox_columns=hoverbox_columns,
            add_lines=lines,
            diurnal_cycle=True,
        )
        traces.append(trace_ts)
        if dispersion_shadows:
            trace_shadows_upper, trace_shadows_lower = self.build_dispersion_shadows(
                df_group=diurnal_cycle_df,
                group_name=compound,
                col_x="hour_of_day",
                color=colorvector[compound_order],
                dispersion_col=dispersion_col,
            )
            traces.extend([trace_shadows_upper, trace_shadows_lower])
        if trend_line:
            trace_trendline = self.build_trend_line(
                df_group=diurnal_cycle_df,
                group_name=compound,
                col_x="hour_of_day",
                color=colorvector[compound_order],
                diurnal_cycle=True,
            )
            traces.append(trace_trendline)

        return traces

    def _get_compound_name_and_order_number(
        self,
        target_compound_value: str,
        filter_by: Literal["target_compound_id", "trace_name"] = "target_compound_id",
    ) -> list[str, int]:
        """
        Get compound name and alphabetical order number by using
        the specified column and the timeseries dataframe.

        :param target_compound_value: Value to filter by in the specified column.
        :type target_compound_value: str
        :param filter_by: Column to filter by ('target_compound_id' or 'trace_name').
        :type filter_by: Literal["target_compound_id", "trace_name"]
        :return: Compound name and alphabetical order number.
        :rtype: list[str, int]
        """
        # Get compound name
        compound_name = self.dataset.timeseries["trace_name"][
            self.dataset.timeseries[filter_by] == target_compound_value
        ].unique()[0]
        # Get the integer order number for the given target compound value
        compound_order = {
            v: i + 1
            for i, v in enumerate(
                sorted(self.dataset.timeseries[filter_by].dropna().unique())
            )
        }.get(target_compound_value)

        return compound_name, compound_order

    def _get_dispersion_column(
        self, aggregation_method: Literal["mean", "median"]
    ) -> str:
        """
        Set dispersion method
        based on given aggregation method.

        :param aggregation_method: 'mean' or 'median'
        :type aggregation_method: Literal["mean", "median"]
        :raises ValueError: if input is something else than allowed will raise 'ValueError'
        :return: name of the column containing aggregated values;
        name of the column containing dispersion values
        :rtype: str
        """

        if aggregation_method == "mean":
            dispersion = "intensity_std"
        elif aggregation_method == "median":
            dispersion = "intensity_mad"
        else:
            raise ValueError("Time method should be 'mean' or 'median'.")
        return dispersion

    def timeseries_trace(
        self,
        df_group: pd.DataFrame,
        group_name: str,
        hoverbox_columns: list,
        col_x: Literal["datetime", "hour_of_day"] = "datetime",
        color: str = None,
        add_lines: bool = True,
        diurnal_cycle: bool = False,
    ) -> go.Scattergl:
        """
        Builds time-series traces

        :param df_group: dataframe containing at least columns given as input
        Dataframe columns e.g.
        - 'datetime'
        -'intensity'
        :type df_group: pd.DataFrame
        :param group_name: trace-group name
        :type group_name: str
        :param hoverbox_columns: list of columns to be shown in hover-box
        :type hoverbox_columns: list
        :param col_x: x-axis column, defaults to "datetime"
        :type col_x: Literal["datetime", "hour_of_day"] , optional
        :param color: color for trace-group, defaults to None
        :type color: str, optional
        :param add_lines: boolean if line is wanted to be shown in figure
        , defaults to True
        :type add_lines: bool, optional
        :param diurnal_cycle: boolean if diurnal cycle data is used
        , defaults to False
        :type diurnal_cycle: bool, optional
        :return: scatter timeseries traces
        :rtype: go.Scattergl (DEFAULT_SCATTER_TYPE)
        """
        # Replace NaN values based on column data type
        for col_name in df_group.columns:
            if pd.api.types.is_object_dtype(df_group[col_name]):
                df_group[col_name] = df_group[col_name].fillna("UNKNOWN").astype(str)
            else:
                df_group[col_name] = df_group[col_name].fillna(0)
        param_mode = "lines+markers" if add_lines else "markers"  # Set mode
        if not diurnal_cycle:  # Check timezone
            if df_group[col_x].dt.tz is None:
                df_group[col_x] = df_group[col_x].dt.tz_localize("UTC")
        hover_items = hover_string(hoverbox_columns)
        if df_group["intensity"].sum() != 0:
            target_timeseries = DEFAULT_SCATTER_TYPE(
                x=df_group[col_x],
                y=df_group["intensity"],
                mode=param_mode,
                name=str(group_name),
                marker={"symbol": np.repeat("circle", len(df_group))},
                customdata=df_group[hoverbox_columns],
                hovertemplate=hover_items,
                line=dict(color=color) if color else {},
                visible=True,
                legendgroup=group_name,  # Group legend items
            )
            return target_timeseries

    def build_dispersion_shadows(
        self,
        df_group: pd.DataFrame,
        group_name: str,
        color: str,
        col_x: Literal["datetime", "hour_of_day"] = "datetime",
        dispersion_col: str = "intensity_std",
    ) -> tuple[go.Scattergl, go.Scattergl] | tuple[None, None]:
        """
        Builds dispersion (std or mad) shadows for main-trace (mean or median).

        :param df_group: Dataframe containing aggregated values and corresponding
        dispersion values for building dispersion traces. Dataframe e.g. columns:
        - 'datetime',
        - 'intensity',
        - 'intensity_std'
        :type df_group: pd.DataFrame
        :param group_name: trace-group name
        :type group_name: str
        :param color: color
        :type color: str
        :param col_x: x-axis values, defaults to "datetime"
        :type col_x: Literal["datetime", "hour_of_day"], optional
        :param dispersion_col: dispersion values ('intensity_std' if 'intensity_mean';
        'intensity_mad' if 'intensity_median' ), defaults to "intensity_std"
        :type dispersion_col: str, optional
        :return: scatter upper and lower bound shadow traces
        :rtype: list[go.Scattergl, go.Scattergl] (DEFAULT_SCATTER_TYPE)
        """

        # Replace NaN values based on column data type
        for col_name in df_group.columns:
            if pd.api.types.is_object_dtype(df_group[col_name]):
                df_group[col_name] = df_group[col_name].fillna("UNKNOWN").astype(str)
            else:
                df_group[col_name] = df_group[col_name].fillna(0)
        # Set names and colors
        upper_shadow_name = f"{group_name}__upper_shadow"
        lower_shadow_name = f"{group_name}__lower_shadow"
        fill_rgba = ensure_rgba(color)

        if df_group["intensity"].sum() != 0:
            df_group["upper_bound"] = df_group["intensity"] + df_group[dispersion_col]
            df_group["lower_bound"] = df_group["intensity"] - df_group[dispersion_col]
            # Create the upper bound (mean(or median) + dispersion), filling to the lower trace
            upper_bound = DEFAULT_SCATTER_TYPE(
                x=df_group[col_x],
                y=df_group["upper_bound"],  # Upper bound
                mode="lines",
                line=dict(color=color, width=0),  # No line, just the shadow
                name=upper_shadow_name,
                fill=None,  # Do not fill this trace
                hoverinfo="skip",  # Disable hover info for the shadow
                showlegend=False,  # Hide shadow trace from legend
                legendgroup=group_name,  # Link with main trace
                visible=True,
            )
            # Create the lower bound (mean(or median) - dispersion), filling to the upper trace
            lower_bound = DEFAULT_SCATTER_TYPE(
                x=df_group[col_x],
                y=df_group["intensity"] - df_group[dispersion_col],  # Lower bound
                mode="lines",
                line=dict(color=color, width=0),  # No line, just the shadow
                name=lower_shadow_name,  # Name for identification
                fill="tonexty",  # Fill between this trace and the previous
                fillcolor=fill_rgba,  # Use transparent version of the original color
                hoverinfo="skip",  # Disable hover info for the shadow
                showlegend=False,  # Hide shadow trace from legend
                legendgroup=group_name,  # Link with main trace
                visible=True,
            )
            return upper_bound, lower_bound
        return None, None

    def build_trend_line(
        self,
        df_group: pd.DataFrame,
        group_name: str,
        col_x: Literal["datetime", "hour_of_day"] = "datetime",
        color: str = None,
        diurnal_cycle: bool = False,
    ) -> go.Scattergl:
        """
        Builds a trend line trace.

        :param df_group: dataframe containing at least columns given as input
        Dataframe columns e.g.
        - 'datetime'
        -'intensity'
        :type df_group: pd.DataFrame
        :param group_name: trace-group name
        :type group_name: str
        :param col_x: x-axis value column name, defaults to "datetime"
        :type col_x: Literal["datetime", "hour_of_day"], optional
        :param color: color for trace-group, defaults to None
        :type color: str, optional
        :param diurnal_cycle: boolean if diurnal cycle data is given
        , defaults to False
        :type diurnal_cycle: bool, optional
        :return: trend-line scatter trace
        :rtype: go.Scattergl (DEFAULT_SCATTER_TYPE)
        """

        # Replace NaN values based on column data type
        for col_name in df_group.columns:
            if pd.api.types.is_object_dtype(df_group[col_name]):
                df_group[col_name] = df_group[col_name].fillna("UNKNOWN").astype(str)
            else:
                df_group[col_name] = df_group[col_name].fillna(0)
        if df_group["intensity"].sum() != 0:
            if not diurnal_cycle:  # Check timezone
                df_group[col_x] = pd.to_datetime(df_group[col_x])
                if df_group[col_x].dt.tz is None:
                    df_group[col_x] = df_group[col_x].dt.tz_localize("UTC")
            # Create a help figure to get the trend line
            help_fig = px.scatter(
                df_group, x=df_group[col_x], y=df_group["intensity"], trendline="lowess"
            )
            x_trend = help_fig["data"][1]["x"]  # Get x-values for trend line
            y_trend = help_fig["data"][1]["y"]  # Get y-values for trend line
            # Create trend line trace
            trend_line_trace = DEFAULT_SCATTER_TYPE(
                x=x_trend,
                y=y_trend,
                name=f"{group_name}_Trend",
                line=dict(width=2, dash="dash", color=color),
                visible=True,
            )

            return trend_line_trace

    def build_layout(
        self,
        diurnal_cycle: bool = False,
    ) -> dict:
        """
        Build the layout of the figure and return layout.

        :param fig: plotly-figure containing traces
        :type fig: go.FigureWidget
        :param diurnal_cycle: whether to use diurnal cycle for x-axis
        :type diurnal_cycle: bool
        :return: layout dictionary to be applied to the figure
        :rtype: dict
        """

        intensity_unit = getattr(self.dataset, "intensity_unit", None)
        yaxis_title = (
            f"Signal intensity ({intensity_unit})"
            if intensity_unit
            else "Signal intensity"
        )
        layout_dict = {
            "showlegend": True,
            "xaxis": {
                "showspikes": True,
                "spikecolor": "black",
                "showline": True,
                "linewidth": 1,
                "linecolor": "black",
                "ticks": "outside",
                "tickwidth": 1,
                "tickcolor": "black",
                "ticklen": 5,
                "rangeslider_visible": True,
                "rangeselector": {
                    "buttons": [
                        {
                            "count": 1,
                            "label": "1d",
                            "step": "day",
                            "stepmode": "backward",
                        },
                        {
                            "count": 6,
                            "label": "1h",
                            "step": "hour",
                            "stepmode": "backward",
                        },
                        {
                            "count": 1,
                            "label": "6h",
                            "step": "hour",
                            "stepmode": "backward",
                        },
                        {
                            "count": 1,
                            "label": "DTD",
                            "step": "day",
                            "stepmode": "todate",
                        },
                        {"step": "all"},
                    ]
                },
            },
            "yaxis": {
                "showspikes": True,
                "spikecolor": "black",
                "showline": True,
                "linewidth": 1,
                "linecolor": "black",
                "ticks": "outside",
                "tickwidth": 1,
                "tickcolor": "black",
                "ticklen": 5,
                "title_text": yaxis_title,
            },
        }
        if diurnal_cycle:  # Diurnal cycle specific layout properties
            layout_dict["xaxis"].update(
                tickmode="array",
                tickvals=[0, 3, 6, 9, 12, 15, 18, 21, 24],
                ticktext=[
                    "00:00",
                    "03:00",
                    "06:00",
                    "09:00",
                    "12:00",
                    "15:00",
                    "18:00",
                    "21:00",
                    "24:00",
                ],
            )

        return layout_dict

    def base_timeseries_figure(
        self,
    ) -> go.FigureWidget:
        """
        Build base FigureWidget and setup layout

        :return: figurewidget which is ready for adding traces
        :rtype: go.FigureWidget
        """

        fig = go.FigureWidget()
        layout = self.build_layout()
        fig.update_layout(layout)

        return fig

    def attach_click_callback(
        self,
        fig: go.FigureWidget,
        callback_function: callable,
        click_output: wg.Output,
        reference_df: pd.DataFrame,
        x_axis: str,
        y_axis: str,
    ) -> None:
        """
        Attach a callback function to the click event handler.

        :param fig: FigureWidget containing traces with marker-points.
        :type fig: go.FigureWidget
        :param callback_function: Callback function to execute
        when a point is clicked.
        :type callback_function: callable
        :param click_output: Output widget for displaying outputs.
        :type click_output: wg.Output
        :param reference_df: Reference DataFrame containing data points.
        :type reference_df: pd.DataFrame
        :param x_axis: x-axis column name.
        :type x_axis: str
        :param y_axis: y-axis column name.
        :type y_axis: str
        """

        self.click_event_handler = ClickEventHandler(
            fig=fig,
            out=click_output,
            dataset=self.dataset,
            callback_func=callback_function,
            reference_df=reference_df,
            x_axis=x_axis,
            y_axis=y_axis,
        )
        for trace in fig.data:
            trace.on_click(self.click_event_handler.click_callback, append=False)
