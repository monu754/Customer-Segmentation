import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, AlertTriangle, BarChart2, CheckCircle, Database, Download, FileText, PieChart, Users } from 'lucide-react';
import { checkHealth } from '../services/api';
import { useAppState } from '../context/AppStateContext';

export const OverviewPage = () => {
  const navigate = useNavigate();
  const [backendStatus, setBackendStatus] = useState<'checking' | 'healthy' | 'unhealthy'>('checking');
  const [error, setError] = useState<string | null>(null);
  const { dataset, analysisId, analysisStatus } = useAppState();

  useEffect(() => {
    checkHealth()
      .then(() => setBackendStatus('healthy'))
      .catch(() => {
        setBackendStatus('unhealthy');
        setError('Backend service is not available');
      });
  }, []);

  if (backendStatus === 'checking') {
    return (
      <div className="p-6 flex items-center gap-3">
        <Activity className="h-6 w-6 animate-spin text-indigo-600" />
        <span>Checking backend service...</span>
      </div>
    );
  }

  if (backendStatus === 'unhealthy') {
    return (
      <div className="p-6 text-center">
        <AlertTriangle className="mx-auto h-8 w-8 text-red-500 mb-4" />
        <h2 className="text-xl font-bold text-gray-900 mb-2">Backend Unavailable</h2>
        <p className="text-gray-600 mb-6">{error}</p>
        <button onClick={() => window.location.reload()} className="px-4 py-2 bg-indigo-600 text-white rounded-md">
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Dashboard Overview</h1>
        <p className="text-gray-600">Run customer segmentation analyses and review generated reports.</p>
      </div>

      <div className="mb-8 flex items-center gap-3 text-green-700">
        <CheckCircle className="h-5 w-5" />
        <span>Backend service is healthy and ready for analysis.</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <SummaryCard title="Dataset" value={dataset?.filename || 'Not loaded'} icon={<Database className="h-6 w-6" />} />
        <SummaryCard title="Records" value={dataset ? dataset.total_rows.toLocaleString() : '0'} icon={<Users className="h-6 w-6" />} />
        <SummaryCard title="Analysis" value={analysisStatus || 'Ready'} icon={<PieChart className="h-6 w-6" />} />
        <SummaryCard title="Reports" value={analysisId ? 'Ready to export' : 'After analysis'} icon={<FileText className="h-6 w-6" />} />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <ActionCard title="Manage Dataset" description="Upload and inspect customer data" icon={<FileText />} onClick={() => navigate('/dataset')} />
        <ActionCard title="Explore Data" description="Visualize distributions and relationships" icon={<BarChart2 />} onClick={() => navigate('/eda')} />
        <ActionCard title="Run Clustering" description="Configure and execute segmentation" icon={<Users />} onClick={() => navigate('/clustering')} />
        <ActionCard
          title="View Reports"
          description="Download analysis results and models"
          icon={<Download />}
          onClick={() => navigate(analysisId ? `/reports/${analysisId}` : '/clustering')}
        />
      </div>
    </div>
  );
};

const SummaryCard = ({ title, value, icon }: { title: string; value: string; icon: React.ReactNode }) => (
  <div className="glass-card p-6 rounded-2xl">
    <div className="text-indigo-600 mb-3">{icon}</div>
    <h2 className="text-sm font-medium text-gray-500">{title}</h2>
    <p className="text-xl font-bold text-gray-900 mt-1">{value}</p>
  </div>
);

const ActionCard = ({ title, description, icon, onClick }: { title: string; description: string; icon: React.ReactNode; onClick: () => void }) => (
  <button onClick={onClick} className="glass-card action-card p-6 rounded-2xl text-left">
    <div className="text-indigo-600 mb-3">{icon}</div>
    <h2 className="font-semibold text-gray-900">{title}</h2>
    <p className="text-sm text-gray-600 mt-2">{description}</p>
  </button>
);
