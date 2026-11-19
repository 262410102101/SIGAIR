"""login.py - autentikasi pengguna."""
import getpass
import hashlib

from koneksi import ambil
from util import bersihkan, jeda, judul

MAKS_PERCOBAAN = 3


def hash_password(password):
    """Mengubah password menjadi hash SHA-256 agar tidak tersimpan sebagai teks biasa."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def login():
    """Meminta username dan password. Mengembalikan data pengguna, atau None jika gagal."""
    for sisa in range(MAKS_PERCOBAAN - 1, -1, -1):
        bersihkan()
        judul('LOGIN')
        username = input('Username: ').strip()
        password = getpass.getpass('Password: ')

        _, baris = ambil(
            'SELECT id_pengguna, username, role, id_petani '
            'FROM pengguna WHERE username = %s AND password = %s',
            (username, hash_password(password)),
        )
        if baris:
            id_pengguna, nama_pengguna, role, id_petani = baris[0]
            return {
                'id_pengguna': id_pengguna,
                'username': nama_pengguna,
                'role': role,
                'id_petani': id_petani,
            }
        print(f'Username atau password salah. Sisa percobaan: {sisa}')
        jeda()
    return None
