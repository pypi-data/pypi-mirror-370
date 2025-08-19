from typing import Tuple, Optional
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import matplotlib.colors as colorvector
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import seaborn as sns
from mpl_toolkits.mplot3d import (  # pylint: disable=unused-import
    Axes3D,  # pylint: disable=unused-import
)  # Importing this registers the 3D projection

from .plots_utils import (
    drop_multiindex_level,
    create_annotations,
    get_color_scale,
    calculate_sparsity_density,
    calculate_skewness_kurtosis,
    prepare_sample_data,
    prepare_mascope_target_data,
    prepare_top_n_heatmap_data,
    prepare_histogram_data,
)
from ..mascope_data.wrapper import MascopeDataWrapper


class BinningPlotter:
    """Class containing functions to build binning related figures."""

    def __init__(self, dataset: MascopeDataWrapper):
        """
        Initialize dataset to self

        :param dataset: MascopeDataWrapper -dataset with
        BinningExtension -extension.
        :type dataset: MascopeDataWrapper
        """
        self.dataset = dataset

    def plot_rtol_across_mz(
        self,
    ) -> Tuple[Figure, Axes]:
        """
        Plot how the rtol changes across the mz-range
        when dynamic rtol is applied.

        :return: Tuple[Figure, Axes]
        """
        # --- 1. Data Preparation ---
        peaks_grouped = self.dataset.peaks_grouped.sort_values("mz")
        if "dynamic_rtol" not in peaks_grouped.columns:
            raise ValueError("No dynamic rtol values found in the dataset.")
        label = peaks_grouped.binning_method.unique()[0]
        # --- 2. Plot Creation ---
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(
            peaks_grouped.mz,
            peaks_grouped.dynamic_rtol,
            label=label,
        )
        # --- 3. Annotations and Extras ---
        ax.set_title("Dynamic rtol across mz-range (Inverse Scaling)")
        ax.set_xlabel("mz")
        ax.set_ylabel("rtol (tolerance)")
        ax.legend()
        return fig, ax

    def plot_heatmap_mzfeatures(
        self,
        matrix: pd.DataFrame,
        ax: Optional[Axes] = None,
        title: str = "Heatmap",
        xlabel: str = "Samples",
        ylabel: str = "mz-features",
        cmap: str = "viridis",
        cbar_label: str = "intensity",
        invert_y: bool = True,
        remove_decimals: bool = True,
        hide_xaxis_labels: bool = True,
        round_index: int = 0,
    ) -> Tuple[Figure, Axes]:
        """Universal function to plot a heatmap for
        any given matrix on a specified axis.


        :param matrix: The input matrix to plot the heatmap.
        :type matrix: pd.DataFrame
        :param ax: The axis on which to plot the heatmap., defaults to None
        :type ax: Optional[Axes], optional
        :param title: The title of the heatmap., defaults to "Heatmap"
        :type title: str, optional
        :param xlabel: The label for the x-axis, defaults to "Samples"
        :type xlabel: str, optional
        :param ylabel: The label for the y-axis, defaults to "mz-features"
        :type ylabel: str, optional
        :param cmap: The colormap to use for the heatmap, defaults to "viridis"
        :type cmap: str, optional
        :param cbar_label: The label for the colorbar, defaults to "intensity"
        :type cbar_label: str, optional
        :param invert_y: should y-axis be inverted, defaults to True
        :type invert_y: bool, optional
        :param remove_decimals: should decimals be removed, defaults to True
        :type remove_decimals: bool, optional
        :param hide_xaxis_labels: should x-axis be hidden, defaults to True
        :type hide_xaxis_labels: bool, optional
        :param round_index: _description_, defaults to 0
        :type round_index: int, optional
        :return: Tuple[Figure, Axes]
        """
        # --- 1. Data Preparation ---
        matrix = matrix.fillna(0)
        # --- 2. Plot Creation ---
        fig = None
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))  # Define figure size
        sns.heatmap(matrix, cmap=cmap, cbar_kws={"label": cbar_label}, ax=ax)
        # --- 3. Annotations and Extras ---
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if invert_y:
            ax.invert_yaxis()
        y_ticks = ax.get_yticks()
        index_labels = matrix.index
        if round_index is not None:
            index_labels = index_labels.round(round_index)
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(
            [index_labels[int(i)] for i in y_ticks if int(i) < len(index_labels)]
        )  # Set rounded labels
        if remove_decimals:
            ax.set_yticklabels(
                [f"{int(float(label.get_text()))}" for label in ax.get_yticklabels()]
            )
        if hide_xaxis_labels:
            ax.set_xticklabels([])
            ax.set_xlabel("")
        plt.close(fig)
        return fig, ax

    def plot_binning_count(
        self,
        binning_count: pd.DataFrame,
        title: str = "Discrete Heatmap",
        xlabel: str = "Samples",
        ylabel: str = "mz-features",
        ax: Optional[Axes] = None,
        invert_y: bool = True,
        remove_decimals: bool = True,
        hide_xaxis_labels: bool = True,
    ) -> Tuple[Figure, Axes]:
        """
        Plots a discrete heatmap of the count matrix on a specified axis.

        :param binning_count: The DataFrame containing the count matrix.
        :type binning_count: pd.DataFrame
        :param ax: The axis on which to plot the heatmap., defaults to None
        :type ax: Optional[Axes], optional
        :param title: The title of the heatmap., defaults to "Heatmap"
        :type title: str, optional
        :param xlabel: The label for the x-axis, defaults to "Samples"
        :type xlabel: str, optional
        :param ylabel: The label for the y-axis, defaults to "mz-features"
        :type ylabel: str, optional
        :param cmap: The colormap to use for the heatmap, defaults to "viridis"
        :type cmap: str, optional
        :param cbar_label: The label for the colorbar, defaults to "intensity"
        :type cbar_label: str, optional
        :param invert_y: should y-axis be inverted, defaults to True
        :type invert_y: bool, optional
        :param remove_decimals: should decimals be removed, defaults to True
        :type remove_decimals: bool, optional
        :param hide_xaxis_labels: should x-axis be hidden, defaults to True
        :type hide_xaxis_labels: bool, optional
        :return: Tuple[Figure, Axes]
        """
        # --- 1. Data Preparation ---
        min_val = binning_count.min().min()
        max_val = binning_count.max().max()
        # Create a list of colors transitioning from white to red
        colors = ["white", "green", "yellow", "#FF7F00", "#FF0000"]
        # Ensure the colormap has at least as many colors as the number of bins
        n_bins = max_val - min_val + 1
        if len(colors) < n_bins:
            # Extend the color list to match the number of bins
            cmap = colorvector.LinearSegmentedColormap.from_list(
                "custom_cmap", colors, N=n_bins
            )
        else:
            # Use the predefined colors if they are sufficient
            cmap = colorvector.ListedColormap(colors[:n_bins])
        # Define the boundaries and normalize
        bounds = np.arange(min_val - 0.5, max_val + 1.5, 1)
        norm = colorvector.BoundaryNorm(bounds, cmap.N)
        # --- 2. Plot Creation ---
        fig = None
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(
            binning_count,
            cmap=cmap,
            norm=norm,
            annot=False,  # Set to True if want to show the counts
            cbar=True,  # Display the color bar
            cbar_kws={
                "ticks": np.arange(min_val, max_val + 1)
            },  # Show all integers on the color bar
            fmt="d",  # Format for the annotations if used
            ax=ax,  # Plot on the provided axis
        )
        # --- 3. Annotations and Extras ---
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if invert_y:
            ax.invert_yaxis()
        # Set rounded index as y-axis labels
        y_ticks = ax.get_yticks()  # Get current y-axis tick positions
        index_labels = binning_count.index  # Get the DataFrame index (mz features)
        index_labels = index_labels.round(0)  # Round index values
        ax.set_yticks(y_ticks)  # Ensure correct tick positions
        ax.set_yticklabels(
            [index_labels[int(i)] for i in y_ticks if int(i) < len(index_labels)]
        )  # Set rounded labels
        if remove_decimals:
            ax.set_yticklabels(
                [f"{int(float(label.get_text()))}" for label in ax.get_yticklabels()]
            )
        if hide_xaxis_labels:
            ax.set_xticklabels([])
            ax.set_xlabel("")
        plt.close(fig)  # Suppress automatic display of the plot
        return fig, ax

    def plot_histogram_with_unique_datetimes(
        self,
        num_bins: int,
        peaks_grouped: pd.DataFrame,
        top_feature_count: int = 5,
        ax: Optional[Axes] = None,
        width: int = 12,
        height: int = 6,
    ) -> Tuple[Figure, Axes]:
        """Histogram of mz group sizes and unique datetime counts in bins.

        :param num_bins: Number of bins to use for the histogram.
        :type num_bins: int
        :param peaks_grouped: DataFrame containing grouped mz-features
        :type peaks_grouped: pd.DataFrame
        :param top_feature_count: count for top features, defaults to 5
        :type top_feature_count: int, optional
        :param ax: Optional[Axes], defaults to None
        :type ax: _type_, optional
        :param width: width of the figure, defaults to 12
        :type width: int, optional
        :param height: height of the figure, defaults to 6
        :type height: int, optional
        :return: Tuple[Figure, Axes]
        """
        # --- 1. Data Preparation ---
        bin_summary_df, top_failed_bins, top_low_unique_bins = prepare_histogram_data(
            peaks_grouped, num_bins, top_feature_count
        )
        # --- 2. Plot Creation ---
        fig = None
        if ax is None:
            fig, ax = plt.subplots(figsize=(width, height))
        # Plot histogram for bin sizes
        ax.bar(
            bin_summary_df["bin"].astype(str),
            bin_summary_df["bin_size"],
            color="blue",
            alpha=0.6,
            label="Bin Size",
        )
        # Overlay histogram for unique datetime counts
        ax.bar(
            bin_summary_df["bin"].astype(str),
            bin_summary_df["unique_datetimes_count"],
            color="red",
            alpha=0.3,
            label="Unique Datetime Count",
        )
        # Add markers for the top failed bins (bin_size >> unique_datetime_count)
        ax.scatter(
            top_failed_bins.index,
            top_failed_bins["bin_size"] + 0.5,
            color="black",
            marker="o",
            s=100,
            label="Top Failure (bin_size >> unique_datetime_count)",
        )
        # Add markers for bins with fewer unique datetimes
        ax.scatter(
            top_low_unique_bins.index,
            top_low_unique_bins["unique_datetimes_count"] + 0.5,
            color="red",
            marker="^",
            s=100,
            label="Low Unique Datetimes",
        )
        # --- 3. Annotations and Extras ---
        tick_step = max(1, len(bin_summary_df) // 15)  # Adjust number of ticks
        ax.set_xticks(
            range(0, len(bin_summary_df), tick_step)
        )  # Set ticks to avoid mismatch
        ax.set_xticklabels(
            bin_summary_df["bin"].astype(str)[::tick_step], rotation=90
        )  # Set corresponding labels
        ax.set_xlabel("mz_weighted_mean")
        ax.set_ylabel("Count")
        ax.set_title("Histogram of mz Group Sizes and Unique Datetime Counts in Bins")
        ax.legend()
        ax.grid(True)
        plt.close(fig)  # Suppress automatic display of the plot
        return fig, ax

    def plot_top_n_heatmap(
        self,
        peaks_grouped: pd.DataFrame,
        matrix: pd.DataFrame,
        n: int = 30,
        is_discrete: bool = False,
        title: int = None,
    ) -> go.FigureWidget:
        """Check the alignment of the top N mz-features based on intensity.

        :param peaks_grouped: DataFrame containing mz-features
        :type peaks_grouped: pd.DataFrame
        :param matrix:  matrix DataFrame
        :type matrix: pd.DataFrame
        :param n: Number of top features to select and plot, defaults to 30
        :type n: int, optional
        :param title: title for figures,
        defaults to None
        :type title: str, optional
        :return: Plotly figure widget
        :rtype: go.FigureWidget
        """
        # --- 1. Data Preparation ---
        matrix = drop_multiindex_level(matrix, "sample_item_id")
        binning_intensity_top_n = prepare_top_n_heatmap_data(peaks_grouped, matrix, n)
        feature_type = "Discrete" if is_discrete else "Continuous"
        if title is None:
            title = (
                f"Top {n} {feature_type} intensity "
                f"Alignment per mz-feature (based on mz_weighted_mean)"
            )
        # --- 2. Plot Creation ---
        fig_top_n = go.FigureWidget()
        # Get the color scale and limits
        color_scale, zmin, zmax = get_color_scale(
            is_discrete, np.max(binning_intensity_top_n.values)
        )
        fig_top_n.add_trace(
            go.Heatmap(
                z=binning_intensity_top_n,
                x=binning_intensity_top_n.columns,
                y=binning_intensity_top_n.index.astype("str"),
                colorscale=color_scale,
                zmin=zmin,
                zmax=zmax,
            )
        )
        # --- 3. Annotations and Extras ---
        fig_top_n.update_layout(title=title)
        # Update layout to control the tick format on y-axis
        fig_top_n.update_layout(
            yaxis={"tickformat": ".3f"}  # Format with `y_axis_decimals` decimal places
        )

        return fig_top_n

    def plot_mascope_targets_heatmap(
        self,
        peaks_grouped: pd.DataFrame,
        match_isotopes: pd,
        matrix: pd.DataFrame,
        is_discrete: bool = False,
        title: str = None,
    ) -> go.FigureWidget:
        """Check the alignment of mascope targets
        by creating a heatmap of matching peaks.


        :param peaks_grouped: DataFrame containing grouped mz-features
        :type peaks_grouped: pd.DataFrame
        :param match_isotopes: DataFrame containing matched isotopes
        :type match_isotopes: pd
        :param matrix: matrix DataFrame
        :type matrix: pd.DataFrame
        :param is_discrete: is data discrete, defaults to False
        :type is_discrete: bool, optional
        :param title: title for the figure, defaults to None
        :type title: str, optional
        :return: Plotly figure widget
        :rtype: go.FigureWidget
        """

        # --- 1. Data Preparation ---
        matrix = drop_multiindex_level(matrix, "sample_item_id")
        target_peak_matrix = prepare_mascope_target_data(peaks_grouped, match_isotopes)
        if len(target_peak_matrix) == 0:
            raise ValueError(
                "No identified Mascope Targets in mz-range "
                f"{min(peaks_grouped.mz)} - {max(peaks_grouped.mz)}"
            )
        # Filter the intensity matrix for the target peaks
        binning_intensity_mcalib = matrix[
            matrix.index.isin(target_peak_matrix.index)
        ].fillna(0)
        # --- 2. Plot Creation ---
        fig_mcalib = go.FigureWidget()
        color_scale, zmin, zmax = get_color_scale(
            is_discrete, np.max(binning_intensity_mcalib.values)
        )
        fig_mcalib.add_trace(
            go.Heatmap(
                z=binning_intensity_mcalib,
                x=binning_intensity_mcalib.columns,
                y=binning_intensity_mcalib.index.astype("str"),
                colorscale=color_scale,
                zmin=zmin,
                zmax=zmax,
            )
        )
        # --- 3. Annotations and Extras ---
        fig_mcalib.update_layout(title=title or "Mascope Targets Heatmap")
        fig_mcalib.update_layout(
            yaxis={"tickformat": ".2f"}  # Format with 2 decimal places
        )
        return fig_mcalib

    def plot_sparsity_density(
        self,
        matrix: pd.DataFrame,
        width: int = 14,
        height: int = 8,
    ) -> Tuple[Figure, Axes]:
        """Plot the sparsity and density of each bin
        using a stacked bar visualization.

        :param matrix: DataFrame containing the binned mz-features.
        :type matrix: pd.DataFrame
        :param width: figure width, defaults to 14
        :type width: int, optional
        :param height: figure height, defaults to 8
        :type height: int, optional
        :return: Tuple[Figure, Axes]
        """
        # --- 1. Data Preparation ---
        combined_df = calculate_sparsity_density(matrix)
        # --- 2. Plot Creation ---
        fig, ax = plt.subplots(figsize=(width, height))
        # Create stacked bars
        bar_width = 0.8
        ax.bar(
            combined_df["Bin"],
            combined_df["Sparsity Ratio"],
            color="red",
            label="Sparsity",
            width=bar_width,
        )
        ax.bar(
            combined_df["Bin"],
            combined_df["Density"],
            bottom=combined_df["Sparsity Ratio"],
            color="lightgreen",
            label="Density",
            width=bar_width,
        )
        ax.legend(loc="upper right")
        # --- 3. Annotations and Extras ---
        # Add a textbox with mean values
        mean_sparsity = combined_df["Sparsity Ratio"].mean()
        mean_density = combined_df["Density"].mean()
        textstr = "\n".join(
            (
                f"Mean Sparsity Ratio: {mean_sparsity:.2f}",
                f"Mean Density: {mean_density:.2f}",
            )
        )
        ax.text(
            0.15,
            1.03,
            textstr,
            verticalalignment="top",
            horizontalalignment="right",
            transform=ax.transAxes,
            fontsize=12,
            bbox={"facecolor": "white", "alpha": 0.5},
        )
        ax.set_xlabel("Weighted mz-feature mean")
        ax.set_ylabel("Proportion")
        ax.set_title("Sparsity and Density of Each Bin (Stacked Bar Visualization)")
        plt.close(fig)  # Suppress automatic display of the plot
        return fig, ax

    def plot_skewness_kurtosis(
        self,
        matrix: pd.DataFrame,
        width: int = 12,
        height: int = 10,
        ax: Optional[Axes] = None,
    ) -> Tuple[Figure, Axes]:
        """Analyze the skewness and kurtosis
        of the binned mz-features to validate the binning process.

        :param matrix: DataFrame containing the binned mz-features.
        where each row represents an mz-feature, and each column
        represents a time point or sample.
        :type matrix: pd.DataFrame
        :param width: figure width, defaults to 12
        :type width: int, optional
        :param height: figure height, defaults to 10
        :type height: int, optional
        :param ax: Optional[Axes], defaults to None
        :type ax: Optional[plt.Axes], optional
        :return: Tuple[Figure, Axes]
        """

        # --- 1. Data Preparation ---
        stats_df = calculate_skewness_kurtosis(matrix)
        # --- 2. Plot Creation ---
        if ax is None:
            fig, ax = plt.subplots(2, 1, figsize=(width, height))
        else:
            fig = ax.figure
            ax = [
                ax,
                ax.twinx(),
            ]  # Use twin axes if only one was given (not ideal but avoids errors)
        # Skewness histogram
        sns.histplot(stats_df["Skewness"], kde=True, color="blue", ax=ax[0])
        ax[0].set_title("Distribution of Feature Skewness")
        ax[0].set_xlabel("Skewness")
        ax[0].set_ylabel("Frequency")
        # Kurtosis histogram
        sns.histplot(stats_df["Kurtosis"], kde=True, color="green", ax=ax[1])
        ax[1].set_title("Distribution of Feature Kurtosis")
        ax[1].set_xlabel("Kurtosis")
        ax[1].set_ylabel("Frequency")
        # --- 3. Annotations and Extras ---
        # Text descriptions
        skewness_text = (
            "Definition: Skewness measures asymmetry in the distribution of values.\n"
            "- Symmetric: Skewness ~ 0\n"
            "- Right-skewed: Positive skewness\n"
            "- Left-skewed: Negative skewness"
        )
        kurtosis_text = (
            "Definition: Kurtosis measures 'tailedness' of the distribution.\n"
            "- Normal: Kurtosis ~ 3\n"
            "- Leptokurtic (>3): Heavy tails, outliers\n"
            "- Platykurtic (<3): Light tails"
        )
        fig.text(0.7, 0.8, skewness_text, wrap=True, ha="center", fontsize=10)
        fig.text(0.7, 0.4, kurtosis_text, wrap=True, ha="center", fontsize=10)
        fig.tight_layout(rect=[0, 0.1, 1, 1])
        plt.close(fig)  # Suppress automatic display of the plot
        return fig, ax

    def plot_outliers_histogram(self, z_scores: pd.DataFrame) -> Tuple[Figure, Axes]:
        """
        Create a histogram of Z-scores.

        :param z_scores: DataFrame of Z-scores.
        :type z_scores: pd.DataFrame
        :return: Tuple[Figure, Axes]
        """

        fig, ax = plt.subplots(figsize=(8, 6))
        z_scores_flat = z_scores.dropna().values.flatten()
        ax.hist(z_scores_flat, bins=50, color="blue", edgecolor="black")
        ax.set_xlabel("Z-score")
        ax.set_ylabel("Frequency")
        ax.set_title("Distribution of Z-scores")
        ax.grid(True)
        plt.close(fig)  # Suppress automatic display
        return fig, ax

    def plot_outliers_ratio(
        self, outlier_ratio: pd.Series, z_threshold: float
    ) -> Tuple[Figure, Axes]:
        """
        Create a bar plot of outlier ratios.

        :param outlier_ratio: Series of outlier ratios.
        :param z_threshold: Z-score threshold.
        :return: Tuple[Figure, Axes]
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        if outlier_ratio.sum() > 0:
            ax.bar(outlier_ratio.index, outlier_ratio, color="orange")
            ax.set_xlabel("Bin")
            ax.set_ylabel("Outlier Ratio")
            ax.set_title("Outlier Ratio of Each Bin")
            ax.grid(True)
        else:
            ax.text(
                0.5,
                0.5,
                f"No Z-scores exceed the threshold ({z_threshold}).",
                ha="center",
                va="center",
                fontsize=12,
                color="gray",
                transform=ax.transAxes,
            )
            ax.set_axis_off()
        plt.close(fig)  # Suppress automatic display
        return fig, ax

    def plot_outliers_boxplot(self, z_scores: pd.DataFrame) -> Tuple[Figure, Axes]:
        """
        Create a box plot of Z-scores.

        :param z_scores: DataFrame of Z-scores.
        :type z_scores: pd.DataFrame
        :return: Tuple[Figure, Axes]
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        z_scores_flat = z_scores.dropna().values.flatten()
        ax.boxplot(z_scores_flat, vert=False)
        ax.set_xlabel("Z-score")
        ax.set_title("Box Plot of Z-scores")
        ax.grid(True)
        plt.close(fig)  # Suppress automatic display
        return fig, ax

    def plot_sample_comparison(
        self,
        sample_idx: str,
        binning_intensity: pd.DataFrame,
        binning_mz: pd.DataFrame,
        peaks_grouped: pd.DataFrame,
        unit: str,
        width: int = 12,
        height: int = 6,
    ) -> Tuple[Figure, Axes]:
        """
        Generate a figure comparing original and
        binned spectra for a single sample.

        :param sample_idx: The sample index to plot.
        :param binning_intensity: DataFrame with binned intensities.
        :param binning_mz: DataFrame with binned mz-values.
        :param peaks_grouped: DataFrame with original spectra data.
        :param unit: Unit of intensity values.
        :param width: Figure width, defaults to 12.
        :param height: Figure height, defaults to 6.
        :return: Tuple[Figure, Axes]
        """
        # --- 1. Data Preparation ---
        binning_intensity = drop_multiindex_level(binning_intensity, "sample_item_id")
        binning_mz = drop_multiindex_level(binning_mz, "sample_item_id")
        original_intensity, binned_intensity, round_df = prepare_sample_data(
            sample_idx, binning_intensity, binning_mz, peaks_grouped
        )
        differ = binned_intensity - original_intensity
        # Find the top 5 positive and negative differences
        top_positive_diffs = differ.nlargest(5)
        top_negative_diffs = differ.nsmallest(5)
        top_diffs = pd.concat([top_positive_diffs, top_negative_diffs])
        # --- 2. Plot Creation ---
        fig, ax = plt.subplots(figsize=(width, height))
        # Plot original mz-feature intensities
        ax.stem(
            round_df.mz,
            round_df.intensity,
            linefmt="-b",
            markerfmt="",
            basefmt=" ",
            label="Original mz-features",
        )
        # Plot the binned mz-features
        ax.stem(
            binning_intensity.index,
            binning_intensity[sample_idx],
            linefmt="-r",
            markerfmt="",
            basefmt=" ",
            label="Binned mz-features",
        )
        # Add lollipop heads for the top positive differences (binned > original)
        ax.stem(
            top_negative_diffs.index,
            binned_intensity[top_negative_diffs.index],
            linefmt="",
            markerfmt="ro",
            basefmt=" ",
            label="Binned > Original",  # Red circles for positive differences
        )
        # Add lollipop heads for the top negative differences (original > binned)
        ax.stem(
            top_positive_diffs.index,
            original_intensity[top_positive_diffs.index],
            linefmt="",
            markerfmt="bo",
            basefmt=" ",
            label="Binned < Original",  # Blue circles for negative differences
        )
        # --- 3. Annotations and Extras ---
        create_annotations(ax, top_diffs, original_intensity, binned_intensity)
        # Filter x-axis labels to show only a subset
        xticks = ax.get_xticks()
        step = max(1, len(xticks) // 10)  # Ensure step is at least 1
        ax.set_xticks(xticks[::step])
        ax.set_title(f"Sample {sample_idx}")
        ax.set_xlabel("mz-Features")
        ax.set_ylabel(f"Intensity ({unit})")
        ax.legend(loc="upper left")
        ax.set_yscale("log")
        ax.grid(True)
        # Add zoomed-in inset for top differences
        zoom_start, zoom_end = top_diffs.index.min(), top_diffs.index.max()
        ax_inset = ax.inset_axes([0.65, 0.2, 0.3, 0.3])
        ax_inset.stem(
            round_df.mz,
            round_df.intensity,
            linefmt="-b",
            markerfmt="bo",
            basefmt=" ",
        )
        ax_inset.stem(
            binning_intensity.index,
            binning_intensity[sample_idx],
            linefmt="-r",
            markerfmt="ro",
            basefmt=" ",
        )
        ax_inset.set_xlim(zoom_start, zoom_end)
        ax_inset.set_yscale("log")
        ax_inset.set_xticklabels([])
        ax.indicate_inset_zoom(ax_inset, edgecolor="black")
        # Count the total occurrences of different cases
        total_original_features = len(original_intensity[original_intensity != 0])
        total_binned_features = len(binned_intensity[binned_intensity != 0])
        # Add difference counts as a text box
        zero_diff_count = (differ == 0).sum()
        positive_diff_count = (differ > 0).sum()
        negative_diff_count = (differ < 0).sum()
        textstr = "\n".join(
            (
                "Total mz-Features:",
                f"Original: {total_original_features}",
                f"Binned: {total_binned_features}",
                "",
                f"Zero Difference: {zero_diff_count}",
                f"Positive Difference: {positive_diff_count}",
                f"Negative Difference: {negative_diff_count}",
            )
        )
        props = {"boxstyle": "round", "facecolor": "wheat", "alpha": 0.5}
        # Adjust layout to prevent overlap
        ax.text(
            0.02,
            0.7,
            textstr,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            bbox=props,
        )
        explanation_text = "\n".join(
            (
                "Explanation of counts:",
                "Zero Difference: No change between original and binned values.",
                "Positive Difference: No matching selected mz and peak shape value in matrices.",
                "Negative Difference: Both mz and peak-area have dropped in pivoting.",
            )
        )
        # Add explanation text to the figure
        fig.text(
            0.5,
            0.01,  # Position at the bottom of the figure
            explanation_text,
            ha="center",
            va="top",
            fontsize=10,
            bbox={"facecolor": "lightyellow", "alpha": 0.5},
        )
        plt.close(fig)  # Suppress automatic display
        return fig, ax
