<div dir="rtl" align="right">

# API

## نمای کلی

مسیر پایه `/api` است. همه endpointهای تحلیلی read-only هستند و JSON
برمی‌گردانند. Swagger توسط Flask-RESTX از کلاس‌های resource و مدل‌های DTO
تولید می‌شود.

| منبع | مسیر |
|---|---|
| Swagger UI | `GET /api/docs/` |
| Swagger spec | `GET /api/swagger.json` |
| OpenAPI helper | `GET /api/openapi.json` |

## Endpointها

| Endpoint | کاربرد | پارامترها |
|---|---|---|
| `GET /api/health` | بررسی زنده بودن سرویس | ندارد |
| `GET /api/analytics/filters` | مقدارهای فیلتر | ندارد |
| `GET /api/analytics/kpis` | KPIهای آخرین دوره | ندارد |
| `GET /api/analytics/trend` | روند ماهانه | ندارد |
| `GET /api/analytics/categories/breakdown` | جمع بر اساس دسته | اختیاری `period` |
| `GET /api/analytics/status/funnel` | جمع بر اساس وضعیت | اختیاری `period` |
| `GET /api/analytics/cities/ranking` | رتبه‌بندی شهرها | اختیاری `period`, `limit` |
| `GET /api/analytics/work-orders` | جزئیات صفحه‌بندی‌شده | اختیاری `city`, `period`, `category`, `page`, `page_size` |
| `GET /api/analytics/data-quality/reconciliation` | mismatchهای reconciliation | ندارد |

## قوانین پارامترها

- `period`: فرمت `YYYY-MM` مثل `1401-09`.
- `limit`: در بازه `1..200` محدود می‌شود.
- `page`: حداقل `1`.
- `page_size`: در بازه `1..500` محدود می‌شود.
- `city`: نام دقیق شهر.
- `category`: کد دسته مثل `CAT_5`.

## نمونه درخواست‌ها

```bash
curl http://localhost:8080/api/health
curl http://localhost:8080/api/analytics/kpis
curl http://localhost:8080/api/analytics/trend
curl "http://localhost:8080/api/analytics/cities/ranking?period=1401-09&limit=5"
curl "http://localhost:8080/api/analytics/work-orders?page=1&page_size=50"
```

## نمونه پاسخ‌ها

Health:

```json
{ "status": "ok" }
```

KPIs:

```json
{
  "period_label": "1401-09",
  "total_open_work_orders": 4381,
  "active_cities": 16,
  "active_categories": 7
}
```

جزئیات دستورکار:

```json
{
  "items": [
    {
      "city_name": "شهر 5",
      "period_label": "1401-09",
      "category_code": "CAT_5",
      "status_name": "دردست اجرا",
      "open_work_order_count": 12
    }
  ],
  "page": 1,
  "page_size": 50,
  "total_items": 137,
  "total_pages": 3
}
```

Reconciliation:

```json
{
  "mismatch_count": 21,
  "mismatches": [
    {
      "period_label": "1401-07",
      "city_name": "کل شرکت",
      "category_name": "...",
      "reported_total": 0,
      "derived_total": 250,
      "variance": -250
    }
  ]
}
```

## خطاها

| وضعیت | معنی |
|---:|---|
| `400` | request یا query parameter نامعتبر |
| `500` | خطای غیرمنتظره سرور |

</div>
