import pandera as pa
import pandas as pd
from pandas.api.types import is_dict_like, is_list_like

DEFAULT_SCHEMA_PARAMS = {
    "strict": False,
    "ordered": False,
    "unique_column_names": True,
    "metadata": None,
    "add_missing_columns": False,
}


# pa.Checks
## Column-level check
def check_dicts(series: pd.Series) -> pd.Series:
    """Check if each value is a dictionary"""

    return series.map(is_dict_like)


## Column-level check
def check_lists(series: pd.Series) -> pd.Series:
    """Check if each value is a list"""

    return series.map(is_list_like)


## Column-level check
def check_datetime_naive(datetime_series: pd.Series) -> bool:
    """
    Checks if all datetime values in the Series are naive (do not have a timezone).

    :param datetime_series: A Pandas Series containing datetime values.
    :return: True if all datetime values are naive, False otherwise.
    """
    return (
        datetime_series.apply(
            lambda x: isinstance(x, pd.Timestamp) and x.tzinfo is None
        )
        != pd.NaT
    ).all()  # Updated to avoid FutureWarning


## Column-level check
def check_norm_intensity_less_than_one(norm_intensity: pd.Series):
    """Checks if all 'norm_intensity' values are less than 1."""

    return (norm_intensity < 1).all()


## Dataframe-level check
def check_cumsum_tic_ratio_increasing(mascope_df: pd.DataFrame) -> bool:
    """Checks if 'cumsum_tic_ratio' is monotonically increasing
    within each 'sample_item_id' group."""

    def is_monotonic_increasing(series: pd.Series) -> bool:
        """Check if a series is monotonically increasing."""
        return series.is_monotonic_increasing

    return (
        mascope_df.groupby("sample_item_id")["cumsum_tic_ratio"]
        .apply(is_monotonic_increasing)
        .all()
    )


# pa.Parser(s)
## Column-level parser
def fill_nan_with_zero(series: pd.Series) -> pd.Series:
    """Parser to fill NaN values in a column with zero."""
    return series.fillna(0)


## Column-level parser
def parse_datetime_with_timezone(series: pd.Series) -> pd.Series:
    """Adjusting the parser to handle timezone localization correctly"""
    return pd.to_datetime(series, utc=True)


## Column-level parser
def drop_timezone(datetime_input: pd.Series | pd.Timestamp) -> pd.Series | pd.Timestamp:
    """Drops timezone from datetime -type series"""

    if isinstance(datetime_input, pd.Series):
        return pd.to_datetime(datetime_input).dt.tz_localize(None)
    elif isinstance(datetime_input, pd.Timestamp):
        return (
            datetime_input.tz_localize(None)
            if datetime_input.tzinfo
            else datetime_input
        )
    else:
        raise TypeError("Input must be a pandas Series or Timestamp.")


## Dataframe-level parser
def calculate_norm_intensity(mascope_df: pd.DataFrame) -> pd.DataFrame:
    """Calculates 'norm_intensity' column."""

    if "intensity" in mascope_df.columns:
        mascope_df["norm_intensity"] = (
            mascope_df["intensity"] / mascope_df["tic"]
        )  # peaks_matched
    elif "sample_peak_intensity" in mascope_df.columns:
        mascope_df["norm_sample_peak_intensity"] = (
            mascope_df["sample_peak_intensity"] / mascope_df["tic"]
        )  # match_data
    return mascope_df


## Dataframe-level parser
def sort_and_calculate_cumsum_tic_ratio(mascope_df: pd.DataFrame) -> pd.DataFrame:
    """Sorts the DataFrame and calculates 'cumsum_tic_ratio'."""

    if "intensity" in mascope_df.columns:  # peaks_matched
        mascope_df = mascope_df.sort_values(
            by=["sample_item_id", "intensity"], ascending=[True, False]
        )
        mascope_df["cumsum_tic_ratio"] = mascope_df.groupby("sample_item_id")[
            "norm_intensity"
        ].cumsum()
    elif "sample_peak_intensity" in mascope_df.columns:  # match_data
        mascope_df = mascope_df.sort_values(
            by=["sample_item_id", "sample_peak_intensity"], ascending=[True, False]
        )
        mascope_df["cumsum_tic_ratio"] = mascope_df.groupby("sample_item_id")[
            "norm_sample_peak_intensity"
        ].cumsum()

    return mascope_df


