import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AlertTriangle, Loader2 } from 'lucide-react';
import { getAnalysisResults, getClusterSummaries } from '../services/api';
import { ClusteringResult } from '../types/api';

export const SegmentInsightsPage = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<ClusteringResult | null>(null);
  const [summary, setSummary] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!analysisId) {
      navigate('/overview');
      return;
    }
    Promise.all([getAnalysisResults(analysisId), getClusterSummaries(analysisId)])
      .then(([result, clusters]) => {
        setAnalysis(result.data);
        setSummary(clusters.data);
      })
      .catch(err => setError(err.response?.data?.detail || err.message || 'Failed to load insights'));
  }, [analysisId, navigate]);

  if (error) return <div className="p-6 text-red-700"><AlertTriangle className="mb-3" />{error}</div>;
  if (!analysis) return <div className="p-6 flex gap-3"><Loader2 className="animate-spin" />Loading insights...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-2">Segment Insights</h1>
      <p className="text-gray-600 mb-6">Interpretation of the {analysis.selected_k} customer segments.</p>
      <div className="grid gap-4 md:grid-cols-2">
        {summary.map(cluster => (
          <article className="bg-white rounded-lg shadow p-5" key={String(cluster.Cluster)}>
            <h2 className="font-semibold text-lg">Cluster {cluster.Cluster}</h2>
            <p className="text-gray-600 mt-2">{cluster.Size} customers</p>
            <dl className="mt-4 space-y-2 text-sm">
              {analysis.features.map(feature => (
                <div className="flex justify-between" key={feature}>
                  <dt>{feature}</dt>
                  <dd className="font-medium">{Number(cluster[`${feature}_mean`]).toFixed(2)}</dd>
                </div>
              ))}
            </dl>
          </article>
        ))}
      </div>
      <button onClick={() => navigate(`/reports/${analysisId}`)} className="mt-6 px-4 py-2 bg-indigo-600 text-white rounded-md">View Reports</button>
    </div>
  );
};
