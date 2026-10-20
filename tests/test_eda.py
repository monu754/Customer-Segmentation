"""
Unit tests for the eda module.
"""
import os
import tempfile
import pandas as pd
import pytest
from src.eda import perform_eda, generate_summary, plot_histograms, plot_boxplots, plot_scatter


def test_generate_summary():
    """Test generating summary statistics."""
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [10, 20, 30, 40, 50]
    })
    summary = generate_summary(df)
    assert isinstance(summary, pd.DataFrame)
    assert summary.shape == (2, 8)  # count, mean, std, min, 25%, 50%, 75%, max
    assert 'A' in summary.index
    assert 'B' in summary.index


def test_perform_eda(tmpdir):
    """Test performing EDA and saving outputs."""
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [10, 20, 30, 40, 50]
    })
    features = ['A', 'B']
    output_dir = str(tmpdir)
    summary = perform_eda(df, features, output_dir)
    # Check that summary is returned
    assert isinstance(summary, pd.DataFrame)
    # Check that output files were created
    assert os.path.exists(os.path.join(output_dir, 'eda_summary.csv'))
    assert os.path.exists(os.path.join(output_dir, 'histogram_A.png'))
    assert os.path.exists(os.path.join(output_dir, 'histogram_B.png'))
    assert os.path.exists(os.path.join(output_dir, 'boxplots.png'))
    assert os.path.exists(os.path.join(output_dir, 'scatter_A_vs_B.png'))


def test_plot_histograms(tmpdir):
    """Test plotting histograms."""
    df = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
    output_dir = str(tmpdir)
    plot_histograms(df, ['A'], output_dir)
    assert os.path.exists(os.path.join(output_dir, 'histogram_A.png'))


def test_plot_boxplots(tmpdir):
    """Test plotting box plots."""
    df = pd.DataFrame({'A': [1, 2, 3, 4, 5], 'B': [10, 20, 30, 40, 50]})
    output_dir = str(tmpdir)
    plot_boxplots(df, ['A', 'B'], output_dir)
    assert os.path.exists(os.path.join(output_dir, 'boxplots.png'))


def test_plot_scatter(tmpdir):
    """Test plotting scatter plot."""
    df = pd.DataFrame({'A': [1, 2, 3, 4, 5], 'B': [10, 20, 30, 40, 50]})
    output_dir = str(tmpdir)
    plot_scatter(df, 'A', 'B', output_dir)
    assert os.path.exists(os.path.join(output_dir, 'scatter_A_vs_B.png'))

    # Test with hue
    df['C'] = ['x', 'y', 'x', 'y', 'x']
    plot_scatter(df, 'A', 'B', output_dir, hue='C')
    # The file name is the same, but we can check that it was overwritten (or we could check the content, but we just check existence)
    assert os.path.exists(os.path.join(output_dir, 'scatter_A_vs_B.png'))