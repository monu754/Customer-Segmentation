"""
Evaluation module for the customer segmentation project.
Computes clustering evaluation metrics.
"""
import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans


def evaluate_clustering(X: np.ndarray, labels: np.ndarray, model=None) -> dict:
    """
    Evaluate clustering performance.

    Parameters
    ----------
    X : np.ndarray
        Feature array (scaled).
    labels : np.ndarray
        Cluster labels for each sample.
    model : KMeans, optional
        Trained K-Means model (to extract inertia if available).

    Returns
    -------
    metrics : dict
        Dictionary containing evaluation metrics.
    """
    metrics = {}

    # Inertia (if model is provided)
    if model is not None:
        metrics['inertia'] = model.inertia_
    else:
        # Compute inertia manually if model not provided
        # This is a simplified version; for accuracy, we should use the model's inertia_
        # We'll compute sum of squared distances to the nearest centroid
        # But we don't have centroids without the model. So we skip if model is None.
        pass

    # Silhouette score (only if number of clusters is between 2 and n_samples-1)
    n_clusters = len(np.unique(labels))
    n_samples = len(X)
    if n_clusters > 1 and n_clusters < n_samples:
        metrics['silhouette_score'] = silhouette_score(X, labels)
    else:
        metrics['silhouette_score'] = None  # Not defined for single cluster or too many clusters

    return metrics


def evaluate_k_range(X: np.ndarray, k_min: int = 1, k_max: int = 10, random_state: int = 42) -> dict:
    """
    Evaluate a range of K values for elbow method and silhouette score.

    Parameters
    ----------
    X : np.ndarray
        Feature array (scaled).
    k_min : int, optional
        Minimum number of clusters to try. Must be at least 1. Default is 1.
    k_max : int, optional
        Maximum number of clusters to try. Must be at least k_min. Default is 10.
    random_state : int, optional
        Random seed for reproducibility. Default is 42.

    Returns
    -------
    results : dict
        Dictionary containing K values, inertias, and silhouette scores.
    """
    # Validate k_min and k_max
    if k_min < 1:
        raise ValueError("k_min must be at least 1")
    if k_max < k_min:
        raise ValueError("k_max must be at least k_min")
    n_samples = len(X)
    if n_samples < 1:
        raise ValueError("X must contain at least one sample")
    if k_max > n_samples:
        raise ValueError("k_max cannot be greater than the number of samples")
    # We can compute inertia for any k up to n_samples, but silhouette score only for 2 <= k <= n_samples-1
    # We'll compute both for k in [k_min, k_max] but set silhouette to None when invalid.
    inertias = []
    silhouette_scores = []
    k_values = list(range(k_min, k_max+1))

    for k in k_values:
        kmeans = KMeans(n_clusters=k, init='k-means++', random_state=random_state, n_init=10)
        kmeans.fit(X)
        inertias.append(kmeans.inertia_)
        if k > 1 and k < n_samples:
            score = silhouette_score(X, kmeans.labels_)
            silhouette_scores.append(score)
        else:
            silhouette_scores.append(None)

    return {
        'k_values': k_values,
        'inertias': inertias,
        'silhouette_scores': silhouette_scores
    }


def select_best_k(k_values, silhouette_scores) -> int:
    """Return the K with the highest valid silhouette score."""
    valid = [
        (k, score)
        for k, score in zip(k_values, silhouette_scores)
        if score is not None
    ]
    if not valid:
        return k_values[0]
    return max(valid, key=lambda item: item[1])[0]


def generate_selection_rationale(k_values, inertias, silhouette_scores, selected_k) -> str:
    """
    Generate a rationale for selecting the optimal K based on elbow method and silhouette score.

    Parameters
    ----------
    k_values : list of int
        List of K values tried.
    inertias : list of float
        Inertia values for each K.
    silhouette_scores : list of float or None
        Silhouette scores for each K (None for invalid K).
    selected_k : int
        The selected number of clusters.

    Returns
    -------
    rationale : str
        Explanation of the trade-off and justification for selected K.
    """
    # Find the elbow point (point of maximum curvature)
    # We'll use a simple method: find the point where the relative decrease in inertia is less than 70% of the previous decrease.
    # Alternatively, we can use the "knee" location detection, but for simplicity, we'll compute the percentage decrease.
    if len(inertias) < 2:
        elbow_rationale = "Insufficient data points for elbow method."
    else:
        # Compute percentage decrease in inertia
        decreases = []
        for i in range(1, len(inertias)):
            if inertias[i-1] == 0:
                decrease = 0
            else:
                decrease = (inertias[i-1] - inertias[i]) / inertias[i-1]
            decreases.append(decrease)
        # Find the point where the decrease drops below a threshold (e.g., 70% of the maximum decrease)
        if decreases:
            max_decrease = max(decreases)
            threshold = 0.3 * max_decrease  # if decrease is less than 30% of max, consider it elbow
            elbow_points = [i for i, d in enumerate(decreases) if d < threshold]
            if elbow_points:
                elbow_k = k_values[elbow_points[0] + 1]  # +1 because decreases[i] is between k_values[i] and k_values[i+1]
                elbow_rationale = f"Elbow method suggests K={elbow_k} (inertia decrease drops below {threshold*100:.1f}% of max decrease)."
            else:
                elbow_rationale = "Elbow method unclear: no clear drop in inertia decrease rate."
        else:
            elbow_rationale = "Elbow method unclear: no inertia decreases."

    # Silhouette score rationale
    valid_scores = [score for score in silhouette_scores if score is not None]
    if valid_scores:
        max_score = max(valid_scores)
        # Find all K with score close to max (within 1%)
        max_ks = [k for k, score in zip(k_values, silhouette_scores) if score is not None and score >= 0.99 * max_score]
        if len(max_ks) == 1:
            silhouette_rationale = f"Silhouette score is maximized at K={max_ks[0]} (score={max_score:.4f})."
        else:
            silhouette_rationale = f"Silhouette score is relatively flat (max={max_score:.4f}) for K in {max_ks}."
    else:
        silhouette_rationale = "No valid silhouette scores (K values too low or too high)."

    # Selected K rationale
    selected_inertia = inertias[k_values.index(selected_k)]
    selected_score = silhouette_scores[k_values.index(selected_k)]
    selected_rationale = f"Selected K={selected_k}: inertia={selected_inertia:.2f}, silhouette score={selected_score if selected_score is not None else 'N/A'}."

    # Combine rationales
    rationale = (
        f"K Selection Rationale:\n"
        f"{elbow_rationale}\n"
        f"{silhouette_rationale}\n"
        f"{selected_rationale}\n"
        f"Note: The elbow method is heuristic; silhouette score measures cluster separation and cohesion. "
        f"Consider both metrics and domain knowledge when selecting K."
    )
    return rationale