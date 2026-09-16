CREATE OR REPLACE VIEW mart.v_fact_detail AS
SELECT
    f.fact_id,
    c.city_key,
    c.city_name,
    c.business_unit_code,
    d.date_key,
    d.fiscal_year,
    d.fiscal_month,
    d.period_label,
    cat.category_key,
    cat.category_code,
    cat.category_name,
    s.status_key,
    s.status_code,
    s.status_name,
    s.stage_order,
    f.open_work_order_count
FROM mart.fact_work_order_status f
JOIN mart.dim_city c     ON c.city_key = f.city_key
JOIN mart.dim_date d     ON d.date_key = f.date_key
JOIN mart.dim_category cat ON cat.category_key = f.category_key
JOIN mart.dim_status s   ON s.status_key = f.status_key
WHERE c.is_company_total = FALSE;

CREATE OR REPLACE VIEW mart.v_kpi_summary AS
WITH latest_period AS (
    SELECT MAX(date_key) AS date_key FROM mart.fact_work_order_status
)
SELECT
    d.period_label,
    SUM(f.open_work_order_count) AS total_open_work_orders,
    COUNT(DISTINCT c.city_key)   AS active_cities,
    COUNT(DISTINCT cat.category_key) AS active_categories
FROM mart.fact_work_order_status f
JOIN latest_period lp ON lp.date_key = f.date_key
JOIN mart.dim_city c ON c.city_key = f.city_key AND c.is_company_total = FALSE
JOIN mart.dim_date d ON d.date_key = f.date_key
JOIN mart.dim_category cat ON cat.category_key = f.category_key
GROUP BY d.period_label;

CREATE OR REPLACE VIEW mart.v_monthly_trend AS
SELECT
    d.date_key,
    d.period_label,
    d.fiscal_year,
    d.fiscal_month,
    SUM(f.open_work_order_count) AS total_open_work_orders
FROM mart.fact_work_order_status f
JOIN mart.dim_date d ON d.date_key = f.date_key
JOIN mart.dim_city c ON c.city_key = f.city_key AND c.is_company_total = FALSE
GROUP BY d.date_key, d.period_label, d.fiscal_year, d.fiscal_month
ORDER BY d.date_key;

CREATE OR REPLACE VIEW mart.v_category_breakdown AS
SELECT
    d.date_key,
    d.period_label,
    cat.category_key,
    cat.category_code,
    cat.category_name,
    SUM(f.open_work_order_count) AS total_open_work_orders
FROM mart.fact_work_order_status f
JOIN mart.dim_date d ON d.date_key = f.date_key
JOIN mart.dim_category cat ON cat.category_key = f.category_key
JOIN mart.dim_city c ON c.city_key = f.city_key AND c.is_company_total = FALSE
GROUP BY d.date_key, d.period_label, cat.category_key, cat.category_code, cat.category_name;

CREATE OR REPLACE VIEW mart.v_status_funnel AS
SELECT
    d.date_key,
    d.period_label,
    s.status_key,
    s.status_code,
    s.status_name,
    s.stage_order,
    SUM(f.open_work_order_count) AS total_open_work_orders
FROM mart.fact_work_order_status f
JOIN mart.dim_date d ON d.date_key = f.date_key
JOIN mart.dim_status s ON s.status_key = f.status_key
JOIN mart.dim_city c ON c.city_key = f.city_key AND c.is_company_total = FALSE
GROUP BY d.date_key, d.period_label, s.status_key, s.status_code, s.status_name, s.stage_order;

CREATE OR REPLACE VIEW mart.v_city_ranking AS
SELECT
    d.date_key,
    d.period_label,
    c.city_key,
    c.city_name,
    c.business_unit_code,
    SUM(f.open_work_order_count) AS total_open_work_orders
FROM mart.fact_work_order_status f
JOIN mart.dim_date d ON d.date_key = f.date_key
JOIN mart.dim_city c ON c.city_key = f.city_key AND c.is_company_total = FALSE
GROUP BY d.date_key, d.period_label, c.city_key, c.city_name, c.business_unit_code;

CREATE OR REPLACE VIEW mart.v_reconciliation_mismatches AS
SELECT
    d.period_label,
    c.city_name,
    cat.category_name,
    r.reported_total,
    r.derived_total,
    (r.reported_total - r.derived_total) AS variance
FROM mart.fact_category_reconciliation r
JOIN mart.dim_city c ON c.city_key = r.city_key
JOIN mart.dim_date d ON d.date_key = r.date_key
JOIN mart.dim_category cat ON cat.category_key = r.category_key
WHERE r.is_reconciled = FALSE;
