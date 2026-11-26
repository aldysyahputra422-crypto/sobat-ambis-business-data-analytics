-- Blok 1 · minggu_05 · NCG Core Dataset v2.0.0
CREATE TABLE sales_transactions (
    transaction_id            VARCHAR(12) PRIMARY KEY,
    transaction_date          DATE        NOT NULL,
    warehouse_id              VARCHAR(10) NOT NULL REFERENCES warehouse_master (warehouse_id),
    sku_id                    VARCHAR(10) NOT NULL REFERENCES product_master (sku_id),
    channel                   VARCHAR(30) NOT NULL,
    destination_city          VARCHAR(40) NOT NULL,
    quantity_ordered_carton   INTEGER     NOT NULL,
    quantity_fulfilled_carton INTEGER     NOT NULL,
    unit_price_idr            INTEGER,
    discount_pct              NUMERIC(4,2) NOT NULL,
    promo_flag                INTEGER     NOT NULL,
    net_sales_idr             BIGINT
);

-- Blok 2 · minggu_05 · NCG Core Dataset v2.0.0
SELECT 'product_master' AS table_name, COUNT(*) AS row_count FROM product_master
UNION ALL SELECT 'warehouse_master', COUNT(*) FROM warehouse_master
UNION ALL SELECT 'sales_transactions', COUNT(*) FROM sales_transactions
UNION ALL SELECT 'inventory_snapshots', COUNT(*) FROM inventory_snapshots
UNION ALL SELECT 'inventory_batches', COUNT(*) FROM inventory_batches
UNION ALL SELECT 'purchase_orders', COUNT(*) FROM purchase_orders
UNION ALL SELECT 'truck_schedule', COUNT(*) FROM truck_schedule
UNION ALL SELECT 'delivery_records', COUNT(*) FROM delivery_records
UNION ALL SELECT 'promotion_calendar', COUNT(*) FROM promotion_calendar;

-- Blok 3 · minggu_05 · NCG Core Dataset v2.0.0
SELECT COUNT(*) AS orphan_rows
FROM sales_transactions AS s
LEFT JOIN product_master AS p ON s.sku_id = p.sku_id
WHERE p.sku_id IS NULL;
