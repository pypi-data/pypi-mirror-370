from __future__ import annotations
import inspect
from functools import partial, cached_property
from types import MethodType
from traitlets import HasTraits, Bool, Int
import pandas as pd

from .schemas import (
    peaks_matched_schema,
    match_data_schema,
    set_unique_index,
    drop_timezone,
    parse_datetime_with_timezone,
    add_column_for_filtering,
    calculate_norm_intensity,
    sort_and_calculate_cumsum_tic_ratio,
)
from .browser import MascopeDataBrowser, handle_outputs
from ..logging_config import logger  # Import the shared logger
from .access import (
    get_mjw_mode,
)

MJW_DEV_MODE = get_mjw_mode()  # Get the MJW_DEV_MODE environment variable


class MascopeDataWrapper(HasTraits):  # Makes possible to observe class-methods
    """Dataset class that wraps mascope database data to itself.

    This class provides a flexible interface for accessing and managing
    Mascope database data. It can be extended with additional properties
    and methods by providing an extension class to the `extend()` method.

    The dataset observes key changes in the `data_source`.
    - When the 'key' changes, all `cached_property` attributes and
    instance attributes containing 'cache' in their names are cleared
    to ensure that outdated data is not used. This triggers the
    `memory_cleared` flag to notify observers.
    - When the data is loaded succesfully, the `data_loaded` flag is set to True.
    It observers changes in the`data_source`'s internal state from 'data_load_key'.

    The class also provides a method to check if a connection (observer) exists
    between a trait and a method, allowing for better control over the observers.

    The `decorate_properties()` method allows for wrapping the getter of all
    properties in the dataset with a given decorator, providing a way to modify.
    """

    memory_cleared = Int(default_value=0).tag(
        sync=True
    )  # Flag to be triggered when cache has been cleared
    data_loaded = Bool(False).tag(
        sync=True
    )  # Flag to indicate if data is loaded from the data source

    def __init__(self, data_source: MascopeDataBrowser):
        """
        Dataset class that wraps mascope database data to itself.

        :param data_source: Data_source should contain:
            - match_samples
            - match_compounds
            - match_isotopes
            - match_ions
            - peaks (if peak-level analysis are performed)
        :type data_source: MascopeDataBrowser
        """
        super().__init__()
        self.data_source = data_source
        self.data_source.parent = self  # Set the dataset in the data source
        self.data_source.data_clear_key.observe(
            self.clear_data_source_and_cache, names="value"
        )  # Clear cache, reset observers when 'data_clear_key' changes after data source is changed
        self.data_source.data_load_key.observe(
            self.is_data_loaded, names="value"
        )  # Observe changes in the data_source's internal state from 'data_load_key'
        self.is_data_loaded()

    @cached_property
    def match_samples(self) -> pd.DataFrame:
        """Sample-level dataframe

        :return: Sample-level dataframe
        :rtype: pd.DataFrame
        """
        return self.data_source.match_samples

    @cached_property
    def match_compounds(self) -> pd.DataFrame:
        """Compound-level dataframe

        :return: Compound-level dataframe
        :rtype: pd.DataFrame
        """
        return self.data_source.match_compounds

    @cached_property
    def match_isotopes(self) -> pd.DataFrame:
        """Isotope-level dataframe

        :return: Isotope-level dataframe
        :rtype: pd.DataFrame
        """
        return self.data_source.match_isotopes

    @cached_property
    def match_ions(self) -> pd.DataFrame:
        """Ion-level dataframe

        :return: Ion-level dataframe
        :rtype: pd.DataFrame
        """
        return self.data_source.match_ions

    @cached_property
    @handle_outputs("data_source.sample_batch_multiselect.load_error_output")
    def match_data(self) -> pd.DataFrame:
        """Build df containing Mascope matches for targets

        :return: DF containing targets and those exact mz-values
        :rtype: pd.DataFrame
        """
        try:
            match_data = pd.merge(
                self.match_isotopes,
                self.match_ions[
                    [
                        "target_ion_formula",
                        "ionization_mechanism",
                        "target_ion_id",
                        "sample_item_id",
                        "target_compound_id",
                        "unit",
                    ]
                ],
                left_on=["target_ion_id", "sample_item_id"],
                right_on=["target_ion_id", "sample_item_id"],
            )
            match_data = pd.merge(
                match_data,
                self.match_compounds[
                    [
                        "target_compound_id",
                        "target_compound_name",
                        "target_compound_formula",
                        "sample_item_id",
                    ]
                ],
                left_on=["target_compound_id", "sample_item_id"],
                right_on=["target_compound_id", "sample_item_id"],
            )
            match_data = pd.merge(
                match_data,
                self.match_samples[
                    [
                        "sample_batch_name",
                        "sample_item_name",
                        "filename",
                        "filter_id",
                        "sample_item_type",
                        "datetime",
                        "datetime_utc",
                        "sample_file_id",
                        "sample_item_id",
                        "instrument",
                        "tic",
                    ]
                ],
                left_on=["sample_item_id"],
                right_on=["sample_item_id"],
            )
            # Move 'unit' after 'intensity'
            columns = match_data.columns.tolist()
            columns.insert(
                columns.index("sample_peak_intensity") + 1,
                columns.pop(columns.index("unit")),
            )
            match_data = match_data[columns]
            # Apply schema validation or skip based on environment mode
            if MJW_DEV_MODE:
                return match_data_schema.validate(match_data.drop_duplicates())
            # Apply parser functions directly
            match_data["datetime"] = drop_timezone(match_data["datetime"])
            match_data["match_isotope_utc_created"] = parse_datetime_with_timezone(
                match_data["match_isotope_utc_created"]
            )
            match_data["match_isotope_utc_modified"] = parse_datetime_with_timezone(
                match_data["match_isotope_utc_modified"]
            )
            match_data = calculate_norm_intensity(match_data)
            match_data = sort_and_calculate_cumsum_tic_ratio(match_data)
            match_data = add_column_for_filtering(match_data)
            return match_data.drop_duplicates()
        except AttributeError as exc:
            raise RuntimeError(
                "Selected batch(es) changed and cache cleared. Load new data."
            ) from exc

    @cached_property
    @handle_outputs("data_source.sample_batch_multiselect.load_error_output")
    def peaks_matched(self) -> pd.DataFrame:
        """Peak-level dataframe with sample-level and match data

        :return: Peak-level dataframe with sample-level and match data
        :rtype: pd.DataFrame
        """
        try:
            match_data = self.match_data.rename(
                columns={
                    "mz": "target_isotope_mz",
                    "match_score": "match_score_isotope",
                },
                errors="ignore",
            )
            peaks_matched = pd.merge(
                self.data_source.peaks,
                match_data[
                    [
                        "target_compound_id",
                        "target_compound_name",
                        "target_compound_formula",
                        "target_ion_formula",
                        "target_isotope_mz",
                        "sample_file_id",
                        "sample_peak_mz",
                        "match_mz_error",
                        "relative_abundance",
                        "match_abundance_error",
                        "match_score_isotope",
                        "ionization_mechanism",
                    ]
                ],
                left_on=["mz", "sample_file_id"],
                right_on=["sample_peak_mz", "sample_file_id"],
                how="left",
            )

            # Apply schema validation or parsers based on environment mode
            if MJW_DEV_MODE:
                return peaks_matched_schema.validate(peaks_matched)
            # Apply parser functions directly
            peaks_matched = calculate_norm_intensity(peaks_matched)
            peaks_matched = sort_and_calculate_cumsum_tic_ratio(peaks_matched)
            peaks_matched = set_unique_index(peaks_matched)
        except AttributeError as exc:
            raise RuntimeError(
                "Selected batch(es) changed and cache cleared. Load new data."
            ) from exc
        return peaks_matched

    @cached_property
    def peaks_or_match_data(self) -> pd.DataFrame:
        """
        Returns the peaks DataFrame if available; otherwise, falls back to match_data
        with renamed and rematched to 'peaks_matched' columns.

        :param dataset: The dataset containing at least match_data
        and possible imported peaks.
        :type dataset: MascopeDataWrapper
        :return: DataFrame with peaks or match_data fallback.
        :rtype: pd.DataFrame
        """
        try:
            # Attempt to use peaks_matched if peaks are available
            if self.data_source.peaks is not None:
                return self.peaks_matched
        except RuntimeError:
            logger.warning("Peaks not available. Falling back to match_data.")

        match_data = self.match_data.copy()
        # Rename columns to match peaks_matched schema
        match_data.rename(
            columns={
                "mz": "target_isotope_mz",
                "match_score": "match_score_isotope",
                "sample_peak_intensity": "intensity",
                "norm_sample_peak_intensity": "norm_intensity",
            },
            inplace=True,
        )
        match_data["mz"] = match_data["sample_peak_mz"]
        # Filter columns to match peaks_matched_schema
        allowed_columns = set(peaks_matched_schema.columns.keys()).union(
            peaks_matched_schema.columns.keys()
        )
        match_data = match_data[
            [col for col in match_data.columns if col in allowed_columns]
        ]
        # Apply schema validation or parsers based on environment mode
        if MJW_DEV_MODE:
            return peaks_matched_schema.validate(match_data)
        # Apply parser functions directly
        match_data = calculate_norm_intensity(match_data)
        match_data = sort_and_calculate_cumsum_tic_ratio(match_data)
        match_data = set_unique_index(match_data)
        return match_data

    @cached_property
    def intensity_unit(self) -> str:
        """
        Returns the unit of the dataset.

        :return: Unit of the dataset
        :rtype: str
        """

        return (
            self.match_compounds.unit.unique().tolist()[0]
            if len(self.match_compounds.unit.unique().tolist()) == 1
            else "mixed"
        )

    def extend(self, extension: type) -> None:
        """
        Extend the dataset class with properties, methods, class-level traits and
        instance-level attributes from the given extension class.

        :param extension: extension-class to be added to the dataset
        :type extension: type
        """
        try:
            logger.info(f"Extending dataset with {extension.__name__}.")
            extension_instance = extension()
            extension_class = type(extension_instance)
            # Handle class-level traits (only if the extension has traits)
            if hasattr(extension_instance, "traits"):
                for name, trait in extension_instance.traits().items():
                    if name not in self.traits():
                        self.add_traits(**{name: trait})
                        logger.debug(f"Added trait: {name}")
                    self.__dict__[name] = getattr(extension_instance, name, None)
            # Handle instance-level attributes
            for name, value in vars(extension_instance).items():
                if name.startswith("_"):  # Skip private members
                    continue
                # Skip if the attribute is already a trait
                if name in self.traits():
                    continue
                # Add non-trait attributes
                if not hasattr(self, name):
                    self.__dict__[name] = (
                        value  # Directly set the attribute in __dict__
                    )
                    logger.debug(f"Added attribute: {name}")
            # Copy methods and properties
            for name, member in extension_class.__dict__.items():
                if name.startswith("_"):
                    continue  # Skip private members
                match member:
                    case cached_property():
                        setattr(self.__class__, name, member)
                        logger.debug(f"Added cached property: {name}")
                    case property():
                        setattr(self.__class__, name, member)
                        logger.debug(f"Added property: {name}")
                    case _ if callable(member):
                        setattr(self, name, MethodType(member, self))
                        logger.debug(f"Added method: {name}")
        except (AttributeError, KeyError) as e:
            logger.error("Error while extending dataset: %s", e)

    def clear_data_source_and_cache(
        self, change=None  # pylint: disable=unused-argument
    ) -> None:
        """
        Clear the data source and cache.
        """
        self.data_loaded = False
        if hasattr(self, "apply_filters"):
            self.set_trait("apply_filters", False)
        # Remove observers of memory_cleared trait
        if "memory_cleared" in self._trait_notifiers:
            self._trait_notifiers["memory_cleared"]["change"] = []
        self.clear_cache()

    @handle_outputs("data_source.sample_batch_multiselect.load_error_output")
    def clear_cache(self, *args, **kwargs) -> None:  # pylint: disable=unused-argument
        """
        Clear cached properties and attributes containing 'cache' in their names.

        This method is called when the key of the data source changes and when data
        is filtered with new parameters or binning parameters are changed.
        It ensures that the cached properties and attributes are cleared to avoid using
        outdated data.
        Cached properties are cleared in the order they were added to the class.
        To achieve this,
            - The method first collects cached_properties added by the extend method
            in the order they were added.
            - Then, it collects all cached properties in alphabetical order and
            drops the ones that are already in added_cached_properties.
            - Finally, it sets the correct order by concatenating the two lists.
        """
        try:
            logger.info("Clearing cached properties and attributes.")
            # Step 1: Get cached properties
            # Step 1.1: Get cached properties added by extend method in order as added
            added_cached_properties = [
                name
                for name, member in self.__class__.__dict__.items()
                if isinstance(member, cached_property)
            ]
            # Step 1.2: Collect all cached properties in alphabetical order
            cached_properties = [
                name
                for name, descriptor in inspect.getmembers(
                    self.__class__, lambda m: hasattr(m, "__get__")
                )
                if isinstance(descriptor, cached_property)
            ]
            # Step 1.3: Drop properties that are already in added_cached_properties
            cached_properties = [
                prop_name
                for prop_name in cached_properties
                if prop_name not in added_cached_properties
            ]
            # Step 1.4: Set to correct order
            cached_properties_ordered = cached_properties + added_cached_properties

            # Step 2: Get attributes containing 'cache'
            cache_attributes = [
                attr_name for attr_name in vars(self) if "cache" in attr_name
            ]
            # Step 3: Clear cached properties sequentially
            for name in cached_properties_ordered:
                self.__dict__.pop(name, None)
                logger.debug(f"Cleared cached property: {name}")
            # Step 4: Clear attributes containing 'cache'
            for attr_name in cache_attributes:
                attr_value = self.__dict__.get(attr_name)
                match attr_value:
                    case pd.DataFrame():
                        if not attr_value.empty:
                            setattr(self, attr_name, pd.DataFrame())
                            logger.debug(f"Reset DataFrame attribute: {attr_name}")
                    case _ if hasattr(attr_value, "clear") and callable(
                        attr_value.clear
                    ):
                        attr_value.clear()
                        logger.debug(f"Cleared attribute: {attr_name}")
                    case _:
                        setattr(self, attr_name, None)  # Reset to None
                        logger.debug(f"Reset attribute: {attr_name}")
            # Step 5: Toggle the memory_cleared trait to notify observers
            self.memory_cleared += 1  # Toggle the value to trigger observers
            logger.info("Toggled memory_cleared trait to notify observers.")
        except (
            AttributeError,
            KeyError,
            TypeError,
        ) as e:
            logger.error("Error while clearing cache: %s", e)

    def decorate_properties(self, decorator: callable) -> None:
        """
        Update all properties in self by wrapping their getter with given decorator.
        This method iterates over all attributes of self.data.source.__class__ that are properties,
        and replaces them with a new property that wraps the original getter.
        """
        try:
            logger.info("Decorating properties with the provided decorator.")
            if hasattr(self, "data_source"):
                for name, member in inspect.getmembers(self.data_source.__class__):
                    if isinstance(member, property):  # Only process properties
                        setter = (
                            member.fset if hasattr(member, "fset") else None
                        )  # Check if the property has a setter
                        # Create a new property with the decorator wrapping the getter
                        if setter:
                            setattr(
                                self.data_source.__class__,
                                name,
                                property(decorator(member.fget), setter),
                            )
                        else:
                            setattr(
                                self.data_source.__class__,
                                name,
                                property(decorator(member.fget)),
                            )
                        logger.debug(f"Decorated property: {name}")
        except (AttributeError, KeyError, TypeError) as e:
            logger.error("Error while decorating properties: %s", e)

    def add_observer(self, name: str, callback: callable) -> None:
        """
        Add an observer to the dataset.
        - First method check if the observer is already connected to the trait.
        - If not, it connects the observer to the trait and
        logs additional context about the callback method.

        :param name: The name of the trait to observe.
        :type name: str
        :param callback: The callback function to be called when the trait changes.
        :type callback: callable
        """
        if not hasattr(self, name):
            raise ValueError(f"Trait '{name}' does not exist in {self}.")
        if not self.is_observer_connected(name, callback):
            self.observe(callback, names=name)
            # Log additional context about the callback
            callback_owner = getattr(callback, "__self__", None)
            callback_owner_class = (
                callback_owner.__class__.__name__ if callback_owner else "Unknown"
            )
            callback_name = (
                callback.__name__ if hasattr(callback, "__name__") else str(callback)
            )

            logger.debug(
                f"Observer added for trait '{name}' -> {callback_name} "
                f"(Owner: {callback_owner_class})"
            )

    def is_observer_connected(
        self, trait_name: str, callback: callable, target: object = None
    ) -> bool:
        """
        Check if a connection (observer) exists between a trait and a method.
        This method is used to determine if a callback function is already connected
        to a trait in the dataset
        To do this, it checks if the callback function is in the list of observers
        for the given trait and event type.
        This information is stored in the protected
        `_trait_notifiers` dictionary of the target object.

        :param trait_name: The name of the trait to check.
        :type trait_name: str
        :param callback: The callback function to check.
        :type callback: callable
        :param target: The object whose traits should be checked (default: self).
        :type target: object
        :return: True if the observer is connected, False otherwise.
        :rtype: bool
        """
        # Check if the target is provided, otherwise use self
        target = target or self
        if trait_name not in target.traits():
            raise ValueError(f"Trait '{trait_name}' does not exist in {target}.")
        # Get the list of observers for the given trait and event type
        observers = target._trait_notifiers.get(  # pylint: disable=protected-access
            trait_name, {}
        ).get("change", [])

        for observer in observers:
            # Compare the id of the wrapped function with the id of the callback
            if isinstance(observer, partial):
                if id(observer.func) == id(callback):
                    return True
            # Compare the id of the function with the id of the callback
            elif id(observer) == id(callback):
                return True

        return False

    def is_data_loaded(self, change=None) -> None:  # pylint: disable=unused-argument
        """
        Check if the data in the data source is valid and complete.
        This method is called when the data_load_key in the data source changes.
        It checks if the data is loaded and sets the `data_loaded` flag accordingly.
        """
        try:
            logger.debug("Checking if data is loaded and valid.")
            is_valid = self.data_source.validate_data_loaded()
            logger.debug(f"Validation result from data source: {is_valid}")

            if is_valid:
                self.data_loaded = True  # Set `data_loaded` only when data is ready
                logger.info(
                    "Data is fully validated and ready. Setting `data_loaded` to True."
                )

            else:
                self.data_loaded = (
                    False  # Set `data_loaded` to False if data is not ready
                )
                logger.warning("Data is not ready. Setting `data_loaded` to False.")
        except (
            AttributeError,
            KeyError,
            TypeError,
        ) as e:
            self.data_loaded = False
            logger.error("Error while checking data readiness: %s", e)
