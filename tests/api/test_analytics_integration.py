from __future__ import annotations


class TestHealth:
    def test_health_check_returns_ok(self, client):
        response = client.get("/api/health")

        assert response.status_code == 200
        assert response.get_json() == {"status": "ok"}


class TestFilters:
    def test_returns_periods_cities_and_categories(self, client, seeded):
        response = client.get("/api/analytics/filters")

        assert response.status_code == 200
        body = response.get_json()

        city_names = {c["city_name"] for c in body["cities"]}
        assert "Tehran" in city_names
        assert "کل شرکت" not in city_names  # aggregate rows are never a filter option

        period_labels = {p["period_label"] for p in body["periods"]}
        assert {"1401-08", "1401-09"}.issubset(period_labels)

        category_codes = {c["category_code"] for c in body["categories"]}
        assert "CAT_1" in category_codes

    def test_empty_database_returns_empty_lists(self, client, empty_db):
        response = client.get("/api/analytics/filters")

        assert response.status_code == 200
        assert response.get_json() == {"periods": [], "cities": [], "categories": []}


class TestKpis:
    def test_returns_latest_period_totals(self, client, seeded):
        response = client.get("/api/analytics/kpis")

        assert response.status_code == 200
        body = response.get_json()
        assert body["period_label"] == "1401-09"
        assert body["total_open_work_orders"] == 15
        assert body["active_cities"] == 1
        assert body["active_categories"] == 1

    def test_empty_database_returns_zeroed_defaults(self, client, empty_db):
        response = client.get("/api/analytics/kpis")

        assert response.status_code == 200
        assert response.get_json() == {
            "period_label": None,
            "total_open_work_orders": 0,
            "active_cities": 0,
            "active_categories": 0,
        }


class TestTrend:
    def test_returns_points_ordered_by_period(self, client, seeded):
        response = client.get("/api/analytics/trend")

        assert response.status_code == 200
        points = response.get_json()
        assert [p["period_label"] for p in points] == ["1401-08", "1401-09"]
        assert points[0]["total_open_work_orders"] == 10
        assert points[1]["total_open_work_orders"] == 15

    def test_empty_database_returns_empty_list(self, client, empty_db):
        response = client.get("/api/analytics/trend")

        assert response.status_code == 200
        assert response.get_json() == []


class TestCategoryBreakdown:
    def test_filters_by_period(self, client, seeded):
        response = client.get(
            "/api/analytics/categories/breakdown", query_string={"period": "1401-09"}
        )

        assert response.status_code == 200
        body = response.get_json()
        assert len(body) == 1
        assert body[0]["category_code"] == "CAT_1"
        assert body[0]["total_open_work_orders"] == 15

    def test_without_period_returns_all_periods(self, client, seeded):
        response = client.get("/api/analytics/categories/breakdown")

        assert response.status_code == 200
        assert len(response.get_json()) == 2  # one row per period

    def test_invalid_period_format_is_rejected(self, client, seeded):
        response = client.get(
            "/api/analytics/categories/breakdown", query_string={"period": "14019"}
        )

        assert response.status_code == 400
        assert "period" in str(response.get_json())

    def test_empty_database_returns_empty_list(self, client, empty_db):
        response = client.get("/api/analytics/categories/breakdown")

        assert response.status_code == 200
        assert response.get_json() == []


class TestStatusFunnel:
    def test_returns_stages_in_order(self, client, seeded):
        response = client.get(
            "/api/analytics/status/funnel", query_string={"period": "1401-09"}
        )

        assert response.status_code == 200
        body = response.get_json()
        assert len(body) == 1
        assert body[0]["total_open_work_orders"] == 15

    def test_invalid_period_format_is_rejected(self, client, seeded):
        response = client.get(
            "/api/analytics/status/funnel", query_string={"period": "1401-9"}
        )

        assert response.status_code == 400

    def test_empty_database_returns_empty_list(self, client, empty_db):
        response = client.get("/api/analytics/status/funnel")

        assert response.status_code == 200
        assert response.get_json() == []


