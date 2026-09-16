<div dir="rtl" align="right">

# مدل داده

## فایل منبع

`data/raw/2016.xlsx` یک گزارش قالب‌بندی‌شده است، نه جدول تخت و تمیز.

| بخش workbook | معنی |
|---|---|
| ردیف 0 | عنوان گزارش، merge شده روی چند ستون |
| ردیف 1 | هدرهای گروهی: ۷ دسته به‌همراه بلوک جمع کل |
| ردیف 2 | labelهای وضعیت داخل هر دسته |
| ردیف‌های 3 به بعد | ۵۴ ردیف داده برای ماه‌های ۷، ۸ و ۹ سال ۱۴۰۱ |

هر ماه شامل ۱۶ واحد عملیاتی و دو ردیف تجمیعی است:

- `جمع به تفکیک هر واحد`
- `کل شرکت` با کد واحد `9999`

## یافته‌های کیفیت داده

| مورد | ریسک | نحوه مدیریت |
|---|---|---|
| ردیف‌های تجمیعی داخل داده هستند | double-count در تحلیل شهری | با `dim_city.is_company_total` علامت‌گذاری و از viewهای شهری حذف می‌شوند |
| بعضی ردیف‌ها period ندارند | نمی‌توان ردیف را به زمان وصل کرد | reject و log می‌شوند |
| عرض بلوک دسته‌ها متغیر است | ستون ثابت در raw شکننده است | داده دسته‌ها در JSONB ذخیره می‌شود |
| total گزارش‌شده ممکن است با total محاسبه‌شده فرق کند | نمی‌توان به total منبع اعتماد کورکورانه کرد | reported و derived ذخیره می‌شوند |
| label دسته تکراری است | label کلید پایدار نیست | کدهای `CAT_1` تا `CAT_7` استفاده می‌شود |
| نام‌های کسب‌وکاری placeholder هستند | فرض دامنه‌ای نباید hard-code شود | از کدها و dimensionهای عمومی استفاده شده است |

## خروجی ETL برای فایل نمونه

| معیار | مقدار |
|---|---:|
| ردیف خام | ۵۴ |
| ردیف reject شده | ۳ |
| ردیف fact | ۱٬۶۳۲ |
| ردیف reconciliation | ۳۵۷ |
| mismatch در reconciliation | ۲۱ |

## مدل ستاره‌ای

```text
dim_city      dim_date       dim_category      dim_status
    \            |                |                 /
     \           |                |                /
      +----------+----------------+---------------+
                 |
       fact_work_order_status
```

grain جدول fact اصلی:

```text
شهر x دوره مالی x دسته x وضعیت
```

## جدول‌ها

| جدول | Grain | کاربرد |
|---|---|---|
| `mart.dim_city` | یک ردیف برای هر شهر/واحد | dimension شهر و واحد کسب‌وکاری |
| `mart.dim_date` | یک ردیف برای هر ماه مالی | dimension دوره مالی جلالی |
| `mart.dim_category` | یک ردیف برای هر دسته | کد پایدار دسته و label نمایشی |
| `mart.dim_status` | یک ردیف برای هر مرحله workflow | dimension وضعیت با ترتیب |
| `mart.fact_work_order_status` | شهر x دوره x دسته x وضعیت | measure اصلی count |
| `mart.fact_category_reconciliation` | شهر x دوره x دسته | مقایسه total گزارش‌شده و محاسبه‌شده |

## Viewها

| View | مصرف‌کننده |
|---|---|
| `mart.v_kpi_summary` | کارت‌های KPI |
| `mart.v_monthly_trend` | نمودار روند |
| `mart.v_category_breakdown` | مقایسه دسته‌ها |
| `mart.v_status_funnel` | funnel وضعیت‌ها |
| `mart.v_city_ranking` | رتبه‌بندی شهرها |
| `mart.v_fact_detail` | جدول جزئیات |
| `mart.v_reconciliation_mismatches` | پنل کیفیت داده |

DDLها در `sql/warehouse/` قرار دارند.

</div>
