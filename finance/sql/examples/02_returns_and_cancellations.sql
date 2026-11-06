-- Merchandise reductions, split into cancellation invoices and other
-- negative quantities. Amounts are negative pence.
SELECT
  CASE
    WHEN is_cancellation = 1 THEN 'cancellation_invoice'
    WHEN is_return = 1 THEN 'return_not_cancellation'
    ELSE 'sale'
  END AS movement,
  COUNT(*) AS lines,
  SUM(line_amount_pence) AS amount_pence
FROM staging.stg_invoice_line
WHERE disposition IN ('kept_merchandise', 'kept_duplicate_extra')
GROUP BY movement
ORDER BY movement;
