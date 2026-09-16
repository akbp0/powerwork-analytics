"""
Analytical REST endpoints, all read-only against warehouse_db.

Endpoint          Purpose
----------------  -------------------------------------------------------
GET /filters      Dropdown/filter options for the dashboard (periods, cities, categories)
GET /kpis         Headline KPI cards for the latest period
GET /trend        Total open work orders per fiscal month (line chart)
GET /categories/breakdown   Open work orders per category (bar/pie chart)
GET /status/funnel          Open work orders per workflow stage (funnel chart)
GET /cities/ranking          Top cities by open work orders (bar chart / table)
GET /work-orders             Paginated, filterable fact-level detail table
GET /data-quality/reconciliation   Rows where source-reported totals don't match derived totals
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from api.extensions.db import get_db
from api.repositories.analytics_repository import AnalyticsRepository
from api.schemas.analytics import (
    CityRankingFilter,
    PeriodFilter,
    WorkOrderDetailFilter,
    parse_or_400,
)
from api.services.analytics_service import AnalyticsService

analytics_bp = Blueprint("analytics", __name__)


def _service() -> AnalyticsService:
    return AnalyticsService(AnalyticsRepository(get_db()))


@analytics_bp.get("/filters")
def get_filters():
    return jsonify(_service().get_filters())


@analytics_bp.get("/kpis")
def get_kpis():
    return jsonify(_service().get_kpis())


@analytics_bp.get("/trend")
def get_trend():
    return jsonify(_service().get_trend())


@analytics_bp.get("/categories/breakdown")
def get_category_breakdown():
    params, error = parse_or_400(PeriodFilter, request.args.to_dict())
    if error:
        return jsonify(error), 400
    return jsonify(_service().get_category_breakdown(params.period))


@analytics_bp.get("/status/funnel")
def get_status_funnel():
    params, error = parse_or_400(PeriodFilter, request.args.to_dict())
    if error:
        return jsonify(error), 400
    return jsonify(_service().get_status_funnel(params.period))


@analytics_bp.get("/cities/ranking")
def get_city_ranking():
    params, error = parse_or_400(CityRankingFilter, request.args.to_dict())
    if error:
        return jsonify(error), 400
    return jsonify(_service().get_city_ranking(params.period, params.limit))


@analytics_bp.get("/work-orders")
def get_work_orders():
    params, error = parse_or_400(WorkOrderDetailFilter, request.args.to_dict())
    if error:
        return jsonify(error), 400
    return jsonify(_service().get_work_order_detail(
        city=params.city, period=params.period, category=params.category,
        page=params.page, page_size=params.page_size,
    ))


@analytics_bp.get("/data-quality/reconciliation")
def get_reconciliation_report():
    return jsonify(_service().get_data_quality_report())


@analytics_bp.errorhandler(Exception)
def handle_unexpected_error(exc):
    return jsonify({"error": "internal_error", "message": str(exc)}), 500
