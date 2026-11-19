-- SIGAIR: data contoh untuk demo (jalankan setelah schema.sql, hanya pada database yang masih kosong)
INSERT INTO petani (nama, alamat, no_hp) VALUES
 ('Pak Slamet', 'Dusun Krajan', '081234567801'),
 ('Bu Sari',    'Dusun Krajan', '081234567802'),
 ('Pak Joko',   'Dusun Wetan',  '081234567803');

INSERT INTO saluran (nama_saluran, debit_air, panjang) VALUES
 ('Saluran A', 25.50, 1200);

INSERT INTO petak_sawah (id_petani, id_saluran, luas_ha, jenis_tanaman) VALUES
 (1, 1, 2.00, 'Padi'),
 (2, 1, 1.00, 'Padi'),
 (3, 1, 1.00, 'Jagung');

INSERT INTO musim_tanam (nama_musim, tgl_mulai, tgl_selesai) VALUES
 ('MT 1 2026/2027', '2026-11-01', '2027-02-28');

-- Akun petani contoh: slamet / slamet123 (terhubung ke petani id 1)
INSERT INTO pengguna (id_petani, username, password, role) VALUES
 (1, 'slamet', '9e4ab9cdc5bbb6ee72378538ea16029f1c8ad12faab55c9c32dbcf4d0290a2f4', 'petani')
ON CONFLICT (username) DO NOTHING;
