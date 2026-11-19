"""main.py - titik masuk aplikasi SIGAIR.

SIGAIR: Sistem Informasi Giliran Air dan Iuran Irigasi Kelompok Tani Berbasis Console
"""
import os

import psycopg2

from login import login
from menu_admin import menu_admin
from menu_petani import menu_petani
from menu_petugas import menu_petugas
from util import bersihkan, jeda

MENU_PER_ROLE = {'admin': menu_admin, 'petugas': menu_petugas, 'petani': menu_petani}

# Mengaktifkan kode warna pada konsol Windows
if os.name == 'nt':
    os.system('')


def tampilan_awal():
    while True:
        bersihkan()
        print('=' * 78)
        print('SELAMAT DATANG DI SIGAIR'.center(78))
        print('=' * 78)
        print('[1] Login Account')
        print('[0] Keluar')
        print('-' * 78)
        pilihan = input('Pilihan Anda [0-1]: ').strip()

        if pilihan == '1':
            user = login()
            if user:
                print(f'\nLogin berhasil. Selamat datang, {user["username"]} ({user["role"]}).')
                jeda()
                MENU_PER_ROLE[user['role']](user)
            else:
                print('\nTerlalu banyak percobaan gagal.')
                jeda()
        elif pilihan == '0':
            print('\nTerima kasih telah menggunakan SIGAIR.')
            return
        else:
            jeda('Pilihan tidak valid. Tekan Enter untuk melanjutkan.')

def main():
    while True:
        try:
            tampilan_awal()
            return
        except psycopg2.OperationalError as galat:
            print('\nTidak dapat terhubung ke database. Periksa pengaturan di koneksi.py '
                  'dan pastikan PostgreSQL berjalan.')
            print(f'Detail: {str(galat).strip()}')
            return
        except psycopg2.Error as galat:
            print(f'\nTerjadi kesalahan database: {str(galat).strip().splitlines()[0]}')
            jeda()


if __name__ == '__main__':
    main()