## Dataframe-level parser
def add_column_for_filtering(mascope_df: pd.DataFrame) -> pd.DataFrame:
    """Create new columns for filtering"""

    mascope_df["sample_item_name_datetime"] = (
        mascope_df["sample_item_name"]
        + "_"
        + pd.to_datetime(mascope_df["datetime"]).astype("str")
    )

    return mascope_df


## Dataframe-level parser
def set_unique_index(mascope_df: pd.DataFrame) -> pd.DataFrame:
    """Create the unique identifier for peak-data"""

    mascope_df["sample_file_id_mz_formula"] = (
        mascope_df["sample_file_id"]
        + "_"
        + mascope_df["mz"].astype("str")
        + "_"
        + mascope_df["target_compound_formula"].fillna("_UNKNOWN")
    )
    mascope_df = mascope_df.drop_duplicates(
        subset=["sample_file_id_mz_formula"], keep="first"
    )
    ## Set the new column as the index
    mascope_df = mascope_df.set_index("sample_file_id_mz_formula")
    if "index" in mascope_df.columns:
        mascope_df = mascope_df.drop(columns=["index"])

    return mascope_df


# Schemas

# Samples DF Schema
match_samples_schema = pa.DataFrameSchema(
    columns={
        "sample_item_id": pa.Column(str, nullable=False, coerce=True),
        "sample_file_id": pa.Column(str, nullable=False, coerce=True),
        "instrument_function_id": pa.Column(str, nullable=True, coerce=True),
        "sample_batch_id": pa.Column(str, nullable=False, coerce=True),
        "sample_item_name": pa.Column(str, nullable=False, coerce=True),
        "filename": pa.Column(str, nullable=False, coerce=True),
        "instrument": pa.Column(str, nullable=False, coerce=True),
        "method_file": pa.Column(str, nullable=True, coerce=True),
        "sample_item_type": pa.Column(str, nullable=False, coerce=True),
        "sample_item_attributes": pa.Column(
            object,
            nullable=False,
            checks=pa.Check(check_dicts, error="Values must be dictionaries"),
        ),
        "filter_id": pa.Column(str, nullable=True, coerce=True),
        "length": pa.Column(float, nullable=False, coerce=True),
        "tic": pa.Column(float, nullable=False, coerce=True),
        "polarity": pa.Column(str, nullable=False, coerce=True),
        "range": pa.Column(
            object,
            nullable=False,
            checks=pa.Check(check_lists, error="Values must be lists"),
            coerce=True,
        ),
        "mz_calibration": pa.Column(
            object,
            nullable=True,
            coerce=True,
            checks=pa.Check(check_dicts, error="Values must be dictionaries"),
        ),
        "datetime": pa.Column(
            pa.DateTime,
            nullable=False,
            coerce=True,
        ),
        "datetime_utc": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=False,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "sample_item_utc_created": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=False,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "sample_item_utc_modified": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=False,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "match_sample_id": pa.Column(str, nullable=False, coerce=True),
        "match_score": pa.Column(float, nullable=False, coerce=True),
        "match_category": pa.Column(object, nullable=True, coerce=True),
        "sample_peak_intensity_sum": pa.Column(float, nullable=False, coerce=True),
        "sample_peak_interference_sum": pa.Column(float, nullable=False, coerce=True),
        "match_sample_utc_created": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=False,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "match_sample_utc_modified": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=True,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "match_collection_types": pa.Column(
            object,
            nullable=False,
            checks=pa.Check(check_lists, error="Values must be lists"),
        ),
        "sample_batch_name": pa.Column(str, nullable=False, coerce=True),
        "sample_item_name_datetime": pa.Column(str, nullable=False, coerce=True),
        "t0": pa.Column(str, nullable=False, coerce=True),
        "t1": pa.Column(str, nullable=False, coerce=True),
    },
    **DEFAULT_SCHEMA_PARAMS,
    unique=[
        "sample_item_id",
        "sample_file_id",
        "filename",
        "datetime",
    ],
    drop_invalid_rows=True,
    coerce=True,
    index=pa.Index(int),
    parsers=[
        pa.Parser(add_column_for_filtering),
    ],
    name="Samples DF Schema",
)

