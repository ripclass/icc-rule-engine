import React, { useState } from 'react';
import { Play, Upload, Download, History, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { Card, CardHeader, CardContent, CardTitle } from '../../components/ui/Card';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import Modal from '../../components/ui/Modal';
import { validationApi } from '../../api';
import type { ValidationRequest, ValidationResponse, ValidationHistory } from '../../types';
import toast from 'react-hot-toast';

const Validation: React.FC = () => {
  const [documentId, setDocumentId] = useState('');
  const [documentData, setDocumentData] = useState('');
  const [ruleFilters, setRuleFilters] = useState('');
  const [validationResult, setValidationResult] = useState<ValidationResponse | null>(null);
  const [validating, setValidating] = useState(false);

  // History modal
  const [historyModalOpen, setHistoryModalOpen] = useState(false);
  const [historyData, setHistoryData] = useState<ValidationHistory | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);

  const handleValidate = async () => {
    if (!documentId || !documentData) {
      toast.error('Please provide document ID and data');
      return;
    }

    try {
      setValidating(true);

      let parsedData;
      try {
        parsedData = JSON.parse(documentData);
      } catch (error) {
        toast.error('Invalid JSON format in document data');
        return;
      }

      let parsedFilters = {};
      if (ruleFilters.trim()) {
        try {
          parsedFilters = JSON.parse(ruleFilters);
        } catch (error) {
          toast.error('Invalid JSON format in rule filters');
          return;
        }
      }

      const request: ValidationRequest = {
        document_id: documentId,
        document_data: parsedData,
        rule_filters: Object.keys(parsedFilters).length > 0 ? parsedFilters : undefined
      };

      const result = await validationApi.validateDocument(request);
      setValidationResult(result);
      toast.success('Validation completed');
    } catch (error) {
      toast.error('Validation failed');
      console.error('Validation error:', error);
    } finally {
      setValidating(false);
    }
  };

  const handleLoadSample = () => {
    setDocumentId('LC-SAMPLE-001');
    setDocumentData(JSON.stringify({
      applicant: "ABC Trading Company Ltd",
      beneficiary: "XYZ Exports Ltd",
      amount: "100000.00",
      currency: "USD",
      expiry_date: "2024-12-31",
      shipment_date: "2024-12-15",
      presentation_date: "2024-12-20",
      latest_shipment_date: "2024-12-30",
      documents: [
        "Commercial Invoice",
        "Bill of Lading",
        "Insurance Certificate"
      ],
      description_of_goods: "Cotton T-shirts, 100% cotton, various sizes",
      port_of_loading: "Mumbai, India",
      port_of_discharge: "New York, USA"
    }, null, 2));
    setRuleFilters(JSON.stringify({ source: "UCP600" }, null, 2));
  };

  const handleViewHistory = async () => {
    if (!documentId) {
      toast.error('Please enter a document ID to view history');
      return;
    }

    try {
      setHistoryLoading(true);
      setHistoryModalOpen(true);
      const history = await validationApi.getValidationHistory(documentId);
      setHistoryData(history);
    } catch (error) {
      toast.error('Failed to load validation history');
      setHistoryModalOpen(false);
    } finally {
      setHistoryLoading(false);
    }
  };

  const exportResults = () => {
    if (!validationResult) return;

    const dataStr = JSON.stringify(validationResult, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `validation-${validationResult.document_id}-${new Date().getTime()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    toast.success('Results exported');
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'fail':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pass':
        return 'text-green-600 bg-green-50 dark:bg-green-900/20 dark:text-green-400';
      case 'fail':
        return 'text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400';
      case 'warning':
        return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20 dark:text-yellow-400';
      default:
        return 'text-gray-600 bg-gray-50 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Document Validation</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Validate Letter of Credit documents against ICC rules
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleLoadSample}
            className="flex items-center space-x-2 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
          >
            <Upload className="w-4 h-4" />
            <span>Load Sample</span>
          </button>
          <button
            onClick={handleViewHistory}
            disabled={!documentId}
            className="flex items-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <History className="w-4 h-4" />
            <span>View History</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle>Validation Input</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Document ID */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Document ID
              </label>
              <input
                type="text"
                value={documentId}
                onChange={(e) => setDocumentId(e.target.value)}
                placeholder="e.g., LC-001"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Document Data */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Document Data (JSON)
              </label>
              <textarea
                value={documentData}
                onChange={(e) => setDocumentData(e.target.value)}
                placeholder="Enter LC document data as JSON..."
                rows={12}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              />
            </div>

            {/* Rule Filters */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Rule Filters (Optional JSON)
              </label>
              <textarea
                value={ruleFilters}
                onChange={(e) => setRuleFilters(e.target.value)}
                placeholder='e.g., {"source": "UCP600"}'
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              />
            </div>

            {/* Validate Button */}
            <button
              onClick={handleValidate}
              disabled={validating || !documentId || !documentData}
              className="w-full flex items-center justify-center space-x-2 bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {validating ? (
                <LoadingSpinner size="sm" />
              ) : (
                <Play className="w-5 h-5" />
              )}
              <span>{validating ? 'Validating...' : 'Run Validation'}</span>
            </button>
          </CardContent>
        </Card>

        {/* Results */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Validation Results</CardTitle>
              {validationResult && (
                <button
                  onClick={exportResults}
                  className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  <Download className="w-4 h-4" />
                  <span>Export</span>
                </button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {validationResult ? (
              <div className="space-y-4">
                {/* Summary */}
                <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      Overall Status
                    </h4>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(validationResult.overall_status)}
                      <span className={`px-2 py-1 rounded text-sm font-medium ${getStatusColor(validationResult.overall_status)}`}>
                        {validationResult.overall_status.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Passed:</span>
                      <span className="ml-1 font-medium text-green-600">{validationResult.passed}</span>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Failed:</span>
                      <span className="ml-1 font-medium text-red-600">{validationResult.failed}</span>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Warnings:</span>
                      <span className="ml-1 font-medium text-yellow-600">{validationResult.warnings}</span>
                    </div>
                  </div>
                </div>

                {/* Individual Results */}
                <div className="space-y-3">
                  <h4 className="font-medium text-gray-900 dark:text-white">
                    Rule Results ({validationResult.results.length})
                  </h4>
                  <div className="max-h-96 overflow-y-auto space-y-2">
                    {validationResult.results.map((result, index) => (
                      <div
                        key={index}
                        className="p-3 border border-gray-200 dark:border-gray-600 rounded-lg"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            {getStatusIcon(result.status)}
                            <span className="font-medium text-gray-900 dark:text-white">
                              {result.rule_id}
                            </span>
                          </div>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(result.status)}`}>
                            {result.status}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          {result.rule_text}
                        </p>
                        {result.details && (
                          <p className="text-sm text-gray-800 dark:text-gray-200">
                            {result.details}
                          </p>
                        )}
                        {result.confidence_score && (
                          <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                            Confidence: {result.confidence_score}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Metadata */}
                <div className="text-xs text-gray-500 dark:text-gray-400 pt-2 border-t border-gray-200 dark:border-gray-600">
                  Document ID: {validationResult.document_id} |
                  Validated: {new Date(validationResult.timestamp).toLocaleString()}
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                Run a validation to see results here
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* History Modal */}
      <Modal
        isOpen={historyModalOpen}
        onClose={() => setHistoryModalOpen(false)}
        title={`Validation History: ${documentId}`}
        size="xl"
      >
        {historyLoading ? (
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner size="lg" />
          </div>
        ) : historyData ? (
          <div className="space-y-4">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Total sessions: {historyData.total_sessions}
            </div>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {historyData.sessions.map((session, index) => (
                <div key={index} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      Session {index + 1}
                    </h4>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {new Date(session.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <div className="space-y-2">
                    {session.results.map((result, resultIndex) => (
                      <div key={resultIndex} className="flex items-center justify-between text-sm">
                        <span className="text-gray-900 dark:text-white">{result.rule_id}</span>
                        <span className={`px-2 py-1 rounded text-xs ${getStatusColor(result.status)}`}>
                          {result.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            No validation history found for this document
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Validation;