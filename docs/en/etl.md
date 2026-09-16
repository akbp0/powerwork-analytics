# ETL

## Purpose

The ETL converts the workbook into warehouse-ready analytical records while
preserving raw lineage and rejected-row diagnostics.

## Stages

| Stage | Class | File | Responsibility |
|---|---|---|---|
| Extract | `ExcelExtractor` | `etl/extract/excel.py` | Parse workbook rows and category blocks |
| Raw load | `SourceLoader` | `etl/load/source.py` | Store raw rows, batch metadata, rejected rows |
| Transform | `WorkOrderTransformer` | `etl/transform/pipeline.py` | Validate, normalize, create dimensions/facts |
| Warehouse load | `WarehouseLoader` | `etl/load/warehouse.py` | Upsert dimensions, facts, reconciliation rows |
| Orchestration | `ETLPipeline` | `etl/run_etl.py` | Run stages in order |

## Automatic Startup Execution

ETL is a normal service in `docker-compose.yml`. It runs after both databases
are healthy:

```text
source-db + warehouse-db -> etl -> api -> nginx
```

The API depends on:

```yaml
etl:
  condition: service_completed_successfully
```

This means the API will not start if the load fails.

## Manual Execution

Inside Docker:

```bash
docker compose run --rm etl
```

Locally:

```bash
pip install -r requirements.txt
python -m etl.run_etl --file data/raw/2016.xlsx
```

## Idempotency

The ETL is safe to rerun:

- Dimensions upsert on stable business keys.
- Facts upsert on the full grain key.
- Reconciliation rows are updated for the same grain.
- Rejected rows are associated with the ETL batch.

## Failure Handling

- Extraction/transform/load failures make the ETL command exit non-zero.
- Source batch metadata records failed loads where possible.
- Invalid rows are not silently dropped; they are recorded in
  `raw.rejected_rows`.
