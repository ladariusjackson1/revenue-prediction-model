"""The committed UCI aggregates must match the forecast series and the explorer."""

from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path

from finance.money import format_pence

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = ROOT / "finance" / "outputs" / "uci_snapshot.json"
DAILY_MART = ROOT / "finance" / "outputs" / "daily_merchandise.csv"
FORECAST_DAILY = ROOT / "projects" / "01-daily-sales-forecast" / "data" / "daily_revenue.csv"
DEMO = ROOT / "docs" / "revenue-quality" / "index.html"
WORKBOOK_SHA256 = "43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d"


def _pence(text: str) -> int:
    return int((Decimal(text) * 100).quantize(Decimal("1")))


def test_snapshot_identities_and_source_hash():
    snapshot = json.loads(SNAPSHOT_PATH.read_text())
    assert snapshot["source_name"] == "UCI Online Retail"
    assert snapshot["license"] == "CC BY 4.0"
    assert snapshot["currency"] == "GBP"
    assert snapshot["xlsx_sha256"] == WORKBOOK_SHA256
    assert snapshot["raw_rows"] == 541909
    assert snapshot["net_pence"] == 976276055
    assert snapshot["gross_pence"] + snapshot["returns_pence"] + snapshot["cancellations_pence"] == snapshot["net_pence"]
    assert snapshot["returns_pence"] == 0
    assert snapshot["negative_qty_kept_rows"] == 0
    assert snapshot["negative_qty_bad_price_rows"] == 1324
    assert snapshot["negative_qty_non_product_rows"] == 12
    assert snapshot["duplicate_extra_pence"] == 2137110
    assert snapshot["duplicate_bridge"]["net_if_extras_removed_pence"] == snapshot["net_pence"] - snapshot["duplicate_extra_pence"]
    assert snapshot["days"] == 373
    assert snapshot["zero_days"] == 69
    assert snapshot["start_date"] == "2010-12-01"
    assert snapshot["end_date"] == "2011-12-08"
    assert snapshot["identified_customers"] == 4361
    assert snapshot["active_one_month_later"] == 1122
    assert snapshot["missing_customer_pence"] == 149172313
    assert snapshot["adjustment_invoice_pence"] == -1106206
    assert snapshot["partial_rows"] == 1632
    assert snapshot["unparseable_rows"] == 4
    statuses = {row["check_name"]: row["status"] for row in snapshot["quality_checks"]}
    assert statuses["recon_lines_equal_daily"] == "pass"
    assert statuses["recon_components_equal_net"] == "pass"
    assert statuses["calendar_has_no_gaps"] == "pass"


def test_daily_mart_matches_the_forecast_series_to_the_penny():
    forecast = list(csv.DictReader(FORECAST_DAILY.open()))
    mart = list(csv.DictReader(DAILY_MART.open()))
    assert len(forecast) == len(mart) == 373
    for left, right in zip(forecast, mart):
        assert left["date"] == right["revenue_date"]
        assert _pence(left["revenue"]) == int(right["net_merchandise_pence"])


def test_explorer_quotes_the_snapshot_rather_than_the_fixture():
    snapshot = json.loads(SNAPSHOT_PATH.read_text())
    page = DEMO.read_text()
    assert format_pence(snapshot["net_pence"]) in page
    assert format_pence(snapshot["duplicate_extra_pence"]) in page
    assert snapshot["xlsx_sha256"] in page
    assert "£46.43" not in page
    assert "COMMA DECIMAL" not in page
    assert "not a client engagement" in page
