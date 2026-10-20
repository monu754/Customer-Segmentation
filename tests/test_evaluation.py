"""
Unit tests for the evaluation module.
"""
import numpy as np
import pytest
from src.evaluation import evaluate_clustering, evaluate_k_range, select_best_k
from sklearn.cluster import KMeans


def test_evaluate_clustering():
    """Test evaluating clustering performance."""
    # Simple deterministic data with clear clusters
    X = np.array([[1, 2], [1, 4], [1, 0],
                  [4, 2], [4, 4], [4, 0]])
    labels = np.array([0, 0, 0, 1, 1, 1])  # First three in cluster 0, last three in cluster 1
    # We need a model to get inertia; we can train one
    model = KMeans(n_clusters=2, random_state=0).fit(X)
    metrics = evaluate_clustering(X, labels, model)
    assert 'inertia' in metrics
    assert 'silhouette_score' in metrics
    assert metrics['inertia'] >= 0
    # Silhouette score should be between -1 and 1
    assert -1 <= metrics['silhouette_score'] <= 1


def test_evaluate_clustering_single_cluster():
    """Test evaluating clustering with a single cluster (silhouette score undefined)."""
    X = np.array([[1, 2], [1, 4], [1, 0]])
    labels = np.array([0, 0, 0])
    model = KMeans(n_clusters=1, random_state=0).fit(X)
    metrics = evaluate_clustering(X, labels, model)
    assert metrics['inertia'] >= 0
    assert metrics['silhouette_score'] is None  # Not defined for single cluster


def test_evaluate_k_range():
    """Test evaluating a range of K values."""
    # Create data with two clear clusters
    X = np.array([[1, 2], [1, 4], [1, 0],
                  [4, 2], [4, 4], [4, 0]])
    results = evaluate_k_range(X, k_min=1, k_max=5)
    assert 'k_values' in results
    assert 'inertias' in results
    assert 'silhouette_scores' in results
    assert results['k_values'] == list(range(1, 6))
    assert len(results['inertias']) == 5
    assert len(results['silhouette_scores']) == 5
    # Silhouette score for k=1 should be None
    assert results['silhouette_scores'][0] is None
    # For k=2, we expect a valid silhouette score
    assert results['silhouette_scores'][1] is not None
    # Inertias should be non-negative and decreasing (or at least not increasing dramatically)
    for inertia in results['inertias']:
        assert inertia >= 0


def test_select_best_k_keeps_k_and_score_aligned():
    """The selected K must correspond to the maximum score's original position."""
    assert select_best_k([1, 2, 3, 4], [None, 0.2, 0.8, 0.4]) == 3


def test_evaluate_k_range_rejects_more_clusters_than_samples():
    """Invalid K ranges fail with a clear validation error."""
    X = np.array([[1, 2], [3, 4]])
    with pytest.raises(ValueError, match="number of samples"):
        evaluate_k_range(X, k_min=1, k_max=3)