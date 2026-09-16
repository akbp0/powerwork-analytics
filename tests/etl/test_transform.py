from etl.extract.excel import RawRecord
from etl.transform.pipeline import WorkOrderTransformer, transform


def _record(**overrides) -> RawRecord:
    base = dict(
        source_row_number=10,
        city_name="شهر 1",
        business_unit_code="1001",
        fiscal_year="1401",
        fiscal_month="7",
        category_columns={
            "0:تست 1": {
                "دردست اجرا": 5,
                "تهیه صورت وضعیت": 2,
                "مجموع دستورکارهای باز": 7,
            }
        },
        is_aggregate_row=False,
    )
    base.update(overrides)
    return RawRecord(**base)


def test_valid_row_produces_facts_and_reconciliation():
    result = transform([_record()])
    assert len(result.facts) == 2  # total column excluded from facts
    assert result.facts[0].open_work_order_count == 5
    assert len(result.reconciliations) == 1
    assert result.reconciliations[0].reported_total == 7
    assert result.reconciliations[0].derived_total == 7
    assert len(result.rejected) == 0


def test_mismatched_total_is_flagged_not_dropped():
    rec = _record(category_columns={
        "0:تست 1": {"دردست اجرا": 5, "مجموع دستورکارهای باز": 99},
    })
    result = transform([rec])
    recon = result.reconciliations[0]
    assert recon.reported_total == 99
    assert recon.derived_total == 5  # still loaded, just flagged as a mismatch


def test_missing_fiscal_period_is_rejected():
    rec = _record(fiscal_year=None, fiscal_month=None)
    result = transform([rec])
    assert len(result.facts) == 0
    assert len(result.rejected) == 1
    assert "missing" in result.rejected[0]["reason"]


def test_aggregate_row_flagged_as_company_total():
    rec = _record(city_name="کل شرکت", business_unit_code="9999", is_aggregate_row=True)
    result = transform([rec])
    city = next(c for c in result.dim_cities if c.city_name == "کل شرکت")
    assert city.is_company_total is True


def test_negative_and_nonnumeric_values_coerced_to_zero():
    rec = _record(category_columns={
        "0:تست 1": {"دردست اجرا": -3, "تهیه صورت وضعیت": "n/a", "مجموع دستورکارهای باز": 0},
    })
    result = transform([rec])
    counts = {f.status_code: f.open_work_order_count for f in result.facts}
    assert counts["IN_PROGRESS"] == 0
    assert counts["STATEMENT_DRAFTED"] == 0


def test_transformer_class_matches_functional_wrapper():
    records = [_record()]
    assert transform(records) == WorkOrderTransformer().transform(records)
