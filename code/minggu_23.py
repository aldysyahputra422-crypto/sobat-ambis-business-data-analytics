# Blok 0 · minggu_23 · NCG Core Dataset v2.0.0
# PERSIAPAN: kode dari minggu sebelumnya (w17_weekly, w17_baselines, w18_linear, w19_compare, w20_validation, w21_errors, w22_intervals, w22_classification). Jalankan sekali sebelum blok berikutnya.
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

# Model final dilatih ulang pada origin 29 September 2025 dengan semua minggu yang sudah selesai
# (train + valid), lalu diuji SEKALI pada test
final_train = trainable_at(model_data, FIT_ORIGIN_TEST)
assert final_train["week_start"].max() + pd.Timedelta(days=7) <= test["forecast_origin"].min()
final_model = LinearRegression().fit(final_train[FINAL_FEATURES], final_train["demand"])
test = test.copy()
test["forecast"] = final_model.predict(test[FINAL_FEATURES])

print("Test, regresi linear :", evaluate(test["demand"], test["forecast"]))
print("Test, moving avg 4   :", evaluate(test["demand"], test["rolling_mean_4"]))
print()
by_cat = {cat: evaluate(g["demand"], g["forecast"]) for cat, g in test.groupby("category")}
print(pd.DataFrame(by_cat).T)
print()
test["residual"] = test["demand"] - test["forecast"]
print("Residual: mean =", round(test["residual"].mean(), 1),
      "| median =", round(test["residual"].median(), 1),
      "| persentil 5% dan 95% =", np.percentile(test["residual"], [5, 95]).round(1))
worst = test.loc[test["residual"].abs().nlargest(3).index, ["sku_id", "week_start", "demand", "forecast", "residual"]]
print(worst.round({"forecast": 1, "residual": 1}).to_string(index=False))

# Interval prediksi 80% dari residual RELATIF di periode validasi (model dilatih pada train saja)
interval_model = LinearRegression().fit(train[FINAL_FEATURES], train["demand"])
valid_pred = interval_model.predict(valid[FINAL_FEATURES])
relative_error = (valid["demand"] - valid_pred) / np.clip(valid_pred, 1, None)
q_low, q_high = np.quantile(relative_error, [0.10, 0.90])
print(f"Kuantil error relatif: 10% = {q_low:.3f}, 90% = {q_high:.3f}")

test["low_80"] = np.clip(test["forecast"] * (1 + q_low), 0, None)
test["high_80"] = test["forecast"] * (1 + q_high)
inside = (test["demand"] >= test["low_80"]) & (test["demand"] <= test["high_80"])
print(f"Cakupan empiris di test: {inside.mean():.1%} (target 80%)")
print(inside.groupby(test["category"]).mean().round(3).to_string())

example = test[test["sku_id"] == "SKU-001"].iloc[0]
print(f"\nContoh SKU-001 minggu {example['week_start'].date()}: prediksi {example['forecast']:.0f} karton, "
      f"interval 80% [{example['low_80']:.0f}, {example['high_80']:.0f}], aktual {example['demand']:.0f}")

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, confusion_matrix, precision_score, recall_score

# Kejadian: permintaan minggu ini > 1,2 x rata-rata 4 minggu sebelumnya ("lonjakan")
model_data = model_data.assign(spike=(model_data["demand"] > 1.2 * model_data["rolling_mean_4"]).astype(int))
c_train = trainable_at(model_data, FIT_ORIGIN_VALID)
c_test = model_data[model_data["forecast_origin"] >= FIT_ORIGIN_VALID]

classifier = LogisticRegression(max_iter=1000).fit(c_train[FINAL_FEATURES], c_train["spike"])
prob = classifier.predict_proba(c_test[FINAL_FEATURES])[:, 1]
base_rate = c_train["spike"].mean()
print(f"Frekuensi lonjakan: train {base_rate:.3f}, test {c_test['spike'].mean():.3f}")
print(f"Brier score model      : {brier_score_loss(c_test['spike'], prob):.4f}")
print(f"Brier score base rate  : {brier_score_loss(c_test['spike'], np.full(len(c_test), base_rate)):.4f}")

