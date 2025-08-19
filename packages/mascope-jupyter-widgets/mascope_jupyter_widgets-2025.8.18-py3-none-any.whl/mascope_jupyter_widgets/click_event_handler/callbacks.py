import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from colorcet import glasbey as colorvector

from .helpers import (
    add_traces_with_annotation,
    get_trace_and_initialize_storage,
    group_clicked_data_by_trace_and_mz,
    extract_reference_data,
    restore_original_markers,
    update_clicked_context,
    update_marker_symbols_and_colors,
)
from ..spectrum.plots import SpectrumPlotter, collect_spectrum_traces
from ..sample_timeseries.plots import (
    SampleTimeSeriesPlotter,
    collect_sample_timeseries_traces,
)
from ..peak_visualization.plots import build_peak_visualization_figs
from ..logging_config import logger  # Import the shared logger


# Callback function
def display_reference_table(
    clicked_point: dict, callback_context: dict, update_markers: bool = True
) -> pd.DataFrame:
    """
    Returns the reference table for the clicked point.

    This function processes the clicked point data and updates the
    reference table accordingly. It also updates the markers on the clicked
    point in the plot if specified. The reference table contains information
    about the clicked point, including its trace name and other relevant
    data.

    :param clicked_point: Dictionary containing clicked point data.
    :rtype clicked_point: dict
    :param callback_context: Dictionary containing the callback context.
    :rtype callback_context: dict
    :param update_markers: Flag to indicate whether to update markers or not.
    :type update_markers: bool
    :return: DataFrame containing the reference table for the clicked point.
    :rtype: pd.DataFrame
    """
    # 1. Extract and validate input data
    context = callback_context
    trace_name = clicked_point["trace_name"]
    selected_data = extract_reference_data(clicked_point, context)
    try:
        trace = get_trace_and_initialize_storage(trace_name, context)
    except ValueError:
        print(f"Trace '{trace_name}' not found.")
        logger.debug(f"Trace '{trace_name}' not found in the dataset.")
        return
    if selected_data.empty:
        logger.warning(
            f"No matching data for trace '{trace_name}' at "
            f"x={clicked_point.get('x_value')}, y={clicked_point.get('y_value')}."
        )
        if update_markers:
            restore_original_markers(
                trace_name,
                trace,
                context["fig"],
                context["original_symbols"],
                context["original_colors"],
            )
        return
    # 2. Update context with clicked data
    context["clicked_dots_data"][trace_name].append(selected_data)
    context["marker_points_idx"][trace_name].append(clicked_point["point_index"])
    if update_markers:
        update_marker_symbols_and_colors(
            trace_name,
            trace,
            context["marker_points_idx"],
            context["original_symbols"],
            context["original_colors"],
            context["fig"],
        )
    # 3. Display part of the reference table
    clicked_points_compound_trace_df = pd.concat(
        context["clicked_dots_data"][trace_name], ignore_index=True
    ).drop_duplicates()

    return clicked_points_compound_trace_df


