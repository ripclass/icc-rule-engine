export interface Rule {
  id: number;
  rule_id: string;
  source: string;
  article: string;
  title?: string;
  text: string;
  type: 'codable' | 'ai_assisted';
  logic?: string;
  version: string;
  created_at: string;
  updated_at?: string;
}

export interface ValidationRequest {
  document_id: string;
  document_data: Record<string, any>;
  rule_filters?: Record<string, string>;
}

export interface ValidationResult {
  rule_id: string;
  rule_text: string;
  status: 'pass' | 'fail' | 'warning';
  details?: string;
  confidence_score?: string;
}

export interface ValidationResponse {
  document_id: string;
  overall_status: 'pass' | 'fail' | 'warning';
  total_rules_checked: number;
  passed: number;
  failed: number;
  warnings: number;
  results: ValidationResult[];
  timestamp: string;
}

export interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'degraded';
  service: string;
  version: string;
  components?: {
    [key: string]: {
      status: 'healthy' | 'unhealthy';
      message: string;
    };
  };
}

export interface RuleUploadResponse {
  message: string;
  rules_created: number;
  rules: Rule[];
}

export interface ValidationHistory {
  document_id: string;
  total_sessions: number;
  sessions: Array<{
    timestamp: string;
    results: Array<{
      rule_id: string;
      rule_text: string;
      status: string;
      details: string;
      confidence_score?: string;
    }>;
  }>;
}