for threshold in [0.5, 0.3]:
    label = (prob >= threshold).astype(int)
    print(f"\nAmbang {threshold}: precision {precision_score(c_test['spike'], label, zero_division=0):.2f}, "
          f"recall {recall_score(c_test['spike'], label):.2f}")
    print(confusion_matrix(c_test["spike"], label))

calibration = pd.DataFrame({"prob": prob, "actual": c_test["spike"].to_numpy()})
calibration["bin"] = pd.cut(calibration["prob"], [0, 0.1, 0.2, 0.3, 0.5, 1.0])
print(calibration.groupby("bin", observed=True)
      .agg(n=("actual", "size"), mean_prob=("prob", "mean"), observed=("actual", "mean")).round(3))

# Blok 1 · minggu_23 · NCG Core Dataset v2.0.0
# Simulasi persediaan mingguan WH-SBY untuk 12 minggu test (6 Oktober - 28 Desember 2025), semua SKU sekaligus.
# Kedua kebijakan mulai dari kondisi yang SAMA: stok, batch, dan PO terbuka pada Senin 6 Oktober 2025 00.00.
# Semua angka di blok PARAMETER adalah asumsi simulasi, bukan data biaya PT NCG. Ubah dan jalankan ulang.
PARAMETER = {
    "biaya_simpan_per_tahun": 0.25,       # proporsi harga pokok per tahun
    "biaya_per_pesanan": 250_000,         # rupiah per PO per SKU
    "lead_time_minggu": 1,                # PO hari Senin tiba Senin berikutnya (KPI-09 WH-SBY: 6,4 hari)
    "umur_saat_diterima_hari": 20,        # umur barang dari produksi saat tiba di gudang
    "kapasitas_keluar_karton": 2 * 360 * 6,  # 2 slot truk x 360 karton x 6 hari kerja = 4.320 per minggu
    "z_safety": 1.2816,                   # target 90% minggu tanpa kekurangan
}
START = pd.Timestamp("2025-10-06")

batches_all = pd.read_csv("data/bersih_inventory_batches.csv",
                          parse_dates=["received_date", "expiry_date"])
snapshots = pd.read_csv("data/bersih_inventory_snapshots.csv", parse_dates=["snapshot_date"])
pos = pd.read_csv("data/bersih_purchase_orders.csv",
                  parse_dates=["order_date", "expected_arrival_date", "actual_arrival_date"])
info = products.set_index("sku_id")
weeks = sorted(test["week_start"].unique())
skus = sorted(test["sku_id"].unique())
actual = test.pivot(index="week_start", columns="sku_id", values="demand")
estimates = {"Baseline: moving average 4": test.pivot(index="week_start", columns="sku_id", values="rolling_mean_4"),
             "Model: regresi linear": test.pivot(index="week_start", columns="sku_id", values="forecast")}

# Ketidakpastian per SKU dari residual VALIDASI (bukan test)
valid_resid = valid.assign(model_err=valid["demand"] - interval_model.predict(valid[FINAL_FEATURES]),
                           base_err=valid["demand"] - valid["rolling_mean_4"])
sigmas = {"Baseline: moving average 4": valid_resid.groupby("sku_id")["base_err"].std(),
          "Model: regresi linear": valid_resid.groupby("sku_id")["model_err"].std()}

# 1. Stok awal: snapshot Senin 29 September (akhir hari), digulir maju dengan transaksi dan penerimaan aktual
#    Selasa 30 September - Minggu 5 Oktober. Hasilnya dipakai oleh KEDUA kebijakan.
#    Stok sistem memuat kesalahan pencatatan (lihat KPI-08). Jika SKU dihitung fisik hari itu, pakai hitungan fisik.
sby_snap = snapshots[(snapshots["warehouse_id"] == "WH-SBY") & (snapshots["snapshot_date"] == "2025-09-29")]
gap = sales[(sales["warehouse_id"] == "WH-SBY") & sales["transaction_date"].between("2025-09-30", "2025-10-05")]
sby_batches = batches_all[batches_all["warehouse_id"] == "WH-SBY"]
received = sby_batches[sby_batches["received_date"].between("2025-09-30", "2025-10-05")]
start_count = sby_snap.set_index("sku_id")
start_count = start_count["on_hand_physical_carton"].fillna(start_count["on_hand_system_carton"])
opening = (start_count
           - gap.groupby("sku_id")["quantity_fulfilled_carton"].sum().reindex(skus, fill_value=0)
           + received.groupby("sku_id")["quantity_received_carton"].sum().reindex(skus, fill_value=0)).clip(lower=0)