# Callback function
def display_spectrum(
    clicked_point: dict, callback_context: dict, update_markers: bool = True
) -> go.FigureWidget:
    """
    Process and return spectrum traces from clicked dot.

    This function processes the clicked point data and builds the
    corresponding spectrum traces.
    It also updates the markers on the clicked point in the plot
    if specified.

    :param clicked_point: Dictionary containing clicked point data.
    :type clicked_point: dict
    :param callback_context: Dictionary containing the callback context.
    :type callback_context: dict
    :param update_markers: Flag to indicate whether to update markers or not.
    :type update_markers: bool
    :return: FigureWidget containing the spectrum traces.
    :rtype: go.FigureWidget
    """
    # 1. Extract and validate input data
    context = callback_context
    trace_name = clicked_point["trace_name"]
    point_idx = clicked_point["point_index"]
    selected_data = extract_reference_data(clicked_point, context)
    if not hasattr(context["dataset"], "get_spectrum_data"):
        raise AttributeError(
            "The dataset object does not have the required method 'get_spectrum_data'. "
            "Please ensure the dataset is extended with SpectrumDataExtension."
        )
    try:
        trace = get_trace_and_initialize_storage(trace_name, context)
    except ValueError:
        print(f"Trace '{trace_name}' not found.")
        logger.debug(f"Trace '{trace_name}' not found in the dataset.")
        return
    if selected_data.empty:
        logger.warning(
            f"No matching data for trace '{trace_name}' at "
            f"x={clicked_point.get('x_value')}, y={clicked_point.get('y_value')}."
        )
        if update_markers:
            restore_original_markers(
                trace_name,
                trace,
                context["fig"],
                context["original_symbols"],
                context["original_colors"],
            )
        return

    # 2. Update context with clicked data
    update_clicked_context(context, trace_name, point_idx, selected_data)
    if update_markers:
        update_marker_symbols_and_colors(
            trace_name,
            trace,
            context["marker_points_idx"],
            context["original_symbols"],
            context["original_colors"],
            context["fig"],
        )

    # 3. Prepare plotter and color map
    spectrum_plotter = SpectrumPlotter(dataset=context["dataset"])
    base_fig = spectrum_plotter.base_spectrum_figure()
    required_columns = ["target_compound_id", "sample_item_id", "mz"]
    sample_item_ids = sorted(
        context["dataset"].match_samples["sample_item_id"].unique()
    )
    color_map = {
        sample_item_id: colorvector[i % len(colorvector)]
        for i, sample_item_id in enumerate(sample_item_ids)
    }

    # 4. Group plot data
    plot_data = group_clicked_data_by_trace_and_mz(
        context["clicked_dots_data"],
        context,
        required_columns,
        trace_name,
        plot_type="spectrum",
    )
    # 5. Prepare subplots: one column per unique mz
    mz_vals = sorted({mz_val for (_, _, mz_val) in plot_data})
    n_mz = len(mz_vals)
    specs = [[{} for _ in range(n_mz)]]
    spectrum_fig = make_subplots(
        rows=1,
        cols=n_mz,
        shared_xaxes=False,
        horizontal_spacing=0.08,
        specs=specs,
        subplot_titles=[f"Spectrum mz={mz:.4f}" for mz in mz_vals],
    )

    # 6. Copy axis titles from base figure
    for col_idx in range(1, n_mz + 1):
        spectrum_fig.update_xaxes(
            title_text=base_fig.layout.xaxis.title.text, row=1, col=col_idx
        )
        if col_idx == 1:
            spectrum_fig.update_yaxes(
                title_text=base_fig.layout.yaxis.title.text, row=1, col=col_idx
            )
        else:
            spectrum_fig.update_yaxes(title_text=None, row=1, col=col_idx)

    # 7. Add spectrum traces to each subplot
    for col_idx, mz_val in enumerate(mz_vals, start=1):
        for (plot_type, trace_name, mz), merged_dfs in plot_data.items():
            if plot_type == "spectrum" and mz == mz_val:
                for merged_df in merged_dfs:
                    spectrum_traces = collect_spectrum_traces(
                        merged_df,
                        trace_name,
                        mz,
                        context,
                        spectrum_plotter,
                        with_suffix=False,
                        color_map=color_map,
                    )
                    spectrum_traces = [t for t in spectrum_traces if t is not None]
                    add_traces_with_annotation(
                        spectrum_fig, spectrum_traces, merged_df, row=1, col=col_idx
                    )

    # 8. Update layout and return go.FigureWidget
    spectrum_fig.update_layout(
        height=400,
        showlegend=True,
    )

    return go.FigureWidget(spectrum_fig)


