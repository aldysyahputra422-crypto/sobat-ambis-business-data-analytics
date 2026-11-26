# Sobat Ambis Business Data Analytics

**From Business Problems to Data-Driven Decisions** · Edisi 2.1 · Bahasa Indonesia

Official learning materials for Sobat Ambis Business Data Analytics. Materi utama ditulis dalam Bahasa Indonesia.

Repository ini adalah tempat distribusi resmi materi publik program: Ebook Peserta, paket kode buku, dan dataset latihan.

## Tentang program

Business Data Analytics adalah program belajar terstruktur dari Sobat Ambis. Peserta belajar mengubah masalah bisnis menjadi pertanyaan analitis, lalu menjawabnya dengan data sampai menjadi rekomendasi keputusan.

- **Durasi:** 6 bulan, 24 minggu, 120 jam belajar.
- **Fokus industri:** FMCG, logistik, dan rantai pasok (*supply chain*).
- **Studi kasus:** PT Nusantara Consumer Goods (PT NCG), perusahaan FMCG dengan empat gudang di Indonesia.

> **PT Nusantara Consumer Goods, tokoh, dan seluruh data studi kasus adalah rekaan hasil simulasi.** Dataset tidak memuat data pribadi atau data perusahaan nyata.

### Untuk siapa

Materi ini cocok jika Anda belum pernah belajar data analytics, mahasiswa dengan pengetahuan analisis dasar, sudah bisa spreadsheet atau SQL dasar, pernah belajar pemrograman tingkat pengantar, atau profesional yang ingin memperkuat kemampuan analisis bisnis.

Program ini membangun fondasi untuk peran seperti Data Analyst, Business Intelligence Analyst, Reporting Analyst, Operations Analyst, dan Supply Chain Analyst. Enam bulan tidak membuat Anda ahli di semua profesi data; setelah lulus, Anda tetap perlu memperdalam keahlian sesuai pekerjaan.

### Kurikulum

| Bulan | Tema | Minggu | Jam |
|---|---|---|---:|
| 1 | Fondasi bisnis dan data | 1–4 | 20 |
| 2 | Akuisisi data dan SQL | 5–8 | 20 |
| 3 | Business Intelligence dan pengambilan keputusan (UTS) | 9–12 | 20 |
| 4 | Python dan statistika terapan | 13–16 | 20 |
| 5 | Predictive analytics | 17–20 | 20 |
| 6 | Evaluasi model dan aplikasi bisnis (UAS) | 21–24 | 20 |

### Status

Program ini **tidak berafiliasi dengan universitas mana pun** dan **tidak terakreditasi BNSP**.

Semua pengujian Edisi 2.1 (query SQL, kode Python, pemeriksaan cetak) dilakukan oleh tim penyusun dan **belum melalui verifikasi independen**. Langkah untuk Windows, Google Sheets, Power BI, dan Google Colab **belum diuji**. Lihat [ERRATA.md](ERRATA.md) untuk masalah yang diketahui.

## Isi repository

| Lokasi | Isi | Lisensi |
|---|---|---|
| [Releases → Edition 2.1](../../releases/tag/edition-2.1) | Ebook Peserta (PDF), paket kode (ZIP), dataset (ZIP) | Lihat bagian Lisensi |
| [`code/`](code/) | Isi paket kode buku Edisi 2.1, satu file per minggu dan bahasa | MIT |
| [`LICENSES/`](LICENSES/) | Teks lisensi lengkap | – |
| [`SHA256SUMS.txt`](SHA256SUMS.txt) | Checksum SHA-256 ketiga file rilis | – |
| [`CHANGELOG.md`](CHANGELOG.md) | Riwayat edisi | – |
| [`ERRATA.md`](ERRATA.md) | Kesalahan dan masalah yang diketahui | – |

PDF dan ZIP tidak disimpan di riwayat Git. Ketiganya diterbitkan sebagai aset **GitHub Release**.

## Unduh

Buka halaman rilis [Edition 2.1](../../releases/tag/edition-2.1), lalu unduh:

| File | Isi |
|---|---|
| `Sobat_Ambis_Business_Data_Analytics_Student_Ebook_Edition_2.1_ID.pdf` | Ebook Peserta Edisi 2.1. PDF ini juga melampirkan paket kode dan dataset |
| `BDA_Kode_Buku_Edisi_2.1.zip` | Paket kode buku Edisi 2.1 (`code/`, `README.md`, `LICENSE`, `requirements.txt`, `environment.yml`, `SHA256SUMS.txt`) |
| `NCG_Core_Dataset_v2.0.0.zip` | NCG Core Dataset v2.0.0: data bersih, data mentah latihan, kamus data, skema SQL, alat verifikasi |

### Memeriksa unduhan

Bandingkan SHA-256 file dengan [`SHA256SUMS.txt`](SHA256SUMS.txt). Simpan `SHA256SUMS.txt` di folder yang sama dengan file unduhan, lalu jalankan:

macOS atau Linux:

```bash
shasum -a 256 -c SHA256SUMS.txt
```

Windows (PowerShell), satu file per perintah:

```powershell
Get-FileHash .\NCG_Core_Dataset_v2.0.0.zip -Algorithm SHA256
```

