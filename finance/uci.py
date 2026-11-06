"""Read the UCI workbook into the same row shape as the CSV fixture.

Requires pandas and openpyxl, which the default offline test command does not.
"""

from __future__ import annotations

from pathlib import Path

from finance.pipeline import COLUMNS


def read_uci_rows(xlsx_path: Path) -> list[dict[str, str]]:
    import pandas as pd

    frame = pd.read_excel(xlsx_path, dtype=str)
    missing = [column for column in COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"{xlsx_path} is missing column(s): {', '.join(missing)}")
    frame = frame[list(COLUMNS)].fillna("")
    rows: list[dict[str, str]] = []
    for record in frame.to_dict(orient="records"):
        cleaned = {}
        for column in COLUMNS:
            value = record[column]
            text = "" if value is None else str(value).strip()
            if text.lower() in {"nan", "none", "nat"}:
                text = ""
            cleaned[column] = text
        rows.append(cleaned)
    return rows
