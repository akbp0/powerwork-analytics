# Overview

## Purpose

PowerWork Analytics turns a non-tabular Excel report into an auditable,
query-ready analytics product. The project covers the full path from raw data
inspection to a dashboard served behind nginx.

## End-to-End Flow

```text
Raw Excel workbook
  -> source PostgreSQL raw schema
  -> Python ETL transform
  -> warehouse PostgreSQL mart schema
  -> Flask-RESTX API
  -> nginx
  -> dashboard
```

## Implemented Features

- Raw Excel extraction from `data/raw/2016.xlsx`.
- Raw source database with batch tracking and rejected-row logging.
- Warehouse star schema with dimensions, facts, and reconciliation facts.
- Analytical SQL views for dashboard/API use cases.
- Class-based ETL pipeline with replaceable stages.
- Flask-RESTX API with generated Swagger documentation.
- Interactive dashboard using `/api/analytics/*`.
- nginx reverse proxy and static dashboard serving.
- Single Docker Compose stack with automatic ETL on startup.
- Tests for ETL transform behavior and API/Swagger generation.

## Repository Layout

```text
data/raw/           Source workbook
etl/                Extract, transform, and load pipeline
sql/source/         Raw source schema
sql/warehouse/      Warehouse DDL and analytical views
src/api/            Flask-RESTX app
dashboard/          Browser dashboard
nginx/              nginx configuration
scripts/            Deployment/operation helpers
docs/en/            English documentation
docs/fa/            Persian documentation
tests/              Unit and API tests
```

## Key URLs

| Purpose | URL |
|---|---|
| Dashboard | `http://localhost:8080/` |
| Swagger UI | `http://localhost:8080/api/docs/` |
| Health through nginx | `http://localhost:8080/health` |
| Direct API health | `http://localhost:5000/api/health` |

## Design Principles

- Keep raw data auditable.
- Make warehouse reads simple and fast.
- Keep SQL in repository classes and warehouse views.
- Generate API docs from the implementation.
- Make startup repeatable with Docker Compose.
- Use nginx as the only public entrypoint.
