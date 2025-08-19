from IsoSpecPy import IsoThreshold, ParseFormula, PeriodicTbl
from molmass import Formula
import pandas as pd
from ..logging_config import logger  # Import the shared logger

ELECTRON_MASS = 5.48579909065e-4


class PeakVisualizationExtension:
    """
    A MascopeDataWrapper extension to handle peak visualization.
    This class provides methods to retrieve isotopocule data for a target ion formula
    and to filter peaks based on mass-to-charge ratio (mz) within specified tolerances.
    """

    def get_mz_list_for_target_formula(
        self, formula: str, isotope_abundance_threshold: float = 0.001
    ) -> list:
        """
        Get a list of m/z values for the isotopocules of a formula.

        This method calculates the m/z values for the isotopocules of a given formula
        based on the specified isotope abundance threshold. It uses the IsoSpecPy library to predict
        the isotopic distribution and returns a list of m/z values adjusted for the electron charge
        if part of the formula.
        If the formula is not valid, it returns an empty list.

        :param formula: The chemical formula of the target ion.
        :type formula: str
        :param isotope_abundance_threshold: The threshold for isotope abundance to consider.
        :type isotope_abundance_threshold: float
        :return: List of m/z values for the isotopocules of the target ion.
        :rtype: list
        """

        def canonicalize_formula(formula: str) -> str:
            """
            Canonicalize a chemical formula using molmass.
            E.g. "H2OH+" -> "H3O+"

            :param formula: The chemical formula to canonicalize.
            :type formula: str
            :return: Canonicalized chemical formula.
            :rtype: str
            """

            f = Formula(formula)
            return f.formula.format("hill").replace("[", "").replace("]", "")

        def conf_to_label(conf: tuple, raw_ion_formula: str) -> str:
            """
            Helper method to convert a configuration tuple to a label string.

            This method generates a label string representing the isotope configuration
            based on the counts of isotopes for each element.
            It formats the label by appending the mass number and count of each isotope,
            omitting the most abundant isotope (usually index 0) unless it's the only one.
            If no isotopes are present, it returns "M0".

            :param conf: Configuration tuple containing isotope counts.
            :type conf: tuple
            :param raw_ion_formula: The chemical formula of the target ion.
            :type raw_ion_formula: str
            :return: Label string representing the isotope configuration.
            :rtype: str
            """

            # Get element order and isotope info
            formula_dict = ParseFormula(raw_ion_formula)
            elements = list(formula_dict.keys())
            isotope_masses = [PeriodicTbl.symbol_to_masses[el] for el in elements]

            label_parts = []
            for el, iso_counts, iso_masses in zip(elements, conf, isotope_masses):
                for idx, count in enumerate(iso_counts):
                    if count == 0:
                        continue
                    # For the most abundant isotope (usually index 0),
                    #  skip label unless it's the only one (M0)
                    if idx == 0:
                        continue

                    mass_number = int(round(iso_masses[idx]))

                    label_parts.append(f"{mass_number}{el}{count if count > 1 else ''}")

            if not label_parts:
                return "M0"
            return "+".join(label_parts)

        # Canonicalize the formula to ensure consistent element order
        formula = canonicalize_formula(formula)
        # Check for explicit charge in formula
        if "+" in formula or "-" in formula:
            raw_ion_formula = formula.replace("+", "").replace("-", "")
            raw_ion_charge = formula.count("+") - formula.count("-")
        else:
            raw_ion_formula = formula
            raw_ion_charge = 0
        # Predict peaks of high resolution isotopes, with configurations
        predicted_peaks = IsoThreshold(
            formula=raw_ion_formula,
            threshold=isotope_abundance_threshold,
            get_confs=True,
        )
        if raw_ion_charge != 0:
            # Extract high resolution masses and probabilities, correct masses for the electron charge
            masses_high_res = [
                (float(m) - ELECTRON_MASS * raw_ion_charge) / abs(raw_ion_charge)
                for m in predicted_peaks.masses
            ]
        else:
            # If no charge, just use the masses as is
            masses_high_res = [float(m) for m in predicted_peaks.masses]
        probs_high_res = [float(p) for p in predicted_peaks.probs]
        labels = [
            conf_to_label(conf, raw_ion_formula) for conf in predicted_peaks.confs
        ]
        isotopocules_theoretical_df = pd.DataFrame(
            {
                "mz": masses_high_res,
                "relative_abundance": probs_high_res,
                "label": labels,
            }
        ).sort_values(by="mz")

        return isotopocules_theoretical_df

    def get_peaks_in_dmz(
        self, sample_item_id: str, mz: float, dmz: float
    ) -> pd.DataFrame:
        """
        Return peaks within ±dmz of mz.

        This method filters the peaks in the `peaks_matched` DataFrame for a specific sample item ID
        and returns those that fall within the specified mass-to-charge ratio (mz) range,
        defined by the mass deviation tolerance (dmz).

        :param sample_item_id: The ID of the sample item to filter peaks for.
        :type sample_item_id: str
        :param mz: The mass-to-charge ratio to search around.
        :type mz: float
        :param dmz: The mass deviation tolerance in Da (Daltons).
        :type dmz: float
        :return: DataFrame containing peaks within the specified mz range.
        :rtype: pd.DataFrame
        """

        if not hasattr(self, "peaks_matched"):
            logger.warning(
                "Dataset does not have peaks_matched attribute. "
                "Please import peaks first. "
            )
            return pd.DataFrame()

        peaks_matched = self.peaks_matched.copy()  # pylint:disable=no-member
        mz_min = mz - dmz
        mz_max = mz + dmz
        return peaks_matched[
            (peaks_matched["sample_item_id"] == sample_item_id)
            & (peaks_matched["mz"] >= mz_min)
            & (peaks_matched["mz"] <= mz_max)
        ]

    def get_peaks_in_ppm(
        self, sample_item_id: str, mz: float, ppm: float
    ) -> pd.DataFrame:
        """
        Return peaks within ±ppm tolerance of mz.

        This method filters the peaks in the `peaks_matched` DataFrame for a specific sample item ID
        and returns those that fall within the specified mass-to-charge ratio (mz) range,
        defined by the parts per million (ppm) tolerance.

        :param sample_item_id: The ID of the sample item to filter peaks for.
        :type sample_item_id: str
        :param mz: The mass-to-charge ratio to search around.
        :type mz: float
        :param ppm: The parts per million tolerance.
        :type ppm: float
        :return: DataFrame containing peaks within the specified mz range.
        :rtype: pd.DataFrame
        """

        if not hasattr(self, "peaks_matched"):
            logger.warning(
                "Dataset does not have peaks_matched attribute. "
                "Please import peaks first. "
            )
            return pd.DataFrame()

        peaks_matched = self.peaks_matched.copy()  # pylint:disable=no-member

        ppm_tol = mz * ppm / 1e6
        mz_min = mz - ppm_tol
        mz_max = mz + ppm_tol
        return peaks_matched[
            (peaks_matched["sample_item_id"] == sample_item_id)
            & (peaks_matched["mz"] >= mz_min)
            & (peaks_matched["mz"] <= mz_max)
        ]
