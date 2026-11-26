# Kode buku Business Data Analytics Edisi 2.1

Isi:
- `code/minggu_NN.py`, `.sql`, `.sh`, `.ps1`, `.rumus.txt`, `.dax.txt`: semua blok kode buku, satu file per minggu dan bahasa,
  urut seperti di buku ("Blok 1", "Blok 2", ...). File Python diawali "Blok 0 · Persiapan" sehingga dapat dijalankan sendiri.
- `requirements.txt`, `environment.yml`: lingkungan rekomendasi Edisi 2.1.

Cara pakai:
1. Ekstrak NCG Core Dataset v2.0.0 (data tidak berubah di Edisi 2.1).
2. Salin `clean/bersih_*.csv` dan `raw/mentah_*.csv` ke folder `data/` di sebelah folder `code/`.
3. Jalankan, misalnya: `python code/minggu_18.py`.

Catatan: folder `code/` di dalam paket dataset v2.0.0 berisi kode Edisi 2.0. Untuk Edisi 2.1, pakai paket ini.
Status pengujian: author-tested (dijalankan tim penyusun di Python 3.12, macOS), belum diverifikasi independen.
Windows, Google Sheets, Power BI, dan Google Colab: belum diuji.

Lisensi:
Kode orisinal dalam paket ini, dan cuplikan kode yang identik di Ebook Peserta, berlisensi MIT
(lihat file `LICENSE`). Copyright (c) 2026 Aldi Syaputra.
Lisensi MIT tidak berlaku untuk teks dan ilustrasi buku (CC BY-NC-ND 4.0), Buku Panduan Mentor,
NCG Core Dataset v2.0.0 (CC BY-NC 4.0), atau dependensi pihak ketiga (lisensi masing-masing).
Pertahankan pemberitahuan hak cipta dan lisensi ini pada setiap salinan atau bagian substansial kode.
