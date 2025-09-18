import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, CheckSquare, Upload, Play, TrendingUp, Clock, AlertCircle } from 'lucide-react';
import { Card, CardHeader, CardContent, CardTitle } from '../../components/ui/Card';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import { dashboardApi } from '../../api';
import type { Rule } from '../../types';

interface DashboardSummary {
  totalRules: number;
  lastRuleUpload?: string;
  totalValidations: number;
  lastValidationStatus?: string;
  recentRules: Rule[];
}

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        setLoading(true);
        const data = await dashboardApi.getSummary();
        setSummary(data);
      } catch (err) {
        setError('Failed to load dashboard data');
        console.error('Dashboard error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Overview of your ICC Rule Engine system
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                <BookOpen className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Rules</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {summary?.totalRules || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <CheckSquare className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Validations Run</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {summary?.totalValidations || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
                <Clock className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Last Upload</p>
                <p className="text-sm font-bold text-gray-900 dark:text-white">
                  {summary?.lastRuleUpload
                    ? formatDate(summary.lastRuleUpload).split(',')[0]
                    : 'No uploads yet'
                  }
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-orange-100 dark:bg-orange-900/20 rounded-lg">
                <TrendingUp className="w-6 h-6 text-orange-600 dark:text-orange-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">System Status</p>
                <p className="text-sm font-bold text-green-600 dark:text-green-400">
                  Operational
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Link
              to="/rules/upload"
              className="flex items-center p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                <Upload className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="ml-4">
                <p className="font-medium text-gray-900 dark:text-white">Upload Rulebook</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Add new ICC rules from PDF
                </p>
              </div>
            </Link>

            <Link
              to="/validation/new"
              className="flex items-center p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <Play className="w-5 h-5 text-green-600 dark:text-green-400" />
              </div>
              <div className="ml-4">
                <p className="font-medium text-gray-900 dark:text-white">Run Validation</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Validate LC documents
                </p>
              </div>
            </Link>
          </div>
        </CardContent>
      </Card>

      {/* Recent Rules */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Recent Rules</CardTitle>
            <Link
              to="/rules"
              className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-500"
            >
              View all
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          {summary?.recentRules.length ? (
            <div className="space-y-4">
              {summary.recentRules.map((rule) => (
                <div
                  key={rule.id}
                  className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <div className={`px-2 py-1 rounded text-xs font-medium ${
                      rule.type === 'codable'
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                        : 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400'
                    }`}>
                      {rule.type === 'codable' ? 'Codable' : 'AI-Assisted'}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {rule.rule_id}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {rule.title || 'No title'}
                      </p>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {formatDate(rule.created_at)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              No rules uploaded yet. <Link to="/rules/upload" className="text-blue-600 dark:text-blue-400 hover:underline">Upload your first rulebook</Link>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;