<div dir="rtl" align="right">

# ETL

## هدف

ETL فایل workbook را به رکوردهای تحلیلی آماده warehouse تبدیل می‌کند، در حالی
که lineage داده خام و اطلاعات ردیف‌های reject شده حفظ می‌شود.

## Stageها

| Stage | کلاس | فایل | مسئولیت |
|---|---|---|---|
| Extract | `ExcelExtractor` | `etl/extract/excel.py` | parse کردن workbook و بلوک‌های دسته |
| Raw load | `SourceLoader` | `etl/load/source.py` | ذخیره raw rows، batch metadata و rejected rows |
| Transform | `WorkOrderTransformer` | `etl/transform/pipeline.py` | اعتبارسنجی، نرمال‌سازی و ساخت dimension/fact |
| Warehouse load | `WarehouseLoader` | `etl/load/warehouse.py` | upsert کردن dimension، fact و reconciliation |
| Orchestration | `ETLPipeline` | `etl/run_etl.py` | اجرای stageها به ترتیب |

## اجرای خودکار هنگام Startup

ETL یک سرویس عادی در `docker-compose.yml` است. بعد از healthy شدن هر دو
دیتابیس اجرا می‌شود:

```text
source-db + warehouse-db -> etl -> api -> nginx
```

API به موفقیت ETL وابسته است:

```yaml
etl:
  condition: service_completed_successfully
```

یعنی اگر load شکست بخورد، API شروع نمی‌شود.

## اجرای دستی

داخل Docker:

```bash
docker compose run --rm etl
```

روی محیط local:

```bash
pip install -r requirements.txt
python -m etl.run_etl --file data/raw/2016.xlsx
```

## Idempotency

اجرای دوباره ETL امن است:

- Dimensionها با business key پایدار upsert می‌شوند.
- Factها با کلید کامل grain upsert می‌شوند.
- ردیف‌های reconciliation برای همان grain update می‌شوند.
- ردیف‌های reject شده به batch مربوطه وصل می‌شوند.

## مدیریت خطا

- خطای extract/transform/load باعث exit code غیرصفر می‌شود.
- metadata مربوط به batch تا حد ممکن وضعیت failed را ثبت می‌کند.
- ردیف‌های نامعتبر silent drop نمی‌شوند و در `raw.rejected_rows` ذخیره می‌شوند.

</div>
