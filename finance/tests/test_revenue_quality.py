"""Behavior tests for the revenue ledger. Amounts are integer pence."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from finance.money import format_pence, to_int, to_pence
from finance.pipeline import ROOT, build_csv, failing_checks, quality, summary

FIXTURE = ROOT / "fixtures" / "online_retail_messy.csv"
# Rows kept under the forecast-matching rule, including one exact-duplicate extra.
# 1530+1530+255+678-500-500+400+300+150+800 = 4643
EXPECTED_NET_PENCE = 4643
EXPECTED_DUPLICATE_EXTRA_PENCE = 1530
EXPECTED_RETURNS_PENCE = -500
EXPECTED_CANCELLATIONS_PENCE = -500


def _build(tmp_path: Path) -> sqlite3.Connection:
    return build_csv(FIXTURE, tmp_path / "ledger", source_name="fixture")


def test_money_parser_rejects_symbols_commas_and_extra_decimals():
    assert to_pence("2.55") == 255
    assert to_pence("2.5") == 250
    assert to_pence("2") == 200
    assert to_pence("-1.00") == -100
    assert to_pence("0") == 0
    assert to_pence("£2.50") is None
    assert to_pence("1,25") is None
    assert to_pence("0.001") is None
    assert to_pence("") is None
    assert to_int("-1") == -1
    assert to_int("1.5") is None
    assert format_pence(EXPECTED_NET_PENCE) == "£46.43"
    assert format_pence(-500) == "-£5.00"


def test_fixture_reconciles_and_names_every_messy_case(tmp_path: Path):
    connection = _build(tmp_path)
    checks = quality(connection)
    assert failing_checks(connection) == []
    totals = summary(connection)
    assert totals["net_pence"] == EXPECTED_NET_PENCE
    assert totals["returns_pence"] == EXPECTED_RETURNS_PENCE
    assert totals["cancellations_pence"] == EXPECTED_CANCELLATIONS_PENCE
    assert totals["duplicate_extra_pence"] == EXPECTED_DUPLICATE_EXTRA_PENCE
    assert totals["gross_pence"] + totals["returns_pence"] + totals["cancellations_pence"] == totals["net_pence"]

    assert checks["finding_duplicate_extras"]["status"] == "observed"
    assert checks["finding_duplicate_extras"]["observed"] == EXPECTED_DUPLICATE_EXTRA_PENCE
    assert checks["finding_missing_customer"]["status"] == "observed"
    assert checks["finding_missing_customer"]["observed"] == 1
    assert checks["finding_unparseable"]["status"] == "observed"
    assert checks["finding_unparseable"]["observed"] == 4
    assert checks["finding_partial_day"]["status"] == "observed"
    assert checks["finding_partial_day"]["observed"] == 1
    assert checks["finding_non_product"]["status"] == "observed"
    assert checks["finding_non_product"]["observed"] == 2
    assert checks["finding_bad_price"]["status"] == "observed"
    assert checks["finding_bad_price"]["observed"] == 2

    partial = connection.execute(
        """
        SELECT line_amount_pence FROM staging.stg_invoice_line
        WHERE invoice_no = '700'
        """
    ).fetchone()
    assert partial["line_amount_pence"] == 900
    assert connection.execute(
        "SELECT disposition FROM staging.stg_invoice_line WHERE invoice_no = '700'"
    ).fetchone()["disposition"] == "excluded_partial_day"

    zero_day = connection.execute(
        "SELECT net_merchandise_pence FROM mart.daily_revenue WHERE revenue_date = '2010-12-06'"
    ).fetchone()
    assert zero_day["net_merchandise_pence"] == 0
    assert totals["days"] == 46


def test_cohort_excludes_blank_customers_and_keeps_repeat_purchases(tmp_path: Path):
    connection = _build(tmp_path)
    rows = connection.execute(
        """
        SELECT cohort_month, activity_month, month_index, customers, net_merchandise_pence
        FROM mart.customer_cohort
        ORDER BY cohort_month, month_index
        """
    ).fetchall()
    assert [(row["cohort_month"], row["month_index"], row["customers"], row["net_merchandise_pence"]) for row in rows] == [
        ("2010-12-01", 0, 1, 3793),
        ("2010-12-01", 1, 1, 150),
        ("2011-01-01", 0, 1, 300),
    ]
    missing = connection.execute(
        """
        SELECT SUM(line_amount_pence) AS pence
        FROM staging.stg_invoice_line
        WHERE missing_customer = 1
          AND disposition IN ('kept_merchandise', 'kept_duplicate_extra')
        """
    ).fetchone()
    assert missing["pence"] == 400


def test_country_window_ranks_ship_to_country_without_fx(tmp_path: Path):
    connection = _build(tmp_path)
    ranks = connection.execute(
        """
        SELECT country, net_merchandise_pence, revenue_rank
        FROM mart.country_revenue
        ORDER BY revenue_rank, country
        """
    ).fetchall()
    assert [(row["country"], row["net_merchandise_pence"], row["revenue_rank"]) for row in ranks] == [
        ("United Kingdom", 4193, 1),
        ("Germany", 300, 2),
        ("France", 150, 3),
    ]


def test_rerun_does_not_double_revenue(tmp_path: Path):
    work = tmp_path / "ledger"
    first = build_csv(FIXTURE, work, source_name="fixture")
    first_net = summary(first)["net_pence"]
    first.close()
    second = build_csv(FIXTURE, work, source_name="fixture")
    assert summary(second)["net_pence"] == first_net == EXPECTED_NET_PENCE
    assert second.execute("SELECT COUNT(*) AS n FROM raw.invoice_line").fetchone()["n"] == 19
    assert second.execute("SELECT COUNT(*) AS n FROM raw.load_run").fetchone()["n"] == 2
    assert failing_checks(second) == []


def test_reconciliation_query_fails_when_the_mart_is_tampered(tmp_path: Path):
    connection = _build(tmp_path)
    assert failing_checks(connection) == []
    connection.execute(
        """
        UPDATE mart.daily_revenue
        SET net_merchandise_pence = net_merchandise_pence + 1
        WHERE revenue_date = '2010-12-01'
        """
    )
    checks = quality(connection)
    assert checks["recon_lines_equal_daily"]["status"] == "fail"
    assert checks["recon_lines_equal_daily"]["observed"] == -1
    difference = connection.execute((ROOT / "sql" / "examples" / "01_reconciliation.sql").read_text()).fetchone()
    assert difference["difference_pence"] == -1


def test_example_queries_run_against_the_fixture(tmp_path: Path):
    connection = _build(tmp_path)
    examples = sorted((ROOT / "sql" / "examples").glob("*.sql"))
    assert len(examples) >= 6
    for path in examples:
        rows = connection.execute(path.read_text()).fetchall()
        assert rows, path.name
    bridge = connection.execute((ROOT / "sql" / "examples" / "05_duplicate_bridge.sql").read_text()).fetchone()
    assert bridge["net_including_duplicate_extras_pence"] == EXPECTED_NET_PENCE
    assert bridge["duplicate_extra_pence"] == EXPECTED_DUPLICATE_EXTRA_PENCE
    assert bridge["net_if_extras_removed_pence"] == EXPECTED_NET_PENCE - EXPECTED_DUPLICATE_EXTRA_PENCE
    movements = {
        row["movement"]: row["amount_pence"]
        for row in connection.execute(
            (ROOT / "sql" / "examples" / "02_returns_and_cancellations.sql").read_text()
        )
    }
    assert movements["return_not_cancellation"] == EXPECTED_RETURNS_PENCE
    assert movements["cancellation_invoice"] == EXPECTED_CANCELLATIONS_PENCE
