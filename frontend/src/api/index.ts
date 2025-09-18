import axios from 'axios';
import type { Rule, ValidationRequest, ValidationResponse, ValidationHistory, HealthStatus, RuleUploadResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Rules API
export const rulesApi = {
  // Get all rules with optional filters
  getRules: async (params?: {
    source?: string;
    domain?: string;
    rule_type?: string;
    skip?: number;
    limit?: number;
  }): Promise<Rule[]> => {
    const response = await api.get('/rules/', { params });
    return response.data;
  },

  // Get a specific rule by rule_id
  getRule: async (ruleId: string): Promise<Rule> => {
    const response = await api.get(`/rules/${ruleId}`);
    return response.data;
  },

  // Update a rule
  updateRule: async (ruleId: string, data: Partial<Rule>): Promise<Rule> => {
    const response = await api.put(`/rules/${ruleId}`, data);
    return response.data;
  },

  // Delete a rule
  deleteRule: async (ruleId: string): Promise<{ message: string }> => {
    const response = await api.delete(`/rules/${ruleId}`);
    return response.data;
  },

  // Upload PDF rulebook
  uploadRulebook: async (file: File, source: string): Promise<RuleUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post(`/rules/upload?source=${encodeURIComponent(source)}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get rule explanation
  explainRule: async (ruleId: string): Promise<{ rule_id: string; rule_text: string; explanation: string }> => {
    const response = await api.get(`/rules/${ruleId}/explain`);
    return response.data;
  },
};

// Validation API
export const validationApi = {
  // Validate a document
  validateDocument: async (request: ValidationRequest): Promise<ValidationResponse> => {
    const response = await api.post('/validate/', request);
    return response.data;
  },

  // Quick validation (summary only)
  quickValidate: async (request: ValidationRequest): Promise<{
    document_id: string;
    overall_status: string;
    summary: {
      total_rules: number;
      passed: number;
      failed: number;
      warnings: number;
    };
    timestamp: string;
  }> => {
    const response = await api.post('/validate/quick', request);
    return response.data;
  },

  // Get validation history for a document
  getValidationHistory: async (documentId: string): Promise<ValidationHistory> => {
    const response = await api.get(`/validate/history/${documentId}`);
    return response.data;
  },
};

// Health API
export const healthApi = {
  // Basic health check
  getHealth: async (): Promise<HealthStatus> => {
    const response = await api.get('/health/');
    return response.data;
  },

  // Detailed health check
  getDetailedHealth: async (): Promise<HealthStatus> => {
    const response = await api.get('/health/detailed');
    return response.data;
  },
};

// Dashboard API (aggregated data)
export const dashboardApi = {
  // Get dashboard summary data
  getSummary: async (): Promise<{
    totalRules: number;
    lastRuleUpload?: string;
    totalValidations: number;
    lastValidationStatus?: string;
    recentRules: Rule[];
  }> => {
    try {
      // Get rules data
      const rules = await rulesApi.getRules({ limit: 100 });

      // Calculate summary
      const totalRules = rules.length;
      const lastRuleUpload = rules.length > 0
        ? rules.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0].created_at
        : undefined;

      const recentRules = rules
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        .slice(0, 5);

      return {
        totalRules,
        lastRuleUpload,
        totalValidations: 0, // This would need to be tracked in the backend
        lastValidationStatus: undefined,
        recentRules,
      };
    } catch (error) {
      console.error('Error fetching dashboard summary:', error);
      return {
        totalRules: 0,
        totalValidations: 0,
        recentRules: [],
      };
    }
  },
};