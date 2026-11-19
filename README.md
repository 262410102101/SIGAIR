# SIGAIR
Sistem Informasi Giliran Air dan Iuran Irigasi Kelompok Tani Berbasis Console
(Python + PostgreSQL)

## Cara menjalankan
1. Install pustaka: `pip install -r requirements.txt`
2. Di pgAdmin, buka Query Tool pada database proyekmu, lalu jalankan `schema.sql`.
   (Opsional untuk demo, pada database kosong) jalankan juga `data_contoh.sql`.
3. Buka `koneksi.py` dan sesuaikan `dbname`, `user`, dan `password`.
4. Jalankan: `python main.py`

## Akun awal
| Username | Password    | Role    |
|----------|-------------|---------|
| admin    | admin123    | admin   |
| petugas  | petugas123  | petugas |
| slamet   | slamet123   | petani (hanya jika memakai data_contoh.sql) |

## Struktur file
| File | Fungsi |
|------|--------|
| main.py | titik masuk, tampilan awal |
| koneksi.py | koneksi dan fungsi akses database |
| util.py | tampilan dan validasi input |
| login.py | login dan hash password |
| menu_admin.py / menu_petugas.py / menu_petani.py | menu per peran |
| master.py | CRUD data master |
| jadwal.py | jadwal otomatis, deteksi bentrok, ubah/batalkan |
| iuran.py | hitung iuran, pembayaran, tunggakan |
| laporan.py | laporan JOIN dan agregasi |
| schema.sql / data_contoh.sql | skema dan data contoh |
