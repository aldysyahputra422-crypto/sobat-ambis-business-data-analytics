# Blok 0 · minggu_20 · NCG Core Dataset v2.0.0
# PERSIAPAN: kode dari minggu sebelumnya (w17_weekly, w17_baselines, w18_linear, w19_compare). Jalankan sekali sebelum blok berikutnya.
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

from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge

# Fitur kandidat baru: gejolak permintaan 4 minggu terakhir yang sudah lengkap (T-5 s.d. T-2).
# Dihitung dari deret lengkap per SKU, dengan shift(2) seperti fitur lain, jadi tersedia pada forecast origin.
sby["rolling_std_4"] = sby.groupby("sku_id")["demand"].transform(lambda s: s.shift(2).rolling(4).std())
model_data = model_data.assign(rolling_std_4=sby["rolling_std_4"])  # indeks sama dengan sby
assert model_data["rolling_std_4"].notna().all()
train = model_data[model_data.index.isin(train.index)]
valid = model_data[model_data.index.isin(valid.index)]
test = model_data[model_data.index.isin(test.index)]

# Data pemilihan model: hanya minggu target sampai 22 September 2025. Test (mulai 6 Oktober) TIDAK disentuh.
selection_data = model_data[model_data["week_start"] <= "2025-09-22"]
assert selection_data["week_start"].max() < test["week_start"].min()

# Backtest sederhana: 3 forecast origin, setiap model dilatih ulang pada origin dan diuji 4 minggu target
FIRST_TARGETS = pd.to_datetime(["2025-07-07", "2025-08-04", "2025-09-01"])


def backtest_wape(make_model, features):
    """WAPE per jendela. make_model=None berarti baseline moving average 4 (tanpa pelatihan)."""
    scores = []
    for first in FIRST_TARGETS:
        origin = first - pd.Timedelta(days=7) + pd.Timedelta(hours=6)
        fit_data = trainable_at(selection_data, origin)
        window = selection_data[(selection_data["week_start"] >= first)
                                & (selection_data["week_start"] < first + pd.Timedelta(weeks=4))]
        assert fit_data["week_start"].max() + pd.Timedelta(days=7) <= window["forecast_origin"].min()
        if make_model is None:
            predicted = window["rolling_mean_4"]
        else:
            predicted = make_model().fit(fit_data[features], fit_data["demand"]).predict(window[features])
        scores.append(evaluate(window["demand"], predicted)["WAPE"])
    return scores


candidates = {
    "Moving average 4 (baseline)": (None, FEATURES),
    "Regresi linear": (LinearRegression, FEATURES),
    "Ridge alpha=1": (lambda: Ridge(alpha=1.0), FEATURES),
    "Ridge alpha=10": (lambda: Ridge(alpha=10.0), FEATURES),
    "Ridge alpha=100": (lambda: Ridge(alpha=100.0), FEATURES),
    "Gradient boosting": (lambda: HistGradientBoostingRegressor(max_depth=4, learning_rate=0.05,
                                                                 max_iter=300, random_state=42), FEATURES),
    "Regresi linear + rolling_std_4": (LinearRegression, FEATURES + ["rolling_std_4"]),
}
rows = []
for name, (make_model, features) in candidates.items():
    scores = backtest_wape(make_model, features)
    rows.append({"model": name, "WAPE_jul": scores[0], "WAPE_agu": scores[1], "WAPE_sep": scores[2],
                 "WAPE_rata2": round(float(np.mean(scores)), 3), "WAPE_terburuk": max(scores)})
comparison = pd.DataFrame(rows)
print(comparison.to_string(index=False))

# Selisih train vs validasi untuk gradient boosting (tanda overfitting), satu kali latih pada origin 30 Juni
gb = candidates["Gradient boosting"][0]().fit(train[FEATURES], train["demand"])
gb_train = evaluate(train["demand"], gb.predict(train[FEATURES]))["WAPE"]
gb_valid = evaluate(valid["demand"], gb.predict(valid[FEATURES]))["WAPE"]
print(f"\nGradient boosting: WAPE train {gb_train}, validasi {gb_valid}")

# Kandidat untuk dikonfirmasi di Minggu 20: regresi linear dengan dan tanpa rolling_std_4.
# Aturan keputusan ditulis SEBELUM backtest Minggu 20: fitur baru dipakai jika WAPE rata-rata lebih rendah
# DAN menang di sedikitnya 4 dari 6 periode.
CANDIDATE_FEATURES = FEATURES + ["rolling_std_4"]

# Blok 1 · minggu_20 · NCG Core Dataset v2.0.0
from sklearn.model_selection import train_test_split

