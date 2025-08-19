from typing import Tuple
import pandas as pd
import numpy as np
from scipy.stats import zscore


def drop_multiindex_level(df: pd.DataFrame, level: str) -> pd.DataFrame:
    """
    Drop a specific level from the MultiIndex columns of a DataFrame.

    :param df: DataFrame with MultiIndex columns.
    :type df: pd.DataFrame
    :param level: The level name to drop from the MultiIndex.
    :type level: str
    :return: DataFrame with the specified level dropped from the MultiIndex columns.
    :rtype: pd.DataFrame

    Used in:
    - BinningPlotter.plot_top_n_heatmap
    - BinningPlotter.plot_mascope_targets_heatmap
    - BinningPlotter.plot_sample_comparison
    """
    if (
        isinstance(df.columns, pd.MultiIndex) and level in df.columns.names
    ):  ## Check if level exists in MultiIndex
        df = df.copy()  # Avoid modifying the original DataFrame
        df.columns = df.columns.droplevel(level)  # Drop the specified level
        df = df.sort_index(axis=1)  # Sort columns by the remaining level
    return df


def summarize_bins_with_unique_datetimes(
    df: pd.DataFrame, bin_edges: int
) -> pd.DataFrame:
    """
    Summarize the bins with unique datetime counts.

    :param df: DataFrame containing grouped mz-features
    :type df: pd.DataFrame
    :param bin_edges: Bin edges for binning
    :type bin_edges: int
    :return: DataFrame with bin summary
    :rtype: pd.DataFrame

    Used in:
    - BinningPlotter.plot_histogram_with_unique_datetimes
    """

    # Use precomputed bin edges
    df["bin"] = pd.cut(df["mz_weighted_mean"], bins=bin_edges, include_lowest=True)

    # Aggregate bin data
    bin_summary = (
        df.groupby("bin", observed=True)
        .agg(
            {
                "datetime": pd.Series.nunique,  # Count unique datetimes
                "mz_weighted_mean": "size",  # Count the size of each bin
            }
        )
        .reset_index()
        .rename(
            columns={
                "datetime": "unique_datetimes_count",
                "mz_weighted_mean": "bin_size",
            }
        )
    )

    return bin_summary


def get_top_n_mz_features(
    df: pd.DataFrame,
    n: int,
) -> list:
    """Get the top N mz-features based on intensity.

    :param df: DataFrame containing grouped mz-features
    :type df: pd.DataFrame
    :param n: Number of top features to select, defaults to 30
    :type n: int
    :return: List of top N mz_weighted_mean -values
    :rtype: list

    Used in:
    - BinningPlotter.plot_top_n_heatmap
    """
    df_sorted = df.sort_values("intensity", ascending=False)
    # Collect the top N mean-mz based on intensity
    top_n = (
        df_sorted["mz_weighted_mean"][
            df_sorted["mz_group"].isin(df_sorted["mz_group"].unique()[:n])
        ]
        .unique()
        .tolist()
    )

    return top_n


def create_annotations(
    ax, top_diffs: pd.Series, original_intensity: pd.Series, binned_intensity: pd.Series
):
    """Adds annotations to the plot for the top differences.

    :param ax: matplotlib axis object to add annotations to
    :type ax: _type_
    :param top_diffs: Series with top differences to annotate
    :type top_diffs: pd.Series
    :param original_intensity: Series of original intensities
    :type original_intensity: pd.Series
    :param binned_intensity: Series of binned intensities
    :type binned_intensity: pd.Series

    Used in:
    - BinningPlotter.plot_sample_comparison
    """

    top_diffs = top_diffs[~top_diffs.index.duplicated()]
    # Select values based on the condition
    y_values = binned_intensity.where(top_diffs < 0, original_intensity)
    for idx in top_diffs.index:
        value = top_diffs.loc[idx]
        y_value = y_values[idx]
        ax.annotate(
            f"{idx:.2f}\n({value:.2f})",
            (idx, y_value),
            textcoords="offset points",
            xytext=(0, 15 if value > 0 else -15),
            ha="center",
            color="black",
            arrowprops=dict(arrowstyle="->", lw=0.5),
        )


