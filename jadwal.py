"""jadwal.py - penjadwalan giliran air: pembuatan otomatis, deteksi bentrok, lihat/ubah/batalkan."""
from datetime import timedelta

from koneksi import ambil, jalankan, jalankan_banyak
from util import (bersihkan, input_int, input_tanggal, input_waktu, jeda, judul,
                  konfirmasi, tampil_menu, tampil_tabel)

SELESAI = "j.tanggal_mulai + j.durasi_jam * INTERVAL '1 hour'"

SQL_JADWAL = f"""
SELECT j.id_jadwal AS id, s.nama_saluran AS saluran, p.id_petak AS petak,
       pt.nama AS petani, m.nama_musim AS musim,
       to_char(j.tanggal_mulai, 'YYYY-MM-DD HH24:MI') AS mulai,
       to_char({SELESAI}, 'YYYY-MM-DD HH24:MI') AS selesai,
       j.durasi_jam AS jam, j.status
FROM jadwal_giliran j
JOIN petak_sawah p  ON p.id_petak   = j.id_petak
JOIN petani pt      ON pt.id_petani = p.id_petani
JOIN saluran s      ON s.id_saluran = p.id_saluran
JOIN musim_tanam m  ON m.id_musim   = j.id_musim
"""


def hitung_durasi(daftar_luas, total_jam):
    """Membagi total_jam ke tiap petak secara proporsional terhadap luasnya.

    durasi = (luas_petak / total_luas) x total_jam, dibulatkan ke bilangan bulat.
    Selisih akibat pembulatan ditambahkan ke petak terakhir.
    """
    total_luas = sum(daftar_luas)
    durasi = [int(luas / total_luas * total_jam + 0.5) for luas in daftar_luas]
    durasi[-1] += total_jam - sum(durasi)
    if any(d < 1 for d in durasi):
        raise ValueError('Total jam terlalu kecil, ada petak yang mendapat kurang dari 1 jam.')
    return durasi


def cek_bentrok(id_saluran, mulai, selesai, abaikan_id=None):
    """Mengembalikan jadwal aktif pada saluran yang sama yang waktunya tumpang tindih.

    Dua interval bentrok jika mulai_A < selesai_B dan mulai_B < selesai_A.
    """
    sql = f"""
        SELECT j.id_jadwal, j.id_petak, j.tanggal_mulai, {SELESAI} AS selesai
        FROM jadwal_giliran j
        JOIN petak_sawah p ON p.id_petak = j.id_petak
        WHERE p.id_saluran = %s AND j.status <> 'batal'
          AND j.tanggal_mulai < %s AND {SELESAI} > %s
    """
    params = [id_saluran, selesai, mulai]
    if abaikan_id is not None:
        sql += ' AND j.id_jadwal <> %s'
        params.append(abaikan_id)
    return ambil(sql + ' ORDER BY j.tanggal_mulai', params)


def tampil_jadwal(where='', params=None):
    kolom, baris = ambil(f'{SQL_JADWAL} {where} ORDER BY j.tanggal_mulai, j.id_jadwal', params)
    tampil_tabel(kolom, baris, '(belum ada jadwal)')


def tampil_saluran():
    kolom, baris = ambil('SELECT id_saluran AS id, nama_saluran, debit_air FROM saluran ORDER BY id_saluran')
    tampil_tabel(kolom, baris)


def tampil_musim():
    kolom, baris = ambil('SELECT id_musim AS id, nama_musim, tgl_mulai, tgl_selesai FROM musim_tanam ORDER BY id_musim')
    tampil_tabel(kolom, baris)


