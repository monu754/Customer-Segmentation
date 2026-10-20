"""
FastAPI application for the Customer Segmentation K-Means clustering project.
Provides REST API endpoints that reuse the existing Python modules.
"""
import os
import json
import uuid
import shutil
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np

# Add the src directory to the path so we can import the existing modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_loader import load_data
from preprocessing import preprocess_data
from eda import perform_eda
from clustering import train_kmeans
from evaluation import evaluate_clustering, evaluate_k_range, generate_selection_rationale
from visualization import plot_elbow, plot_silhouette, plot_clusters
from reporting import (
    save_processed_data, save_model, generate_cluster_summary,
    save_cluster_summary, save_evaluation_metrics
)

# Initialize FastAPI app
app = FastAPI(
    title="Customer Segmentation K-Means API",
    description="REST API for customer segmentation using K-Means clustering",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for datasets and analyses (in production, use a database or file storage)
# Structure: {dataset_id: {"data": df, "filename": str, "upload_time": datetime}}
datasets = {}
analyses = {}

# Create necessary directories
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)
os.makedirs('outputs/plots', exist_ok=True)
os.makedirs('outputs/models', exist_ok=True)
os.makedirs('outputs/reports', exist_ok=True)
os.makedirs('temp', exist_ok=True)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Customer Segmentation K-Means API"}


