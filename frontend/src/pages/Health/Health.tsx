import React, { useState, useEffect } from 'react';
import { RefreshCw, CheckCircle, XCircle, AlertTriangle, Database, Zap, Settings, Activity } from 'lucide-react';
import { Card, CardHeader, CardContent, CardTitle } from '../../components/ui/Card';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import { healthApi } from '../../api';
import type { HealthStatus } from '../../types';
import toast from 'react-hot-toast';

const Health: React.FC = () => {
  const [healthData, setHealthData] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    fetchHealthData();
  }, []);

  const fetchHealthData = async () => {
    try {
      setLoading(true);
      const data = await healthApi.getDetailedHealth();
      setHealthData(data);
      setLastUpdated(new Date());
    } catch (error) {
      toast.error('Failed to fetch health status');
      console.error('Health check error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'unhealthy':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'degraded':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-50 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800';
      case 'unhealthy':
        return 'text-red-600 bg-red-50 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800';
      case 'degraded':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400 dark:border-yellow-800';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200 dark:bg-gray-900/20 dark:text-gray-400 dark:border-gray-800';
    }
  };

  const getComponentIcon = (component: string) => {
    switch (component) {
      case 'database':
        return <Database className="w-5 h-5" />;
      case 'openai':
        return <Zap className="w-5 h-5" />;
      case 'environment':
        return <Settings className="w-5 h-5" />;
      default:
        return <Activity className="w-5 h-5" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">System Health</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Monitor the health and status of ICC Rule Engine components
          </p>
        </div>
        <button
          onClick={fetchHealthData}
          disabled={loading}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {loading && !healthData ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : (
        <>
          {/* Overall Status */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  {healthData && getStatusIcon(healthData.status)}
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                      {healthData?.service || 'ICC Rule Engine'}
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400">
                      Version {healthData?.version || '1.0.0'}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${
                    healthData ? getStatusColor(healthData.status) : getStatusColor('unknown')
                  }`}>
                    {healthData?.status.toUpperCase() || 'UNKNOWN'}
                  </div>
                  {lastUpdated && (
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      Last updated: {lastUpdated.toLocaleTimeString()}
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Component Status */}
          {healthData?.components && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Object.entries(healthData.components).map(([componentName, component]) => (
                <Card key={componentName}>
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className={`p-2 rounded-lg ${
                        component.status === 'healthy'
                          ? 'bg-green-100 dark:bg-green-900/20'
                          : 'bg-red-100 dark:bg-red-900/20'
                      }`}>
                        {getComponentIcon(componentName)}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900 dark:text-white capitalize">
                          {componentName.replace('_', ' ')}
                        </h3>
                        <div className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                          component.status === 'healthy' ? getStatusColor('healthy') : getStatusColor('unhealthy')
                        }`}>
                          {component.status.toUpperCase()}
                        </div>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {component.message}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* System Information */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Service Information */}
            <Card>
              <CardHeader>
                <CardTitle>Service Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Service Name:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {healthData?.service || 'ICC Rule Engine'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Version:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {healthData?.version || '1.0.0'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Status:</span>
                  <span className={`font-medium ${
                    healthData?.status === 'healthy' ? 'text-green-600 dark:text-green-400' :
                    healthData?.status === 'degraded' ? 'text-yellow-600 dark:text-yellow-400' :
                    'text-red-600 dark:text-red-400'
                  }`}>
                    {healthData?.status?.toUpperCase() || 'UNKNOWN'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Uptime:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    Active
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <button
                  onClick={fetchHealthData}
                  className="w-full flex items-center justify-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Refresh Health Status</span>
                </button>

                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full flex items-center justify-center space-x-2 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
                >
                  <Activity className="w-4 h-4" />
                  <span>View API Documentation</span>
                </a>

                <a
                  href="http://localhost:8000/health/detailed"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full flex items-center justify-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>Raw Health Data</span>
                </a>
              </CardContent>
            </Card>
          </div>

          {/* Status History (placeholder) */}
          <Card>
            <CardHeader>
              <CardTitle>System Metrics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">99.9%</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Uptime</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {healthData?.components ? Object.keys(healthData.components).length : 0}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Components Monitored</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                    {lastUpdated ? Math.floor((Date.now() - lastUpdated.getTime()) / 1000) : 0}s
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Last Check</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};

export default Health;