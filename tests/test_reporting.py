"""
Unit tests for the reporting module.
"""
import os
import tempfile
import numpy as np
import pandas as pd
import pytest
from src.reporting import save_processed_data, save_model, generate_cluster_summary, save_cluster_summary, save_evaluation_metrics
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib


def test_save_processed_data(tmpdir):
    """Test saving processed data with cluster labels."""
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [4, 5, 6]
    })
    labels = np.array([0, 1, 0])
    output_dir = str(tmpdir)
    output_path = os.path.join(output_dir, 'processed.csv')
    save_processed_data(df, labels, output_path)
    assert os.path.exists(output_path)
    df_loaded = pd.read_csv(output_path)
    assert 'Cluster' in df_loaded.columns
    assert df_loaded['Cluster'].tolist() == [0, 1, 0]
    # Original columns should be preserved
    assert 'A' in df_loaded.columns
    assert 'B' in df_loaded.columns


def test_save_model(tmpdir):
    """Test saving the model and scaler."""
    # Create a simple KMeans model and scaler
    X = np.array([[1, 2], [1, 4], [4, 2], [4, 4]])
    model = KMeans(n_clusters=2, random_state=0).fit(X)
    scaler = StandardScaler().fit(X)
    output_dir = str(tmpdir)
    output_path = os.path.join(output_dir, 'model.pkl')
    save_model(model, scaler, output_path)
    assert os.path.exists(output_path)
    # Load the saved object and check contents
    saved = joblib.load(output_path)
    assert 'model' in saved
    assert 'scaler' in saved
    # Check that the model is a KMeans instance
    assert isinstance(saved['model'], KMeans)
    # Check that the scaler is a StandardScaler instance
    assert isinstance(saved['scaler'], StandardScaler)


def test_generate_cluster_summary():
    """Test generating cluster summary."""
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5, 6],
        'B': [10, 20, 30, 40, 50, 60]
    })
    labels = np.array([0, 0, 1, 1, 0, 1])
    feature_names = ['A', 'B']
    summary = generate_cluster_summary(df, labels, feature_names)
    assert isinstance(summary, pd.DataFrame)
    # Should have one row per cluster
    assert len(summary) == 2
    # Check that the cluster column is present
    assert 'Cluster' in summary.columns
    # Check that size column is present
    assert 'Size' in summary.columns
    # Check that mean columns are present
    assert 'A_mean' in summary.columns
    assert 'B_mean' in summary.columns
    # Check the sizes: cluster 0 has 3 samples, cluster 1 has 3 samples
    assert summary.loc[summary['Cluster'] == 0, 'Size'].values[0] == 3
    assert summary.loc[summary['Cluster'] == 1, 'Size'].values[0] == 3
    # Check the means (approximate)
    # Cluster 0: A values [1,2,5] -> mean 8/3 ≈ 2.666667; B values [10,20,50] -> mean 80/3 ≈ 26.666667
    # Cluster 1: A values [3,4,6] -> mean 13/3 ≈ 4.333333; B values [30,40,60] -> mean 130/3 ≈ 43.333333
    np.testing.assert_allclose(summary.loc[summary['Cluster'] == 0, 'A_mean'].values[0], 8/3, rtol=1e-5)
    np.testing.assert_allclose(summary.loc[summary['Cluster'] == 0, 'B_mean'].values[0], 80/3, rtol=1e-5)
    np.testing.assert_allclose(summary.loc[summary['Cluster'] == 1, 'A_mean'].values[0], 13/3, rtol=1e-5)
    np.testing.assert_allclose(summary.loc[summary['Cluster'] == 1, 'B_mean'].values[0], 130/3, rtol=1e-5)


def test_save_cluster_summary(tmpdir):
    """Test saving cluster summary to CSV."""
    summary_df = pd.DataFrame({
        'Cluster': [0, 1],
        'Size': [10, 15],
        'A_mean': [1.5, 2.5],
        'B_mean': [15.5, 25.5]
    })
    output_dir = str(tmpdir)
    output_path = os.path.join(output_dir, 'summary.csv')
    save_cluster_summary(summary_df, output_path)
    assert os.path.exists(output_path)
    summary_loaded = pd.read_csv(output_path)
    pd.testing.assert_frame_equal(summary_loaded, summary_df)


def test_save_evaluation_metrics(tmpdir):
    """Test saving evaluation metrics to JSON."""
    metrics = {
        'inertia': 123.456,
        'silhouette_score': 0.789
    }
    output_dir = str(tmpdir)
    output_path = os.path.join(output_dir, 'metrics.json')
    save_evaluation_metrics(metrics, output_path)
    assert os.path.exists(output_path)
    import json
    with open(output_path, 'r') as f:
        metrics_loaded = json.load(f)
    assert metrics_loaded == metrics