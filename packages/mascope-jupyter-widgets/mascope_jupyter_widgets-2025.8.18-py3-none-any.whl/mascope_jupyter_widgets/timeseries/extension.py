from functools import cached_property
from typing import Literal
import numpy as np
import pandas as pd

from .schemas import (
    drop_timezone,
    parse_datetime_with_timezone,
    add_hour_of_day,
    add_tic_to_rows,
    missing_dispersion_values_to_zero,
    timeseries_schema,
    diurnal_cycle_schema,
    time_aggregated_schema,
)
from ..mascope_data.access import (
    get_mjw_mode,
)
from ..logging_config import logger  # Import the shared logger

MJW_DEV_MODE = get_mjw_mode()  # Get the MJW_DEV_MODE environment variable


class TimeSeriesDataExtension:
    """
    Timeseries related extension for MascopeDataWrapper -dataset.
    Can be used to build 'target_compound_id' specific - and
    dataframe-level timeseries -, aggregated timeseries - and diurnal cycle
    dataframes.
    """

    def __init__(self) -> None:
        """
        Initialize the TimeSeriesDataExtension class.

        This class is designed to extend the functionality of the MascopeDataWrapper
        dataset by providing methods for handling time series data.
        It includes methods for aggregating, and processing time series data
        at the compound level.
        The class also initializes an empty DataFrame to store added untarget peaks.
        """
        self.added_untarget_peaks_cache = (
            pd.DataFrame()
        )  # Initialize an attribute to store added Untarget peaks

    @cached_property
    def timeseries(self) -> pd.DataFrame:
        """
        Compound-level dataframe with sample-level data.

        - This method collects a compound-level dataframe
        with a wider set of sample-level columns.
        - It adds tic to the rows and renames the columns
        to match the expected output.
        - The method also handles the addition of untarget peaks
        by checking if the added_untarget_peaks_cache attribute
        is initialized and appending any added peaks to the timeseries dataframe.
        - The method applies schema validation or parsers based on the environment mode
        (MJW_DEV_MODE).
            + If the mode is set to development, it validates the data using
            the `timeseries_schema`.
            + Otherwise, it applies parser functions directly
            to the data.

        :return: Compound-level dataframe with columns:
            "filename",
            "sample_item_name",
            "filter_id",
            "tic",
            "datetime",
            "datetime_utc",
            "instrument",
            "sample_item_id" and
            "sample_item_type"
        from sample-level dataframe.
        :rtype: pd.DataFrame
        """
        dataset = self

        # Compound-level df with wider set of sample-level columns
        timeseries = pd.merge(
            dataset.match_compounds,  # pylint: disable=E1101 # MacopeDataWrapper.match_compounds
            dataset.match_samples[  # pylint: disable=E1101 # MacopeDataWrapper.match_samples
                [
                    "filename",
                    "sample_item_name",
                    "filter_id",
                    "tic",
                    "datetime",
                    "datetime_utc",
                    "instrument",
                    "sample_item_id",
                    "sample_item_type",
                ]
            ],
            left_on=["sample_item_id"],
            right_on=["sample_item_id"],
        )
        # Edit
        timeseries = timeseries.rename(
            columns={"sample_peak_intensity_sum": "intensity"}
        )
        timeseries = timeseries.drop(
            columns=["match_compound_utc_modified", "match_compound_utc_created"]
        )
        timeseries["target_compound_name"] = timeseries["target_compound_name"].replace(
            "", None
        )
        timeseries["target_compound_name"] = timeseries["target_compound_name"].fillna(
            timeseries["target_compound_formula"]
        )
        timeseries["trace_name"] = (
            timeseries.target_compound_formula
            + " ("
            + timeseries.target_compound_name
            + ")"
        )
        timeseries["unit"] = (
            dataset.intensity_unit  # pylint: disable=E1101
        )  # MacopeDataWrapper.intensity_unit
        # Ensure `added_untarget_peaks_cache` is initialized
        if self.added_untarget_peaks_cache is None:
            self.added_untarget_peaks_cache = pd.DataFrame()
        # Append any added Untarget peaks
        if not self.added_untarget_peaks_cache.empty:
            timeseries = pd.concat(
                [
                    timeseries,
                    self.added_untarget_peaks_cache.drop_duplicates(),
                ],
                ignore_index=True,
            )

        # Apply schema validation or parsers based on environment mode
        if MJW_DEV_MODE:
            return timeseries_schema.validate(timeseries)
        # Apply parser functions directly
        timeseries["datetime"] = drop_timezone(timeseries["datetime"])
        timeseries["datetime_utc"] = parse_datetime_with_timezone(
            timeseries["datetime_utc"]
        )
        timeseries = add_hour_of_day(timeseries)
        timeseries = add_tic_to_rows(timeseries)
        return timeseries

    def get_compound_timeseries(
        self,
        target_compound_value: str = None,
        filter_by: Literal["target_compound_id", "trace_name"] = "target_compound_id",
    ) -> pd.DataFrame:
        """
        Collects a subset of the timeseries dataframe filtered by the specified column.
        If no value for target_compound_value is provided,
        the entire timeseries dataframe is returned.

        :param target_compound_value: Value to filter by in the specified column.
        :type target_compound_value: str
        :param filter_by: Column to filter by ('target_compound_id' or 'trace_name').
        :type filter_by: Literal["target_compound_id", "trace_name"]
        :return: Filtered compound-level dataframe.
        :rtype: pd.DataFrame
        """
        # Validate filter_by
        match filter_by:
            case "target_compound_id" | "trace_name":
                pass
            case _:
                raise ValueError(
                    f"Invalid filter_by='{filter_by}', must be 'target_compound_id'"
                    " or 'trace_name'."
                )

        if target_compound_value:
            unique_values = self.timeseries[filter_by].unique().tolist()
            if target_compound_value not in unique_values:
                raise ValueError(
                    f"Invalid value '{target_compound_value}' for column '{filter_by}'."
                )
            return self.timeseries[self.timeseries[filter_by] == target_compound_value]
        else:
            return self.timeseries

    def get_compound_aggregated_timeseries(
        self,
        target_compound_value: str = None,
        filter_by: Literal["target_compound_id", "trace_name"] = "target_compound_id",
        freq: Literal["Hourly", "Daily", "Weekly", "Monthly"] = "Daily",
        method: Literal["mean", "median"] = "mean",
    ) -> pd.DataFrame:
        """
        Calculates time-aggregated timeseries by input frequency
        (Default 'Daily') and method (Default 'mean').

        This method allows for the aggregation of time-series data
        based on a specified frequency and method (mean or median).
        The aggregation is performed on the compound-level dataframe,

        :param target_compound_value: Value to filter by in the specified column.
        :type target_compound_value: str
        :param filter_by: Column to filter by ('target_compound_id' or 'trace_name').
        :type filter_by: Literal["target_compound_id", "trace_name"]
        :param freq: Time-aggregation frequency: "Hourly", "Daily", "Weekly", or "Monthly".
        :type freq: Literal["Hourly", "Daily", "Weekly", "Monthly"], optional
        :param method: Method for time-aggregated intensity calculation ('mean' or 'median').
        :type method: Literal["mean", "median"], optional
        :raises ValueError: If invalid method, frequency, or filter_by is given.
        :return: Aggregated time-series compound-level dataframe.
        :rtype: pd.DataFrame
        """

        freq_map = {"Hourly": "h", "Daily": "D", "Weekly": "W", "Monthly": "ME"}

        # Validate method, frequency, and filter_by
        match method:
            case "mean" | "median":
                pass
            case _:
                raise ValueError(
                    f"Invalid method='{method}', must be 'mean' or 'median'"
                )
        match freq:
            case "Hourly" | "Daily" | "Weekly" | "Monthly":
                freq_code = freq_map[freq]
            case _:
                raise ValueError(
                    f"Invalid freq='{freq}', must be one of {list(freq_map.keys())}"
                )
        match filter_by:
            case "target_compound_id" | "trace_name":
                pass
            case _:
                raise ValueError(
                    f"Invalid filter_by='{filter_by}', must be 'target_compound_id'"
                    " or 'trace_name'."
                )
        # Filter the timeseries data
        if target_compound_value:
            unique_values = self.timeseries[filter_by].unique().tolist()
            if target_compound_value not in unique_values:
                raise ValueError(
                    f"Invalid value '{target_compound_value}' for column '{filter_by}'."
                )
            compound_timeseries = self.timeseries[
                self.timeseries[filter_by] == target_compound_value
            ]
            grouper = [
                pd.Grouper(key="datetime", freq=freq_code),
                pd.Grouper(key="datetime_utc", freq=freq_code),
            ]
            all_data = False
        else:
            compound_timeseries = self.timeseries
            grouper = [
                pd.Grouper(key="datetime", freq=freq_code),
                pd.Grouper(key="datetime_utc", freq=freq_code),
                "trace_name",
            ]
            all_data = True

        # Group data
        time_aggregated_compound = compound_timeseries.groupby(
            grouper, as_index=False
        ).agg(**get_agg_funcs(method))
        # Rename columns after aggregation
        time_aggregated_compound = time_aggregated_compound.rename(
            columns=lambda col: col.replace("_mean", "").replace("_median", "")
        )

        time_aggregated_compound = add_categorial_columns(
            compound_timeseries=compound_timeseries,
            aggregated_df=time_aggregated_compound,
            group_by=(
                [pd.Grouper(key="datetime", freq=freq_code)]
                if not all_data
                else [
                    pd.Grouper(key="datetime", freq=freq_code),
                    "trace_name",
                ]
            ),
            str_for_multiple=f"{freq}-{method}",
            all_data=all_data,
        )
        # Apply schema validation or parsers based on environment mode
        if MJW_DEV_MODE:
            return time_aggregated_schema.validate(time_aggregated_compound)
        # Apply parser functions directly
        time_aggregated_compound["datetime"] = drop_timezone(
            time_aggregated_compound["datetime"]
        )
        time_aggregated_compound["datetime_utc"] = parse_datetime_with_timezone(
            time_aggregated_compound["datetime_utc"]
        )
        time_aggregated_compound = missing_dispersion_values_to_zero(
            time_aggregated_compound
        )

        return time_aggregated_compound

    def get_compound_diurnal_cycle(
        self,
        target_compound_value: str = None,
        filter_by: Literal["target_compound_id", "trace_name"] = "target_compound_id",
        method: Literal["mean", "median"] = "mean",
    ) -> pd.DataFrame:
        """
        Calculates hour-of-day (diurnal cycle) aggregated timeseries values for intensity.

        This method allows for the aggregation of time-series data
        based on the hour of the day and a specified method (mean or median).

        :param target_compound_value: Value to filter by in the specified column.
        :type target_compound_value: str
        :param filter_by: Column to filter by ('target_compound_id' or 'trace_name').
        :type filter_by: Literal["target_compound_id", "trace_name"]
        :param method: Summarization method for hour-of-day ('mean' or 'median').
        :type method: Literal["mean", "median"], optional
        :return: Aggregated hour-of-day compound-level dataframe.
        :rtype: pd.DataFrame
        """
        match method:
            case "mean" | "median":
                pass  # Valid cases, continue execution
            case _:
                raise ValueError(
                    f"Invalid method='{method}', must be 'mean' or 'median'"
                )
        # Validate filter_by
        match filter_by:
            case "target_compound_id" | "trace_name":
                pass  # Valid cases, continue execution
            case _:
                raise ValueError(
                    f"Invalid filter_by='{filter_by}', must be 'target_compound_id'"
                    " or 'trace_name'."
                )
        # Filter the timeseries data
        if target_compound_value:
            unique_values = self.timeseries[filter_by].unique().tolist()
            if target_compound_value not in unique_values:
                raise ValueError(
                    f"Invalid value '{target_compound_value}' for column '{filter_by}'."
                )
            compound_timeseries = self.timeseries[
                self.timeseries[filter_by] == target_compound_value
            ]
            grouper = ["hour_of_day", "hour_of_day_utc"]
            all_data = False
        else:
            compound_timeseries = self.timeseries
            grouper = [
                "hour_of_day",
                "hour_of_day_utc",
                "trace_name",
            ]
            all_data = True
        # Group data
        aggregated_diurnal_cycle_df = (
            compound_timeseries.groupby(
                grouper,
            )
            .agg(**get_agg_funcs(method))
            .reset_index()
        )
        # Rename columns after aggregation
        aggregated_diurnal_cycle_df = aggregated_diurnal_cycle_df.rename(
            columns=lambda col: col.replace("_mean", "").replace("_median", "")
        )
        aggregated_diurnal_cycle_df = add_categorial_columns(
            compound_timeseries=compound_timeseries,
            aggregated_df=aggregated_diurnal_cycle_df,
            group_by=(
                ["hour_of_day"] if not all_data else ["hour_of_day", "trace_name"]
            ),
            str_for_multiple=f"Diurnal Cycle {method}",
            all_data=all_data,
        )
        # Apply schema validation or parsers based on environment mode
        if MJW_DEV_MODE:
            return diurnal_cycle_schema.validate(aggregated_diurnal_cycle_df)
        # Apply parser functions directly
        aggregated_diurnal_cycle_df = missing_dispersion_values_to_zero(
            aggregated_diurnal_cycle_df
        )
        return aggregated_diurnal_cycle_df

    def add_untarget_peak(self, peak: float) -> None:
        """
        Add a single untarget peak to the added_untarget_peaks_cache attribute,
        which will be attached to timeseries.

        This method is used to add a peak to the timeseries data.
        It checks if the peak is valid and if the dataset has a 'binning_intensity'
        property.
        If the peak is not found in the binning intensity matrix,
        it raises a ValueError.
        The method also clears the timeseries cache
        after adding the peak to ensure that the timeseries data is up-to-date.

        :param peak: The untarget peak (m/z value).
        :type peak: float
        """
        try:
            logger.debug("Adding untarget peak: %f", peak)

            def _get_reference_row(sample_item_id: str) -> dict:
                """
                Add a single selected peak to the added_untarget_peaks_cache attribute,
                which will be attached to timeseries.

                :param peak: The selected peak (m/z value).
                :type peak: float
                """
                match = self.timeseries[
                    self.timeseries["sample_item_id"] == sample_item_id
                ]
                return match.iloc[0].to_dict() if not match.empty else {}

            # Error handling
            if not isinstance(peak, (int, float)):
                error_message = f"Invalid peak value: {peak}. Must be a number."
                logger.error(error_message)
                raise ValueError(error_message)
            if not hasattr(self, "binning_intensity"):
                error_message = (
                    "The dataset does not have a 'binning_intensity' property. "
                    "Extend the dataset with BinningExtension and set parameters to enable this."
                )
                logger.error(error_message)
                raise AttributeError(error_message)

            # Extract the binning_intensity matrix
            binning_intensity = self.binning_intensity  # pylint: disable=E1101
            if peak not in binning_intensity.index:
                error_message = (
                    f"Peak {peak} not found in the binning intensity matrix."
                )
                logger.error(error_message)
                raise ValueError(error_message)

            # Get the single row for the selected peak
            row = binning_intensity.loc[peak]

            # Prepare the new peak data
            new_peaks_data = []
            for (datetime, sample_item_id), intensity in row.items():
                reference_row = _get_reference_row(sample_item_id)
                new_peaks_data.append(
                    {
                        "target_compound_id": None,
                        "target_compound_name": None,
                        "target_compound_formula": None,
                        "intensity": 0 if pd.isna(intensity) else intensity,
                        "datetime": datetime,
                        "datetime_utc": reference_row.get("datetime_utc"),
                        "sample_item_id": sample_item_id,
                        "sample_item_name": reference_row.get(
                            "sample_item_name", f"Sample {sample_item_id}"
                        ),
                        "unit": self.intensity_unit,  # pylint: disable=E1101
                        "filename": reference_row.get("filename"),
                        "filter_id": reference_row.get("filter_id"),
                        "tic": reference_row.get("tic"),
                        "instrument": reference_row.get("instrument"),
                        "sample_item_type": reference_row.get("sample_item_type"),
                        "trace_name": str(peak),
                        "match_category": None,
                        "match_compound_id": None,
                        "match_score": None,
                    }
                )
            logger.debug("Prepared new peak data for peak: %f", peak)
            # Append the new peak to the `added_untarget_peaks_cache` attribute
            new_peaks_df = pd.DataFrame(new_peaks_data)
            self.added_untarget_peaks_cache = pd.concat(
                [self.added_untarget_peaks_cache, new_peaks_df], ignore_index=True
            )
            logger.info(
                "Added new peak data to the timeseries cache for peak: %f", peak
            )

            # Clear only the cache for timeseries
            if "timeseries" in self.__dict__:
                self.__dict__.pop("timeseries")
                logger.debug("Cleared the timeseries cache after adding peak: %f", peak)

        except (
            AttributeError,
            ValueError,
            TypeError,
        ) as e:
            logger.error("Error in add_untarget_peak for peak: %f: %s", peak, e)
            raise


