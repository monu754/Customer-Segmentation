"""
Unit tests for the clustering module.
"""
import numpy as np
import pytest
from src.clustering import train_kmeans
from sklearn.cluster import KMeans


def test_train_kmeans():
    """Test training a K-Means model."""
    # Simple deterministic data
    X = np.array([[1, 2], [1, 4], [1, 0],
                  [4, 2], [4, 4], [4, 0]])
    model, labels, centroids = train_kmeans(X, n_clusters=2, random_state=0)
    # Check that we got a KMeans model
    assert isinstance(model, KMeans)
    # Check that labels are integers and in range [0, n_clusters-1]
    assert labels.dtype.kind in 'iu'  # integer
    assert np.all(labels >= 0) and np.all(labels < 2)
    # Check that centroids shape is correct
    assert centroids.shape == (2, 2)
    # Check that the model's inertia is non-negative
    assert model.inertia_ >= 0


def test_train_kmeans_reproducibility():
    """Test that setting random_state gives reproducible results."""
    X = np.random.RandomState(42).randn(100, 2)
    model1, labels1, _ = train_kmeans(X, n_clusters=3, random_state=123)
    model2, labels2, _ = train_kmeans(X, n_clusters=3, random_state=123)
    # Labels should be identical
    np.testing.assert_array_equal(labels1, labels2)
    # Centroids should be identical
    np.testing.assert_array_equal(model1.cluster_centers_, model2.cluster_centers_)