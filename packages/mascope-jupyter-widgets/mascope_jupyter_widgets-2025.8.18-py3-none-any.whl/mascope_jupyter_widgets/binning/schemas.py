import pandera as pa
import pandas as pd
import numpy as np

# Import global schemas
from ..mascope_data.schemas import (
    peaks_matched_schema,
    set_unique_index,
    DEFAULT_SCHEMA_PARAMS,
)

DEFAULT_SCHEMA_PARAMS_MATRIX = {
    "strict": False,  # Allow non-strict validation to work with multi-index columns
    "coerce": True,  # Coerce data types if needed
}


# pa.Parser(s)
## Dataframe-level parser
def add_weighted_mz_mean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pandera parser function to calculate the weighted mean for each mz_group
    and add it as a new column to the DataFrame.
    """

    # Define a function to calculate the weighted mean
    def calculate_weighted_mean(group: pd.DataFrame) -> float:
        return np.average(group["mz"], weights=group["intensity"])

    # Group by mz_group and calculate the intensity weighted mean for mz
    weighted_means_bin = (
        df.groupby("mz_group", group_keys=True)
        .apply(calculate_weighted_mean)
        .reset_index(name="mz_weighted_mean")
    )
    # Round the weighted mean to 4 decimal places
    weighted_means_bin["mz_weighted_mean"] = weighted_means_bin[
        "mz_weighted_mean"
    ].round(4)

    # Merge the weighted means back into the original DataFrame
    df = df.merge(weighted_means_bin, on="mz_group", how="left")

    return df


## Dataframe-level parser
def add_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pandera parser function to calculate
    statistics (mean, std, cov) for mz, intensity, and norm_intensity.
    Adds the calculated columns to the DataFrame.
    """
    # Calculate mz statistics
    df["mz_mean"] = df.groupby("mz_group")["mz"].transform("mean")
    df["mz_std"] = df.groupby("mz_group")["mz"].transform("std")
    df["mz_cov"] = df["mz_std"] / df["mz_mean"]
    # Calculate intensity statistics
    df["intensity_mean"] = df.groupby("mz_group")["intensity"].transform("mean")
    df["intensity_std"] = df.groupby("mz_group")["intensity"].transform("std")
    df["intensity_cov"] = df["intensity_std"] / df["intensity_mean"]
    # Calculate norm_intensity statistics
    df["norm_intensity_mean"] = df.groupby("mz_group")["norm_intensity"].transform(
        "mean"
    )
    df["norm_intensity_std"] = df.groupby("mz_group")["norm_intensity"].transform("std")
    df["norm_intensity_cov"] = df["norm_intensity_std"] / df["norm_intensity_mean"]

    return df


# Peaks DF Schema
peaks_grouped_schema = pa.DataFrameSchema(
    columns={
        **peaks_matched_schema.columns,
        "mz_group": pa.Column(int, nullable=False, coerce=True),
        "binning_method": pa.Column(str, nullable=False, coerce=True),
        "dynamic_rtol": pa.Column(float, nullable=False, coerce=True, required=False),
        "mz_weighted_mean": pa.Column(float, nullable=False, coerce=True),
        "mz_mean": pa.Column(float, nullable=False, coerce=True),
        "mz_std": pa.Column(float, nullable=True, coerce=True),
        "mz_cov": pa.Column(float, nullable=True, coerce=True),
        "intensity_mean": pa.Column(float, nullable=False, coerce=True),
        "intensity_std": pa.Column(float, nullable=True, coerce=True),
        "intensity_cov": pa.Column(float, nullable=True, coerce=True),
        "norm_intensity_mean": pa.Column(float, nullable=False, coerce=True),
        "norm_intensity_std": pa.Column(float, nullable=True, coerce=True),
        "norm_intensity_cov": pa.Column(float, nullable=True, coerce=True),
    },
    **DEFAULT_SCHEMA_PARAMS,
    unique=[],
    index=pa.Index(
        pa.String,
        unique=True,
    ),
    checks=[],
    parsers=[
        pa.Parser(add_weighted_mz_mean),
        pa.Parser(add_statistics),
        pa.Parser(set_unique_index),
    ],
    name="Grouped Peak data combined with match data",
)


# Matrix schemas
def create_matrix_schema(name: str, allow_nan: bool = True) -> pa.DataFrameSchema:
    """
    Helper function to create a binning matrix schema
    with a given name and NaN allowance.

    :param name: The name of the schema.
    :type name: str
    :param allow_nan: Whether to allow NaN values in the MultiIndex levels.
    :type allow_nan: bool
    :return: A Pandera DataFrameSchema for the matrix.
    :rtype: pa.DataFrameSchema
    """
    return pa.DataFrameSchema(
        columns={},  # Leave columns empty since MultiIndex columns are validated separately
        index=pa.Index(
            float, unique=True, name="mz_weighted_mean"
        ),  # Ensure index is unique and of type float
        checks=[
            # Check that columns are a MultiIndex
            pa.Check(
                lambda df: isinstance(df.columns, pd.MultiIndex),
                error="Columns must be a MultiIndex.",
            ),
            # Check that the MultiIndex has exactly two levels
            pa.Check(
                lambda df: df.columns.nlevels == 2,
                error="MultiIndex must have exactly two levels.",
            ),
            # Check that the MultiIndex level names are correct
            pa.Check(
                lambda df: set(df.columns.names) == {"datetime", "sample_item_id"},
                error="MultiIndex column levels must be 'datetime' and 'sample_item_id'.",
            ),
            # Validate the format of the 'datetime' level using regex
            pa.Check(
                lambda df: df.columns.get_level_values("datetime")
                .astype(str)  # Convert to string for regex matching
                .str.match(
                    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$"
                )  # Match the datetime format 'YYYY-MM-DD HH:MM:SS'
                .all(),
                error="Datetime level values must match the format 'YYYY-MM-DD HH:MM:SS'.",
            ),
            # Check for NaN values in the 'datetime' level
            pa.Check(
                lambda df: (
                    not df.columns.get_level_values("datetime").isna().any()
                    if not allow_nan
                    else True
                ),
                error="The 'datetime' level must not contain NaN values.",
            ),
            # Check for NaN values in the 'sample_item_id' level
            pa.Check(
                lambda df: (
                    not df.columns.get_level_values("sample_item_id").isna().any()
                    if not allow_nan
                    else True
                ),
                error="The 'sample_item_id' level must not contain NaN values.",
            ),
        ],
        **DEFAULT_SCHEMA_PARAMS_MATRIX,
        name=name,
    )


# Intensity-matrix Schema
binning_intensity_schema = create_matrix_schema(
    name="Mascope peaks Intensity-matrix Schema", allow_nan=True
)

# TIC-normalized Intensity-matrix Schema
binning_norm_intensity_schema = create_matrix_schema(
    name="Mascope peaks tic-normalized Intensity-matrix Schema", allow_nan=True
)

# mz-matrix Schema
binning_mz_schema = create_matrix_schema(
    name="Mascope peaks mz-matrix Schema", allow_nan=True
)

# Count-matrix Schema (NaN values are NOT allowed)
binning_count_schema = create_matrix_schema(
    name="Mascope peaks Count-matrix Schema", allow_nan=False
)
