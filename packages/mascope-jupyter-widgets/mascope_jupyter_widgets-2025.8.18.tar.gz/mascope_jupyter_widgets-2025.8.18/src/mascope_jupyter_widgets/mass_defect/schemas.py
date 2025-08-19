import pandera as pa
import pandas as pd
import numpy as np
from ..mascope_data.schemas import (
    peaks_matched_schema,
    set_unique_index,
    DEFAULT_SCHEMA_PARAMS,
)


# pa.Check
# Column-level check
def check_mass_defect_range(mass_defect: pd.Series) -> bool:
    """
    Ensure mass_defect values are between -0.5 and 0.5.
    """
    return (mass_defect >= -0.5) & (mass_defect <= 0.5)


# pa.Parser
# Dataframe-level parser
def calculate_mz_round_and_mass_defects_to_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate 'mz_round' and 'mass_defect' - columns.
    """

    if "mz_round" not in df.columns:
        df["mz_round"] = df["mz"].round()
    if "mass_defect" not in df.columns:
        df["mass_defect"] = df["mz"] - df["mz_round"]

    return df


# Dataframe-level parser
def calculate_min_max_intensity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate min-max normalized intensity for e.g. to be used
    for marker size and color calculations.
    """
    df["intensity"] = df["intensity"].fillna(0)
    min_value = df["intensity"].min()
    max_value = df["intensity"].max()
    df["min_max_intensity"] = (df["intensity"] - min_value) / (max_value - min_value)
    df["min_max_intensity"] = df["min_max_intensity"].fillna(0)

    return df


# Dataframe-level parser
def calculate_log_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate log-values for intensity columns.
    """

    df["log_intensity"] = np.log(df["intensity"].replace(0, np.nan))
    df["log1p_intensity"] = np.log1p(df["intensity"].replace(0, np.nan))
    # Calculate min-max normalized log1p intensity
    df["log1p_min_max_intensity"] = (
        np.log1p(df["intensity"]) - np.log1p(df["intensity"]).min()
    ) / (np.log1p(df["intensity"]).max() - np.log1p(df["intensity"]).min())
    df["log_intensity"] = df["log_intensity"].fillna(0)
    df["log1p_intensity"] = df["log1p_intensity"].fillna(0)
    df["log1p_min_max_intensity"] = df["log1p_min_max_intensity"].fillna(0)

    return df


# Dataframe-level parser
def add_trace_name_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a new column 'trace_name' to the DataFrame.
    """
    df["trace_name"] = df["sample_item_name_datetime"]
    return df


# Schemas
# Mascope Peaks mass_defect DF Schema
peaks_mass_defect_schema = pa.DataFrameSchema(
    columns={
        **peaks_matched_schema.columns,
        "mz_round": pa.Column(float, nullable=False, coerce=True),
        "mass_defect": pa.Column(
            float, nullable=False, coerce=True, checks=pa.Check(check_mass_defect_range)
        ),
    },
    **DEFAULT_SCHEMA_PARAMS,
    unique=[],
    index=pa.Index(
        str,
        unique=True,
    ),
    parsers=[
        pa.Parser(calculate_mz_round_and_mass_defects_to_columns),
        pa.Parser(set_unique_index),
    ],
    checks=[],
    name="Mascope Mass Defect DF Schema",
)

# Mascope Peaks Scaled mass_defect DF Schema
peaks_mass_defect_scaled_schema = pa.DataFrameSchema(
    columns={
        **peaks_mass_defect_schema.columns,
        "kendrick_mass_defect": pa.Column(float, nullable=False, coerce=True),
        "kendrick_method": pa.Column(str, nullable=False, coerce=True),
        "log_intensity": pa.Column(float, nullable=False, coerce=True),
        "log1p_intensity": pa.Column(float, nullable=False, coerce=True),
        "log1p_min_max_intensity": pa.Column(float, nullable=False, coerce=True),
        "min_max_intensity": pa.Column(float, nullable=False, coerce=True),
        "trace_name": pa.Column(str, nullable=False, coerce=True),
    },
    **DEFAULT_SCHEMA_PARAMS,
    unique=[],
    index=pa.Index(str, unique=True),
    parsers=[
        pa.Parser(calculate_min_max_intensity),
        pa.Parser(calculate_log_values),
        pa.Parser(add_trace_name_column),
    ],
    checks=[],
    name="Mascope Scaled Mass Defect DF Schema",
)
