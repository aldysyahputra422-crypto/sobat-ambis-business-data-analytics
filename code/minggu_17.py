# Blok 1 · minggu_17 · NCG Core Dataset v2.0.0
import numpy as np
import pandas as pd

sales = pd.read_csv("data/bersih_sales_transactions.csv", parse_dates=["transaction_date"])
products = pd.read_csv("data/bersih_product_master.csv")
promos = pd.read_csv("data/bersih_promotion_calendar.csv",
                     parse_dates=["planned_start_date", "planned_end_date", "announced_at"])

# Target: total karton DIPESAN per gudang, SKU, minggu (Senin-Minggu)
sales["week_start"] = sales["transaction_date"].dt.to_period("W-SUN").dt.start_time
weekly = (sales.groupby(["warehouse_id", "sku_id", "week_start"], as_index=False)
          .agg(demand=("quantity_ordered_carton", "sum")))

# Minggu tanpa pesanan harus tercatat sebagai 0, bukan hilang
all_weeks = pd.date_range("2024-01-01", "2025-12-22", freq="W-MON")
full = pd.MultiIndex.from_product([weekly["warehouse_id"].unique(), weekly["sku_id"].unique(), all_weeks],
                                  names=["warehouse_id", "sku_id", "week_start"])
weekly = (weekly.set_index(["warehouse_id", "sku_id", "week_start"])
          .reindex(full, fill_value=0).reset_index())

# Fokus contoh: WH-SBY
sby = weekly[weekly["warehouse_id"] == "WH-SBY"].sort_values(["sku_id", "week_start"]).copy()
print("Baris WH-SBY:", len(sby), "=", sby["sku_id"].nunique(), "SKU x", sby["week_start"].nunique(), "minggu")
print(sby[sby["sku_id"] == "SKU-001"].tail(3).to_string(index=False))

# Blok 2 · minggu_17 · NCG Core Dataset v2.0.0
# Garis waktu: prediksi untuk minggu target T dibuat pada forecast origin = Senin 06.00 minggu T-1.
# Data terakhir yang lengkap adalah minggu T-2 (berakhir Minggu malam). Karena itu semua lag mulai dari 2.
sby["forecast_origin"] = sby["week_start"] - pd.Timedelta(days=7) + pd.Timedelta(hours=6)
by_sku = sby.groupby("sku_id")["demand"]
sby["lag_2"] = by_sku.shift(2)
sby["lag_3"] = by_sku.shift(3)
sby["lag_52"] = by_sku.shift(52)
sby["rolling_mean_4"] = by_sku.transform(lambda s: s.shift(2).rolling(4).mean())  # minggu T-5 s.d. T-2

# Aturan ketersediaan: pada forecast origin O, baris latih boleh dipakai hanya jika minggu targetnya
# SUDAH SELESAI sebelum O (week_start + 7 hari <= tanggal O). Minggu T-1 yang sedang berjalan tidak boleh ikut.
def trainable_at(frame, origin):
    """Baris yang targetnya sudah selesai diamati pada forecast origin."""
    return frame[frame["week_start"] + pd.Timedelta(days=7) <= pd.Timestamp(origin).normalize()]


# Jadwal model: dilatih pada origin Senin 30 Juni 2025, dievaluasi untuk minggu target 7 Juli - 22 September.
# Untuk test, dilatih ulang pada origin Senin 29 September 2025, dievaluasi untuk minggu target 6 Oktober - 22 Desember.
FIT_ORIGIN_VALID = pd.Timestamp("2025-06-30 06:00")
FIT_ORIGIN_TEST = pd.Timestamp("2025-09-29 06:00")
train = trainable_at(sby, FIT_ORIGIN_VALID)
valid = sby[(sby["forecast_origin"] >= FIT_ORIGIN_VALID) & (sby["week_start"] <= "2025-09-22")]
test = sby[sby["forecast_origin"] >= FIT_ORIGIN_TEST]
assert train["week_start"].max() + pd.Timedelta(days=7) <= valid["forecast_origin"].min()
print("Train:", train["week_start"].min().date(), "s.d.", train["week_start"].max().date(), len(train), "baris")
print("Valid:", valid["week_start"].min().date(), "s.d.", valid["week_start"].max().date(), len(valid), "baris")
print("Test :", test["week_start"].min().date(), "s.d.", test["week_start"].max().date(), len(test), "baris")

def evaluate(actual, predicted):
    """MAE, RMSE, WAPE, dan bias dalam satu baris."""
    error = predicted - actual
    return {"MAE": round(float(np.mean(np.abs(error))), 1),
            "RMSE": round(float(np.sqrt(np.mean(error ** 2))), 1),
            "WAPE": round(float(np.sum(np.abs(error)) / np.sum(actual)), 3),
            "Bias": round(float(np.sum(error) / np.sum(actual)), 3)}


baseline_results = {
    "Naive (lag_2)": evaluate(valid["demand"], valid["lag_2"]),
    "Moving average 4": evaluate(valid["demand"], valid["rolling_mean_4"]),
    "Seasonal naive (lag_52)": evaluate(valid["demand"], valid["lag_52"]),
}
print(pd.DataFrame(baseline_results).T)
