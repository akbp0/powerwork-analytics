# Data Model

## Source Workbook

`data/raw/2016.xlsx` is a formatted report, not a clean flat table.

| Workbook area | Meaning |
|---|---|
| Row 0 | Report title, merged across columns |
| Row 1 | Group headers: 7 categories plus one grand-total block |
| Row 2 | Status labels inside each category |
| Rows 3+ | 54 data rows across fiscal months 7, 8, and 9 of year 1401 |

Each month includes 16 operating units and two aggregate rows:

- `جمع به تفکیک هر واحد`
- `کل شرکت`, business unit code `9999`

## Data Quality Findings

| Finding | Risk | Handling |
|---|---|---|
| Aggregate rows embedded in data | Double-counting city analytics | Flagged with `dim_city.is_company_total`; excluded from per-city views |
| Missing fiscal period on some rows | Cannot assign row to time | Rejected and logged |
| Variable category block width | Fixed raw columns would break | Raw category cells stored as JSONB |
| Reported totals can mismatch derived totals | Source totals cannot be blindly trusted | Store reported and derived totals |
| Duplicate category labels | Label is not a stable key | Use stable `CAT_1` to `CAT_7` codes |
| Placeholder business names | Domain labels are not reliable | Use generic codes and dimensions |

## ETL Output for Sample File

| Metric | Value |
|---|---:|
| Raw rows | 54 |
| Rejected rows | 3 |
| Fact rows | 1,632 |
| Reconciliation rows | 357 |
| Reconciliation mismatches | 21 |

## Star Schema

```text
dim_city      dim_date       dim_category      dim_status
    \            |                |                 /
     \           |                |                /
      +----------+----------------+---------------+
                 |
       fact_work_order_status
```

Main fact grain:

```text
city x fiscal period x category x status
```

## Tables

| Table | Grain | Purpose |
|---|---|---|
| `mart.dim_city` | One row per unit/city | City and business-unit dimension |
| `mart.dim_date` | One row per fiscal month | Jalali fiscal period dimension |
| `mart.dim_category` | One row per category | Stable category codes and display labels |
| `mart.dim_status` | One row per workflow stage | Ordered status dimension |
| `mart.fact_work_order_status` | City x period x category x status | Main count measure |
| `mart.fact_category_reconciliation` | City x period x category | Reported vs derived totals |

## Views

| View | Consumer |
|---|---|
| `mart.v_kpi_summary` | KPI cards |
| `mart.v_monthly_trend` | Trend chart |
| `mart.v_category_breakdown` | Category comparison |
| `mart.v_status_funnel` | Workflow funnel |
| `mart.v_city_ranking` | City ranking |
| `mart.v_fact_detail` | Detail table |
| `mart.v_reconciliation_mismatches` | Data-quality panel |

DDL lives in `sql/warehouse/`.
