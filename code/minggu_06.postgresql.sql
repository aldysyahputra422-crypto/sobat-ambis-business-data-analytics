-- Blok 1 · minggu_06 · NCG Core Dataset v2.0.0
SELECT kolom_1, kolom_2          -- kolom apa yang ditampilkan
FROM nama_tabel                  -- dari tabel mana
WHERE syarat                     -- baris mana yang diambil
ORDER BY kolom_1 DESC            -- urutan hasil
LIMIT 10;                        -- berapa baris

-- Blok 2 · minggu_06 · NCG Core Dataset v2.0.0
SELECT transaction_id, transaction_date, sku_id, channel,
       quantity_fulfilled_carton, net_sales_idr
FROM sales_transactions
WHERE warehouse_id = 'WH-SBY'
  AND transaction_date BETWEEN '2025-03-01' AND '2025-03-31'
ORDER BY net_sales_idr DESC
LIMIT 5;

-- Blok 3 · minggu_06 · NCG Core Dataset v2.0.0
SELECT
    CASE
        WHEN quantity_fulfilled_carton = quantity_ordered_carton THEN 'Terpenuhi penuh'
        WHEN quantity_fulfilled_carton = 0 THEN 'Tidak terpenuhi'
        ELSE 'Terpenuhi sebagian'
    END AS fulfillment_status,
    COUNT(*) AS jumlah_baris
FROM sales_transactions
WHERE warehouse_id = 'WH-SBY'
  AND transaction_date BETWEEN '2025-03-01' AND '2025-03-31'
GROUP BY 1
ORDER BY 2 DESC;

-- Blok 4 · minggu_06 · NCG Core Dataset v2.0.0
SELECT sku_id, product_name, category, shelf_life_days
FROM product_master
WHERE shelf_life_days < 300
ORDER BY shelf_life_days, sku_id;
