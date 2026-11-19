"""util.py - fungsi bantu tampilan dan validasi input untuk console."""
import os
from datetime import datetime

from tabulate import tabulate

FORMAT_WAKTU = '%Y-%m-%d %H:%M'
FORMAT_TANGGAL = '%Y-%m-%d'


HEADER_ASCII = r"""
════════════════════════════════════════════════════════════════════════════
                                                             /\             
  █████  █████  █████  █████  █████  ████                   /  \            
  █        █    █      █   █    █    █   █                 /    \           
  █████    █    █  ██  █████    █    ████                 |  ~~  |          
      █    █    █   █  █   █    █    █  █                 | ~~~~ |          
  █████  █████  █████  █   █  █████  █   █                 \____/           
  ────────────────────────────────────────                      
        Sistem Informasi Giliran Air dan Iuran Irigasi Kelompok Tani        
════════════════════════════════════════════════════════════════════════════
"""

def bersihkan():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(HEADER_ASCII.strip('\n'))


def jeda(pesan='\nTekan Enter untuk melanjutkan.'):
    input(pesan)


def judul(teks):
    print('=' * 60)
    print(teks.center(60))
    print('=' * 60)


def tampil_tabel(kolom, baris, kosong='(data kosong)'):
    if not baris:
        print(kosong)
    else:
        print(tabulate(baris, headers=kolom, tablefmt='fancy_grid'))


def tampil_menu(judul_menu, opsi, label_nol='Kembali'):
    """Menampilkan menu bernomor dan mengembalikan pilihan pengguna."""
    bersihkan()
    judul(judul_menu)
    for nomor, teks in opsi:
        print(f'{nomor}. {teks}')
    print(f'0. {label_nol}')
    return input('Masukkan pilihan anda: ').strip()


def input_teks(label, wajib=True):
    while True:
        nilai = input(f'{label}: ').strip()
        if nilai:
            return nilai
        if not wajib:
            return None
        print('Input tidak boleh kosong.')


def input_int(label, minimal=None, wajib=True):
    while True:
        mentah = input(f'{label}: ').strip()
        if mentah == '':
            if not wajib:
                return None
            print('Input tidak boleh kosong.')
            continue
        try:
            angka = int(mentah)
        except ValueError:
            print('Input harus berupa angka bulat.')
            continue
        if minimal is not None and angka < minimal:
            print(f'Nilai minimal {minimal}.')
            continue
        return angka


def input_float(label, wajib=True):
    """Membaca bilangan desimal yang lebih dari nol."""
    while True:
        mentah = input(f'{label}: ').strip().replace(',', '.')
        if mentah == '':
            if not wajib:
                return None
            print('Input tidak boleh kosong.')
            continue
        try:
            angka = float(mentah)
        except ValueError:
            print('Input harus berupa angka.')
            continue
        if angka <= 0:
            print('Nilai harus lebih dari nol.')
            continue
        return angka


def input_waktu(label, wajib=True):
    """Membaca tanggal dan jam dengan format YYYY-MM-DD HH:MM."""
    while True:
        mentah = input(f'{label} (YYYY-MM-DD HH:MM): ').strip()
        if mentah == '':
            if not wajib:
                return None
            print('Input tidak boleh kosong.')
            continue
        try:
            return datetime.strptime(mentah, FORMAT_WAKTU)
        except ValueError:
            print('Format salah. Contoh: 2026-11-15 06:00')


def input_tanggal(label, wajib=True):
    """Membaca tanggal dengan format YYYY-MM-DD."""
    while True:
        mentah = input(f'{label} (YYYY-MM-DD): ').strip()
        if mentah == '':
            if not wajib:
                return None
            print('Input tidak boleh kosong.')
            continue
        try:
            return datetime.strptime(mentah, FORMAT_TANGGAL).date()
        except ValueError:
            print('Format salah. Contoh: 2026-11-15')


def konfirmasi(pesan):
    while True:
        jawab = input(f'{pesan} (y/t): ').strip().lower()
        if jawab in ('y', 't'):
            return jawab == 'y'
        print('Jawab dengan y atau t.')
