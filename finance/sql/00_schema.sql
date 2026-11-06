-- Three attached databases: raw, staging, mart.
-- raw keeps the extract as text. staging types every row and assigns one
-- disposition. mart holds the daily ledger, cohorts, country mix, and checks.

CREATE TABLE IF NOT EXISTS raw.load_run (
  run_id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_name TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  row_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.invoice_line (
  source_row_number INTEGER PRIMARY KEY,
  invoice_no TEXT NOT NULL,
  stock_code TEXT NOT NULL,
  description TEXT NOT NULL,
  quantity_text TEXT NOT NULL,
  invoice_ts TEXT NOT NULL,
  unit_price_text TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  country TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.stg_invoice_line (
  source_row_number INTEGER PRIMARY KEY,
  invoice_no TEXT NOT NULL,
  stock_code TEXT NOT NULL,
  description TEXT NOT NULL,
  invoice_ts TEXT NOT NULL,
  country TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  quantity INTEGER,
  unit_price_pence INTEGER,
  line_amount_pence INTEGER,
  is_cancellation INTEGER NOT NULL,
  is_return INTEGER NOT NULL,
  missing_customer INTEGER NOT NULL,
  dup_n INTEGER NOT NULL,
  dup_count INTEGER NOT NULL,
  disposition TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mart.daily_revenue (
  revenue_date TEXT PRIMARY KEY,
  gross_sales_pence INTEGER NOT NULL,
  returns_pence INTEGER NOT NULL,
  cancellations_pence INTEGER NOT NULL,
  net_merchandise_pence INTEGER NOT NULL,
  duplicate_extra_pence INTEGER NOT NULL,
  line_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS mart.customer_cohort (
  cohort_month TEXT NOT NULL,
  activity_month TEXT NOT NULL,
  month_index INTEGER NOT NULL,
  customers INTEGER NOT NULL,
  net_merchandise_pence INTEGER NOT NULL,
  PRIMARY KEY (cohort_month, activity_month)
);

CREATE TABLE IF NOT EXISTS mart.country_revenue (
  country TEXT PRIMARY KEY,
  net_merchandise_pence INTEGER NOT NULL,
  line_count INTEGER NOT NULL,
  share_bps INTEGER NOT NULL,
  revenue_rank INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS mart.quality_check (
  check_name TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  observed INTEGER NOT NULL,
  detail TEXT NOT NULL
);
