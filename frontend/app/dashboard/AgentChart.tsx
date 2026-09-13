'use client';

import { AgentMetric } from "@/types/analytics";

interface AgentChartProps {
  metrics: AgentMetric[];
}

export default function AgentChart({ metrics }: AgentChartProps) {
  // Find max tokens for relative percentage bar scaling
  const maxTokens = Math.max(...metrics.map((m) => m.total_tokens_consumed), 1);

  return (
    <div style={{ marginTop: "2rem", padding: "1.5rem", border: "1px solid #e2e8f0", borderRadius: "8px", background: "#fff" }}>
      <h3 style={{ margin: "0 0 1rem 0", fontSize: "1.1rem", color: "#1e293b" }}>
        Token Consumption Distribution
      </h3>
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {metrics.map((metric) => {
          const percentage = Math.round((metric.total_tokens_consumed / maxTokens) * 100);
          return (
            <div key={metric.agent_id}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.25rem", fontSize: "0.85rem" }}>
                <span style={{ fontFamily: "monospace", color: "#475569" }}>{metric.agent_id}</span>
                <span style={{ fontWeight: 600 }}>{metric.total_tokens_consumed.toLocaleString()} tokens</span>
              </div>
              <div style={{ height: "12px", width: "100%", backgroundColor: "#f1f5f9", borderRadius: "6px", overflow: "hidden" }}>
                <div
                  style={{
                    height: "100%",
                    width: `${percentage}%`,
                    backgroundColor: metric.error_rate_percentage > 0 ? "#ef4444" : "#3b82f6",
                    transition: "width 0.4s ease-in-out",
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}