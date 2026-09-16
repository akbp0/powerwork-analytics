# PowerWork Analytics

Project documentation lives under `docs` in two complete language folders:

- English: `docs/en/README.md`
- فارسی: `docs/fa/README.md`

Quick start:

```bash
cp .env.example .env
docker compose up --build
```

Startup runs PostgreSQL, then ETL, then the API, then nginx.

Open the dashboard at `http://localhost:8080/`.

مستندات کامل پروژه داخل فولدر `docs` قرار دارد:

- انگلیسی: `docs/en/README.md`
- فارسی: `docs/fa/README.md`

اجرای سریع:

```bash
cp .env.example .env
docker compose up --build
```

در زمان startup ابتدا PostgreSQL، سپس ETL، بعد API و در نهایت nginx اجرا
می‌شود.

داشبورد از مسیر `http://localhost:8080/` در دسترس است.
