-- Blok 1 · minggu_07 · NCG Core Dataset v2.0.0
SELECT warehouse_id,
       SUM(quantity_ordered_carton)   AS ordered_carton,
       SUM(quantity_fulfilled_carton) AS fulfilled_carton,
       ROUND(1.0 * SUM(quantity_fulfilled_carton) / SUM(quantity_ordered_carton), 3) AS fill_rate
FROM sales_transactions
WHERE transaction_date BETWEEN '2025-01-01' AND '2025-12-31'
GROUP BY warehouse_id
ORDER BY fill_rate;

-- Blok 2 · minggu_07 · NCG Core Dataset v2.0.0
SELECT s.warehouse_id, p.category,
       ROUND(1.0 * SUM(s.quantity_fulfilled_carton) / SUM(s.quantity_ordered_carton), 3) AS fill_rate
FROM sales_transactions AS s
JOIN product_master AS p ON s.sku_id = p.sku_id
WHERE s.transaction_date BETWEEN '2025-01-01' AND '2025-12-31'
GROUP BY s.warehouse_id, p.category
HAVING 1.0 * SUM(s.quantity_fulfilled_carton) / SUM(s.quantity_ordered_carton) < 0.93
ORDER BY fill_rate;

-- Blok 3 · minggu_07 · NCG Core Dataset v2.0.0
WITH last_snapshot AS (
    SELECT warehouse_id, sku_id, on_hand_system_carton, reorder_point_carton
    FROM inventory_snapshots
    WHERE snapshot_date = '2025-12-29'
),
recent_demand AS (
    SELECT warehouse_id, sku_id,
           SUM(quantity_ordered_carton) / 28.0 AS avg_daily_demand
    FROM sales_transactions
    WHERE transaction_date BETWEEN '2025-12-01' AND '2025-12-28'
    GROUP BY warehouse_id, sku_id
)
SELECT l.warehouse_id, l.sku_id, l.on_hand_system_carton,
       ROUND(d.avg_daily_demand, 1) AS avg_daily_demand,
       ROUND(l.on_hand_system_carton / d.avg_daily_demand, 0) AS days_of_cover,
       CASE
           WHEN l.on_hand_system_carton / d.avg_daily_demand > 60 THEN 'Overstock'
           WHEN l.on_hand_system_carton < l.reorder_point_carton THEN 'Di bawah ROP'
           ELSE 'Normal'
       END AS stock_status
FROM last_snapshot AS l
JOIN recent_demand AS d
  ON l.warehouse_id = d.warehouse_id AND l.sku_id = d.sku_id
ORDER BY days_of_cover DESC, l.warehouse_id, l.sku_id
LIMIT 8;

-- Blok 4 · minggu_07 · NCG Core Dataset v2.0.0
WITH monthly AS (
    SELECT DATE_TRUNC('month', s.transaction_date)::date AS sales_month,
           p.category, s.sku_id,
           SUM(s.net_sales_idr) AS net_sales_idr
    FROM sales_transactions AS s
    JOIN product_master AS p ON s.sku_id = p.sku_id
    WHERE s.transaction_date BETWEEN '2025-01-01' AND '2025-12-31'
    GROUP BY 1, 2, 3
)
SELECT sales_month, category, sku_id, net_sales_idr,
       RANK() OVER (PARTITION BY sales_month, category ORDER BY net_sales_idr DESC) AS rank_in_category,
       LAG(net_sales_idr) OVER (PARTITION BY sku_id ORDER BY sales_month) AS prev_month_sales
FROM monthly
WHERE category = 'Snack' AND sales_month IN ('2025-02-01', '2025-03-01')
ORDER BY sales_month, rank_in_category;
