"""
Main script for the customer segmentation project.
Orchestrates the complete workflow: data loading, preprocessing, EDA,
clustering, evaluation, visualization, and reporting.
"""
import os
import sys
import argparse
import json

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from data_loader import load_data
from preprocessing import preprocess_data
from eda import perform_eda
from clustering import train_kmeans
from evaluation import evaluate_clustering, evaluate_k_range, generate_selection_rationale, select_best_k
from visualization import plot_elbow, plot_silhouette, plot_clusters
from reporting import save_processed_data, save_model, generate_cluster_summary, save_cluster_summary, save_evaluation_metrics


def main():
    parser = argparse.ArgumentParser(description='Customer Segmentation using K-Means Clustering')
    parser.add_argument('--data', type=str, default='data/raw/Mall_Customers.csv', help='Path to the input data file (CSV or Excel)')
    parser.add_argument('--features', type=str, nargs='+', default=['Annual Income (k$)', 'Spending Score (1-100)'], help='Features to use for clustering')
    parser.add_argument('--k_min', type=int, default=2, help='Minimum number of clusters to evaluate')
    parser.add_argument('--k_max', type=int, default=10, help='Maximum number of clusters to evaluate')
    parser.add_argument('--random_state', type=int, default=42, help='Random seed for reproducibility')
    parser.add_argument('--skip_eda', action='store_true', help='Skip exploratory analysis to speed up execution')
    args = parser.parse_args()

    # Create output directories
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('outputs/plots', exist_ok=True)
    os.makedirs('outputs/models', exist_ok=True)
    os.makedirs('outputs/reports', exist_ok=True)

    print("Loading data...")
    df_original = load_data(args.data)
    print(f"Loaded data with shape: {df_original.shape}")

    if not args.skip_eda:
        print("Performing exploratory data analysis on original data...")
        summary = perform_eda(df_original, args.features, 'outputs/plots')
        print("EDA summary saved to outputs/plots/eda_summary.csv")

    print("Preprocessing data...")
    df_cleaned, X_scaled, scaler, feature_names = preprocess_data(df_original, features=args.features)
    print(f"Cleaned data shape: {df_cleaned.shape}")
    print(f"Preprocessed data shape: {X_scaled.shape}")
    print(f"Features used: {feature_names}")
    print(f"Rows removed during preprocessing: {len(df_original) - len(df_cleaned)}")

    print(f"Evaluating K range from {args.k_min} to {args.k_max}...")
    k_results = evaluate_k_range(X_scaled, k_min=args.k_min, k_max=args.k_max, random_state=args.random_state)

    best_k = select_best_k(k_results['k_values'], k_results['silhouette_scores'])
    if all(score is None for score in k_results['silhouette_scores']):
        print("Warning: No valid silhouette scores. Defaulting to the first evaluated K.")
    print(f"Best K based on silhouette score: {best_k}")

    # Generate elbow and silhouette plots for the evaluated K range
    print("Generating elbow and silhouette plots...")
    plot_elbow(k_results['k_values'], k_results['inertias'], 'outputs/plots')
    plot_silhouette(k_results['k_values'], k_results['silhouette_scores'], 'outputs/plots')

    print(f"Training K-Means model with K={best_k}...")
    model, labels, centroids = train_kmeans(X_scaled, n_clusters=best_k, random_state=args.random_state)
    print(f"Model inertia: {model.inertia_}")

    print("Evaluating clustering...")
    metrics = evaluate_clustering(X_scaled, labels, model)
    print(f"Inertia: {metrics.get('inertia')}")
    print(f"Silhouette score: {metrics.get('silhouette_score')}")

    # Generate selection rationale
    rationale = generate_selection_rationale(
        k_results['k_values'],
        k_results['inertias'],
        k_results['silhouette_scores'],
        best_k
    )
    print("\n" + rationale)

    print("Creating visualizations...")
    plot_clusters(X_scaled, labels, centroids, feature_names, 'outputs/plots')

    print("Generating reports...")
    # Save processed data with cluster labels (using cleaned data)
    save_processed_data(df_cleaned, labels, 'data/processed/customers_clustered.csv')
    # Save the model and scaler
    save_model(model, scaler, 'outputs/models/kmeans_model.pkl')
    # Generate and save cluster summary
    cluster_summary = generate_cluster_summary(df_cleaned, labels, feature_names)
    save_cluster_summary(cluster_summary, 'outputs/reports/cluster_summary.csv')
    # Save evaluation metrics for the selected K
    save_evaluation_metrics(metrics, 'outputs/reports/metrics.json')
    # Save full evaluation results (K range) and rationale
    evaluation_results = {
        'k_values': k_results['k_values'],
        'inertias': k_results['inertias'],
        'silhouette_scores': k_results['silhouette_scores'],
        'selected_k': best_k,
        'selection_rationale': rationale
    }
    with open('outputs/reports/evaluation_results.json', 'w') as f:
        json.dump(evaluation_results, f, indent=2)
    print("Full evaluation results saved to outputs/reports/evaluation_results.json")

    print("Done! All outputs have been generated.")
    print(f"Processed data saved to: data/processed/customers_clustered.csv")
    print(f"Model saved to: outputs/models/kmeans_model.pkl")
    print(f"Cluster summary saved to: outputs/reports/cluster_summary.csv")
    print(f"Evaluation metrics saved to: outputs/reports/metrics.json")
    print(f"Evaluation details saved to: outputs/reports/evaluation_results.json")
    print(f"Plots saved to: outputs/plots/")


if __name__ == "__main__":
    main()