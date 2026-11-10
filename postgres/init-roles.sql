-- Creates the restricted runtime database role used by the FastAPI API
-- so PostgreSQL Row-Level Security (RLS) is strictly enforced (no BYPASSRLS).
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ai_tracker_app') THEN
        CREATE ROLE ai_tracker_app LOGIN PASSWORD 'ai_tracker_app_dev_password' NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    END IF;
END
$$;

GRANT CONNECT ON DATABASE ai_usage_tracker TO ai_tracker_app;
GRANT USAGE ON SCHEMA public TO ai_tracker_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ai_tracker_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO ai_tracker_app;

