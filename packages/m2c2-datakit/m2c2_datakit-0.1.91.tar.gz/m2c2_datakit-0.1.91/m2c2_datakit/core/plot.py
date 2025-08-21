import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl

from .config import (settings)


def plot_pairplot(df: pd.DataFrame):
    """
    Plot a pairplot for all numeric variables in the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to plot.
    """
    # Set the global aesthetic style and high-quality font
    sns.set(style="whitegrid", rc={"axes.facecolor": "#F5F5F5"})
    mpl.rcParams["font.family"] = "Arial"
    mpl.rcParams["figure.dpi"] = settings.DEFAULT_DPI  # High DPI for clarity

    # Create pairplot with clean styling
    pairplot = sns.pairplot(
        df,
        diag_kind="kde",
        plot_kws={"alpha": 0.7, "color": settings.DEFAULT_PLOT_COLOR},
        diag_kws={"color": settings.DEFAULT_PLOT_COLOR},
    )
    pairplot.fig.suptitle(
        "Pairplot of Variables", fontsize=16, fontweight="bold", y=1.02
    )
    plt.show()


def plot_distribution(df: pd.DataFrame):
    """
    Plot the distribution of each numeric variable in the DataFrame as separate plots.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to plot.
    """
    # Set a clean, modern Seaborn theme
    sns.set_theme(style="whitegrid", rc={"axes.facecolor": "#F9F9F9"})

    # Get a color palette
    palette = sns.color_palette("muted", len(df.columns))

    # Iterate through each numeric column and plot
    for i, column in enumerate(df.select_dtypes(include=["number"]).columns):
        fig, ax = plt.subplots(figsize=(8, 4))  # Explicitly create a new figure
        sns.histplot(
            df[column],
            kde=True,
            label=column,
            alpha=0.8,
            color=palette[i % len(palette)],  # Rotate through colors
            edgecolor="black",
            ax=ax,  # Ensure plotting happens in the right figure
        )

        # Style the plot titles and labels
        ax.set_title(
            f"Distribution of {column}", fontsize=16, fontweight="bold", pad=12
        )
        ax.set_xlabel("Value", fontsize=13)
        ax.set_ylabel("Frequency", fontsize=13)
        ax.tick_params(axis="both", labelsize=11)

        # Add a legend with better placement
        ax.legend(fontsize=11, loc="best", frameon=False)

        # Remove unnecessary spines for a sleek look
        sns.despine(ax=ax, left=True, bottom=True)

        # Enhance layout
        plt.tight_layout()

        # Explicitly show each figure before creating the next
        plt.show()
