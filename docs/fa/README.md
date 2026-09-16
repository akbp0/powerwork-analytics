<div dir="rtl" align="right">

# مستندات PowerWork Analytics

PowerWork Analytics یک پلتفرم تحلیلی end-to-end برای دیتاست دستورکارها است.
این پروژه فایل Excel گزارش‌محور را دریافت می‌کند، داده خام و lineage را در
PostgreSQL ذخیره می‌کند، با ETL قابل اجرای مجدد داده را تبدیل می‌کند، انبار
داده‌ی ستاره‌ای می‌سازد، API تحلیلی read-only با Flask-RESTX ارائه می‌دهد و
داشبورد را پشت nginx سرو می‌کند.

## فهرست مستندات

| سند | کاربرد |
|---|---|
| `overview.md` | محدوده پروژه، قابلیت‌ها، جریان کلی و ساختار repo |
| `architecture.md` | معماری سیستم، لایه‌بندی backend و جریان startup |
| `data-model.md` | پروفایل داده، کیفیت داده، schema و viewهای warehouse |
| `etl.md` | stageهای ETL، idempotency، خطاها و اجرای دستی |
| `api.md` | endpointها، پارامترها، مثال‌ها و Swagger |
| `dashboard.md` | پنل‌های داشبورد، مصرف API و رفتار runtime |
| `deployment.md` | Docker Compose، nginx، متغیرهای محیطی و عملیات |

## اجرای سریع

```bash
cp .env.example .env
docker compose up --build
```

ترتیب startup:

```text
source-db + warehouse-db -> etl -> api -> nginx
```

ETL هنگام startup به‌صورت خودکار اجرا می‌شود و فایل `data/raw/2016.xlsx` را
قبل از شروع API load می‌کند.

آدرس‌ها:

- داشبورد: `http://localhost:8080/`
- Swagger: `http://localhost:8080/api/docs/`
- Health: `http://localhost:8080/health`
- API مستقیم برای دیباگ: `http://localhost:5000/api/health`

## اجزای runtime

| سرویس | تکنولوژی | نقش |
|---|---|---|
| `source-db` | PostgreSQL 17 | دیتابیس raw landing |
| `warehouse-db` | PostgreSQL 17 | انبار داده تحلیلی |
| `etl` | Python | load داده از Excel به source و warehouse هنگام startup |
| `api` | Flask-RESTX + Gunicorn | API تحلیلی read-only و Swagger |
| `nginx` | nginx Alpine | entrypoint عمومی، سرو داشبورد و reverse proxy |

## نتیجه فعلی داده

اجرای ETL روی `data/raw/2016.xlsx` این خروجی را تولید می‌کند:

- ۵۴ ردیف خام.
- ۳ ردیف ردشده.
- ۱٬۶۳۲ ردیف fact.
- ۳۵۷ ردیف reconciliation.
- ۲۱ mismatch برای بررسی کیفیت داده.

## دستورهای کاربردی

```bash
docker compose up --build
docker compose ps
docker compose logs -f etl
docker compose logs -f api
docker compose run --rm etl
docker compose down
```

جزئیات کامل اجرا در `deployment.md` آمده است.

</div>
