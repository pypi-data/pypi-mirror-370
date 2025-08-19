from typing import Literal, Union, Callable
from functools import cached_property
from traitlets import HasTraits, Int
import numpy as np
import pandas as pd

from .schemas import (
    peaks_grouped_schema,
    binning_intensity_schema,
    binning_mz_schema,
    binning_count_schema,
    binning_norm_intensity_schema,
    add_weighted_mz_mean,
    add_statistics,
    set_unique_index,
)
from ..mascope_data.access import (
    get_mjw_mode,
)

MJW_DEV_MODE = get_mjw_mode()  # Get the MJW_DEV_MODE environment variable


class BinningExtension(HasTraits):
    """
    Extension-class for grouping mz-values
    to bins from multiple samples."""

    binning_parameters_changed = Int(default_value=0).tag(
        sync=True
    )  # Flag to indicate parameter changes

    def __init__(self) -> None:
        """Initialize the BinningExtension class."""
        super().__init__()
        self.binning_parameters = dict()

    @cached_property
    def peaks_grouped(
        self,
    ) -> pd.DataFrame:
        """
        Groups mz-values to bins based on the selected method.

        - This method uses the binning parameters set in `set_binning_parameters`
        to group the mz-values in the peaks DataFrame.
        - The method can be either 'groupby_isclose' or 'groupby_isclose_dynamic',
        depending on the user's choice.
        - The resulting DataFrame will contain additional
        columns for the mz_group and dynamic_rtol.
        - The method applies schema validation or parsers based on the environment mode
        (MJW_DEV_MODE).
            + If the mode is set to development, it validates the data using
            the `peaks_grouped_schema`.
            + Otherwise, it applies parser functions directly
            to the data.


        :raises ValueError: If no binning parameters have been set.
        :return: Grouped peaks DataFrame with additional columns
        for mz_group and dynamic_rtol.
        :rtype: pd.DataFrame
        """

        # Ensure the method and parameters are set
        if (
            not self.binning_parameters
            or "binning_method" not in self.binning_parameters
            or "kwargs" not in self.binning_parameters
        ):
            raise ValueError(
                "No binning parameters have been set. "
                "Please call `set_binning_parameters` first."
            )
        # Get the peaks DataFrame
        peaks = (
            self.peaks_or_match_data  # pylint: disable=E1101
        )  # MascopeDataWrapper.peaks_or_match_data  # Use the peaks or match_data
        # Retrieve the cached parameters
        binning_method = self.binning_parameters["binning_method"]
        kwargs = self.binning_parameters["kwargs"]
        # Sort the peaks by mz
        peaks = peaks.sort_values("mz")
        # Apply the binning method directly
        result = binning_method(peaks["mz"], **kwargs)
        # Unpack the result
        if isinstance(result, tuple):
            mz_groups, dynamic_rtol_values = result
            peaks["dynamic_rtol"] = dynamic_rtol_values
        else:
            mz_groups = result
        # Add new columns
        peaks["mz_group"] = mz_groups
        peaks["binning_method"] = (
            f"{binning_method.__name__}({kwargs})"  # Store the used method and parameters
        )
        # Apply schema validation or parsers based on `develop_mode`
        if MJW_DEV_MODE:
            return peaks_grouped_schema.validate(peaks)
        # Apply parser functions directly
        peaks = add_weighted_mz_mean(peaks)
        peaks = add_statistics(peaks)
        peaks = set_unique_index(peaks)
        return peaks

    @cached_property
    def binning_intensity(self) -> pd.DataFrame:
        """
        Cached property for the intensity matrix.

        1. Groups the data by mz_weighted_mean, datetime, and sample_item_id.
        2. The resulting DataFrame is reshaped to create a pivot table

        - Aggregation function is set to 'max' by default. This will control which
        values are used for the pivot table in case multiple peaks from same sample.
        - If you want to use a different aggregation function,
        you can set it in the binning_parameters dictionary.
        - The method applies schema validation or parsers based on the environment mode
        (MJW_DEV_MODE).
            + If the mode is set to development, it validates the data using
            the `binning_intensity_schema`.
            + Otherwise, it applies parser functions directly
            to the data.

        :return: _intensity matrix for the peaks_grouped DataFrame.
        :rtype: pd.DataFrame
        """
        binning_intensity = (
            self.peaks_grouped.groupby(
                ["mz_weighted_mean", "datetime", "sample_item_id"]
            )["intensity"]
            .agg(self.binning_parameters["aggfunc"])  # Apply the aggregation function
            .unstack(level=["datetime", "sample_item_id"])  # Reshape the data
        )
        binning_intensity = binning_intensity.sort_index(
            axis=1, level="datetime"
        )  # Ensure columns are sorted by 'datetime'
        if MJW_DEV_MODE:
            binning_intensity = binning_intensity_schema.validate(binning_intensity)

        return binning_intensity

    @cached_property
    def binning_mz(self) -> pd.DataFrame:
        """
        Cached property for the mz matrix.

        1. The method filters the peaks_grouped DataFrame
        based on the binning_intensity values
        2. Groups the data by mz_weighted_mean, datetime, and sample_item_id.
        3. The resulting DataFrame is reshaped to create a pivot table

        - The method applies schema validation or parsers based on the environment mode
        (MJW_DEV_MODE).
            + If the mode is set to development, it validates the data using
            the `binning_mz_schema`.
            + Otherwise, it applies parser functions directly
            to the data.

        :return: _mz matrix for the peaks_grouped DataFrame.
        :rtype: pd.DataFrame
        """

        filtered_df = self.peaks_grouped[
            self.peaks_grouped["intensity"].isin(self.binning_intensity.values.ravel())
        ]
        filtered_df = filtered_df.sort_values(["mz_weighted_mean", "datetime"])
        binning_mz = (
            filtered_df.groupby(["mz_weighted_mean", "datetime", "sample_item_id"])[
                "mz"
            ]
            .agg(self.binning_parameters["aggfunc"])  # Apply the aggregation function
            .unstack(level=["datetime", "sample_item_id"])  # Reshape the data
        )
        binning_mz = binning_mz.sort_index(
            axis=1, level="datetime"
        )  # Ensure columns are sorted by 'datetime'
        # Apply schema validation or parsers based on `develop_mode`
        if MJW_DEV_MODE:
            binning_mz = binning_mz_schema.validate(binning_mz)

        return binning_mz

    @cached_property
    def binning_count(self) -> pd.DataFrame:
        """
        Cached property for the count matrix.
        1. Groups the data by mz_weighted_mean, datetime, and sample_item_id.
        2. Counts the number of occurrences of each group.
        2. The resulting DataFrame is reshaped to create a pivot table containing the counts.
        - The method applies schema validation or parsers based on the environment mode
        (MJW_DEV_MODE).
            + If the mode is set to development, it validates the data using
            the `binning_count_schema`.
            + Otherwise, it applies parser functions directly
            to the data.

        :return: _count matrix for the peaks_grouped DataFrame.
        :rtype: pd.DataFrame
        """

        binning_count = (
            self.peaks_grouped.groupby(
                ["mz_weighted_mean", "datetime", "sample_item_id"]
            )
            .size()  # Count the number of occurrences
            .unstack(
                level=["datetime", "sample_item_id"], fill_value=0
            )  # Reshape the data
        )
        binning_count = binning_count.sort_index(
            axis=1, level="datetime"
        )  # Ensure columns are sorted by 'datetime'
        # Apply schema validation or parsers based on `develop_mode`
        if MJW_DEV_MODE:
            binning_count = binning_count_schema.validate(binning_count)

        return binning_count

    @cached_property
    def binning_norm_intensity(self) -> pd.DataFrame:
        """
        Cached property for the tic-normalized intensity matrix.

        1. The method filters the peaks_grouped DataFrame
        based on the binning_intensity values.
        2. Groups the data by mz_weighted_mean, datetime, and sample_item_id.
        3. The resulting DataFrame is reshaped to create a pivot table containing the
        tic-normalized intensity values.
        - The method applies schema validation or parsers based on the environment mode
        (MJW_DEV_MODE).
            + If the mode is set to development, it validates the data using
            the `binning_norm_intensity_schema`.
            + Otherwise, it applies parser functions directly
            to the data.

        :return: tic-normalized intensity matrix for the peaks_grouped DataFrame.
        :rtype: pd.DataFrame
        """

        filtered_df = self.peaks_grouped[
            self.peaks_grouped["intensity"].isin(self.binning_intensity.values.ravel())
        ]
        filtered_df = filtered_df.sort_values(["mz_weighted_mean", "datetime"])
        binning_norm_intensity = (
            filtered_df.groupby(["mz_weighted_mean", "datetime", "sample_item_id"])[
                "norm_intensity"
            ]
            .agg(self.binning_parameters["aggfunc"])  # Apply the aggregation function
            .unstack(level=["datetime", "sample_item_id"])  # Reshape the data
        )
        binning_norm_intensity = binning_norm_intensity.sort_index(
            axis=1, level="datetime"
        )  # Ensure columns are sorted by 'datetime'
        # Apply schema validation or parsers based on `develop_mode`
        if MJW_DEV_MODE:
            binning_norm_intensity = binning_norm_intensity_schema.validate(
                binning_norm_intensity
            )

        return binning_norm_intensity

    def set_binning_parameters(
        self,
        binning_method: Literal["groupby_isclose", "groupby_isclose_dynamic"],
        aggfunc: Union[str, Callable] = "max",  # Allow strings or callables
        **kwargs,
    ) -> None:
        """
        Set the binning parameters and cache them for use in the peaks_grouped property.

        This method allows you to specify the binning method and any additional
        parameters required for that method. The binning method can be either
        'groupby_isclose' or 'groupby_isclose_dynamic'.
        The aggregation function can be a string (e.g., 'sum', 'mean', 'max')
        or a callable custom build method.


        :param binning_method: The binning method to use
        :type binning_method: Literal["groupby_isclose", "groupby_isclose_dynamic"]
        :param aggfunc: Aggregation function to use for matrix calculations.
        Can be a string (e.g., 'sum', 'mean', 'max') or a callable custom build method.
        :type aggfunc: Union[str, Callable]
        :param kwargs: Additional parameters for the selected binning method.
        :type kwargs: dict
        """

        method_map = {
            "groupby_isclose": self.groupby_isclose,
            "groupby_isclose_dynamic": self.groupby_isclose_dynamic,
        }
        if binning_method not in method_map:
            raise ValueError(
                "Invalid method. Choose 'groupby_isclose' or 'groupby_isclose_dynamic'."
            )
        allowed_aggfuncs = [
            "sum",
            "mean",
            "min",
            "max",
            "median",
            "std",
            "var",
            "count",
            "first",
            "last",
            "prod",
        ]
        if not (callable(aggfunc) or aggfunc in allowed_aggfuncs):
            raise ValueError(
                f"Invalid aggregation function '{aggfunc}'. "
                f"Allowed values are: {allowed_aggfuncs} or any callable."
            )
        # Cache the method and parameters
        self.binning_parameters = {
            "binning_method": method_map[binning_method],
            "kwargs": kwargs,  # Store the additional parameters
            "aggfunc": aggfunc,  # Store the aggregation function
        }
        # Clear the cache only if peaks_grouped is already calculated and not empty
        if (
            "peaks_grouped" in self.__dict__
            and self.__dict__["peaks_grouped"] is not None
            and not self.__dict__["peaks_grouped"].empty
        ):
            self.clear_cache()  # pylint: disable=E1101
            # MascopeDataWrapper.clear_cache()

        self.binning_parameters_changed += (
            1  # Change the flag to indicate parameters have changed
        )

    def groupby_isclose_dynamic(
        self,
        series: pd.Series,
        base_rtol: float = 0,
        scale_factor: float = 1.0,
        method: Literal["sqrt", "exp", "log", "log_alpha"] = "log",
        alpha: float = 1.0,  # Used only if method is 'log_alpha'
        atol: float = 0,
    ) -> pd.Series:
        """
        Groups mz-features dynamically based on
        different methods for scaling rtol.

        This method allows you to specify the base rtol in ppm, scale factor,
        and the method for dynamic rtol calculation. The method can be
        'log', 'sqrt', 'exp', or 'log_alpha'. The alpha parameter is
        used only if the method is 'log_alpha'.
        The method returns a Series with the same index as the input
        series, where each value is the group number for that mz-feature.
        The dynamic rtol is calculated based on the specified method
        and the input series.
        The method also returns the dynamic rtol values used for each
        mz-feature.

        :param series: Series of mz-values.
        :type series: pd.Series
        :param base_rtol: Base rtol value.
        :type base_rtol: float
        :param scale_factor: Scale factor for adjusting rtol.
        :type scale_factor: float
        :param method: Method for dynamic rtol calculation.
        :type method: str
        :param alpha: Alpha parameter for 'log_alpha' method.
        :type alpha: float
        :param atol: Absolute tolerance value.
        :type atol: float
        :return: Grouping and dynamic tolerance values.
        :rtype: tuple[pd.Series, pd.Series]
        """
        if not isinstance(series, pd.Series):
            raise ValueError("s must be a pandas Series.")
        if base_rtol <= 0:
            raise ValueError("base_rtol must be greater than 0.")
        if scale_factor <= 0:
            raise ValueError("scale_factor must be greater than 0.")
        if method == "log_alpha" and (alpha is None or alpha <= 0):
            raise ValueError("alpha must be greater than 0 for 'log_alpha' method.")
        if atol < 0:
            raise ValueError("atol must be greater than or equal to 0.")
        if method not in ["log", "sqrt", "exp", "log_alpha"]:
            raise ValueError(
                "Unsupported method. Choose from 'log', 'sqrt', 'exp', 'log_alpha'."
            )

        # Calculate dynamic rtol based on the specified method
        epsilon = 1e-10  # Small value to avoid division by zero
        if method == "log":
            rtol_values = base_rtol / (
                1 + scale_factor * np.log(series / (series.min() + epsilon))
            )
        elif method == "sqrt":
            rtol_values = base_rtol / (
                1 + scale_factor * np.sqrt(series / (series.min() + epsilon))
            )
        elif method == "exp":
            rtol_values = base_rtol * np.exp(
                -scale_factor * (series / (series.min() + epsilon))
            )
        elif method == "log_alpha":
            rtol_values = (
                base_rtol
                / (1 + scale_factor * np.log(series / (series.min() + epsilon)))
                ** alpha
            )
        else:
            raise ValueError(
                "Unsupported method. Choose from 'log', 'sqrt', 'exp', 'log_alpha'."
            )
        # Calculate tolerance for grouping using rtol_values and atol
        tolerance = series * (rtol_values / 1e6) + atol
        # Identify groups using cumulative sum based on tolerance
        # Use diff() to find the difference between consecutive elements
        # Fill NaN values with 0 and check if the difference is greater than tolerance
        by = series.diff().fillna(0).gt(tolerance).cumsum()

        return (
            by,
            rtol_values,
        )  # Return the group and the dynamic tolerance used for each mz-value

    def groupby_isclose(
        self, series: pd.Series, atol: int = 0, rtol: int = 0
    ) -> pd.Series:
        """
        Groups all selected batch samples
        mz-features by given rtolerance.

        This method allows you to specify the absolute tolerance ppm (atol)
        and relative tolerance ppm (rtol) for grouping mz-features. The
        method returns a Series with the same index as the input
        series, where each value is the group number for that mz-feature.
        The grouping is done based on the specified tolerances.

        :param series: pd.Series containing values that will be grouped
        :type series: pd.Series
        :param atol: base tolerance if wanted to use, default=0
        :type atol: int
        :param rtol: ppm-threshold to use for binning/grouping
        :type rtol: int
        :return: pd.Series containing mz-group value for each mz-feature
        :rtype: pd.Series
        """

        if not isinstance(series, pd.Series):
            raise ValueError("s must be a pandas Series.")
        if rtol <= 0:
            raise ValueError("base_rtol must be greater than 0.")
        if atol < 0:
            raise ValueError("atol must be greater than or equal to 0.")
        # Calculate tolerance value:
        tolerance = atol + rtol * series / 1e6
        # Identify groups using cumulative sum based on tolerance
        # Use diff() to find the difference between consecutive elements
        # Fill NaN values with 0 and check if the difference is greater than tolerance
        by = series.diff().fillna(0).gt(tolerance).cumsum()

        return by