Setelah dataset diekstrak, `tools/verify_environment.py` di dalam paket dataset memeriksa checksum setiap file data.

## Memakai dataset dan kode

1. Unduh dan ekstrak `NCG_Core_Dataset_v2.0.0.zip`. Ikuti `README_DATA.md` di dalamnya.
2. Dapatkan kode dengan salah satu cara: unduh `BDA_Kode_Buku_Edisi_2.1.zip` dari halaman rilis, atau *clone* repository ini dan pakai folder `code/`.
3. Buat folder `data/` di sebelah folder `code/`. Salin `clean/bersih_*.csv` dan `raw/mentah_*.csv` dari paket dataset ke folder `data/`.
4. Pasang lingkungan Python (lihat Persyaratan software), lalu jalankan dari folder yang berisi `code/` dan `data/`, misalnya:

```bash
python code/minggu_18.py
```

Setiap file `code/minggu_NN.py` dapat dijalankan sendiri dan berisi blok kode satu minggu sesuai urutan di buku. Salin kode dari file ini, bukan dari PDF, agar indentasi Python tetap benar.

> Paket dataset v2.0.0 juga memiliki folder `code/`. Folder itu berisi kode **Edisi 2.0**. Untuk Edisi 2.1, pakai paket kode Edisi 2.1 atau folder `code/` di repository ini.

Dataset tidak berubah di Edisi 2.1. Versinya tetap **v2.0.0**.

## Persyaratan software

Lingkungan yang diuji tim penyusun: **Python 3.12 di macOS**.

| Paket Python | Versi |
|---|---|
| pandas | 2.2.3 |
| numpy | 2.0.2 |
| scikit-learn | 1.6.1 |
| scipy | 1.14.1 |
| matplotlib | 3.9.4 |
| pyparsing | 3.2.3 |
| jupyterlab | ≥ 4.2 |

Pasang dengan `pip install -r code/requirements.txt` atau `conda env create -f code/environment.yml`. Versi lain dapat memberi angka sedikit berbeda; Ebook bab Persiapan memuat matriks kompatibilitas yang diuji.

Perangkat lain yang dipakai buku:

- spreadsheet: Google Sheets, LibreOffice Calc, atau Microsoft Excel;
- database: PostgreSQL + pgAdmin 4, atau SQLite + DB Browser for SQLite (query diuji di PostgreSQL 16.2 dan SQLite 3);
- dashboard: Power BI Desktop (hanya Windows) atau Data Studio (browser).

Windows, Google Sheets, Power BI, dan Google Colab **belum diuji** oleh tim penyusun untuk Edisi 2.1. Jika Anda menemukan masalah di platform tersebut, laporkan lewat Issues.

## Lisensi

Setiap komponen memiliki lisensi sendiri.

| Komponen | Lisensi | Teks lisensi |
|---|---|---|
| Teks dan ilustrasi orisinal Ebook Peserta | CC BY-NC-ND 4.0 | [`LICENSES/LICENSE-BOOK-CC-BY-NC-ND-4.0.txt`](LICENSES/LICENSE-BOOK-CC-BY-NC-ND-4.0.txt) |
| Kode orisinal dalam paket kode dan folder `code/`, serta cuplikan kode yang identik di Ebook | MIT | [`LICENSES/LICENSE-CODE-MIT.txt`](LICENSES/LICENSE-CODE-MIT.txt) |
| NCG Core Dataset v2.0.0 | CC BY-NC 4.0 | [`LICENSES/LICENSE-DATA-CC-BY-NC-4.0.txt`](LICENSES/LICENSE-DATA-CC-BY-NC-4.0.txt) dan `LICENSE-DATA.md` di paket dataset |

- © 2026 Aldi Syaputra. Diterbitkan oleh Sobat Ambis.
- Lisensi MIT **tidak** berlaku untuk teks dan ilustrasi buku, dataset, atau dependensi pihak ketiga.
- Materi pihak ketiga yang disebut di buku (misalnya dataset Kaggle untuk latihan tambahan, huruf, dan dokumentasi perangkat lunak) mengikuti lisensinya masing-masing dan **tidak** didistribusikan di repository ini.
- Atribusi dataset yang disarankan: *NCG Core Dataset v2.0.0, Sobat Ambis (2026), CC BY-NC 4.0.*

## Melaporkan kesalahan

Jika Anda menemukan instruksi yang tidak berjalan, angka yang tidak cocok, atau penjelasan yang membingungkan, buka **[Issue baru](../../issues/new)** dan sertakan:

1. edisi dan nomor halaman (misalnya "Edisi 2.1, hlm. 199");
2. versi dataset (v2.0.0);
3. sistem operasi dan versi software (misalnya Python 3.12, pandas 2.2.3);
4. langkah yang Anda jalankan;
5. hasil yang Anda dapat (pesan error lengkap jika ada) dan hasil yang Anda harapkan.

Jangan menyertakan data pribadi, password, atau token di Issue. Laporan yang terbukti benar dicatat di [ERRATA.md](ERRATA.md) dan diperbaiki pada edisi berikutnya: perbaikan kecil sebagai 2.1.x, perubahan materi sebagai 2.2.

Repository ini hanya berisi materi peserta. Materi mentor tidak dipublikasikan.