# A. KESALAHAN: memakai promo yang BENAR-BENAR terjadi (dari transaksi) + rata-rata tanpa shift + split acak
observed = (sales[sales["warehouse_id"] == "WH-SBY"]
            .groupby(["sku_id", "transaction_date", "week_start"], as_index=False)["promo_flag"].max()
            .groupby(["sku_id", "week_start"], as_index=False)["promo_flag"].sum()
            .rename(columns={"promo_flag": "observed_promo_days"}))
leaky = model_data.merge(observed, on=["sku_id", "week_start"], how="left").fillna({"observed_promo_days": 0})
leaky["rolling_mean_4_leaky"] = leaky.groupby("sku_id")["demand"].transform(lambda s: s.rolling(4).mean())
leaky_features = ["lag_2", "lag_3", "rolling_mean_4_leaky", "weeks_to_lebaran", "pre_lebaran", "observed_promo_days"]
leaky = leaky.dropna(subset=leaky_features)
tr, te = train_test_split(leaky, test_size=0.25, random_state=0)
bad_model = LinearRegression().fit(tr[leaky_features], tr["demand"])
print("Model bocor, split acak :", evaluate(te["demand"], bad_model.predict(te[leaky_features])))

# Satu sumber bocor saja: promo teramati vs promo yang sudah diumumkan, dengan split waktu yang benar
only_promo = ["lag_2", "lag_3", "rolling_mean_4", "weeks_to_lebaran", "pre_lebaran", "observed_promo_days"]
lk_train = trainable_at(leaky, FIT_ORIGIN_VALID)
lk_valid = leaky[leaky["week_start"].isin(valid["week_start"])]
promo_leak_model = LinearRegression().fit(lk_train[only_promo], lk_train["demand"])
print("Promo teramati (bocor)  :", evaluate(lk_valid["demand"], promo_leak_model.predict(lk_valid[only_promo])))
print("Promo terencana (sah)   :", evaluate(valid["demand"], linear.predict(valid[FEATURES])))

# B. BENAR: rolling-origin backtest, 6 periode. Setiap 2 minggu model dilatih ulang pada forecast origin
# (Senin 06.00) hanya dengan minggu target yang sudah selesai, lalu dipakai untuk 2 minggu target berikutnya.
# Dua kandidat dari Minggu 19 dibandingkan dengan baseline. Test tetap tidak disentuh.
backtest = []
for first_target in pd.date_range("2025-07-07", periods=6, freq="14D"):
    origin = first_target - pd.Timedelta(days=7) + pd.Timedelta(hours=6)
    fit_data = trainable_at(selection_data, origin)
    eval_data = selection_data[(selection_data["week_start"] >= first_target)
                               & (selection_data["week_start"] < first_target + pd.Timedelta(days=14))]
    assert fit_data["week_start"].max() + pd.Timedelta(days=7) <= eval_data["forecast_origin"].min()
    row = {"origin": origin.strftime("%Y-%m-%d %H:%M"),
           "WAPE_baseline": evaluate(eval_data["demand"], eval_data["rolling_mean_4"])["WAPE"]}
    for label, features in [("WAPE_linear", FEATURES), ("WAPE_linear_std", CANDIDATE_FEATURES)]:
        fitted = LinearRegression().fit(fit_data[features], fit_data["demand"])
        row[label] = evaluate(eval_data["demand"], fitted.predict(eval_data[features]))["WAPE"]
    backtest.append(row)
backtest = pd.DataFrame(backtest)
print(backtest.to_string(index=False))

# Kestabilan: rata-rata, simpangan baku, periode terburuk, dan jumlah menang
stability = pd.DataFrame({col: {"rata2": round(backtest[col].mean(), 3), "simpangan_baku": round(backtest[col].std(), 3),
                                "terburuk": backtest[col].max(),
                                "menang_vs_baseline": int((backtest[col] < backtest["WAPE_baseline"]).sum())}
                          for col in ["WAPE_baseline", "WAPE_linear", "WAPE_linear_std"]}).T
stability = stability.astype({"menang_vs_baseline": int})
print()
print(stability.to_string())

# Keputusan sesuai aturan yang ditulis di Minggu 19
std_wins = int((backtest["WAPE_linear_std"] < backtest["WAPE_linear"]).sum())
use_std = (backtest["WAPE_linear_std"].mean() < backtest["WAPE_linear"].mean()) and std_wins >= 4
FINAL_FEATURES = CANDIDATE_FEATURES if use_std else FEATURES
print(f"\nrolling_std_4 lebih baik di {std_wins} dari 6 periode -> fitur final:", FINAL_FEATURES)