# Compounds DF Schema
match_compounds_schema = pa.DataFrameSchema(
    columns={
        "match_compound_id": pa.Column(str, nullable=False, coerce=True),
        "sample_item_id": pa.Column(str, nullable=False, coerce=True),
        "target_compound_id": pa.Column(str, nullable=False, coerce=True),
        "match_score": pa.Column(float, nullable=False, coerce=True),
        "match_category": pa.Column(object, nullable=False, coerce=True),
        "sample_peak_intensity_sum": pa.Column(
            float, nullable=False, coerce=True, parsers=pa.Parser(fill_nan_with_zero)
        ),
        "sample_peak_interference_sum": pa.Column(
            float, nullable=False, coerce=True, parsers=pa.Parser(fill_nan_with_zero)
        ),
        "match_compound_utc_created": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=False,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "match_compound_utc_modified": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=True,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "unit": pa.Column(str, nullable=False, coerce=True),
        "target_compound_name": pa.Column(str, nullable=True, coerce=True),
        "target_compound_formula": pa.Column(str, nullable=False, coerce=True),
    },
    **DEFAULT_SCHEMA_PARAMS,
    unique=["match_compound_id", "target_compound_id"],
    coerce=True,
    index=pa.Index(int),
    parsers=[],
    name="Compounds DF Schema",
)

# Ions DF Schema
match_ions_schema = pa.DataFrameSchema(
    columns={
        "match_ion_id": pa.Column(str, nullable=False, coerce=True),
        "sample_item_id": pa.Column(str, nullable=False, coerce=True),
        "target_ion_id": pa.Column(str, nullable=False, coerce=True),
        "match_score": pa.Column(float, nullable=False, coerce=True),
        "match_category": pa.Column(object, nullable=False, coerce=True),
        "sample_peak_intensity_sum": pa.Column(
            float, nullable=False, coerce=True, parsers=pa.Parser(fill_nan_with_zero)
        ),
        "sample_peak_interference_sum": pa.Column(
            float, nullable=False, coerce=True, parsers=pa.Parser(fill_nan_with_zero)
        ),
        "match_ion_utc_created": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=False,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "match_ion_utc_modified": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=True,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "unit": pa.Column(str, nullable=False, coerce=True),
        "target_compound_id": pa.Column(str, nullable=False, coerce=True),
        "target_ion_formula": pa.Column(str, nullable=False, coerce=True),
        "filter_params": pa.Column(
            object,
            nullable=False,
            checks=pa.Check(check_dicts, error="Values must be dictionaries"),
            coerce=True,
        ),
        "ionization_mechanism": pa.Column(str, nullable=False, coerce=True),
    },
    **DEFAULT_SCHEMA_PARAMS,
    unique=["match_ion_id", "target_compound_id"],
    coerce=True,
    index=pa.Index(int),
    parsers=[],
    name="Ions DF Schema",
)

# Isotopes DF Schema
match_isotopes_schema = pa.DataFrameSchema(
    columns={
        "match_isotope_id": pa.Column(str, nullable=False, coerce=True),
        "target_isotope_id": pa.Column(str, nullable=False, coerce=True),
        "sample_item_id": pa.Column(str, nullable=False, coerce=True),
        "sample_peak_id": pa.Column(int, nullable=False, coerce=True),
        "sample_peak_mz": pa.Column(float, nullable=False, coerce=True),
        "sample_peak_intensity": pa.Column(
            float, nullable=False, coerce=True, parsers=pa.Parser(fill_nan_with_zero)
        ),
        "sample_peak_intensity_relative": pa.Column(
            float, nullable=False, coerce=True, parsers=pa.Parser(fill_nan_with_zero)
        ),
        "sample_peak_tof": pa.Column(float, nullable=False, coerce=True),
        "match_abundance_error": pa.Column(float, nullable=False, coerce=True),
        "match_mz_error": pa.Column(float, nullable=False, coerce=True),
        "match_isotope_similarity": pa.Column(float, nullable=False, coerce=True),
        "match_score": pa.Column(float, nullable=False, coerce=True),
        "match_isotope_utc_created": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=False,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "match_isotope_utc_modified": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=True,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "mz": pa.Column(float, nullable=False, coerce=True),
        "relative_abundance": pa.Column(float, nullable=False, coerce=True),
        "target_ion_id": pa.Column(str, nullable=False, coerce=True),
        "sample_peak_interference": pa.Column(float, nullable=True, coerce=True),
    },
    **DEFAULT_SCHEMA_PARAMS,
    unique=["match_isotope_id", "match_isotope_utc_created"],
    coerce=True,
    index=pa.Index(int),
    parsers=[],
    name="Isotopes DF Schema",
)

