-- Blok 1 · minggu_08 · NCG Core Dataset v2.0.0
CREATE TABLE raw_sales_transactions (
    transaction_id TEXT, transaction_date TEXT, warehouse_id TEXT, sku_id TEXT,
    channel TEXT, destination_city TEXT, quantity_ordered_carton TEXT,
    quantity_fulfilled_carton TEXT, unit_price_idr TEXT, discount_pct TEXT,
    promo_flag TEXT, net_sales_idr TEXT
);

-- Blok 2 · minggu_08 · NCG Core Dataset v2.0.0
SELECT transaction_id, COUNT(*)
FROM v_sales_clean
GROUP BY transaction_id
HAVING COUNT(*) > 1;

-- Blok 3 · minggu_08 · NCG Core Dataset v2.0.0
SELECT
    (SELECT COUNT(*) FROM raw_sales_transactions) AS total_rows,
    (SELECT COUNT(*) - COUNT(DISTINCT transaction_id) FROM raw_sales_transactions) AS duplicate_rows,
    (SELECT COUNT(*) FROM raw_sales_transactions WHERE unit_price_idr IS NULL OR unit_price_idr = '') AS null_price_rows,
    (SELECT COUNT(*) FROM raw_sales_transactions AS r
       WHERE NOT EXISTS (SELECT 1 FROM product_master AS p WHERE p.sku_id = r.sku_id)) AS orphan_sku_rows,
    (SELECT COUNT(*) FROM raw_sales_transactions
       WHERE CAST(quantity_fulfilled_carton AS INTEGER) < 0) AS negative_qty_rows;

-- Blok 4 · minggu_08 · NCG Core Dataset v2.0.0
SELECT transaction_id, COUNT(*) AS copies
FROM raw_sales_transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1
ORDER BY transaction_id
LIMIT 5;

-- Blok 5 · minggu_08 · NCG Core Dataset v2.0.0
SELECT channel AS channel_raw, COUNT(*) AS jumlah
FROM raw_sales_transactions
GROUP BY channel
ORDER BY jumlah DESC, 1;

-- Blok 6 · minggu_08 · NCG Core Dataset v2.0.0
SELECT
    CASE
        WHEN UPPER(TRIM(channel)) IN ('MODERN TRADE', 'MT') THEN 'Modern Trade'
        WHEN UPPER(TRIM(channel)) IN ('TRADITIONAL TRADE', 'TT', 'TRAD. TRADE') THEN 'Traditional Trade'
        WHEN UPPER(TRIM(channel)) = 'DISTRIBUTOR' THEN 'Distributor'
        WHEN UPPER(REPLACE(TRIM(channel), '-', '')) = 'ECOMMERCE' THEN 'E-commerce'
        ELSE 'TIDAK DIKENAL'
    END AS channel_clean,
    COUNT(*) AS jumlah
FROM raw_sales_transactions
GROUP BY 1
ORDER BY jumlah DESC, 1;

-- Blok 7 · minggu_08 · NCG Core Dataset v2.0.0
CREATE VIEW v_sales_clean AS
SELECT DISTINCT
       transaction_id,
       CAST(transaction_date AS DATE) AS transaction_date,
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
WHERE pg_input_is_valid(transaction_date, 'date')   -- PostgreSQL 16 ke atas
  AND transaction_date LIKE '____-__-__'
  AND CAST(quantity_fulfilled_carton AS INTEGER) >= 0
  AND UPPER(sku_id) IN (SELECT sku_id FROM product_master);

-- Blok 8 · minggu_08 · NCG Core Dataset v2.0.0
SELECT COUNT(*) AS clean_rows,
       SUM(CASE WHEN unit_price_idr IS NULL THEN 1 ELSE 0 END) AS null_price,
       COUNT(DISTINCT channel) AS channels
FROM v_sales_clean;

-- Blok 9 · minggu_08 · NCG Core Dataset v2.0.0
SELECT warehouse_id,
       COUNT(*) AS counted_lines,
       SUM(CASE WHEN on_hand_system_carton = on_hand_physical_carton THEN 1 ELSE 0 END) AS exact_match,
       ROUND(1.0 * SUM(CASE WHEN on_hand_system_carton = on_hand_physical_carton THEN 1 ELSE 0 END) / COUNT(*), 3) AS inventory_record_accuracy,
       SUM(on_hand_system_carton - on_hand_physical_carton) AS net_difference_carton
FROM inventory_snapshots
WHERE on_hand_physical_carton IS NOT NULL
  AND snapshot_date BETWEEN '2025-01-01' AND '2025-12-31'
GROUP BY warehouse_id
ORDER BY inventory_record_accuracy;

-- Blok 10 · minggu_08 · NCG Core Dataset v2.0.0
SELECT b.warehouse_id, p.category,
       SUM(b.quantity_remaining_carton) AS carton_at_risk,
       SUM(b.quantity_remaining_carton * p.unit_cost_idr) AS value_at_cost_idr
FROM inventory_batches AS b
JOIN product_master AS p ON b.sku_id = p.sku_id
WHERE b.quantity_remaining_carton > 0
  AND b.expiry_date > DATE '2025-12-31'           -- belum kedaluwarsa pada tanggal acuan
  AND b.expiry_date <= DATE '2025-12-31' + 90     -- kedaluwarsa dalam 90 hari ke depan
GROUP BY b.warehouse_id, p.category
ORDER BY value_at_cost_idr DESC;

-- Blok 11 · minggu_08 · NCG Core Dataset v2.0.0
SELECT b.warehouse_id,
       SUM(b.quantity_expired_carton) AS expired_carton,
       SUM(b.quantity_expired_carton * p.unit_cost_idr) AS writeoff_value_idr
FROM inventory_batches AS b
JOIN product_master AS p ON b.sku_id = p.sku_id
GROUP BY b.warehouse_id
ORDER BY writeoff_value_idr DESC;

-- Blok 12 · minggu_08 · NCG Core Dataset v2.0.0
SELECT warehouse_id,
       DATE_TRUNC('month', order_ready_date)::date AS ready_month,
       COUNT(*) AS deliveries,
       ROUND(AVG(1.0 * on_time_flag), 3) AS on_time_rate
FROM delivery_records
WHERE warehouse_id = 'WH-SBY'
  AND order_ready_date BETWEEN '2025-01-01' AND '2025-06-30'
GROUP BY 1, 2
ORDER BY 2;

-- Blok 13 · minggu_08 · NCG Core Dataset v2.0.0
SELECT warehouse_id,
       COUNT(*) AS completed_slots,
       ROUND(AVG(1.0 * loaded_carton / truck_capacity_carton), 3) AS avg_utilization,
       ROUND(AVG(EXTRACT(EPOCH FROM (dock_start_time - actual_arrival_time)) / 60.0), 0) AS avg_wait_minutes
FROM truck_schedule
WHERE status = 'Completed'
GROUP BY warehouse_id
ORDER BY avg_wait_minutes DESC;
