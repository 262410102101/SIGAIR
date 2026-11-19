"""menu_petugas.py - menu untuk peran Petugas Pembagi Air."""
from jadwal import jadwal_hari_ini, jadwal_per_saluran, update_status
from util import jeda, tampil_menu


def menu_petugas(user):
    opsi = [('1', 'Jadwal hari ini'), ('2', 'Update status jadwal'), ('3', 'Lihat jadwal per saluran')]
    while True:
        pilihan = tampil_menu(f'MENU PETUGAS - {user["username"]}', opsi, label_nol='Logout')
        if pilihan == '1':
            jadwal_hari_ini()
        elif pilihan == '2':
            update_status()
        elif pilihan == '3':
            jadwal_per_saluran()
        elif pilihan == '0':
            return
        else:
            print('Pilihan tidak valid.')
        jeda()
