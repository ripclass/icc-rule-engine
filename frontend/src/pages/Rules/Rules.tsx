import React, { useState, useEffect } from 'react';
import {
  Search,
  Upload,
  Eye,
  Trash2,
  HelpCircle
} from 'lucide-react';
import { Card, CardHeader, CardContent, CardTitle } from '../../components/ui/Card';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import Modal from '../../components/ui/Modal';
import { rulesApi } from '../../api';
import type { Rule } from '../../types';
import toast from 'react-hot-toast';

const Rules: React.FC = () => {
  const [rules, setRules] = useState<Rule[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  // Modal states
  const [viewModalOpen, setViewModalOpen] = useState(false);
  const [explainModalOpen, setExplainModalOpen] = useState(false);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [selectedRule, setSelectedRule] = useState<Rule | null>(null);
  const [explanation, setExplanation] = useState('');
  const [explanationLoading, setExplanationLoading] = useState(false);

  // Upload states
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadSource, setUploadSource] = useState('');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchRules();
  }, [sourceFilter, typeFilter]);

  const fetchRules = async () => {
    try {
      setLoading(true);
      const filters: any = {};
      if (sourceFilter) filters.source = sourceFilter;
      if (typeFilter) filters.rule_type = typeFilter;

      const data = await rulesApi.getRules(filters);
      setRules(data);
    } catch (error) {
      toast.error('Failed to fetch rules');
      console.error('Error fetching rules:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExplainRule = async (rule: Rule) => {
    setSelectedRule(rule);
    setExplainModalOpen(true);
    setExplanationLoading(true);

    try {
      const response = await rulesApi.explainRule(rule.rule_id);
      setExplanation(response.explanation);
    } catch (error) {
      setExplanation('Failed to generate explanation. Please try again.');
      toast.error('Failed to explain rule');
    } finally {
      setExplanationLoading(false);
    }
  };

  const handleDeleteRule = async (rule: Rule) => {
    if (!confirm(`Are you sure you want to delete rule ${rule.rule_id}?`)) return;

    try {
      await rulesApi.deleteRule(rule.rule_id);
      toast.success('Rule deleted successfully');
      fetchRules();
    } catch (error) {
      toast.error('Failed to delete rule');
    }
  };

  const handleUpload = async () => {
    if (!uploadFile || !uploadSource) {
      toast.error('Please select a file and enter source');
      return;
    }

    try {
      setUploading(true);
      const response = await rulesApi.uploadRulebook(uploadFile, uploadSource);
      toast.success(`Successfully uploaded ${response.rules_created} rules`);
      setUploadModalOpen(false);
      setUploadFile(null);
      setUploadSource('');
      fetchRules();
    } catch (error) {
      toast.error('Failed to upload rulebook');
    } finally {
      setUploading(false);
    }
  };

  const filteredRules = rules.filter(rule =>
    rule.rule_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    rule.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (rule.title && rule.title.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const uniqueSources = Array.from(new Set(rules.map(rule => rule.source)));

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Rules Management</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage ICC trade finance rules and upload new rulebooks
          </p>
        </div>
        <button
          onClick={() => setUploadModalOpen(true)}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Upload className="w-4 h-4" />
          <span>Upload Rulebook</span>
        </button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-4">
            {/* Search */}
            <div className="flex-1 min-w-64">
              <div className="relative">
                <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search rules..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Source Filter */}
            <select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Sources</option>
              {uniqueSources.map(source => (
                <option key={source} value={source}>{source}</option>
              ))}
            </select>

            {/* Type Filter */}
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Types</option>
              <option value="codable">Codable</option>
              <option value="ai_assisted">AI-Assisted</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Rules Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Rules ({filteredRules.length})</CardTitle>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Showing {filteredRules.length} of {rules.length} rules
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <LoadingSpinner size="lg" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Rule ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Source
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Title
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {filteredRules.map((rule) => (
                    <tr key={rule.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {rule.rule_id}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          Article {rule.article}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                          {rule.source}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 dark:text-white max-w-xs truncate">
                          {rule.title || 'No title'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          rule.type === 'codable'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                            : 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400'
                        }`}>
                          {rule.type === 'codable' ? 'Codable' : 'AI-Assisted'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {new Date(rule.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => {
                              setSelectedRule(rule);
                              setViewModalOpen(true);
                            }}
                            className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                            title="View rule"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleExplainRule(rule)}
                            className="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300"
                            title="Explain rule"
                          >
                            <HelpCircle className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteRule(rule)}
                            className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                            title="Delete rule"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {filteredRules.length === 0 && !loading && (
                <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                  No rules found matching your criteria
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* View Rule Modal */}
      <Modal
        isOpen={viewModalOpen}
        onClose={() => setViewModalOpen(false)}
        title={`Rule: ${selectedRule?.rule_id}`}
        size="lg"
      >
        {selectedRule && (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Title</label>
              <p className="text-gray-900 dark:text-white">{selectedRule.title || 'No title'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Source</label>
              <p className="text-gray-900 dark:text-white">{selectedRule.source}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Article</label>
              <p className="text-gray-900 dark:text-white">{selectedRule.article}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Type</label>
              <p className="text-gray-900 dark:text-white">{selectedRule.type}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Text</label>
              <p className="text-gray-900 dark:text-white whitespace-pre-wrap">{selectedRule.text}</p>
            </div>
            {selectedRule.logic && (
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Logic</label>
                <pre className="bg-gray-100 dark:bg-gray-700 p-3 rounded text-sm text-gray-900 dark:text-white overflow-x-auto">
                  {selectedRule.logic}
                </pre>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Explain Rule Modal */}
      <Modal
        isOpen={explainModalOpen}
        onClose={() => setExplainModalOpen(false)}
        title={`Explanation: ${selectedRule?.rule_id}`}
        size="lg"
      >
        <div className="space-y-4">
          {explanationLoading ? (
            <div className="flex items-center justify-center py-8">
              <LoadingSpinner size="lg" />
            </div>
          ) : (
            <div className="prose dark:prose-invert max-w-none">
              <p className="text-gray-900 dark:text-white whitespace-pre-wrap">{explanation}</p>
            </div>
          )}
        </div>
      </Modal>

      {/* Upload Modal */}
      <Modal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        title="Upload Rulebook"
        size="md"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Source Name
            </label>
            <input
              type="text"
              value={uploadSource}
              onChange={(e) => setUploadSource(e.target.value)}
              placeholder="e.g., UCP600, ISBP, eUCP"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              PDF File
            </label>
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              onClick={() => setUploadModalOpen(false)}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleUpload}
              disabled={uploading || !uploadFile || !uploadSource}
              className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {uploading && <LoadingSpinner size="sm" />}
              <span>Upload</span>
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Rules;