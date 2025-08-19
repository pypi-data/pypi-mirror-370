from __future__ import annotations
import re
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ..logging_config import logger  # Import the shared logger


# Helper function
def get_trace_and_initialize_storage(trace_name: str, context: dict) -> go.Trace:
    """
    Locate the trace in the figure and initialize storage for clicked points.

    This helper function searches for a trace in the figure by its name
    and initializes storage for clicked points if not already present.

    :param trace_name: Name of the trace.
    :type trace_name: str
    :param context: Callback context containing the figure and storage.
    :type context: dict
    :return: The located trace.
    :rtype: go.Trace
    """
    trace = next((t for t in context["fig"].data if t.name == trace_name), None)
    if not trace:
        raise ValueError(f"Trace '{trace_name}' not found.")
    # Initialize storage for clicked points if not already present
    if trace_name not in context["clicked_dots_data"]:
        context["clicked_dots_data"][trace_name] = []
        context["marker_points_idx"][trace_name] = []
        marker = trace.marker
        context["original_symbols"][trace_name] = (
            list(marker.symbol)
            if isinstance(marker.symbol, (list, np.ndarray))
            else [marker.symbol] * len(trace.x)
        )
        context["original_colors"][trace_name] = (
            list(marker.color)
            if isinstance(marker.color, (list, np.ndarray))
            else [marker.color] * len(trace.x)
        )
    return trace


# Helper function
def extract_reference_data(clicked_point: dict, context: dict) -> pd.DataFrame:
    """
    Extract and validate reference data for the clicked point.

    This helper function extracts the reference data for a clicked point
    from the context.
    It checks if the x-axis is datetime and localizes it
    if necessary.
    It then filters the reference DataFrame based on the
    clicked point's x and y values.

    :param clicked_point: Dictionary containing clicked point data.
    :type clicked_point: dict
    :param context: Callback context containing the reference DataFrame.
    :type context: dict
    :return: The extracted reference data.
    :rtype: pd.DataFrame
    """

    x_value, y_value = clicked_point["x_value"], clicked_point["y_value"]
    ref_df = pd.DataFrame(context["reference_df"])
    # Handle datetime localization if necessary
    if (context["x_axis"] == "datetime") and (ref_df[context["x_axis"]].dt.tz is None):
        ref_df[context["x_axis"]] = ref_df[context["x_axis"]].dt.tz_localize("UTC")
    # Find matching data points in the reference DataFrame
    selected_data = ref_df[
        (ref_df[context["x_axis"]] == x_value) & (ref_df[context["y_axis"]] == y_value)
    ]
    # Filter out rows where y-axis value is zero to avoid empty traces
    y_axis = context.get("y_axis")
    if y_axis and y_axis in selected_data.columns:
        selected_data = selected_data[selected_data[y_axis] != 0]

    return selected_data


# Helper function
def find_dataset_property_with_columns(
    dataset: object, required_columns: list
) -> pd.DataFrame:
    """
    Find a property in the dataset object that is a DataFrame
    and contains the required columns.

    This helper function iterates through the properties of the dataset
    and checks if any of them is a DataFrame containing all the required columns.
    If a matching DataFrame is found, it is returned.
    If no matching DataFrame is found, a ValueError is raised.

    :param dataset: The dataset object to search.
    :type dataset: object
    :param required_columns: List of required column names.
    :type required_columns: list
    :return: The matching DataFrame.
    :rtype: pd.DataFrame
    :raises ValueError: If no matching DataFrame is found.
    """
    for _, attr in dataset.__dict__.items():
        if isinstance(attr, pd.DataFrame) and all(
            col in attr.columns for col in required_columns
        ):
            return attr
    message = (
        "Dataset does not contain a property with all"
        " required columns: {', '.join(required_columns)}"
    )
    logger.warning(message)
    raise ValueError(message)


