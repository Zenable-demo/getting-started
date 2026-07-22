-- Initial schema: events table, kv_store table, guardrail_findings table

CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    data TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS kv_store (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS guardrail_findings (
    id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    pattern_name VARCHAR(255) NOT NULL,
    line_content TEXT,
    scanned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
