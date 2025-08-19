from __future__ import annotations
import io
from contextlib import redirect_stdout
import pandas as pd
import pandera as pa
import numpy as np
import ipywidgets as wg

from tqdm.notebook import tqdm
from mascope_sdk import (
    get_sample_batch_data,
    get_sample_peaks,
    get_sample_spectrum,
    get_sample_peak_timeseries,
)
from traitlets import directional_link
from .access import load_url

from .lib.dropdown import (
    UrlDropdown,
    WorkspaceDropdown,
)
from .lib.multiselect import SampleBatchMultiSelect

# Import global schemas
from .schemas import (
    match_compounds_schema,
    match_ions_schema,
    match_isotopes_schema,
    match_samples_schema,
    peaks_schema,
    sample_batches_schema,
    workspaces_schema,
)
from ..logging_config import logger  # Import the shared logger

# DataBrowser settings
style = {"description_width": "100px"}
layout_props = {"width": "500px"}


# Decorator
def handle_outputs(output_widget_name):
    """
    Decorator to handle output prints and redirect them to the specified output widget.

    :param output_widget_name: The name of the output widget attribute
    (e.g., 'sample_batch_multiselect.load_error_output').
    :type output_widget_name: str
    """

    def decorator(func: object) -> object:
        """
        Decorator function to wrap the original function with output handling.

        :param func: The original function to be decorated.
        :type func: function
        """

        def wrapper(self, *args, **kwargs) -> object:
            """
            Wrapper function to handle output and exceptions.

            :param self: The instance of the class where the function is defined.
            :type self: object
            :param args: Positional arguments for the original function.
            :param kwargs: Keyword arguments for the original function.
            :return: The result of the original function.
            """

            def resolve_nested_attributes(obj: object, attr_path: str) -> object:
                """
                This function traverses the object's attributes using a dot-separated path.
                :param obj: The object to resolve attributes from.
                :type obj: object
                :param attr_path: The dot-separated attribute path
                (e.g., 'data_source.sample_batch_multiselect.load_error_output').
                :type attr_path: str
                :return: The resolved attribute object.
                :rtype: object
                """
                for attr in attr_path.split("."):
                    obj = obj.__dict__.get(attr, None)
                    if obj is None:
                        raise AttributeError(
                            f"Attribute '{attr}' not found in path '{attr_path}'."
                        )
                return obj

            try:
                # Resolve the output widget
                output_widget = resolve_nested_attributes(self, output_widget_name)
                with output_widget:
                    buffer = io.StringIO()  # Create a buffer to capture stdout
                    with redirect_stdout(buffer):
                        try:
                            result = func(self, *args, **kwargs)
                            output_widget.clear_output(wait=True)
                            return result
                        except Exception as e:
                            output_widget.clear_output(wait=True)
                            output_widget.append_stdout(buffer.getvalue())
                            output_widget.append_stdout(f"Error: {e}")
                            raise
            except AttributeError as e:
                logger.error("Error resolving output widget: %s", e)
                raise

        return wrapper

    return decorator


