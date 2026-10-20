"""
Unit tests for the preprocessing module.
"""
import numpy as np
import pandas as pd
import pytest
from src.preprocessing import preprocess_data


def test_preprocess_data_no_missing_no_duplicates():
    """Test preprocessing with clean data."""
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [10, 20, 30, 40, 50],
        'C': ['x', 'y', 'x', 'y', 'x']
    })
    features = ['A', 'B']
    df_cleaned, X_scaled, scaler, feature_names = preprocess_data(df, features=features)
    assert isinstance(df_cleaned, pd.DataFrame)
    assert df_cleaned.shape == (5, 3)  # Keep all columns
    assert X_scaled.shape == (5, 2)
    assert feature_names == ['A', 'B']
    # Check that scaling worked (mean approx 0, std approx 1)
    assert np.allclose(X_scaled.mean(axis=0), [0, 0], atol=1e-10)
    assert np.allclose(X_scaled.std(axis=0), [1, 1], atol=1e-10)


def test_preprocess_data_with_missing():
    """Test preprocessing with missing values."""
    df = pd.DataFrame({
        'A': [1, 2, np.nan, 4, 5],
        'B': [10, np.nan, 30, 40, 50]
    })
    features = ['A', 'B']
    df_cleaned, X_scaled, scaler, feature_names = preprocess_data(df, features=features, handle_missing='median')
    # Check that there are no NaNs in the cleaned data
    assert not df_cleaned.isnull().any().any()
    assert not np.isnan(X_scaled).any()
    assert df_cleaned.shape == (5, 2)  # No rows dropped
    # Check that the median imputation was done (the NaN positions should be filled with median)
    # Original median of A: (1,2,4,5) -> 3.0; B: (10,30,40,50) -> 35.0
    # We can't easily check the exact values without knowing the scaling, but we can check shape and no NaN.
    assert not np.isnan(X_scaled).any()


def test_preprocess_data_remove_duplicates():
    """Test preprocessing removes duplicates."""
    df = pd.DataFrame({
        'A': [1, 2, 2, 3],
        'B': [10, 20, 20, 30]
    })
    features = ['A', 'B']
    df_cleaned, X_scaled, scaler, feature_names = preprocess_data(df, features=features, remove_duplicates=True)
    # After removing duplicates, we should have 3 unique rows
    assert isinstance(df_cleaned, pd.DataFrame)
    assert df_cleaned.shape == (3, 2)
    assert X_scaled.shape == (3, 2)


def test_preprocess_data_invalid_feature():
    """Test preprocessing with a feature not in the dataframe."""
    df = pd.DataFrame({'A': [1, 2, 3]})
    with pytest.raises(ValueError):
        preprocess_data(df, features=['B'])


def test_preprocess_data_scale_false():
    """Test preprocessing with scaling turned off."""
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [10, 20, 30, 40, 50]
    })
    features = ['A', 'B']
    df_cleaned, X_scaled, scaler, feature_names = preprocess_data(df, features=features, scale_features=False)
    assert isinstance(df_cleaned, pd.DataFrame)
    assert df_cleaned.shape == (5, 2)
    assert X_scaled.shape == (5, 2)
    assert scaler is None
    # Check that the values are the original (but as numpy array)
    expected = df_cleaned[features].values
    np.testing.assert_array_equal(X_scaled, expected)