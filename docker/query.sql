-- To automatically capture slow queries, execute this on your database to log any statement exceeding 15ms

ALTER SYSTEM SET log_min_duration_statement = 15; -- milliseconds
SELECT pg_reload_conf();