def opening_batches(sku):
    """Dengan FEFO, stok yang tersisa adalah batch paling baru. Isi stok awal dari batch terbaru ke lama."""
    rows = sby_batches[(sby_batches["sku_id"] == sku) & (sby_batches["received_date"] <= "2025-10-05")]
    left, out = int(opening[sku]), []
    for _, b in rows.sort_values("received_date", ascending=False).iterrows():
        take = min(left, int(b["quantity_received_carton"]))
        if take > 0:
            out.append([b["expiry_date"], take])
        left -= take
    if left > 0:  # snapshot lebih besar daripada catatan batch: sisanya diberi umur batch tertua
        out.append([rows["expiry_date"].min(), left])
    return out


# 2. PO nyata yang sudah dipesan sebelum 6 Oktober tetapi belum tiba: masuk antrean, sama untuk kedua kebijakan.
#    Barang yang tiba di tengah minggu dianggap siap dijual Senin berikutnya.
open_po = pos[(pos["warehouse_id"] == "WH-SBY") & (pos["order_date"] < START)
              & ~(pos["actual_arrival_date"] < START)].copy()
open_po["arrival"] = open_po["actual_arrival_date"].fillna(open_po["expected_arrival_date"])
open_po["ready_week"] = open_po["arrival"].apply(lambda d: d if d.day_of_week == 0 else d + pd.offsets.Week(weekday=0))
po_expiry = sby_batches.dropna(subset=["po_id"]).set_index("po_id")["expiry_date"]