def add_categorial_columns(
    compound_timeseries: pd.DataFrame,
    aggregated_df: pd.DataFrame,
    group_by: list,
    str_for_multiple: str,
    all_data: bool = False,
) -> pd.DataFrame:
    """
    Add categorical columns after grouping to the aggregated dataframe.

    This function handles the addition of categorical columns
    to the aggregated dataframe after grouping.
    It ensures that the categorical columns are correctly resolved
    and merged into the aggregated dataframe.
    The function also handles cases where multiple values exist
    for the same aggregated time point.
    The categorical columns are defined in the check_cols list,
    and the function uses the resolve_multiple_values function
    to handle cases where multiple values exist for the same time point.
    The function returns the aggregated dataframe with the added categorical columns.

    :param compound_timeseries: Original compound timeseries data
    :type compound_timeseries: pd.DataFrame
    :param aggregated_df: Dataframe to which categorical columns are added
    :type aggregated_df: pd.DataFrame
    :param group_by: List of columns to group by
    :type group_by: list
    :param str_for_multiple: String to use when multiple categorial values
    for same aggregated time point
    :type str_for_multiple: str
    :param all_data: Whether to group by all data or just specific compound data
    :type all_data: bool, Default to False
    :return: Aggregated dataframe with added categorical columns
    :rtype: pd.DataFrame
    """
    # Define the columns to check for categorical values
    check_cols = [
        "match_compound_id",
        "sample_item_id",
        "sample_item_name",
        "target_compound_id",
        "match_category",
        "unit",
        "target_compound_name",
        "target_compound_formula",
        "filename",
        "filter_id",
        "instrument",
        "sample_item_type",
        "trace_name" if not all_data else None,
        "date",
    ]
    # Remove None values (if alldata is True, the column will not be added)
    check_cols = [col for col in check_cols if col is not None]
    # Apply transformation to relevant columns
    grouped = (
        compound_timeseries.groupby(group_by)[check_cols]
        .agg(
            lambda series: resolve_multiple_values(
                series=series, str_for_multiple=str_for_multiple
            )
        )
        .reset_index()
    )
    # Extract the Grouper column names and append the rest
    group_by_columns = [g.key for g in group_by if isinstance(g, pd.Grouper)]
    ## Append other columns that are not pd.Grouper (strings)
    group_by_columns += [g for g in group_by if not isinstance(g, pd.Grouper)]
    # Merge the categorical columns back into aggregated_df
    aggregated_df = aggregated_df.merge(grouped, on=group_by_columns, how="left")
    aggregated_df["aggregate"] = str_for_multiple

    return aggregated_df