# Helper function
def update_marker_symbols_and_colors(
    trace_name: str,
    trace: go.Trace,
    marker_points: dict,
    original_symbols: dict,
    original_colors: dict,
    fig: go.FigureWidget,
) -> None:
    """
    Update the marker symbols and colors for a trace.

    This helper function updates the marker symbols and colors for a trace
    based on the clicked points. It sets the marker symbol to "star" and
    the color to "black" for the clicked points, while restoring the original
    symbols and colors for the rest of the points.
    It uses the original symbols and colors stored in the context.

    :param trace_name: Name of the trace.
    :type trace_name: str
    :param trace: The trace object.
    :type trace: go.Trace
    :param marker_points: Dictionary of marker points.
    :type marker_points: dict
    :param original_symbols: Dictionary of original marker symbols.
    :type original_symbols: dict
    :param original_colors: Dictionary of original marker colors.
    :type original_colors: dict
    :param fig: The Plotly figure widget.
    :type fig: go.FigureWidget
    """
    msymbols = original_symbols[trace_name][:]
    mcolors = original_colors[trace_name][:]
    for idx in marker_points[trace_name]:
        msymbols[idx], mcolors[idx] = "star", "black"
    with fig.batch_update():
        trace.marker.symbol = msymbols
        trace.marker.color = mcolors


# Helper function
def restore_original_markers(
    trace_name: str,
    trace: go.Trace,
    fig: go.FigureWidget,
    original_symbols: dict,
    original_colors: dict,
) -> None:
    """
    Restore the original marker symbols and colors for a trace.

    This helper function sets the marker symbol and color back to their original
    values stored in the context.

    :param trace_name: Name of the trace.
    :type trace_name: str
    :param trace: The trace object.
    :type trace: go.Trace
    :param fig: The Plotly figure widget.
    :type fig: go.FigureWidget
    :param original_symbols: Dictionary of original marker symbols.
    :type original_symbols: dict
    :param original_colors: Dictionary of original marker colors.
    :type original_colors: dict
    """
    with fig.batch_update():
        trace.marker.symbol = original_symbols[trace_name]
        trace.marker.color = original_colors[trace_name]


# Helper function
def merge_clicked_points_with_match_data(
    clicked_points_df: pd.DataFrame, context: dict, required_columns: list
) -> pd.DataFrame:
    """
    Merge the clicked points DataFrame with the match data from the dataset.

    This helper function checks if the clicked points DataFrame contains
    a target compound ID. If it does, it merges the clicked points with the
    match data from the dataset based on the target compound ID and sample item ID.
    If the target compound ID is NaN, it extracts numeric values from the
    trace names and filters the dataset using the peak ± 0.05 range.
    If the "mz" column is not present in the clicked points DataFrame,
    it finds the dataset property with the required columns and merges
    accordingly.
    If none of these conditions are met, it returns the clicked points DataFrame as is.

    :param clicked_points_df: DataFrame containing clicked points.
    :type clicked_points_df: pd.DataFrame
    :param context: Callback context containing the dataset.
    :type context: dict
    :param required_columns: List of required columns for the match data.
    :type required_columns: list
    :return: Merged DataFrame.
    :rtype: pd.DataFrame
    """

    target_compound_id = clicked_points_df.target_compound_id.iloc[0]
    # Handle untarget peaks in target_compound_id
    if pd.isna(target_compound_id):
        # Use trace_names column to extract numeric values
        trace_names = clicked_points_df["trace_name"].fillna("")
        numeric_values = (
            trace_names.apply(
                lambda x: re.findall(r"\b\d+\.\d+\b", x)
            )  # Extract numeric values
            .explode()  # Flatten lists of numbers
            .dropna()
            .astype(float)
        )
        peak = numeric_values.iloc[0]
        # Filter the dataset using the peak ± 0.05 range
        dataset = context["dataset"]
        peak_data = dataset.peaks_matched
        filtered_data = peak_data[
            (peak_data["mz"] >= peak - 0.05) & (peak_data["mz"] <= peak + 0.05)
        ]
        # Merge the filtered data with clicked_points_df
        merged_data = pd.merge(
            clicked_points_df,
            filtered_data,
            on=["sample_item_id"],
            how="inner",
        )
        return drop_duplicate_suffix_columns(merged_data)

    # Handle cases where "mz" is not in clicked_points_df columns
    if "mz" not in clicked_points_df.columns:
        match_data = find_dataset_property_with_columns(
            context["dataset"], required_columns
        )
        merged_data = pd.merge(
            clicked_points_df,
            match_data,
            on=["target_compound_id", "sample_item_id"],
            how="inner",
        )
        return drop_duplicate_suffix_columns(merged_data)

    # Default case: return the clicked_points_df as is
    return clicked_points_df