@app.post("/api/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload a CSV or Excel file and return dataset ID and metadata.
    """
    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ['.csv', '.xlsx', '.xls']:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Only CSV and Excel files are allowed."
        )

    # Generate unique dataset ID
    dataset_id = str(uuid.uuid4())

    # Save uploaded file temporarily
    temp_file_path = f"temp/{dataset_id}_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Load the data to get metadata
        df = load_data(temp_file_path)

        # Store dataset info
        datasets[dataset_id] = {
            "data": df,
            "filename": file.filename,
            "file_path": temp_file_path,
            "upload_time": pd.Timestamp.now()
        }

        # Return dataset metadata (convert numpy types to Python native types for JSON serialization)
        return {
            "dataset_id": dataset_id,
            "filename": file.filename,
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "column_names": df.columns.tolist(),
            "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
            "missing_values": {k: int(v) for k, v in df.isnull().sum().to_dict().items()},
            "duplicate_rows": int(df.duplicated().sum())
        }

    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/api/datasets/{dataset_id}/preview")
async def get_dataset_preview(dataset_id: str, rows: int = 10):
    """
    Get a preview of the dataset (first N rows, column info).
    """
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = datasets[dataset_id]["data"]

    # Get preview data
    preview_df = df.head(rows)

    return {
        "dataset_id": dataset_id,
        "filename": datasets[dataset_id]["filename"],
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": df.columns.tolist(),
        "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "preview_rows": preview_df.fillna("").to_dict(orient="records"),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum())
    }


@app.get("/api/datasets/{dataset_id}/summary")
async def get_dataset_summary(dataset_id: str):
    """
    Get statistical summary and data quality report.
    """
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = datasets[dataset_id]["data"]

    # Basic statistics for numeric columns
    numeric_df = df.select_dtypes(include=[np.number])
    stats = {}
    if not numeric_df.empty:
        stats = numeric_df.describe().to_dict()

    # Column information
    column_info = []
    for col in df.columns:
        col_info = {
            "name": col,
            "type": str(df[col].dtype),
            "missing_count": int(df[col].isnull().sum()),
            "missing_percentage": round((df[col].isnull().sum() / len(df)) * 100, 2),
            "unique_count": int(df[col].nunique())
        }

        # Add numeric stats if applicable
        if df[col].dtype in [np.int64, np.float64, np.int32, np.float32]:
            col_info.update({
                "mean": float(df[col].mean()) if not df[col].isnull().all() else None,
                "median": float(df[col].median()) if not df[col].isnull().all() else None,
                "std": float(df[col].std()) if not df[col].isnull().all() else None,
                "min": float(df[col].min()) if not df[col].isnull().all() else None,
                "max": float(df[col].max()) if not df[col].isnull().all() else None
            })

        column_info.append(col_info)

    return {
        "dataset_id": dataset_id,
        "filename": datasets[dataset_id]["filename"],
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "column_info": column_info,
        "summary_statistics": stats,
        "data_quality": {
            "total_missing_values": int(df.isnull().sum().sum()),
            "columns_with_missing": [col for col in df.columns if df[col].isnull().sum() > 0],
            "duplicate_rows": int(df.duplicated().sum()),
            "memory_usage": int(df.memory_usage(deep=True).sum())
        }
    }


@app.delete("/api/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """
    Delete a dataset and associated analyses.
    """
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Clean up file
    file_path = datasets[dataset_id]["file_path"]
    if os.path.exists(file_path):
        os.remove(file_path)

    # Remove from storage
    del datasets[dataset_id]

    # Also remove any analyses associated with this dataset
    analyses_to_remove = [aid for aid, analysis in analyses.items()
                         if analysis.get("dataset_id") == dataset_id]
    for aid in analyses_to_remove:
        del analyses[aid]

    return {"message": "Dataset deleted successfully"}


@app.post("/api/analysis/eda")
async def run_eda(dataset_id: str, features: List[str]):
    """
    Generate exploratory analysis results for a dataset and selected features.
    """
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = datasets[dataset_id]["data"]

    # Validate features exist
    missing_features = set(features) - set(df.columns)
    if missing_features:
        raise HTTPException(
            status_code=400,
            detail=f"The following features are not in the dataset: {list(missing_features)}"
        )

    # Generate analysis ID
    analysis_id = str(uuid.uuid4())

    try:
        # Perform EDA
        eda_summary = perform_eda(df, features, 'outputs/plots')

        # Store analysis info
        analyses[analysis_id] = {
            "dataset_id": dataset_id,
            "type": "eda",
            "features": features,
            "eda_summary": eda_summary,
            "timestamp": pd.Timestamp.now(),
            "status": "completed"
        }

        return {
            "analysis_id": analysis_id,
            "dataset_id": dataset_id,
            "type": "eda",
            "features": features,
            "status": "completed",
            "eda_summary": eda_summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing EDA: {str(e)}")


@app.get("/api/analysis/{analysis_id}/eda/plots/{plot_name}")
async def get_eda_plot(analysis_id: str, plot_name: str):
    """
    Retrieve a specific EDA plot image.
    """
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = analyses[analysis_id]
    if analysis["type"] != "eda":
        raise HTTPException(status_code=400, detail="Analysis is not an EDA analysis")

    # Construct plot file path
    plot_path = f"outputs/plots/{plot_name}.png"
    if not os.path.exists(plot_path):
        # Try to find any plot that matches the name
        import glob
        matching_plots = glob.glob(f"outputs/plots/*{plot_name}*.png")
        if not matching_plots:
            raise HTTPException(status_code=404, detail="Plot not found")
        plot_path = matching_plots[0]

    return FileResponse(plot_path, media_type="image/png")


@app.post("/api/clustering/run")
async def run_clustering(
    dataset_id: str,
    features: List[str],
    k_min: int = 2,
    k_max: int = 10,
    random_state: int = 42,
    n_init: int = 10
):
    """
    Run K-Means clustering on a dataset with given parameters.
    """
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Validate parameters
    if k_min < 1:
        raise HTTPException(status_code=400, detail="k_min must be at least 1")
    if k_max < k_min:
        raise HTTPException(status_code=400, detail="k_max must be greater than or equal to k_min")
    if k_max > 20:  # Reasonable upper limit
        raise HTTPException(status_code=400, detail="k_max should not exceed 20 for performance reasons")

    df = datasets[dataset_id]["data"]

    # Validate features exist and are numeric
    missing_features = set(features) - set(df.columns)
    if missing_features:
        raise HTTPException(
            status_code=400,
            detail=f"The following features are not in the dataset: {list(missing_features)}"
        )

    # Check if features are numeric
    non_numeric_features = []
    for feature in features:
        if feature in df.columns and df[feature].dtype not in [np.int64, np.float64, np.int32, np.float32]:
            non_numeric_features.append(feature)

    if non_numeric_features:
        raise HTTPException(
            status_code=400,
            detail=f"The following features are not numeric and cannot be used for clustering: {non_numeric_features}"
        )

    # Generate analysis ID
    analysis_id = str(uuid.uuid4())

    try:
        # Preprocess data
        df_cleaned, X_scaled, scaler, feature_names = preprocess_data(
            df, features=features, scale_features=True
        )

        # Evaluate K range
        k_results = evaluate_k_range(X_scaled, k_min=k_min, k_max=k_max, random_state=random_state)

        # Select the best K based on silhouette score (ignoring None values)
        valid_scores = [score for score in k_results['silhouette_scores'] if score is not None]
        if not valid_scores:
            # If no valid silhouette scores (e.g., all K invalid), default to k_min
            best_k = k_min
        else:
            # Find the index of the maximum silhouette score
            best_idx = valid_scores.index(max(valid_scores))
            best_k = k_results['k_values'][best_idx]

        # Train K-Means model with best K
        model, labels, centroids = train_kmeans(
            X_scaled, n_clusters=best_k, random_state=random_state, n_init=n_init
        )

        # Evaluate clustering
        metrics = evaluate_clustering(X_scaled, labels, model)

        # Generate selection rationale
        rationale = generate_selection_rationale(
            k_results['k_values'],
            k_results['inertias'],
            k_results['silhouette_scores'],
            best_k
        )

        # Generate visualizations
        plot_elbow(k_results['k_values'], k_results['inertias'], 'outputs/plots')
        plot_silhouette(k_results['k_values'], k_results['silhouette_scores'], 'outputs/plots')
        plot_clusters(X_scaled, labels, centroids, feature_names, 'outputs/plots')

        # Generate reports
        # Save processed data with cluster labels
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

        # Store analysis info
        analyses[analysis_id] = {
            "dataset_id": dataset_id,
            "type": "clustering",
            "features": features,
            "k_min": k_min,
            "k_max": k_max,
            "best_k": best_k,
            "random_state": random_state,
            "n_init": n_init,
            "timestamp": pd.Timestamp.now(),
            "status": "completed",
            "results": {
                "metrics": metrics,
                "cluster_summary": cluster_summary.to_dict() if hasattr(cluster_summary, 'to_dict') else cluster_summary,
                "evaluation_results": evaluation_results,
                "feature_names": feature_names
            }
        }

        return {
            "analysis_id": analysis_id,
            "dataset_id": dataset_id,
            "type": "clustering",
            "features": features,
            "k_range_evaluated": list(range(k_min, k_max + 1)),
            "selected_k": best_k,
            "status": "completed",
            "results": {
                "metrics": metrics,
                "evaluation_results": evaluation_results,
                "cluster_summary": cluster_summary.to_dict() if hasattr(cluster_summary, 'to_dict') else cluster_summary
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running clustering: {str(e)}")


@app.get("/api/analysis/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """
    Get the status of an analysis run.
    """
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = analyses[analysis_id]
    return {
        "analysis_id": analysis_id,
        "status": analysis["status"],
        "type": analysis["type"],
        "timestamp": analysis["timestamp"]
    }


@app.get("/api/analysis/{analysis_id}/results")
async def get_analysis_results(analysis_id: str):
    """
    Get the full results of a completed clustering run.
    """
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = analyses[analysis_id]
    if analysis["type"] != "clustering":
        raise HTTPException(status_code=400, detail="Analysis is not a clustering analysis")

    if analysis["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis is not completed yet")

    return {
        "analysis_id": analysis_id,
        "dataset_id": analysis["dataset_id"],
        "type": analysis["type"],
        "features": analysis["features"],
        "best_k": analysis["best_k"],
        "timestamp": analysis["timestamp"],
        "results": analysis["results"]
    }


@app.get("/api/analysis/{analysis_id}/clusters")
async def get_cluster_summaries(analysis_id: str):
    """
    Get cluster summaries (size, centroids, etc.).
    """
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = analyses[analysis_id]
    if analysis["type"] != "clustering":
        raise HTTPException(status_code=400, detail="Analysis is not a clustering analysis")

    if analysis["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis is not completed yet")

    return {
        "analysis_id": analysis_id,
        "cluster_summary": analysis["results"]["cluster_summary"]
    }


@app.get("/api/analysis/{analysis_id}/evaluations")
async def get_evaluation_results(analysis_id: str):
    """
    Get evaluation metrics for the evaluated K range.
    """
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = analyses[analysis_id]
    if analysis["type"] != "clustering":
        raise HTTPException(status_code=400, detail="Analysis is not a clustering analysis")

    if analysis["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis is not completed yet")

    return {
        "analysis_id": analysis_id,
        "evaluation_results": analysis["results"]["evaluation_results"]
    }


@app.get("/api/analysis/{analysis_id}/plots/elbow")
async def get_elbow_plot(analysis_id: str):
    """
    Retrieve elbow plot image.
    """
    plot_path = "outputs/plots/elbow_plot.png"
    if not os.path.exists(plot_path):
        raise HTTPException(status_code=404, detail="Elbow plot not found")
    return FileResponse(plot_path, media_type="image/png")


@app.get("/api/analysis/{analysis_id}/plots/silhouette")
async def get_silhouette_plot(analysis_id: str):
    """
    Retrieve silhouette plot image.
    """
    plot_path = "outputs/plots/silhouette_plot.png"
    if not os.path.exists(plot_path):
        raise HTTPException(status_code=404, detail="Silhouette plot not found")
    return FileResponse(plot_path, media_type="image/png")


@app.get("/api/analysis/{analysis_id}/plots/clusters")
async def get_cluster_plot(analysis_id: str):
    """
    Retrieve cluster visualization scatter plot image.
    """
    plot_path = "outputs/plots/cluster_visualization.png"
    if not os.path.exists(plot_path):
        raise HTTPException(status_code=404, detail="Cluster visualization plot not found")
    return FileResponse(plot_path, media_type="image/png")


@app.get("/api/analysis/{analysis_id}/export/csv")
async def export_clustered_data(analysis_id: str):
    """
    Download the clustered dataset with labels.
    """
    # For simplicity, we'll use the standard output path
    # In a more robust implementation, we'd save this per-analysis
    file_path = "data/processed/customers_clustered.csv"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Clustered data file not found")

    return FileResponse(
        file_path,
        media_type="text/csv",
        filename="customers_clustered.csv"
    )


@app.get("/api/analysis/{analysis_id}/export/summary")
async def export_cluster_summary(analysis_id: str):
    """
    Download cluster summary as CSV.
    """
    file_path = "outputs/reports/cluster_summary.csv"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Cluster summary file not found")

    return FileResponse(
        file_path,
        media_type="text/csv",
        filename="cluster_summary.csv"
    )


@app.get("/api/analysis/{analysis_id}/export/metrics")
async def export_evaluation_metrics(analysis_id: str):
    """
    Download evaluation metrics as JSON.
    """
    file_path = "outputs/reports/metrics.json"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Evaluation metrics file not found")

    return FileResponse(
        file_path,
        media_type="application/json",
        filename="metrics.json"
    )


@app.get("/api/analysis/{analysis_id}/export/model")
async def export_trained_model(analysis_id: str):
    """
    Download the trained model and scaler (as pickle).
    """
    file_path = "outputs/models/kmeans_model.pkl"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Model file not found")

    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename="kmeans_model.pkl"
    )


# Cleanup endpoint for development (remove in production)
@app.delete("/api/cleanup")
async def cleanup_temp_files():
    """
    Clean up temporary files (development only).
    """
    import glob
    temp_files = glob.glob("temp/*")
    for f in temp_files:
        try:
            os.remove(f)
        except:
            pass
    return {"message": "Temporary files cleaned up"}