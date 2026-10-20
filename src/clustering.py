"""
Clustering module for the customer segmentation project.
Implements K-Means clustering using scikit-learn.
"""
from sklearn.cluster import KMeans
import numpy as np


def train_kmeans(X: np.ndarray, n_clusters: int, random_state: int = 42, n_init: int = 10) -> tuple:
    """
    Train a K-Means clustering model.

    Parameters
    ----------
    X : np.ndarray
        Feature array (scaled).
    n_clusters : int
        Number of clusters.
    random_state : int, optional
        Random seed for reproducibility. Default is 42.
    n_init : int, optional
        Number of times the K-Means algorithm is run with different centroid seeds.
        Default is 10.

    Returns
    -------
    model : KMeans
        Trained K-Means model.
    labels : np.ndarray
        Cluster labels for each sample.
    centroids : np.ndarray
        Cluster centroids (in the scaled feature space).
    """
    model = KMeans(
        n_clusters=n_clusters,
        init='k-means++',
        n_init=n_init,
        random_state=random_state
    )
    model.fit(X)
    labels = model.labels_
    centroids = model.cluster_centers_
    return model, labels, centroids