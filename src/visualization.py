"""
Visualization module for the customer segmentation project.
Creates plots for exploratory analysis, elbow method, silhouette scores, and cluster visualization.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import pandas as pd
from typing import List, Optional


def plot_elbow(k_values: List[int], inertias: List[float], output_dir: str) -> None:
    """
    Plot the elbow method (inertia vs. K) and save to output_dir.

    Parameters
    ----------
    k_values : list of int
        List of K values tried.
    inertias : list of float
        Inertia values for each K.
    output_dir : str
        Directory to save the plot.
    """
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(8, 6))
    plt.plot(k_values, inertias, 'bo-')
    plt.xlabel('Number of clusters (K)')
    plt.ylabel('Inertia (Within-Cluster Sum of Squares)')
    plt.title('Elbow Method for Optimal K')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'elbow_plot.png'))
    plt.close()


def plot_silhouette(k_values: List[int], silhouette_scores: List[Optional[float]], output_dir: str) -> None:
    """
    Plot silhouette scores vs. K and save to output_dir.

    Parameters
    ----------
    k_values : list of int
        List of K values tried.
    silhouette_scores : list of float or None
        Silhouette scores for each K (None for invalid K).
    output_dir : str
        Directory to save the plot.
    """
    os.makedirs(output_dir, exist_ok=True)
    # Filter out None values for plotting
    valid_k = []
    valid_scores = []
    for k, score in zip(k_values, silhouette_scores):
        if score is not None:
            valid_k.append(k)
            valid_scores.append(score)
    if not valid_k:
        return
    plt.figure(figsize=(8, 6))
    plt.plot(valid_k, valid_scores, 'go-')
    plt.xlabel('Number of clusters (K)')
    plt.ylabel('Silhouette Score')
    plt.title('Silhouette Score for Optimal K')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'silhouette_plot.png'))
    plt.close()


def plot_clusters(X: np.ndarray, labels: np.ndarray, centroids: np.ndarray, feature_names: List[str], output_dir: str) -> None:
    """
    Plot clusters in 2D (using the first two features) and save to output_dir.

    Parameters
    ----------
    X : np.ndarray
        Feature array (scaled).
    labels : np.ndarray
        Cluster labels.
    centroids : np.ndarray
        Cluster centroids (in scaled feature space).
    feature_names : list of str
        Names of the features (should be at least two).
    output_dir : str
        Directory to save the plot.
    """
    os.makedirs(output_dir, exist_ok=True)
    if len(feature_names) < 2:
        # If we have less than two features, we cannot create a scatter plot.
        # We could use PCA, but for simplicity, we skip.
        return
    # We'll use the first two features for visualization
    x_idx = 0
    y_idx = 1
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(X[:, x_idx], X[:, y_idx], c=labels, cmap='viridis', alpha=0.6)
    # Plot centroids
    plt.scatter(centroids[:, x_idx], centroids[:, y_idx], c='red', marker='X', s=200, label='Centroids')
    plt.xlabel(feature_names[x_idx])
    plt.ylabel(feature_names[y_idx])
    plt.title('Customer Segments (K-Means Clustering)')
    plt.legend()
    plt.colorbar(scatter, label='Cluster Label')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'cluster_visualization.png'))
    plt.close()


def plot_feature_distributions(df: pd.DataFrame, features: List[str], output_dir: str) -> None:
    """
    Plot histograms for each feature and save to output_dir.
    This function is similar to the one in eda.py but is kept here for completeness.
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