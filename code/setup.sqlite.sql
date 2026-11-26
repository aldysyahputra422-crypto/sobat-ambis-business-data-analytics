-- Blok 1 · setup · NCG Core Dataset v2.0.0
PRAGMA foreign_keys = ON;

-- Blok 2 · setup · NCG Core Dataset v2.0.0
PRAGMA foreign_keys;
INSERT INTO sales_transactions VALUES ('TRX-TEST', '2025-01-01', 'WH-SBY', 'SKU-999', 'MT', 'X', 1, 1, 1, 0, 0, 1);

-- Blok 3 · setup · NCG Core Dataset v2.0.0
SELECT COUNT(*) FROM sales_transactions WHERE unit_price_idr = '';

-- Blok 4 · setup · NCG Core Dataset v2.0.0
UPDATE inventory_snapshots SET on_hand_physical_carton = NULL WHERE on_hand_physical_carton = '';
UPDATE purchase_orders SET actual_arrival_date = NULL WHERE actual_arrival_date = '';
UPDATE purchase_orders SET quantity_received_carton = NULL WHERE quantity_received_carton = '';
UPDATE inventory_batches SET po_id = NULL WHERE po_id = '';
UPDATE truck_schedule SET actual_arrival_time = NULL WHERE actual_arrival_time = '';
UPDATE truck_schedule SET dock_start_time = NULL WHERE dock_start_time = '';
UPDATE truck_schedule SET dock_end_time = NULL WHERE dock_end_time = '';
