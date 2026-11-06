-- What the published daily series includes, and what it would be if exact
-- duplicate extras were removed. This is a sensitivity, not a second fact.
SELECT
  SUM(net_merchandise_pence) AS net_including_duplicate_extras_pence,
  SUM(duplicate_extra_pence) AS duplicate_extra_pence,
  SUM(net_merchandise_pence) - SUM(duplicate_extra_pence) AS net_if_extras_removed_pence
FROM mart.daily_revenue;
