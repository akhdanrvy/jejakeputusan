# JejakKeputusan

Aplikasi AI agent yang membaca catatan rapat, mencatat setiap keputusan, lalu memberi
peringatan kalau keputusan baru bertentangan dengan keputusan rapat sebelumnya.
Proyek tugas mata kuliah Infrastruktur dan Platform Cerdas (Magister ITB). Ini versi V1.

## Tentang pengembang

- Pengembang masih pemula. Setiap selesai membuat atau mengubah file, jelaskan singkat
  dalam Bahasa Indonesia: apa isinya dan kenapa dibuat begitu.
- Utamakan kode yang sederhana dan mudah dibaca daripada kode yang canggih.
- Kode ini akan dipresentasikan, jadi beri komentar singkat di bagian penting.

## Aturan proyek (wajib)

1. Semua berjalan **lokal**. Tidak boleh memakai API berbayar atau layanan AI online.
2. Semua library harus **open source**. Tanyakan dulu sebelum menambah library baru.
3. Laptop: Windows 11, Intel i5-1235U, RAM 24 GB, **tanpa GPU khusus** (model berjalan di CPU).
   Karena lambat: matikan mode thinking qwen3, pakai `temperature = 0`, dan uji dengan data kecil.
4. **Agen tidak boleh mengubah atau menghapus keputusan lama.** Perubahan status hanya
   terjadi lewat tombol konfirmasi di antarmuka.
5. Kerjakan **satu tahap per sesi** (lihat "Tahapan pengerjaan"). Susun rencana dulu sebelum
   menulis kode, dan jangan mengerjakan tahap berikutnya tanpa diminta.

## Teknologi

| Kebutuhan                 | Teknologi                                                 |
| ------------------------- | --------------------------------------------------------- |
| Bahasa                    | Python 3.10+ dengan virtual environment (`.venv`)         |
| Model AI                  | Ollama, model qwen3:4b.                                   |
| Embedding                 | Ollama, model `qwen3-embedding:0.6b`                      |
| Pencarian keputusan mirip | ChromaDB (mode persisten, metrik cosine)                  |
| Penyimpanan keputusan     | SQLite (satu file)                                        |
| Validasi keluaran LLM     | Pydantic + structured outputs Ollama (parameter `format`) |
| Membaca .docx             | python-docx                                               |
| Tampilan                  | Gradio                                                    |

Nama model dan pengaturan lain disimpan di `config.py`, bukan ditulis langsung di kode.

## Struktur folder

```
jejak-keputusan/
  CLAUDE.md
  requirements.txt
  config.py          # nama model, jumlah kandidat, lokasi file
  db.py              # koneksi SQLite + ChromaDB, fungsi ubah_status_keputusan
  tools.py           # 6 tools agen
  agent.py           # system prompt + agent loop
  app.py             # tampilan Gradio
  data/
    catatan/         # catatan rapat contoh (.txt)
    db/              # file SQLite dan ChromaDB (jangan di-commit)
  tests/             # script uji per tahap
```

## Konsep inti

**Keputusan** = hal yang disepakati dan mengubah apa yang akan dilakukan tim
(contoh: "Acara diadakan 13 Desember").
**Bukan keputusan**: usulan yang belum disepakati, laporan progres, diskusi tanpa kesimpulan.

**4 label hubungan** antara keputusan baru dan keputusan lama:

| Label          | Arti                                                      | Tindakan                                                       |
| -------------- | --------------------------------------------------------- | -------------------------------------------------------------- |
| `baru`         | Tidak terkait keputusan lama                              | Simpan, status aktif                                           |
| `sama`         | Isinya sama dengan keputusan lama                         | Catat sebagai penegasan                                        |
| `memperbarui`  | Keputusan baru **secara eksplisit** mengganti yang lama   | Simpan, minta konfirmasi untuk menandai yang lama "digantikan" |
| `bertentangan` | Tidak bisa berlaku bersamaan, dan tidak disebut mengganti | Simpan, tampilkan peringatan + alasan + kedua kutipan          |

**Status keputusan:** `aktif`, `digantikan`, `dibatalkan`.
Hanya keputusan berstatus `aktif` yang ikut dibandingkan.

## Data (SQLite)

Tabel `keputusan`:
`id`, `rapat_id`, `tanggal_rapat`, `topik`, `isi` (satu kalimat), `penanggung_jawab`,
`kutipan` (kalimat asli dari catatan), `status` (default `aktif`), `digantikan_oleh`.

Tabel `peringatan`:
`id`, `keputusan_baru_id`, `keputusan_lama_id`, `label`, `alasan`,
`status` (`menunggu` / `selesai`).

Setiap keputusan juga disimpan vektornya di ChromaDB dengan `id` yang sama.

