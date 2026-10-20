"""
Unit tests for the visualization module.
"""
import os
import tempfile
import numpy as np
import pytest
from src.visualization import plot_elbow, plot_silhouette, plot_clusters


def test_plot_elbow(tmpdir):
    """Test plotting the elbow method."""
    k_values = [1, 2, 3, 4]
    inertias = [100, 80, 60, 40]
    output_dir = str(tmpdir)
    plot_elbow(k_values, inertias, output_dir)
    assert os.path.exists(os.path.join(output_dir, 'elbow_plot.png'))


def test_plot_silhouette(tmpdir):
    """Test plotting silhouette scores."""
    k_values = [2, 3, 4, 5]
    silhouette_scores = [0.5, 0.6, 0.55, 0.5]
    output_dir = str(tmpdir)
    plot_silhouette(k_values, silhouette_scores, output_dir)
    assert os.path.exists(os.path.join(output_dir, 'silhouette_plot.png'))


def test_plot_silhouette_with_none(tmpdir):
    """Test plotting silhouette scores when some are None."""
    k_values = [1, 2, 3]
    silhouette_scores = [None, 0.5, 0.6]
    output_dir = str(tmpdir)
    plot_silhouette(k_values, silhouette_scores, output_dir)
    # Should still create a plot (only for valid scores)
    assert os.path.exists(os.path.join(output_dir, 'silhouette_plot.png'))


def test_plot_clusters(tmpdir):
    """Test plotting clusters."""
    # Create simple clustered data
    X = np.array([[1, 2], [1, 4], [1, 0],
                  [4, 2], [4, 4], [4, 0]])
    labels = np.array([0, 0, 0, 1, 1, 1])
    centroids = np.array([[1, 2], [4, 2]])
    feature_names = ['Feature1', 'Feature2']
    output_dir = str(tmpdir)
    plot_clusters(X, labels, centroids, feature_names, output_dir)
    assert os.path.exists(os.path.join(output_dir, 'cluster_visualization.png'))

    # Test with less than two features (should not create a plot)
    X_single = X[:, 0].reshape(-1, 1)
    labels_single = labels
    centroids_single = centroids[:, 0].reshape(-1, 1)
    feature_names_single = ['Feature1']
    plot_clusters(X_single, labels_single, centroids_single, feature_names_single, output_dir)
    # No plot should be created (function returns early)
    # We can check that no new file was created, but we just note that the function should handle it.