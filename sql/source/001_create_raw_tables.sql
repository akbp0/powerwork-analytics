-- ============================================================================
-- SOURCE DATABASE (source_db)
-- Purpose: landing zone for raw operational exports (Excel/CSV) with the
-- re-runnable (idempotent re-processing, full lineage back to the file).
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.work_order_status_wide (
    raw_id              BIGSERIAL PRIMARY KEY,
    batch_id            UUID NOT NULL,
    source_file         TEXT NOT NULL,
    source_sheet        TEXT NOT NULL DEFAULT 'Sheet1',
    source_row_number   INTEGER NOT NULL,

    city_name           TEXT,
    business_unit_code  TEXT,
    fiscal_year         TEXT,
    fiscal_month        TEXT,

    category_columns    JSONB NOT NULL,

    is_aggregate_row     BOOLEAN NOT NULL DEFAULT FALSE,

    loaded_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_raw_wows_batch ON raw.work_order_status_wide (batch_id);
CREATE INDEX IF NOT EXISTS ix_raw_wows_city_period
    ON raw.work_order_status_wide (city_name, fiscal_year, fiscal_month);

CREATE TABLE IF NOT EXISTS raw.etl_batch (
    batch_id        UUID PRIMARY KEY,
    source_file     TEXT NOT NULL,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at     TIMESTAMPTZ,
    status          TEXT NOT NULL DEFAULT 'running'
                        CHECK (status IN ('running', 'succeeded', 'failed')),
    rows_extracted  INTEGER,
    rows_rejected   INTEGER,
    error_message   TEXT
);

CREATE TABLE IF NOT EXISTS raw.rejected_rows (
    rejected_id     BIGSERIAL PRIMARY KEY,
    batch_id        UUID NOT NULL REFERENCES raw.etl_batch (batch_id),
    source_row_number INTEGER,
    raw_payload     JSONB,
    reject_reason   TEXT NOT NULL,
    rejected_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
