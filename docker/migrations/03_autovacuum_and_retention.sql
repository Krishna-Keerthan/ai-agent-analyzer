-- -----------------------------------------------------------------------------
-- 1. Dynamically Apply Autovacuum Tuning to ALL Existing Leaf Partitions
-- -----------------------------------------------------------------------------
DO $$
DECLARE
    part_record RECORD;
BEGIN
    FOR part_record IN
        SELECT c.relname AS partition_name
        FROM pg_class c
        JOIN pg_inherits i ON c.oid = i.inhrelid
        JOIN pg_class p ON p.oid = i.inhparent
        WHERE p.relname = 'agent_runs'
          AND c.relkind = 'r'
    LOOP
        EXECUTE FORMAT(
            'ALTER TABLE %I SET (
                autovacuum_vacuum_scale_factor = 0.05,
                autovacuum_vacuum_threshold = 1000,
                autovacuum_analyze_scale_factor = 0.02,
                autovacuum_analyze_threshold = 500
            );',
            part_record.partition_name
        );
    END LOOP;
END $$;

-- -----------------------------------------------------------------------------
-- 2. Update Partition Automation to Apply Storage Parameters on Creation
-- -----------------------------------------------------------------------------
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
            'CREATE TABLE IF NOT EXISTS %I PARTITION OF agent_runs 
             FOR VALUES FROM (%L) TO (%L)
             WITH (
                 autovacuum_vacuum_scale_factor = 0.05,
                 autovacuum_vacuum_threshold = 1000,
                 autovacuum_analyze_scale_factor = 0.02,
                 autovacuum_analyze_threshold = 500
             );',
            partition_name, start_date, end_date
        );
        EXECUTE sql_stmt;
        RETURN FORMAT('Created partition with custom autovacuum: %s', partition_name);
    END IF;
    
    RETURN FORMAT('Partition %s already exists', partition_name);
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- 3. Automated Partition Pruning Function (Data Lifecycle Retention)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION drop_old_agent_runs_partitions(retention_months INT DEFAULT 6)
RETURNS TABLE(dropped_partition TEXT) AS $$
DECLARE
    cutoff_date TIMESTAMPTZ := DATE_TRUNC('month', NOW() - (retention_months || ' months')::INTERVAL);
    part_record RECORD;
    drop_stmt TEXT;
BEGIN
    FOR part_record IN
        SELECT c.relname AS partition_name
        FROM pg_class c
        JOIN pg_inherits i ON c.oid = i.inhrelid
        JOIN pg_class p ON p.oid = i.inhparent
        WHERE p.relname = 'agent_runs'
          AND c.relkind = 'r'
    LOOP
        IF part_record.partition_name ~ '^agent_runs_\d{4}_\d{2}$' THEN
            DECLARE
                part_date_str TEXT := SUBSTRING(part_record.partition_name FROM 'agent_runs_(\d{4}_\d{2})');
                part_date TIMESTAMPTZ := TO_DATE(part_date_str, 'YYYY_MM');
            BEGIN
                IF part_date < cutoff_date THEN
                    drop_stmt := FORMAT('DROP TABLE IF EXISTS %I CASCADE;', part_record.partition_name);
                    EXECUTE drop_stmt;
                    dropped_partition := part_record.partition_name;
                    RETURN NEXT;
                END IF;
            END;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;