import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AlertTriangle, BarChart2, Loader2 } from 'lucide-react';
import { getAnalysisResults, getElbowPlot, getSilhouettePlot } from '../services/api';
import { ClusteringResult } from '../types/api';

export const EvaluationPage = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<ClusteringResult | null>(null);
  const [plotUrl, setPlotUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!analysisId) {
      navigate('/overview');
      return;
    }
    getAnalysisResults(analysisId)
      .then(response => setAnalysis(response.data))
      .catch(err => setError(err.response?.data?.detail || err.message || 'Failed to load analysis'));
    getElbowPlot(analysisId)
      .then(response => setPlotUrl(URL.createObjectURL(response.data)))
      .catch(() => undefined);
    return () => {
      if (plotUrl) URL.revokeObjectURL(plotUrl);
    };
  }, [analysisId, navigate]);

  if (error) {
    return <div className="p-6 text-red-700"><AlertTriangle className="mb-3" />{error}</div>;
  }
  if (!analysis) {
    return <div className="p-6 flex gap-3"><Loader2 className="animate-spin" />Loading evaluation...</div>;
  }

  const metrics = analysis.results.metrics;
  const evaluation = analysis.results.evaluation_results;
  return (
    <div className="p-6">
      <div className="flex items-center gap-3 mb-6">
        <BarChart2 className="text-indigo-600" />
        <div>
          <h1 className="text-2xl font-bold">Cluster Evaluation</h1>
          <p className="text-gray-600">Evaluation for K values {evaluation.k_values.join(', ')}.</p>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Metric title="Selected K" value={String(analysis.selected_k)} />
        <Metric title="Inertia" value={metrics.inertia.toFixed(2)} />
        <Metric title="Silhouette score" value={metrics.silhouette_score?.toFixed(3) ?? 'N/A'} />
      </div>
      {plotUrl && <img src={plotUrl} alt="Elbow plot" className="bg-white rounded-lg shadow max-w-3xl" />}
      <p className="mt-6 whitespace-pre-line text-gray-700">{evaluation.selection_rationale}</p>
      <button onClick={() => navigate(`/segments/${analysisId}`)} className="mt-6 px-4 py-2 bg-indigo-600 text-white rounded-md">
        View Segments
      </button>
    </div>
  );
};

const Metric = ({ title, value }: { title: string; value: string }) => (
  <div className="bg-white p-5 rounded-lg shadow">
    <p className="text-sm text-gray-500">{title}</p>
    <p className="text-2xl font-bold text-indigo-600 mt-2">{value}</p>
  </div>
);