def buat_jadwal_otomatis():
    bersihkan()
    judul('BUAT JADWAL GILIRAN OTOMATIS')
    print('Saluran:')
    tampil_saluran()
    id_saluran = input_int('\nID saluran', minimal=1)
    _, petak = ambil('SELECT id_petak, luas_ha FROM petak_sawah WHERE id_saluran = %s ORDER BY id_petak',
                     (id_saluran,))
    if not petak:
        print('Saluran tidak ditemukan atau belum memiliki petak sawah.')
        return

    print('\nMusim tanam:')
    tampil_musim()
    id_musim = input_int('\nID musim tanam', minimal=1)
    _, ada = ambil('SELECT 1 FROM musim_tanam WHERE id_musim = %s', (id_musim,))
    if not ada:
        print('Musim tanam tidak ditemukan.')
        return

    mulai = input_waktu('Tanggal dan jam mulai')
    total_jam = input_int('Total jam air tersedia', minimal=1)

    try:
        durasi = hitung_durasi([float(luas) for _, luas in petak], total_jam)
    except ValueError as galat:
        print(galat)
        return

    rencana = []
    waktu = mulai
    for (id_petak, luas), jam in zip(petak, durasi):
        selesai = waktu + timedelta(hours=jam)
        rencana.append((id_petak, float(luas), jam, waktu, selesai))
        waktu = selesai

    print('\nRancangan jadwal:')
    tampil_tabel(['Petak', 'Luas (ha)', 'Durasi (jam)', 'Mulai', 'Selesai'],
                 [(r[0], r[1], r[2], r[3].strftime('%Y-%m-%d %H:%M'), r[4].strftime('%Y-%m-%d %H:%M'))
                  for r in rencana])

    kolom, bentrok = cek_bentrok(id_saluran, rencana[0][3], rencana[-1][4])
    if bentrok:
        print('\nTerdapat jadwal yang bentrok pada saluran ini:')
        tampil_tabel(['ID jadwal', 'Petak', 'Mulai', 'Selesai'], bentrok)
        print('Ubah tanggal mulai atau total jam, lalu coba lagi.')
        return
    print('\nTidak ada bentrok.')

    if konfirmasi('Simpan jadwal ini'):
        jalankan_banyak(
            'INSERT INTO jadwal_giliran (id_petak, id_musim, tanggal_mulai, durasi_jam) '
            'VALUES (%s, %s, %s, %s)',
            [(r[0], id_musim, r[3], r[2]) for r in rencana])
        print('Jadwal berhasil disimpan.')
    else:
        print('Jadwal tidak disimpan.')


def menu_lihat_jadwal():
    opsi = [('1', 'Semua jadwal'), ('2', 'Per saluran'), ('3', 'Per petani'),
            ('4', 'Per tanggal'), ('5', 'Per musim tanam')]
    pilihan = tampil_menu('LIHAT JADWAL', opsi)
    print()
    if pilihan == '1':
        tampil_jadwal()
    elif pilihan == '2':
        tampil_saluran()
        tampil_jadwal('WHERE s.id_saluran = %s', (input_int('\nID saluran', minimal=1),))
    elif pilihan == '3':
        tampil_jadwal('WHERE pt.id_petani = %s', (input_int('ID petani', minimal=1),))
    elif pilihan == '4':
        tampil_jadwal('WHERE j.tanggal_mulai::date = %s', (input_tanggal('Tanggal'),))
    elif pilihan == '5':
        tampil_musim()
        tampil_jadwal('WHERE m.id_musim = %s', (input_int('\nID musim', minimal=1),))
    elif pilihan != '0':
        print('Pilihan tidak valid.')


