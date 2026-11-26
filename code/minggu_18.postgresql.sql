-- Blok 1 · minggu_18 · NCG Core Dataset v2.0.0
SELECT campaign_id, sku_id, planned_start_date, announced_at, promotion_type
FROM promotion_calendar
WHERE warehouse_id = 'WH-SBY'
  AND planned_start_date BETWEEN '2025-10-13' AND '2025-10-19'
  AND announced_at <= '2025-10-06 06:00:00'
ORDER BY planned_start_date, sku_id;
