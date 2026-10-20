import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { getAnalysisStatus, getDatasetPreview } from '../services/api';
import { AnalysisStatus, DatasetPreview } from '../types/api';

interface AppState {
  datasetId: string | null;
  dataset: DatasetPreview | null;
  analysisId: string | null;
  analysisStatus: AnalysisStatus['status'] | null;
  setDatasetId: (id: string | null) => void;
  setAnalysis: (id: string | null, status?: AnalysisStatus['status'] | null) => void;
  clearWorkspace: () => void;
}

const AppStateContext = createContext<AppState | null>(null);

export const AppStateProvider = ({ children }: { children: React.ReactNode }) => {
  const [datasetId, setDatasetIdState] = useState<string | null>(() => localStorage.getItem('currentDatasetId'));
  const [dataset, setDataset] = useState<DatasetPreview | null>(null);
  const [analysisId, setAnalysisId] = useState<string | null>(() => localStorage.getItem('currentAnalysisId'));
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus['status'] | null>(null);

  const sync = () => {
    setDatasetIdState(localStorage.getItem('currentDatasetId'));
    setAnalysisId(localStorage.getItem('currentAnalysisId'));
  };

  useEffect(() => {
    window.addEventListener('workspacechange', sync);
    window.addEventListener('storage', sync);
    return () => {
      window.removeEventListener('workspacechange', sync);
      window.removeEventListener('storage', sync);
    };
  }, []);

  useEffect(() => {
    if (!datasetId) {
      setDataset(null);
      return;
    }
    getDatasetPreview(datasetId, 1).then(response => setDataset(response.data)).catch(() => setDataset(null));
  }, [datasetId]);

  useEffect(() => {
    if (!analysisId) {
      setAnalysisStatus(null);
      return;
    }
    let active = true;
    const refresh = () => getAnalysisStatus(analysisId)
      .then(response => {
        if (active) setAnalysisStatus(response.data.status);
      })
      .catch(() => {
        if (active) setAnalysisStatus(null);
      });
    refresh();
    const interval = window.setInterval(refresh, 5000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, [analysisId]);

  const value = useMemo<AppState>(() => ({
    datasetId,
    dataset,
    analysisId,
    analysisStatus,
    setDatasetId: (id) => {
      if (id) localStorage.setItem('currentDatasetId', id);
      else localStorage.removeItem('currentDatasetId');
      sync();
      window.dispatchEvent(new Event('workspacechange'));
    },
    setAnalysis: (id, status = null) => {
      if (id) localStorage.setItem('currentAnalysisId', id);
      else localStorage.removeItem('currentAnalysisId');
      setAnalysisStatus(status);
      sync();
      window.dispatchEvent(new Event('workspacechange'));
    },
    clearWorkspace: () => {
      localStorage.removeItem('currentDatasetId');
      localStorage.removeItem('currentAnalysisId');
      setDataset(null);
      setAnalysisStatus(null);
      sync();
      window.dispatchEvent(new Event('workspacechange'));
    },
  }), [datasetId, dataset, analysisId, analysisStatus]);

  return <AppStateContext.Provider value={value}>{children}</AppStateContext.Provider>;
};

export const useAppState = () => {
  const context = useContext(AppStateContext);
  if (!context) throw new Error('useAppState must be used inside AppStateProvider');
  return context;
};
