from datetime import datetime, timedelta
import pandera as pa
import numpy as np
import pandas as pd

# Import global schemas
from ..mascope_data.schemas import (
    match_compounds_schema,
    DEFAULT_SCHEMA_PARAMS,
    parse_datetime_with_timezone,
    drop_timezone,
    check_datetime_naive,
)


# pa.Parser(s)
## Dataframe-level parser
def add_tic_to_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Add tic to own rows.

    This function checks if the 'tic' values are already present in the dataset.
    If not, it creates new rows with 'tic' values and appends them to the original DataFrame.
    """
    # Check if TIC values are already in the dataset
    if (
        not df["target_compound_name"].eq("tic").any()
        and len(df["target_compound_name"].unique()) > 1
    ):
        ## Find unique TIC values and corresponding rows
        unique_sample_rows = df.drop_duplicates(subset=["sample_item_id"])
        ## Build new rows based on unique sample_item_id values and their corresponding columns
        new_rows = []
        for _, row in unique_sample_rows.iterrows():
            ## Create a new row based on the 'tic' value and its corresponding values
            new_row = row.to_dict()
            new_row.update(
                {
                    "target_compound_id": "tic",
                    "sample_item_id": "tic",
                    "match_compound_id": "tic",
                    "target_compound_name": "tic",
                    "target_compound_formula": "tic",
                    "trace_name": "tic",
                    "intensity": row["tic"],  # Assign 'tic' value to 'intensity'
                    "sample_peak_interference_sum": row["tic"],
                    "match_score": 0,
                }
            )
            new_rows.append(new_row)
        tic_df = pd.DataFrame(new_rows)

        # Append new rows to the original DataFrame
        df = pd.concat([df, tic_df], ignore_index=True)

    return df


## Dataframe-level parser
def missing_dispersion_values_to_zero(df: pd.DataFrame) -> pd.DataFrame:
    """Set missing dispersion-values (std or mad) to zero for all relevant columns.

    This function checks for the presence of dispersion columns in the DataFrame
    and sets their values to zero if they are missing (NaN).
    It also replaces any infinite values with NaN and fills them with zero.
    """

    # Define dispersion columns
    columns = [
        "intensity",
        "match_score",
        "tic",
        "sample_peak_interference_sum",
    ]

    dispersion_cols = [
        col_name
        for base_col in columns
        for col_name in [f"{base_col}_std", f"{base_col}_mad"]
        if col_name in df.columns
    ]

    if dispersion_cols:
        df[dispersion_cols] = (
            df[dispersion_cols].replace([np.inf, -np.inf], np.nan).fillna(0)
        )

    return df


## Dataframe-level parser
def add_hour_of_day(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds 'date' and 'hour_of_day' -columns to dataframe
    in str and int32format.

    The 'hour_of_day' is rounded to the nearest hour using the 30-minute rule.
    The 'date' column is formatted as 'YYYY-MM-DD'.
    The 'hour_of_day_utc' is also rounded to the nearest hour using the 30-minute rule.
    The 'datetime' column is expected to NOT be in UTC timezone.
    The 'datetime_utc' column is expected to be in UTC timezone.
    """

    def round_to_nearest_hour(t: pd.Timestamp) -> int:
        """Helper function to round to the nearest hour using 30-minute rule"""
        if pd.isnull(t):
            return None

        # Calculate rounded hour for each day
        round_hour_day = t.replace(
            second=0, microsecond=0, minute=0, hour=t.hour
        ) + timedelta(hours=t.minute // 30)

        # Extract hour part directly from the datetime object
        round_hour_int = round_hour_day.hour  # Get the hour part as integer

        return round_hour_int

    df["date"] = df["datetime"].dt.date
    df["hour_of_day"] = df["datetime"].apply(round_to_nearest_hour)
    df["hour_of_day_utc"] = df["datetime_utc"].apply(round_to_nearest_hour)
    df = df.sort_values(by="hour_of_day")
    # Convert 'date' from datetime.date to datetime.datetime before using strftime
    df["date"] = df["date"].apply(
        lambda d: datetime.combine(d, datetime.min.time()).strftime("%Y-%m-%d")
    )

    return df


# pa.Check(s)
## Dataframe-level check
def check_column_presence(df: pd.DataFrame) -> bool:
    """Validates that column cleaning has been worked correctly.

    The function checks if the 'intensity' column is present and
    the 'match_compound_utc_modified' column is absent in the DataFrame.
    It returns True if the conditions are met, otherwise False.
    """
    required_column = "intensity"
    forbidden_column = "match_compound_utc_modified"

    return required_column in df.columns and forbidden_column not in df.columns


## Column-level check
def check_column_pairs(df: pd.DataFrame) -> bool:
    """Check that dataframe contains correct pair
    'mean' and 'std OR 'median' and 'mad'"""

    pairs = [["intensity", "intensity_std"], ["intensity", "intensity_mad"]]

    return any(all(col in df.columns for col in pair) for pair in pairs)


# Schema(s)

# Match compounds longform DF Schema
timeseries_schema = pa.DataFrameSchema(
    columns={
        **{
            key: value
            for key, value in match_compounds_schema.columns.items()
            if key
            not in [
                "sample_peak_intensity_sum",
                "match_compound_utc_modified",
                "match_compound_utc_created",
                "target_compound_id",
                "target_compound_name",
                "target_compound_formula",
                "match_category",
                "match_compound_id",
                "match_score",
            ]
        },  # Exclude these columns from the inherited schema and edit if needed
        "target_compound_id": pa.Column(str, nullable=True, coerce=True),
        "target_compound_name": pa.Column(str, nullable=True, coerce=True),
        "target_compound_formula": pa.Column(str, nullable=True, coerce=True),
        "match_category": pa.Column(str, nullable=True, coerce=True),
        "match_compound_id": pa.Column(str, nullable=True, coerce=True),
        "match_score": pa.Column(float, nullable=True, coerce=True),
        "intensity": pa.Column(float, nullable=False, coerce=True),
        "sample_item_name": pa.Column(str, nullable=True, coerce=True),
        "filename": pa.Column(str, nullable=True, coerce=True),
        "filter_id": pa.Column(str, nullable=True, coerce=True),
        "tic": pa.Column(float, nullable=True, coerce=True),
        "datetime": pa.Column(
            pa.DateTime,
            nullable=False,
            coerce=False,
            parsers=[pa.Parser(drop_timezone)],
            checks=[
                pa.Check(check_datetime_naive, error="Not datetime naive"),
            ],
        ),
        "datetime_utc": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=True,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "instrument": pa.Column(str, nullable=True, coerce=True),
        "sample_item_type": pa.Column(str, nullable=True, coerce=True),
        "trace_name": pa.Column(str, nullable=True, coerce=True),
        "date": pa.Column(object, nullable=False, coerce=True),
        "hour_of_day": pa.Column(np.int64, nullable=False, coerce=True),
        "hour_of_day_utc": pa.Column(np.int64, nullable=False, coerce=True),
    },
    **DEFAULT_SCHEMA_PARAMS,
    unique=[],
    index=pa.Index(int),
    checks=[pa.Check(check_column_presence)],
    parsers=[pa.Parser(add_hour_of_day), pa.Parser(add_tic_to_rows)],
    name="Compounds longform DF Schema",
)

# Time-aggregated timeseries DF Schema
time_aggregated_schema = pa.DataFrameSchema(
    columns={
        **{
            key: value
            for key, value in timeseries_schema.columns.items()
            if key
            not in [
                "hour_of_day",
                "hour_of_day_utc",
                "match_category",
            ]
        },  # Exclude these columns from the inherited schema and edit if needed
        "match_category": pa.Column(str, nullable=False, coerce=True, required=False),
        "intensity_std": pa.Column(float, nullable=False, coerce=True, required=False),
        "intensity_mad": pa.Column(float, nullable=False, coerce=True, required=False),
        "match_score_std": pa.Column(
            float, nullable=False, coerce=True, required=False
        ),
        "match_score_mad": pa.Column(
            float, nullable=False, coerce=True, required=False
        ),
        "tic_std": pa.Column(float, nullable=False, coerce=True, required=False),
        "tic_mad": pa.Column(float, nullable=False, coerce=True, required=False),
        "sample_peak_interference_sum_std": pa.Column(
            float, nullable=False, coerce=True, required=False
        ),
        "sample_peak_interference_sum_mad": pa.Column(
            float, nullable=False, coerce=True, required=False
        ),
        "aggregate": pa.Column(str, nullable=False, coerce=True),
    },
    **DEFAULT_SCHEMA_PARAMS,
    unique=[],
    index=pa.Index(int),
    checks=[
        pa.Check(check_column_pairs, error="Not correct summary pairs"),
    ],
    parsers=[pa.Parser(missing_dispersion_values_to_zero)],
    name="Aggregated Datetime frequency DF Schema",
)

# Aggregated Diurnal Cycle DF Schema
diurnal_cycle_schema = pa.DataFrameSchema(
    columns={
        **{
            key: value
            for key, value in timeseries_schema.columns.items()
            if key
            not in [
                "datetime",
                "datetime_utc",
                "match_category",
            ]
        },  # Exclude these columns from the inherited schema and edit if needed
        "match_category": pa.Column(str, nullable=False, coerce=True),
        "intensity_std": pa.Column(float, nullable=False, coerce=True, required=False),
        "intensity_mad": pa.Column(float, nullable=False, coerce=True, required=False),
        "match_score_std": pa.Column(
            float, nullable=False, coerce=True, required=False
        ),
        "match_score_mad": pa.Column(
            float, nullable=False, coerce=True, required=False
        ),
        "tic_std": pa.Column(float, nullable=False, coerce=True, required=False),
        "tic_mad": pa.Column(float, nullable=False, coerce=True, required=False),
        "sample_peak_intensity_sum_std": pa.Column(
            float, nullable=False, coerce=True, required=False
        ),
        "sample_peak_intensity_sum_mad": pa.Column(
            float, nullable=False, coerce=True, required=False
        ),
        "sample_peak_interference_sum_std": pa.Column(
            float, nullable=False, coerce=True, required=False
        ),
        "sample_peak_interference_sum_mad": pa.Column(
            float, nullable=False, coerce=True, required=False
        ),
        "aggregate": pa.Column(str, nullable=False, coerce=True),
    },
    **DEFAULT_SCHEMA_PARAMS,
    unique=[],
    index=pa.Index(int),
    checks=[pa.Check(check_column_pairs, error="Not correct summary pairs")],
    parsers=[pa.Parser(missing_dispersion_values_to_zero)],
    name="Aggregated Diurnal Cycle DF Schema",
)
