"""Load an invoice extract into raw, staging, and mart SQLite databases.

A run is a full refresh: fact tables are replaced, and raw.load_run gains one
row. Running the same file twice does not double revenue.
"""

from __future__ import annotations

import csv
import hashlib
import sqlite3
from pathlib import Path

from finance.money import to_int, to_pence

ROOT = Path(__file__).resolve().parent
SQL_DIR = ROOT / "sql"
COLUMNS = (
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
)


def connect(work_dir: Path) -> sqlite3.Connection:
    """Attach raw, staging, and mart as three database files."""
    work_dir.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(work_dir / "pipeline.sqlite")
    connection.row_factory = sqlite3.Row
    for name in ("raw", "staging", "mart"):
        connection.execute(f"ATTACH DATABASE ? AS {name}", (str(work_dir / f"{name}.sqlite"),))
    connection.create_function("to_pence", 1, to_pence, deterministic=True)
    connection.create_function("to_int", 1, to_int, deterministic=True)
    return connection


def _script(connection: sqlite3.Connection, name: str) -> None:
    connection.executescript((SQL_DIR / name).read_text())


def _blank(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "nat"}:
        return ""
    return text


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [column for column in COLUMNS if reader.fieldnames is None or column not in reader.fieldnames]
        if missing:
            raise ValueError(f"{path} is missing column(s): {', '.join(missing)}")
        return [{column: _blank(row.get(column)) for column in COLUMNS} for row in reader]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(rows: list[dict[str, str]], work_dir: Path, source_name: str, sha256: str) -> sqlite3.Connection:
    """Refresh the ledger from an in-memory row list. Returns an open connection."""
    connection = connect(work_dir)
    _script(connection, "00_schema.sql")
    _script(connection, "05_reset_facts.sql")
    connection.executemany(
        """
        INSERT INTO raw.invoice_line (
          source_row_number, invoice_no, stock_code, description,
          quantity_text, invoice_ts, unit_price_text, customer_id, country
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                index,
                row["InvoiceNo"],
                row["StockCode"],
                row["Description"],
                row["Quantity"],
                row["InvoiceDate"],
                row["UnitPrice"],
                row["CustomerID"],
                row["Country"],
            )
            for index, row in enumerate(rows, start=1)
        ],
    )
    connection.execute(
        "INSERT INTO raw.load_run (source_name, sha256, row_count) VALUES (?, ?, ?)",
        (source_name, sha256, len(rows)),
    )
    _script(connection, "10_stage.sql")
    _script(connection, "20_marts.sql")
    _script(connection, "30_quality.sql")
    connection.commit()
    return connection


def build_csv(path: Path, work_dir: Path, source_name: str | None = None) -> sqlite3.Connection:
    rows = read_csv(path)
    return build(rows, work_dir, source_name or path.name, sha256_file(path))


def quality(connection: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    _script(connection, "30_quality.sql")
    connection.commit()
    rows = connection.execute("SELECT * FROM mart.quality_check ORDER BY check_name").fetchall()
    return {row["check_name"]: row for row in rows}


def failing_checks(connection: sqlite3.Connection) -> list[str]:
    return [
        row["check_name"]
        for row in connection.execute(
            "SELECT check_name FROM mart.quality_check WHERE status = 'fail' ORDER BY check_name"
        )
    ]


def summary(connection: sqlite3.Connection) -> dict[str, int]:
    row = connection.execute(
        """
        SELECT
          SUM(net_merchandise_pence) AS net_pence,
          SUM(gross_sales_pence) AS gross_pence,
          SUM(returns_pence) AS returns_pence,
          SUM(cancellations_pence) AS cancellations_pence,
          SUM(duplicate_extra_pence) AS duplicate_extra_pence,
          COUNT(*) AS days,
          SUM(CASE WHEN net_merchandise_pence = 0 THEN 1 ELSE 0 END) AS zero_days
        FROM mart.daily_revenue
        """
    ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}
