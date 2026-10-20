import React from 'react';
import { Activity, BarChart2, Database, Layers, PieChart } from 'lucide-react';
import { useAppState } from '../../context/AppStateContext';

export const Header = () => {
  const { dataset, analysisId, analysisStatus } = useAppState();
  const statusLabel = analysisStatus ? analysisStatus.replace(/^\w/, value => value.toUpperCase()) : 'No analysis';

  return (
    <header className="topbar">
      <div className="flex items-center justify-between gap-6 px-6 py-4 md:px-8">
        <div className="flex items-center gap-4 min-w-0">
          <div className="brand-mark"><Layers className="h-5 w-5" /></div>
          <div className="min-w-0">
            <p className="eyebrow">Workspace</p>
            <h1 className="truncate text-lg md:text-xl font-semibold text-slate-900">Customer Segmentation</h1>
          </div>
        </div>
        <div className="flex items-center gap-2 md:gap-3">
          <div className={`status-pill ${dataset ? 'status-good' : 'status-muted'}`}>
            <Database className="h-4 w-4" />
            <span className="hidden sm:inline">{dataset ? `${dataset.total_rows.toLocaleString()} records` : 'No dataset'}</span>
          </div>
          <div className={`status-pill ${analysisStatus === 'failed' ? 'status-bad' : analysisId ? 'status-accent' : 'status-muted'}`}>
            {analysisStatus === 'running' ? <BarChart2 className="h-4 w-4 animate-spin" /> : analysisStatus === 'completed' ? <PieChart className="h-4 w-4" /> : <Activity className="h-4 w-4" />}
            <span className="hidden sm:inline">{statusLabel}</span>
          </div>
        </div>
      </div>
    </header>
  );
};