# Helper function
def drop_duplicate_suffix_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop one of each pair of columns with _x and _y suffixes,
    keeping _x and renaming it to base name.

    This helper function iterates through the columns of the DataFrame
    and checks for pairs of columns with the same base name but different
    suffixes (_x and _y). It drops the _y version and renames the _x version
    to the base name. The function returns the modified DataFrame.
    Useful for cleaning up DataFrames after merging or joining operations.

    :param df: DataFrame to process.
    :type df: pd.DataFrame
    :return: DataFrame with duplicate suffix columns dropped and renamed.
    :rtype: pd.DataFrame
    """
    to_drop = []
    rename = {}
    for col in df.columns:
        if col.endswith("_x") or col.endswith("_y"):
            base = col[:-2]
            if f"{base}_x" in df.columns and f"{base}_y" in df.columns:
                if col.endswith("_y"):
                    to_drop.append(col)
                elif col.endswith("_x"):
                    rename[col] = base
    df = df.drop(columns=to_drop)
    df = df.rename(columns=rename)
    return df


# Helper function
def group_clicked_data_by_trace_and_mz(
    clicked_dots_dict: dict,
    context: dict,
    required_columns: list,
    trace_name: str,
    plot_type: str = None,
) -> dict:
    """
    Groups clicked data by (trace_name, mz) for plotting.

    This function iterates through the clicked data dictionary and
    groups the data by trace name and mz value.
    It checks if the required columns are present in the clicked data
    and merges with match data if necessary.
    It returns a dictionary where the keys are tuples of (plot_type, trace_name, mz)
    and the values are lists of DataFrames containing the clicked data.


    :param clicked_dots_dict: Dictionary containing clicked data.
    :type clicked_dots_dict: dict
    :param context: Callback context containing the dataset.
    :type context: dict
    :param required_columns: List of required columns for the match data.
    :type required_columns: list
    :param trace_name: Name of the trace.
    :type trace_name: str
    :param plot_type: Type of plot (optional).
    :type plot_type: str
    :return: Dictionary of grouped clicked data.
    :rtype: dict
    """
    plot_data = {}
    for selected_data in clicked_dots_dict[trace_name].values():
        if not all(col in selected_data.columns for col in required_columns):
            merged_df = merge_clicked_points_with_match_data(
                selected_data, context, required_columns
            )
        else:
            merged_df = selected_data
        if merged_df.empty or "mz" not in merged_df.columns:
            continue
        for mz_val in merged_df["mz"].unique():
            sub_df = merged_df[merged_df["mz"] == mz_val]
            if plot_type:
                unique_key = (plot_type, trace_name, float(mz_val))
            else:
                unique_key = (trace_name, float(mz_val))
            plot_data.setdefault(unique_key, [])
            # Avoid duplicates
            if not any(df.equals(sub_df) for df in plot_data[unique_key]):
                plot_data[unique_key].append(sub_df)
    return plot_data


# Helper function
def update_clicked_context(
    context: dict, trace_name: str, point_idx: int, selected_data: pd.DataFrame
):
    """
    Update the clicked context with the selected data.

    This function updates the context dictionary with the selected data
    for the clicked point. It checks if the trace name is already present
    in the clicked_dots_data dictionary and initializes it if not.
    It also checks if the clicked point index is already present
    and adds it to the marker_points_idx list if not.
    The selected data is stored in the clicked_dots_data dictionary
    under the trace name and point index.

    :param context: The context dictionary to update.
    :param trace_name: The name of the trace.
    :param point_idx: The index of the clicked point.
    :param selected_data: The selected data to add to the context.
    """

    if trace_name not in context["clicked_dots_data"] or not isinstance(
        context["clicked_dots_data"][trace_name], dict
    ):
        context["clicked_dots_data"][trace_name] = {}
    if trace_name not in context["marker_points_idx"]:
        context["marker_points_idx"][trace_name] = []
    if point_idx not in context["clicked_dots_data"][trace_name]:
        context["clicked_dots_data"][trace_name][point_idx] = selected_data
        context["marker_points_idx"][trace_name].append(point_idx)


# Helper function
def add_traces_with_annotation(
    fig: go.Figure,
    traces: list[go.Trace],
    merged_df: pd.DataFrame,
    row: int = None,
    col: int = None,
) -> None:
    """
    Add traces to the figure with hover annotations.

    This function adds traces to the specified row and column of the figure.
    It also builds a hover annotation string from the merged DataFrame
    and sets it for each trace.
    The hover annotation includes the mz, sample_peak_mz,
    match_mz_error, match_isotope_correlation, and match_score values.
    The function handles cases where these columns may not be present
    in the DataFrame.

    :param fig: The Plotly figure.
    :type fig: go.Figure
    :param traces: List of traces to add to the figure.
    :type traces: list[go.Trace]
    :param merged_df: Merged DataFrame containing the clicked data.
    :type merged_df: pd.DataFrame
    :param row: Row index for the subplot.
    :type row: int
    :param col: Column index for the subplot.
    :type col: int
    :return: None
    """

    annotation_text = build_trace_annotation(merged_df)
    for trace in traces:
        if annotation_text not in trace.hovertemplate:
            trace.hovertemplate = (
                (trace.hovertemplate or "") + annotation_text + "<extra></extra>"
            )
        if row is not None and col is not None:
            fig.add_trace(trace, row=row, col=col)
        else:
            fig.add_trace(trace)


# Helper function
def build_trace_annotation(merged_df: pd.DataFrame) -> str:
    """
    Build a trace annotation string from the merged DataFrame.

    This function constructs a string containing the mz, sample_peak_mz,
    match_mz_error, match_isotope_correlation, and match_score values
    from the merged DataFrame. It checks for the presence of these columns
    and handles cases where they may not be present.
    The resulting string is formatted for display in a Plotly figure hoverbox.

    :param merged_df: Merged DataFrame containing the clicked data.
    :type merged_df: pd.DataFrame
    :return: Formatted annotation string for the trace.
    :rtype: str
    """

    if "sample_peak_mz" in merged_df.columns and pd.notnull(
        merged_df["sample_peak_mz"].iloc[0]
    ):
        peak_mz = merged_df["sample_peak_mz"].iloc[0]
    else:
        peak_mz = merged_df["mz"].iloc[0]
    mz_val_disp = merged_df["mz"].iloc[0] if "mz" in merged_df.columns else "N/A"
    match_mz_error_val = (
        merged_df["match_mz_error"].iloc[0]
        if "match_mz_error" in merged_df.columns
        else "N/A"
    )
    match_isotope_correlation = (
        merged_df["match_isotope_correlation"].iloc[0]
        if "match_isotope_correlation" in merged_df.columns
        else "N/A"
    )
    match_score = (
        merged_df["match_score_isotope"].iloc[0]
        if "match_score_isotope" in merged_df.columns
        else (
            merged_df["matchscore"].iloc[0]
            if "matchscore" in merged_df.columns
            else (
                merged_df["match_score"].iloc[0]
                if "match_score" in merged_df.columns
                else "N/A"
            )
        )
    )

    def _fmt4(val: str | float) -> str:
        """
        Format a value to 4 decimal places.

        This helper function attempts to convert the input value to a float
        and format it to 4 decimal places. If the conversion fails,
        it returns the original value as a string.

        :param val: The value to format.
        :type val: str | float
        :return: Formatted value as a string.
        :rtype: str
        """
        try:
            return f"{float(val):.4f}"
        except (ValueError, TypeError):
            return str(val)

    return (
        f"mz: {_fmt4(mz_val_disp)}<br>"
        f"sample_peak_mz: {_fmt4(peak_mz)}<br>"
        f"match_mz_error: {_fmt4(match_mz_error_val)}<br>"
        f"match_isotope_correlation: {_fmt4(match_isotope_correlation)}<br>"
        f"match_score: {_fmt4(match_score)}<br>"
    )
