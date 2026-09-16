from __future__ import annotations

import logging
import uuid

from psycopg import Connection

from etl.base import BaseLoader
from etl.transform.pipeline import TransformResult

logger = logging.getLogger(__name__)


class WarehouseLoader(BaseLoader):
    """Upserts one transformed batch's dimensions and facts into ``mart``."""

    def __init__(self, conn: Connection):
        self._conn = conn

    def load(self, result: TransformResult, batch_id: uuid.UUID) -> None:
        city_keys = self._upsert_cities(result)
        date_keys = self._upsert_dates(result)
        category_keys = self._upsert_categories(result)
        status_keys = self._get_status_keys()

        with self._conn.cursor() as cur:
            for fact in result.facts:
                status_key = status_keys.get(fact.status_code)
                if status_key is None:
                    # Unrecognized status label — log and skip rather than fail the whole batch.
                    logger.warning("Unknown status_code %r; skipping fact row", fact.status_code)
                    continue
                cur.execute(
                    """
                    INSERT INTO mart.fact_work_order_status
                        (city_key, date_key, category_key, status_key, open_work_order_count, batch_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (city_key, date_key, category_key, status_key) DO UPDATE
                        SET open_work_order_count = EXCLUDED.open_work_order_count,
                            batch_id = EXCLUDED.batch_id,
                            loaded_at = now()
                    """,
                    (
                        city_keys[fact.city_name], date_keys[fact.date_key],
                        category_keys[fact.category_code], status_key,
                        fact.open_work_order_count, str(batch_id),
                    ),
                )

            for rec in result.reconciliations:
                cur.execute(
                    """
                    INSERT INTO mart.fact_category_reconciliation
                        (city_key, date_key, category_key, reported_total, derived_total, batch_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (city_key, date_key, category_key) DO UPDATE
                        SET reported_total = EXCLUDED.reported_total,
                            derived_total = EXCLUDED.derived_total,
                            batch_id = EXCLUDED.batch_id,
                            loaded_at = now()
                    """,
                    (
                        city_keys[rec.city_name], date_keys[rec.date_key],
                        category_keys[rec.category_code], rec.reported_total,
                        rec.derived_total, str(batch_id),
                    ),
                )

        logger.info(
            "Warehouse load complete: %d facts, %d reconciliation rows (batch=%s)",
            len(result.facts), len(result.reconciliations), batch_id,
        )

    # -- internals ----------------------------------------------------------

    def _upsert_cities(self, result: TransformResult) -> dict[str, int]:
        city_keys: dict[str, int] = {}
        with self._conn.cursor() as cur:
            for city in result.dim_cities:
                cur.execute(
                    """
                    INSERT INTO mart.dim_city (city_name, business_unit_code, is_company_total)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (business_unit_code) DO UPDATE
                        SET city_name = EXCLUDED.city_name,
                            is_company_total = EXCLUDED.is_company_total,
                            updated_at = now()
                    RETURNING city_key
                    """,
                    (city.city_name, city.business_unit_code, city.is_company_total),
                )
                city_keys[city.city_name] = cur.fetchone()[0]
        return city_keys

    def _upsert_dates(self, result: TransformResult) -> dict[int, int]:
        date_keys: dict[int, int] = {}
        with self._conn.cursor() as cur:
            for d in result.dim_dates:
                cur.execute(
                    """
                    INSERT INTO mart.dim_date (date_key, fiscal_year, fiscal_month, period_label)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (date_key) DO NOTHING
                    RETURNING date_key
                    """,
                    (d.date_key, d.fiscal_year, d.fiscal_month, d.period_label),
                )
                row = cur.fetchone()
                date_keys[d.date_key] = row[0] if row else d.date_key
        return date_keys

    def _upsert_categories(self, result: TransformResult) -> dict[str, int]:
        category_keys: dict[str, int] = {}
        with self._conn.cursor() as cur:
            for cat in result.dim_categories:
                cur.execute(
                    """
                    INSERT INTO mart.dim_category (category_code, category_name, display_order)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (category_code) DO UPDATE
                        SET category_name = EXCLUDED.category_name
                    RETURNING category_key
                    """,
                    (cat.category_code, cat.category_name, cat.display_order),
                )
                category_keys[cat.category_code] = cur.fetchone()[0]
        return category_keys

    def _get_status_keys(self) -> dict[str, int]:
        with self._conn.cursor() as cur:
            cur.execute("SELECT status_code, status_key FROM mart.dim_status")
            return dict(cur.fetchall())
