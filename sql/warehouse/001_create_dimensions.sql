CREATE SCHEMA IF NOT EXISTS mart;

CREATE TABLE IF NOT EXISTS mart.dim_city (
    city_key            SERIAL PRIMARY KEY,
    city_name           TEXT NOT NULL,
    business_unit_code  TEXT NOT NULL,
    is_company_total    BOOLEAN NOT NULL DEFAULT FALSE,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_dim_city_code UNIQUE (business_unit_code)
);

CREATE TABLE IF NOT EXISTS mart.dim_date (
    date_key            INTEGER PRIMARY KEY,
    fiscal_year         SMALLINT NOT NULL,
    fiscal_month        SMALLINT NOT NULL CHECK (fiscal_month BETWEEN 1 AND 12),
    period_label        TEXT NOT NULL,
    gregorian_month_start DATE,
    CONSTRAINT uq_dim_date_period UNIQUE (fiscal_year, fiscal_month)
);

CREATE TABLE IF NOT EXISTS mart.dim_category (
    category_key        SERIAL PRIMARY KEY,
    category_code        TEXT NOT NULL,
    category_name        TEXT NOT NULL,
    display_order         SMALLINT NOT NULL,
    CONSTRAINT uq_dim_category_code UNIQUE (category_code)
);

CREATE TABLE IF NOT EXISTS mart.dim_status (
    status_key          SERIAL PRIMARY KEY,
    status_code          TEXT NOT NULL,
    status_name           TEXT NOT NULL,
    stage_order            SMALLINT NOT NULL,
    CONSTRAINT uq_dim_status_code UNIQUE (status_code)
);

INSERT INTO mart.dim_status (status_code, status_name, stage_order) VALUES
    ('IN_PROGRESS',        'در دست اجرا',              1),
    ('STATEMENT_DRAFTED',  'تهیه صورت وضعیت',          2),
    ('WITH_CONSULTANT',    'صورت وضعیت نزد مشاور',      3),
    ('WITH_HQ',            'صورت وضعیت نزد ستاد',      4),
    ('WITH_FINANCE',       'صورت وضعیت نزد مالی',      5)
ON CONFLICT (status_code) DO NOTHING;
