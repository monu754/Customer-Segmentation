"""End-to-end regression tests for the FastAPI workflow."""
from io import BytesIO

import pandas as pd
from fastapi.testclient import TestClient

from backend.main import app


def test_api_upload_analyze_and_export(tmp_path, monkeypatch):
    """Upload a dataset, run EDA and clustering, then verify persisted outputs."""
    monkeypatch.setattr("backend.main.UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr("backend.main.ANALYSIS_DIR", tmp_path / "analyses")
    (tmp_path / "uploads").mkdir()
    backend_module = __import__("backend.main", fromlist=["datasets", "analyses"])
    backend_module.datasets.clear()
    backend_module.analyses.clear()

    frame = pd.DataFrame(
        {
            "Annual Income (k$)": [15, 16, 78, 79, 80, 81],
            "Spending Score (1-100)": [39, 41, 80, 82, 79, 81],
        }
    )
    csv = frame.to_csv(index=False).encode()

    with TestClient(app) as client:
        upload = client.post(
            "/api/datasets/upload",
            files={"file": ("customers.csv", BytesIO(csv), "text/csv")},
        )
        assert upload.status_code == 200
        dataset_id = upload.json()["dataset_id"]

        eda = client.post(
            "/api/analysis/eda",
            json={"dataset_id": dataset_id, "features": list(frame.columns)},
        )
        assert eda.status_code == 200
        assert eda.json()["status"] == "completed"

        clustering = client.post(
            "/api/clustering/run",
            json={
                "dataset_id": dataset_id,
                "features": list(frame.columns),
                "k_min": 1,
                "k_max": 3,
                "random_state": 42,
                "n_init": 10,
            },
        )
        assert clustering.status_code == 200
        result = clustering.json()
        assert result["status"] == "completed"
        assert result["selected_k"] == 2
        assert result["results"]["metrics"]["silhouette_score"] is not None

        analysis_id = result["analysis_id"]
        assert client.get(f"/api/analysis/{analysis_id}/status").json()["status"] == "completed"
        assert client.get(f"/api/analysis/{analysis_id}/clusters").status_code == 200
        assert client.get(f"/api/analysis/{analysis_id}/evaluations").status_code == 200
        for endpoint in ("csv", "summary", "metrics", "model"):
            response = client.get(f"/api/analysis/{analysis_id}/export/{endpoint}")
            assert response.status_code == 200
            assert response.content