def run_policy(policy):
    p = PARAMETER
    stock = {sku: opening_batches(sku) for sku in skus}
    pipeline = {}  # minggu siap -> list of (sku, expiry, qty)
    for _, po in open_po.iterrows():
        expiry = po_expiry.get(po["po_id"], po["arrival"] + pd.Timedelta(
            days=int(info.loc[po["sku_id"], "shelf_life_days"]) - p["umur_saat_diterima_hari"]))
        pipeline.setdefault(po["ready_week"], []).append((po["sku_id"], expiry, int(po["quantity_ordered_carton"])))
    estimate, sigma = estimates[policy], sigmas[policy]
    totals = dict.fromkeys(["demand", "shipped", "lost_stock", "lost_truck", "expired", "orders",
                            "holding_rp", "lost_margin_rp", "expiry_rp", "received", "sku_weeks", "sku_weeks_no_stockout",
                            "sku_weeks_complete"], 0)
    start_qty = sum(q for sku in skus for _, q in stock[sku])
    for i, week in enumerate(weeks):
        for sku, expiry, qty in pipeline.pop(week, []):  # penerimaan Senin pagi
            stock[sku].append([expiry, qty])
            totals["received"] += qty
        # Keputusan pesan Senin 06.00: posisi persediaan = stok di tangan + semua PO yang belum tiba.
        # Batas horizon: PO hanya dibuat jika tiba sebelum simulasi berakhir. PO yang tiba sesudahnya tidak
        # melayani permintaan apa pun di simulasi, jadi biaya pesannya tidak boleh dihitung.
        arrive = week + pd.Timedelta(weeks=p["lead_time_minggu"])
        if arrive <= weeks[-1]:
            totals["decisions"] = totals.get("decisions", 0) + 1
            for sku in skus:
                on_hand = sum(q for _, q in stock[sku])
                on_order = sum(q for w, items in pipeline.items() for s, _, q in items if s == sku)
                target = (estimate.loc[week, sku] + estimate.loc[weeks[i + 1], sku]
                          + p["z_safety"] * sigma[sku] * np.sqrt(2))
                qty = int(round(target - on_hand - on_order))
                if qty > 0:
                    life = int(info.loc[sku, "shelf_life_days"]) - p["umur_saat_diterima_hari"]
                    pipeline.setdefault(arrive, []).append((sku, arrive + pd.Timedelta(days=life), qty))
                    totals["orders"] += 1
        # Permintaan minggu ini: dibatasi stok, lalu dibatasi kapasitas truk keluar (dibagi proporsional)
        demand = actual.loc[week]
        can_ship = {sku: min(int(demand[sku]), sum(q for _, q in stock[sku])) for sku in skus}
        total_ship = sum(can_ship.values())
        ratio = min(1.0, p["kapasitas_keluar_karton"] / total_ship) if total_ship else 1.0
        week_end = week + pd.Timedelta(days=7)
        for sku in skus:
            ship = int(can_ship[sku] * ratio)
            cost = info.loc[sku, "unit_cost_idr"]
            margin = info.loc[sku, "list_price_idr"] - cost
            left = ship
            for b in sorted(stock[sku], key=lambda b: b[0]):  # FEFO: kedaluwarsa paling awal keluar dulu
                take = min(b[1], left)
                b[1] -= take
                left -= take
            expired = sum(q for e, q in stock[sku] if e < week_end)
            stock[sku] = [b for b in stock[sku] if b[0] >= week_end and b[1] > 0]
            if int(demand[sku]) > 0:  # dihitung per minggu-SKU yang ada permintaannya
                totals["sku_weeks"] += 1
                # stok cukup: seluruh permintaan bisa dipenuhi dari stok, SEBELUM batasan truk
                totals["sku_weeks_no_stockout"] += int(can_ship[sku] == int(demand[sku]))
                # end-to-end: seluruh permintaan benar-benar terkirim, SESUDAH batasan truk
                totals["sku_weeks_complete"] += int(ship == int(demand[sku]))
            totals["demand"] += int(demand[sku])
            totals["shipped"] += ship
            totals["lost_stock"] += int(demand[sku]) - can_ship[sku]
            totals["lost_truck"] += can_ship[sku] - ship
            totals["expired"] += expired
            totals["lost_margin_rp"] += (int(demand[sku]) - ship) * margin
            totals["expiry_rp"] += expired * cost
            totals["holding_rp"] += (sum(q for _, q in stock[sku]) * cost
                                     * p["biaya_simpan_per_tahun"] / 52)
    totals["ending_stock"] = sum(q for sku in skus for _, q in stock[sku])
    # Verifikasi neraca: stok awal + diterima - dikirim - kedaluwarsa = stok akhir
    assert start_qty + totals["received"] - totals["shipped"] - totals["expired"] == totals["ending_stock"]
    return totals


summary = {}
for policy in estimates:
    t = run_policy(policy)
    summary[policy] = {
        "fill_rate": round(t["shipped"] / t["demand"], 3),
        # dibandingkan dengan target desain z = 1,28 (sekitar 0,90): hanya mengukur kehabisan stok
        "tingkat_tanpa_stockout": round(t["sku_weeks_no_stockout"] / t["sku_weeks"], 3),
        # tidak sebanding dengan target z: ikut memuat kegagalan kirim karena kapasitas truk
        "tingkat_kirim_lengkap": round(t["sku_weeks_complete"] / t["sku_weeks"], 3),
        "karton_hilang_stok": t["lost_stock"],
        "karton_hilang_truk": t["lost_truck"],
        "stok_akhir_minggu12": t["ending_stock"],
        "karton_kedaluwarsa": t["expired"],
        "jumlah_po": t["orders"],
        "margin_hilang_juta": round(t["lost_margin_rp"] / 1e6, 1),
        "biaya_simpan_juta": round(t["holding_rp"] / 1e6, 1),
        "biaya_kedaluwarsa_juta": round(t["expiry_rp"] / 1e6, 1),
        "biaya_pesan_juta": round(t["orders"] * PARAMETER["biaya_per_pesanan"] / 1e6, 1),
    }
    # Total dihitung dari rupiah sebelum pembulatan, agar sama dengan uji sensitivitas
    summary[policy]["total_biaya_juta"] = round((t["lost_margin_rp"] + t["holding_rp"] + t["expiry_rp"]
                                                 + t["orders"] * PARAMETER["biaya_per_pesanan"]) / 1e6, 1)

