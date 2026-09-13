import { getTenantAnalytics } from "@/lib/api";
import AgentChart from "./AgentChart";
import RefreshControl from "./RefreshControl";
import { AgentMetric } from "@/types/analytics";

const DEMO_TENANT_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11";

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ days?: string }>;
}) {
  const params = await searchParams;
  const days = params.days ? parseInt(params.days, 10) : 7;
  const analyticsData = await getTenantAnalytics(DEMO_TENANT_ID, days);

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", maxWidth: "1000px", margin: "0 auto" }}>
      <h1>AI Agent Analytics Dashboard</h1>
      <p style={{ color: "#666", marginBottom: "1.5rem" }}>
        Tenant ID: <code>{analyticsData.tenant_id}</code> | Window: Last {analyticsData.window_days} Days
      </p>

      <RefreshControl />

      <div style={{ marginBottom: "1.5rem" }}>
        <a href="?days=7" style={{ marginRight: "12px", textDecoration: days === 7 ? "underline" : "none", fontWeight: days === 7 ? "bold" : "normal" }}>7 Days</a>
        <a href="?days=30" style={{ marginRight: "12px", textDecoration: days === 30 ? "underline" : "none", fontWeight: days === 30 ? "bold" : "normal" }}>30 Days</a>
        <a href="?days=90" style={{ textDecoration: days === 90 ? "underline" : "none", fontWeight: days === 90 ? "bold" : "normal" }}>90 Days</a>
      </div>

      <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #cbd5e1" }}>
            <th style={{ padding: "10px" }}>Agent ID</th>
            <th style={{ padding: "10px" }}>Total Runs</th>
            <th style={{ padding: "10px" }}>Error Rate</th>
            <th style={{ padding: "10px" }}>Avg Tokens</th>
            <th style={{ padding: "10px" }}>Total Tokens</th>
          </tr>
        </thead>
        <tbody>
          {analyticsData.metrics.map((metric: AgentMetric) => (
            <tr key={metric.agent_id} style={{ borderBottom: "1px solid #e2e8f0" }}>
              <td style={{ padding: "10px" }}><code>{metric.agent_id}</code></td>
              <td style={{ padding: "10px" }}>{metric.total_runs}</td>
              <td style={{ padding: "10px", color: metric.error_rate_percentage > 0 ? "#ef4444" : "#0f172a" }}>
                {metric.error_rate_percentage}%
              </td>
              <td style={{ padding: "10px" }}>{metric.avg_tokens_recent_runs}</td>
              <td style={{ padding: "10px", fontWeight: 600 }}>{metric.total_tokens_consumed.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Interactive Visualizer Client Component */}
      <AgentChart metrics={analyticsData.metrics} />
    </div>
  );
}