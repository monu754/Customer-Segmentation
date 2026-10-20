import React, { useState, useCallback } from 'react';
import { getAnalysisResults, getAnalysisStatus, getClusterPlot, getClusterSummaries, getDatasetPreview, getElbowPlot, getEvaluationResults, getSilhouettePlot, runClustering } from '../services/api';
import { ClusteringResult } from '../types/api';
import { ScatterChart, Activity, Loader2, CheckCircle, AlertTriangle, RefreshCw, PieChart, BarChart2 } from 'lucide-react';
import { useAppState } from '../context/AppStateContext';

export const ClusteringPage = () => {
  const { datasetId, setAnalysis } = useAppState();
  const [features, setFeatures] = useState<string[]>([]);
  const [availableFeatures, setAvailableFeatures] = useState<string[]>([]);
  const [kMin, setKMin] = useState<number>(2);
  const [kMax, setKMax] = useState<number>(10);
  const [randomState, setRandomState] = useState<number>(42);
  const [nInit, setNInit] = useState<number>(10);

  const [clusteringAnalysis, setClusteringAnalysis] = useState<ClusteringResult | null>(null);
  const [analysisStatus, setAnalysisStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [selectedPlot, setSelectedPlot] = useState<'elbow' | 'silhouette' | 'clusters' | null>(null);
  const [plotBlob, setPlotBlob] = useState<Blob | null>(null);

  React.useEffect(() => {
    if (datasetId) {
      getDatasetPreview(datasetId, 1)
        .then(response => setAvailableFeatures(response.data.numeric_columns))
        .catch(err => setError(err.response?.data?.detail || err.message || 'Failed to load dataset features'));
    }
  }, [datasetId]);

  const handleRunClustering = useCallback(async () => {
    if (!datasetId) {
      setError('Please select a dataset first');
      return;
    }

    if (features.length < 2) {
      setError('Please select at least two numeric features for clustering');
      return;
    }

    if (kMin < 1) {
      setError('Minimum K must be at least 1');
      return;
    }

    if (kMax < kMin) {
      setError('Maximum K must be greater than or equal to minimum K');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    setAnalysisStatus('running');

    try {
      const response = await runClustering(datasetId, features, kMin, kMax, randomState, nInit);
      const data = response.data;

      setClusteringAnalysis(data);
      setAnalysis(data.analysis_id, 'completed');
      setSuccess('Clustering completed successfully!');
      setAnalysisStatus('completed');

      // Auto-select elbow plot
      setSelectedPlot('elbow');
      await loadPlot(data.analysis_id, 'elbow');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to run clustering');
      setAnalysisStatus('failed');
    } finally {
      setLoading(false);
    }
  }, [datasetId, features, kMin, kMax, randomState, nInit]);

  const loadPlot = useCallback(async (analysisId: string, plotType: 'elbow' | 'silhouette' | 'clusters') => {
    try {
      let response: { data: Blob } | undefined;
      if (plotType === 'elbow') {
        response = await getElbowPlot(analysisId);
      } else if (plotType === 'silhouette') {
        response = await getSilhouettePlot(analysisId);
      } else if (plotType === 'clusters') {
        response = await getClusterPlot(analysisId);
      }

      if (!response) {
        throw new Error(`Unsupported plot type: ${plotType}`);
      }
      setPlotBlob(response.data);
      setSelectedPlot(plotType);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || `Failed to load ${plotType} plot`);
    }
  }, []);

  // Poll for analysis status if needed
  React.useEffect(() => {
    if (clusteringAnalysis?.analysis_id && analysisStatus === 'running') {
      const checkStatus = async () => {
        try {
          const response = await getAnalysisStatus(clusteringAnalysis.analysis_id);
          setAnalysisStatus(response.data.status);

          if (response.data.status === 'completed') {
            const resultsResponse = await getAnalysisResults(clusteringAnalysis.analysis_id);
            setClusteringAnalysis(resultsResponse.data);
            setSuccess('Clustering completed successfully!');
          }
        } catch (err) {
          // Ignore polling errors
        }
      };

      const interval = setInterval(checkStatus, 3000);
      return () => clearInterval(interval);
    }
  }, [clusteringAnalysis?.analysis_id, analysisStatus]);

  if (loading && !clusteringAnalysis) {
    return (
      <div className="p-6">
        <div className="flex flex-col items-center justify-center min-h-[200px]">
          <Loader2 className="h-8 w-8 animate-spin mb-4" />
          <p className="text-gray-600">Running clustering analysis...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Clustering Configuration & Execution</h1>
        <p className="text-gray-600">
          Configure and run K-Means clustering on your dataset to discover customer segments.
        </p>
      </div>

      {/* Status Alerts */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border-l-4 border-red-400 text-red-700">
          <AlertTriangle className="h-4 w-4 mr-2" />
          <span>{error}</span>
        </div>
      )}
      {success && (
        <div className="mb-4 p-4 bg-green-50 border-l-4 border-green-400 text-green-700">
          <CheckCircle className="h-4 w-4 mr-2" />
          <span>{success}</span>
        </div>
      )}

      {/* Dataset Selection */}
      {!datasetId && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <Activity className="h-5 w-5 text-blue-600" />
            <div>
              <h3 className="font-semibold text-gray-900">No Dataset Selected</h3>
              <p className="text-sm text-gray-600">
                Please upload a dataset first in the Dataset Management page to perform clustering.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Clustering Controls */}
      {datasetId && (
        <>
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Clustering Configuration</h2>
            <div className="space-y-6">

              {/* Feature Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Features for Clustering
                </label>
                <div className="flex flex-wrap gap-2">
                  {availableFeatures.map((feature) => (
                    <label key={feature} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={features.includes(feature)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFeatures([...features, feature]);
                          } else {
                            setFeatures(features.filter(f => f !== feature));
                          }
                        }}
                        className="h-4 w-4 text-indigo-600"
                      />
                      <span className="text-sm text-gray-700">{feature}</span>
                    </label>
                  ))}
                </div>
                {features.length > 0 && (
                  <p className="mt-2 text-sm text-gray-500">
                    Selected: {features.join(', ')}
                  </p>
                )}
                {features.length === 0 && (
                  <p className="mt-2 text-sm text-gray-500">
                    No features selected
                  </p>
                )}
              </div>

              {/* K Range Selection */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Number of Clusters (K)
                  </label>
                  <div className="flex items-center">
                    <input
                      type="number"
                      value={kMin}
                      onChange={(e) => setKMin(Math.max(1, parseInt(e.target.value) || 1))}
                      min="1"
                      max="20"
                      className="w-20 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <span className="ml-3 text-sm text-gray-500">
                      (typically 2-10)
                    </span>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Maximum Number of Clusters (K)
                  </label>
                  <div className="flex items-center">
                    <input
                      type="number"
                      value={kMax}
                      onChange={(e) => setKMax(Math.max(parseInt(e.target.value) || 2, kMin))}
                      min="2"
                      max="20"
                      className="w-20 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <span className="ml-3 text-sm text-gray-500">
                      (should be &gt;= min K)
                    </span>
                  </div>
                </div>
              </div>

              {/* Advanced Settings */}
              <div className="border-t pt-4">
                <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                  <input
                    type="checkbox"
                    checked={true}
                    readOnly
                    className="h-4 w-4 text-indigo-600 mr-2"
                  />
                  Use advanced settings
                </label>

                <div className="mt-3 space-y-2">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Random State (Seed)
                      </label>
                      <input
                        type="number"
                        value={randomState}
                        onChange={(e) => setRandomState(parseInt(e.target.value) || 42)}
                        className="w-24 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Number of Initializations
                      </label>
                      <input
                        type="number"
                        value={nInit}
                        onChange={(e) => setNInit(Math.max(1, parseInt(e.target.value) || 1))}
                        min="1"
                        max="20"
                        className="w-24 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6">
              <button
                onClick={handleRunClustering}
                disabled={loading || !datasetId || features.length < 2}
                className={`px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:bg-indigo-300 disabled:cursor-not-allowed transition-colors`}
              >
                {loading ? 'Running Analysis...' : 'Run K-Means Clustering'}
              </button>
            </div>
          </div>

          {/* Clustering Results */}
          {clusteringAnalysis && (
            <div className="mt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Clustering Results</h2>

              {/* Status Indicator */}
              <div className="mb-4 flex items-center space-x-3">
                {analysisStatus === 'running' && (
                  <>
                    <Activity className="h-4 w-4 animate-spin" />
                    <span className="text-indigo-600 font-medium">Analysis running...</span>
                  </>
                )}
                {analysisStatus === 'completed' && (
                  <>
                    <PieChart className="h-4 w-4 text-green-500" />
                    <span className="text-green-600 font-medium">Analysis completed successfully</span>
                  </>
                )}
                {analysisStatus === 'failed' && (
                  <>
                    <AlertTriangle className="h-4 w-4 text-red-500" />
                    <span className="text-red-600 font-medium">Analysis failed</span>
                  </>
                )}
              </div>

              {/* Key Metrics */}
              {clusteringAnalysis.results && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-3">Key Metrics</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-white p-4 rounded-lg shadow">
                      <h4 className="text-sm font-medium text-gray-500 mb-2">Inertia</h4>
                      <p className="text-2xl font-bold text-indigo-600">
                        {clusteringAnalysis.results.metrics.inertia.toFixed(2)}
                      </p>
                      <p className="text-sm text-gray-500">
                        Lower is better (measures cluster compactness)
                      </p>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow">
                      <h4 className="text-sm font-medium text-gray-500 mb-2">Silhouette Score</h4>
                      <p className="text-2xl font-bold text-indigo-600">
                        {clusteringAnalysis.results.metrics.silhouette_score?.toFixed(3) ?? 'N/A'}
                      </p>
                      <p className="text-sm text-gray-500">
                        Higher is better (measures cluster separation)
                      </p>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow">
                      <h4 className="text-sm font-medium text-gray-500 mb-2">Selected K</h4>
                      <p className="text-2xl font-bold text-indigo-600">
                        {clusteringAnalysis.selected_k}
                      </p>
                      <p className="text-sm text-gray-500">
                        Number of clusters
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Visualization Controls */}
              {clusteringAnalysis.analysis_id && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-3">Visualizations</h3>
                  <div className="flex items-center space-x-3 mb-4">
                    <label className="text-sm font-medium text-gray-700">
                      Select Plot:
                    </label>
                    <select
                      value={selectedPlot || ''}
                      onChange={(e) => {
                        const plotType = e.target.value as 'elbow' | 'silhouette' | 'clusters';
                        if (plotType) {
                          loadPlot(clusteringAnalysis.analysis_id, plotType);
                        }
                      }}
                      className="border px-3 py-1 rounded"
                    >
                      <option value="elbow">Elbow Plot</option>
                      <option value="silhouette">Silhouette Plot</option>
                      <option value="clusters">Cluster Visualization</option>
                    </select>
                    <button
                      onClick={() => {
                        if (selectedPlot) {
                          loadPlot(clusteringAnalysis.analysis_id, selectedPlot);
                        }
                      }}
                      className="px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                    >
                      <RefreshCw className="h-4 w-4" />
                    </button>
                  </div>

                  {/* Plot Display */}
                  {plotBlob && (
                    <div className="bg-white p-4 rounded-lg shadow">
                      <img
                        src={URL.createObjectURL(plotBlob)}
                        alt={selectedPlot || 'Clustering Plot'}
                        className="w-full h-auto rounded"
                        style={{ maxHeight: '500px' }}
                      />
                    </div>
                  )}
                  {!plotBlob && selectedPlot && (
                    <div className="bg-white p-4 rounded-lg shadow min-h-[200px] flex items-center justify-center">
                      <Loader2 className="h-6 w-6 animate-spin" />
                      <p className="ml-2 text-gray-600">Loading plot...</p>
                    </div>
                  )}
                </div>
              )}

              {/* Evaluation Results */}
              {clusteringAnalysis.results && clusteringAnalysis.results.evaluation_results && (
                <div className="mt-8">
                  <h3 className="font-semibold text-gray-900 mb-3">Evaluation Results</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full bg-white border">
                      <thead>
                        <tr className="bg-gray-50">
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            K
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Inertia
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Silhouette Score
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Status
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {clusteringAnalysis.results.evaluation_results.k_values.map((k, index) => {
                          const inertia = clusteringAnalysis.results.evaluation_results.inertias[index];
                          const silhouetteScore = clusteringAnalysis.results.evaluation_results.silhouette_scores[index];
                          const isSelected = k === clusteringAnalysis.selected_k;

                          return (
                            <tr
                              key={index}
                              className={`${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'} ${isSelected ? 'bg-indigo-50' : ''}`}
                            >
                              <td className="px-4 py-2 text-sm font-medium">
                                {k}
                              </td>
                              <td className="px-4 py-2 text-sm">
                                {inertia !== null ? inertia.toFixed(2) : 'N/A'}
                              </td>
                              <td className="px-4 py-2 text-sm">
                                {silhouetteScore !== null ? silhouetteScore.toFixed(3) : 'N/A'}
                              </td>
                              <td className="px-4 py-2 text-sm">
                                {isSelected ? (
                                  <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                                    SELECTED
                                  </span>
                                ) : (
                                  silhouetteScore === null ? (
                                    <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">
                                      INVALID
                                    </span>
                                  ) : (
                                    <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
                                      VALID
                                    </span>
                                  )
                                )}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>

                  {/* Selection Rationale */}
                  <div className="mt-4 p-4 bg-indigo-50 rounded-lg">
                    <h4 className="font-semibold text-indigo-800 mb-2">Selection Rationale</h4>
                    <p className="text-sm text-gray-700">
                      {clusteringAnalysis.results.evaluation_results.selection_rationale}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};