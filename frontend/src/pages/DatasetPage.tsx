import React, { useState, useCallback } from 'react';
import { uploadDataset, getDatasetPreview, getDatasetSummary, deleteDataset } from '../services/api';
import { DatasetInfo, DatasetPreview, DatasetSummary } from '../types/api';
import { FileText, Upload, Trash2, RefreshCw, Loader2, CheckCircle, AlertTriangle } from 'lucide-react';
import { useAppState } from '../context/AppStateContext';

export const DatasetPage = () => {
  const { setDatasetId: setActiveDataset, clearWorkspace } = useAppState();
  const [datasetId, setDatasetId] = useState<string | null>(null);
  const [datasetInfo, setDatasetInfo] = useState<DatasetInfo | null>(null);
  const [datasetPreview, setDatasetPreview] = useState<DatasetPreview | null>(null);
  const [datasetSummary, setDatasetSummary] = useState<DatasetSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewRows, setPreviewRows] = useState<number>(10);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setError(null);
      setSuccess(null);
    }
  };

  const handleDrop = (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
      setError(null);
      setSuccess(null);
    }
  };

  const handleUpload = useCallback(async () => {
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await uploadDataset(selectedFile);
      const data = response.data;

      setDatasetId(data.dataset_id);
      setActiveDataset(data.dataset_id);
      setDatasetInfo(data);
      setSuccess('Dataset uploaded successfully!');

      // Load preview and summary
      await loadDatasetDetails(data.dataset_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to upload dataset');
    } finally {
      setLoading(false);
    }
  }, [selectedFile]);

  const loadDatasetDetails = useCallback(async (id: string) => {
    try {
      const [previewResponse, summaryResponse] = await Promise.all([
        getDatasetPreview(id, previewRows),
        getDatasetSummary(id)
      ]);

      setDatasetPreview(previewResponse.data);
      setDatasetSummary(summaryResponse.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load dataset details');
    }
  }, [previewRows]);

  const handleDelete = useCallback(async () => {
    if (!datasetId) return;

    if (window.confirm('Are you sure you want to delete this dataset? This action cannot be undone.')) {
      setLoading(true);
      try {
        await deleteDataset(datasetId);
        setDatasetId(null);
        clearWorkspace();
        setDatasetInfo(null);
        setDatasetPreview(null);
        setDatasetSummary(null);
        setSuccess('Dataset deleted successfully');
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Failed to delete dataset');
      } finally {
        setLoading(false);
      }
    }
  }, [datasetId]);

  const handleRefresh = useCallback(() => {
    if (datasetId) {
      loadDatasetDetails(datasetId);
    }
  }, [datasetId, loadDatasetDetails]);

  if (loading && !datasetId) {
    return (
      <div className="p-6">
        <div className="flex flex-col items-center justify-center min-h-[200px]">
          <Loader2 className="h-8 w-8 animate-spin mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Dataset Management</h1>
        <p className="text-gray-600">
          Upload and manage your customer dataset for segmentation analysis.
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

      {/* Upload Section */}
      <div className="mb-8">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-500 transition-border">
          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            className="hidden"
            id="file-input"
            onChange={handleFileChange}
          />
          <label htmlFor="file-input" className="cursor-pointer">
            {selectedFile ? (
              <>
                <FileText className="h-6 w-6 mb-3" />
                <p className="font-medium">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">Click to change file</p>
              </>
            ) : (
              <>
                <Upload className="h-8 w-8 mb-4" />
                <p className="font-medium">Drag & drop or click to upload</p>
                <p className="text-sm text-gray-500">
                  Supported formats: CSV, Excel (.xlsx, .xls)
                </p>
              </>
            )}
          </label>
          <button
            onClick={handleUpload}
            disabled={loading || !selectedFile}
            className={`mt-6 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:bg-indigo-300 disabled:cursor-not-allowed transition-colors`}
          >
            {loading ? 'Uploading...' : 'Upload Dataset'}
          </button>
        </div>
      </div>

      {/* Dataset Info Section */}
      {datasetInfo && (
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Dataset Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold text-gray-900 mb-2">Filename</h3>
              <p className="text-gray-600">{datasetInfo.filename}</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold text-gray-900 mb-2">Rows</h3>
              <p className="text-gray-600">{datasetInfo.rows.toLocaleString()}</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold text-gray-900 mb-2">Columns</h3>
              <p className="text-gray-600">{datasetInfo.columns}</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold text-gray-900 mb-2">Numeric Columns</h3>
              <p className="text-gray-600">{datasetInfo.numeric_columns.length}</p>
            </div>
          </div>
        </div>
      )}

      {/* Dataset Preview Section */}
      {datasetPreview && (
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900">Dataset Preview</h2>
            <div className="flex items-center space-x-2">
              <label className="text-gray-700">Rows to show:</label>
              <select
                value={previewRows}
                onChange={(e) => {
                  setPreviewRows(Number(e.target.value));
                  loadDatasetDetails(datasetId!);
                }}
                className="border px-2 py-1 rounded"
              >
                {[5, 10, 20, 50, 100].map((rows) => (
                  <option key={rows} value={rows}>
                    {rows}
                  </option>
                ))}
              </select>
              <button
                onClick={handleRefresh}
                className="px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
              >
                <RefreshCw className="h-4 w-4" />
              </button>
            </div>
          </div>

          {datasetPreview.total_rows === 0 ? (
            <p className="text-gray-500 text-center py-4">No data available</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white border">
                <thead>
                  <tr className="bg-gray-50">
                    {datasetPreview.columns.map((col) => (
                      <th key={col} className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {datasetPreview.preview_rows.map((row, rowIndex) => (
                    <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      {datasetPreview.columns.map((col, colIndex) => (
                        <td key={colIndex} className="px-4 py-2 text-sm">
                          {row[col] === '' ? '<em>Missing</em>' : String(row[col])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="mt-4 text-sm text-gray-500">
            Showing {Math.min(datasetPreview.total_rows, previewRows)} of {datasetPreview.total_rows.toLocaleString()} rows
          </div>
        </div>
      )}

      {/* Dataset Summary Section */}
      {datasetSummary && (
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Data Quality Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Missing Values */}
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold text-gray-900 mb-2">Missing Values</h3>
              {Object.keys(datasetSummary.data_quality.columns_with_missing).length > 0 ? (
                <ul className="space-y-1 text-sm">
                  {datasetSummary.data_quality.columns_with_missing.map((col) => (
                    <li key={col} className="flex justify-between">
                      <span>{col}</span>
                      <span className="text-red-600 font-medium">
                        {datasetSummary.data_quality.columns_with_missing.length > 0
                          ? `${datasetSummary.column_info.find(c => c.name === col)?.missing_count?.toLocaleString() || '0'} ({datasetSummary.column_info.find(c => c.name === col)?.missing_percentage || 0}%)`
                          : '0 (0%)'}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-green-600">No missing values detected</p>
              )}
            </div>

            {/* Duplicate Rows */}
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold text-gray-900 mb-2">Duplicate Rows</h3>
              <p className={`text-${datasetSummary.data_quality.duplicate_rows > 0 ? 'red-600' : 'green-600'} font-medium`}>
                {datasetSummary.data_quality.duplicate_rows.toLocaleString()} ({(
                  (datasetSummary.data_quality.duplicate_rows / datasetSummary.total_rows) * 100
                ).toFixed(2)}%)
              </p>
            </div>
          </div>

          {/* Column Details */}
          <div className="mt-6">
            <h3 className="font-semibold text-gray-900 mb-4">Column Details</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white border">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Column Name
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Missing
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Unique Values
                    </th>
                    {datasetSummary.column_info.some(col => col.mean !== undefined) && (
                      <>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Mean
                        </th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Std Dev
                        </th>
                      </>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {datasetSummary.column_info.map((col, index) => (
                    <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-4 py-2 text-sm">{col.name}</td>
                      <td className="px-4 py-2 text-sm">{col.type}</td>
                      <td className="px-4 py-2 text-sm">
                        {col.missing_count > 0 ? (
                          <span className="text-red-600">{col.missing_count.toLocaleString()} ({col.missing_percentage}%)</span>
                        ) : (
                          <span className="text-green-600">0 (0%)</span>
                        )}
                      </td>
                      <td className="px-4 py-2 text-sm">{col.unique_count.toLocaleString()}</td>
                      {col.mean !== undefined && (
                        <>
                          <td className="px-4 py-2 text-sm">{col.mean !== null ? col.mean.toFixed(2) : 'N/A'}</td>
                          <td className="px-4 py-2 text-sm">{col.std !== undefined && col.std !== null ? col.std.toFixed(2) : 'N/A'}</td>
                        </>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {datasetId && (
        <div className="mt-8">
          <button
            onClick={handleDelete}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 mr-2"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Delete Dataset
          </button>
        </div>
      )}
    </div>
  );
};