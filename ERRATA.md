# Errata dan masalah yang diketahui

Daftar ini mencatat kesalahan yang sudah ditemukan dan masalah yang masih terbuka. Daftar ini **tidak** berarti semua kemungkinan masalah sudah ditemukan atau diselesaikan. Jika Anda menemukan masalah baru, laporkan lewat [Issues](../../issues/new).

Nomor halaman mengacu pada PDF Ebook Peserta Edisi 2.1 (241 halaman).

## Masalah yang diketahui di Edisi 2.1 (terbuka)

| Kode | Lokasi | Masalah | Dampak | Status |
|---|---|---|---|---|
| K-01 | Lampiran Kamus KPI, kartu KPI-06 (hlm. 225) | KPI-06 bernama "Cycle service level". Definisinya: bagian minggu-SKU berpesanan tanpa kekurangan sama sekali; rumus: minggu-SKU tanpa kekurangan ÷ minggu-SKU dengan pesanan, dari `sales_transactions`. Unit hitungnya adalah minggu-SKU, bukan siklus replenishment yang didefinisikan secara formal, sehingga nama itu belum tepat | Rumus dan angka benar menurut definisi di kartu. Pembaca bisa salah mengira KPI ini mengukur keberhasilan per siklus pemesanan. Baca KPI-06 sebagai tingkat minggu-SKU tanpa kekurangan | Istilah sedang ditinjau untuk pembaruan 2.1.x. Rumus tidak diubah di PDF 2.1 |
| K-02 | Minggu 7, Contoh terpandu 3, `days_of_cover` (hlm. 74–75) | Satu baris berbeda antara PostgreSQL dan SQLite: WH-SMG SKU-018 tercatat 129 hari (PostgreSQL) dan 130 hari (SQLite), karena perbedaan pembulatan `ROUND` | Pengguna SQLite melihat angka berbeda 1 hari pada satu baris. Kesimpulan contoh tidak berubah | Diketahui; tidak diubah |
| K-03 | Angka hasil kode yang disisipkan otomatis, misalnya bias −0,022 | Angka negatif hasil otomatis dicetak dengan tanda hubung (-0,022), sedangkan teks biasa memakai tanda minus (−0,022) | Tampilan saja; nilai benar | Dijadwalkan untuk pembaruan berikutnya |
| K-04 | Blok kode panjang di PDF | Baris kode yang sangat panjang dibungkus ke baris berikutnya di PDF | Menyalin dari PDF dapat merusak indentasi Python | Pakai file di `code/` atau paket kode, bukan PDF |
| K-05 | Paket NCG Core Dataset v2.0.0, folder `code/` | Folder itu berisi kode Edisi 2.0, bukan Edisi 2.1 | Angka Bulan 5–6 dari kode Edisi 2.0 berbeda dari Ebook 2.1 | Pakai paket kode Edisi 2.1. Dataset tidak diubah agar versinya tetap konsisten |
| K-06 | Minggu 19, model gradient boosting | Dengan scikit-learn 1.9, WAPE gradient boosting dapat bergeser sampai sekitar 0,01 dibanding lingkungan rekomendasi (scikit-learn 1.6.1). Model lain tidak berubah | Angka gradient boosting Anda bisa sedikit berbeda dari buku | Dijelaskan di Ebook (bab Persiapan dan Minggu 19); pakai lingkungan rekomendasi untuk mencocokkan angka |
| K-07 | Windows, Google Sheets, Power BI, Google Colab | Langkah untuk platform ini belum diuji oleh tim penyusun | Langkah bisa tidak berjalan persis seperti tertulis | Belum diuji. Laporan pengguna diterima lewat Issues |
| K-08 | Seluruh Edisi 2.1 | Pengujian dilakukan oleh tim penyusun dan belum melalui verifikasi independen atau tinjauan pakar | – | Terbuka |

## Diperbaiki di Edisi 2.1

| Kode | Edisi terdampak | Lokasi | Masalah | Dampak | Perbaikan |
|---|---|---|---|---|---|
| E-01 | 2.0, 2.0.1 | Studi Kasus, gambar model data | Panah relasi salah: `inventory_batches` menuju `sales_transactions` (seharusnya `purchase_orders`), `delivery_records` menuju `purchase_orders` (seharusnya `truck_schedule`), `purchase_orders` menuju `promotion_calendar` (tidak ada relasi) | Pembaca dapat salah memahami struktur JOIN | Diagram digambar ulang dari skema; rujukan foreign key lengkap ada di `schema.sql` |
| E-02 | 2.0, 2.0.1 | Minggu 9, 10, 22 | Nomor gambar ganda, misalnya "Gambar 10. Gambar 10.1." | Tampilan | Nomor manual dihapus |
| E-03 | 2.0, 2.0.1 | Bulan 5–6 | Data latih memuat minggu target yang belum selesai pada forecast origin (kebocoran satu minggu); simulasi persediaan memberi stok awal berbeda kepada dua kebijakan | Angka model dan klaim penghematan Edisi 2.0 tidak sah | Aturan data latih tunggal, simulasi dengan kondisi awal identik; semua angka dihitung ulang. Angka Edisi 2.0 tidak berlaku lagi |

## Diperbaiki di Edisi 2.0.1

| Edisi terdampak | Masalah | Perbaikan |
|---|---|---|
| 2.0 | PDF tercetak pada skala sekitar 69% karena satu tabel hasil query lebih lebar dari area cetak | Skala cetak 100%. Isi, kode, data, dan angka tidak berubah |
