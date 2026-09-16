
from __future__ import annotations

import psycopg
from flask import Flask, current_app, g


class WarehouseDatabase:
    _CONTEXT_KEY = "warehouse_conn"

    def init_app(self, app: Flask) -> None:
        app.teardown_appcontext(self.close_connection)

    def get_connection(self) -> psycopg.Connection:
        if self._CONTEXT_KEY not in g:
            g.warehouse_conn = psycopg.connect(current_app.config["WAREHOUSE_DATABASE_URL"])
        return g.warehouse_conn

    def close_connection(self, exception: BaseException | None = None) -> None:
        conn = g.pop(self._CONTEXT_KEY, None)
        if conn is not None:
            conn.close()


# Module-level singleton: imported by the app factory (to register the
# teardown hook) and by resources/repositories (to obtain a connection).
warehouse_db = WarehouseDatabase()