def ubah_jadwal():
    bersihkan()
    judul('UBAH JADWAL')
    tampil_jadwal("WHERE j.status = 'terjadwal'")
    id_jadwal = input_int('\nID jadwal yang diubah (0 = batal)', minimal=0)
    if id_jadwal == 0:
        return
    _, baris = ambil(
        'SELECT j.tanggal_mulai, j.durasi_jam, p.id_saluran FROM jadwal_giliran j '
        "JOIN petak_sawah p ON p.id_petak = j.id_petak WHERE j.id_jadwal = %s AND j.status = 'terjadwal'",
        (id_jadwal,))
    if not baris:
        print('Jadwal tidak ditemukan atau statusnya bukan terjadwal.')
        return
    mulai_lama, durasi_lama, id_saluran = baris[0]

    mulai = input_waktu('Tanggal jam mulai baru (Enter = tetap)', wajib=False) or mulai_lama
    durasi = input_int('Durasi baru dalam jam (Enter = tetap)', minimal=1, wajib=False) or durasi_lama
    selesai = mulai + timedelta(hours=durasi)

    _, bentrok = cek_bentrok(id_saluran, mulai, selesai, abaikan_id=id_jadwal)
    if bentrok:
        print('\nPerubahan ditolak, bentrok dengan jadwal berikut:')
        tampil_tabel(['ID jadwal', 'Petak', 'Mulai', 'Selesai'], bentrok)
        return
    if konfirmasi('Simpan perubahan'):
        jalankan('UPDATE jadwal_giliran SET tanggal_mulai = %s, durasi_jam = %s WHERE id_jadwal = %s',
                 (mulai, durasi, id_jadwal))
        print('Jadwal berhasil diperbarui.')


def batalkan_jadwal():
    bersihkan()
    judul('BATALKAN JADWAL')
    tampil_jadwal("WHERE j.status = 'terjadwal'")
    id_jadwal = input_int('\nID jadwal yang dibatalkan (0 = batal)', minimal=0)
    if id_jadwal == 0:
        return
    if konfirmasi('Apakah Anda yakin ingin membatalkan jadwal ini'):
        jumlah = jalankan("UPDATE jadwal_giliran SET status = 'batal' "
                          "WHERE id_jadwal = %s AND status = 'terjadwal'", (id_jadwal,))
        print('Jadwal dibatalkan.' if jumlah else 'Jadwal tidak ditemukan atau sudah selesai/batal.')


def jadwal_hari_ini():
    bersihkan()
    judul('JADWAL GILIRAN HARI INI')
    tampil_jadwal(f"WHERE j.tanggal_mulai < CURRENT_DATE + INTERVAL '1 day' AND {SELESAI} > CURRENT_DATE "
                  "AND j.status <> 'batal'")


def update_status():
    bersihkan()
    judul('UPDATE STATUS JADWAL')
    tampil_jadwal("WHERE j.status = 'terjadwal'")
    id_jadwal = input_int('\nID jadwal (0 = batal)', minimal=0)
    if id_jadwal == 0:
        return
    print('1. Selesai\n2. Batal')
    pilihan = input('Status baru: ').strip()
    status = {'1': 'selesai', '2': 'batal'}.get(pilihan)
    if not status:
        print('Pilihan tidak valid.')
        return
    jumlah = jalankan('UPDATE jadwal_giliran SET status = %s WHERE id_jadwal = %s AND status = %s',
                      (status, id_jadwal, 'terjadwal'))
    print('Status berhasil diperbarui.' if jumlah else 'Jadwal tidak ditemukan atau sudah selesai/batal.')


def jadwal_per_saluran():
    bersihkan()
    judul('JADWAL PER SALURAN')
    tampil_saluran()
    print()
    tampil_jadwal('WHERE s.id_saluran = %s', (input_int('\nID saluran', minimal=1),))


def jadwal_saya(id_petani):
    bersihkan()
    judul('JADWAL GILIRAN AIR SAYA')
    tampil_jadwal('WHERE pt.id_petani = %s', (id_petani,))


def menu_jadwal():
    opsi = [('1', 'Buat jadwal otomatis'), ('2', 'Lihat jadwal'),
            ('3', 'Ubah jadwal'), ('4', 'Batalkan jadwal')]
    while True:
        pilihan = tampil_menu('PENJADWALAN GILIRAN AIR', opsi)
        if pilihan == '1':
            buat_jadwal_otomatis()
        elif pilihan == '2':
            menu_lihat_jadwal()
        elif pilihan == '3':
            ubah_jadwal()
        elif pilihan == '4':
            batalkan_jadwal()
        elif pilihan == '0':
            return
        else:
            print('Pilihan tidak valid.')
        jeda()
