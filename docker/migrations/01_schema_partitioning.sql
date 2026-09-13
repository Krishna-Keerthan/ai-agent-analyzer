-- Enable UUID generation extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE agent_runs (
    id UUID DEFAULT gen_random_uuid() NOT NULL,
    tenant_id UUID NOT NULL,
    agent_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    execution_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- STATIC PARTITION DEFINITIONS
CREATE TABLE agent_runs_2026_09 PARTITION OF agent_runs
FOR VALUES FROM ('2026-09-01 00:00:00+00') TO ('2026-10-01 00:00:00+00');

CREATE TABLE agent_runs_2026_10 PARTITION OF agent_runs 
FOR VALUES FROM ('2026-10-01 00:00:00+00') TO ('2026-11-01 00:00:00+00');

-- Dynamic Partition Automation Function
CREATE OR REPLACE FUNCTION create_agent_runs_partition(target_date TIMESTAMPTZ)
RETURNS TEXT AS $$
DECLARE
    partition_date TEXT := TO_CHAR(target_date, 'YYYY_MM');
    start_date TEXT := TO_CHAR(DATE_TRUNC('month', target_date), 'YYYY-MM-DD');
    end_date TEXT := TO_CHAR(DATE_TRUNC('month', target_date) + INTERVAL '1 month', 'YYYY-MM-DD');
    partition_name TEXT := 'agent_runs_' || partition_date;
    sql_stmt TEXT;
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relname = partition_name
    ) THEN
        sql_stmt := FORMAT(
            'CREATE TABLE IF NOT EXISTS %I PARTITION OF agent_runs FOR VALUES FROM (%L) TO (%L);',
            partition_name, start_date, end_date
        );
        EXECUTE sql_stmt;
        RETURN FORMAT('Created partition: %s', partition_name);
    END IF;
    RETURN FORMAT('PARTITION %s already exists', partition_name);
END;
$$ LANGUAGE plpgsql;