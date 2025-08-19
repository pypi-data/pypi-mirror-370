import re
import numpy as np
import pandas as pd
import plotly.validators.scatter.marker as pvm
import plotly.graph_objs as go

# This can be changed to go.Scatter if needed
# better quality for smaller datasets and vector graphics.
# Using Scattergl for better performance with large datasets
DEFAULT_SCATTER_TYPE = go.Scattergl  # or go.Scatter # pylint: disable=invalid-name
from .logging_config import logger  # Import the shared logger


def hover_string(df_columns: pd.Series) -> str:
    """
    Build HoverBox from given DataFrame column names.

    This function generates a hover string template that can be used with a DataFrame
    in Plotly figure building for the 'hovertemplate' attribute. The hover string
    includes the column names and their corresponding values from the DataFrame.

    Example:
        >>> import pandas as pd
        >>> from plot_tools import hover_string
        >>> df = pd.DataFrame({
        ...     'column_1': [1, 2, 3],
        ...     'column_2': ['A', 'B', 'C'],
        ...     'column_3': [10.5, 20.5, 30.5]
        ... })
        >>> hover_template = hover_string(df.columns)
        >>> print(hover_template)
        <b>column 1: %{customdata[0]}</b><br><br>column 2: %{customdata[1]}<br>
        column 3: %{customdata[2]}<br><extra></extra>

    :param df_columns: Columns of the dataframe to be shown in the hover box.
    Columns should be part of the dataframe used as input in plot building.
    :type df_columns: pd.Series
    :type df: pd.DataFrame
    :return: hover string that can be used in plotly-figure building as
    'hovertemplate' attribute.
    :rtype: string
    """
    b = "<b>"
    for i, col in enumerate(df_columns):
        col = re.sub("_", " ", col)
        if i == 0:
            a = str(col + ": %{customdata[" + str(i) + "]}</b><br><br>")
        elif "Names" in col:
            a = str("<br>")
        else:
            a = str(col + ": %{customdata[" + str(i) + "]}<br>")
        b = str(b + a)
    b = b + "<extra></extra>"  # Remove unneed add on box

    return b


def fetch_plotly_symbols() -> list:
    """
    Collets only 'str' type symbols
    from Plotly and orders them.

    :return: list of plotly symbols without numeric or any duplicates.
    :rtype: list
    """

    # Get all marker symbols from Plotly
    all_symbols = pvm.SymbolValidator().values

    # Exclude all symbols containing "star"
    filtered_symbols = [s for s in all_symbols if "star" not in str(s)]

    # Convert all to strings and remove numeric duplicates
    unique_symbols = set(str(s) for s in filtered_symbols)
    named_symbols = [s for s in unique_symbols if not s.isdigit()]

    main_shapes = [
        symbol for symbol in named_symbols if "-" not in symbol
    ]  # Filter out "-open" and "-dot" variants
    sub_shapes = sorted(
        [symbol for symbol in named_symbols if symbol not in main_shapes]
    )  # Variants of main shapes
    all_shapes = main_shapes + sub_shapes
    all_shapes.sort(key=lambda x: x != "circle")  # Circle first

    return all_shapes


def ensure_rgba(color: str | tuple, alpha=0.2) -> str:
    """
    Ensure the color is in an rgba
    format with the specified transparency.

    :param color: The input color in hex, rgb, or rgba format.
    :type color: str/tuple
    :param alpha: The transparency level to apply, defaults to 0.2
    :type alpha: float, optional
    :return: The color in rgba format with the specified transparency.
    :rtype: str
    """
    try:
        logger.debug("Ensuring RGBA format for color: %s with alpha: %f", color, alpha)

        if isinstance(color, str):
            if color.startswith("#"):
                # Convert hex to rgba
                hex_color = color.lstrip("#")
                rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
                rgba = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"
                logger.debug("Converted hex color %s to RGBA: %s", color, rgba)
                return rgba
            elif color.startswith("rgb"):
                # Convert rgb to rgba
                rgba = color.replace("rgb(", "rgba(").replace(")", f", {alpha})")
                logger.debug("Converted RGB color %s to RGBA: %s", color, rgba)
                return rgba
        elif isinstance(color, tuple) and len(color) == 3:
            # Convert tuple (r, g, b) to rgba
            rgba = (
                f"rgba({int(color[0] * 255)}, {int(color[1] * 255)},"
                f" {int(color[2] * 255)}, {alpha})"
            )
            logger.debug("Converted tuple color %s to RGBA: %s", color, rgba)
            return rgba

        # Invalid color format
        raise ValueError("Invalid color format. Please use hex, rgb, or rgba.")
    except Exception as e:
        logger.error("Error in ensure_rgba: %s", e)
        raise


