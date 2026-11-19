"""master.py - kelola data master (petani, saluran, petak sawah, musim tanam, pengguna).

CRUD dibuat berbasis konfigurasi (dictionary ENTITAS) agar satu rangkaian fungsi
dapat dipakai untuk semua tabel master.
"""
import getpass
from datetime import datetime

import psycopg2

from koneksi import ambil, jalankan
from login import hash_password
from util import (FORMAT_TANGGAL, input_int, input_teks, jeda, judul, bersihkan,
                  konfirmasi, tampil_menu, tampil_tabel)

# field: (nama_kolom, label, tipe)
# tipe: teks, teks_opsional, int, int_opsional, float_positif, float_opsional,
#       tanggal, password, pilihan:a,b,c
ENTITAS = {
    '1': {
        'judul': 'Data Petani', 'tabel': 'petani', 'pk': 'id_petani',
        'dasar': 'SELECT id_petani, nama, alamat, no_hp FROM petani',
        'urut': 'id_petani', 'cari': 'nama', 'rujukan': [],
        'field': [('nama', 'Nama', 'teks'),
                  ('alamat', 'Alamat', 'teks_opsional'),
                  ('no_hp', 'No. HP', 'teks_opsional')],
    },
    '2': {
        'judul': 'Data Saluran', 'tabel': 'saluran', 'pk': 'id_saluran',
        'dasar': 'SELECT id_saluran, nama_saluran, debit_air, panjang FROM saluran',
        'urut': 'id_saluran', 'cari': 'nama_saluran', 'rujukan': [],
        'field': [('nama_saluran', 'Nama saluran', 'teks'),
                  ('debit_air', 'Debit air (liter/detik)', 'float_positif'),
                  ('panjang', 'Panjang saluran (m)', 'float_opsional')],
    },
    '3': {
        'judul': 'Data Petak Sawah', 'tabel': 'petak_sawah', 'pk': 'id_petak',
        'dasar': ('SELECT p.id_petak, pt.nama AS petani, s.nama_saluran AS saluran, '
                  'p.luas_ha, p.jenis_tanaman '
                  'FROM petak_sawah p '
                  'JOIN petani pt ON pt.id_petani = p.id_petani '
                  'JOIN saluran s ON s.id_saluran = p.id_saluran'),
        'urut': 'p.id_petak', 'cari': 'p.jenis_tanaman', 'rujukan': ['1', '2'],
        'field': [('id_petani', 'ID petani pemilik', 'int'),
                  ('id_saluran', 'ID saluran yang mengairi', 'int'),
                  ('luas_ha', 'Luas (hektare)', 'float_positif'),
                  ('jenis_tanaman', 'Jenis tanaman', 'teks_opsional')],
    },
    '4': {
        'judul': 'Data Musim Tanam', 'tabel': 'musim_tanam', 'pk': 'id_musim',
        'dasar': 'SELECT id_musim, nama_musim, tgl_mulai, tgl_selesai FROM musim_tanam',
        'urut': 'id_musim', 'cari': 'nama_musim', 'rujukan': [],
        'field': [('nama_musim', 'Nama musim', 'teks'),
                  ('tgl_mulai', 'Tanggal mulai', 'tanggal'),
                  ('tgl_selesai', 'Tanggal selesai', 'tanggal')],
    },
    '5': {
        'judul': 'Data Pengguna', 'tabel': 'pengguna', 'pk': 'id_pengguna',
        'dasar': 'SELECT id_pengguna, username, role, id_petani FROM pengguna',
        'urut': 'id_pengguna', 'cari': 'username', 'rujukan': ['1'],
        'field': [('username', 'Username', 'teks'),
                  ('password', 'Password (min. 6 karakter)', 'password'),
                  ('role', 'Role (admin/petugas/petani)', 'pilihan:admin,petugas,petani'),
                  ('id_petani', 'ID petani (khusus role petani)', 'int_opsional')],
    },
}


def parse(tipe, mentah):
    """Mengubah teks masukan menjadi nilai sesuai tipe. Melempar ValueError jika tidak valid."""
    dasar = tipe.split(':')[0]
    if dasar.startswith('pilihan'):
        opsi = tipe.split(':')[1].split(',')
        if mentah.lower() in opsi:
            return mentah.lower()
        raise ValueError('pilih salah satu: ' + ', '.join(opsi))
    if dasar.startswith('int'):
        try:
            return int(mentah)
        except ValueError:
            raise ValueError('harus berupa angka bulat')
    if dasar.startswith('float'):
        try:
            angka = float(mentah.replace(',', '.'))
        except ValueError:
            raise ValueError('harus berupa angka')
        if angka <= 0:
            raise ValueError('harus lebih dari nol')
        return angka
    if dasar == 'tanggal':
        try:
            return datetime.strptime(mentah, FORMAT_TANGGAL).date()
        except ValueError:
            raise ValueError('format harus YYYY-MM-DD')
    if dasar == 'password':
        if len(mentah) < 6:
            raise ValueError('minimal 6 karakter')
        return hash_password(mentah)
    return mentah


