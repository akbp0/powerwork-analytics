<div dir="rtl" align="right">

# معماری

## دیاگرام سیستم

```text
data/raw/2016.xlsx
        |
        | ExcelExtractor
        v
source_db.raw
        |
        | SourceLoader + WorkOrderTransformer + WarehouseLoader
        v
warehouse_db.mart
        |
        | mart.v_* analytical views
        v
Flask-RESTX API
        |
        | nginx reverse proxy
        v
Dashboard
```

## مسئولیت لایه‌ها

| لایه | مسئولیت |
|---|---|
| فایل Excel | ورودی اصلی، بدون تغییر |
| `source_db.raw` | ردیف‌های خام، metadata مربوط به batch، ردیف‌های reject شده |
| ETL | استخراج، اعتبارسنجی، نرمال‌سازی، reconciliation و load |
| `warehouse_db.mart` | dimensionها، factها و viewهای آماده query |
| API | endpointهای JSON read-only و Swagger خودکار |
| nginx | entrypoint عمومی، static files، reverse proxy، gzip و headerها |
| داشبورد | KPI، نمودار، فیلتر، drill-down و پنل کیفیت داده |

## چرا دو دیتابیس؟

`source_db` نشان می‌دهد فایل منبع دقیقا چه داده‌ای داشته است. این لایه برای
traceability، lineage و reprocessing طراحی شده است.

`warehouse_db` نشان می‌دهد تحلیل‌ها باید از چه مدلی سریع بخوانند. این لایه
برای درخواست‌های read-heavy داشبورد و API طراحی شده است.

این جداسازی باعث می‌شود پیچیدگی raw ingestion وارد queryهای تحلیلی نشود و API
از جزئیات landing zone جدا بماند.

## لایه‌بندی Backend

```text
namespaces -> services -> repositories -> mart views
```

| Package | نقش |
|---|---|
| `src/api/namespaces` | resourceهای Flask-RESTX، پارامترها و decoratorهای Swagger |
| `src/api/services` | orchestration و شکل‌دهی پاسخ |
| `src/api/repositories` | دسترسی SQL به viewهای warehouse |
| `src/api/models` | DTOها برای schemaهای Swagger |
| `src/api/extensions` | lifecycle دیتابیس و RESTX API مشترک |

## جریان Startup

`docker-compose.yml` تنها stack پروژه است. ترتیب startup عمدا کنترل‌شده است:

```text
source-db و warehouse-db healthy می‌شوند
etl اجرا می‌شود و با موفقیت تمام می‌شود
api شروع می‌شود و healthy می‌شود
nginx شروع می‌شود
```

اگر ETL شکست بخورد، API شروع نمی‌شود. این کار مانع سرو شدن داشبورد روی
warehouse خالی یا ناقص می‌شود.

</div>