# Peaks DF Schema
peaks_schema = pa.DataFrameSchema(
    columns={
        "mz": pa.Column(float, nullable=False, coerce=True),
        "intensity": pa.Column(float, nullable=False, coerce=True),
        "unit": pa.Column(str, nullable=True, coerce=True),
        "sample_batch_name": pa.Column(str, nullable=False, coerce=True),
        "sample_item_name": pa.Column(str, nullable=False, coerce=True),
        "filename": pa.Column(str, nullable=False, coerce=True),
        "filter_id": pa.Column(str, nullable=True, coerce=True),
        "sample_item_type": pa.Column(str, nullable=False, coerce=True),
        "datetime": pa.Column(
            pa.DateTime,
            coerce=False,
            parsers=[pa.Parser(drop_timezone)],
            checks=[
                pa.Check(check_datetime_naive, error="Not in correct format."),
            ],
        ),
        "datetime_utc": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=False,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "sample_file_id": pa.Column(str, nullable=False, coerce=True),
        "sample_item_id": pa.Column(str, nullable=False, coerce=True),
        "tic": pa.Column(float, nullable=False, coerce=True),
        "instrument": pa.Column(str, nullable=True, coerce=True),
        "sample_item_name_datetime": pa.Column(str, nullable=False, coerce=True),
    },
    **DEFAULT_SCHEMA_PARAMS,
    unique=[],
    coerce=True,
    index=pa.Index(
        int,
        unique=True,
    ),
    checks=[],
    parsers=[
        pa.Parser(add_column_for_filtering),
    ],
    name="Peaks DF Schema",
)

# Workspaces DF schema
workspaces_schema = pa.DataFrameSchema(
    columns={
        "workspace_id": pa.Column(str, nullable=False),
        "workspace_name": pa.Column(str, nullable=True),
        "workspace_description": pa.Column(str, nullable=True),
        "workspace_type": pa.Column(str, nullable=False),
        "icon": pa.Column(str, nullable=True),
        "instrument": pa.Column(str, nullable=True),
        "locked": pa.Column(bool, nullable=True, coerce=True),
        "workspace_utc_created": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=False,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "workspace_utc_modified": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=True,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
    },
    **DEFAULT_SCHEMA_PARAMS,
    unique=["workspace_id"],
    index=pa.Index(int),
    name="Workspaces DF Schema",
)

# Batches DF schema
sample_batches_schema = pa.DataFrameSchema(
    columns={
        "sample_batch_id": pa.Column(str, nullable=False),
        "workspace_id": pa.Column(str, nullable=False),
        "sample_batch_name": pa.Column(str, nullable=True),
        "sample_batch_description": pa.Column(str, nullable=True),
        "sample_batch_type": pa.Column(str, nullable=False),
        "locked": pa.Column(bool, nullable=True, coerce=True),
        "polarity": pa.Column(str, nullable=False, coerce=True),
        "sample_batch_utc_created": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=False,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "sample_batch_utc_modified": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=True,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "build_params.calibration_collection": pa.Column(str, nullable=False),
        "build_params.ion_mechanisms": pa.Column(
            object,
            nullable=False,
            checks=pa.Check(check_lists, error="Values must be lists"),
        ),
        "build_params.calibration_ion_mechanisms": pa.Column(
            object,
            nullable=True,
            checks=pa.Check(check_lists, error="Values must be lists"),
        ),
    },
    **DEFAULT_SCHEMA_PARAMS,
    unique=["sample_batch_id"],
    index=pa.Index(int),
    name="Batches DF Schema",
)

