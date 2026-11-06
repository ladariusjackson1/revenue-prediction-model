-- Full refresh of one extract. The load log is append-only so a rerun is
-- visible, but invoice lines and marts are replaced rather than doubled.
DELETE FROM mart.quality_check;
DELETE FROM mart.country_revenue;
DELETE FROM mart.customer_cohort;
DELETE FROM mart.daily_revenue;
DELETE FROM staging.stg_invoice_line;
DELETE FROM raw.invoice_line;
