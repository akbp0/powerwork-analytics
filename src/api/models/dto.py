from __future__ import annotations

from flask_restx import fields

from api.extensions.restx import api


class FilterDTO:
    period = api.model("Period", {
        "date_key": fields.Integer(description="YYYYMM-style fiscal period key", example=140109),
        "period_label": fields.String(description="Display label, e.g. '1401-09'", example="1401-09"),
        "fiscal_year": fields.Integer(description="Fiscal year number", example=1401),
        "fiscal_month": fields.Integer(description="Fiscal month number", example=9),
    })

    city = api.model("City", {
        "city_key": fields.Integer(description="Internal city identifier", example=42),
        "city_name": fields.String(description="Human-readable city name", example="Tehran"),
        "business_unit_code": fields.String(description="Business unit code", example="BU_1"),
    })

    category = api.model("Category", {
        "category_key": fields.Integer(description="Internal category id", example=5),
        "category_code": fields.String(description="Stable category code", example="CAT_5"),
        "category_name": fields.String(description="Category display name", example="Electrical"),
    })

    filters = api.model("Filters", {
        "periods": fields.List(fields.Nested(period), description="Available fiscal periods for filtering"),
        "cities": fields.List(fields.Nested(city), description="Available cities to filter by"),
        "categories": fields.List(fields.Nested(category), description="Available categories to filter by"),
    })


class KpiDTO:
    summary = api.model("KpiSummary", {
        "period_label": fields.String(allow_null=True, description="Period label the KPIs relate to", example="1401-09"),
        "total_open_work_orders": fields.Integer(description="Total open work orders in period", example=12345),
        "active_cities": fields.Integer(description="Number of cities with open work orders", example=87),
        "active_categories": fields.Integer(description="Number of categories with open work orders", example=12),
    })


class TrendDTO:
    point = api.model("TrendPoint", {
        "date_key": fields.Integer(description="YYYYMM period key", example=140109),
        "period_label": fields.String(description="Display label", example="1401-09"),
        "fiscal_year": fields.Integer(description="Fiscal year", example=1401),
        "fiscal_month": fields.Integer(description="Fiscal month", example=9),
        "total_open_work_orders": fields.Integer(description="Open work orders in this point", example=2300),
    })


class CategoryBreakdownDTO:
    item = api.model("CategoryBreakdownItem", {
        "date_key": fields.Integer(description="YYYYMM period key", example=140109),
        "period_label": fields.String(description="Display label", example="1401-09"),
        "category_key": fields.Integer(description="Internal category id", example=5),
        "category_code": fields.String(description="Stable category code", example="CAT_5"),
        "category_name": fields.String(description="Category display name", example="Electrical"),
        "total_open_work_orders": fields.Integer(description="Open work orders for this category", example=400),
    })


class StatusFunnelDTO:
    item = api.model("StatusFunnelItem", {
        "date_key": fields.Integer(description="YYYYMM period key", example=140109),
        "period_label": fields.String(description="Display label", example="1401-09"),
        "status_key": fields.Integer(description="Status id", example=2),
        "status_code": fields.String(description="Stable status code", example="IN_PROGRESS"),
        "status_name": fields.String(description="Human readable status name", example="In progress"),
        "stage_order": fields.Integer(description="Order in funnel visualization", example=2),
        "total_open_work_orders": fields.Integer(description="Count in this stage", example=1000),
    })


class CityRankingDTO:
    item = api.model("CityRankingItem", {
        "date_key": fields.Integer(description="YYYYMM period key", example=140109),
        "period_label": fields.String(description="Display label", example="1401-09"),
        "city_key": fields.Integer(description="Internal city id", example=42),
        "city_name": fields.String(description="City display name", example="Tehran"),
        "business_unit_code": fields.String(description="Business unit code", example="BU_1"),
        "total_open_work_orders": fields.Integer(description="Count for ranking", example=5300),
    })


class WorkOrderDTO:
    item = api.model("WorkOrderDetailItem", {
        "fact_id": fields.Integer(description="Fact table row id", example=987654),
        "city_key": fields.Integer(description="City id", example=42),
        "city_name": fields.String(description="City name", example="Tehran"),
        "business_unit_code": fields.String(description="Business unit code", example="BU_1"),
        "date_key": fields.Integer(description="YYYYMM period key", example=140109),
        "fiscal_year": fields.Integer(description="Fiscal year", example=1401),
        "fiscal_month": fields.Integer(description="Fiscal month", example=9),
        "period_label": fields.String(description="Display label", example="1401-09"),
        "category_key": fields.Integer(description="Category id", example=5),
        "category_code": fields.String(description="Category code", example="CAT_5"),
        "category_name": fields.String(description="Category name", example="Electrical"),
        "status_key": fields.Integer(description="Status id", example=2),
        "status_code": fields.String(description="Status code", example="IN_PROGRESS"),
        "status_name": fields.String(description="Status name", example="In progress"),
        "stage_order": fields.Integer(description="Stage order", example=2),
        "open_work_order_count": fields.Integer(description="Number of open work orders in this row", example=1),
    })

    page = api.model("WorkOrderPage", {
        "items": fields.List(fields.Nested(item), description="Page items"),
        "page": fields.Integer(description="Current page number", example=1),
        "page_size": fields.Integer(description="Rows per page", example=50),
        "total_items": fields.Integer(description="Total matching rows", example=1234),
        "total_pages": fields.Integer(description="Total pages available", example=25),
    })


class ReconciliationDTO:
    mismatch = api.model("ReconciliationMismatch", {
        "period_label": fields.String(description="Period label", example="1401-09"),
        "city_name": fields.String(description="City name", example="Tehran"),
        "category_name": fields.String(description="Category name", example="Electrical"),
        "reported_total": fields.Integer(description="Total reported by source", example=100),
        "derived_total": fields.Integer(description="Computed derived total", example=98),
        "variance": fields.Integer(description="Difference between reported and derived", example=2),
    })

    report = api.model("ReconciliationReport", {
        "mismatch_count": fields.Integer(description="Number of mismatching rows", example=3),
        "mismatches": fields.List(fields.Nested(mismatch), description="List of mismatching rows"),
    })


class ErrorDTO:
    """Standardized error response model used across the API so clients can
    rely on a stable error shape and the Swagger UI documents expected errors.
    """
    error = api.model("Error", {
        "code": fields.String(description="Machine-readable error code", example="invalid_request"),
        "message": fields.String(description="Human-readable error message", example="Invalid request parameters"),
        "details": fields.List(fields.Raw, description="Optional list of detailed error objects", example=[{"loc": ["period"], "msg": "period must match YYYY-MM"}]),
    })


class HealthDTO:
    status = api.model("HealthStatus", {
        "status": fields.String(example="ok", description="Service health status"),
    })
