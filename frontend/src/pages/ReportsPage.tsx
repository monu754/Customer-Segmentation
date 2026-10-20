import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AlertTriangle, Download, Loader2 } from 'lucide-react';
import { exportClusteredData, exportClusterSummary, exportEvaluationMetrics, exportTrainedModel, getAnalysisResults } from '../services/api';
import { ClusteringResult } from '../types/api';

export const ReportsPage = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<ClusteringResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!analysisId) {
      navigate('/overview');
      return;
    }
    getAnalysisResults(analysisId)
      .then(response => setAnalysis(response.data))
      .catch(err => setError(err.response?.data?.detail || err.message || 'Failed to load reports'));
  }, [analysisId, navigate]);

  const download = async (name: string, request: () => Promise<any>) => {
    if (!analysisId) return;
    try {
      const response = await request();
      const url = URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = name;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || `Failed to download ${name}`);
    }
  };

  if (error) return <div className="p-6 text-red-700"><AlertTriangle className="mb-3" />{error}</div>;
  if (!analysis) return <div className="p-6 flex gap-3"><Loader2 className="animate-spin" />Loading reports...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-2">Reports and Exports</h1>
      <p className="text-gray-600 mb-6">Analysis {analysis.analysis_id} selected K: {analysis.selected_k}</p>
      <div className="grid gap-4 md:grid-cols-2">
        <DownloadButton label="Clustered data CSV" onClick={() => download('customers_clustered.csv', () => exportClusteredData(analysisId!))} />
        <DownloadButton label="Cluster summary CSV" onClick={() => download('cluster_summary.csv', () => exportClusterSummary(analysisId!))} />
        <DownloadButton label="Evaluation metrics JSON" onClick={() => download('metrics.json', () => exportEvaluationMetrics(analysisId!))} />
        <DownloadButton label="Trained model" onClick={() => download('kmeans_model.pkl', () => exportTrainedModel(analysisId!))} />
      </div>
    </div>
  );
};

const DownloadButton = ({ label, onClick }: { label: string; onClick: () => void }) => (
  <button onClick={onClick} className="bg-white rounded-lg shadow p-5 flex items-center gap-3 hover:bg-gray-50">
    <Download className="text-indigo-600" />
    <span>{label}</span>
  </button>
);