def get_color_scale(is_discrete: bool, zmax: float) -> tuple:
    """
    Generate a color scale for heatmaps based on whether the data is discrete or continuous.

    :param is_discrete: Whether the data is discrete.
    :type is_discrete: bool
    :param zmax: Maximum value in the data.
    :type zmax: float
    :return: Tuple containing the color scale, zmin, and zmax.
    :rtype: tuple

    Used in:
    - BinningPlotter.plot_top_n_heatmap
    - BinningPlotter.plot_mascope_targets_heatmap
    """
    if is_discrete:
        if zmax > 2:
            color_scale = [
                [0.0, "white"],
                [1.0 / zmax, "green"],
                [2.0 / zmax, "yellow"],
                [3.0 / zmax, "orange"],
                [1.0, "darkred"],
            ]
        elif zmax == 1:
            color_scale = [
                [0.0, "white"],
                [1, "green"],
            ]
        else:
            color_scale = [
                [0.0, "white"],
                [0.5, "green"],
                [1.0, "yellow"],
            ]
        zmin = 0
    else:
        color_scale = "Viridis"  # Default continuous color scale
        zmin = None
        zmax = None

    return color_scale, zmin, zmax


def calculate_sparsity_density(matrix: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate sparsity and density for each bin.

    :param matrix: DataFrame containing the binned mz-features.
    :return: DataFrame with sparsity and density for each bin.

    Used in:
    - BinningPlotter.plot_sparsity_density
    """
    zero_counts = (matrix.fillna(0) == 0).sum(axis=1)
    total_elements = matrix.shape[1]  # Number of samples (columns)

    sparsity_ratio = zero_counts / total_elements
    density = 1 - sparsity_ratio

    return pd.DataFrame(
        {
            "Bin": matrix.index,
            "Sparsity Ratio": sparsity_ratio,
            "Density": density,
        }
    )


def calculate_skewness_kurtosis(matrix: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate skewness and kurtosis for each mz-feature.

    :param matrix: DataFrame containing the binned mz-features.
    :return: DataFrame with skewness and kurtosis for each mz-feature.

    Used in:
    - BinningPlotter.plot_skewness_kurtosis
    """

    feature_skewness = matrix.skew(axis=1)
    feature_kurtosis = matrix.kurtosis(axis=1)

    return pd.DataFrame({"Skewness": feature_skewness, "Kurtosis": feature_kurtosis})


def calculate_z_scores(matrix: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Z-scores for each mz-feature within each bin.

    :param matrix: DataFrame with binned mz-features.
    :return: DataFrame of Z-scores.

    Used in:
    - BinningPlotter.plot_outliers_histogram
    - BinningPlotter.plot_outliers_boxplot
    """
    if matrix.isna().any().any():
        matrix = matrix.fillna(0)

    z_scores = matrix.apply(zscore, axis=1)
    return pd.DataFrame(z_scores.tolist(), index=matrix.index, columns=matrix.columns)


def calculate_outliers(
    matrix: pd.DataFrame, z_threshold: float = 3.0
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Calculate Z-scores and outlier ratios.

    :param matrix: DataFrame containing the binned mz-features.
    :param z_threshold: Z-score threshold.
    :return: Tuple containing Z-scores and outlier ratios.
    :rtype: Tuple[pd.DataFrame, pd.Series]

    Used in:
    - BinningPlotter.plot_outliers_ratio
    """
    z_scores = calculate_z_scores(matrix)
    outliers = (z_scores.abs() > z_threshold).astype(int)
    outlier_ratio = outliers.sum(axis=1) / outliers.shape[1]
    return z_scores, outlier_ratio


def prepare_sample_data(
    sample_idx: str,
    binning_intensity: pd.DataFrame,
    binning_mz: pd.DataFrame,
    peaks_grouped: pd.DataFrame,
) -> Tuple[pd.Series, pd.Series, pd.DataFrame]:
    """
    Prepare data for a given sample by extracting and aligning intensities
    from orginal peaks and binned peaks.

    :param sample_idx: The sample index to process.
    :type sample_idx: str
    :param binning_intensity: DataFrame with binned intensities.
    :type binning_intensity: pd.DataFrame
    :param binning_mz: DataFrame with binned mz-values.
    :type binning_mz: pd.DataFrame
    :param peaks_grouped: DataFrame with original spectra data.
    :type peaks_grouped: pd.DataFrame
    :return: Tuple containing original_intensity, binned_intensity, and mz_values.
    :rtype: Tuple[pd.Series, pd.Series, pd.DataFrame]

    Used in:
    - BinningPlotter.plot_sample_comparison
    """
    # Extract binned intensity and mz-values for the sample
    binned_intensity = binning_intensity[sample_idx].dropna()
    binned_intensity.index = binning_mz[sample_idx].dropna().values

    # Extract original intensity and mz-values for the sample
    round_df = peaks_grouped[peaks_grouped["datetime"] == sample_idx]
    original_intensity = round_df["intensity"]
    original_intensity.index = round_df["mz"]
    original_intensity = original_intensity.dropna()

    # Align indices and fill missing values with 0
    original_intensity = original_intensity.reindex(
        original_intensity.index.union(binned_intensity.index), fill_value=0
    )
    binned_intensity = binned_intensity.reindex(
        original_intensity.index.union(binned_intensity.index), fill_value=0
    )

    return original_intensity, binned_intensity, round_df


def prepare_mascope_target_data(
    peaks_grouped: pd.DataFrame,
    match_isotopes: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Prepare data for plotting mascope target heatmap.

    :param peaks_grouped: DataFrame containing grouped mz-features.
    :type peaks_grouped: pd.DataFrame
    :param match_isotopes: DataFrame containing matched isotopes.
    :type peaks_grouped: pd.DataFrame
    :return: Tuple containing the filtered mz-matrix and target peak matrix.
    :type: Tuple[pd.DataFrame, pd.DataFrame]

    Used in:
    - BinningPlotter.plot_mascope_targets_heatmap
    """
    # Create mz-matrix from mascope peaks DataFrame
    binning_mz = peaks_grouped.pivot_table(
        index="mz_weighted_mean", columns="datetime", values="mz", fill_value=None
    )
    # Collect target peaks m/z values
    target_peaks = (
        match_isotopes.sample_peak_mz[match_isotopes.sample_peak_intensity != 0]
        .unique()
        .tolist()
    )
    # Extract rows from mz-matrix that match the target peaks
    target_peak_matrix_list = [
        binning_mz[binning_mz.eq(x).any(axis=1)] for x in target_peaks
    ]
    target_peak_matrix = pd.concat(target_peak_matrix_list).drop_duplicates()

    return target_peak_matrix


def prepare_top_n_heatmap_data(
    peaks_grouped: pd.DataFrame,
    matrix: pd.DataFrame,
    n: int,
) -> pd.DataFrame:
    """
    Prepare data for plotting the top N mz-features heatmap.

    :param peaks_grouped: DataFrame containing mz-features.
    :type peaks_grouped: pd.DataFrame
    :param matrix: DataFrame containing the intensity matrix.
    :type matrix: pd.DataFrame
    :param n: Number of top features to select.
    :type n: int
    :return: Filtered intensity matrix for the top N mz-features.
    :rtype: pd.DataFrame

    Used in:
    - BinningPlotter.plot_top_n_heatmap
    """
    # Get top N mz-features based on intensity
    top_n_mz_features = get_top_n_mz_features(peaks_grouped, n)
    # Filter the matrix for the top N mz-features
    binning_intensity_top_n = matrix[matrix.index.isin(top_n_mz_features)].fillna(0)

    return binning_intensity_top_n


def prepare_histogram_data(
    peaks_grouped: pd.DataFrame,
    num_bins: int,
    top_feature_count: int,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Prepare data for plotting the histogram of mz group sizes and unique datetime counts.

    :param peaks_grouped: DataFrame containing grouped mz-features.
    :type peaks_grouped: pd.DataFrame
    :param num_bins: Number of bins to use for the histogram.
    :type num_bins: int
    :param top_feature_count: Number of top features to identify.
    :type top_feature_count: int
    :return: Tuple containing the bin summary DataFrame,
    top failed bins, and top low unique bins.
    :rtype: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]

    Used in:
    - BinningPlotter.plot_histogram_with_unique_datetimes
    """
    # Precompute unique mz_weighted_mean values and bin edges
    unique_mz = sorted(peaks_grouped["mz_weighted_mean"].unique())
    bin_edges = np.linspace(min(unique_mz), max(unique_mz), num_bins + 1)
    # Summarize bin data
    bin_summary_df = summarize_bins_with_unique_datetimes(
        df=peaks_grouped, bin_edges=bin_edges
    )
    # Calculate the failure metric
    bin_summary_df["failure_metric"] = (
        bin_summary_df["bin_size"] - bin_summary_df["unique_datetimes_count"]
    )
    # Identify top failed bins (where bin_size >> unique_datetime_count)
    top_failed_bins = bin_summary_df.nlargest(top_feature_count, "failure_metric")
    # Filter out cases where unique_datetime_count is zero
    bin_summary_df_nonzero = bin_summary_df[
        bin_summary_df["unique_datetimes_count"] > 0
    ]
    # Identify top bins with low unique datetime counts
    top_low_unique_bins = bin_summary_df_nonzero.nsmallest(
        top_feature_count, "unique_datetimes_count"
    )

    return bin_summary_df, top_failed_bins, top_low_unique_bins
