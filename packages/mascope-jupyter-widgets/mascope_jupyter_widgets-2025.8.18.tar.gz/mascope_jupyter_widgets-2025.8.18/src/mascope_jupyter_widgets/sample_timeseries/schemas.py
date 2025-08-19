import pandera as pa
from ..mascope_data.schemas import match_samples_schema

# Sample timeseries schema
sample_peak_timeseries_schema = pa.DataFrameSchema(
    columns={
        **match_samples_schema.columns,
        "time": pa.Column(float, nullable=False, coerce=True, required=True),
        "height": pa.Column(float, nullable=False, coerce=True, required=True),
        "mz": pa.Column(float, nullable=False, coerce=True, required=True),
    },
    checks=[
        pa.Check(lambda df: df["height"] >= 0, error="Height must be non-negative"),
    ],
    index=pa.Index(int),
    name="Sample Level Timeseries Schema",
    strict=False,
)
