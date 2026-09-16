<div dir="rtl" align="right">

# دیپلوی

## یک Stack واحد

پروژه فقط یک فایل Compose دارد:

```text
docker-compose.yml
```


## اجرا

```bash
cp .env.example .env
docker compose up --build
```

## سرویس‌ها

| سرویس | عمومی؟ | توضیح |
|---|---|---|
| `nginx` | بله | entrypoint عمومی HTTP |
| `api` | فقط debug روی localhost | API Flask روی Gunicorn |
| `etl` | خیر | هنگام startup اجرا می‌شود و تمام می‌شود |
| `source-db` | فقط debug روی localhost | دیتابیس raw source |
| `warehouse-db` | فقط debug روی localhost | warehouse تحلیلی |

## متغیرهای محیطی

| متغیر | مقدار پیش‌فرض | کاربرد |
|---|---:|---|
| `POSTGRES_USER` | `postgres` | کاربر PostgreSQL |
| `POSTGRES_PASSWORD` | `postgres` | رمز PostgreSQL |
| `SOURCE_POSTGRES_DB` | `source_db` | نام دیتابیس source |
| `WAREHOUSE_POSTGRES_DB` | `warehouse_db` | نام دیتابیس warehouse |
| `SOURCE_DB_PORT` | `5433` | پورت host برای source DB |
| `WAREHOUSE_DB_PORT` | `5434` | پورت host برای warehouse DB |
| `API_HTTP_PORT` | `5000` | پورت host برای debug مستقیم API |
| `NGINX_HTTP_PORT` | `8080` | پورت عمومی nginx |
| `GUNICORN_WORKERS` | `2` | تعداد workerهای Gunicorn |
| `GUNICORN_THREADS` | `4` | تعداد thread برای هر worker |
| `GUNICORN_TIMEOUT` | `120` | timeout درخواست‌های Gunicorn |

برای سرور واقعی، `POSTGRES_PASSWORD` را تغییر دهید، `APP_ENV=production`
بگذارید، `FLASK_DEBUG=0` را نگه دارید و اگر nginx باید روی HTTP استاندارد
گوش کند `NGINX_HTTP_PORT=80` تنظیم کنید.

## اسکریپت Deploy

```bash
bash scripts/deploy.sh
```

این اسکریپت:

- `.env` را می‌خواند.
- imageهای PostgreSQL و nginx را pull می‌کند.
- image مربوط به API/ETL را build می‌کند.
- کل stack را بالا می‌آورد.
- وضعیت سرویس‌ها را نمایش می‌دهد.

## رفتار nginx

کانفیگ nginx در `nginx/conf.d/powerwork.conf` است.

nginx:

- داشبورد را سرو می‌کند.
- مسیر `/api/*` را به `api:5000` proxy می‌کند.
- مسیر `/swaggerui/*` را برای assetهای Swagger proxy می‌کند.
- مسیر `/health` را به `/api/health` وصل می‌کند.
- مسیر `/nginx-health` را برای healthcheck ارائه می‌دهد.
- gzip را فعال می‌کند.
- headerهای امنیتی پایه اضافه می‌کند.
- assetهای static را cache می‌کند.
- برای API rate limit اعمال می‌کند.


</div>
