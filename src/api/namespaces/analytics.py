from __future__ import annotations

import re

from flask_restx import Namespace, reqparse

from api.models.dto import (
    CategoryBreakdownDTO,
    CityRankingDTO,
    FilterDTO,
    KpiDTO,
    ReconciliationDTO,
    StatusFunnelDTO,
    TrendDTO,
    WorkOrderDTO,
)
from api.namespaces.base import BaseAnalyticsResource

analytics_ns = Namespace(
    "analytics",
    description="Read-only analytical endpoints over the warehouse's mart schema",
    path="/analytics",
)

_PERIOD_PATTERN = re.compile(r"^\d{4}-\d{2}$")
_PERIOD_HELP = "Fiscal period filter, format YYYY-MM (e.g. 1401-09). Omit for all periods."


def _clean_period(namespace: Namespace, value: str | None) -> str | None:
    """Shared period-format validation, mirroring the old pydantic
    ``pattern=r"^\\d{4}-\\d{2}$"`` constraint but surfaced through
    Flask-RESTX's own ``abort`` so it shows up in the Swagger error docs."""
    if value and not _PERIOD_PATTERN.match(value):
        namespace.abort(400, "invalid_request", details=[
            {"loc": ["period"], "msg": "period must match YYYY-MM"}
        ])
    return value


# --------------------------------------------------------------------------
# Request parsers — these double as the Swagger "Parameters" section for
# each endpoint, so the docs and the validation can never drift apart.
# --------------------------------------------------------------------------

period_parser = reqparse.RequestParser()
period_parser.add_argument("period", type=str, location="args", required=False, help=_PERIOD_HELP)

city_ranking_parser = period_parser.copy()
city_ranking_parser.add_argument(
    "limit", type=int, location="args", required=False, default=20,
    help="Max rows to return (1-200, default 20)",
)

work_order_parser = reqparse.RequestParser()
work_order_parser.add_argument("city", type=str, location="args", required=False,
                                help="Exact city name to filter by")
work_order_parser.add_argument("period", type=str, location="args", required=False, help=_PERIOD_HELP)
work_order_parser.add_argument("category", type=str, location="args", required=False,
                                help="category_code to filter by, e.g. CAT_5")
work_order_parser.add_argument("page", type=int, location="args", required=False, default=1,
                                help="1-based page number")
work_order_parser.add_argument("page_size", type=int, location="args", required=False, default=50,
                                help="Rows per page (1-500, default 50)")


@analytics_ns.route("/filters")
class FiltersResource(BaseAnalyticsResource):
    """Dropdown/filter options consumed by the dashboard."""

    @analytics_ns.doc(summary="List available filter options")
    @analytics_ns.marshal_with(FilterDTO.filters)
    def get(self):
        return self.service.get_filters()


@analytics_ns.route("/kpis")
class KpisResource(BaseAnalyticsResource):
    """Headline KPI cards for the latest available fiscal period."""

    @analytics_ns.doc(summary="Get headline KPIs for the latest period")
    @analytics_ns.marshal_with(KpiDTO.summary)
    def get(self):
        return self.service.get_kpis()


@analytics_ns.route("/trend")
class TrendResource(BaseAnalyticsResource):
    """Total open work orders per fiscal month, for the trend line chart."""

    @analytics_ns.doc(summary="Get the monthly open-work-order trend")
    @analytics_ns.marshal_list_with(TrendDTO.point)
    def get(self):
        return self.service.get_trend()


@analytics_ns.route("/categories/breakdown")
class CategoryBreakdownResource(BaseAnalyticsResource):
    """Open work orders per category, optionally scoped to one fiscal period."""

    @analytics_ns.doc(summary="Get open work orders broken down by category")
    @analytics_ns.expect(period_parser)
    @analytics_ns.marshal_list_with(CategoryBreakdownDTO.item)
    def get(self):
        args = period_parser.parse_args()
        period = _clean_period(analytics_ns, args["period"])
        return self.service.get_category_breakdown(period)


@analytics_ns.route("/status/funnel")
class StatusFunnelResource(BaseAnalyticsResource):
    """Open work orders per workflow stage, for the funnel chart."""

    @analytics_ns.doc(summary="Get the workflow-stage funnel")
    @analytics_ns.expect(period_parser)
    @analytics_ns.marshal_list_with(StatusFunnelDTO.item)
    def get(self):
        args = period_parser.parse_args()
        period = _clean_period(analytics_ns, args["period"])
        return self.service.get_status_funnel(period)


@analytics_ns.route("/cities/ranking")
class CityRankingResource(BaseAnalyticsResource):
    """Top cities ranked by open work orders."""

    @analytics_ns.doc(summary="Rank cities by open work orders")
    @analytics_ns.expect(city_ranking_parser)
    @analytics_ns.marshal_list_with(CityRankingDTO.item)
    def get(self):
        args = city_ranking_parser.parse_args()
        period = _clean_period(analytics_ns, args["period"])
        limit = max(1, min(args["limit"] or 20, 200))
        return self.service.get_city_ranking(period, limit)


@analytics_ns.route("/work-orders")
class WorkOrdersResource(BaseAnalyticsResource):
    """Paginated, filterable fact-level detail table backing the drill-down."""

    @analytics_ns.doc(summary="List work-order detail rows (paginated)")
    @analytics_ns.expect(work_order_parser)
    @analytics_ns.marshal_with(WorkOrderDTO.page)
    def get(self):
        args = work_order_parser.parse_args()
        period = _clean_period(analytics_ns, args["period"])
        page = max(1, args["page"] or 1)
        page_size = max(1, min(args["page_size"] or 50, 500))
        return self.service.get_work_order_detail(
            city=args["city"], period=period, category=args["category"],
            page=page, page_size=page_size,
        )


@analytics_ns.route("/data-quality/reconciliation")
class ReconciliationResource(BaseAnalyticsResource):
    """Rows where the source's own reported category total didn't match the
    sum of its status columns."""

    @analytics_ns.doc(summary="Get data-quality reconciliation mismatches")
    @analytics_ns.marshal_with(ReconciliationDTO.report)
    def get(self):
        return self.service.get_data_quality_report()
