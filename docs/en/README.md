# PowerWork Analytics Documentation

PowerWork Analytics is an end-to-end analytics platform for a work-order
reporting dataset. It ingests a human-formatted Excel workbook, stores raw
lineage in PostgreSQL, transforms the data through an idempotent ETL pipeline,
loads a dimensional warehouse, exposes read-only analytical endpoints through
Flask-RESTX, and serves a dashboard through nginx.

## Documentation Index

| Document | Purpose |
|---|---|
| `overview.md` | Project scope, features, flow, and repository layout |
| `architecture.md` | System architecture, backend layering, and startup flow |
| `data-model.md` | Source profiling, quality findings, warehouse schema, views |
| `etl.md` | ETL stages, idempotency, error handling, and manual execution |
| `api.md` | API endpoints, parameters, examples, and Swagger docs |
| `dashboard.md` | Dashboard panels, API usage, and runtime behavior |
| `deployment.md` | Docker Compose, nginx, environment variables, and operations |

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

Startup order:

```text
source-db + warehouse-db -> etl -> api -> nginx
```

The ETL runs automatically during startup and loads `data/raw/2016.xlsx`
before the API starts.

Open:

- Dashboard: `http://localhost:8080/`
- Swagger: `http://localhost:8080/api/docs/`
- Health: `http://localhost:8080/health`
- Direct API debug endpoint: `http://localhost:5000/api/health`

## Main Runtime Components

| Component | Technology | Role |
|---|---|---|
| `source-db` | PostgreSQL 17 | Raw landing database |
| `warehouse-db` | PostgreSQL 17 | Dimensional analytical warehouse |
| `etl` | Python | Startup data load from Excel to source and warehouse |
| `api` | Flask-RESTX + Gunicorn | Read-only analytics API and Swagger |
| `nginx` | nginx Alpine | Public edge, dashboard static server, API reverse proxy |

## Current Data Result

Running the ETL against `data/raw/2016.xlsx` produces:

- 54 raw source rows.
- 3 rejected rows.
- 1,632 fact rows.
- 357 reconciliation rows.
- 21 reconciliation mismatches surfaced for review.

## Useful Commands

```bash
docker compose up --build
docker compose ps
docker compose logs -f etl
docker compose logs -f api
docker compose run --rm etl
docker compose down
```

For full operational details, see `deployment.md`.
