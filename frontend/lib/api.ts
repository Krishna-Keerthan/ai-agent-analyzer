import { TenantAnalyticsResponse } from "@/types/analytics";

const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || "http://127.0.0.1:8000";

export async function getTenantAnalytics(
  tenantId: string,
  days: number = 7
): Promise<TenantAnalyticsResponse> {
  const response = await fetch(
    `${BACKEND_URL}/api/v1/analytics/tenants/${tenantId}/agent-performance?days=${days}`,
    {
      // Revalidate dashboard metrics on the server every 10 seconds
      next: { revalidate: 10 },
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch tenant analytics: ${response.statusText}`);
  }

  return response.json();
}