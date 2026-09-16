from pathlib import Path

from etl.extract.excel import ExcelExtractor
from etl.transform.pipeline import WorkOrderTransformer

if __name__ == "__main__":
    path = Path("data/raw/2016.xlsx")
    records = ExcelExtractor().extract(path)
    result = WorkOrderTransformer().transform(records)

    print(f"Raw rows extracted:      {len(records)}")
    print(f"Rejected rows:           {len(result.rejected)}")
    print(f"Distinct cities:         {len(result.dim_cities)}")
    print(f"Distinct fiscal periods: {len(result.dim_dates)}")
    print(f"Distinct categories:     {len(result.dim_categories)}")
    print(f"Fact rows (long format): {len(result.facts)}")
    print(f"Reconciliation checks:   {len(result.reconciliations)}")

    mismatches = [r for r in result.reconciliations if r.reported_total != r.derived_total]
    print(f"Reconciliation mismatches: {len(mismatches)}")
    for m in mismatches[:10]:
        print(f"  - {m.city_name} / {m.date_key} / {m.category_code}: "
              f"reported={m.reported_total} derived={m.derived_total}")

    if result.rejected:
        print("\nRejected rows:")
        for r in result.rejected:
            print(f"  - row {r['source_row_number']}: {r['reason']}")
