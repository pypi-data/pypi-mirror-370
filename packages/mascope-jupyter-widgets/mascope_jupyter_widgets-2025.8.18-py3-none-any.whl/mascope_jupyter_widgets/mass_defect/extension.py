from functools import cached_property
from typing import Literal
import pandas as pd
import pandera as pa
from pandarallel import pandarallel

from .schemas import (
    peaks_mass_defect_schema,
    peaks_mass_defect_scaled_schema,
    calculate_mz_round_and_mass_defects_to_columns,
    calculate_min_max_intensity,
    calculate_log_values,
    add_trace_name_column,
    set_unique_index,
)
from ..mascope_data.access import (
    get_mjw_mode,
)

MJW_DEV_MODE = get_mjw_mode()  # Get the MJW_DEV_MODE environment variable
base_units = {
    "c1H": 1.007825,
    "c12C": 12,
    "c13C": 13.003355,
    "c14N": 14.003074,
    "c15N": 15.000109,
    "c16O": 15.994915,
    "cNO2": 46.0055,
    "cCO": 28.0101,
    "cCH2": 14.01565,
    "cC2H2": 26.04,
    "cCH4": 16.043,
    "cC2H4": 28.05,
    "cC3H6": 42.08,
    "cC2H4O": 44.0262,
    "c32S": 31.972072,
    "cC6H10O5": 162.0528,
    "cIsoprene": 68.06260,
}  # Base units for mass defect scaling calculation


