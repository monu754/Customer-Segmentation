"""
Exploratory Data Analysis module for the customer segmentation project.
Generates dataset summaries and visualizations.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import List, Optional


def generate_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate summary statistics for the dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Input data.

    Returns
    -------
    pd.DataFrame
        Summary statistics (transposed describe).
    """
    summary = df.describe(include=[np.number]).T
    return summary


def plot_histograms(df: pd.DataFrame, features: List[str], output_dir: str) -> None:
    """
    Plot histograms for the specified features and save to output_dir.

    Parameters
    ----------
    df : pd.DataFrame
        Input data.
    features : list of str
        Features to plot.
    output_dir : str
        Directory to save the plots.
    """
    os.makedirs(output_dir, exist_ok=True)
    for feature in features:
        plt.figure(figsize=(8, 6))
        sns.histplot(df[feature], kde=True)
        plt.title(f'Histogram of {feature}')
        plt.xlabel(feature)
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'histogram_{feature.replace(" ", "_").replace("(", "").replace(")", "")}.png'))
        plt.close()


def plot_boxplots(df: pd.DataFrame, features: List[str], output_dir: str) -> None:
    """
    Plot box plots for the specified features and save to output_dir.

    Parameters
    ----------
    df : pd.DataFrame
        Input data.
    features : list of str
        Features to plot.
    output_dir : str
        Directory to save the plots.
    """
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df[features])
    plt.title('Box Plots of Features')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'boxplots.png'))
    plt.close()


def plot_scatter(df: pd.DataFrame, feature_x: str, feature_y: str, output_dir: str, hue: Optional[str] = None) -> None:
    """
    Plot a scatter plot of two features and save to output_dir.

    Parameters
    ----------
    df : pd.DataFrame
        Input data.
    feature_x : str
        Feature for x-axis.
    feature_y : str
        Feature for y-axis.
    output_dir : str
        Directory to save the plot.
    hue : str, optional
        Feature to color points by (e.g., cluster label).
    """
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(8, 6))
    if hue is not None:
        sns.scatterplot(data=df, x=feature_x, y=feature_y, hue=hue, palette='viridis')
        plt.legend(title=hue)
    else:
        sns.scatterplot(data=df, x=feature_x, y=feature_y)
    plt.title(f'Scatter Plot: {feature_x} vs {feature_y}')
    plt.xlabel(feature_x)
    plt.ylabel(feature_y)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'scatter_{feature_x.replace(" ", "_")}_vs_{feature_y.replace(" ", "_")}.png'))
    plt.close()


def perform_eda(df: pd.DataFrame, features: List[str], output_dir: str) -> pd.DataFrame:
    """
    Perform exploratory data analysis: generate summary and plots.

    Parameters
    ----------
    df : pd.DataFrame
        Input data.
    features : list of str
        Features to analyze.
    output_dir : str
        Directory to save outputs.

    Returns
    -------
    pd.DataFrame
        Summary statistics.
    """
    # Generate summary
    summary = generate_summary(df)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Save summary to CSV
    summary_path = os.path.join(output_dir, 'eda_summary.csv')
    summary.to_csv(summary_path)

    # Plot histograms
    plot_histograms(df, features, output_dir)

    # Plot box plots
    plot_boxplots(df, features, output_dir)

    # Plot scatter plot for the first two features (if at least two features)
    if len(features) >= 2:
        plot_scatter(df, features[0], features[1], output_dir)

    return summary