import json
from uuid import UUID

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Query
import asyncpg

from app.db import init_db_pool, close_db_pool, get_db_connection
from app.schemas import BatchTraceIngestRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_pool()
    yield
    await close_db_pool()


app = FastAPI(
    title="AI Agent Analytics Engine",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "analytics-engine"
    }


@app.get("/api/v1/db-test")
async def db_connectivity_test(conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        row = await conn.fetchrow(
            """
            SELECT 
            current_database() AS db_name,
            current_user AS user_name,
            pg_backend_pid() AS backend_pid;
            """
        )
        return {
            "status":"connected",
            "database":row["db_name"],
            "user":row["user_name"],
            "backend_pid":row["backend_pid"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Pool Error: {str(e)}")


@app.post("/api/v1/traces/batch", status_code=status.HTTP_201_CREATED)
async def ingest_trace_batch(
    payload: BatchTraceIngestRequest,
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Ingests up to 10,000 trace events in a single batch using PostgreSQL binary COPY.
    Bypasses row-by-row SQL parsing and WAL log amplification.
    """

    try:
        # Transform pydantic models into a list of tuples for binary COPY
        records = [
            (
                trace.id,
                trace.tenant_id,
                trace.agent_id,
                trace.created_at,
                json.dumps(trace.execution_metadata)
            )
            for trace in payload.traces
        ]

        await conn.copy_records_to_table(
            table_name="agent_runs",
            records=records,
            columns=["id", "tenant_id", "agent_id", "created_at", "execution_metadata"]
        )

        return {
            "status": "success",
            "ingested_count": len(records)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk Ingestion Error: {str(e)}"
        )


@app.get("/api/v1/analytics/tenants/{tenant_id}/agent-performance")
async def get_tenant_agent_performance(
    tenant_id: UUID,
    days: int = Query(default=7, ge=1, le=90),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Returns aggregated token usage, run counts, and error rates per agent 
    for a specific tenant within the specified day window.
    """
    query = """
    WITH recent_runs AS (
        SELECT 
            agent_id,
            execution_metadata->>'status' AS run_status,
            COALESCE((execution_metadata->'tokens'->>'total')::INT, 0) AS total_tokens,
            ROW_NUMBER() OVER (
                PARTITION BY agent_id 
                ORDER BY created_at DESC
            ) AS run_rank
        FROM agent_runs
        WHERE tenant_id = $1
          AND created_at >= NOW() - ($2 || ' days')::INTERVAL
    )
    SELECT 
        agent_id,
        COUNT(*) AS total_runs,
        COUNT(*) FILTER (WHERE run_status = 'ERROR') AS error_count,
        ROUND(
            (COUNT(*) FILTER (WHERE run_status = 'ERROR')::NUMERIC / NULLIF(COUNT(*), 0)) * 100, 
            2
        ) AS error_rate_percentage,
        ROUND(AVG(total_tokens) FILTER (WHERE run_rank <= 100), 2) AS avg_tokens_recent_runs,
        SUM(total_tokens) AS total_tokens_consumed
    FROM recent_runs
    GROUP BY agent_id;
    """
    try:
        rows = await conn.fetch(query, tenant_id, str(days))
        return {
            "tenant_id": tenant_id,
            "window_days": days,
            "metrics": [dict(row) for row in rows]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics Query Error: {str(e)}")


@app.get("/api/v1/analytics/tenants/{tenant_id}/agent-performance")
async def get_tenant_agent_performance(
    tenant_id: UUID,
    days: int = Query(default=7, ge=1, le=90),
    conn: asyncpg.Connection = Depends(get_db_connection)
):

    ANALYTICS_QUERY = """
WITH recent_runs AS (
    SELECT 
        agent_id,
        execution_metadata->>'status' AS run_status,
        COALESCE((execution_metadata->'tokens'->>'total')::INT, 0) AS total_tokens,
        ROW_NUMBER() OVER (
            PARTITION BY agent_id 
            ORDER BY created_at DESC
        ) AS run_rank
    FROM agent_runs
    WHERE tenant_id = $1
      AND created_at >= NOW() - ($2 || ' days')::INTERVAL
)
SELECT 
    agent_id,
    COUNT(*) AS total_runs,
    COUNT(*) FILTER (WHERE run_status = 'ERROR') AS error_count,
    ROUND(
        (COUNT(*) FILTER (WHERE run_status = 'ERROR')::NUMERIC / NULLIF(COUNT(*), 0)) * 100, 
        2
    ) AS error_rate_percentage,
    ROUND(AVG(total_tokens) FILTER (WHERE run_rank <= 100), 2) AS avg_tokens_recent_runs,
    SUM(total_tokens) AS total_tokens_consumed
FROM recent_runs
GROUP BY agent_id;
"""
    
    try:
        async with conn.transaction():
            await conn.execute("SET LOCAL work_mem = '64MB';")

            rows = await conn.fetch(ANALYTICS_QUERY, tenant_id, str(days))

            return {
                "tenant_id": tenant_id,
                "window_days": days,
                "metrics": [dict(row) for row in rows]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics Query Editor: {str(e)}")

    