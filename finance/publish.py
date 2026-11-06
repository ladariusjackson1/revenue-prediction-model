"""Build the UCI snapshot and the static explorer from a finished ledger."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from finance.money import format_pence
from finance.pipeline import failing_checks, sha256_file, summary

OUTPUTS = Path(__file__).resolve().parent / "outputs"
DEMO_PATH = Path(__file__).resolve().parents[1] / "docs" / "revenue-quality" / "index.html"

SOURCE_URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
CITATION = (
    "Daqing Chen, Sai Laing Sain, and Kun Guo (2012). "
    "Data mining for the online retail industry: A case study of RFM model-based "
    "customer segmentation using data mining. Journal of Database Marketing and "
    "Customer Strategy Management, 19(3)."
)


def _rows(connection, sql: str) -> list[dict]:
    return [dict(row) for row in connection.execute(sql)]


def write_outputs(connection, xlsx_path: Path, retrieved_on: str) -> dict:
    """Write aggregate files. No customer-level rows are published."""
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    if failing_checks(connection):
        raise RuntimeError(f"Quality checks failed: {failing_checks(connection)}")

    totals = summary(connection)
    checks = _rows(connection, "SELECT check_name, status, observed, detail FROM mart.quality_check ORDER BY check_name")
    countries = _rows(
        connection,
        """
        SELECT country, net_merchandise_pence, line_count, share_bps, revenue_rank
        FROM mart.country_revenue
        ORDER BY revenue_rank, country
        """,
    )
    cohorts = _rows(
        connection,
        """
        SELECT cohort_month, month_index,
               SUM(customers) AS customers,
               SUM(net_merchandise_pence) AS net_merchandise_pence
        FROM mart.customer_cohort
        GROUP BY cohort_month, month_index
        ORDER BY cohort_month, month_index
        """,
    )
    repeat = connection.execute(
        """
        SELECT
          SUM(CASE WHEN month_index = 0 THEN customers ELSE 0 END) AS identified_customers,
          SUM(CASE WHEN month_index = 1 THEN customers ELSE 0 END) AS active_next_month
        FROM mart.customer_cohort
        """
    ).fetchone()
    movements = _rows(
        connection,
        (Path(__file__).resolve().parent / "sql" / "examples" / "02_returns_and_cancellations.sql").read_text(),
    )
    bridge = dict(
        connection.execute(
            (Path(__file__).resolve().parent / "sql" / "examples" / "05_duplicate_bridge.sql").read_text()
        ).fetchone()
    )
    findings = connection.execute(
        """
        SELECT
          SUM(CASE WHEN disposition = 'excluded_partial_day' THEN 1 ELSE 0 END) AS partial_rows,
          SUM(CASE WHEN disposition = 'excluded_non_product' THEN 1 ELSE 0 END) AS non_product_rows,
          SUM(CASE WHEN disposition = 'excluded_bad_price' THEN 1 ELSE 0 END) AS bad_price_rows,
          SUM(CASE WHEN disposition = 'excluded_unparseable' THEN 1 ELSE 0 END) AS unparseable_rows,
          SUM(CASE WHEN missing_customer = 1
                    AND disposition IN ('kept_merchandise', 'kept_duplicate_extra')
                   THEN 1 ELSE 0 END) AS missing_customer_rows,
          SUM(CASE WHEN missing_customer = 1
                    AND disposition IN ('kept_merchandise', 'kept_duplicate_extra')
                   THEN line_amount_pence ELSE 0 END) AS missing_customer_pence,
          SUM(CASE WHEN invoice_no LIKE 'A%' THEN 1 ELSE 0 END) AS adjustment_invoice_rows,
          SUM(CASE WHEN invoice_no LIKE 'A%' THEN COALESCE(line_amount_pence, 0) ELSE 0 END) AS adjustment_invoice_pence,
          SUM(CASE WHEN is_return = 1 AND disposition = 'excluded_bad_price' THEN 1 ELSE 0 END) AS negative_qty_bad_price_rows,
          SUM(CASE WHEN is_return = 1 AND disposition = 'excluded_non_product' THEN 1 ELSE 0 END) AS negative_qty_non_product_rows,
          SUM(CASE WHEN is_return = 1 AND disposition IN ('kept_merchandise', 'kept_duplicate_extra') THEN 1 ELSE 0 END) AS negative_qty_kept_rows
        FROM staging.stg_invoice_line
        """
    ).fetchone()
    span = connection.execute(
        "SELECT MIN(revenue_date) AS start_date, MAX(revenue_date) AS end_date FROM mart.daily_revenue"
    ).fetchone()
    raw_rows = connection.execute("SELECT COUNT(*) AS n FROM raw.invoice_line").fetchone()["n"]

    daily_path = OUTPUTS / "daily_merchandise.csv"
    with daily_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "revenue_date",
                "gross_sales_pence",
                "returns_pence",
                "cancellations_pence",
                "net_merchandise_pence",
                "duplicate_extra_pence",
                "line_count",
            ],
        )
        writer.writeheader()
        for row in connection.execute(
            """
            SELECT revenue_date, gross_sales_pence, returns_pence, cancellations_pence,
                   net_merchandise_pence, duplicate_extra_pence, line_count
            FROM mart.daily_revenue
            ORDER BY revenue_date
            """
        ):
            writer.writerow(dict(row))

    _write_csv(OUTPUTS / "country_revenue.csv", countries)
    _write_csv(OUTPUTS / "cohort_by_month.csv", cohorts)

    snapshot = {
        "source_name": "UCI Online Retail",
        "citation": CITATION,
        "source_url": "https://archive.ics.uci.edu/dataset/352/online+retail",
        "download_url": SOURCE_URL,
        "license": "CC BY 4.0",
        "license_url": LICENSE_URL,
        "currency": "GBP",
        "xlsx_sha256": sha256_file(xlsx_path),
        "xlsx_bytes": xlsx_path.stat().st_size,
        "retrieved_on": retrieved_on,
        "raw_rows": int(raw_rows),
        "start_date": span["start_date"],
        "end_date": span["end_date"],
        **totals,
        "duplicate_bridge": {key: int(value) for key, value in bridge.items()},
        "movements": movements,
        "identified_customers": int(repeat["identified_customers"] or 0),
        "active_one_month_later": int(repeat["active_next_month"] or 0),
        "partial_rows": int(findings["partial_rows"] or 0),
        "non_product_rows": int(findings["non_product_rows"] or 0),
        "bad_price_rows": int(findings["bad_price_rows"] or 0),
        "unparseable_rows": int(findings["unparseable_rows"] or 0),
        "missing_customer_rows": int(findings["missing_customer_rows"] or 0),
        "missing_customer_pence": int(findings["missing_customer_pence"] or 0),
        "adjustment_invoice_rows": int(findings["adjustment_invoice_rows"] or 0),
        "adjustment_invoice_pence": int(findings["adjustment_invoice_pence"] or 0),
        "negative_qty_bad_price_rows": int(findings["negative_qty_bad_price_rows"] or 0),
        "negative_qty_non_product_rows": int(findings["negative_qty_non_product_rows"] or 0),
        "negative_qty_kept_rows": int(findings["negative_qty_kept_rows"] or 0),
        "countries": countries,
        "quality_checks": checks,
    }
    (OUTPUTS / "uci_snapshot.json").write_text(json.dumps(snapshot, indent=2) + "\n")
    return snapshot


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def render_demo(snapshot: dict) -> str:
    """Static page. Every figure is formatted from the snapshot integers."""
    net = format_pence(snapshot["net_pence"])
    gross = format_pence(snapshot["gross_pence"])
    cancels = format_pence(snapshot["cancellations_pence"])
    returns = format_pence(snapshot["returns_pence"])
    dup = format_pence(snapshot["duplicate_extra_pence"])
    deduped = format_pence(snapshot["net_pence"] - snapshot["duplicate_extra_pence"])
    missing = format_pence(snapshot["missing_customer_pence"])
    adjustments = format_pence(snapshot["adjustment_invoice_pence"])
    countries = "".join(
        "<tr>"
        f"<td>{_esc(row['country'])}</td>"
        f"<td>{row['revenue_rank']}</td>"
        f"<td>{format_pence(row['net_merchandise_pence'])}</td>"
        f"<td>{row['share_bps'] / 100:.2f}%</td>"
        f"<td>{row['line_count']:,}</td>"
        "</tr>"
        for row in snapshot["countries"][:8]
    )
    checks = "".join(
        "<tr>"
        f"<td><code>{_esc(row['check_name'])}</code></td>"
        f"<td>{_esc(row['status'])}</td>"
        f"<td>{row['observed']:,}</td>"
        f"<td>{_esc(row['detail'])}</td>"
        "</tr>"
        for row in snapshot["quality_checks"]
    )
    identified = snapshot["identified_customers"]
    came_back = snapshot["active_one_month_later"]
    comeback = f"{came_back / identified:.1%}" if identified else "n/a"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Revenue quality — UCI Online Retail</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #0b1f2a;
      --muted: #3a5563;
      --line: #d5dee3;
      --paper: #f4f7f8;
      --panel: #fff;
      --accent: #0d8a6a;
    }}
    body {{
      margin: 0;
      font: 16px/1.5 "Segoe UI", Helvetica, Arial, sans-serif;
      color: var(--ink);
      background: var(--paper);
    }}
    main {{ max-width: 980px; margin: 0 auto; padding: 32px 20px 64px; }}
    h1 {{ font-size: 2rem; line-height: 1.2; margin-bottom: 0.2em; }}
    h2 {{ margin-top: 2rem; }}
    p, li {{ color: var(--ink); }}
    .muted {{ color: var(--muted); }}
    .banner {{
      background: #fff8e8;
      border: 1px solid #ecd9a4;
      border-radius: 12px;
      padding: 12px 14px;
    }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }}
    .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; }}
    .card b {{ display: block; font-size: 1.35rem; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); }}
    th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }}
    th {{ font-size: 0.85rem; color: var(--muted); }}
    code, pre {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
    pre {{ background: #0b1f2a; color: #f4f7f8; padding: 14px; border-radius: 12px; overflow: auto; }}
    a {{ color: var(--accent); }}
  </style>
</head>
<body>
<main>
  <p class="muted">Finance analytics case study · public research extract · not a client engagement</p>
  <h1>Can this retail extract support a revenue number?</h1>
  <p>Question: for the UCI Online Retail gift wholesaler, what merchandise revenue is left after cancellations, non-product lines, bad prices, and a partial final day — and does that daily mart tie back to the invoice lines to the penny?</p>
  <div class="banner">
    <strong>These figures are aggregates from the public file, not a forecast and not a business result.</strong>
    Nobody adopted this pipeline. It does not estimate ROI. The retailer is the one in the UCI citation, not a client of this portfolio.
  </div>

  <h2>Headline, in GBP pence carried as integers</h2>
  <div class="grid">
    <div class="card"><span class="muted">Net merchandise</span><b>{net}</b><span class="muted">{snapshot['start_date']} to {snapshot['end_date']}</span></div>
    <div class="card"><span class="muted">Gross sales</span><b>{gross}</b><span class="muted">positive merchandise lines</span></div>
    <div class="card"><span class="muted">Cancellations</span><b>{cancels}</b><span class="muted">invoice numbers starting with C</span></div>
    <div class="card"><span class="muted">Other returns</span><b>{returns}</b><span class="muted">negative qty, not a C invoice</span></div>
  </div>
  <p>Identity held by the quality check <code>recon_components_equal_net</code>: gross + cancellations + other returns = net. Calendar days: {snapshot['days']:,}. Days with £0.00 net: {snapshot['zero_days']:,}. Source rows: {snapshot['raw_rows']:,}.</p>

  <h2>Duplicate sensitivity</h2>
  <p>The forecast-matching total <strong>keeps</strong> exact duplicate extras, because that is what the published daily series does. Removing them would change the total. That difference is a decision, not a discovered fact about the shop floor.</p>
  <div class="grid">
    <div class="card"><span class="muted">Net, duplicates kept</span><b>{net}</b></div>
    <div class="card"><span class="muted">Exact-duplicate extras inside that net</span><b>{dup}</b></div>
    <div class="card"><span class="muted">Net if those extras are removed</span><b>{deduped}</b></div>
  </div>

  <h2>What was left out, and what was kept without a customer</h2>
  <ul>
    <li>Partial final day rows: {snapshot['partial_rows']:,}. The file's last timestamp is before 16:00, so that calendar day is not a full trading day.</li>
    <li>Non-product stock codes (postage, fees, manual codes, gift vouchers, letter-prefixed goods): {snapshot['non_product_rows']:,} rows.</li>
    <li>Invoice numbers starting with A, including the bad-debt adjustments: {snapshot['adjustment_invoice_rows']:,} rows, signed amount {adjustments}. They are not in the merchandise total.</li>
    <li>Other returns inside the merchandise total: {snapshot['negative_qty_kept_rows']:,} lines, {returns}. Negative quantities that are not cancellation invoices and did not survive the rules: {snapshot['negative_qty_bad_price_rows']:,} with a non-positive price, {snapshot['negative_qty_non_product_rows']:,} with a non-product code.</li>
    <li>Unparseable date, quantity, or price: {snapshot['unparseable_rows']:,}. Prices with a currency symbol, a comma, or more than two decimal places are not rounded into the ledger. Bad parsed prices (zero or negative): {snapshot['bad_price_rows']:,}.</li>
    <li>Kept lines with no customer id: {snapshot['missing_customer_rows']:,} rows, {missing}. They are in revenue. They are not in the cohort.</li>
  </ul>

  <h2>Customers who can be followed</h2>
  <p>{identified:,} customer ids have at least one kept merchandise line. {came_back:,} of them ({comeback}) also have kept merchandise in the following calendar month. That is a one-month repeat count on this extract, not a retention rate for a subscription and not a lifetime value.</p>

  <h2>Ship-to country</h2>
  <p>Unit prices in this file are GBP. Country is where the order was shipped, not a second currency. Share is truncated integer basis points, so the column can sum to slightly under 100%.</p>
  <table>
    <thead><tr><th>Country</th><th>Rank</th><th>Net</th><th>Share</th><th>Lines</th></tr></thead>
    <tbody>{countries}</tbody>
  </table>

  <h2>Quality checks on this snapshot</h2>
  <table>
    <thead><tr><th>Check</th><th>Status</th><th>Observed</th><th>Meaning</th></tr></thead>
    <tbody>{checks}</tbody>
  </table>

  <h2>How the number is rebuilt</h2>
  <ol>
    <li><code>raw</code> stores every source field as text, plus a row in <code>load_run</code> for each refresh.</li>
    <li><code>staging</code> parses quantity and price to integers, flags cancellations, returns, missing customers, and exact duplicates, and assigns one disposition.</li>
    <li><code>mart</code> is the daily calendar (gaps filled with zero), the customer cohort, the country ranking, and the checks.</li>
  </ol>
  <p>SQLite is the whole warehouse. The extract is one file of about half a million rows. A hosted warehouse would not change the SQL and would add an account.</p>
  <pre>SELECT
  (SELECT SUM(line_amount_pence) FROM staging.stg_invoice_line
    WHERE disposition IN ('kept_merchandise', 'kept_duplicate_extra'))
  -
  (SELECT SUM(net_merchandise_pence) FROM mart.daily_revenue)
  AS difference_pence;</pre>
  <p>Offline fixture and tests: <code>python -m finance.run</code> from the repository root. Rebuild this page from the workbook: <code>python -m finance.run --uci path/to/Online\\ Retail.xlsx</code>. The workbook is not in git. Download { _esc(snapshot['download_url']) } and check the sha256 below before trusting a new total.</p>

  <h2>Provenance</h2>
  <ul>
    <li>{_esc(snapshot['citation'])}</li>
    <li>License: <a href="{_esc(snapshot['license_url'])}">{_esc(snapshot['license'])}</a>. This page republishes aggregates, not the raw invoice lines.</li>
    <li>Workbook sha256 <code>{_esc(snapshot['xlsx_sha256'])}</code> ({snapshot['xlsx_bytes']:,} bytes), retrieved { _esc(snapshot['retrieved_on']) }.</li>
    <li>Same merchandise rule as <code>projects/01-daily-sales-forecast</code>: stock code starts with a digit, price &gt; 0, partial final day dropped. The daily mart matches that committed series to the penny. The forecast's test error is a description of that series, not a claim that the model changed revenue.</li>
  </ul>

  <h2>Limits</h2>
  <ul>
    <li>No payment date, tax, or currency rate. There is nothing here to age as accounts receivable, and nothing to convert from another currency.</li>
    <li>Exact duplicates may be real repeated lines or a double-loaded extract. Both treatments are reported. Neither is labeled as cash collected.</li>
    <li>Customer id is the public research identifier. Published outputs are aggregates. The local SQLite files that still contain those ids are gitignored.</li>
    <li>The 19-row fixture under <code>finance/fixtures</code> plants a return, a currency symbol, and a comma decimal so the parser is tested. Those planted rows are not in the totals on this page.</li>
  </ul>
</main>
</body>
</html>
"""


def write_demo(snapshot: dict, path: Path = DEMO_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_demo(snapshot))
    return path


def _esc(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
