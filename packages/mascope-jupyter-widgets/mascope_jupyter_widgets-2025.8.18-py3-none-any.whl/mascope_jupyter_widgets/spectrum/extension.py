from typing import Dict, Any
import warnings
import pandas as pd
import numpy as np

from .schemas import (
    spectrum_schema,
    add_column_for_filtering,
    set_unique_index,
    calculate_tic_norm_intensity_and_cumsum_tic_ratio,
)
from ..mascope_data.access import (
    get_mjw_mode,
)
from ..logging_config import logger  # Import the shared logger

warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
)  # TODO, Think later groupby deprecation warning
# Import global schemas


MJW_DEV_MODE = get_mjw_mode()  # Get the MJW_DEV_MODE environment variable


class SpectrumDataExtension:
    """
    Spectrum related data extension for MascopeDataWrapper.
    When wrapped with MascopeDataWrapper, this extension provides
    additional methods to access spectrum data.
    """

    def __init__(self) -> None:
        """Initialize the SpectrumDataExtension class.

        This class is designed to extend the functionality of
        the MascopeDataWrapper class to include methods for
        accessing and processing spectrum data.
        It initializes the class with empty dictionaries for
        cached samples spectra and spectrum parameters.
        """

        self.cached_samples_spectra: Dict[str, Dict[str, Any]] = {}
        self.cached_spectrum_params: Dict[str, Any] = (
            {  # Dictionary to store spectrum parameters
                "mz_min": None,
                "mz_max": None,
                "t_min": None,
                "t_max": None,
                "sample_item_id": None,
            }
        )

    def get_spectrum_data(
        self,
        sample_item_id: str = None,
        mz_min: float = None,
        mz_max: float = None,
        t_min: float = None,
        t_max: float = None,
    ) -> pd.DataFrame:
        """
        Get spectrum data for a specific sample_item_id or
        all sample files when sample_item_id is None.

        If mz_min and mz_max are provided, only the data within
        the mz range will be returned. Else, all data will be returned.

        Similarly, if t_min and t_max are provided, only the spectrum data
        within the time range will be returned for given mz-range values.

        :param sample_item_id: sample file id, defaults to None
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
        :return: Spectrum data for the given sample file id
        :rtype: pd.DataFrame
        """

        self.cached_spectrum_params.update(
            {
                "mz_min": mz_min,
                "mz_max": mz_max,
                "t_min": t_min,
                "t_max": t_max,
                "sample_item_id": sample_item_id,
            }
        )
        if sample_item_id:
            if (
                sample_item_id
                not in self.match_samples[  # pylint: disable=E1101
                    "sample_item_id"
                ].unique()
            ):
                raise ValueError(f"Invalid sample item id: {sample_item_id}")
            return self.get_sample_spectrum()
        else:  # If no specific sample_item_id is provided, compute for all samples
            return self.get_all_sample_spectra()

    def get_all_sample_spectra(self) -> pd.DataFrame:
        """
        Compute the spectrum data for all samples.

        This method retrieves the spectrum data for all samples
        in the match_samples DataFrame.
        It concatenates the spectrum data for each sample file id
        and processes it to add additional columns for filtering,
        sets a unique index, and calculates the TIC normalized
        intensity and cumulative TIC ratio.

        :return: Spectrum data for all samples
        :rtype: pd.DataFrame
        """
        spectrum_df = pd.concat(
            [
                self.get_spectrum_data(sample_item_id=sample_item_id)
                for sample_item_id in self.match_samples[  # pylint: disable=E1101
                    "sample_item_id"
                ]
            ]
        )
        # If in developer mode, validate the schema
        if MJW_DEV_MODE:
            return spectrum_schema.validate(spectrum_df)
        # If not in developer mode, process parser functions
        spectrum_df = add_column_for_filtering(spectrum_df)
        spectrum_df = set_unique_index(spectrum_df)
        spectrum_df = calculate_tic_norm_intensity_and_cumsum_tic_ratio(spectrum_df)

        return spectrum_df

    def get_sample_spectrum(self) -> pd.DataFrame:
        """
        Get the spectrum data for a specific sample file id.

        This method retrieves the spectrum data for a specific
        sample file id from the match_samples DataFrame.
        It processes the spectrum data to add additional columns
        for filtering, sets a unique index, and calculates the
        TIC normalized intensity and cumulative TIC ratio.
        It also caches the spectrum data for future use.
        If the spectrum data is already cached with the same
        parameters, it returns the cached data.
        If the parameters are not provided, it raises a ValueError.
        If the sample file id is not found in the match_samples
        DataFrame, it raises a ValueError.

        :return: spectrum data for sample
        :rtype: pd.DataFrame
        """
        try:
            logger.debug(
                "Fetching spectrum data for sample_item_id: %s",
                self.cached_spectrum_params["sample_item_id"],
            )

            # Columns to add from sample-level DF to spectrum-level DF
            cols_to_add = [
                "sample_batch_name",
                "sample_item_name",
                "filename",
                "filter_id",
                "sample_item_type",
                "datetime",
                "datetime_utc",
                "sample_item_id",
                "sample_file_id",
                "instrument",
                "tic",
            ]
            sample_item_id = self.cached_spectrum_params["sample_item_id"]
            mz_min = self.cached_spectrum_params["mz_min"]
            mz_max = self.cached_spectrum_params["mz_max"]
            t_min = self.cached_spectrum_params["t_min"]
            t_max = self.cached_spectrum_params["t_max"]

            # Log the parameters being used
            logger.debug(
                "Spectrum parameters - mz_min: %s, mz_max: %s, t_min: %s, t_max: %s",
                mz_min,
                mz_max,
                t_min,
                t_max,
            )

            # Collect sample-level data
            match_samples = self.match_samples  # pylint: disable=E1101

            # Check if the spectrum is already cached with the same parameters
            cached_spectrum = self.cached_samples_spectra.get(sample_item_id, None)
            if cached_spectrum:
                cached_params = cached_spectrum.get("params", {})
                if (
                    cached_params.get("mz_min") == mz_min
                    and cached_params.get("mz_max") == mz_max
                    and cached_params.get("t_min") == t_min
                    and cached_params.get("t_max") == t_max
                ):
                    logger.debug("Cache hit for sample_item_id: %s", sample_item_id)
                    return cached_spectrum["data"]
                else:
                    logger.debug(
                        "Cache miss for sample_item_id: %s due to parameter mismatch.",
                        sample_item_id,
                    )
            else:
                logger.info("Cache miss for sample_item_id: %s", sample_item_id)

            # Subset match_samples to the specific sample_item_id and collect spectrum data
            match_samples_round = match_samples[
                match_samples["sample_item_id"] == sample_item_id
            ]
            logger.debug("Loaded match_samples for sample_item_id: %s", sample_item_id)

            sample_spectrum = (
                self.data_source.load_sample_file_spectrum(  # pylint: disable=E1101
                    sample_item_id=sample_item_id,
                    mz_min=mz_min,
                    mz_max=mz_max,
                    t_min=t_min,
                    t_max=t_max,
                )
            )
            logger.debug("Loaded spectrum data for sample_item_id: %s", sample_item_id)

            sample_spectrum_df = pd.DataFrame(
                {
                    "intensity": sample_spectrum["intensity"],
                    "mz": sample_spectrum["mz"],
                    "unit": np.repeat(
                        sample_spectrum["intensity_unit"],
                        len(sample_spectrum["mz"]),
                    ),
                    "sample_item_id": np.repeat(
                        sample_item_id, len(sample_spectrum["mz"])
                    ),
                }
            )
            logger.debug(
                "Created spectrum DataFrame for sample_item_id: %s", sample_item_id
            )

            # Collect needed information from match_samples to sample_spectrum_df
            for col in cols_to_add:
                sample_spectrum_df[col] = match_samples_round[col].unique().tolist()[0]
            logger.debug(
                "Added additional columns to spectrum DataFrame for sample_item_id: %s",
                sample_item_id,
            )

            # Cache the spectrum data with the parameters
            self.cached_samples_spectra[sample_item_id] = {
                "data": sample_spectrum_df,
                "params": self.cached_spectrum_params.copy(),
            }
            logger.debug("Cached spectrum data for sample_item_id: %s", sample_item_id)

            # Reset cached parameters
            for key in self.cached_spectrum_params:
                self.cached_spectrum_params[key] = None

            # If in developer mode, validate the schema
            if MJW_DEV_MODE:
                logger.debug(
                    "Validating spectrum DataFrame schema for sample_item_id: %s",
                    sample_item_id,
                )
                return spectrum_schema.validate(sample_spectrum_df)

            # Process additional parser functions
            sample_spectrum_df = add_column_for_filtering(sample_spectrum_df)
            sample_spectrum_df = set_unique_index(sample_spectrum_df)
            sample_spectrum_df = calculate_tic_norm_intensity_and_cumsum_tic_ratio(
                sample_spectrum_df
            )
            logger.debug(
                "Processed spectrum DataFrame for sample_item_id: %s", sample_item_id
            )

            return sample_spectrum_df

        except Exception as e:
            logger.error(
                "Error in get_sample_spectrum for sample_item_id: %s: %s",
                self.cached_spectrum_params["sample_item_id"],
                e,
            )
            raise
