# Changelog

Riwayat lengkap ada di Ebook Peserta, Lampiran Riwayat Versi dan Errata. Masalah yang diketahui: [ERRATA.md](ERRATA.md).

## Edisi 2.1 — November 2026

Rilis publik pertama di repository ini. Dataset tetap NCG Core Dataset v2.0.0.

- **Minggu 17–23, UAS:** satu aturan data latih. Baris dipakai hanya jika minggunya sudah selesai pada forecast origin. Semua model, interval, klasifikasi, dan simulasi dihitung ulang (errata E-03).
- **Minggu 18:** fitur Lebaran hanya memakai tanggal yang sudah diumumkan lewat SKB 3 Menteri pada forecast origin.
- **Minggu 19–20:**
  - Minggu 19 memilih model dengan backtest sederhana tiga origin dan aturan keputusan yang ditulis sebelum hasil.
  - Minggu 20 memakai backtest enam origin dan tabel kestabilan.
  - Model final memakai tujuh fitur: WAPE test 0,184, bias −0,022, baseline 0,209.
- **Minggu 23:** simulasi persediaan yang adil:
  - stok awal dan PO terbuka identik untuk kedua kebijakan;
  - kapasitas truk sebagai batasan;
  - sensitivitas tujuh skenario;
  - dua ukuran layanan yang dipisahkan.
- **Konten baru:**
  - subbab proses bisnis di Minggu 1;
  - grafik Matplotlib di Minggu 14;
  - teknik pengambilan sampel di Minggu 16;
  - paragraf interpretasi hasil;
  - kotak "kapan konsep ini tidak tepat dipakai";
  - 12 kartu KPI.
- **Kode:** paket terpisah `BDA_Kode_Buku_Edisi_2.1.zip`, berlisensi MIT, dengan `pyparsing==3.2.3`.
- **Tampilan:**
  - sistem visual Edisi 1.0 dipulihkan;
  - isi 10,5 pt, teks diagram minimal 9 pt;
  - diagram teknis digambar ulang sesuai kode dan skema.
- **Errata diperbaiki:** E-01 (panah ERD), E-02 (nomor gambar ganda), E-03 (kebocoran satu minggu dan simulasi tidak adil).

## Edisi 2.0.1 — November 2026 (digantikan)

Cetak terkoreksi. Edisi 2.0 tercetak pada skala sekitar 69%; Edisi 2.0.1 tercetak 100%. Isi tidak berubah.

## Edisi 2.0 — November 2026 (digantikan)

- Fitur promosi memakai `promotion_calendar` dengan aturan `announced_at` ≤ forecast origin.
- Satu garis waktu forecast.
- Simulasi persediaan 12 minggu.
- NCG Core Dataset v2.0.0 dengan SHA-256 dan manifest.
- Kamus KPI dan templat dokumen profesional.

## Edisi 1.0 — November 2026 (digantikan)

Edisi pertama.
