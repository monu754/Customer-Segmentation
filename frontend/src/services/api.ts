import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for debugging
api.interceptors.request.use((config) => {
  console.log(`Making request to: ${config.url}`);
  return config;
});

// Add response interceptor for debugging
api.interceptors.response.use(
  (response) => {
    console.log(`Received response from: ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`API Error:`, error);
    return Promise.reject(error);
  }
);

// Health check
export const checkHealth = () => api.get('/api/health');

// Dataset management
export const uploadDataset = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/datasets/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const getDatasetPreview = (datasetId: string, rows = 10) =>
  api.get(`/api/datasets/${datasetId}/preview?rows=${rows}`);

export const getDatasetSummary = (datasetId: string) =>
  api.get(`/api/datasets/${datasetId}/summary`);

export const deleteDataset = (datasetId: string) =>
  api.delete(`/api/datasets/${datasetId}`);

// EDA
export const runEDA = (datasetId: string, features: string[]) =>
  api.post('/api/analysis/eda', { dataset_id: datasetId, features });

export const getEDAPlot = (analysisId: string, plotName: string) =>
  api.get(`/api/analysis/${analysisId}/eda/plots/${plotName}`, {
    responseType: 'blob',
  });

// Clustering
export const runClustering = (
  datasetId: string,
  features: string[],
  kMin: number = 2,
  kMax: number = 10,
  randomState: number = 42,
  nInit: number = 10
) =>
  api.post('/api/clustering/run', {
    dataset_id: datasetId,
    features,
    k_min: kMin,
    k_max: kMax,
    random_state: randomState,
    n_init: nInit,
  });

export const getAnalysisStatus = (analysisId: string) =>
  api.get(`/api/analysis/${analysisId}/status`);

export const getAnalysisResults = (analysisId: string) =>
  api.get(`/api/analysis/${analysisId}/results`);

export const getClusterSummaries = (analysisId: string) =>
  api.get(`/api/analysis/${analysisId}/clusters`);

export const getEvaluationResults = (analysisId: string) =>
  api.get(`/api/analysis/${analysisId}/evaluations`);

// Plots
export const getElbowPlot = (analysisId: string) =>
  api.get(`/api/analysis/${analysisId}/plots/elbow`, {
    responseType: 'blob',
  });

export const getSilhouettePlot = (analysisId: string) =>
  api.get(`/api/analysis/${analysisId}/plots/silhouette`, {
    responseType: 'blob',
  });

export const getClusterPlot = (analysisId: string) =>
  api.get(`/api/analysis/${analysisId}/plots/clusters`, {
    responseType: 'blob',
  });

// Exports
export const exportClusteredData = (analysisId: string) =>
  api.get(`/api/analysis/${analysisId}/export/csv`, {
    responseType: 'blob',
  });

export const exportClusterSummary = (analysisId: string) =>
  api.get(`/api/analysis/${analysisId}/export/summary`, {
    responseType: 'blob',
  });

export const exportEvaluationMetrics = (analysisId: string) =>
  api.get(`/api/analysis/${analysisId}/export/metrics`, {
    responseType: 'blob',
  });

export const exportTrainedModel = (analysisId: string) =>
  api.get(`/api/analysis/${analysisId}/export/model`, {
    responseType: 'blob',
  });