class MassDefectDataExtension:
    """
    Mass defect related extension
    for MascopeDataWrapper -dataset.
    """

    @cached_property
    def peaks_mass_defect(self) -> pd.DataFrame:
        """
        Mascope peak-level dataframe (if peaks imported, otherwise match_data)
        with mass defect specific columns for sample-specific data.

        - This method is used to calculate the mass defect for each peak in the dataset.
        - It uses the `peaks_or_match_data` method of the dataset to access
        the 'peak_matched' data if available and falls back to the `match_data` if not.
        - The method applies a schema validation or parsers based on the environment mode
        (MJW_DEV_MODE).
            + If the mode is set to development, it validates the data using
            the `peaks_mass_defect_schema`.
            + Otherwise, it applies parser functions directly
            to the data.

        :return: peak-level dataframe with 'mz_round' and 'mass_defect'
        columns added by pandera parsers
        :rtype: pd.DataFrame
        """

        peaks_mass_defect = (
            self.peaks_or_match_data  # pylint: disable=E1101
        )  # MascopeDataWrapper.peaks_or_match_data
        peaks_mass_defect = peaks_mass_defect.where(pd.notna(peaks_mass_defect), None)

        # Apply schema validation or parsers based on environment mode
        if MJW_DEV_MODE:
            return peaks_mass_defect_schema.validate(peaks_mass_defect)
        # Apply parser functions directly
        peaks_mass_defect = calculate_mz_round_and_mass_defects_to_columns(
            peaks_mass_defect
        )
        peaks_mass_defect = set_unique_index(peaks_mass_defect)
        return peaks_mass_defect

    @cached_property
    @pa.check_output(peaks_mass_defect_schema)
    def peaks_grouped_mass_defect(self) -> pd.DataFrame:
        """
        Mascope grouped peak-level dataframe (if peaks imported, otherwise match_data)
        with mass defect specific columns for sample-specific data

        - This method is used to calculate the mass defect for each mz-group
        'intensity weighted mz mean' in the `peaks_grouped` property of the dataset.
        - The method also handles the aggregation of columns based on their data types
        (numeric, datetime, categorical) and applies appropriate aggregation functions.
        - After the aggregation, it filters the columns to match the schema
        defined in `peaks_mass_defect_schema` and drops duplicate rows according 'mz_weighted_mean'.

        - The method applies a schema validation or parsers based on the environment mode
        (MJW_DEV_MODE).
            + If the mode is set to development, it validates the data using
            the `peaks_mass_defect_schema`.
            + Otherwise, it applies parser functions directly
            to the data.

        :return: grouped peak-level dataframe with 'mz_round' and 'mass_defect'
        columns added by pandera parsers
        :rtype: pd.DataFrame
        """

        pandarallel.initialize(verbose=0)

        if not hasattr(self, "peaks_grouped") or not isinstance(
            self.peaks_grouped,  # pylint: disable=E1101
            pd.DataFrame,  # MascopeDataWrapper.peaks_grouped
        ):
            raise AttributeError(
                "The dataset does not have a 'peaks_grouped' property. "
                "Extend the dataset with BinningExtension to enable this."
            )
        peaks_grouped_mass_defect = (
            self.peaks_grouped.copy()  # pylint: disable=E1101 # MascopeDataWrapper.peaks_grouped
        )

        def aggregate_group(group):
            import pandas as pd  # pylint: disable=import-outside-toplevel disable=redefined-outer-name disable=reimported

            result = {}

            # Iterate over columns and their data types
            for column_name, dtype in group.dtypes.items():
                column = group[column_name]
                match dtype:
                    case _ if pd.api.types.is_numeric_dtype(dtype):
                        # Numeric columns: Aggregate by mean or first value
                        result[column_name] = (
                            column.mean() if column.nunique() > 1 else column.iloc[0]
                        )
                    case _ if pd.api.types.is_datetime64_any_dtype(dtype):
                        # Datetime columns: Aggregate based on time range
                        min_datetime = column.min()
                        max_datetime = column.max()
                        time_range = max_datetime - min_datetime
                        match time_range:
                            case _ if time_range <= pd.Timedelta(days=1):
                                result[column_name] = min_datetime.floor("h")
                            case _ if time_range <= pd.Timedelta(days=7):
                                result[column_name] = min_datetime.floor("D")
                            case _ if time_range <= pd.Timedelta(days=30):
                                result[column_name] = min_datetime.to_period(
                                    "W"
                                ).start_time
                            case _:
                                result[column_name] = min_datetime.to_period(
                                    "M"
                                ).start_time
                    case _:
                        # Categorical or object columns
                        non_null_values = column.dropna().unique()
                        special_columns = {
                            "target_compound_name",
                            "target_compound_formula",
                            "target_ion_formula",
                        }

                        match len(non_null_values):
                            case 0:  # No non-null values
                                result[column_name] = None
                            case 1:  # Only one unique value
                                result[column_name] = non_null_values[0]
                            case _ if column_name in special_columns:
                                result[column_name] = "; ".join(
                                    map(str, non_null_values)
                                )
                            case _:  # More than one unique value
                                has_duplicate_sample_item_id = (
                                    group["sample_item_id"].duplicated().any()
                                    if "sample_item_id" in group.columns
                                    else False
                                )
                                duplicate_info = (
                                    "Duplicates in sample_item_id"
                                    if has_duplicate_sample_item_id
                                    else "No duplicates in sample_item_id"
                                )
                                result[column_name] = (
                                    f"Aggregation: mean, Total count: {len(column)}, "
                                    f"{duplicate_info}"
                                )

            return pd.Series(result)

        # Group by "mz_weighted_mean" and update the DataFrame
        peaks_grouped_mass_defect = peaks_grouped_mass_defect.groupby(
            "mz_weighted_mean"
        ).parallel_apply(aggregate_group)

        # Select only one row per group
        peaks_grouped_mass_defect = peaks_grouped_mass_defect.drop_duplicates(
            subset=["mz_weighted_mean"]
        )
        # Reset the index to avoid ambiguity between index and column labels and sort values
        peaks_grouped_mass_defect = peaks_grouped_mass_defect.reset_index(
            drop=True
        ).sort_values(["mz_weighted_mean", "datetime"])
        # Edit to correspond to peaks_mass_defect schema
        peaks_grouped_mass_defect["mz"] = peaks_grouped_mass_defect["mz_weighted_mean"]
        peaks_grouped_mass_defect["sample_item_id"] = "binned peaks"
        peaks_grouped_mass_defect["sample_item_name_datetime"] = "binned peaks"
        # Filter columns to match peaks_mass_defect_schema
        allowed_columns = set(peaks_mass_defect_schema.columns.keys())
        peaks_grouped_mass_defect = peaks_grouped_mass_defect[
            [col for col in peaks_grouped_mass_defect.columns if col in allowed_columns]
        ]
        # Ensure all values even midnight has UTC timezone
        peaks_grouped_mass_defect["datetime_utc"] = pd.to_datetime(
            peaks_grouped_mass_defect["datetime_utc"], utc=True
        )
        # Ensure all values are None if NaT or NaN
        peaks_grouped_mass_defect = peaks_grouped_mass_defect.where(
            pd.notna(peaks_grouped_mass_defect), None
        )
        # Apply schema validation or parsers based on environment mode
        if MJW_DEV_MODE:
            return peaks_mass_defect_schema.validate(peaks_grouped_mass_defect)
        # Apply parser functions directly
        peaks_grouped_mass_defect = calculate_mz_round_and_mass_defects_to_columns(
            peaks_grouped_mass_defect
        )
        peaks_grouped_mass_defect = set_unique_index(peaks_grouped_mass_defect)
        return peaks_grouped_mass_defect

    @property
    def base_units(self) -> dict:
        """
        Initialize base units for mass defect calculation.

        :return: Dictionary of base units for mass defect calculation.
        :rtype: dict
        """
        return base_units

    def add_base_unit(self, unit_name: str, mass_value: float) -> None:
        """
        Add a new base unit to 'base_units' for mass defect scaling.

        :param unit_name: Name of the new base unit.
        :param mass_value: Mass value associated with the new base unit.
        """
        if unit_name in base_units:
            raise ValueError(f"Base unit '{unit_name}' already exists.")
        else:
            base_units[unit_name] = mass_value

    def calculate_scaled_mass_defect(
        self,
        mass_defect_method: Literal["MD", "KMD", "KMD_base", "REKMD", "SKMD"],
        mz_normalization_method: callable,
        base_unit: str = None,
        integer_scaling_factor: float = None,
        binned_data: bool = False,
    ) -> pd.DataFrame:
        """
        Calculate Scaled Mass Defect based on the given method, base_unit
        and integer scaling value.

        - The method handles the calculation of the Kendrick mass defect
        based on the provided method, base unit and integer scaling factor.
        - It adds a new column 'kendrick_mass_defect' to the DataFrame
        with the calculated mass defect values, and a 'kendrick_method' column to the DataFrame
        indicating the method used for calculation.
        - The method also validates the input parameters and raises a ValueError
        if any of the required parameters are missing.

        - The method applies a schema validation or parsers based on the environment mode
        (MJW_DEV_MODE).
            + If the mode is set to development, it validates the data using
            the `peaks_mass_defect_scaled_schema`.
            + Otherwise, it applies parser functions directly

        :param mass_defect_method: Method to use for calculating the Kendrick mass defect.
        :type mass_defect_method: Literal["MD", "KMD", "KMD_base", "REKMD", "SKMD"]
        :param mz_normalization_method: Function to apply for normalization.
        'floor', 'ceil', 'round'
        :type mz_normalization_method: callable
        :param base_unit: Base unit for calculation.
        :type base_unit: str
        :param integer_scaling_factor: integer scaling factor.
        :type integer_scaling_factor: float
        :param binned_data: If True, use binned data (peaks_grouped_mass_defect) for calculations.
        If False, use unbinned data (peaks_mass_defect).
        :type binned_data: bool
        :return: Updated DataFrame with 'kendrick_mass_defect' -column for scaled mass-defect
        and 'kendrick_method' -column which shows used method, base_unit and
        integer scaling value.
        :rtype: pd.DataFrame
        """
        if binned_data:
            if not hasattr(self, "peaks_grouped"):
                raise AttributeError(
                    "When 'binned_data' is True, the dataset must have a 'peaks_grouped' property."
                    "Extend dataset with BinningExtension to enable this."
                )
            peaks_mass_defect = self.peaks_grouped_mass_defect.copy()
        else:
            peaks_mass_defect = self.peaks_mass_defect
        if mass_defect_method != "KMD" and (
            base_unit is None
            or integer_scaling_factor is None
            or self.base_units is None
        ):
            raise ValueError(
                "To calculate any method other than basic mass defect ('MD'), "
                "please provide the following parameters:\n"
                "- 'base_unit': Key from list dataset.base_units \n"
                "- 'mass_defect_method': one of ('KMD_base', 'REKMD', 'SKMD')\n"
                "- 'integer_scaling_factor': an integer scaling factor"
            )
        match mass_defect_method:
            case "KMD":
                peaks_mass_defect["kendrick_mass_defect"] = peaks_mass_defect[
                    "mz"
                ] - mz_normalization_method(peaks_mass_defect["mz"])
            case "KMD_base":
                base_km = (
                    mz_normalization_method(self.base_units[base_unit])
                    / self.base_units[base_unit]
                )
                peaks_mass_defect["kendrick_mass_defect"] = peaks_mass_defect[
                    "mz"
                ] * base_km - mz_normalization_method(peaks_mass_defect["mz"] * base_km)
            case "REKMD":
                base_km = mz_normalization_method(
                    self.base_units[base_unit] / integer_scaling_factor
                ) / (self.base_units[base_unit] / integer_scaling_factor)
                peaks_mass_defect["kendrick_mass_defect"] = peaks_mass_defect[
                    "mz"
                ] * base_km - mz_normalization_method(peaks_mass_defect["mz"] * base_km)
            case "SKMD":
                base_km = integer_scaling_factor / self.base_units[base_unit]
                peaks_mass_defect["kendrick_mass_defect"] = peaks_mass_defect[
                    "mz"
                ] * base_km - mz_normalization_method(peaks_mass_defect["mz"] * base_km)
            case _:
                raise ValueError(f"Invalid mass defect method: {mass_defect_method}")
        # Build kendrick_method string with only used parameters
        method_parts = [mass_defect_method]
        if base_unit is not None and mass_defect_method in {
            "KMD_base",
            "REKMD",
            "SKMD",
        }:
            method_parts.append(str(base_unit))
        if integer_scaling_factor is not None and mass_defect_method in {
            "REKMD",
            "SKMD",
        }:
            method_parts.append(str(integer_scaling_factor))
        peaks_mass_defect["kendrick_method"] = ", ".join(method_parts)
        # Apply schema validation or parsers based on environment mode
        if MJW_DEV_MODE:
            return peaks_mass_defect_scaled_schema.validate(peaks_mass_defect)
        # Apply parser functions directly
        peaks_mass_defect = calculate_min_max_intensity(peaks_mass_defect)
        peaks_mass_defect = calculate_log_values(peaks_mass_defect)
        peaks_mass_defect = add_trace_name_column(peaks_mass_defect)

        return peaks_mass_defect
