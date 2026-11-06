-- Seven calendar days of net merchandise, including explicit zero days.
SELECT
  revenue_date,
  net_merchandise_pence,
  rolling_7_pence
FROM mart.daily_with_roll
ORDER BY revenue_date;
