"""
Reporting module for the customer segmentation project.
Generates reports, saves processed data, model, and summaries.
"""
import pandas as pd
import numpy as np
import os
import joblib
from typing import List, Optional


def save_processed_data(df: pd.DataFrame, labels: np.ndarray, output_path: str) -> None:
    """
    Save the processed data with cluster labels to a CSV file.

    Parameters
    ----------
    df : pd.DataFrame
        Original data (cleaned).
    labels : np.ndarray
        Cluster labels for each sample.
    output_path : str
        Path to save the CSV file.
    """
    # Create a copy to avoid modifying the original
    df_out = df.copy()
    # Add cluster labels
    df_out['Cluster'] = labels
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Save to CSV
    df_out.to_csv(output_path, index=False)


def save_model(model, scaler, output_path: str) -> None:
    """
    Save the trained K-Means model and scaler to a file using joblib.

    Parameters
    ----------
    model : KMeans
        Trained K-Means model.
    scaler : StandardScaler
        Fitted scaler object.
    output_path : str
        Path to save the model file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump({'model': model, 'scaler': scaler}, output_path)


def generate_cluster_summary(df: pd.DataFrame, labels: np.ndarray, feature_names: List[str]) -> pd.DataFrame:
    """
    Generate a summary of each cluster (size, centroid values in original feature space).

    Parameters
    ----------
    df : pd.DataFrame
        Original data (cleaned, with the same features used for clustering).
    labels : np.ndarray
        Cluster labels for each sample.
    feature_names : list of str
        Names of the features used for clustering.

    Returns
    -------
    summary_df : pd.DataFrame
        Summary statistics for each cluster.
    """
    # Add labels to the dataframe
    df_with_labels = df.copy()
    df_with_labels['Cluster'] = labels

    # Group by cluster and compute size and mean
    summary = df_with_labels.groupby('Cluster').agg(
        Size=('Cluster', 'size'),
        **{f'{feat}_mean': (feat, 'mean') for feat in feature_names}
    ).reset_index()
    return summary


def save_cluster_summary(summary_df: pd.DataFrame, output_path: str) -> None:
    """
    Save the cluster summary to a CSV file.

    Parameters
    ----------
    summary_df : pd.DataFrame
        Cluster summary data.
    output_path : str
        Path to save the CSV file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    summary_df.to_csv(output_path, index=False)


def save_evaluation_metrics(metrics: dict, output_path: str) -> None:
    """
    Save evaluation metrics to a JSON file.

    Parameters
    ----------
    metrics : dict
        Dictionary of evaluation metrics.
    output_path : str
        Path to save the JSON file.
    """
    import json
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=4)