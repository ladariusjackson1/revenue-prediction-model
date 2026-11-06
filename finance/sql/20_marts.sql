-- Daily merchandise ledger. Missing calendar days inside the kept range are
-- explicit zeros (this retailer has structural Saturday gaps).
-- gross + returns + cancellations = net, with those three buckets disjoint:
-- cancellation invoices (any sign), other negative quantities, everything else.

INSERT INTO mart.daily_revenue (
  revenue_date,
  gross_sales_pence,
  returns_pence,
  cancellations_pence,
  net_merchandise_pence,
  duplicate_extra_pence,
  line_count
)
WITH RECURSIVE bounds AS (
  SELECT
    MIN(date(invoice_ts)) AS start_date,
    MAX(date(invoice_ts)) AS end_date
  FROM staging.stg_invoice_line
  WHERE disposition IN ('kept_merchandise', 'kept_duplicate_extra')
),
days AS (
  SELECT start_date AS revenue_date, end_date
  FROM bounds
  WHERE start_date IS NOT NULL
  UNION ALL
  SELECT date(revenue_date, '+1 day'), end_date
  FROM days
  WHERE revenue_date < end_date
)
SELECT
  days.revenue_date,
  COALESCE(SUM(
    CASE
      WHEN lines.is_cancellation = 0 AND lines.quantity > 0 THEN lines.line_amount_pence
      ELSE 0
    END
  ), 0) AS gross_sales_pence,
  COALESCE(SUM(
    CASE WHEN lines.is_return = 1 THEN lines.line_amount_pence ELSE 0 END
  ), 0) AS returns_pence,
  COALESCE(SUM(
    CASE WHEN lines.is_cancellation = 1 THEN lines.line_amount_pence ELSE 0 END
  ), 0) AS cancellations_pence,
  COALESCE(SUM(lines.line_amount_pence), 0) AS net_merchandise_pence,
  COALESCE(SUM(
    CASE
      WHEN lines.disposition = 'kept_duplicate_extra' THEN lines.line_amount_pence
      ELSE 0
    END
  ), 0) AS duplicate_extra_pence,
  COUNT(lines.source_row_number) AS line_count
FROM days
LEFT JOIN staging.stg_invoice_line AS lines
  ON date(lines.invoice_ts) = days.revenue_date
 AND lines.disposition IN ('kept_merchandise', 'kept_duplicate_extra')
GROUP BY days.revenue_date;

DROP VIEW IF EXISTS mart.daily_with_roll;
CREATE VIEW mart.daily_with_roll AS
SELECT
  revenue_date,
  gross_sales_pence,
  returns_pence,
  cancellations_pence,
  net_merchandise_pence,
  duplicate_extra_pence,
  line_count,
  SUM(net_merchandise_pence) OVER (
    ORDER BY revenue_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS rolling_7_pence
FROM mart.daily_revenue;

-- Identified customers only. Invoices with a blank customer id stay in the
-- daily revenue mart and out of this cohort.
INSERT INTO mart.customer_cohort (
  cohort_month,
  activity_month,
  month_index,
  customers,
  net_merchandise_pence
)
WITH kept AS (
  SELECT
    customer_id,
    date(invoice_ts, 'start of month') AS activity_month,
    line_amount_pence
  FROM staging.stg_invoice_line
  WHERE disposition IN ('kept_merchandise', 'kept_duplicate_extra')
    AND customer_id <> ''
),
firsts AS (
  SELECT customer_id, MIN(activity_month) AS cohort_month
  FROM kept
  GROUP BY customer_id
)
SELECT
  firsts.cohort_month,
  kept.activity_month,
  (
    CAST(strftime('%Y', kept.activity_month) AS INTEGER)
    - CAST(strftime('%Y', firsts.cohort_month) AS INTEGER)
  ) * 12
  + (
    CAST(strftime('%m', kept.activity_month) AS INTEGER)
    - CAST(strftime('%m', firsts.cohort_month) AS INTEGER)
  ) AS month_index,
  COUNT(DISTINCT kept.customer_id) AS customers,
  SUM(kept.line_amount_pence) AS net_merchandise_pence
FROM kept
JOIN firsts ON firsts.customer_id = kept.customer_id
GROUP BY firsts.cohort_month, kept.activity_month;

-- share_bps is integer basis points (10_000 = 100%), truncated toward zero.
INSERT INTO mart.country_revenue (
  country,
  net_merchandise_pence,
  line_count,
  share_bps,
  revenue_rank
)
SELECT
  country,
  SUM(line_amount_pence) AS net_merchandise_pence,
  COUNT(*) AS line_count,
  CAST(
    SUM(line_amount_pence) * 10000
    / NULLIF(SUM(SUM(line_amount_pence)) OVER (), 0)
    AS INTEGER
  ) AS share_bps,
  RANK() OVER (ORDER BY SUM(line_amount_pence) DESC) AS revenue_rank
FROM staging.stg_invoice_line
WHERE disposition IN ('kept_merchandise', 'kept_duplicate_extra')
GROUP BY country;
