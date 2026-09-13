export interface AgentMetric {
  agent_id: string;
  total_runs: number;
  error_count: number;
  error_rate_percentage: number;
  avg_tokens_recent_runs: number;
  total_tokens_consumed: number;
}

export interface TenantAnalyticsResponse {
  tenant_id: string;
  window_days: number;
  metrics: AgentMetric[];
}