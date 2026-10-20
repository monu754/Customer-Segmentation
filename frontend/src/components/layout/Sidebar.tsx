import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  BarChart2,
  ScatterChart,
  Users,
  FileText as FileIcon
} from 'lucide-react';
import { useAppState } from '../../context/AppStateContext';

export const Sidebar = () => {
  const { analysisId } = useAppState();

  return (
    <aside className="sidebar w-64 hidden lg:flex flex-col">
      <div className="px-6 py-4">
        <div className="flex items-center space-x-3 mb-6">
          <LayoutDashboard className="h-6 w-6 text-indigo-600" />
          <h2 className="text-lg font-semibold text-gray-900">
            Customer Segmentation
          </h2>
        </div>

        <nav className="space-y-1">
          <NavLink
            to="/"
            end
            className={({ isActive }) => `
              flex items-center px-3 py-2 mb-2 text-sm font-medium
              ${isActive ? 'bg-indigo-50 text-indigo-600' : 'text-gray-600 hover:bg-gray-50'}
              rounded-lg
            `}
          >
            <LayoutDashboard className="h-4 w-4 mr-3" />
            Overview
          </NavLink>

          <NavLink
            to="/dataset"
            className={({ isActive }) => `
              flex items-center px-3 py-2 mb-2 text-sm font-medium
              ${isActive ? 'bg-indigo-50 text-indigo-600' : 'text-gray-600 hover:bg-gray-50'}
              rounded-lg
            `}
          >
            <FileText className="h-4 w-4 mr-3" />
            Dataset
          </NavLink>

          <NavLink
            to="/eda"
            className={({ isActive }) => `
              flex items-center px-3 py-2 mb-2 text-sm font-medium
              ${isActive ? 'bg-indigo-50 text-indigo-600' : 'text-gray-600 hover:bg-gray-50'}
              rounded-lg
            `}
          >
            <BarChart2 className="h-4 w-4 mr-3" />
            Exploratory Analysis
          </NavLink>

          <NavLink
            to="/clustering"
            className={({ isActive }) => `
              flex items-center px-3 py-2 mb-2 text-sm font-medium
              ${isActive ? 'bg-indigo-50 text-indigo-600' : 'text-gray-600 hover:bg-gray-50'}
              rounded-lg
            `}
          >
            <ScatterChart className="h-4 w-4 mr-3" />
            Clustering
          </NavLink>

          <NavLink
            to={analysisId ? `/segments/${analysisId}` : '/clustering'}
            className={({ isActive }) => `
              flex items-center px-3 py-2 mb-2 text-sm font-medium
              ${isActive ? 'bg-indigo-50 text-indigo-600' : 'text-gray-600 hover:bg-gray-50'}
              rounded-lg
            `}
          >
            <Users className="h-4 w-4 mr-3" />
            Segments
          </NavLink>

          <NavLink
            to={analysisId ? `/reports/${analysisId}` : '/clustering'}
            className={({ isActive }) => `
              flex items-center px-3 py-2 mb-2 text-sm font-medium
              ${isActive ? 'bg-indigo-50 text-indigo-600' : 'text-gray-600 hover:bg-gray-50'}
              rounded-lg
            `}
          >
            <FileIcon className="h-4 w-4 mr-3" />
            Reports
          </NavLink>

        </nav>
      </div>

      <div className="mt-auto px-6 pt-4 pb-8">
        <div className="sidebar-footer"><span className="pulse-dot" /> Live workspace</div>
      </div>
    </aside>
  );
};