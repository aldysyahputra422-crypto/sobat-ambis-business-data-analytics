# Blok 1 · minggu_15 · NCG Core Dataset v2.0.0
"""inventory_report.py: laporan fill rate mingguan yang dapat diulang.

Jalankan: python inventory_report.py
Input : data/mentah_sales_transactions.csv, data/bersih_product_master.csv
Output: output/fill_rate_weekly.csv
"""
from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
CHANNEL_MAP = {"MODERN TRADE": "Modern Trade", "MT": "Modern Trade",
               "TRADITIONAL TRADE": "Traditional Trade", "TT": "Traditional Trade",
               "TRAD. TRADE": "Traditional Trade", "DISTRIBUTOR": "Distributor",
               "E-COMMERCE": "E-commerce", "ECOMMERCE": "E-commerce"}


def load_data():
    sales = pd.read_csv(DATA_DIR / "mentah_sales_transactions.csv")
    products = pd.read_csv(DATA_DIR / "bersih_product_master.csv")
    return sales, products


def clean_sales(sales, products):
    sales = sales.drop_duplicates().copy()
    sales = sales.sort_values("unit_price_idr", na_position="last")
    sales = sales.drop_duplicates(subset="transaction_id", keep="first")
    sales["transaction_date"] = pd.to_datetime(sales["transaction_date"], format="%Y-%m-%d", errors="coerce")
    sales["sku_id"] = sales["sku_id"].str.upper()
    sales = sales.dropna(subset=["transaction_date"])
    sales = sales[sales["sku_id"].isin(products["sku_id"])]
    sales = sales[(sales["quantity_fulfilled_carton"] >= 0)
                  & (sales["quantity_fulfilled_carton"] <= sales["quantity_ordered_carton"])]
    median_qty = sales.groupby(["warehouse_id", "sku_id"])["quantity_ordered_carton"].transform("median")
    sales = sales[sales["quantity_ordered_carton"] <= 20 * median_qty.clip(lower=1)].copy()
    sales["channel"] = sales["channel"].str.strip().str.upper().map(CHANNEL_MAP)
    return sales


def validate(sales):
    """Hentikan program jika data tidak memenuhi aturan dasar."""
    assert sales["transaction_id"].is_unique, "transaction_id ganda"
    assert sales["channel"].notna().all(), "channel tidak dikenal"
    assert (sales["quantity_fulfilled_carton"] >= 0).all(), "kuantitas negatif"
    assert sales["transaction_date"].between("2024-01-01", "2025-12-31").all(), "tanggal di luar periode"


def weekly_fill_rate(sales):
    sales = sales.assign(week_start=sales["transaction_date"].dt.to_period("W-SUN").dt.start_time)
    weekly = (sales.groupby(["warehouse_id", "week_start"], as_index=False)
              [["quantity_ordered_carton", "quantity_fulfilled_carton"]].sum())
    weekly["fill_rate"] = (weekly["quantity_fulfilled_carton"] / weekly["quantity_ordered_carton"]).round(4)
    return weekly


def main():
    sales, products = load_data()
    sales = clean_sales(sales, products)
    validate(sales)
    weekly = weekly_fill_rate(sales)
    OUTPUT_DIR.mkdir(exist_ok=True)
    weekly.to_csv(OUTPUT_DIR / "fill_rate_weekly.csv", index=False)
    print(f"{len(sales)} transaksi bersih -> {len(weekly)} baris mingguan disimpan")
    print(weekly[weekly["warehouse_id"] == "WH-SBY"].nsmallest(3, "fill_rate").to_string(index=False))


if __name__ == "__main__":
    main()
