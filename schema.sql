-- SIGAIR: skema basis data PostgreSQL
-- Jalankan di pgAdmin (Query Tool) pada database proyekmu.
-- Urutan pembuatan tabel sudah memperhatikan foreign key.

CREATE TABLE IF NOT EXISTS petani (
    id_petani SERIAL PRIMARY KEY,
    nama      VARCHAR(100) NOT NULL,
    alamat    VARCHAR(200),
    no_hp     VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS saluran (
    id_saluran   SERIAL PRIMARY KEY,
    nama_saluran VARCHAR(50) NOT NULL,
    debit_air    DECIMAL(8,2) NOT NULL,
    panjang      DECIMAL(8,2)
);

CREATE TABLE IF NOT EXISTS petak_sawah (
    id_petak      SERIAL PRIMARY KEY,
    id_petani     INT NOT NULL,
    id_saluran    INT NOT NULL,
    luas_ha       DECIMAL(6,2) NOT NULL CHECK (luas_ha > 0),
    jenis_tanaman VARCHAR(50),
    FOREIGN KEY (id_petani)  REFERENCES petani(id_petani),
    FOREIGN KEY (id_saluran) REFERENCES saluran(id_saluran)
);

CREATE TABLE IF NOT EXISTS musim_tanam (
    id_musim    SERIAL PRIMARY KEY,
    nama_musim  VARCHAR(50) NOT NULL,
    tgl_mulai   DATE NOT NULL,
    tgl_selesai DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS jadwal_giliran (
    id_jadwal     SERIAL PRIMARY KEY,
    id_petak      INT NOT NULL,
    id_musim      INT NOT NULL,
    tanggal_mulai TIMESTAMP NOT NULL,
    durasi_jam    INT NOT NULL CHECK (durasi_jam > 0),
    status        VARCHAR(20) NOT NULL DEFAULT 'terjadwal'
                  CHECK (status IN ('terjadwal','selesai','batal')),
    FOREIGN KEY (id_petak)  REFERENCES petak_sawah(id_petak),
    FOREIGN KEY (id_musim)  REFERENCES musim_tanam(id_musim)
);

CREATE TABLE IF NOT EXISTS iuran_air (
    id_iuran     SERIAL PRIMARY KEY,
    id_petani    INT NOT NULL,
    periode      VARCHAR(20) NOT NULL,
    jumlah       DECIMAL(12,2) NOT NULL,
    status_bayar VARCHAR(10) NOT NULL DEFAULT 'belum'
                 CHECK (status_bayar IN ('belum','lunas')),
    FOREIGN KEY (id_petani) REFERENCES petani(id_petani)
);

CREATE TABLE IF NOT EXISTS pengguna (
    id_pengguna SERIAL PRIMARY KEY,
    id_petani   INT NULL,
    username    VARCHAR(50) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    role        VARCHAR(20) NOT NULL CHECK (role IN ('admin','petugas','petani')),
    FOREIGN KEY (id_petani) REFERENCES petani(id_petani)
);

-- Akun awal (password disimpan dalam bentuk hash SHA-256)
-- admin / admin123   dan   petugas / petugas123
INSERT INTO pengguna (username, password, role) VALUES
 ('admin',   '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin'),
 ('petugas', '2dad904f71aa0dcf6ea1addaa084a5865ffe448e4d3f900668e1cc7e7b6153d7', 'petugas')
ON CONFLICT (username) DO NOTHING;
