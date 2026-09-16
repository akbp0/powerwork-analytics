# Dashboard

## Overview

The dashboard is a single-page browser application in `dashboard/index.html`.
nginx serves it as static content. The page uses relative API paths, so it
works through nginx without environment-specific hostnames.

```js
const API = "/api/analytics";
```

## Panels

| Panel | Endpoint | UI |
|---|---|---|
| KPI summary | `GET /api/analytics/kpis` | KPI cards |
| Trend | `GET /api/analytics/trend` | Line chart |
| Category breakdown | `GET /api/analytics/categories/breakdown` | Doughnut chart |
| Status funnel | `GET /api/analytics/status/funnel` | Horizontal bar chart |
| City ranking | `GET /api/analytics/cities/ranking` | Ranked list |
| Work-order details | `GET /api/analytics/work-orders` | Paginated table |
| Data quality | `GET /api/analytics/data-quality/reconciliation` | Mismatch badge/table |
| Filters | `GET /api/analytics/filters` | Dropdown controls |

## Runtime Behavior

- Loads filters first.
- Loads dashboard panels in parallel.
- Manual refresh reloads all panels.
- Period changes refresh period-dependent panels.
- City/category filters refresh the detail table.
- API errors show a toast and mark system status offline.
- Swagger is linked from the UI at `/api/docs/`.

## Frontend Dependencies

- Chart.js from CDN.
- Vazirmatn font from Google Fonts.
- No build step is required for the current dashboard.
