"""
Preprocessing module for the customer segmentation project.
Handles missing values, feature selection, and feature scaling.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import Tuple, List, Optional


def preprocess_data(
    df: pd.DataFrame,
    features: Optional[List[str]] = None,
    handle_missing: str = 'median',
    remove_duplicates: bool = True,
    scale_features: bool = True
) -> Tuple[pd.DataFrame, np.ndarray, StandardScaler, List[str]]:
    """
    Preprocess the data for clustering.

    Parameters
    ----------
    df : pd.DataFrame
        Input data.
    features : list of str, optional
        Features to use for clustering. If None, use all numeric columns.
    handle_missing : str, optional
        How to handle missing values: 'median', 'mean', or 'drop'.
        Default is 'median'.
    remove_duplicates : bool, optional
        Whether to remove duplicate rows. Default is True.
    scale_features : bool, optional
        Whether to scale features using StandardScaler. Default is True.

    Returns
    -------
    cleaned_df : pd.DataFrame
        DataFrame after handling missing values and duplicates (with original index of kept rows).
    processed_data : np.ndarray
        Processed feature array (scaled if scale_features=True).
    scaler : StandardScaler
        Fitted scaler object (if scale_features=True, else None).
    feature_names : list of str
        Names of the features used.
    """
    # Make a copy to avoid modifying the original
    df_cleaned = df.copy()

    # Handle missing values
    if handle_missing == 'median':
        for col in df_cleaned.select_dtypes(include=[np.number]).columns:
            df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].median())
    elif handle_missing == 'mean':
        for col in df_cleaned.select_dtypes(include=[np.number]).columns:
            df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mean())
    elif handle_missing == 'drop':
        df_cleaned = df_cleaned.dropna()
    else:
        raise ValueError(f"Unsupported handle_missing value: {handle_missing}")

    # Remove duplicates
    if remove_duplicates:
        df_cleaned = df_cleaned.drop_duplicates()

    # Select features
    if features is None:
        # Use all numeric columns
        feature_names = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
    else:
        feature_names = features
        # Ensure all selected features exist in the dataframe
        missing_features = set(feature_names) - set(df_cleaned.columns)
        if missing_features:
            raise ValueError(f"The following features are not in the dataframe: {missing_features}")

    # Extract the feature data
    X = df_cleaned[feature_names].values

    # Scale features
    if scale_features:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
    else:
        scaler = None
        X_scaled = X

    return df_cleaned, X_scaled, scaler, feature_names