class MascopeDataBrowser:
    """Reactive batch multiselect component, with dropdowns for Mascope URL and workspace,
    and a multiselect for sample batches"""

    def __init__(self):
        """
        Initialize MascopeDataBrowser
        """
        super().__init__()
        # URL selector
        self.url_dropdown = UrlDropdown(
            load_url(), style=style, layout_props=layout_props
        )
        # Store access token at MascopeDataBrowser level for reuse
        self.access_token = self.url_dropdown.access_token
        # Workspace selector
        self.workspace_dropdown = WorkspaceDropdown(
            style=style, layout_props=layout_props
        )
        # Link URL dropdown value to workspace dropdown url property
        directional_link((self.url_dropdown, "value"), (self.workspace_dropdown, "url"))
        # Sample batch selector
        self.sample_batch_multiselect = SampleBatchMultiSelect(
            style=style, layout_props=layout_props
        )
        # Link URL dropdown value to sample batch multiselect url property
        directional_link(
            (self.url_dropdown, "value"), (self.sample_batch_multiselect, "url")
        )
        # Link workspace dropdown value to sample batch dropdown workspace_id property
        directional_link(
            (self.workspace_dropdown, "value"),
            (self.sample_batch_multiselect, "workspace_id"),
            lambda workspace: workspace["workspace_id"] if workspace else "",
        )
        #  When batch selection changes, clear stored dataframes
        self.sample_batch_multiselect.observe(self.clear_dataframes, names="value")
        # When 'import peaks' checkbox changes, clear stored dataframes
        self.sample_batch_multiselect.import_peaks_checkbox.observe(
            self.clear_dataframes, names="value"
        )
        # Load sample batch data on button click
        self.sample_batch_multiselect.on_load_button_clicked = (
            self.load_sample_batches_data
        )
        # Initialize dataframes
        self._match_samples = None
        self._match_compounds = None
        self._match_ions = None
        self._match_isotopes = None
        self._peaks = None

    @property
    def data_clear_key(self) -> wg.IntText:
        """Hidden button for property_cache clearing"""
        return self.sample_batch_multiselect.data_clear_key

    @property
    def data_load_key(self) -> wg.IntText:
        """Hidden button for data-loading"""
        return self.sample_batch_multiselect.data_load_key

    @property
    def mascope_url(self) -> str:
        """Mascope URL

        :return: Mascope URL
        :rtype: str
        """
        return self.url_dropdown.value

    @property
    def workspace_selected(self) -> dict:
        """Selected workspace

        :return: Selected workspace
        :rtype: dict
        """
        return self.workspace_dropdown.value

    @property
    @pa.check_output(workspaces_schema)
    def workspaces(self) -> pd.DataFrame:
        """All workspaces as a dataframe

        :return: Workspaces
        :rtype: pd.DataFrame
        """
        return pd.json_normalize(pd.DataFrame(self.workspace_dropdown.options)[1])

    @property
    def sample_batches_selected(self) -> tuple:
        """Selected sample batches

        :return: Selected sample batches
        :rtype: tuple
        """
        return self.sample_batch_multiselect.value

    @property
    @pa.check_output(sample_batches_schema)
    def sample_batches(self) -> pd.DataFrame:
        """All sample batches of the selected workspace as a dataframe

        :return: Sample batches
        :rtype: pd.DataFrame
        """
        return pd.json_normalize(pd.DataFrame(self.sample_batch_multiselect.options)[1])

    @property
    @handle_outputs("sample_batch_multiselect.load_error_output")
    def match_samples(self) -> pd.DataFrame:
        """Samples (with all metadata) of the selected sample batch as a dataframe.

        :return: Samples
        :rtype: pd.DataFrame
        """
        if self._match_samples is None:
            raise RuntimeError(
                "Selected batch(es) changed and cache cleared. Load new data."
            )
        return self._match_samples

    @property
    @handle_outputs("sample_batch_multiselect.load_error_output")
    def match_compounds(self) -> pd.DataFrame:
        """Compound-level match/target data aggregation of the selected batch.

        :return: Compound-level matches
        :rtype: pd.DataFrame
        """
        if self._match_compounds is None:
            raise RuntimeError(
                "Selected batch(es) changed and cache cleared. Load new data."
            )

        return self._match_compounds

    @property
    @handle_outputs("sample_batch_multiselect.load_error_output")
    def match_ions(self) -> pd.DataFrame:
        """Ion-level match/target data aggregation of the selected batch.

        :return: Ion-level matches
        :rtype: pd.DataFrame
        """
        if self._match_ions is None:
            raise RuntimeError(
                "Selected batch(es) changed and cache cleared. Load new data."
            )

        return self._match_ions

    @property
    @handle_outputs("sample_batch_multiselect.load_error_output")
    def match_isotopes(self) -> pd.DataFrame:
        """Isotope-level match/target data aggregation of the selected batch.

        :return: Isotope-level matches
        :rtype: pd.DataFrame
        """
        if self._match_isotopes is None:
            raise RuntimeError(
                "Selected batch(es) changed and cache cleared. Load new data."
            )

        return self._match_isotopes

    @property
    @handle_outputs("sample_batch_multiselect.load_error_output")
    def peaks(self) -> pd.DataFrame:
        """Peaks with selected sample-level metadata of
        the selected sample batch(es) as a dataframe.

        :return: Peaks
        :rtype: pd.DataFrame
        """

        if self._peaks is None:
            raise RuntimeError("Peak data not loaded.")
        else:
            return self._peaks

    def load_sample_file_spectrum(
        self,
        sample_item_id: str,
        mz_min: float = None,
        mz_max: float = None,
        t_min: float = None,
        t_max: float = None,
    ) -> dict:
        """Get sample file spectrum data.

        This method fetches the spectrum data for a given sample file ID
        from mascope_sdk.

        :param sample_item_id: sample item id, defaults to None
        :type sample_item_id: str, optional
        :param mz_min: mz range low end, defaults to None
        :type mz_min: float, optional
        :param mz_max: mz range high end, defaults to None
        :type mz_max: float, optional
        :param t_min: time starting point, defaults to None
        :type t_min: float, optional
        :param t_max: time ending point, defaults to None
        :type t_max: float, optional
        :raises ValueError: if sample file id can't be found
        from match_samples
        :return: sample file spectrum data
        :rtype: dict
        """

        logger.info(
            f"Fetching spectrum for sample_item_id={sample_item_id},"
            f" mz_min={mz_min}, mz_max={mz_max}, t_min={t_min}, t_max={t_max}",
        )
        try:
            return get_sample_spectrum(
                sample_item_id=sample_item_id,
                mascope_url=self.mascope_url,
                access_token=self.access_token,
                mz_min=mz_min,
                mz_max=mz_max,
                t_min=t_min,
                t_max=t_max,
            )
        except Exception as e:
            logger.error(
                "Error fetching spectrum for sample_item_id=%s: %s",
                sample_item_id,
                e,
            )
            raise

    def load_sample_file_peak_timeseries(
        self,
        sample_item_id: str,
        peak_mz: float,
        peak_mz_tolerance_ppm: float = 1,
        t_min: float | None = None,
        t_max: float | None = None,
    ) -> pd.DataFrame:
        """
        Load the sample-level peak timeseries for a given sample_item_id and peak m/z.

        Method fetches the timeseries data from mascope_sdk and merges it with
        the sample-level data. It also handles exceptions and logs errors.

        :param sample_item_id: The ID of the sample item to retrieve.
        :type sample_item_id: str
        :param peak_mz: The m/z value of the peak to retrieve.
        :type peak_mz: float
        :param peak_mz_tolerance_ppm: The tolerance in ppm for the peak m/z.
        :type peak_mz_tolerance_ppm: float, optional
        :param t_min: The minimum time value for the timeseries, defaults to None.
        :type t_min: float | None, optional
        :param t_max: The maximum time value for the timeseries, defaults to None.
        :type t_max: float | None, optional
        :return: A DataFrame containing the peak timeseries data.
        """
        logger.info(
            f"Fetching peak timeseries for sample_item_id={sample_item_id},"
            f" peak_mz={peak_mz}, tolerance_ppm={peak_mz_tolerance_ppm}",
        )
        try:
            sample_timeseries = pd.DataFrame(
                get_sample_peak_timeseries(
                    mascope_url=self.mascope_url,
                    access_token=self.access_token,
                    sample_item_id=sample_item_id,
                    peak_mz=peak_mz,
                    peak_mz_tolerance_ppm=peak_mz_tolerance_ppm,
                    t_min=t_min,
                    t_max=t_max,
                )
            )
            logger.debug(sample_timeseries)
            sample_timeseries["sample_item_id"] = sample_item_id
            sample_timeseries = pd.merge(
                sample_timeseries, self.match_samples, on="sample_item_id", how="left"
            )
            logger.info(
                f"Browser Fetched timeseries with {len(sample_timeseries)} rows.",
            )
            return sample_timeseries
        except Exception as e:
            logger.error(
                "Error fetching peak timeseries for sample_item_id=%s, peak_mz=%s: %s",
                sample_item_id,
                peak_mz,
                e,
            )
            raise

    def clear_dataframes(self, change) -> None:  # pylint: disable=unused-argument
        """Clears the stored DataFrames.

        This method is called when the sample batch selection changes
        or when the import peaks checkbox is toggled.

        :param change: The change dictionary containing old and new values.
        :type change: dict"""

        logger.info("Clearing all stored DataFrames.")
        self._match_samples = None
        self._match_compounds = None
        self._match_ions = None
        self._match_isotopes = None
        self._peaks = None
        self.data_clear_key.value += 1  # Trigger cache clearing
        logger.info("All DataFrames cleared successfully.")

    @handle_outputs("sample_batch_multiselect.load_error_output")
    def load_sample_batches_data(self) -> None:
        """Get sample batches' data

        This method fetches the sample batches data from mascope_sdk
        and validates the data using pandera schemas. It also handles
        exceptions and logs errors.

        :raises RuntimeError: If validation fails or if data is not ready.
        """

        logger.debug("Starting to load sample batches data.")
        logger.debug(
            f"Number of selected sample batches: {len(self.sample_batches_selected)}",
        )

        match_samples_dfs = []
        match_compounds_dfs = []
        match_ions_dfs = []
        match_isotopes_dfs = []
        peaks_dfs = []

        # Columns to add from sample-level DF to peak-level DF
        cols_to_add = [
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

        # Request and collect data from each selected batch
        for sample_batch in tqdm(
            self.sample_batches_selected, desc="Processing batches", leave=False
        ):
            logger.debug(f"Processing sample batch: {sample_batch['sample_batch_id']}")
            sample_batch_data = get_sample_batch_data(
                self.mascope_url,
                self.access_token,
                sample_batch["sample_batch_id"],
            )
            match_samples_dfs.append(pd.DataFrame(sample_batch_data.get("samples")))
            match_compounds_dfs.append(pd.DataFrame(sample_batch_data.get("compounds")))
            match_ions_dfs.append(pd.DataFrame(sample_batch_data.get("ions")))
            match_isotopes_dfs.append(pd.DataFrame(sample_batch_data.get("isotopes")))
            # Collect peaks if checkbox is selected
            if self.sample_batch_multiselect.import_peaks_checkbox.value:
                for sample_item in tqdm(
                    sample_batch_data.get("samples", []),
                    desc="Collecting peaks",
                    leave=False,
                ):
                    logger.debug(
                        f"Collecting peaks for sample_item_id: {sample_item['sample_item_id']}"
                    )
                    sample_peaks = pd.DataFrame(
                        get_sample_peaks(
                            mascope_url=self.mascope_url,
                            sample_item_id=sample_item["sample_item_id"],
                            access_token=self.access_token,
                        )
                    )
                    sample_peaks["sample_item_id"] = sample_item["sample_item_id"]
                    # Make subset of match_samples according round sample_id
                    batch_samples = pd.DataFrame(sample_batch_data.get("samples"))
                    match_samples_sub = batch_samples[
                        batch_samples["sample_item_id"] == sample_item["sample_item_id"]
                    ]
                    for col in cols_to_add:
                        # Collect needed information from match_samples
                        sample_peaks[col] = match_samples_sub[col].unique().tolist()[0]

                    peaks_dfs.append(sample_peaks)
        logger.debug("Finished collecting data from sample batches.")
        # Concatenate data into combined dataframes
        validation_steps = [
            ("match_samples", match_samples_schema, match_samples_dfs),
            ("match_compounds", match_compounds_schema, match_compounds_dfs),
            ("match_ions", match_ions_schema, match_ions_dfs),
            ("match_isotopes", match_isotopes_schema, match_isotopes_dfs),
        ]
        for name, schema, dfs in validation_steps:
            try:
                logger.info(f"Starting validation for {name}.")
                if schema == match_samples_schema:
                    # Before validation
                    match_samples_raw_df = pd.concat(dfs)
                    logger.debug(
                        f"Validating {name} with {len(match_samples_raw_df)} rows."
                    )
                    # Perform validation
                    match_samples_validated_df = schema.validate(
                        match_samples_raw_df, lazy=True
                    )
                    # Log dropped rows
                    dropped_samples = match_samples_raw_df.loc[
                        ~match_samples_raw_df.index.isin(
                            match_samples_validated_df.index
                        )
                    ]
                    if not dropped_samples.empty:
                        logger.warning(
                            f"{len(dropped_samples)} rows were dropped during {name} validation."
                        )
                        logger.warning(
                            f"Dropped sample_item_ids: {dropped_samples['sample_item_id'].tolist()}"
                        )
                    self._match_samples = match_samples_validated_df
                elif schema == match_compounds_schema:
                    match_compounds = schema.validate(pd.concat(dfs), lazy=True)
                    self._match_compounds = match_compounds[
                        match_compounds["sample_item_id"].isin(
                            self.match_samples.sample_item_id.tolist()
                        )
                    ]  # Subset match_compounds to only include sample_item_id from match_samples
                elif schema == match_ions_schema:
                    match_ions = schema.validate(pd.concat(dfs), lazy=True)
                    self._match_ions = match_ions[
                        match_ions["sample_item_id"].isin(
                            self.match_samples.sample_item_id.tolist()
                        )
                    ]  # Subset match_ions to only include sample_item_id from match_samples
                elif schema == match_isotopes_schema:
                    match_isotopes = schema.validate(pd.concat(dfs), lazy=True)
                    self._match_isotopes = match_isotopes[
                        match_isotopes["sample_item_id"].isin(
                            self.match_samples.sample_item_id.tolist()
                        )
                    ]  # Subset match_isotopes to only include sample_item_id from match_samples
                logger.debug(f"Data validation successful for {name}.")
            except pa.errors.SchemaError as e:
                logger.error(f"Validation failed for {name}: {e}")
                raise RuntimeError(f"Validation failed for {name}: {e}") from e

        # Check if peaks are wanted
        if self.sample_batch_multiselect.import_peaks_checkbox.value:
            try:
                # Combine list elements to one dataframe
                peaks = pd.concat(peaks_dfs)
                # Subset peaks to only include sample_item_id from match_samples
                peaks = peaks[
                    peaks["sample_item_id"].isin(
                        self.match_samples.sample_item_id.tolist()
                    )
                ]
                # Check if it's ORBI or TOF Data
                peaks["intensity"] = np.where(
                    peaks["instrument"].str.lower().str.contains("orbi"),
                    peaks["height"],
                    peaks["area"],
                )
                # Drop intensity & peak_heigh columns
                peaks = peaks.drop(columns=["area", "height"])

                # Add unit-column
                ## Add 'unit' column from compound-level DF
                peaks = pd.merge(
                    peaks,
                    self._match_compounds[["sample_item_id", "unit"]],
                    how="left",
                    on="sample_item_id",
                )
                ## Move 'unit' after 'intensity'
                columns = peaks.columns.tolist()
                columns.insert(
                    columns.index("intensity") + 1,
                    columns.pop(columns.index("unit")),
                )
                ## Reorder DataFrame
                self._peaks = peaks_schema.validate(peaks[columns], lazy=True)
                logger.debug("Validation successful for peaks.")
            except pa.errors.SchemaError as e:
                logger.error(f"Validation failed for peaks: {e}")
                raise RuntimeError(f"Validation failed for peaks: {e}") from e

        # Validate that all data is loaded before updating data_load_key
        if self.validate_data_loaded():
            self.data_load_key.value += 1  # Trigger data loading key change
            logger.info("Data successfully loaded and validated.")
        else:
            logger.error("Data validation failed. Not all data is ready.")
            raise RuntimeError("Data validation failed. Not all data is ready.")

    def validate_data_loaded(self) -> bool:
        """
        Validate if all required dataframes are loaded and ready.

        :return: True if all data is valid, False otherwise.
        :rtype: bool
        """
        try:
            has_match_samples = (
                isinstance(self._match_samples, pd.DataFrame)
                and not self._match_samples.empty
            )
            has_match_compounds = (
                isinstance(self._match_compounds, pd.DataFrame)
                and not self._match_compounds.empty
            )
            has_match_ions = (
                isinstance(self._match_ions, pd.DataFrame)
                and not self._match_ions.empty
            )
            has_match_isotopes = (
                isinstance(self._match_isotopes, pd.DataFrame)
                and not self._match_isotopes.empty
            )
            has_peaks = (
                not self.sample_batch_multiselect.import_peaks_checkbox.value
                or (isinstance(self._peaks, pd.DataFrame) and not self._peaks.empty)
            )

            is_valid = (
                has_match_samples
                and has_match_compounds
                and has_match_ions
                and has_match_isotopes
                and has_peaks
            )

            if is_valid:
                logger.debug("All data validated successfully.")
            else:
                logger.warning("Data validation failed. Some datasets are incomplete.")

            return is_valid
        except (AttributeError, ValueError, TypeError) as e:
            logger.error("Error during data validation: %s", e)
            return False
