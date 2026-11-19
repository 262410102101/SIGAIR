"""koneksi.py - koneksi dan fungsi bantu akses database PostgreSQL."""
from contextlib import closing

import psycopg2

# Sesuaikan dengan pengaturan PostgreSQL di komputermu
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'kolab algo x basduy',
    'user': 'postgres',
    'password': '123', 
}


def koneksi():
    """Membuat koneksi baru ke database."""
    return psycopg2.connect(**DB_CONFIG)


def ambil(sql, params=None):
    """Menjalankan SELECT. Mengembalikan (daftar_kolom, daftar_baris)."""
    with closing(koneksi()) as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        kolom = [d[0] for d in cur.description]
        return kolom, cur.fetchall()


def jalankan(sql, params=None):
    """Menjalankan INSERT/UPDATE/DELETE. Mengembalikan jumlah baris terpengaruh."""
    conn = koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            jumlah = cur.rowcount
        conn.commit()
        return jumlah
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def jalankan_banyak(sql, daftar_params):
    """Menjalankan satu perintah untuk banyak data dalam satu transaksi."""
    conn = koneksi()
    try:
        with conn.cursor() as cur:
            cur.executemany(sql, daftar_params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
