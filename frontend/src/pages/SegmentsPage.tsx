import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AlertTriangle, Loader2 } from 'lucide-react';
import { getAnalysisResults, getClusterPlot, getClusterSummaries } from '../services/api';
import { ClusteringResult } from '../types/api';

export const SegmentsPage = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<ClusteringResult | null>(null);
  const [summary, setSummary] = useState<any[]>([]);
  const [plotUrl, setPlotUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!analysisId) {
      navigate('/overview');
      return;
    }
    Promise.all([getAnalysisResults(analysisId), getClusterSummaries(analysisId), getClusterPlot(analysisId)])
      .then(([result, clusters, plot]) => {
        setAnalysis(result.data);
        setSummary(clusters.data);
        setPlotUrl(URL.createObjectURL(plot.data));
      })
      .catch(err => setError(err.response?.data?.detail || err.message || 'Failed to load segments'));
    return () => {
      if (plotUrl) URL.revokeObjectURL(plotUrl);
    };
  }, [analysisId, navigate]);

  if (error) return <div className="p-6 text-red-700"><AlertTriangle className="mb-3" />{error}</div>;
  if (!analysis) return <div className="p-6 flex gap-3"><Loader2 className="animate-spin" />Loading segments...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-2">Customer Segments</h1>
      <p className="text-gray-600 mb-6">{analysis.selected_k} clusters identified from {analysis.features.join(', ')}.</p>
      {plotUrl && <img src={plotUrl} alt="Cluster visualization" className="max-w-3xl bg-white rounded-lg shadow mb-8" />}
      <div className="overflow-x-auto bg-white rounded-lg shadow">
        <table className="min-w-full text-sm">
          <thead><tr className="border-b text-left"><th className="p-3">Cluster</th><th className="p-3">Size</th>{analysis.features.map(feature => <th className="p-3" key={feature}>{feature} mean</th>)}</tr></thead>
          <tbody>{summary.map(cluster => <tr className="border-b" key={String(cluster.Cluster)}><td className="p-3">{cluster.Cluster}</td><td className="p-3">{cluster.Size}</td>{analysis.features.map(feature => <td className="p-3" key={feature}>{Number(cluster[`${feature}_mean`]).toFixed(2)}</td>)}</tr>)}</tbody>
        </table>
      </div>
      <button onClick={() => navigate(`/segments/${analysisId}/insights`)} className="mt-6 px-4 py-2 bg-indigo-600 text-white rounded-md">View Insights</button>
    </div>
  );
};
