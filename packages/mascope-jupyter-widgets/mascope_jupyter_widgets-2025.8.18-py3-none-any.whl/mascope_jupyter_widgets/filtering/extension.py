from traitlets import Bool, HasTraits
import numpy as np
import pandas as pd


def filter_decorator(func: callable) -> callable:
    """Decorator to apply filtering while preserving Pandera validation.

    This decorator is used to wrap properties in the FilteringExtension class.
    It checks if the property is a DataFrame and if filtering is enabled.
    If both conditions are met, it applies the filtering logic defined in the
    filter_data method of the parent object.

    :param func: The original property function to be wrapped.
    :type func: callable
    :return: A wrapper function that applies filtering if conditions are met.
    :rtype: callable
    """

    def wrapper(instance, *args, **kwargs):
        # Access the parent object (self) from the instance
        parent = instance.parent

        dataset_property = func(instance, *args, **kwargs)  # Call the original property
        if (
            isinstance(
                dataset_property,
                pd.DataFrame,  # Check if the original property is a DataFrame
            )
            and parent.apply_filters  # Check if filtering is enabled
        ):  # Check if filtering is enabled  # If both conditions are met apply filtering
            return parent.filter_data(dataset_property)  # return filtered DataFrame
        return (
            dataset_property  # Return the original property if no filtering is applied
        )

    return wrapper


