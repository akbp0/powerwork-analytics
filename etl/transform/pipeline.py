from __future__ import annotations
import logging
import re
from dataclasses import dataclass
from typing import Iterable
from etl.base import BaseTransformer
from etl.extract.excel import RawRecord

logger = logging.getLogger(__name__)


@dataclass
class DimCity:
    city_name: str
    business_unit_code: str
    is_company_total: bool


@dataclass
class DimDate:
    fiscal_year: int
    fiscal_month: int

    @property
    def date_key(self) -> int:
        return self.fiscal_year * 100 + self.fiscal_month

    @property
    def period_label(self) -> str:
        return f"{self.fiscal_year}-{self.fiscal_month:02d}"


@dataclass
class DimCategory:
    category_code: str
    category_name: str
    display_order: int


@dataclass
class FactRow:
    city_name: str
    date_key: int
    category_code: str
    status_code: str
    status_name: str
    open_work_order_count: int


@dataclass
class ReconciliationRow:
    city_name: str
    date_key: int
    category_code: str
    reported_total: int
    derived_total: int


@dataclass
class TransformResult:
    dim_cities: list[DimCity]
    dim_dates: list[DimDate]
    dim_categories: list[DimCategory]
    facts: list[FactRow]
    reconciliations: list[ReconciliationRow]
    rejected: list[dict]


class WorkOrderTransformer(BaseTransformer[RawRecord, TransformResult]):
    """Applies the business rules described in the module docstring and
    reshapes wide raw rows into the warehouse's long/star-schema shape."""

    TOTAL_COLUMN_PATTERN = re.compile(r"مجموع|^کل\b|کل\\?n?دستورکارهای")

    CANONICAL_STATUS_CODES = {
        "دردست اجرا": "IN_PROGRESS",
        "تهیه صورت وضعیت": "STATEMENT_DRAFTED",
        "صورت وضعیت نزد مشاور": "WITH_CONSULTANT",
        "صورت وضعیت نزد ستاد": "WITH_HQ",
        "صورت وضعیت نزد مالی": "WITH_FINANCE",
    }

    def transform(self, records: Iterable[RawRecord]) -> TransformResult:
        dim_cities: dict[str, DimCity] = {}
        dim_dates: dict[int, DimDate] = {}
        dim_categories: dict[str, DimCategory] = {}
        facts: list[FactRow] = []
        reconciliations: list[ReconciliationRow] = []
        rejected: list[dict] = []

        for rec in records:
            period = self._validate_period(rec, rejected)
            if period is None:
                continue
            fiscal_year, fiscal_month = period
            date_key = fiscal_year * 100 + fiscal_month
            dim_dates.setdefault(date_key, DimDate(fiscal_year, fiscal_month))

            # Business rule 1: aggregate rows are flagged, not treated as a city.
            is_total_row = rec.is_aggregate_row
            code = rec.business_unit_code or ("TOTAL" if is_total_row else "UNKNOWN")
            dim_cities.setdefault(
                rec.city_name,
                DimCity(city_name=rec.city_name, business_unit_code=code, is_company_total=is_total_row),
            )

            self._transform_categories(rec, date_key, dim_categories, facts, reconciliations)

        return TransformResult(
            dim_cities=list(dim_cities.values()),
            dim_dates=list(dim_dates.values()),
            dim_categories=list(dim_categories.values()),
            facts=facts,
            reconciliations=reconciliations,
            rejected=rejected,
        )

    # -- internals ----------------------------------------------------------

    def _validate_period(self, rec: RawRecord, rejected: list[dict]) -> tuple[int, int] | None:
        if rec.fiscal_year is None or rec.fiscal_month is None:
            rejected.append({
                "source_row_number": rec.source_row_number,
                "reason": "missing fiscal_year/fiscal_month",
                "payload": rec.__dict__,
            })
            return None
        try:
            fiscal_year = int(float(rec.fiscal_year))
            fiscal_month = int(float(rec.fiscal_month))
        except ValueError:
            rejected.append({
                "source_row_number": rec.source_row_number,
                "reason": f"non-numeric fiscal_year/fiscal_month: {rec.fiscal_year!r}/{rec.fiscal_month!r}",
                "payload": rec.__dict__,
            })
            return None
        if not (1 <= fiscal_month <= 12):
            rejected.append({
                "source_row_number": rec.source_row_number,
                "reason": f"fiscal_month out of range: {fiscal_month}",
                "payload": rec.__dict__,
            })
            return None
        return fiscal_year, fiscal_month

    def _transform_categories(self, rec: RawRecord, date_key: int,
                               dim_categories: dict[str, DimCategory],
                               facts: list[FactRow],
                               reconciliations: list[ReconciliationRow]) -> None:
        for order, (block_key, statuses) in enumerate(rec.category_columns.items()):
            _, category_name = block_key.split(":", 1)
            category_code = f"CAT_{order + 1}" if order < 7 else "CAT_GRAND_TOTAL"
            dim_categories.setdefault(
                category_code,
                DimCategory(category_code=category_code, category_name=category_name, display_order=order + 1),
            )
            if category_code == "CAT_GRAND_TOTAL":
                # This block is the row's overall total across all categories,
                # not a category in its own right — used only as a sanity
                # check, not modeled as an 8th dim_category member.
                continue

            reported_total = None
            derived_total = 0
            for status_label, raw_value in statuses.items():
                value = self._to_int(
                    raw_value,
                    context=f"row {rec.source_row_number} / {category_name} / {status_label}",
                )
                if self.TOTAL_COLUMN_PATTERN.search(status_label):
                    reported_total = value
                    continue
                derived_total += value
                facts.append(
                    FactRow(
                        city_name=rec.city_name,
                        date_key=date_key,
                        category_code=category_code,
                        status_code=self._status_code(status_label),
                        status_name=status_label.strip(),
                        open_work_order_count=value,
                    )
                )

            if reported_total is not None:
                reconciliations.append(
                    ReconciliationRow(
                        city_name=rec.city_name,
                        date_key=date_key,
                        category_code=category_code,
                        reported_total=reported_total,
                        derived_total=derived_total,
                    )
                )
                if reported_total != derived_total:
                    logger.warning(
                        "Reconciliation mismatch: city=%s period=%s category=%s reported=%s derived=%s",
                        rec.city_name, date_key, category_code, reported_total, derived_total,
                    )

    @staticmethod
    def _to_int(value, *, context: str) -> int:
        """Coerce a raw cell to a non-negative int, logging (not silently
        swallowing) anything unexpected. NaN/blank -> 0, since an empty status
        cell in this report means 'no work orders in that stage', not 'unknown'.
        """
        if value is None or (isinstance(value, float) and value != value):  # NaN
            return 0
        try:
            n = int(float(value))
        except (TypeError, ValueError):
            logger.warning("Non-numeric value %r at %s; coercing to 0", value, context)
            return 0
        if n < 0:
            logger.warning("Negative value %s at %s; coercing to 0", n, context)
            return 0
        return n

    @classmethod
    def _status_code(cls, label: str) -> str:
        label = label.strip()
        return cls.CANONICAL_STATUS_CODES.get(label, re.sub(r"\W+", "_", label).strip("_").upper() or "UNKNOWN")


# Backwards-compatible functional entrypoint (also what the existing test
# suite in tests/etl/test_transform.py imports).
def transform(records: Iterable[RawRecord]) -> TransformResult:
    return WorkOrderTransformer().transform(records)
