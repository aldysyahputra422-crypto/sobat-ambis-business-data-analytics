# Blok 1 · minggu_13 · NCG Core Dataset v2.0.0
import pandas as pd

pd.set_option("display.width", 110)
pd.set_option("display.max_columns", 12)

DATA_DIR = "data/"   # Colab: "/content/drive/MyDrive/bda/data/"

sales_raw = pd.read_csv(DATA_DIR + "mentah_sales_transactions.csv")
products = pd.read_csv(DATA_DIR + "bersih_product_master.csv")

print("Ukuran sales_raw:", sales_raw.shape)
print("Ukuran products:", products.shape)
print(sales_raw.head(3))

# Blok 2 · minggu_13 · NCG Core Dataset v2.0.0
# Variabel dan tipe data
warehouse_id = "WH-SBY"          # str
truck_slots_per_day = 2          # int
truck_capacity_carton = 360      # int
target_fill_rate = 0.95          # float

# List: urutan nilai
weekly_orders = [3920, 4105, 3870, 6310]

# Dictionary: pasangan kunci-nilai
truck_slots = {"WH-SBY": 2, "WH-CKR": 3, "WH-SMG": 2, "WH-MKS": 2}

daily_capacity = truck_slots[warehouse_id] * truck_capacity_carton
print("Kapasitas kirim harian", warehouse_id, "=", daily_capacity, "karton")

for week_number, orders in enumerate(weekly_orders, start=1):
    weekly_capacity = daily_capacity * 6   # tidak ada pengiriman hari Minggu
    status = "melebihi kapasitas" if orders > weekly_capacity else "aman"
    print(f"Minggu {week_number}: {orders} karton -> {status}")


def fill_rate(fulfilled, ordered):
    """Porsi karton dipesan yang terpenuhi. Mengembalikan None jika tidak ada pesanan."""
    if ordered == 0:
        return None
    return fulfilled / ordered


print("Fill rate contoh:", round(fill_rate(195836, 216697), 3))

# Blok 3 · minggu_13 · NCG Core Dataset v2.0.0
print(sales_raw.dtypes)
print()
print("Nilai kosong per kolom:")
print(sales_raw.isna().sum()[sales_raw.isna().sum() > 0])
print()
print("Variasi penulisan channel:")
print(sales_raw["channel"].value_counts())
print()
print(sales_raw[["quantity_ordered_carton", "quantity_fulfilled_carton"]].describe().round(1))
