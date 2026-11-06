-- Tie the line ledger to the daily mart. difference_pence must be 0.
SELECT
  (
    SELECT COALESCE(SUM(line_amount_pence), 0)
    FROM staging.stg_invoice_line
    WHERE disposition IN ('kept_merchandise', 'kept_duplicate_extra')
  ) AS line_pence,
  (
    SELECT COALESCE(SUM(net_merchandise_pence), 0)
    FROM mart.daily_revenue
  ) AS daily_pence,
  (
    SELECT COALESCE(SUM(line_amount_pence), 0)
    FROM staging.stg_invoice_line
    WHERE disposition IN ('kept_merchandise', 'kept_duplicate_extra')
  ) - (
    SELECT COALESCE(SUM(net_merchandise_pence), 0)
    FROM mart.daily_revenue
  ) AS difference_pence;
