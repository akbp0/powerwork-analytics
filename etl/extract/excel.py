from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from etl.base import BaseExtractor

AGGREGATE_ROW_LABELS = {"جمع به تفکیک هر واحد", "کل شرکت"}


@dataclass
class RawRecord:
    source_row_number: int
    city_name: str | None
    business_unit_code: str | None
    fiscal_year: str | None
    fiscal_month: str | None
    category_columns: dict = field(default_factory=dict)
    is_aggregate_row: bool = False


class ExcelExtractor(BaseExtractor[RawRecord]):

    FIXED_COLUMNS = 4  # city_name, business_unit_code, fiscal_year, fiscal_month

    # Each category block's column width, in source-column order. Determined
    # by profiling row 1 / row 2 of the source file. Column counts vary per
    # block (5, 5, 5, 6, 6, 6, 6) plus a trailing 6-wide grand-total block —
    # this is exactly why the raw layer stores category_columns as JSONB
    # rather than fixed columns (see sql/source/001_create_raw_tables.sql).
    CATEGORY_BLOCK_SIZES = [5, 5, 5, 6, 6, 6, 6]
    GRAND_TOTAL_BLOCK_SIZE = 6

    AGGREGATE_ROW_LABELS = AGGREGATE_ROW_LABELS

    def extract(self, path: Path, sheet_name: str | int = 0) -> list[RawRecord]:
        """Read the workbook and return one RawRecord per data row (rows 3..N)."""
        df = pd.read_excel(path, sheet_name=sheet_name, header=None)

        header_row1 = df.iloc[1].tolist()  # category group labels
        header_row2 = df.iloc[2].tolist()  # per-status labels within each group
        category_group_labels = [
            str(v) for v in header_row1[self.FIXED_COLUMNS:] if pd.notna(v)
        ]  # 7 category labels + 1 grand-total label, in column order

        block_sizes = self.CATEGORY_BLOCK_SIZES + [self.GRAND_TOTAL_BLOCK_SIZE]

        records: list[RawRecord] = []
        for row_idx in range(3, len(df)):
            row = df.iloc[row_idx].tolist()
            city_name = row[0] if pd.notna(row[0]) else None
            if city_name is None:
                continue  # fully blank spacer row, if any

            category_payload: dict = {}
            col = self.FIXED_COLUMNS
            for block_i, size in enumerate(block_sizes):
                label = category_group_labels[block_i] if block_i < len(category_group_labels) else f"block_{block_i}"
                statuses = self._status_labels_for_block(header_row2, col, size)
                values = row[col:col + size]
                category_payload[f"{block_i}:{label}"] = dict(zip(statuses, values))
                col += size

            records.append(
                RawRecord(
                    source_row_number=row_idx + 1,  # 1-based, matches the spreadsheet row
                    city_name=str(city_name),
                    business_unit_code=str(row[1]) if pd.notna(row[1]) else None,
                    fiscal_year=str(row[2]) if pd.notna(row[2]) else None,
                    fiscal_month=str(row[3]) if pd.notna(row[3]) else None,
                    category_columns=category_payload,
                    is_aggregate_row=str(city_name) in self.AGGREGATE_ROW_LABELS,
                )
            )
        return records

    @staticmethod
    def _status_labels_for_block(header_row2: list, start: int, size: int) -> list[str]:
        return [str(v) if pd.notna(v) else f"status_{i}" for i, v in enumerate(header_row2[start:start + size])]


def extract_excel(path: Path) -> pd.DataFrame:
    return pd.read_excel(path)


# Backwards-compatible functional entrypoint, so any external caller (or a
# quick shell one-liner) written against the old free-function API keeps
# working without change.
def extract_raw(path: Path, sheet_name: str | int = 0) -> list[RawRecord]:
    return ExcelExtractor().extract(path, sheet_name=sheet_name)
