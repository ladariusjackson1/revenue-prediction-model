-- One disposition per source row. Priority is top to bottom:
--   unparseable date, partial final day, unparseable quantity or price,
--   zero quantity, non-product stock code, non-positive price,
--   exact-duplicate extra, otherwise kept merchandise.
-- Exact duplicate means all eight source fields match. The earliest source
-- row is the keeper. Extras stay in the forecast-matching total and are
-- flagged kept_duplicate_extra so the revenue impact is visible.
-- A final calendar day is partial when the extract's last timestamp is
-- before 16:00. That whole day is left out, which is the same cutoff the
-- daily forecast series uses.

INSERT INTO staging.stg_invoice_line (
  source_row_number,
  invoice_no,
  stock_code,
  description,
  invoice_ts,
  country,
  customer_id,
  quantity,
  unit_price_pence,
  line_amount_pence,
  is_cancellation,
  is_return,
  missing_customer,
  dup_n,
  dup_count,
  disposition
)
WITH partial AS (
  SELECT CASE
    WHEN max_ts IS NULL THEN NULL
    WHEN CAST(strftime('%H', max_ts) AS INTEGER) < 16 THEN date(max_ts)
    ELSE NULL
  END AS partial_day
  FROM (
    SELECT MAX(invoice_ts) AS max_ts
    FROM raw.invoice_line
    WHERE invoice_ts <> ''
      AND date(invoice_ts) IS NOT NULL
  )
),
base AS (
  SELECT
    r.source_row_number,
    r.invoice_no,
    r.stock_code,
    r.description,
    r.invoice_ts,
    r.country,
    r.customer_id,
    r.quantity_text,
    r.unit_price_text,
    to_int(r.quantity_text) AS quantity,
    to_pence(r.unit_price_text) AS unit_price_pence,
    CASE
      WHEN UPPER(SUBSTR(r.invoice_no, 1, 1)) = 'C' THEN 1
      ELSE 0
    END AS is_cancellation,
    ROW_NUMBER() OVER (
      PARTITION BY
        r.invoice_no,
        r.stock_code,
        r.description,
        r.quantity_text,
        r.invoice_ts,
        r.unit_price_text,
        r.customer_id,
        r.country
      ORDER BY r.source_row_number
    ) AS dup_n,
    COUNT(*) OVER (
      PARTITION BY
        r.invoice_no,
        r.stock_code,
        r.description,
        r.quantity_text,
        r.invoice_ts,
        r.unit_price_text,
        r.customer_id,
        r.country
    ) AS dup_count
  FROM raw.invoice_line AS r
)
SELECT
  source_row_number,
  invoice_no,
  stock_code,
  description,
  invoice_ts,
  country,
  customer_id,
  quantity,
  unit_price_pence,
  CASE
    WHEN quantity IS NOT NULL AND unit_price_pence IS NOT NULL
    THEN quantity * unit_price_pence
  END AS line_amount_pence,
  is_cancellation,
  CASE
    WHEN quantity IS NOT NULL AND quantity < 0 AND is_cancellation = 0 THEN 1
    ELSE 0
  END AS is_return,
  CASE WHEN customer_id = '' THEN 1 ELSE 0 END AS missing_customer,
  dup_n,
  dup_count,
  CASE
    WHEN invoice_ts = '' OR date(invoice_ts) IS NULL THEN 'excluded_unparseable'
    WHEN date(invoice_ts) = (SELECT partial_day FROM partial) THEN 'excluded_partial_day'
    WHEN quantity IS NULL OR unit_price_pence IS NULL THEN 'excluded_unparseable'
    WHEN quantity = 0 THEN 'excluded_bad_quantity'
    WHEN stock_code NOT GLOB '[0-9]*' THEN 'excluded_non_product'
    WHEN unit_price_pence <= 0 THEN 'excluded_bad_price'
    WHEN dup_n > 1 THEN 'kept_duplicate_extra'
    ELSE 'kept_merchandise'
  END AS disposition
FROM base;
