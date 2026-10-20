"""FastAPI backend exposing the customer segmentation workflow to the frontend."""
from __future__ import annotations

import io
import json
import shutil
import uuid
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from src.clustering import train_kmeans
from src.eda import perform_eda
from src.evaluation import evaluate_clustering, evaluate_k_range, generate_selection_rationale, select_best_k
from src.preprocessing import preprocess_data
from src.reporting import (
    generate_cluster_summary,
    save_cluster_summary,
    save_evaluation_metrics,
    save_model,
    save_processed_data,
)
from src.visualization import plot_clusters, plot_elbow, plot_silhouette


ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = ROOT / "data" / "uploads"
ANALYSIS_DIR = ROOT / "outputs" / "analyses"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Customer Segmentation API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

datasets: dict[str, dict[str, Any]] = {}
analyses: dict[str, dict[str, Any]] = {}


class EDARequest(BaseModel):
    dataset_id: str
    features: list[str] = Field(min_length=1)


class ClusteringRequest(BaseModel):
    dataset_id: str
    features: list[str] = Field(min_length=2)
    k_min: int = Field(default=2, ge=1)
    k_max: int = Field(default=10, ge=1)
    random_state: int = 42
    n_init: int = Field(default=10, ge=1)


def _dataset(dataset_id: str) -> dict[str, Any]:
    dataset = datasets.get(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


def _analysis(analysis_id: str) -> dict[str, Any]:
    analysis = analyses.get(analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if hasattr(value, "item"):
        return _json_safe(value.item())
    if pd.isna(value):
        return None
    return value


def _dataset_info(dataset_id: str, dataset: dict[str, Any]) -> dict[str, Any]:
    frame = dataset["frame"]
    return {
        "dataset_id": dataset_id,
        "filename": dataset["filename"],
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "column_names": frame.columns.tolist(),
        "numeric_columns": frame.select_dtypes(include="number").columns.tolist(),
        "missing_values": {key: int(value) for key, value in frame.isna().sum().items()},
        "duplicate_rows": int(frame.duplicated().sum()),
    }


def _validate_features(frame: pd.DataFrame, features: list[str]) -> None:
    missing = [feature for feature in features if feature not in frame.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Unknown feature(s): {', '.join(missing)}")
    non_numeric = [feature for feature in features if not pd.api.types.is_numeric_dtype(frame[feature])]
    if non_numeric:
        raise HTTPException(status_code=400, detail=f"Features must be numeric: {', '.join(non_numeric)}")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "customer-segmentation-api"}


@app.post("/api/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)) -> dict[str, Any]:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".csv", ".xlsx", ".xls"}:
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")

    dataset_id = uuid.uuid4().hex
    target = UPLOAD_DIR / f"{dataset_id}{suffix}"
    with target.open("wb") as output:
        shutil.copyfileobj(file.file, output)

    try:
        frame = pd.read_csv(target) if suffix == ".csv" else pd.read_excel(target)
    except Exception as exc:
        target.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Could not read dataset: {exc}") from exc

    if frame.empty:
        target.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Dataset must contain at least one row")
    datasets[dataset_id] = {"frame": frame, "filename": file.filename or target.name, "path": target}
    return _dataset_info(dataset_id, datasets[dataset_id])


@app.get("/api/datasets/{dataset_id}/preview")
def dataset_preview(dataset_id: str, rows: int = 10) -> dict[str, Any]:
    dataset = _dataset(dataset_id)
    frame = dataset["frame"]
    rows = max(1, min(rows, 100))
    return {
        **_dataset_info(dataset_id, dataset),
        "total_rows": len(frame),
        "total_columns": len(frame.columns),
        "columns": frame.columns.tolist(),
        "data_types": {key: str(value) for key, value in frame.dtypes.items()},
        "preview_rows": _json_safe(frame.head(rows).where(frame.head(rows).notna(), None).to_dict("records")),
    }


@app.get("/api/datasets/{dataset_id}/summary")
def dataset_summary(dataset_id: str) -> dict[str, Any]:
    dataset = _dataset(dataset_id)
    frame = dataset["frame"]
    numeric = frame.select_dtypes(include="number")
    column_info = []
    for name in frame.columns:
        series = frame[name]
        item: dict[str, Any] = {
            "name": name,
            "type": str(series.dtype),
            "missing_count": int(series.isna().sum()),
            "missing_percentage": float(series.isna().mean() * 100),
            "unique_count": int(series.nunique(dropna=True)),
        }
        if pd.api.types.is_numeric_dtype(series):
            stats = series.describe()
            item.update({key: float(stats[key]) for key in ("mean", "50%", "std", "min", "max") if key in stats})
            item["median"] = item.pop("50%")
        column_info.append(item)
    return {
        "dataset_id": dataset_id,
        "filename": dataset["filename"],
        "total_rows": len(frame),
        "total_columns": len(frame.columns),
        "column_info": column_info,
        "summary_statistics": _json_safe(numeric.describe().to_dict()),
        "data_quality": {
            "total_missing_values": int(frame.isna().sum().sum()),
            "columns_with_missing": frame.columns[frame.isna().any()].tolist(),
            "duplicate_rows": int(frame.duplicated().sum()),
            "memory_usage": int(frame.memory_usage(deep=True).sum()),
        },
    }


@app.delete("/api/datasets/{dataset_id}")
def delete_dataset(dataset_id: str) -> dict[str, str]:
    dataset = _dataset(dataset_id)
    dataset["path"].unlink(missing_ok=True)
    datasets.pop(dataset_id, None)
    return {"status": "deleted"}


@app.post("/api/analysis/eda")
def run_eda(request: EDARequest) -> dict[str, Any]:
    dataset = _dataset(request.dataset_id)
    _validate_features(dataset["frame"], request.features)
    analysis_id = uuid.uuid4().hex
    plot_dir = ANALYSIS_DIR / analysis_id / "plots"
    summary = perform_eda(dataset["frame"], request.features, str(plot_dir))
    plots = sorted(
        path.name
        for path in plot_dir.glob("*.png")
        if path.is_file()
    )
    result = {
        "analysis_id": analysis_id,
        "dataset_id": request.dataset_id,
        "type": "eda",
        "features": request.features,
        "eda_summary": _json_safe(summary.to_dict()),
        "plots": plots,
        "timestamp": pd.Timestamp.now("UTC").isoformat(),
        "status": "completed",
        "plot_dir": plot_dir,
    }
    analyses[analysis_id] = result
    return {key: value for key, value in result.items() if key != "plot_dir"}


@app.post("/api/clustering/run")
def run_clustering(request: ClusteringRequest) -> dict[str, Any]:
    dataset = _dataset(request.dataset_id)
    if request.k_max < request.k_min:
        raise HTTPException(status_code=400, detail="k_max must be greater than or equal to k_min")
    _validate_features(dataset["frame"], request.features)
    try:
        cleaned, scaled, scaler, feature_names = preprocess_data(dataset["frame"], request.features)
        results = evaluate_k_range(scaled, request.k_min, request.k_max, request.random_state)
        selected_k = select_best_k(results["k_values"], results["silhouette_scores"])
        model, labels, centroids = train_kmeans(
            scaled, selected_k, request.random_state, request.n_init
        )
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    analysis_id = uuid.uuid4().hex
    analysis_root = ANALYSIS_DIR / analysis_id
    plot_dir = analysis_root / "plots"
    report_dir = analysis_root / "reports"
    model_path = analysis_root / "kmeans_model.pkl"
    processed_path = analysis_root / "customers_clustered.csv"
    summary_path = report_dir / "cluster_summary.csv"
    metrics_path = report_dir / "metrics.json"
    plot_elbow(results["k_values"], results["inertias"], str(plot_dir))
    plot_silhouette(results["k_values"], results["silhouette_scores"], str(plot_dir))
    plot_clusters(scaled, labels, centroids, feature_names, str(plot_dir))
    metrics = evaluate_clustering(scaled, labels, model)
    summary = generate_cluster_summary(cleaned, labels, feature_names)
    rationale = generate_selection_rationale(
        results["k_values"], results["inertias"], results["silhouette_scores"], selected_k
    )
    save_processed_data(cleaned, labels, str(processed_path))
    save_model(model, scaler, str(model_path))
    save_cluster_summary(summary, str(summary_path))
    save_evaluation_metrics(metrics, str(metrics_path))
    result = {
        "analysis_id": analysis_id,
        "dataset_id": request.dataset_id,
        "type": "clustering",
        "features": feature_names,
        "k_range_evaluated": results["k_values"],
        "selected_k": selected_k,
        "status": "completed",
        "results": {
            "metrics": _json_safe(metrics),
            "evaluation_results": _json_safe({
                **results,
                "selected_k": selected_k,
                "selection_rationale": rationale,
            }),
            "cluster_summary": _json_safe(summary.to_dict("records")),
        },
        "plot_dir": plot_dir,
        "processed_path": processed_path,
        "summary_path": summary_path,
        "metrics_path": metrics_path,
        "model_path": model_path,
    }
    analyses[analysis_id] = result
    return {key: value for key, value in result.items() if key.endswith("id") or key in {"type", "features", "k_range_evaluated", "selected_k", "status", "results"}}


@app.get("/api/analysis/{analysis_id}/status")
def analysis_status(analysis_id: str) -> dict[str, Any]:
    analysis = _analysis(analysis_id)
    return {"analysis_id": analysis_id, "status": analysis["status"], "type": analysis["type"], "timestamp": pd.Timestamp.now("UTC").isoformat()}


@app.get("/api/analysis/{analysis_id}/results")
def analysis_results(analysis_id: str) -> dict[str, Any]:
    analysis = _analysis(analysis_id)
    return {key: value for key, value in analysis.items() if not isinstance(value, Path)}


@app.get("/api/analysis/{analysis_id}/clusters")
def cluster_summaries(analysis_id: str) -> list[dict[str, Any]]:
    analysis = _analysis(analysis_id)
    if analysis["type"] != "clustering":
        raise HTTPException(status_code=400, detail="Analysis is not a clustering analysis")
    return analysis["results"]["cluster_summary"]


@app.get("/api/analysis/{analysis_id}/evaluations")
def evaluation_results(analysis_id: str) -> dict[str, Any]:
    analysis = _analysis(analysis_id)
    if analysis["type"] != "clustering":
        raise HTTPException(status_code=400, detail="Analysis is not a clustering analysis")
    return analysis["results"]["evaluation_results"]


def _plot_response(analysis_id: str, filename: str) -> FileResponse:
    analysis = _analysis(analysis_id)
    plot_path = analysis["plot_dir"] / filename
    if not plot_path.exists():
        raise HTTPException(status_code=404, detail="Plot not found")
    return FileResponse(plot_path, media_type="image/png")


@app.get("/api/analysis/{analysis_id}/eda/plots/{plot_name}")
def eda_plot(analysis_id: str, plot_name: str) -> FileResponse:
    safe_name = Path(plot_name).name
    return _plot_response(analysis_id, safe_name if safe_name.endswith(".png") else f"{safe_name}.png")


@app.get("/api/analysis/{analysis_id}/plots/{plot_name}")
def clustering_plot(analysis_id: str, plot_name: str) -> FileResponse:
    names = {"elbow": "elbow_plot.png", "silhouette": "silhouette_plot.png", "clusters": "cluster_visualization.png"}
    if plot_name not in names:
        raise HTTPException(status_code=404, detail="Unknown plot")
    return _plot_response(analysis_id, names[plot_name])


def _file_export(analysis_id: str, key: str, media_type: str) -> FileResponse:
    analysis = _analysis(analysis_id)
    path = analysis.get(key)
    if not isinstance(path, Path) or not path.exists():
        raise HTTPException(status_code=404, detail="Export not found")
    return FileResponse(path, media_type=media_type, filename=path.name)


@app.get("/api/analysis/{analysis_id}/export/csv")
def export_csv(analysis_id: str) -> FileResponse:
    return _file_export(analysis_id, "processed_path", "text/csv")


@app.get("/api/analysis/{analysis_id}/export/summary")
def export_summary(analysis_id: str) -> FileResponse:
    return _file_export(analysis_id, "summary_path", "text/csv")


@app.get("/api/analysis/{analysis_id}/export/metrics")
def export_metrics(analysis_id: str) -> FileResponse:
    return _file_export(analysis_id, "metrics_path", "application/json")


@app.get("/api/analysis/{analysis_id}/export/model")
def export_model(analysis_id: str) -> FileResponse:
    return _file_export(analysis_id, "model_path", "application/octet-stream")