# Callback function
def display_sample_timeseries(
    clicked_point: dict, callback_context: dict, update_markers: bool = True
) -> pd.DataFrame:
    """
    Process and returns sample timeseries traces from clicked dot.

    This function processes the clicked point data and builds the
    corresponding sample timeseries traces.
    It also updates the markers on the clicked point in the plot
    if specified.

    :param clicked_point: Dictionary containing clicked point data.
    :type clicked_point: dict
    :param callback_context: Dictionary containing the callback context.
    :type callback_context: dict
    :param update_markers: Flag to indicate whether to update markers or not.
    :type update_markers: bool
    :return: FigureWidget containing the sample timeseries traces.
    :rtype: go.FigureWidget
    """

    # 1. Extract and validate input data
    context = callback_context
    trace_name = clicked_point["trace_name"]
    point_idx = clicked_point["point_index"]
    selected_data = extract_reference_data(clicked_point, context)
    if not hasattr(context["dataset"], "get_sample_peak_timeseries"):
        raise AttributeError(
            "The dataset object does not have the required method 'get_sample_peak_timeseries'. "
            "Please ensure the dataset is extended with SampleTimeSeriesExtension."
        )
    try:
        trace = get_trace_and_initialize_storage(trace_name, context)
    except ValueError:
        print(f"Trace '{trace_name}' not found.")
        logger.debug(f"Trace '{trace_name}' not found in the dataset.")
        return
    if selected_data.empty:
        logger.warning(
            f"No matching data for trace '{trace_name}' at "
            f"x={clicked_point.get('x_value')}, y={clicked_point.get('y_value')}."
        )
        if update_markers:
            restore_original_markers(
                trace_name,
                trace,
                context["fig"],
                context["original_symbols"],
                context["original_colors"],
            )
        return

    # 2. Update context with clicked data
    update_clicked_context(context, trace_name, point_idx, selected_data)
    if update_markers:
        update_marker_symbols_and_colors(
            trace_name,
            trace,
            context["marker_points_idx"],
            context["original_symbols"],
            context["original_colors"],
            context["fig"],
        )

    # 3. Prepare plotter and figure
    sample_timeseries_plotter = SampleTimeSeriesPlotter(dataset=context["dataset"])
    timeseries_fig = sample_timeseries_plotter.base_timeseries_figure()
    required_columns = ["sample_peak_mz", "mz", "sample_item_id"]

    # 4. Group plot data
    plot_data = group_clicked_data_by_trace_and_mz(
        context["clicked_dots_data"],
        context,
        required_columns,
        trace_name,
        plot_type="timeseries",
    )
    # 5. Add sample timeseries traces with annotation
    for key, merged_dfs in plot_data.items():
        _, trace_name, mz_val = key
        for merged_df in merged_dfs:
            timeseries_traces = collect_sample_timeseries_traces(
                merged_df, trace_name, mz_val, context, sample_timeseries_plotter
            )
            timeseries_traces = [t for t in timeseries_traces if t is not None]
            add_traces_with_annotation(timeseries_fig, timeseries_traces, merged_df)
    # 6. Update layout and return
    timeseries_fig.update_layout(title="Sample Timeseries")

    return timeseries_fig