class TestCityRanking:
    def test_excludes_company_total_row(self, client, seeded):
        # Scoped to one period: the seed data spans two periods and
        # v_city_ranking is grouped by (period, city), so an unfiltered
        # request legitimately returns one Tehran row per period.
        response = client.get(
            "/api/analytics/cities/ranking", query_string={"period": "1401-09"}
        )

        assert response.status_code == 200
        body = response.get_json()
        names = [row["city_name"] for row in body]
        assert names == ["Tehran"]

    def test_unfiltered_request_returns_one_row_per_period(self, client, seeded):
        response = client.get("/api/analytics/cities/ranking")

        assert response.status_code == 200
        body = response.get_json()
        assert {row["city_name"] for row in body} == {"Tehran"}
        assert len(body) == 2  # one row per seeded period, never the company total

    def test_limit_is_clamped_to_valid_range(self, client, seeded):
        response = client.get(
            "/api/analytics/cities/ranking", query_string={"limit": 0}
        )

        # limit is clamped server-side to a minimum of 1, never rejected
        assert response.status_code == 200

    def test_empty_database_returns_empty_list(self, client, empty_db):
        response = client.get("/api/analytics/cities/ranking")

        assert response.status_code == 200
        assert response.get_json() == []


class TestWorkOrders:
    def test_default_pagination(self, client, seeded):
        response = client.get("/api/analytics/work-orders")

        assert response.status_code == 200
        body = response.get_json()
        assert body["page"] == 1
        assert body["page_size"] == 50
        assert body["total_items"] == 2
        assert body["total_pages"] == 1
        assert len(body["items"]) == 2

    def test_filters_by_city_and_period(self, client, seeded):
        response = client.get(
            "/api/analytics/work-orders",
            query_string={"city": "Tehran", "period": "1401-09"},
        )

        assert response.status_code == 200
        body = response.get_json()
        assert body["total_items"] == 1
        assert body["items"][0]["period_label"] == "1401-09"

    def test_filters_by_category(self, client, seeded):
        response = client.get(
            "/api/analytics/work-orders", query_string={"category": "CAT_1"}
        )

        assert response.status_code == 200
        assert response.get_json()["total_items"] == 2

    def test_unmatched_filter_returns_empty_page_not_error(self, client, seeded):
        response = client.get(
            "/api/analytics/work-orders", query_string={"city": "Nowhere"}
        )

        assert response.status_code == 200
        body = response.get_json()
        assert body["items"] == []
        assert body["total_items"] == 0
        assert body["total_pages"] == 1

    def test_page_size_is_clamped_to_max(self, client, seeded):
        response = client.get(
            "/api/analytics/work-orders", query_string={"page_size": 10_000}
        )

        assert response.status_code == 200
        assert response.get_json()["page_size"] == 500

    def test_invalid_period_format_is_rejected(self, client, seeded):
        response = client.get(
            "/api/analytics/work-orders", query_string={"period": "not-a-period"}
        )

        assert response.status_code == 400

    def test_empty_database_returns_empty_page(self, client, empty_db):
        response = client.get("/api/analytics/work-orders")

        assert response.status_code == 200
        assert response.get_json() == {
            "items": [],
            "page": 1,
            "page_size": 50,
            "total_items": 0,
            "total_pages": 1,
        }


class TestReconciliation:
    def test_reports_reported_vs_derived_mismatch(self, client, seeded):
        response = client.get("/api/analytics/data-quality/reconciliation")

        assert response.status_code == 200
        body = response.get_json()
        assert body["mismatch_count"] == 1
        row = body["mismatches"][0]
        assert row["city_name"] == "Tehran"
        assert row["reported_total"] == 20
        assert row["derived_total"] == 15
        assert row["variance"] == 5

    def test_empty_database_has_no_mismatches(self, client, empty_db):
        response = client.get("/api/analytics/data-quality/reconciliation")

        assert response.status_code == 200
        assert response.get_json() == {"mismatch_count": 0, "mismatches": []}