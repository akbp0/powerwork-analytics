from __future__ import annotations

import logging
import os
from contextlib import contextmanager

import psycopg

logger = logging.getLogger(__name__)


@contextmanager
def get_connection(env_var: str):
    """Open a connection to the database named by the given environment
    variable (SOURCE_DATABASE_URL or WAREHOUSE_DATABASE_URL), committing on
    success and rolling back on any exception.
    """
    dsn = os.getenv(env_var)
    if not dsn:
        raise RuntimeError(f"{env_var} is not set — check your .env / environment configuration")

    conn = psycopg.connect(dsn)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        logger.exception("Transaction rolled back for %s", env_var)
        raise
    finally:
        conn.close()
