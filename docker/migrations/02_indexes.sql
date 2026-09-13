-- -----------------------------------------------------------------------------
-- 1. JSONB Path-Ops GIN Index
-- Fast containment queries (@>) on execution_metadata (tool calls, models, tokens)
-- 50% smaller footprint than default jsonb_ops
-- -----------------------------------------------------------------------------
CREATE INDEX idx_runs_metadata_path_ops 
ON agent_runs USING GIN (execution_metadata jsonb_path_ops);

-- -----------------------------------------------------------------------------
-- 2. Composite Covering B-Tree Index (INCLUDE Clause)
-- Satisfies tenant dashboard lists via Index Only Scans
-- Eliminates heap reads by storing agent_id in B-tree leaf nodes
-- -----------------------------------------------------------------------------
CREATE INDEX idx_runs_tenant_created_covering 
ON agent_runs (tenant_id, created_at DESC) 
INCLUDE (agent_id);

-- -----------------------------------------------------------------------------
-- 3. Partial B-Tree Index for Error Filtering
-- Indexes ONLY error records, keeping index size tiny (~95% smaller)
-- -----------------------------------------------------------------------------
CREATE INDEX idx_runs_errors_partial 
ON agent_runs (tenant_id, created_at DESC) 
WHERE (execution_metadata->>'status') = 'ERROR';