# Revenue quality on the UCI Online Retail extract

This is the finance case study in the portfolio. The question is narrow on purpose.

**Before forecasting the next day of sales, can the revenue number itself be tied from invoice lines to a daily mart, to the penny, after the messy rows are classified?**

The source is the public UCI Online Retail workbook (a UK gift wholesaler, 1 Dec 2010 through 9 Dec 2011, CC BY 4.0). It is not a client file. Nothing here was adopted by that retailer, and nothing here is an ROI.

## Answer on this extract

Merchandise net sales are **£9,762,760.55** from 1 Dec 2010 through 8 Dec 2011 (373 calendar days, 69 of them £0.00). That is the same series the daily forecast trains on. The tie is exact:

| Piece | Amount |
| --- | ---: |
| Gross merchandise (positive quantity, not a cancellation) | £10,072,920.35 |
| Cancellation invoices (number starts with C) | −£310,159.80 |
| Other returns inside the merchandise rule | £0.00 |
| **Net** | **£9,762,760.55** |

Exact duplicate extras sit inside that net: **£21,371.10** on 5,250 extra lines. Dropping them would leave £9,741,389.45. The published forecast series keeps them. Both totals are in the mart. The duplicate total is a sensitivity, not a second set of books.

Other facts from the same run, all in `outputs/uci_snapshot.json`:

- 541,909 source rows.
- 1,632 rows on 9 Dec 2011 are dropped. The file ends at 12:50, before the 16:00 full-day cutoff.
- 2,983 rows are non-product (postage, fees, manual codes, gift vouchers, letter-prefixed goods).
- 3 invoice numbers starting with A, including a bad-debt adjustment, sum to −£11,062.06 and are not merchandise. Stock code `B` does not start with a digit.
- 4 prices of `0.001` (PADS and bank charges) are rejected for having three decimal places. They are not rounded.
- 130,547 kept lines have no customer id. They contribute £1,491,723.13 of revenue and are excluded from the cohort.
- 4,361 customer ids have kept merchandise. 1,122 of them also have kept merchandise in the next calendar month (25.7%). That is not a subscription retention rate.
- 1,336 negative quantities are not cancellation invoices. 1,324 have a non-positive price and 12 are non-product, so none of them enter the merchandise net. The 19-row fixture plants one true merchandise return so that branch of the SQL is still tested. Those planted rows are not in the figures above.
- United Kingdom is 84.77% of net merchandise. Country is ship-to. Prices are already GBP.

The static explorer repeats these figures from the snapshot: [`docs/revenue-quality/index.html`](../docs/revenue-quality/index.html). Open that file in a browser. It does not call a server.

## Tradeoffs

- **SQLite, three files (`raw`, `staging`, `mart`), not a warehouse.** Half a million rows fit in one process. The SQL is the part worth reading. A hosted warehouse would add an account and would not change the joins.
- **Integer pence, not floats.** SQLite has no decimal type. `to_pence` rejects `£`, commas, and more than two decimal places. Quantity must be a whole number. Line amount is `quantity * unit_price_pence`.
- **Full refresh, not an incremental load.** Each run deletes the fact tables and appends one row to `raw.load_run`. A second run of the same file does not double revenue. That is the idempotency this extract needs. It is not a streaming ingest.
- **Duplicates are flagged and kept in the official net.** The extract does not say whether an exact repeat is two items or a double load. Removing them silently would make the mart disagree with the forecast series. The bridge query shows the effect instead.
- **The forecast stays, as a consumer.** Project 01 predicts the next day of this daily mart. Its test MAE (£11,629.44 on 1 Oct 2011–8 Dec 2011) describes that holdout. It is not evidence that a model improved the business. Projects 02–07 are synthetic and are labeled that way. They are not this case study.

## Architecture

```
Online Retail.xlsx  or  fixtures/online_retail_messy.csv
        │  text in, sha256 recorded
        ▼
raw.invoice_line          raw.load_run
        │  SQL: parse, flags, one disposition
        ▼
staging.stg_invoice_line
        │  SQL: calendar, cohort, country window, checks
        ▼
mart.daily_revenue / customer_cohort / country_revenue / quality_check
        │
        ├── outputs/*.csv and uci_snapshot.json   (aggregates only)
        └── docs/revenue-quality/index.html
```

Disposition priority, top wins: unparseable date, partial final day, unparseable quantity or price, zero quantity, non-product stock code, non-positive price, exact-duplicate extra, otherwise kept merchandise.

