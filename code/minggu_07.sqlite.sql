-- Blok 1 · minggu_07 · NCG Core Dataset v2.0.0
WITH monthly AS (
    SELECT strftime('%Y-%m-01', s.transaction_date) AS sales_month,
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
