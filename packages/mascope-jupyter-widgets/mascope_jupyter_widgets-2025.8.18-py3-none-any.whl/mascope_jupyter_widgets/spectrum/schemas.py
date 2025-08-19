import warnings
import pandera as pa
import pandas as pd

from ..mascope_data.schemas import (
    peaks_schema,
    DEFAULT_SCHEMA_PARAMS,
    add_column_for_filtering,
)

warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
)  # TODO, Think later groupby deprecation warning
# Import global schemas


# Parser(s)
## Dataframe-level parser
def set_unique_index(spectrum_df: pd.DataFrame) -> pd.DataFrame:
    """Create the unique identifier for peak-data"""

    spectrum_df["sample_file_id_mz"] = (
        spectrum_df["sample_file_id"] + "_" + spectrum_df["mz"].astype("str")
    )
    spectrum_df = spectrum_df.drop_duplicates(
        subset=["sample_file_id_mz"], keep="first"
    )
    spectrum_df = spectrum_df.set_index("sample_file_id_mz")

    return spectrum_df


## Dataframe-level parser
def calculate_tic_norm_intensity_and_cumsum_tic_ratio(
    spectrum_df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculates spectrum 'tic', 'norm_intensity' and 'cumsum_tic_ratio' columns
    for spectrum data."""

    def compute_norm_and_cumsum(group: pd.DataFrame) -> pd.DataFrame:
        """Compute 'norm_intensity' and 'cumsum_tic_ratio' columns."""
        group = group.copy()
        tic = group["intensity"].sum()
        group["tic"] = tic
        group["norm_intensity"] = group["intensity"] / tic
        group = group.sort_values(by="intensity", ascending=False)
        group["cumsum_tic_ratio"] = group["norm_intensity"].cumsum()
        # Add the group key as a column (future-proof)
        group["sample_item_id"] = group["sample_item_id"].iloc[0]
        return group

    spectrum_df = spectrum_df.groupby("sample_item_id", group_keys=False).apply(
        compute_norm_and_cumsum
    )
    return spectrum_df


# Scema(s)
## Spectrum DF Schema
spectrum_schema = pa.DataFrameSchema(
    columns={
        **peaks_schema.columns,
        "norm_intensity": pa.Column(float, nullable=False, coerce=True, required=True),
        "cumsum_tic_ratio": pa.Column(
            float, nullable=False, coerce=True, required=True
        ),
    },
    **DEFAULT_SCHEMA_PARAMS,
    unique=[],
    index=pa.Index(
        pa.String,
        unique=True,
    ),
    checks=[],
    parsers=[
        pa.Parser(add_column_for_filtering),
        pa.Parser(set_unique_index),
        pa.Parser(calculate_tic_norm_intensity_and_cumsum_tic_ratio),
    ],
    name="Spectrum DF Schema",
)