class FilteringExtension(HasTraits):
    """
    Filtering extension for MascopeDataWrapper.
    When wrapped with MascopeDataWrapper -dataset,
    this extension provides filtering to all properties
    in dataset.
    Filters can be specified using the set_filters method.
    When apply_filters is set to True, all properties
    will be filtered based on the specified criteria.
    Filtering can be also performed by using methods directly.
    Filters can be applied to the following properties:
    - peaks_matched (peak-level data)
    - match_samples (sample-level data)
    - match_compounds (compound-level data)
    - match_ions (ion-level data)
    - match_isotopes (isotope-level data)
    - match_data (match-data-level data)
    """

    apply_filters = Bool(False).tag(
        sync=True  # Flag to switch between filtered and non-filtered data
    )

    def __init__(self):
        """
        Initialize filtering parameters.
        Filtering parameters can be set using the set_filters method.
        """
        super().__init__()
        self.samples = None  # List of sample names in 'sample_item_id' format
        self.mz_range = (
            None  # Tuple specifying the lower and upper bounds for m/z values
        )
        self.intensity_threshold = None  # Intensity threshold for filtering
        self.cumsum_threshold = (
            None  # Cumulative TIC ratio from high-to-low as percentage
        )
        self.time_range = None  # Tuple specifying the start and end times for filtering
        self.exclude_masses = None  # List of unit masses to exclude
        self.range_tolerance = 0.5  # Tolerance for mass range when excluding masses

    def set_filters(
        self,
        samples: list[str] = None,
        mz_range: tuple[float, float] = None,
        intensity_threshold: float = None,
        cumsum_threshold: float = None,
        time_range: tuple[pd.Timestamp, pd.Timestamp] = None,
        exclude_masses: list[int] = None,
    ) -> None:
        """Set all filtering parameters.

        :param samples: List of sample names in 'sample_item_id' format
        to filter by, defaults to None.
        :type samples: list[str], optional
        :param mz_range: Tuple specifying the lower and upper bounds
        for m/z values, defaults to None.
        :type mz_range: tuple[float, float], optional
        :param intensity_threshold: Intensity threshold for filtering, defaults to None.
        :type intensity_threshold: float, optional
        :param cumsum_threshold: Cumulative TIC ratio from high-to-low
        percentage threshold for filtering, defaults to None.
        :type cumsum_threshold: float, optional
        :param time_range: Tuple specifying the start and end times for filtering, defaults to None.
        :type time_range: tuple[pd.Timestamp, pd.Timestamp], optional
        :param exclude_masses: List of unit masses to exclude, defaults to None.
        :type exclude_masses: list[int], optional
        """

        self.samples = samples
        self.mz_range = mz_range
        self.intensity_threshold = intensity_threshold
        self.cumsum_threshold = cumsum_threshold
        self.time_range = time_range
        self.exclude_masses = exclude_masses
        # Trigger filtering logic by toggling apply_filters
        if not self.apply_filters:
            print("Setting apply_filters to True")
            self.set_trait("apply_filters", True)
        else:
            # Explicitly notify observers of unchanged value
            self.notify_change(
                {
                    "type": "change",
                    "name": "apply_filters",
                    "old": True,
                    "new": True,
                    "owner": self,
                }
            )

    def filter_data(self, dataset_property: pd.DataFrame) -> pd.DataFrame:
        """
        Filter the DataFrame based on the provided
        filtering criteria.

        :param dataset_property: Any datasource pd.DataFrame
        :type dataset_property: pd.DataFrame
        :return: filtered dataframe or the original pd.DataFrame
        :rtype: pd.DataFrame
        """
        dataset_property = self.filter_by_sample(self.samples, dataset_property)
        dataset_property = self.filter_by_mz_range(self.mz_range, dataset_property)
        dataset_property = self.filter_by_intensity_threshold(
            self.intensity_threshold, dataset_property
        )
        dataset_property = self.filter_by_cumsum_threshold(
            self.cumsum_threshold, dataset_property
        )
        dataset_property = self.filter_by_time_range(self.time_range, dataset_property)
        dataset_property = self.filter_by_exclude_masses(
            self.exclude_masses, dataset_property
        )

        return dataset_property

    def filter_by_sample(
        self, samples: list, dataset_property: pd.DataFrame
    ) -> pd.DataFrame:
        """Filter the dataset by sample_item_id

        :param samples: list of sample_item_id to filter by
        :type samples: list
        :param dataset_property: Any datasource pd.DataFrame
        :type dataset_property: pd.DataFrame
        :return: filtered dataframe or the original pd.DataFrame
        :rtype: pd.DataFrame
        """

        if self.samples and "sample_item_id" in dataset_property.columns:
            dataset_property = dataset_property[
                dataset_property["sample_item_id"].isin(samples)
            ]

        return dataset_property

    def filter_by_mz_range(
        self, mz_range: tuple[float, float], dataset_property: pd.DataFrame
    ) -> pd.DataFrame:
        """Filter the dataset by mz range

        :param mz_range: Tuple specifying the lower and upper bounds for m/z values
        :type mz_range: tuple[float, float]
        :param dataset_property: Any datasource pd.DataFrame
        :type dataset_property: pd.DataFrame
        :return: filtered dataframe or the original pd.DataFrame
        :rtype: pd.DataFrame
        """
        match dataset_property.columns:
            case columns if "mz" in columns:
                mz_column = "mz"
            case columns if "target_isotope_mz" in columns:
                mz_column = "target_isotope_mz"
            case _:
                mz_column = None
        if self.mz_range and mz_column:
            dataset_property = dataset_property[
                (dataset_property[mz_column] >= mz_range[0])
                & (dataset_property[mz_column] <= mz_range[1])
            ]

        return dataset_property

    def filter_by_intensity_threshold(
        self, intensity_threshold: float, dataset_property: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Filter the dataset by intensity threshold.
        Intensity threshold should be given as a percentage.
        If peak-level data is used, the intensity threshold
        is calculated from the un-filtered peak-level data by using
        protected data-source attribute '_peaks' which contains always
        un-processed data.
        If peak-level data is not used, the intensity threshold
        is calculated from the un-filtered match-isotope data by using
        protected data-source attribute '_match_isotopes' which contains always
        un-processed data.


        :param intensity_threshold: Intensity threshold for filtering as percentage
        :type intensity_threshold: float
        :param dataset_property: Any datasource pd.DataFrame
        :type dataset_property: pd.DataFrame
        :return: filtered dataframe or the original pd.DataFrame
        :rtype: pd.DataFrame
        """
        if intensity_threshold is not None:
            match dataset_property.columns:
                case columns if "intensity" in columns:
                    intensity_column = "intensity"
                    source_df = (
                        self.data_source._peaks.copy()  # pylint: disable=protected-access disable=no-member
                    )
                case columns if "sample_peak_intensity_sum" in columns:
                    intensity_column = "sample_peak_intensity_sum"
                    source_df = (
                        self.data_source._match_isotopes.copy()  # pylint: disable=protected-access disable=no-member
                    )
                case columns if "sample_peak_intensity" in columns:
                    intensity_column = "sample_peak_intensity"
                    source_df = (
                        self.data_source._match_isotopes.copy()  # pylint: disable=protected-access disable=no-member
                    )
                case _:
                    intensity_column = None
                    source_df = None
            # Calculate intensity threshold
            if source_df is not None and intensity_column in source_df.columns:
                intensity_threshold = np.round(
                    np.percentile(
                        source_df[intensity_column].dropna(),
                        intensity_threshold,
                    ),
                    3,
                )
        if intensity_threshold is not None and intensity_column is not None:
            dataset_property = dataset_property[
                dataset_property[intensity_column] >= intensity_threshold
            ]

        return dataset_property

    def filter_by_cumsum_threshold(
        self, cumsum_threshold: float, dataset_property: pd.DataFrame
    ) -> pd.DataFrame:
        """Filter the dataset by cumulative TIC ratio threshold

        :param cumsum_threshold: Cumulative TIC ratio from high-to-low
        percentage threshold for filtering
        :type cumsum_threshold: float
        :param dataset_property: Any datasource pd.DataFrame
        :type dataset_property: pd.DataFrame
        :return: filtered dataframe or the original pd.DataFrame
        :rtype: pd.DataFrame
        """

        if (
            self.cumsum_threshold is not None
            and "cumsum_tic_ratio" in dataset_property.columns
        ):
            dataset_property = dataset_property[
                dataset_property["cumsum_tic_ratio"] <= (cumsum_threshold / 100)
            ]

        return dataset_property

    def filter_by_time_range(
        self,
        time_range: tuple[pd.Timestamp, pd.Timestamp],
        dataset_property: pd.DataFrame,
    ) -> pd.DataFrame:
        """Filter the dataset by time range

        :param time_range: Tuple specifying the start and end times for filtering
        :type time_range: tuple[pd.Timestamp, pd.Timestamp]
        :param dataset_property: Any datasource pd.DataFrame
        :type dataset_property: pd.DataFrame
        :return: filtered dataframe or the original pd.DataFrame
        :rtype: pd.DataFrame
        """
        if self.time_range and "datetime" in dataset_property.columns:
            dataset_property = dataset_property[
                (dataset_property["datetime"] >= time_range[0])
                & (dataset_property["datetime"] <= time_range[1])
            ]
        return dataset_property

    def filter_by_exclude_masses(
        self, exclude_masses: list[int], dataset_property: pd.DataFrame
    ) -> pd.DataFrame:
        """Filter the dataset by excluding unit masses

        :param exclude_masses: List of unit masses to exclude
        :type exclude_masses: list[int]
        :param dataset_property: Any datasource pd.DataFrame
        :type dataset_property: pd.DataFrame
        :return: filtered dataframe or the original pd.DataFrame
        :rtype: pd.DataFrame
        """
        match dataset_property.columns:
            case columns if "mz" in columns:
                mz_column = "mz"
            case columns if "target_isotope_mz" in columns:
                mz_column = "target_isotope_mz"
            case _:
                mz_column = None
        if exclude_masses and mz_column in dataset_property.columns:
            mask = pd.Series(False, index=dataset_property.index)
            for mass in exclude_masses:
                lower_bound = mass - self.range_tolerance
                upper_bound = mass + self.range_tolerance
                mask |= (dataset_property[mz_column] >= lower_bound) & (
                    dataset_property[mz_column] <= upper_bound
                )
            dataset_property = dataset_property[~mask]

        return dataset_property
