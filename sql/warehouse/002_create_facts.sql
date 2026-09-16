CREATE TABLE IF NOT EXISTS mart.fact_work_order_status (
    fact_id             BIGSERIAL PRIMARY KEY,
    city_key            INTEGER NOT NULL REFERENCES mart.dim_city (city_key),
    date_key            INTEGER NOT NULL REFERENCES mart.dim_date (date_key),
    category_key        INTEGER NOT NULL REFERENCES mart.dim_category (category_key),
    status_key          INTEGER NOT NULL REFERENCES mart.dim_status (status_key),

    open_work_order_count  INTEGER NOT NULL CHECK (open_work_order_count >= 0),

    batch_id            UUID NOT NULL,
    loaded_at           TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_fact_grain UNIQUE (city_key, date_key, category_key, status_key)
);

CREATE INDEX IF NOT EXISTS ix_fact_city      ON mart.fact_work_order_status (city_key);
CREATE INDEX IF NOT EXISTS ix_fact_date      ON mart.fact_work_order_status (date_key);
CREATE INDEX IF NOT EXISTS ix_fact_category  ON mart.fact_work_order_status (category_key);
CREATE INDEX IF NOT EXISTS ix_fact_status    ON mart.fact_work_order_status (status_key);
CREATE INDEX IF NOT EXISTS ix_fact_date_city ON mart.fact_work_order_status (date_key, city_key);

CREATE TABLE IF NOT EXISTS mart.fact_category_reconciliation (
    reconciliation_id   BIGSERIAL PRIMARY KEY,
    city_key            INTEGER NOT NULL REFERENCES mart.dim_city (city_key),
    date_key            INTEGER NOT NULL REFERENCES mart.dim_date (date_key),
    category_key        INTEGER NOT NULL REFERENCES mart.dim_category (category_key),

    reported_total       INTEGER NOT NULL,
    derived_total          INTEGER NOT NULL,
    is_reconciled           BOOLEAN GENERATED ALWAYS AS (reported_total = derived_total) STORED,

    batch_id            UUID NOT NULL,
    loaded_at           TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_reconciliation_grain UNIQUE (city_key, date_key, category_key)
);

CREATE INDEX IF NOT EXISTS ix_reconciliation_mismatch
    ON mart.fact_category_reconciliation (is_reconciled) WHERE is_reconciled = FALSE;