# Cek silang stok awal: snapshot Senin 6 Oktober (akhir hari) = stok awal - kiriman 6 Oktober + penerimaan 6 Oktober.
# Selisih yang tersisa adalah kesalahan pencatatan baru selama minggu itu, yang belum diketahui pada 6 Oktober.
snap_1006 = snapshots[(snapshots["warehouse_id"] == "WH-SBY") & (snapshots["snapshot_date"] == START)]
day = sales[(sales["warehouse_id"] == "WH-SBY") & (sales["transaction_date"] == START)]
check = (opening - day.groupby("sku_id")["quantity_fulfilled_carton"].sum().reindex(skus, fill_value=0)
         + sby_batches[sby_batches["received_date"] == START].groupby("sku_id")["quantity_received_carton"].sum()
         .reindex(skus, fill_value=0))
diff = (check - snap_1006.set_index("sku_id")["on_hand_system_carton"]).astype(int)
print("Selisih cek silang terhadap stok sistem 6 Oktober:", diff[diff != 0].to_dict())
print(f"Stok awal 6 Oktober (sama untuk kedua kebijakan): {int(opening.sum())} karton; "
      f"PO terbuka di data PT NCG: {len(open_po)} PO, {int(open_po['quantity_ordered_carton'].sum())} karton")
print(pd.DataFrame({k: pd.Series(v, dtype=object) for k, v in summary.items()}).to_string())  # object: bilangan bulat tetap tampil bulat
weekly_total = actual.sum(axis=1)
print("\nMinggu dengan permintaan > kapasitas keluar 4.320 karton:",
      int((weekly_total > PARAMETER["kapasitas_keluar_karton"]).sum()), "dari", len(weeks))

# Uji sensitivitas: ubah SATU asumsi, jalankan ulang kedua kebijakan dari kondisi awal yang sama
def total_cost_juta(t):
    return (t["lost_margin_rp"] + t["holding_rp"] + t["expiry_rp"]
            + t["orders"] * PARAMETER["biaya_per_pesanan"]) / 1e6


ACUAN = dict(PARAMETER)
scenarios = [("acuan", "Acuan", {}),
             ("pesan_100rb", "Biaya pesan Rp100.000", {"biaya_per_pesanan": 100_000}),
             ("pesan_1jt", "Biaya pesan Rp1.000.000", {"biaya_per_pesanan": 1_000_000}),
             ("simpan_40", "Biaya simpan 40%/tahun", {"biaya_simpan_per_tahun": 0.40}),
             ("layanan_80", "Target layanan 80% (z = 0,84)", {"z_safety": 0.8416}),
             ("layanan_95", "Target layanan 95% (z = 1,64)", {"z_safety": 1.6449}),
             ("lead_2", "Lead time 2 minggu", {"lead_time_minggu": 2})]
rows = []
for key, label, change in scenarios:
    PARAMETER.clear()
    PARAMETER.update(ACUAN, **change)
    b, m = run_policy("Baseline: moving average 4"), run_policy("Model: regresi linear")
    cost_b, cost_m = round(total_cost_juta(b), 1), round(total_cost_juta(m), 1)
    rows.append({"key": key, "skenario": label, "biaya_baseline_juta": cost_b, "biaya_model_juta": cost_m,
                 "selisih_juta": round(cost_b - cost_m, 1),  # dari angka yang ditampilkan, agar bisa dicek pembaca
                 "fill_baseline": round(b["shipped"] / b["demand"], 3),
                 "fill_model": round(m["shipped"] / m["demand"], 3)})
PARAMETER.clear()
PARAMETER.update(ACUAN)
sensitivity = pd.DataFrame(rows)
print("\nSensitivitas (selisih positif = model lebih murah):")
print(sensitivity.drop(columns="key").to_string(index=False))
