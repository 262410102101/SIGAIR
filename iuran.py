"""iuran.py - hitung iuran air, catat pembayaran, daftar tunggakan."""
from koneksi import ambil, jalankan, jalankan_banyak
from util import (bersihkan, input_float, input_int, input_teks, jeda, judul,
                  konfirmasi, tampil_menu, tampil_tabel)


def rupiah(angka):
    return 'Rp ' + f'{float(angka):,.0f}'.replace(',', '.')


def hitung_iuran():
    bersihkan()
    judul('HITUNG IURAN AIR')
    periode = input_teks('Periode (contoh: 2026-MT1)')
    tarif = input_float('Tarif iuran per hektare (Rp)')

    # Total luas petak per petani; petani yang sudah punya iuran pada periode ini dilewati
    _, baris = ambil(
        'SELECT p.id_petani, p.nama, SUM(s.luas_ha) AS total_luas '
        'FROM petani p JOIN petak_sawah s ON s.id_petani = p.id_petani '
        'WHERE p.id_petani NOT IN (SELECT id_petani FROM iuran_air WHERE periode = %s) '
        'GROUP BY p.id_petani, p.nama ORDER BY p.id_petani', (periode,))
    if not baris:
        print('\nTidak ada petani yang perlu dihitung (semua sudah memiliki iuran pada periode ini).')
        return

    hasil = [(id_petani, nama, float(luas), tarif * float(luas)) for id_petani, nama, luas in baris]
    print()
    tampil_tabel(['ID petani', 'Nama', 'Total luas (ha)', 'Iuran'],
                 [(h[0], h[1], h[2], rupiah(h[3])) for h in hasil])
    print(f'Total iuran: {rupiah(sum(h[3] for h in hasil))}')

    if konfirmasi('\nSimpan iuran ini'):
        jalankan_banyak('INSERT INTO iuran_air (id_petani, periode, jumlah) VALUES (%s, %s, %s)',
                        [(h[0], periode, h[3]) for h in hasil])
        print('Iuran berhasil disimpan.')


def catat_pembayaran():
    bersihkan()
    judul('CATAT PEMBAYARAN IURAN')
    daftar_tunggakan()
    id_iuran = input_int('\nID iuran yang dibayar (0 = batal)', minimal=0)
    if id_iuran == 0:
        return
    if konfirmasi('Tandai iuran ini sebagai lunas'):
        jumlah = jalankan("UPDATE iuran_air SET status_bayar = 'lunas' "
                          "WHERE id_iuran = %s AND status_bayar = 'belum'", (id_iuran,))
        print('Pembayaran berhasil dicatat.' if jumlah else 'ID tidak ditemukan atau sudah lunas.')


def daftar_tunggakan():
    """Menampilkan iuran yang belum dibayar, diurutkan dari jumlah terbesar."""
    kolom, baris = ambil(
        "SELECT i.id_iuran AS id, p.nama, i.periode, i.jumlah FROM iuran_air i "
        "JOIN petani p ON p.id_petani = i.id_petani WHERE i.status_bayar = 'belum' "
        "ORDER BY i.jumlah DESC")
    tampil_tabel(kolom, [(r[0], r[1], r[2], rupiah(r[3])) for r in baris], '(tidak ada tunggakan)')
    if baris:
        print(f'Total tunggakan: {rupiah(sum(r[3] for r in baris))}')


def status_iuran(id_petani):
    bersihkan()
    judul('STATUS IURAN SAYA')
    kolom, baris = ambil('SELECT id_iuran AS id, periode, jumlah, status_bayar AS status FROM iuran_air '
                         'WHERE id_petani = %s ORDER BY id_iuran', (id_petani,))
    tampil_tabel(kolom, [(r[0], r[1], rupiah(r[2]), r[3]) for r in baris], '(belum ada data iuran)')


def menu_iuran():
    opsi = [('1', 'Hitung iuran'), ('2', 'Catat pembayaran'), ('3', 'Daftar tunggakan')]
    while True:
        pilihan = tampil_menu('IURAN AIR', opsi)
        if pilihan == '1':
            hitung_iuran()
        elif pilihan == '2':
            catat_pembayaran()
        elif pilihan == '3':
            bersihkan(); judul('DAFTAR TUNGGAKAN'); daftar_tunggakan()
        elif pilihan == '0':
            return
        else:
            print('Pilihan tidak valid.')
        jeda()