# Callback function
def display_spectrum_and_timeseries_target_database(
    clicked_point: dict, callback_context: dict, update_markers: bool = True
) -> tuple[go.FigureWidget, str]:
    """
    Process and return spectrum and sample timeseries traces from clicked dot.

    This function processes the clicked point data and builds the
    corresponding spectrum and sample timeseries traces.
    It also updates the markers on the clicked point in the plot
    if specified.

    :param clicked_point: Dictionary containing clicked point data.
    :type clicked_point: dict
    :param callback_context: Dictionary containing the callback context.
    :type callback_context: dict
    :param update_markers: Flag to indicate whether to update markers or not.
    :type update_markers: bool
    :return: Tuple containing FigureWidget with spectrum and sample timeseries traces,
    and combined annotation text.
    :rtype: tuple[go.FigureWidget, str]
    """

    # 1. Extrract and validate input data
    context = callback_context
    trace_name = clicked_point["trace_name"]
    point_idx = clicked_point["point_index"]
    selected_data = extract_reference_data(clicked_point, context)
    if not hasattr(context["dataset"], "get_spectrum_data"):
        raise AttributeError(
            "The dataset object does not have the required method 'get_spectrum_data'. "
            "Please ensure the dataset is extended with SpectrumDataExtension."
        )
    try:
        trace = get_trace_and_initialize_storage(trace_name, context)
    except ValueError:
        print(f"Trace '{trace_name}' not found.")
        logger.debug(f"Trace '{trace_name}' not found in the dataset.")
        return
    if selected_data.empty:
        logger.warning(
            f"No matching data for trace '{trace_name}' at "
            f"x={clicked_point.get('x_value')}, y={clicked_point.get('y_value')}."
        )
        if update_markers:
            restore_original_markers(
                trace_name,
                trace,
                context["fig"],
                context["original_symbols"],
                context["original_colors"],
            )
        return

    # 2. Update context with clicked data
    update_clicked_context(context, trace_name, point_idx, selected_data)
    if update_markers:
        update_marker_symbols_and_colors(
            trace_name,
            trace,
            context["marker_points_idx"],
            context["original_symbols"],
            context["original_colors"],
            context["fig"],
        )

    # 3. Prepare plotters and figures
    spectrum_plotter = SpectrumPlotter(dataset=context["dataset"])
    spectrum_fig = spectrum_plotter.base_spectrum_figure()
    sample_timeseries_plotter = SampleTimeSeriesPlotter(dataset=context["dataset"])
    timeseries_fig = sample_timeseries_plotter.base_timeseries_figure()
    required_columns = ["target_compound_id", "sample_item_id", "sample_peak_mz", "mz"]
    sample_item_ids = sorted(
        context["dataset"].match_samples["sample_item_id"].unique()
    )
    color_map_sid = {
        sample_item_id: colorvector[i % len(colorvector)]
        for i, sample_item_id in enumerate(sample_item_ids)
    }

    # 4. Group plot data
    plot_data_spectrum = group_clicked_data_by_trace_and_mz(
        context["clicked_dots_data"],
        context,
        required_columns,
        trace_name,
        plot_type="spectrum",
    )
    plot_data_ts = group_clicked_data_by_trace_and_mz(
        context["clicked_dots_data"],
        context,
        required_columns,
        trace_name,
        plot_type="timeseries",
    )
    # 5. Create subplot figure
    mz_vals = sorted({mz_val for (_, _, mz_val) in plot_data_spectrum})
    n_mz = len(mz_vals)
    specs = [
        [{} for _ in range(n_mz)],
        [{"colspan": n_mz, "type": "xy"}] + [None] * (n_mz - 1),
    ]
    fig = make_subplots(
        rows=2,
        cols=n_mz,
        shared_xaxes=False,
        vertical_spacing=0.1,
        specs=specs,
        row_heights=[0.5, 0.5],
    )
    for col_idx in range(1, n_mz + 1):
        # X axis title for all spectrum subplots
        fig.update_xaxes(
            title_text=spectrum_fig.layout.xaxis.title.text, row=1, col=col_idx
        )
        # Y axis title only for the first spectrum subplot
        if col_idx == 1:
            fig.update_yaxes(
                title_text=spectrum_fig.layout.yaxis.title.text, row=1, col=col_idx
            )
        else:
            fig.update_yaxes(title_text=None, row=1, col=col_idx)
    fig.update_xaxes(title_text=timeseries_fig.layout.xaxis.title.text, row=2, col=1)
    fig.update_yaxes(title_text=timeseries_fig.layout.yaxis.title.text, row=2, col=1)

    # 6. Add spectrum traces
    for col_idx, mz_val in enumerate(mz_vals, start=1):
        for (plot_type, trace_name, mz), merged_dfs in plot_data_spectrum.items():
            if plot_type == "spectrum" and mz == mz_val:
                for merged_df in merged_dfs:
                    spectrum_traces = collect_spectrum_traces(
                        merged_df,
                        trace_name,
                        mz,
                        context,
                        spectrum_plotter,
                        with_suffix=True,
                        color_map=color_map_sid,
                    )
                    spectrum_traces = [t for t in spectrum_traces if t is not None]
                    add_traces_with_annotation(
                        fig, spectrum_traces, merged_df, row=1, col=col_idx
                    )

    # 7. Add timeseries traces
    for (plot_type, trace_name, mz_val), merged_dfs in plot_data_ts.items():
        if plot_type != "timeseries":
            continue
        for merged_df in merged_dfs:
            timeseries_traces = collect_sample_timeseries_traces(
                merged_df,
                trace_name,
                mz_val,
                context,
                sample_timeseries_plotter,
                with_suffix=True,
                color_map=color_map_sid,
            )
            timeseries_traces = [t for t in timeseries_traces if t is not None]
            add_traces_with_annotation(fig, timeseries_traces, merged_df, row=2, col=1)
    # 8. Update layout
    fig.update_layout(
        height=800,
        showlegend=True,
        title_text="Spectrum and Sample Timeseries",
    )
    return go.FigureWidget(fig)