def extract_figure_data(
    fig, x_col="x", y_col="intensity", name_col="name"
) -> pd.DataFrame:
    """
    Extracts data from a Plotly FigureWidget and returns it as a pandas DataFrame.

    This function iterates through the traces in the provided Plotly figure,
    extracts the x and y data, and any custom data associated with the traces.
    It also handles the hovertemplate to dynamically extract column names for
    the custom data.
    This function has been utilized e.g. to extract widgets figure data to property
    dataframes.

    :param fig: The Plotly FigureWidget containing the traces.
    :type fig: go.FigureWidget
    :param x_col: The name of the x-axis column in the resulting DataFrame.
    :type x_col: str
    :param y_col: The name of the y-axis column in the resulting DataFrame.
    :type y_col: str
    :param name_col: The name of the trace name column in the resulting DataFrame.
    :type name_col: str
    :return: A pandas DataFrame containing the extracted data.
    :rtype: pd.DataFrame
    """
    try:
        # Check if the figure has any data
        if not hasattr(fig, "data") or not fig.data:
            logger.warning("The figure has no data.")
            return pd.DataFrame()

        # Extract data from each trace
        data_list = []
        for trace in fig.data:
            if hasattr(trace, "x") and hasattr(trace, "y"):
                trace_data = pd.DataFrame(
                    {
                        x_col: trace.x,
                        y_col: trace.y,
                        name_col: trace.name if hasattr(trace, "name") else None,
                    }
                )
                if hasattr(trace, "customdata") and trace.customdata is not None:
                    cd = np.array(trace.customdata)
                    if cd.ndim == 1:
                        cd = cd.reshape(1, -1)
                    n_cols = cd.shape[1] if cd.shape[0] > 0 else 0
                    # Dynamically extract column names from hovertemplate
                    if hasattr(trace, "hovertemplate") and trace.hovertemplate:
                        matches = re.findall(
                            r"(?i)(?:<b>)?([a-zA-Z0-9 _\-]+):\s*%\{customdata\[\d+\]\}",
                            trace.hovertemplate,
                        )
                    else:
                        # Fallback to generic column names if hovertemplate is not available
                        matches = [f"custom_{i}" for i in range(n_cols)]
                    # Ensure the number of column names matches the number of columns in customdata
                    if n_cols == 0:
                        customdata_df = pd.DataFrame()
                    elif len(matches) != n_cols:
                        custom_columns = [f"custom_{i}" for i in range(n_cols)]
                        customdata_df = pd.DataFrame(cd, columns=custom_columns)
                    else:
                        customdata_df = pd.DataFrame(cd, columns=matches)

                    trace_data = pd.concat([trace_data, customdata_df], axis=1)

                # Drop duplicate columns
                trace_data = trace_data.loc[:, ~trace_data.columns.duplicated()]

                # Drop helper traces (e.g., shadows of aggregated timeseries)
                trace_data = trace_data[
                    ~trace_data[name_col].str.contains(
                        r"__lower_shadow|__upper_shadow|_Trend|_Stem", na=False
                    )
                ]

                if not trace_data.empty:
                    data_list.append(trace_data)

        # Combine all traces into a single DataFrame
        if data_list:
            figure_data = pd.concat(data_list, ignore_index=True)
            logger.debug("Successfully extracted data from the figure.")
        else:
            logger.warning("No valid data found in the figure traces.")
            return pd.DataFrame()

        # Check if the resulting DataFrame is empty
        if figure_data.empty:
            logger.warning("The resulting DataFrame is empty.")
        else:
            logger.info(
                "The resulting DataFrame contains %d rows and %d columns.",
                figure_data.shape[0],
                figure_data.shape[1],
            )

        return figure_data

    except (
        AttributeError,
        ValueError,
        TypeError,
    ) as e:
        logger.error("Error while extracting figure data: %s", e)
        return pd.DataFrame()  # Return an empty DataFrame in case of an error