## Data dictionary

Amounts in the marts are integer pence. Dates are `YYYY-MM-DD`. Empty customer id is `''`, not null.

| Object | Column | Meaning |
| --- | --- | --- |
| `raw.invoice_line` | eight source texts | Invoice, stock, description, quantity, timestamp, unit price, customer id, country. Unmodified aside from trim. |
| `raw.load_run` | `sha256`, `row_count` | One row per refresh. Facts are replaced; this log is appended. |
| `staging.stg_invoice_line` | `quantity`, `unit_price_pence`, `line_amount_pence` | Parsed integers. Null when the text is rejected. |
| | `is_cancellation` | Invoice number starts with C. |
| | `is_return` | Parsed quantity is negative and the invoice is not a cancellation. |
| | `missing_customer` | Customer id is blank. |
| | `dup_n`, `dup_count` | Window over the eight source fields. `dup_n = 1` is the keeper. |
| | `disposition` | The single outcome used by the marts. See the priority list. |
| `mart.daily_revenue` | `gross_sales_pence`, `returns_pence`, `cancellations_pence`, `net_merchandise_pence` | Disjoint buckets. They sum to net. Missing dates inside the range are rows of zero. |
| | `duplicate_extra_pence` | Part of net that sits on `kept_duplicate_extra`. |
| `mart.customer_cohort` | `cohort_month`, `month_index`, `customers`, `net_merchandise_pence` | First kept month for a customer id, then later months. Blank ids are absent. |
| `mart.country_revenue` | `share_bps`, `revenue_rank` | Basis points truncated toward zero (10,000 = 100%). Ranked by net pence. |
| `mart.quality_check` | `status`, `observed` | `pass` or `fail` for invariants. `observed` when the extract contains the messy case. |

## Queries worth opening

The files under `sql/examples/` are what the tests execute.

- `01_reconciliation.sql` — line pence minus daily pence. Must be 0.
- `02_returns_and_cancellations.sql` — sales, cancellation invoices, other returns.
- `03_customer_cohort.sql` — cohort month and months since first purchase.
- `04_country_window.sql` — rank, share, and a running total by country.
- `05_duplicate_bridge.sql` — net with duplicates, the extra amount, net without them.
- `06_rolling_seven_day.sql` — seven calendar days, zeros included.
- `sql/10_stage.sql` — the disposition rules.
- `sql/30_quality.sql` — the checks, including the one that fails if a daily total is edited.

## Reproduce

From the repository root:

```bash
python -m finance.run
```

That runs `finance/tests` on the fixture and rewrites the explorer from the committed snapshot. No network.

To rebuild the snapshot from the workbook (pandas and openpyxl):

```bash
python -m finance.run --uci "/path/to/Online Retail.xlsx"
```

Hash and download rules are in [PROVENANCE.md](PROVENANCE.md).

## Limits

- No cash application, tax, duty, or credit note matched back to an original invoice beyond the C prefix on the invoice number.
- No accounts-receivable aging. There is no payment date. Inventing one would be a fake control.
- Customer id is a research key. Published outputs stop at aggregates.
- One year, one wholesaler, structural zero Saturdays. The forecast error on the last 69 days is about that season, not a general retail result.
- The Double Eagle dashboard elsewhere in this repo is a planning illustration with assumed customers. It is not this ledger and it is not live books.

## Interview guide

A 15-minute walkthrough that stays inside what the code does:

1. Open `sql/10_stage.sql` and explain the disposition order. Why the partial day is dropped before the product filter: the whole day is incomplete, including its fees.
2. Run the reconciliation example and say what `difference_pence` means. Then point at the test that adds one penny to 1 Dec 2010 and expects the check to fail.
3. Show the duplicate bridge. Say why both numbers are kept, and what evidence would be required to drop the extras (a line id from the source system, which this file does not have).
4. Show the cohort query and the blank-customer exclusion. Revenue includes those invoices. The repeat count does not. Quote 1,122 of 4,361, and say it is one month on one extract.
5. If asked about production: full refresh is enough for a file that arrives as a snapshot. A daily ledger from an ERP would need a real invoice-line key, late-arriving credits, and a currency table. This repo does not pretend to have them.

Do not claim the model beat a buyer, saved money, or was used in production. The defendable sentence is: the daily series the forecast uses reconciles to the classified invoice lines, and the messy rows are counted rather than dropped in silence.
