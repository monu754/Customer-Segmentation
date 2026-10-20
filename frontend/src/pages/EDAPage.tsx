import React, { useState, useCallback } from 'react';
import { getDatasetPreview, getEDAPlot, runEDA } from '../services/api';
import { EDAAnalysis } from '../types/api';
import { BarChart2, Activity, Loader2, CheckCircle, AlertTriangle, RefreshCw } from 'lucide-react';
import { useAppState } from '../context/AppStateContext';

export const EDAPage = () => {
  const { datasetId } = useAppState();
  const [features, setFeatures] = useState<string[]>([]);
  const [availableFeatures, setAvailableFeatures] = useState<string[]>([]);
  const [edaAnalysis, setEDAAnalysis] = useState<EDAAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [selectedPlot, setSelectedPlot] = useState<string | null>(null);
  const [plotBlob, setPlotBlob] = useState<Blob | null>(null);

  React.useEffect(() => {
    if (datasetId) {
      getDatasetPreview(datasetId, 1)
        .then(response => setAvailableFeatures(response.data.numeric_columns))
        .catch(err => setError(err.response?.data?.detail || err.message || 'Failed to load dataset features'));
    }
  }, [datasetId]);

  const handleRunEDA = useCallback(async () => {
    if (!datasetId) {
      setError('Please select a dataset first');
      return;
    }

    if (features.length === 0) {
      setError('Please select at least one feature for EDA');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await runEDA(datasetId, features);
      const data = response.data;

      setEDAAnalysis(data);
      setSuccess('EDA completed successfully!');

      // Auto-select first plot if available
      if (data.plots.length > 0) {
        setSelectedPlot(data.plots[0]);
        await loadPlot(data.analysis_id, data.plots[0]);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to run EDA');
    } finally {
      setLoading(false);
    }
  }, [datasetId, features]);

  const loadPlot = useCallback(async (analysisId: string, plotName: string) => {
    try {
      const response = await getEDAPlot(analysisId, plotName);
      setPlotBlob(response.data);
      setSelectedPlot(plotName);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load plot');
    }
  }, []);

  if (loading && !edaAnalysis) {
    return (
      <div className="p-6">
        <div className="flex flex-col items-center justify-center min-h-[200px]">
          <Loader2 className="h-8 w-8 animate-spin mb-4" />
          <p className="text-gray-600">Running EDA...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Exploratory Data Analysis</h1>
        <p className="text-gray-600">
          Explore and visualize your dataset to understand patterns and distributions before clustering.
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
                Please upload a dataset first in the Dataset Management page to perform EDA.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* EDA Controls */}
      {datasetId && (
        <>
          <div className="mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Analysis Configuration</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Features for Analysis
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
              </div>

              <div className="flex items-center justify-between">
                <button
                  onClick={handleRunEDA}
                  disabled={loading || !datasetId || features.length === 0}
                  className={`px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:bg-indigo-300 disabled:cursor-not-allowed transition-colors`}
                >
                  {loading ? 'Running Analysis...' : 'Run EDA'}
                </button>
              </div>
            </div>
          </div>

          {/* EDA Results */}
          {edaAnalysis && (
            <div className="mt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4">EDA Results</h2>

              {/* Summary Statistics */}
              {edaAnalysis.eda_summary && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-3">Summary Statistics</h3>
                  <div className="bg-white p-4 rounded-lg shadow">
                    {typeof edaAnalysis.eda_summary === 'object' && edaAnalysis.eda_summary !== null ? (
                      <div className="space-y-2">
                        {Object.entries(edaAnalysis.eda_summary).map(([key, value]) => (
                          <div key={key} className="flex justify-between text-sm">
                            <span className="font-medium">{key.replace(/_/g, ' ')}:</span>
                            <span className="text-gray-600">
                              {typeof value === 'number' ? value.toFixed(2) : String(value)}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-600">Summary statistics available</p>
                    )}
                  </div>
                </div>
              )}

              {/* Visualization Controls */}
              {edaAnalysis.plots.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-3">Visualizations</h3>
                  <div className="flex items-center space-x-3 mb-4">
                    <label className="text-sm font-medium text-gray-700">
                      Select Plot:
                    </label>
                    <select
                      value={selectedPlot || ''}
                      onChange={(e) => {
                        const plotName = e.target.value;
                        if (plotName) {
                          loadPlot(edaAnalysis.analysis_id, plotName);
                        }
                      }}
                      className="border px-3 py-1 rounded"
                    >
                      {edaAnalysis.plots.map((plot) => (
                        <option key={plot} value={plot}>
                          {plot.replace(/\.png$/, '').replace(/_/g, ' ')}
                        </option>
                      ))}
                    </select>
                    <button
                      onClick={() => {
                        if (selectedPlot) {
                          loadPlot(edaAnalysis.analysis_id, selectedPlot);
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
                        alt="EDA Plot"
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
            </div>
          )}
        </>
      )}
    </div>
  );
};