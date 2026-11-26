# Blok 0 · minggu_18 · NCG Core Dataset v2.0.0
# PERSIAPAN: kode dari minggu sebelumnya (w17_weekly, w17_baselines). Jalankan sekali sebelum blok berikutnya.
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

# Blok 1 · minggu_18 · NCG Core Dataset v2.0.0
from sklearn.linear_model import LinearRegression

# Tanggal Idul Fitri dan kapan tanggal itu resmi diketahui (penandatanganan SKB 3 Menteri libur nasional).
# Sidang isbat dapat menggeser tanggal +-1 hari; pada data mingguan pergeseran ini jarang memindahkan minggu.
LEBARAN = pd.DataFrame({
    "date": pd.to_datetime(["2024-04-10", "2025-03-31", "2026-03-21"]),
    "known_from": pd.to_datetime(["2023-09-12", "2024-10-14", "2025-09-19"]),
})
MAX_WEEKS = 12  # di luar 12 minggu, jarak ke Lebaran dianggap "jauh"


def weeks_to_lebaran(row):
    """Minggu dari minggu target ke Lebaran berikutnya, hanya memakai tanggal yang sudah diumumkan pada origin."""
    known = LEBARAN[LEBARAN["known_from"] <= row["forecast_origin"]]
    gaps = [(d - row["week_start"]).days / 7 for d in known["date"] if d >= row["week_start"]]
    if not gaps:  # Lebaran berikutnya belum diumumkan: harus masih jauh, kalau tidak fitur ini tidak sah
        later = LEBARAN.loc[LEBARAN["date"] >= row["week_start"], "date"].min()
        assert (later - row["week_start"]).days / 7 > MAX_WEEKS, f"Lebaran {later.date()} belum diumumkan"
        return MAX_WEEKS
    return min(min(gaps), MAX_WEEKS)


def planned_promo_days(row):
    """Jumlah hari promosi di minggu target yang SUDAH diumumkan pada forecast origin."""
    known = promos[(promos["warehouse_id"] == "WH-SBY") & (promos["sku_id"] == row["sku_id"])
                   & (promos["announced_at"] <= row["forecast_origin"])]
    week_days = pd.date_range(row["week_start"], periods=7)
    covered = set()
    for start, end in zip(known["planned_start_date"], known["planned_end_date"]):
        covered.update(d for d in week_days if start <= d <= end)
    return len(covered)


sby["weeks_to_lebaran"] = sby.apply(weeks_to_lebaran, axis=1)
sby["pre_lebaran"] = (sby["weeks_to_lebaran"] <= 4).astype(int)
sby["planned_promo_days"] = sby.apply(planned_promo_days, axis=1)
sby = sby.merge(products[["sku_id", "category"]], on="sku_id", how="left", validate="many_to_one")

FEATURES = ["lag_2", "lag_3", "rolling_mean_4", "weeks_to_lebaran", "pre_lebaran", "planned_promo_days"]
model_data = sby.dropna(subset=["lag_2", "lag_3", "rolling_mean_4"])
train = trainable_at(model_data, FIT_ORIGIN_VALID)
valid = model_data[model_data["week_start"].isin(valid["week_start"])]
test = model_data[model_data["week_start"].isin(test["week_start"])]

linear = LinearRegression()
linear.fit(train[FEATURES], train["demand"])
for name, coef in zip(FEATURES, linear.coef_):
    print(f"{name:20s} {coef:8.3f}")
print(f"{'intercept':20s} {linear.intercept_:8.3f}")
print("Validasi model    :", evaluate(valid["demand"], linear.predict(valid[FEATURES])))
print("Validasi baseline :", evaluate(valid["demand"], valid["rolling_mean_4"]))
