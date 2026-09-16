from __future__ import annotations

import os
import uuid
from pathlib import Path

import psycopg
import pytest

from api import create_app

SCHEMA_FILES = [
    "sql/warehouse/001_create_dimensions.sql",
    "sql/warehouse/002_create_facts.sql",
    "sql/warehouse/003_analytical_views.sql",
]

# Truncating these three is enough: the fact tables FK-reference them, and
# TRUNCATE ... CASCADE takes care of the dependent fact rows regardless of
# statement order.
DIM_TABLES = ["mart.dim_city", "mart.dim_date", "mart.dim_category"]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _database_url() -> str | None:
    return os.getenv("TEST_WAREHOUSE_DATABASE_URL") or os.getenv("WAREHOUSE_DATABASE_URL")


@pytest.fixture(scope="session")
def warehouse_url() -> str:
    url = _database_url()
    if not url:
        pytest.skip(
            "Set WAREHOUSE_DATABASE_URL (or TEST_WAREHOUSE_DATABASE_URL) to a "
            "Postgres database to run the API integration suite, e.g. the "
            "warehouse-db service from docker-compose.yml."
        )
    return url


@pytest.fixture(scope="session")
def _schema_ready(warehouse_url: str) -> None:
    try:
        conn = psycopg.connect(warehouse_url, connect_timeout=5)
    except psycopg.OperationalError as exc:
        pytest.skip(f"Could not connect to the test warehouse database: {exc}")
        return
    try:
        with conn.cursor() as cur:
            for rel_path in SCHEMA_FILES:
                cur.execute((_repo_root() / rel_path).read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()


@pytest.fixture(scope="session")
def app(warehouse_url: str, _schema_ready: None):
    os.environ["WAREHOUSE_DATABASE_URL"] = warehouse_url
    flask_app = create_app()
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db_conn(warehouse_url: str):
    conn = psycopg.connect(warehouse_url)
    yield conn
    conn.close()


def _truncate_all(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(f"TRUNCATE {', '.join(DIM_TABLES)} RESTART IDENTITY CASCADE")
    conn.commit()


def _seed(conn: psycopg.Connection) -> dict:
    """Seeds a small, deterministic dataset:

    - Two fiscal periods (1401-08, 1401-09)
    - One real city (Tehran) plus one company-total aggregate row, which
      every per-city view must exclude
    - One category with fact rows in both periods
    - One reconciliation row with a deliberate reported/derived mismatch
    """
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO mart.dim_city (city_name, business_unit_code, is_company_total) "
            "VALUES (%s, %s, %s), (%s, %s, %s) RETURNING city_key",
            ("Tehran", "BU-01", False, "کل شرکت", "9999", True),
        )
        tehran_key, total_key = (row[0] for row in cur.fetchall())

        cur.execute(
            "INSERT INTO mart.dim_date (date_key, fiscal_year, fiscal_month, period_label) "
            "VALUES (%s, %s, %s, %s), (%s, %s, %s, %s) RETURNING date_key",
            (140108, 1401, 8, "1401-08", 140109, 1401, 9, "1401-09"),
        )
        aug_key, sep_key = (row[0] for row in cur.fetchall())

        cur.execute(
            "INSERT INTO mart.dim_category (category_code, category_name, display_order) "
            "VALUES (%s, %s, %s) RETURNING category_key",
            ("CAT_1", "Electrical", 1),
        )
        cat_key = cur.fetchone()[0]

        cur.execute("SELECT status_key FROM mart.dim_status ORDER BY stage_order LIMIT 1")
        status_key = cur.fetchone()[0]

        batch_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO mart.fact_work_order_status "
            "(city_key, date_key, category_key, status_key, open_work_order_count, batch_id) "
            "VALUES (%s, %s, %s, %s, %s, %s), (%s, %s, %s, %s, %s, %s)",
            (
                tehran_key, aug_key, cat_key, status_key, 10, batch_id,
                tehran_key, sep_key, cat_key, status_key, 15, batch_id,
            ),
        )

        cur.execute(
            "INSERT INTO mart.fact_category_reconciliation "
            "(city_key, date_key, category_key, reported_total, derived_total, batch_id) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (tehran_key, sep_key, cat_key, 20, 15, batch_id),
        )
    conn.commit()
    return {
        "tehran_key": tehran_key,
        "total_key": total_key,
        "aug_key": aug_key,
        "sep_key": sep_key,
        "cat_key": cat_key,
    }


@pytest.fixture()
def seeded(db_conn):
    """A function-scoped fixture giving each test a clean, deterministic
    dataset and cleaning up afterwards, so tests never depend on run order."""
    _truncate_all(db_conn)
    ids = _seed(db_conn)
    yield ids
    _truncate_all(db_conn)


@pytest.fixture()
def empty_db(db_conn):
    """Guarantees a fully empty warehouse, for exercising the endpoints'
    zero-rows / no-data code paths."""
    _truncate_all(db_conn)
    yield
    _truncate_all(db_conn)
