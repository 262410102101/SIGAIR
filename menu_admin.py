"""menu_admin.py - menu utama untuk peran Admin."""
from iuran import menu_iuran
from jadwal import menu_jadwal
from laporan import menu_laporan
from master import menu_master
from util import tampil_menu, jeda


def menu_admin(user):
    opsi = [('1', 'Kelola Data Master'), ('2', 'Penjadwalan Giliran Air'),
            ('3', 'Iuran Air'), ('4', 'Laporan')]
    while True:
        pilihan = tampil_menu(f'MENU ADMIN - {user["username"]}', opsi, label_nol='Logout')
        if pilihan == '1':
            menu_master()
        elif pilihan == '2':
            menu_jadwal()
        elif pilihan == '3':
            menu_iuran()
        elif pilihan == '4':
            menu_laporan()
        elif pilihan == '0':
            return
        else:
            jeda('Pilihan tidak valid. Tekan Enter untuk melanjutkan.')