# Callback function
def display_spectrum_and_timeseries_isospecpy(
    clicked_point: dict, callback_context: dict, update_markers: bool = True
) -> dict:
    """
    Process and return spectrum and isotopocule traces from clicked dot.

    This function processes the clicked point data and builds the
    corresponding spectrum and isotopocule traces.
    It also updates the markers on the clicked point in the plot
    if specified.

    :param clicked_point: Dictionary containing clicked point data.
    :type clicked_point: dict
    :param callback_context: Dictionary containing the callback context.
    :type callback_context: dict
    :param update_markers: Flag to indicate whether to update markers or not.
    :type update_markers: bool
    :return: Dictionary containing FigureWidget with isotopocule traces
    and their corresponding target ion formulas.
    :rtype: dict
    """

    # 1. Extrract and validate input data
    context = callback_context
    trace_name = clicked_point["trace_name"]
    point_idx = clicked_point["point_index"]
    selected_data = extract_reference_data(clicked_point, context)
    if not hasattr(context["dataset"], "get_spectrum_data"):
        raise AttributeError(
            "The dataset object does not have the required method 'get_spectrum_data'. "
            "Please ensure the dataset is extended with SpectrumDataExtension."
        )
    try:
        trace = get_trace_and_initialize_storage(trace_name, context)
    except ValueError:
        print(f"Trace '{trace_name}' not found.")
        logger.debug(f"Trace '{trace_name}' not found in the dataset.")
        return
    if selected_data.empty:
        logger.warning(
            f"No matching data for trace '{trace_name}' at "
            f"x={clicked_point.get('x_value')}, y={clicked_point.get('y_value')}."
        )
        if update_markers:
            restore_original_markers(
                trace_name,
                trace,
                context["fig"],
                context["original_symbols"],
                context["original_colors"],
            )
        return

    # 2. Update context with clicked data
    update_clicked_context(context, trace_name, point_idx, selected_data)
    if update_markers:
        update_marker_symbols_and_colors(
            trace_name,
            trace,
            context["marker_points_idx"],
            context["original_symbols"],
            context["original_colors"],
            context["fig"],
        )

    required_columns = [
        "target_compound_id",
        "target_ion_formula",
        "sample_item_id",
        "sample_peak_mz",
        "mz",
    ]
    # 3. Group plot data
    plot_data = group_clicked_data_by_trace_and_mz(
        context["clicked_dots_data"],
        context,
        required_columns,
        trace_name,
    )

    # 4. Create subplot figure
    spectrum_figs = build_peak_visualization_figs(plot_data, callback_context)

    return spectrum_figs
