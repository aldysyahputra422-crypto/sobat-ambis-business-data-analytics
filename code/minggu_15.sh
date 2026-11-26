# Blok 1 · minggu_15 · NCG Core Dataset v2.0.0
cd laporan-fill-rate
git init
echo "data/" >> .gitignore           # data tidak ikut diunggah
echo "output/" >> .gitignore
pip freeze > requirements.txt        # catat versi pustaka
git add README.md requirements.txt inventory_report.py .gitignore
git commit -m "Laporan fill rate mingguan: pembersihan, validasi, agregasi"

# Blok 2 · minggu_15 · NCG Core Dataset v2.0.0
git remote add origin https://github.com/nama-anda/laporan-fill-rate.git
git branch -M main
git push -u origin main
