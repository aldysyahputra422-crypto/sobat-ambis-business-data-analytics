# Blok 0 · minggu_14 · NCG Core Dataset v2.0.0
# PERSIAPAN: kode dari minggu sebelumnya (w13_load). Jalankan sekali sebelum blok berikutnya.
import pandas as pd

pd.set_option("display.width", 110)
pd.set_option("display.max_columns", 12)

DATA_DIR = "data/"   # Colab: "/content/drive/MyDrive/bda/data/"

sales_raw = pd.read_csv(DATA_DIR + "mentah_sales_transactions.csv")
products = pd.read_csv(DATA_DIR + "bersih_product_master.csv")

print("Ukuran sales_raw:", sales_raw.shape)
print("Ukuran products:", products.shape)
print(sales_raw.head(3))

# Blok 1 · minggu_14 · NCG Core Dataset v2.0.0
sales = sales_raw.copy()
log = []   # catatan setiap langkah pembersihan

# 1. Duplikat persis
before = len(sales)
sales = sales.drop_duplicates()
log.append(("duplikat persis", before - len(sales)))

# 2. Near-duplicate: transaction_id sama, isi berbeda. Simpan baris yang harganya terisi.
before = len(sales)
sales = sales.sort_values("unit_price_idr", na_position="last")
sales = sales.drop_duplicates(subset="transaction_id", keep="first")
log.append(("near-duplicate transaction_id", before - len(sales)))

# 3. Tanggal tidak valid -> NaT, lalu dibuang
sales["transaction_date"] = pd.to_datetime(sales["transaction_date"], format="%Y-%m-%d", errors="coerce")
before = len(sales)
sales = sales.dropna(subset=["transaction_date"])
log.append(("tanggal tidak valid", before - len(sales)))

# 4. SKU: samakan huruf, buang yang tidak terdaftar
sales["sku_id"] = sales["sku_id"].str.upper()
before = len(sales)
sales = sales[sales["sku_id"].isin(products["sku_id"])].copy()
log.append(("SKU tidak terdaftar", before - len(sales)))

# 5. Kuantitas tidak valid
before = len(sales)
valid_qty = (sales["quantity_fulfilled_carton"] >= 0) & (
    sales["quantity_fulfilled_carton"] <= sales["quantity_ordered_carton"])
sales = sales[valid_qty].copy()
log.append(("kuantitas tidak valid", before - len(sales)))

# 6. Outlier salah ketik: > 20 x median gudang-SKU
median_qty = sales.groupby(["warehouse_id", "sku_id"])["quantity_ordered_carton"].transform("median")
is_typo = sales["quantity_ordered_carton"] > 20 * median_qty.clip(lower=1)
log.append(("outlier salah ketik", int(is_typo.sum())))
sales = sales[~is_typo].copy()

# 7. Channel baku
channel_map = {"MODERN TRADE": "Modern Trade", "MT": "Modern Trade",
               "TRADITIONAL TRADE": "Traditional Trade", "TT": "Traditional Trade",
               "TRAD. TRADE": "Traditional Trade", "DISTRIBUTOR": "Distributor",
               "E-COMMERCE": "E-commerce", "ECOMMERCE": "E-commerce"}
sales["channel"] = sales["channel"].str.strip().str.upper().map(channel_map)
assert sales["channel"].notna().all(), "Ada channel yang belum dipetakan"

# 8. Harga kosong diisi harga daftar, ditandai
list_price = products.set_index("sku_id")["list_price_idr"]
sales["price_imputed"] = sales["unit_price_idr"].isna()
sales["unit_price_idr"] = sales["unit_price_idr"].fillna(sales["sku_id"].map(list_price))
sales["net_sales_idr"] = (sales["quantity_fulfilled_carton"] * sales["unit_price_idr"]
                          * (1 - sales["discount_pct"]))

print(pd.DataFrame(log, columns=["langkah", "baris_dibuang"]))
print("Baris bersih:", len(sales), "| harga diimputasi:", int(sales["price_imputed"].sum()))

# Blok 2 · minggu_14 · NCG Core Dataset v2.0.0
sales = sales.merge(products[["sku_id", "category", "shelf_life_days"]], on="sku_id", how="left",
                    validate="many_to_one")
sales["month"] = sales["transaction_date"].dt.to_period("M").astype(str)

by_category = (sales[sales["transaction_date"].dt.year == 2025]
               .groupby(["warehouse_id", "category"], as_index=False)
               [["quantity_ordered_carton", "quantity_fulfilled_carton"]].sum())
by_category["fill_rate"] = (by_category["quantity_fulfilled_carton"]
                            / by_category["quantity_ordered_carton"]).round(3)
print(by_category.sort_values("fill_rate").head(5).to_string(index=False))
print()

monthly = sales[sales["warehouse_id"] == "WH-SBY"].pivot_table(
    index="month", values=["quantity_ordered_carton", "quantity_fulfilled_carton"], aggfunc="sum")
monthly["fill_rate"] = (monthly["quantity_fulfilled_carton"] / monthly["quantity_ordered_carton"]).round(3)
print(monthly.loc["2025-01":"2025-06"])

# Blok 3 · minggu_14 · NCG Core Dataset v2.0.0
import matplotlib.pyplot as plt

# Satu pertanyaan, satu grafik: bulan mana fill rate WH-SBY jatuh di bawah target?
fig, ax = plt.subplots(figsize=(6.4, 3.0))
ax.plot(monthly.index, monthly["fill_rate"] * 100, marker="o", color="#1F6FB2", linewidth=2)
ax.axhline(95, color="#D6336C", linestyle="--", linewidth=1)          # target fill rate volume (KPI-01)
ax.text(len(monthly) - 1, 95.6, "target 95%", color="#D6336C", ha="right")
ax.set_ylim(70, 100)                                                    # sumbu dipotong: tulis di keterangan grafik
ax.set_ylabel("Fill rate volume (%)")
ax.set_title("WH-SBY: fill rate volume per bulan, 2024–2025", loc="left")
ax.tick_params(axis="x", rotation=90)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig("fig_w14_fill_rate.png", dpi=200)                           # simpan untuk laporan
plt.close(fig)

lowest = monthly["fill_rate"].idxmin()
print("Bulan terendah:", lowest, "| fill rate", monthly.loc[lowest, "fill_rate"])
print("Bulan di bawah target 95%:", int((monthly["fill_rate"] < 0.95).sum()), "dari", len(monthly))