def baca_nilai(tipe, label, edit=False, lama=None):
    """Membaca satu isian. Pada mode edit, Enter kosong berarti nilai lama dipertahankan."""
    dasar = tipe.split(':')[0]
    opsional = dasar.endswith('opsional')
    while True:
        if edit:
            tampil = 'tersembunyi' if dasar == 'password' else lama
            petunjuk = f'{label} [{tampil}] (Enter = tetap): '
        else:
            petunjuk = f'{label}{" (opsional)" if opsional else ""}: '
        mentah = (getpass.getpass(petunjuk) if dasar == 'password' else input(petunjuk)).strip()

        if mentah == '':
            if edit:
                return lama
            if opsional:
                return None
            print(f'{label} tidak boleh kosong.')
            continue
        try:
            return parse(tipe, mentah)
        except ValueError as galat:
            print(f'Input tidak valid: {galat}.')


def pesan_galat(galat):
    baris_pertama = str(galat).strip().splitlines()[0]
    if isinstance(galat, psycopg2.IntegrityError):
        return ('Gagal: data tidak valid atau melanggar aturan relasi '
                '(ID terkait tidak ada, username sudah dipakai, atau data masih dipakai tabel lain).\n'
                f'Detail: {baris_pertama}')
    return f'Gagal: {baris_pertama}'


def lihat(e, kata=None):
    sql = e['dasar']
    params = None
    if kata:
        sql += f" WHERE {e['cari']} ILIKE %s"
        params = (f'%{kata}%',)
    sql += f" ORDER BY {e['urut']}"
    kolom, baris = ambil(sql, params)
    tampil_tabel(kolom, baris)


def tampil_rujukan(e):
    """Menampilkan data tabel lain yang ID-nya perlu diketik pengguna."""
    for kode in e['rujukan']:
        print(f"\n{ENTITAS[kode]['judul']}:")
        lihat(ENTITAS[kode])
    if e['rujukan']:
        print()


def tambah(e):
    bersihkan()
    judul(f"TAMBAH {e['judul'].upper()}")
    tampil_rujukan(e)
    nilai = [baca_nilai(tipe, label) for _, label, tipe in e['field']]
    kolom = ', '.join(k for k, _, _ in e['field'])
    penampung = ', '.join(['%s'] * len(nilai))
    try:
        jalankan(f"INSERT INTO {e['tabel']} ({kolom}) VALUES ({penampung})", nilai)
        print('\nData berhasil ditambahkan.')
    except psycopg2.Error as galat:
        print('\n' + pesan_galat(galat))


def ubah(e):
    bersihkan()
    judul(f"UBAH {e['judul'].upper()}")
    lihat(e)
    id_data = input_int('\nMasukkan ID yang ingin diubah (0 = batal)', minimal=0)
    if id_data == 0:
        return
    kolom = [k for k, _, _ in e['field']]
    _, baris = ambil(f"SELECT {', '.join(kolom)} FROM {e['tabel']} WHERE {e['pk']} = %s", (id_data,))
    if not baris:
        print('ID tidak ditemukan.')
        return
    print()
    tampil_rujukan(e)
    nilai = [baca_nilai(tipe, label, edit=True, lama=baris[0][i])
             for i, (_, label, tipe) in enumerate(e['field'])]
    if not konfirmasi('Simpan perubahan'):
        print('Perubahan dibatalkan.')
        return
    atur = ', '.join(f'{k} = %s' for k in kolom)
    try:
        jalankan(f"UPDATE {e['tabel']} SET {atur} WHERE {e['pk']} = %s", nilai + [id_data])
        print('\nData berhasil diperbarui.')
    except psycopg2.Error as galat:
        print('\n' + pesan_galat(galat))


def hapus(e):
    bersihkan()
    judul(f"HAPUS {e['judul'].upper()}")
    lihat(e)
    id_data = input_int('\nMasukkan ID yang ingin dihapus (0 = batal)', minimal=0)
    if id_data == 0:
        return
    if not konfirmasi('Apakah Anda yakin ingin menghapus data ini'):
        print('Penghapusan dibatalkan.')
        return
    try:
        jumlah = jalankan(f"DELETE FROM {e['tabel']} WHERE {e['pk']} = %s", (id_data,))
        print('\nData berhasil dihapus.' if jumlah else '\nID tidak ditemukan.')
    except psycopg2.Error as galat:
        print('\n' + pesan_galat(galat))


def cari(e):
    bersihkan()
    judul(f"CARI {e['judul'].upper()}")
    kata = input_teks('Kata kunci pencarian')
    print()
    lihat(e, kata)


def menu_entitas(e):
    opsi = [('1', 'Lihat data'), ('2', 'Tambah data'), ('3', 'Ubah data'),
            ('4', 'Hapus data'), ('5', 'Cari data')]
    while True:
        pilihan = tampil_menu(e['judul'].upper(), opsi)
        if pilihan == '1':
            bersihkan(); judul(e['judul'].upper()); lihat(e)
        elif pilihan == '2':
            tambah(e)
        elif pilihan == '3':
            ubah(e)
        elif pilihan == '4':
            hapus(e)
        elif pilihan == '5':
            cari(e)
        elif pilihan == '0':
            return
        else:
            print('Pilihan tidak valid.')
        jeda()


def menu_master():
    opsi = [(kode, e['judul']) for kode, e in ENTITAS.items()]
    while True:
        pilihan = tampil_menu('KELOLA DATA MASTER', opsi)
        if pilihan in ENTITAS:
            menu_entitas(ENTITAS[pilihan])
        elif pilihan == '0':
            return
        else:
            jeda('Pilihan tidak valid. Tekan Enter untuk melanjutkan.')
