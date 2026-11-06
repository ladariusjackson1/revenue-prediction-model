-- First purchase month, then later months, for customers who have an id.
-- month_index 0 is the cohort month. Blank customer ids are not in this table.
SELECT
  cohort_month,
  activity_month,
  month_index,
  customers,
  net_merchandise_pence
FROM mart.customer_cohort
ORDER BY cohort_month, month_index;
