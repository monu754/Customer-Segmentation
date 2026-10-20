import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { OverviewPage } from './pages/OverviewPage';
import { DatasetPage } from './pages/DatasetPage';
import { EDAPage } from './pages/EDAPage';
import { ClusteringPage } from './pages/ClusteringPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { SegmentsPage } from './pages/SegmentsPage';
import { SegmentInsightsPage } from './pages/SegmentInsightsPage';
import { ReportsPage } from './pages/ReportsPage';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { AppStateProvider } from './context/AppStateContext';

function App() {
  return (
    <Router>
      <AppStateProvider>
        <div className="app-shell flex h-screen">
          <Sidebar />
          <div className="flex-1 flex flex-col min-w-0">
            <Header />
            <main className="flex-1 p-6 md:p-8 overflow-y-auto">
            <Routes>
              <Route path="/" element={<Navigate replace to="/overview" />}/>
              <Route path="/overview" element={<OverviewPage />} />
              <Route path="/dataset" element={<DatasetPage />} />
              <Route path="/eda" element={<EDAPage />} />
              <Route path="/clustering" element={<ClusteringPage />} />
              <Route path="/evaluation/:analysisId" element={<EvaluationPage />} />
              <Route path="/segments/:analysisId" element={<SegmentsPage />} />
              <Route path="/segments/:analysisId/insights" element={<SegmentInsightsPage />} />
              <Route path="/reports/:analysisId" element={<ReportsPage />} />
              <Route path="*" element={<Navigate replace to="/overview" />}/>
            </Routes>
            </main>
          </div>
        </div>
      </AppStateProvider>
    </Router>
  );
}

export default App;