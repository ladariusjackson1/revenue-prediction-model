-- Ship-to country mix. Prices in this extract are GBP even when the country
-- is not the United Kingdom; there is no FX rate to apply.
SELECT
  country,
  net_merchandise_pence,
  line_count,
  share_bps,
  revenue_rank,
  SUM(net_merchandise_pence) OVER (
    ORDER BY revenue_rank
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS cumulative_pence
FROM mart.country_revenue
ORDER BY revenue_rank, country;
