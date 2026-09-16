from __future__ import annotations

from api.repositories.analytics_repository import AnalyticsRepository


class AnalyticsService:
    def __init__(self, repo: AnalyticsRepository):
        self._repo = repo

    def get_filters(self) -> dict:
        return {
            "periods": self._repo.list_periods(),
            "cities": self._repo.list_cities(),
            "categories": self._repo.list_categories(),
        }

    def get_kpis(self) -> dict:
        summary = self._repo.kpi_summary()
        return summary or {
            "period_label": None,
            "total_open_work_orders": 0,
            "active_cities": 0,
            "active_categories": 0,
        }

    def get_trend(self) -> list[dict]:
        return self._repo.monthly_trend()

    def get_category_breakdown(self, period: str | None) -> list[dict]:
        return self._repo.category_breakdown(period)

    def get_status_funnel(self, period: str | None) -> list[dict]:
        return self._repo.status_funnel(period)

    def get_city_ranking(self, period: str | None, limit: int) -> list[dict]:
        return self._repo.city_ranking(period, limit)

    def get_work_order_detail(self, *, city: str | None, period: str | None,
                               category: str | None, page: int, page_size: int) -> dict:
        rows, total = self._repo.work_order_detail(
            city_name=city, period_label=period, category_code=category,
            page=page, page_size=page_size,
        )
        return {
            "items": rows,
            "page": page,
            "page_size": page_size,
            "total_items": total,
            "total_pages": max(1, -(-total // page_size)),
        }

    def get_data_quality_report(self) -> dict:
        mismatches = self._repo.reconciliation_mismatches()
        return {"mismatch_count": len(mismatches), "mismatches": mismatches}