def resolve_multiple_values(series: pd.Series, str_for_multiple: str) -> str:
    """
    Handle categorical columns manually.

    This function checks for unique values in a categorical column
    and returns a specific string if multiple values exist.
    If only one unique value exists, it returns that value.
    If no values exist, it returns "UNKNOWN".

    :param series: categorical column from dataframe which is aggregated
    :type series: pd.Series
    :param str_for_multiple: 'str' used in cases of multiple values
    after aggregation
    :type str_for_multiple: str
    :return: of multiple returns str_for_multiple;
    if unique returns it
    :rtype: str
    """
    unique_values = series.dropna().unique()
    if len(unique_values) == 0:
        return "UNKNOWN"
    return unique_values[0] if len(unique_values) == 1 else str_for_multiple


def get_agg_funcs(method: Literal["mean", "median"]) -> dict:
    """
    Dynamically defines aggregation functions
    based on method ('mean' or 'median').

    This function returns a dictionary of aggregation functions
    for the specified method.
    The aggregation functions are defined for the following columns:
    "intensity", "match_score", "tic", and "sample_peak_interference_sum".

    :param method: user defined method
    :type method: Literal["mean", "median"]
    :raises ValueError: when wrong method is given
    ('mean' or 'median' allowed)
    :return: dictionary containing correct
    pair (('_mean' and '_std') OR ('_median' and '_mad'))
    :rtype: dict
    """

    # Define columns to aggregate dynamically
    columns = [
        "intensity",
        "match_score",
        "tic",
        "sample_peak_interference_sum",
    ]
    # Define aggregation functions dynamically
    match method:
        case "mean":
            return {f"{col}_mean": (col, "mean") for col in columns} | {
                f"{col}_std": (col, "std") for col in columns
            }
        case "median":
            return {f"{col}_median": (col, "median") for col in columns} | {
                f"{col}_mad": (
                    col,
                    lambda x: np.median(
                        np.abs(x - np.median(x))
                    ),  # Median Absolute Deviation (MAD)
                )
                for col in columns
            }
        case _:
            raise ValueError(
                f"Unsupported method: {method}. Choose from 'mean' or 'median'."
            )
