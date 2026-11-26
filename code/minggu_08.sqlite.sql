-- Blok 1 · minggu_08 · NCG Core Dataset v2.0.0
CREATE VIEW v_sales_clean AS
SELECT DISTINCT
       transaction_id,
       transaction_date,
       warehouse_id,
       UPPER(sku_id) AS sku_id,
       CASE
           WHEN UPPER(TRIM(channel)) IN ('MODERN TRADE', 'MT') THEN 'Modern Trade'
           WHEN UPPER(TRIM(channel)) IN ('TRADITIONAL TRADE', 'TT', 'TRAD. TRADE') THEN 'Traditional Trade'
           WHEN UPPER(TRIM(channel)) = 'DISTRIBUTOR' THEN 'Distributor'
           WHEN UPPER(REPLACE(TRIM(channel), '-', '')) = 'ECOMMERCE' THEN 'E-commerce'
       END AS channel,
       CAST(quantity_ordered_carton AS INTEGER) AS quantity_ordered_carton,
       CAST(quantity_fulfilled_carton AS INTEGER) AS quantity_fulfilled_carton,
       CAST(NULLIF(unit_price_idr, '') AS NUMERIC) AS unit_price_idr,
       CAST(discount_pct AS NUMERIC) AS discount_pct
FROM raw_sales_transactions
WHERE date(transaction_date) = transaction_date   -- tanggal tidak valid menghasilkan NULL atau tanggal lain
  AND CAST(quantity_fulfilled_carton AS INTEGER) >= 0
  AND UPPER(sku_id) IN (SELECT sku_id FROM product_master);
