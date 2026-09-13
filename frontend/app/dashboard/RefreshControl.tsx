'use client';

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function RefreshControl() {
  const router = useRouter();
  const [autoRefresh, setAutoRefresh] = useState(false);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      router.refresh();
    }, 5000);
    return () => clearInterval(interval);
  }, [autoRefresh, router]);

  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
      <label style={{ fontSize: "0.875rem", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.4rem" }}>
        <input
          type="checkbox"
          checked={autoRefresh}
          onChange={(e) => setAutoRefresh(e.target.checked)}
        />
        Live Auto-Refresh (5s)
      </label>
      {autoRefresh && <span style={{ fontSize: "0.75rem", color: "#22c55e", fontWeight: 600 }}>● Polling active</span>}
    </div>
  );
}