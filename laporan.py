"""laporan.py - laporan dengan query JOIN dan agregasi (SUM, COUNT, GROUP BY)."""
from iuran import daftar_tunggakan, rupiah
from jadwal import tampil_jadwal, tampil_musim
from koneksi import ambil
from util import bersihkan, input_int, jeda, judul, tampil_menu, tampil_tabel


def rekap_pemakaian_air():
    bersihkan()
    judul('REKAP PEMAKAIAN AIR PER SALURAN')
    kolom, baris = ambil(
        "SELECT s.nama_saluran AS saluran, COUNT(j.id_jadwal) AS jumlah_jadwal, "
        "COALESCE(SUM(j.durasi_jam), 0) AS total_jam "
        "FROM saluran s "
        "LEFT JOIN petak_sawah p ON p.id_saluran = s.id_saluran "
        "LEFT JOIN jadwal_giliran j ON j.id_petak = p.id_petak AND j.status <> 'batal' "
        "GROUP BY s.id_saluran, s.nama_saluran ORDER BY total_jam DESC")
    tampil_tabel(kolom, baris)


def laporan_penunggak():
    bersihkan()
    judul('DAFTAR PENUNGGAK IURAN')
    daftar_tunggakan()


def riwayat_jadwal_musim():
    bersihkan()
    judul('RIWAYAT JADWAL PER MUSIM TANAM')
    tampil_musim()
    id_musim = input_int('\nID musim tanam', minimal=1)
    print()
    tampil_jadwal('WHERE m.id_musim = %s', (id_musim,))


def rekap_pemasukan():
    bersihkan()
    judul('REKAP PEMASUKAN IURAN PER PERIODE')
    kolom, baris = ambil(
        "SELECT periode, COUNT(*) AS jumlah_pembayaran, SUM(jumlah) AS total "
        "FROM iuran_air WHERE status_bayar = 'lunas' GROUP BY periode ORDER BY periode")
    tampil_tabel(kolom, [(r[0], r[1], rupiah(r[2])) for r in baris], '(belum ada pembayaran)')
    if baris:
        print(f'Total pemasukan: {rupiah(sum(r[2] for r in baris))}')


def menu_laporan():
    opsi = [('1', 'Rekap pemakaian air per saluran'), ('2', 'Daftar penunggak iuran'),
            ('3', 'Riwayat jadwal per musim tanam'), ('4', 'Rekap pemasukan iuran')]
    while True:
        pilihan = tampil_menu('LAPORAN', opsi)
        if pilihan == '1':
            rekap_pemakaian_air()
        elif pilihan == '2':
            laporan_penunggak()
        elif pilihan == '3':
            riwayat_jadwal_musim()
        elif pilihan == '4':
            rekap_pemasukan()
        elif pilihan == '0':
            return
        else:
            print('Pilihan tidak valid.')
        jeda()
