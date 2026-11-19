"""menu_petani.py - menu untuk peran Petani (hanya melihat data miliknya sendiri)."""
from iuran import status_iuran
from jadwal import jadwal_saya
from util import jeda, tampil_menu


def menu_petani(user):
    if user['id_petani'] is None:
        print('Akun ini belum terhubung ke data petani. Hubungi Admin.')
        jeda()
        return
    opsi = [('1', 'Jadwal giliran air saya'), ('2', 'Status iuran saya')]
    while True:
        pilihan = tampil_menu(f'MENU PETANI - {user["username"]}', opsi, label_nol='Logout')
        if pilihan == '1':
            jadwal_saya(user['id_petani'])
        elif pilihan == '2':
            status_iuran(user['id_petani'])
        elif pilihan == '0':
            return
        else:
            print('Pilihan tidak valid.')
        jeda()
