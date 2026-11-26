# Blok 1 · minggu_16 · NCG Core Dataset v2.0.0
import numpy as np
import pandas as pd
from scipy import stats

sales = pd.read_csv("data/bersih_sales_transactions.csv", parse_dates=["transaction_date"])

# Permintaan harian SKU-001 di WH-SBY, Senin-Sabtu, 2024-2025
daily = (sales[(sales["warehouse_id"] == "WH-SBY") & (sales["sku_id"] == "SKU-001")]
         .groupby("transaction_date")
         .agg(demand=("quantity_ordered_carton", "sum"), promo=("promo_flag", "max"))
         .reset_index())
daily = daily[daily["transaction_date"].dt.day_of_week < 6]

promo = daily.loc[daily["promo"] == 1, "demand"]
normal = daily.loc[daily["promo"] == 0, "demand"]
print(f"Hari promo : n={len(promo)}, rata-rata={promo.mean():.1f}, sd={promo.std():.1f}")
print(f"Hari normal: n={len(normal)}, rata-rata={normal.mean():.1f}, sd={normal.std():.1f}")

# Selisih rata-rata dan interval kepercayaan 95% (Welch)
diff = promo.mean() - normal.mean()
se = np.sqrt(promo.var() / len(promo) + normal.var() / len(normal))
result = stats.ttest_ind(promo, normal, equal_var=False)
print(f"Selisih rata-rata: {diff:.1f} karton/hari")
print(f"CI 95% (pendekatan normal): [{diff - 1.96 * se:.1f}, {diff + 1.96 * se:.1f}]")
print(f"Uji t Welch: t={result.statistic:.2f}, p-value={result.pvalue:.2g}")

# Besar efek: Cohen's d
pooled_sd = np.sqrt((promo.var() + normal.var()) / 2)
print(f"Cohen's d: {diff / pooled_sd:.2f}")

# Bootstrap: interval tanpa asumsi distribusi normal
rng = np.random.default_rng(42)
boot = [rng.choice(promo, len(promo)).mean() - rng.choice(normal, len(normal)).mean() for _ in range(5000)]
print(f"CI 95% bootstrap: [{np.percentile(boot, 2.5):.1f}, {np.percentile(boot, 97.5):.1f}]")
