# Architecture

## System Diagram

```text
data/raw/2016.xlsx
        |
        | ExcelExtractor
        v
source_db.raw
        |
        | SourceLoader + WorkOrderTransformer + WarehouseLoader
        v
warehouse_db.mart
        |
        | mart.v_* analytical views
        v
Flask-RESTX API
        |
        | nginx reverse proxy
        v
Dashboard
```

## Layer Responsibilities

| Layer | Responsibility |
|---|---|
| Excel source | Original input file, kept unchanged |
| `source_db.raw` | Raw rows, batch metadata, rejected rows |
| ETL | Extraction, validation, normalization, reconciliation, loading |
| `warehouse_db.mart` | Dimensions, facts, and query-oriented views |
| API | Read-only JSON endpoints and generated Swagger |
| nginx | Public entrypoint, static files, reverse proxy, compression, headers |
| Dashboard | KPIs, charts, filters, drill-down, quality panel |

## Why Two Databases

`source_db` stores what arrived from the source system. It is optimized for
traceability, lineage, and reprocessing.

`warehouse_db` stores what analytics should query. It is optimized for
read-heavy dashboard/API requests.

This separation prevents raw ingestion concerns from leaking into analytical
queries and keeps the API isolated from raw landing complexity.

## Backend Layering

```text
namespaces -> services -> repositories -> mart views
```

| Package | Role |
|---|---|
| `src/api/namespaces` | Flask-RESTX resources, request parsing, Swagger decorators |
| `src/api/services` | Business orchestration and response shaping |
| `src/api/repositories` | SQL access to warehouse views |
| `src/api/models` | DTO models for Swagger schemas |
| `src/api/extensions` | DB lifecycle and shared Flask-RESTX API object |

## Startup Flow

`docker-compose.yml` defines one stack. Startup is intentionally ordered:

```text
source-db and warehouse-db become healthy
etl runs and exits successfully
api starts and becomes healthy
nginx starts
```

If ETL fails, the API does not start. This prevents the dashboard from serving
against an empty or partially loaded warehouse.
