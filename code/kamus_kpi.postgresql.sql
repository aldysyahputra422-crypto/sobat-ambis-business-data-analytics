-- Blok 1 · kamus_kpi · NCG Core Dataset v2.0.0
WITH s AS (
    SELECT warehouse_id,
           SUM(quantity_ordered_carton) AS ordered_carton,
           SUM(quantity_fulfilled_carton) AS fulfilled_carton,
           COUNT(*) AS order_lines,
           SUM(CASE WHEN quantity_fulfilled_carton = quantity_ordered_carton THEN 1 ELSE 0 END) AS full_lines
    FROM sales_transactions
    WHERE transaction_date BETWEEN '2025-01-01' AND '2025-12-31'
    GROUP BY warehouse_id
)
SELECT warehouse_id,
       ROUND(1.0 * fulfilled_carton / ordered_carton, 3) AS kpi01_fill_rate_volume,
       ROUND(1.0 * full_lines / order_lines, 3) AS kpi02_order_line_fill_rate
FROM s
ORDER BY warehouse_id;