# Match Data DF Schema
match_data_schema = pa.DataFrameSchema(
    columns={
        "match_isotope_id": pa.Column(str, nullable=False, coerce=True),
        "target_isotope_id": pa.Column(str, nullable=False, coerce=True),
        "datetime": pa.Column(
            pa.DateTime,
            coerce=False,
            parsers=[pa.Parser(drop_timezone)],
            checks=[
                pa.Check(check_datetime_naive, error="Not in correct format."),
            ],
        ),
        "sample_item_id": pa.Column(str, nullable=False, coerce=True),
        "sample_peak_id": pa.Column(str, nullable=False, coerce=True),
        "sample_peak_mz": pa.Column(float, nullable=False, coerce=True),
        "sample_peak_intensity": pa.Column(float, nullable=False, coerce=True),
        "unit": pa.Column(str, nullable=False, coerce=True),
        "sample_peak_intensity_relative": pa.Column(float, nullable=False, coerce=True),
        "sample_peak_tof": pa.Column(float, nullable=False, coerce=True),
        "match_abundance_error": pa.Column(float, nullable=False, coerce=True),
        "match_mz_error": pa.Column(float, nullable=False, coerce=True),
        "match_isotope_similarity": pa.Column(float, nullable=False, coerce=True),
        "match_score": pa.Column(float, nullable=False, coerce=True),
        "match_isotope_utc_created": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=False,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "match_isotope_utc_modified": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=True,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "mz": pa.Column(float, nullable=False, coerce=True),
        "relative_abundance": pa.Column(float, nullable=False, coerce=True),
        "target_ion_id": pa.Column(str, nullable=False, coerce=True),
        "sample_peak_interference": pa.Column(float, nullable=True, coerce=True),
        "target_ion_formula": pa.Column(str, nullable=False, coerce=True),
        "ionization_mechanism": pa.Column(str, nullable=False, coerce=True),
        "target_compound_id": pa.Column(str, nullable=False, coerce=True),
        "target_compound_name": pa.Column(str, nullable=True, coerce=True),
        "target_compound_formula": pa.Column(str, nullable=False, coerce=True),
        "sample_file_id": pa.Column(str, nullable=False, coerce=True),
        "sample_batch_name": pa.Column(str, nullable=False, coerce=True),
        "sample_item_name": pa.Column(str, nullable=False, coerce=True),
        "filename": pa.Column(str, nullable=False, coerce=True),
        "filter_id": pa.Column(str, nullable=True, coerce=True),
        "sample_item_type": pa.Column(str, nullable=False, coerce=True),
        "datetime_utc": pa.Column(
            pd.DatetimeTZDtype(tz="UTC"),
            nullable=False,
            coerce=True,
            parsers=pa.Parser(parse_datetime_with_timezone),
        ),
        "tic": pa.Column(float, nullable=False, coerce=True),
        "instrument": pa.Column(str, nullable=True, coerce=True),
        "sample_item_name_datetime": pa.Column(str, nullable=False, coerce=True),
        "norm_sample_peak_intensity": pa.Column(
            float,
            nullable=False,
            coerce=True,
            checks=pa.Check(
                check_norm_intensity_less_than_one,
                error="tic-normalized values more than 1, suspend.",
            ),
        ),
    },
    **DEFAULT_SCHEMA_PARAMS,
    unique=[
        "match_isotope_id",
    ],
    coerce=True,
    index=pa.Index(int),
    parsers=[
        pa.Parser(add_column_for_filtering),
        pa.Parser(calculate_norm_intensity),
        pa.Parser(sort_and_calculate_cumsum_tic_ratio),
    ],
    name="Match Data Schema",
)

# Peaks DF Schema
peaks_matched_schema = pa.DataFrameSchema(
    columns={
        **peaks_schema.columns,
        "norm_intensity": pa.Column(
            float,
            nullable=False,
            coerce=True,
            checks=pa.Check(
                check_norm_intensity_less_than_one,
                error="tic-normalized values more than 1, suspend.",
            ),
        ),
        "cumsum_tic_ratio": pa.Column(float, nullable=False, coerce=True),
        "target_compound_id": pa.Column(str, nullable=True, coerce=True),
        "target_compound_name": pa.Column(str, nullable=True, coerce=True),
        "target_compound_formula": pa.Column(str, nullable=True, coerce=True),
        "target_ion_formula": pa.Column(str, nullable=True, coerce=True),
        "target_isotope_mz": pa.Column(float, nullable=True, coerce=True),
        "sample_peak_mz": pa.Column(float, nullable=True, coerce=True),
        "match_mz_error": pa.Column(float, nullable=True, coerce=True),
        "relative_abundance": pa.Column(float, nullable=True, coerce=True),
        "match_abundance_error": pa.Column(float, nullable=True, coerce=True),
        "match_score_isotope": pa.Column(float, nullable=True, coerce=True),
        "ionization_mechanism": pa.Column(str, nullable=True, coerce=True),
    },
    **DEFAULT_SCHEMA_PARAMS,
    unique=[],
    coerce=True,
    index=pa.Index(
        pa.String,
        unique=True,
    ),
    checks=[],
    parsers=[
        pa.Parser(set_unique_index),
        pa.Parser(calculate_norm_intensity),
        pa.Parser(sort_and_calculate_cumsum_tic_ratio),
    ],
    name="Peak data combined with match data",
)
