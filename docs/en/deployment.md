# Deployment

## Single Stack

The project intentionally uses one Compose file:

```text
docker-compose.yml
```

There is no separate dev/prod Compose file. Runtime behavior is controlled by
`.env`.

## Start

```bash
cp .env.example .env
docker compose up --build
```

## Services

| Service | Public? | Notes |
|---|---|---|
| `nginx` | Yes | Public HTTP entrypoint |
| `api` | Localhost debug only | Gunicorn Flask API |
| `etl` | No | Runs at startup and exits |
| `source-db` | Localhost debug only | Raw source database |
| `warehouse-db` | Localhost debug only | Analytical warehouse |

## Environment Variables

| Variable | Default | Purpose |
|---|---:|---|
| `POSTGRES_USER` | `postgres` | PostgreSQL user |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password |
| `SOURCE_POSTGRES_DB` | `source_db` | Source DB name |
| `WAREHOUSE_POSTGRES_DB` | `warehouse_db` | Warehouse DB name |
| `SOURCE_DB_PORT` | `5433` | Host source DB port |
| `WAREHOUSE_DB_PORT` | `5434` | Host warehouse DB port |
| `API_HTTP_PORT` | `5000` | Host API debug port |
| `NGINX_HTTP_PORT` | `8080` | Public nginx HTTP port |
| `GUNICORN_WORKERS` | `2` | Gunicorn worker count |
| `GUNICORN_THREADS` | `4` | Gunicorn threads per worker |
| `GUNICORN_TIMEOUT` | `120` | Gunicorn request timeout |

For a real server, change `POSTGRES_PASSWORD`, set `APP_ENV=production`, keep
`FLASK_DEBUG=0`, and set `NGINX_HTTP_PORT=80` if nginx should bind standard
HTTP.

## Deploy Helper

```bash
bash scripts/deploy.sh
```

The script:

- Reads `.env`.
- Pulls PostgreSQL and nginx images.
- Builds the API/ETL image.
- Starts the whole stack.
- Prints service status.

## nginx Behavior

nginx configuration lives in `nginx/conf.d/powerwork.conf`.

It:

- Serves the dashboard.
- Proxies `/api/*` to `api:5000`.
- Proxies `/swaggerui/*` for Swagger assets.
- Proxies `/health` to `/api/health`.
- Exposes `/nginx-health`.
- Enables gzip.
- Adds basic security headers.
- Caches static assets.
- Applies API rate limiting.

## Operations

```bash
docker compose ps
docker compose logs -f etl
docker compose logs -f api
docker compose logs -f nginx
docker compose run --rm etl
docker compose down
```
