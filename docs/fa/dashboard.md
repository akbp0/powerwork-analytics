<div dir="rtl" align="right">

# داشبورد

## نمای کلی

داشبورد یک برنامه single-page در `dashboard/index.html` است. nginx آن را به
صورت static content سرو می‌کند. صفحه از مسیرهای نسبی API استفاده می‌کند، پس
پشت nginx به hostname خاصی وابسته نیست.

```js
const API = "/api/analytics";
```

## پنل‌ها

| پنل | Endpoint | UI |
|---|---|---|
| خلاصه KPI | `GET /api/analytics/kpis` | کارت‌های KPI |
| روند | `GET /api/analytics/trend` | نمودار خطی |
| شکست دسته‌ها | `GET /api/analytics/categories/breakdown` | نمودار doughnut |
| funnel وضعیت | `GET /api/analytics/status/funnel` | نمودار میله‌ای افقی |
| رتبه‌بندی شهر | `GET /api/analytics/cities/ranking` | لیست رتبه‌بندی |
| جزئیات دستورکار | `GET /api/analytics/work-orders` | جدول صفحه‌بندی‌شده |
| کیفیت داده | `GET /api/analytics/data-quality/reconciliation` | badge و جدول mismatch |
| فیلترها | `GET /api/analytics/filters` | کنترل‌های dropdown |

## رفتار runtime

- ابتدا فیلترها load می‌شوند.
- پنل‌های داشبورد به‌صورت موازی load می‌شوند.
- refresh دستی همه پنل‌ها را دوباره load می‌کند.
- تغییر period پنل‌های وابسته به period را refresh می‌کند.
- فیلترهای city/category جدول جزئیات را refresh می‌کنند.
- خطای API toast نشان می‌دهد و وضعیت سیستم را offline می‌کند.
- لینک Swagger در UI به `/api/docs/` اشاره می‌کند.

## وابستگی‌های Frontend

- Chart.js از CDN.
- فونت Vazirmatn از Google Fonts.
- در وضعیت فعلی داشبورد به build step نیاز ندارد.

</div>
