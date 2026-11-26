-- Blok 1 · minggu_11 · NCG Core Dataset v2.0.0
SELECT s.transaction_date, s.warehouse_id, w.city, s.sku_id, p.product_name, p.category, s.channel,
       s.quantity_ordered_carton, s.quantity_fulfilled_carton, s.net_sales_idr
FROM sales_transactions AS s
JOIN product_master AS p ON s.sku_id = p.sku_id
JOIN warehouse_master AS w ON s.warehouse_id = w.warehouse_id
WHERE s.transaction_date BETWEEN '2025-01-01' AND '2025-12-31'
ORDER BY s.transaction_date, s.warehouse_id, s.sku_id, s.channel
LIMIT 3;
