"""
Orchestrates one end-to-end ETL run via the ``ETLPipeline`` class:

  1. Extract  -> ExcelExtractor parses the Excel export into RawRecord objects
  2. Load     -> SourceLoader persists raw records into source_db (full lineage, batch-tracked)
  3. Transform-> WorkOrderTransformer cleans/validates/reshapes into dimension + fact rows
  4. Load     -> WarehouseLoader upserts into warehouse_db (mart schema)

Usage:
    python -m etl.run_etl --file data/raw/2016.xlsx

Exit code is non-zero on failure so this composes cleanly with cron/Airflow/
CI schedulers.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from etl.common.db import get_connection
from etl.extract.excel import ExcelExtractor
from etl.load.source import SourceLoader
from etl.load.warehouse import WarehouseLoader
from etl.transform.pipeline import WorkOrderTransformer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("etl.run_etl")


class ETLPipeline:

    def __init__(self,
                 extractor: ExcelExtractor | None = None,
                 transformer: WorkOrderTransformer | None = None):
        self._extractor = extractor or ExcelExtractor()
        self._transformer = transformer or WorkOrderTransformer()

    def run(self, file_path: Path) -> None:
        load_dotenv()

        logger.info("Extracting %s", file_path)
        records = self._extractor.extract(file_path)
        logger.info("Extracted %d raw rows", len(records))

        with get_connection("SOURCE_DATABASE_URL") as source_conn:
            source_loader = SourceLoader(source_conn)
            batch_id = source_loader.start_batch(file_path)
            try:
                source_loader.load_raw_records(batch_id, file_path, records)
            except Exception as exc:  # noqa: BLE001 - top-level batch guard, re-raised after bookkeeping
                source_loader.finish_batch(batch_id, rows_extracted=len(records),
                                            rows_rejected=0, status="failed", error_message=str(exc))
                raise

            logger.info("Transforming raw records")
            result = self._transformer.transform(records)
            logger.info(
                "Transformed: %d cities, %d periods, %d categories, %d facts, %d reconciliation rows, %d rejected",
                len(result.dim_cities), len(result.dim_dates), len(result.dim_categories),
                len(result.facts), len(result.reconciliations), len(result.rejected),
            )
            source_loader.load_rejected_rows(batch_id, result.rejected)
            source_loader.finish_batch(
                batch_id, rows_extracted=len(records), rows_rejected=len(result.rejected),
            )

        with get_connection("WAREHOUSE_DATABASE_URL") as warehouse_conn:
            WarehouseLoader(warehouse_conn).load(result, batch_id)

        logger.info("ETL run complete (batch=%s)", batch_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the PowerWork Analytics ETL pipeline")
    parser.add_argument("--file", type=Path, default=Path("data/raw/2016.xlsx"),
                         help="Path to the raw Excel export")
    args = parser.parse_args()

    try:
        ETLPipeline().run(args.file)
    except Exception:
        logger.exception("ETL run failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
