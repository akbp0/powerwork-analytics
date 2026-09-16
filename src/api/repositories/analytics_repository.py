from __future__ import annotations

from abc import ABC, abstractmethod

from psycopg import Connection
from psycopg.rows import dict_row


class BaseRepository(ABC):
    """Common contract for repositories that own a single psycopg connection.
    """

    def __init__(self, conn: Connection):
        self._conn = conn

    def _query(self, sql: str, params: tuple = ()) -> list[dict]:
        with self._conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    @property
    @abstractmethod
    def schema(self) -> str:
        """The Postgres schema this repository reads from."""


class AnalyticsRepository(BaseRepository):
    """Read-only access to the ``mart`` analytical views."""

    schema = "mart"

    def list_periods(self) -> list[dict]:
        return self._query(
            "SELECT date_key, period_label, fiscal_year, fiscal_month "
            "FROM mart.dim_date ORDER BY date_key"
        )

    def list_cities(self) -> list[dict]:
        return self._query(
            "SELECT city_key, city_name, business_unit_code "
            "FROM mart.dim_city WHERE is_company_total = FALSE ORDER BY city_name"
        )

    def list_categories(self) -> list[dict]:
        return self._query(
            "SELECT category_key, category_code, category_name "
            "FROM mart.dim_category WHERE category_code <> 'CAT_GRAND_TOTAL' ORDER BY display_order"
        )

    def kpi_summary(self) -> dict | None:
        rows = self._query(
            "SELECT * FROM mart.v_kpi_summary ORDER BY period_label DESC LIMIT 1"
        )
        return rows[0] if rows else None

    def monthly_trend(self) -> list[dict]:
        return self._query("SELECT * FROM mart.v_monthly_trend ORDER BY date_key")

    def category_breakdown(self, period_label: str | None = None) -> list[dict]:
        if period_label:
            return self._query(
                "SELECT * FROM mart.v_category_breakdown WHERE period_label = %s "
                "ORDER BY total_open_work_orders DESC",
                (period_label,),
            )
        return self._query("SELECT * FROM mart.v_category_breakdown ORDER BY period_label, category_key")

    def status_funnel(self, period_label: str | None = None) -> list[dict]:
        if period_label:
            return self._query(
                "SELECT * FROM mart.v_status_funnel WHERE period_label = %s ORDER BY stage_order",
                (period_label,),
            )
        return self._query("SELECT * FROM mart.v_status_funnel ORDER BY period_label, stage_order")

    def city_ranking(self, period_label: str | None = None, limit: int = 20) -> list[dict]:
        if period_label:
            return self._query(
                "SELECT * FROM mart.v_city_ranking WHERE period_label = %s "
                "ORDER BY total_open_work_orders DESC LIMIT %s",
                (period_label, limit),
            )
        return self._query(
            "SELECT * FROM mart.v_city_ranking ORDER BY period_label, total_open_work_orders DESC LIMIT %s",
            (limit,),
        )

    def work_order_detail(self, *, city_name: str | None, period_label: str | None,
                           category_code: str | None, page: int, page_size: int) -> tuple[list[dict], int]:
        filters, params = [], []
        if city_name:
            filters.append("city_name = %s")
            params.append(city_name)
        if period_label:
            filters.append("period_label = %s")
            params.append(period_label)
        if category_code:
            filters.append("category_code = %s")
            params.append(category_code)
        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

        total = self._query(f"SELECT COUNT(*) AS n FROM mart.v_fact_detail {where_clause}", tuple(params))[0]["n"]
        rows = self._query(
            f"SELECT * FROM mart.v_fact_detail {where_clause} "
            "ORDER BY period_label, city_name, category_code, stage_order "
            "LIMIT %s OFFSET %s",
            tuple(params) + (page_size, (page - 1) * page_size),
        )
        return rows, total

    def reconciliation_mismatches(self) -> list[dict]:
        return self._query(
            "SELECT * FROM mart.v_reconciliation_mismatches ORDER BY period_label, city_name"
        )
