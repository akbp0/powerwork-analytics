import os


class Settings:
    """Central application configuration, loaded from the environment.

    Flask's `app.config.from_object()` reads every uppercase class
    attribute, so this doubles as both the config object and its own
    schema/documentation.
    """

    ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

    SOURCE_DATABASE_URL = os.getenv("SOURCE_DATABASE_URL", "")
    WAREHOUSE_DATABASE_URL = os.getenv("WAREHOUSE_DATABASE_URL", "")

    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "5000"))

    API_TITLE = "PowerWork Analytics API"
    API_VERSION = "1.0.0"
    RESTX_JSON = {"ensure_ascii": False}
