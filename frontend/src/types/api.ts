// Dataset types
export interface DatasetInfo {
  dataset_id: string;
  filename: string;
  rows: number;
  columns: number;
  column_names: string[];
  numeric_columns: string[];
  missing_values: Record<string, number>;
  duplicate_rows: number;
}

export interface DatasetPreview {
  dataset_id: string;
  filename: string;
  total_rows: number;
  total_columns: number;
  columns: string[];
  data_types: Record<string, string>;
  preview_rows: Record<string, any>[];
  missing_values: Record<string, number>;
  duplicate_rows: number;
}

export interface DatasetSummary {
  dataset_id: string;
  filename: string;
  total_rows: number;
  total_columns: number;
  column_info: Array<{
    name: string;
    type: string;
    missing_count: number;
    missing_percentage: number;
    unique_count: number;
    mean?: number;
    median?: number;
    std?: number;
    min?: number;
    max?: number;
  }>;
  summary_statistics: Record<string, any>;
  data_quality: {
    total_missing_values: number;
    columns_with_missing: string[];
    duplicate_rows: number;
    memory_usage: number;
  };
}

// EDA types
export interface EDAAnalysis {
  analysis_id: string;
  dataset_id: string;
  type: 'eda';
  features: string[];
  eda_summary: Record<string, unknown>;
  plots: string[];
  timestamp: string;
  status: 'completed' | 'failed';
}

// Clustering types
export interface ClusteringConfig {
  dataset_id: string;
  features: string[];
  k_min?: number;
  k_max?: number;
  random_state?: number;
  n_init?: number;
}

export interface ClusteringResult {
  analysis_id: string;
  dataset_id: string;
  type: 'clustering';
  features: string[];
  k_range_evaluated: number[];
  selected_k: number;
  status: 'completed' | 'running' | 'failed';
  results: {
    metrics: {
      inertia: number;
      silhouette_score: number | null;
    };
    evaluation_results: {
      k_values: number[];
      inertias: number[];
      silhouette_scores: (number | null)[];
      selected_k: number;
      selection_rationale: string;
    };
    cluster_summary: Record<string, any>;
  };
}

// Analysis status
export interface AnalysisStatus {
  analysis_id: string;
  status: 'idle' | 'loading' | 'running' | 'completed' | 'failed';
  type: 'eda' | 'clustering' | null;
  timestamp: string;
}

// Cluster data
export interface ClusterInfo {
  cluster_id: number | string;
  size: number;
  percentage: number;
  [key: string]: any; // Feature statistics will vary
}

// Chart data types
export interface ScatterPlotDataPoint {
  x: number;
  y: number;
  cluster: number | string;
  [key: string]: any; // Additional features
}

export interface ElbowChartDataPoint {
  k: number;
  inertia: number;
}

export interface SilhouetteChartDataPoint {
  k: number;
  silhouette_score: number | null;
}