## 6 tools agen

Setiap tool adalah fungsi Python biasa dengan type hint dan docstring yang jelas
(docstring dibaca LLM untuk memutuskan kapan tool dipakai). Tool selalu mengembalikan
teks atau JSON yang jelas. Kalau gagal, kembalikan pesan error, jangan menghentikan program.

| Tool                  | Masukan                              | Keluaran                                                                                                  |
| --------------------- | ------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| `baca_catatan`        | path file (.txt/.md/.docx)           | Teks dipotong per agenda                                                                                  |
| `ekstrak_keputusan`   | teks satu agenda                     | Daftar keputusan JSON (isi, topik, penanggung jawab, kutipan). Memakai LLM dengan format JSON tetap       |
| `cari_keputusan_lama` | isi satu keputusan                   | Maksimal `JUMLAH_KANDIDAT` keputusan lama berstatus aktif yang paling mirip (dari ChromaDB)               |
| `cek_kontradiksi`     | keputusan baru + satu keputusan lama | Label (salah satu dari 4) + alasan. Memakai LLM dengan format JSON tetap; label di luar 4 pilihan ditolak |
| `simpan_keputusan`    | keputusan + rapat_id + tanggal       | ID keputusan baru (ke SQLite dan ChromaDB)                                                                |
| `buat_laporan`        | topik (opsional)                     | Daftar keputusan berstatus aktif, dikelompokkan per topik                                                 |

`ubah_status_keputusan` (di `db.py`) **bukan** tool agen. Fungsi ini hanya dipanggil
tombol konfirmasi di Gradio.

## Agen

- Satu agen dengan pola LLM + tools + loop (Ollama tool calling).
- Berhenti saat LLM tidak meminta tool lagi, atau setelah `MAX_STEPS = 20` langkah.
- Alur per catatan: baca → ekstrak keputusan → untuk setiap keputusan: cari keputusan lama,
  cek kontradiksi per pasangan → simpan → ringkasan + daftar peringatan.
- Pengaturan awal di `config.py`: `JUMLAH_KANDIDAT = 3` (selama pengembangan, nanti bisa 5).

## Tampilan (Gradio)

Satu halaman, tiga panel:

1. Kiri: unggah catatan, isi tanggal rapat, tombol "Proses dengan agen", riwayat rapat.
2. Tengah: daftar keputusan dengan status.
3. Kanan: peringatan kontradiksi dengan tombol "Yang baru berlaku",
   "Yang lama berlaku", "Bukan kontradiksi".

## Data uji (fiktif): panitia acara

- **Rapat 1 (3 Nov):** Acara diadakan 13 Desember. Konsumsi dari katering A.
- **Rapat 2 (10 Nov):** Publikasi mulai 1 Desember. Anggaran dekorasi Rp5 juta.
- **Rapat 3 (24 Nov):** Acara diadakan 20 Desember (tanpa menyebut mengganti Rapat 1).
  Konsumsi tetap katering A. Anggaran dekorasi naik menjadi Rp7 juta, menggantikan keputusan Rapat 2.

Hasil yang diharapkan saat Rapat 3 diproses:
tanggal acara = `bertentangan`, konsumsi = `sama`, dekorasi = `memperbarui`.
Tambahkan juga kalimat usulan dan laporan progres di catatan supaya ekstraksi ikut teruji.

## Tahapan pengerjaan

1. **Persiapan:** struktur folder, `requirements.txt`, `config.py`, 3 catatan rapat contoh,
   script untuk mengetes Ollama dan mengukur waktu jawab.
2. **Ekstraksi:** `baca_catatan`, `ekstrak_keputusan`, diuji dengan catatan Rapat 1.
3. **Perbandingan:** `db.py`, `simpan_keputusan`, `cari_keputusan_lama`, `cek_kontradiksi`,
   diuji dengan 4 pasangan contoh (satu per label).
4. **Agen dan antarmuka:** `buat_laporan`, `agent.py`, `app.py`.
5. **Uji dan demo:** jalankan skenario 3 rapat dari awal, catat hasil dan waktu proses.

Setiap tahap selesai bila script ujinya berjalan dan hasilnya sesuai harapan.
Setelah itu pengembang melakukan `git commit`.

## Perintah yang sering dipakai (Windows)

```powershell
.venv\Scripts\activate          # aktifkan virtual environment
pip install -r requirements.txt
python tests\<nama_script>.py   # jalankan uji tahap tertentu
python app.py                   # buka aplikasi (http://localhost:7860)
```

## Di luar cakupan V1

Perekam suara atau transkripsi, banyak tim atau pengguna, login, deployment ke server,
integrasi kalender. Jangan dibuat kecuali diminta.
