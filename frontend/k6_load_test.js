import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Counter } from 'k6/metrics';

// Custom metrics tracking
const ingestLatency = new Trend('ingest_latency_ms');
const analyticsLatency = new Trend('analytics_latency_ms');
const failedRequests = new Counter('failed_requests');

export const options = {
  stages: [
    { duration: '30s', target: 50 },   // Warm-up to 50 VUs
    { duration: '1m',  target: 200 },  // Ramp-up to 200 concurrent VUs
    { duration: '1m',  target: 500 },  // Peak load: 500 VUs
    { duration: '30s', target: 0 },    // Cool-down
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],             // Less than 1% failure rate
    'analytics_latency_ms': ['p(95)<15'],       // 95% of analytics queries < 15ms
    'ingest_latency_ms': ['p(95)<100'],         // 95% of batch writes < 100ms
  },
};

const BASE_URL = 'http://127.0.0.1:8000';
const TENANT_ID = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11';

export default function () {
  // 90% Write Traffic / 10% Read Traffic split
  const isWrite = Math.random() < 0.9;

  if (isWrite) {
    // -------------------------------------------------------------------------
    // 1. Batch Trace Ingestion (POST /api/v1/traces/batch)
    // -------------------------------------------------------------------------
    const payload = JSON.stringify({
      traces: Array.from({ length: 10 }, () => ({
        tenant_id: TENANT_ID,
        agent_id: 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
        created_at: new Date().toISOString(),
        execution_metadata: {
          model: 'gpt-4o',
          tokens: { prompt: 150, completion: 50, total: 200 },
          status: Math.random() < 0.05 ? 'ERROR' : 'SUCCESS',
          tools: ['vector_search']
        }
      }))
    });

    const params = { headers: { 'Content-Type': 'application/json' } };
    const res = http.post(`${BASE_URL}/api/v1/traces/batch`, payload, params);

    ingestLatency.add(res.timings.duration);
    const success = check(res, { 'ingest status 201': (r) => r.status === 201 });
    if (!success) failedRequests.add(1);

  } else {
    // -------------------------------------------------------------------------
    // 2. Real-Time Dashboard Query (GET /api/v1/analytics/tenants/.../agent-performance)
    // -------------------------------------------------------------------------
    const res = http.get(`${BASE_URL}/api/v1/analytics/tenants/${TENANT_ID}/agent-performance?days=7`);

    analyticsLatency.add(res.timings.duration);
    const success = check(res, { 'analytics status 200': (r) => r.status === 200 });
    if (!success) failedRequests.add(1);
  }

  sleep(0.1); // Small think-time between virtual user requests
}