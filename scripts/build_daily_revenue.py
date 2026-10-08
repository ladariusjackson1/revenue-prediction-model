"""Download UCI Online Retail and write data/daily_revenue.csv.

Source: https://archive.ics.uci.edu/dataset/352/online+retail
License: Creative Commons Attribution 4.0 International (CC BY 4.0)

The raw workbook is about 23 MB and is not committed. This script rebuilds the
small daily aggregate that the rest of the project reads.
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.forecast import daily_net_sales, write_daily_revenue  # noqa: E402

SOURCE_URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
RAW_DIR = ROOT / "data" / "raw"
WORKBOOK_NAME = "Online Retail.xlsx"


def download_workbook(destination: Path = RAW_DIR / WORKBOOK_NAME) -> Path:
    """Download the UCI zip and extract the workbook."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    zip_path = destination.with_suffix(".zip")
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "revenue-forecast-dataset-build"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        zip_path.write_bytes(response.read())
    with zipfile.ZipFile(zip_path) as archive:
        member = next(name for name in archive.namelist() if name.endswith(".xlsx"))
        archive.extract(member, destination.parent)
        extracted = destination.parent / member
    if extracted.resolve() != destination.resolve():
        extracted.replace(destination)
    return destination


def build(workbook: Path, output: Path) -> pd.DataFrame:
    print(f"Reading {workbook}")
    transactions = pd.read_excel(workbook, engine="openpyxl")
    print(f"Invoice lines in workbook: {len(transactions):,}")
    daily = daily_net_sales(transactions)
    write_daily_revenue(daily, output)
    print(
        f"Wrote {len(daily):,} days to {output} "
        f"({daily['date'].min().date()} to {daily['date'].max().date()})"
    )
    print(f"Total net sales: £{daily['revenue'].sum():,.2f}")
    print(f"Zero-sales days: {int((daily['revenue'] == 0).sum())}")
    return daily


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workbook",
        type=Path,
        help="Existing .xlsx to aggregate. Downloads the UCI file when omitted.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data" / "daily_revenue.csv",
    )
    args = parser.parse_args()
    workbook = args.workbook if args.workbook else download_workbook()
    build(workbook, args.output)


if __name__ == "__main__":
    main()
