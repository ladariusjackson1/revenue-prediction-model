-- Invariants use pass/fail. Messy-source findings use observed when the count
-- is non-zero: they are properties of the extract, not silent drops.
DELETE FROM mart.quality_check;

INSERT INTO mart.quality_check (check_name, status, observed, detail)
SELECT
  'recon_lines_equal_daily',
  CASE WHEN line_pence = daily_pence THEN 'pass' ELSE 'fail' END,
  line_pence - daily_pence,
  'Sum of kept line pence minus sum of daily net pence. Zero means the mart ties to the ledger.'
FROM (
  SELECT
    COALESCE((
      SELECT SUM(line_amount_pence)
      FROM staging.stg_invoice_line
      WHERE disposition IN ('kept_merchandise', 'kept_duplicate_extra')
    ), 0) AS line_pence,
    COALESCE((
      SELECT SUM(net_merchandise_pence) FROM mart.daily_revenue
    ), 0) AS daily_pence
);

INSERT INTO mart.quality_check (check_name, status, observed, detail)
SELECT
  'recon_components_equal_net',
  CASE WHEN gap = 0 THEN 'pass' ELSE 'fail' END,
  gap,
  'gross_sales_pence + returns_pence + cancellations_pence - net_merchandise_pence across the calendar.'
FROM (
  SELECT COALESCE(SUM(
    gross_sales_pence + returns_pence + cancellations_pence - net_merchandise_pence
  ), 0) AS gap
  FROM mart.daily_revenue
);

INSERT INTO mart.quality_check (check_name, status, observed, detail)
SELECT
  'calendar_has_no_gaps',
  CASE WHEN gap_count = 0 THEN 'pass' ELSE 'fail' END,
  gap_count,
  'Count of consecutive daily-mart dates more than one day apart.'
FROM (
  SELECT COUNT(*) AS gap_count
  FROM (
    SELECT
      revenue_date,
      LAG(revenue_date) OVER (ORDER BY revenue_date) AS previous_date
    FROM mart.daily_revenue
  )
  WHERE previous_date IS NOT NULL
    AND julianday(revenue_date) - julianday(previous_date) <> 1
);

INSERT INTO mart.quality_check (check_name, status, observed, detail)
SELECT
  'kept_amounts_not_null',
  CASE WHEN null_count = 0 THEN 'pass' ELSE 'fail' END,
  null_count,
  'Kept merchandise rows with a null line amount.'
FROM (
  SELECT COUNT(*) AS null_count
  FROM staging.stg_invoice_line
  WHERE disposition IN ('kept_merchandise', 'kept_duplicate_extra')
    AND line_amount_pence IS NULL
);

INSERT INTO mart.quality_check (check_name, status, observed, detail)
SELECT
  'finding_duplicate_extras',
  CASE WHEN extra_count = 0 THEN 'pass' ELSE 'observed' END,
  extra_count,
  'Exact duplicate extras still included in the forecast-matching net, in pence of those extras.'
FROM (
  SELECT
    COUNT(*) AS extra_count,
    COALESCE(SUM(line_amount_pence), 0) AS extra_pence
  FROM staging.stg_invoice_line
  WHERE disposition = 'kept_duplicate_extra'
);

-- The insert above stored the row count in observed. Replace observed with
-- the pence impact, which is the number a reviewer should quote.
UPDATE mart.quality_check
SET observed = (
  SELECT COALESCE(SUM(line_amount_pence), 0)
  FROM staging.stg_invoice_line
  WHERE disposition = 'kept_duplicate_extra'
)
WHERE check_name = 'finding_duplicate_extras';

INSERT INTO mart.quality_check (check_name, status, observed, detail)
SELECT
  'finding_missing_customer',
  CASE WHEN missing_rows = 0 THEN 'pass' ELSE 'observed' END,
  missing_rows,
  'Kept merchandise rows with a blank customer id. They stay in revenue and out of cohorts.'
FROM (
  SELECT COUNT(*) AS missing_rows
  FROM staging.stg_invoice_line
  WHERE disposition IN ('kept_merchandise', 'kept_duplicate_extra')
    AND missing_customer = 1
);

INSERT INTO mart.quality_check (check_name, status, observed, detail)
SELECT
  'finding_unparseable',
  CASE WHEN bad_rows = 0 THEN 'pass' ELSE 'observed' END,
  bad_rows,
  'Rows dropped because the date, quantity, or price could not be parsed. Symbols, comma decimals, and more than two price decimals land here.'
FROM (
  SELECT COUNT(*) AS bad_rows
  FROM staging.stg_invoice_line
  WHERE disposition = 'excluded_unparseable'
);

INSERT INTO mart.quality_check (check_name, status, observed, detail)
SELECT
  'finding_partial_day',
  CASE WHEN partial_rows = 0 THEN 'pass' ELSE 'observed' END,
  partial_rows,
  'Rows on a final calendar day whose last timestamp is before 16:00.'
FROM (
  SELECT COUNT(*) AS partial_rows
  FROM staging.stg_invoice_line
  WHERE disposition = 'excluded_partial_day'
);

INSERT INTO mart.quality_check (check_name, status, observed, detail)
SELECT
  'finding_non_product',
  CASE WHEN fee_rows = 0 THEN 'pass' ELSE 'observed' END,
  fee_rows,
  'Rows whose stock code does not start with a digit (postage, fees, manual adjustments, gift vouchers, letter-prefixed goods).'
FROM (
  SELECT COUNT(*) AS fee_rows
  FROM staging.stg_invoice_line
  WHERE disposition = 'excluded_non_product'
);

INSERT INTO mart.quality_check (check_name, status, observed, detail)
SELECT
  'finding_bad_price',
  CASE WHEN bad_rows = 0 THEN 'pass' ELSE 'observed' END,
  bad_rows,
  'Product rows with a parsed price of zero or less.'
FROM (
  SELECT COUNT(*) AS bad_rows
  FROM staging.stg_invoice_line
  WHERE disposition = 'excluded_bad_price'
);
