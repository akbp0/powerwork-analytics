"""Loads extracted raw records into source_db (raw.work_order_status_wide)."""
from __future__ import annotations

import json
import logging
import math
import uuid
from pathlib import Path

from psycopg import Connection

from etl.base import BaseLoader
from etl.extract.excel import RawRecord

logger = logging.getLogger(__name__)


def _sanitize_for_json(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, dict):
        return {key: _sanitize_for_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize_for_json(item) for item in value]
    return value


class SourceLoader(BaseLoader):
    """Owns the full lifecycle of one ETL batch against ``source_db``:
    starting it, loading raw/rejected rows, and closing it out."""

    def __init__(self, conn: Connection):
        self._conn = conn

    def start_batch(self, source_file: Path) -> uuid.UUID:
        batch_id = uuid.uuid4()
        with self._conn.cursor() as cur:
            cur.execute(
                "INSERT INTO raw.etl_batch (batch_id, source_file) VALUES (%s, %s)",
                (str(batch_id), str(source_file)),
            )
        return batch_id

    def finish_batch(self, batch_id: uuid.UUID, *, rows_extracted: int, rows_rejected: int,
                      status: str = "succeeded", error_message: str | None = None) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                UPDATE raw.etl_batch
                SET finished_at = now(), status = %s, rows_extracted = %s,
                    rows_rejected = %s, error_message = %s
                WHERE batch_id = %s
                """,
                (status, rows_extracted, rows_rejected, error_message, str(batch_id)),
            )

    def load_raw_records(self, batch_id: uuid.UUID, source_file: Path, records: list[RawRecord]) -> None:
        with self._conn.cursor() as cur:
            for rec in records:
                cur.execute(
                    """
                    INSERT INTO raw.work_order_status_wide
                        (batch_id, source_file, source_row_number, city_name,
                         business_unit_code, fiscal_year, fiscal_month,
                         category_columns, is_aggregate_row)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        str(batch_id), str(source_file), rec.source_row_number, rec.city_name,
                        rec.business_unit_code, rec.fiscal_year, rec.fiscal_month,
                        json.dumps(_sanitize_for_json(rec.category_columns), ensure_ascii=False, allow_nan=False),
                        rec.is_aggregate_row,
                    ),
                )
        logger.info("Loaded %d raw rows into raw.work_order_status_wide (batch=%s)", len(records), batch_id)

    def load_rejected_rows(self, batch_id: uuid.UUID, rejected: list[dict]) -> None:
        if not rejected:
            return
        with self._conn.cursor() as cur:
            for item in rejected:
                cur.execute(
                    """
                    INSERT INTO raw.rejected_rows (batch_id, source_row_number, raw_payload, reject_reason)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (str(batch_id), item.get("source_row_number"),
                     json.dumps(item.get("payload"), default=str, ensure_ascii=False), item["reason"]),
                )
        logger.warning("Logged %d rejected rows for batch=%s", len(rejected), batch_id)

    def load(self, batch_id: uuid.UUID, source_file: Path, records: list[RawRecord]) -> None:
        """Satisfies BaseLoader; delegates to load_raw_records for the
        common case of loading a fresh batch of raw rows."""
        self.load_raw_records(batch_id, source_file, records)
