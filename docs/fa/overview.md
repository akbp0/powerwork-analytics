<div dir="rtl" align="right">


## قابلیت‌های پیاده‌سازی‌شده

- استخراج داده از `data/raw/2016.xlsx`.
- دیتابیس source با batch tracking و ثبت ردیف‌های reject شده.
- مدل ستاره‌ای warehouse با dimension، fact و reconciliation fact.
- Viewهای SQL تحلیلی برای API و داشبورد.
- ETL شی‌گرا با stageهای قابل تعویض.
- API با Flask-RESTX و مستندات Swagger خودکار.
- داشبورد تعاملی بر پایه `/api/analytics/*`.
- nginx برای reverse proxy و سرو فایل‌های static.
- یک Docker Compose stack واحد با اجرای خودکار ETL هنگام startup.
- تست برای منطق transform و تولید API/Swagger.

## ساختار repository

```text
data/raw/           فایل workbook منبع
etl/                پایپ‌لاین extract، transform و load
sql/source/         اسکیمای raw منبع
sql/warehouse/      DDL warehouse و viewهای تحلیلی
src/api/            برنامه Flask-RESTX
dashboard/          داشبورد تحت وب
nginx/              کانفیگ nginx
scripts/            اسکریپت‌های deploy و operation
docs/en/            مستندات انگلیسی
docs/fa/            مستندات فارسی
tests/              تست‌های واحد و API
```

## آدرس‌های مهم

| کاربرد | آدرس |
|---|---|
| داشبورد | `http://localhost:8080/` |
| Swagger UI | `http://localhost:8080/api/docs/` |
| Health از طریق nginx | `http://localhost:8080/health` |
| Health مستقیم API | `http://localhost:5000/api/health` |

## اصول طراحی

- داده خام باید قابل audit بماند.
- خواندن از warehouse باید ساده و سریع باشد.
- SQL در repositoryها و viewهای warehouse متمرکز باشد.
- مستندات API از کد تولید شود.
- startup با Docker Compose قابل تکرار باشد.
- nginx تنها entrypoint عمومی باشد.

</div>
