# Panduan Prompt Claude Code: JejakKeputusan V1

Panduan ini berisi prompt siap tempel untuk Claude Code, dari persiapan sampai aplikasi selesai.
Setiap tahap punya pola yang sama:

1. **Prompt Rencana**: Claude menyusun rencana, belum menulis kode.
2. **Prompt Kerjakan**: Claude menulis kode sesuai rencana.
3. **Prompt Uji dan Jelaskan**: Claude menjalankan uji dan menjelaskan hasilnya.
4. **Cek manual + commit**: kamu memastikan hasilnya benar, lalu `git commit`.

Aturan main:
- **Satu tahap, satu sesi.** Setelah tahap selesai dan di-commit, ketik `/clear` di Claude Code
  sebelum mulai tahap berikutnya. `CLAUDE.md` membuat Claude tetap ingat konteks proyek.
- Baca dulu setiap perubahan yang diusulkan Claude sebelum menyetujuinya.
- Kalau ada error, pakai prompt di bagian **"Kalau ada masalah"** di akhir panduan.

---

## Langkah 0: Setup tambahan (manual, di terminal)

Jalankan di folder proyek `jejak-keputusan`, lewat terminal Antigravity atau PowerShell.

### 0.1 Virtual environment Python

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Kalau muncul error *"running scripts is disabled on this system"*, jalankan sekali:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

lalu ulangi `.venv\Scripts\activate`. Tanda berhasil: muncul `(.venv)` di awal baris terminal.

### 0.2 Git

```powershell
git init
```

### 0.3 Tes kecepatan model dan pilih model

```powershell
ollama run qwen3:4b --verbose
```

Ketik pertanyaan pendek, misalnya `Sebutkan 3 manfaat rapat yang efektif.`
Catat angka **eval rate** di akhir jawaban. Ketik `/bye` untuk keluar, lalu ulangi dengan `qwen3:8b`.

| Hasil | Pilihan |
|---|---|
| `qwen3:8b` sekitar 5 token/detik atau lebih | Pakai `qwen3:8b` |
| `qwen3:8b` jauh di bawah 5 token/detik | Pakai `qwen3:4b` |

Setelah memilih, buka `CLAUDE.md` dan ubah baris model menjadi satu model saja,
misalnya `Ollama, model qwen3:4b`.

### 0.4 Pastikan `CLAUDE.md` ada di folder proyek, lalu jalankan Claude Code

```powershell
claude
```

---

## Tahap 1: Persiapan

### Prompt Rencana

```text
Baca CLAUDE.md dengan teliti. Kita mulai Tahap 1 (Persiapan) saja.
Susun rencana file yang akan dibuat untuk tahap ini, berisi:
1. requirements.txt
2. .gitignore (abaikan .venv, data/db, __pycache__)
3. config.py berisi nama model LLM, nama model embedding, JUMLAH_KANDIDAT = 3,
   MAX_STEPS = 20, dan lokasi folder data
4. tiga catatan rapat fiktif di data/catatan/ sesuai "Data uji" di CLAUDE.md
   (rapat1.txt, rapat2.txt, rapat3.txt), ditulis seperti notulen asli: ada judul,
   tanggal, peserta, beberapa agenda, dan di antaranya terselip usulan serta laporan progres
   yang BUKAN keputusan
5. tests/tes_ollama.py untuk mengecek Ollama berjalan, mengirim satu pertanyaan ke model
   dengan mode thinking dimatikan, dan mencetak lama waktu jawabnya

Jelaskan rencananya dalam Bahasa Indonesia. Jangan menulis kode dulu.
```

### Prompt Kerjakan

```text
Rencananya sudah oke. Silakan buat file-file Tahap 1 sesuai rencana.
Pastikan cara mematikan mode thinking qwen3 sesuai dokumentasi Ollama yang berlaku.
Setelah selesai, jelaskan singkat isi setiap file.
```

### Prompt Uji dan Jelaskan

```text
Install library dari requirements.txt di virtual environment, lalu jalankan
tests/tes_ollama.py. Tunjukkan hasilnya dan berapa detik waktu jawabnya.
Kalau ada error, jelaskan penyebabnya dengan bahasa sederhana lalu perbaiki.
```

### Cek manual

- [ ] `python tests\tes_ollama.py` menampilkan jawaban model dan waktunya
- [ ] Ketiga catatan rapat bisa dibuka dan isinya sesuai skenario
- [ ] Folder `data/db/` tidak ikut terdeteksi Git (`git status`)

```powershell
git add .
git commit -m "Tahap 1: persiapan proyek dan data uji"
```

---

## Tahap 2: Ekstraksi keputusan

Ketik `/clear` dulu di Claude Code.

### Prompt Rencana

```text
Baca CLAUDE.md. Tahap 1 sudah selesai. Kita kerjakan Tahap 2 (Ekstraksi) saja.
Susun rencana untuk:
1. tools.py dengan dua tool pertama:
   - baca_catatan: membaca .txt/.md/.docx dan memotong teks per agenda
   - ekstrak_keputusan: memakai LLM dengan structured output (Pydantic + parameter format
     Ollama) untuk mengambil keputusan dari satu agenda. Setiap keputusan berisi isi
     (satu kalimat), topik, penanggung_jawab (boleh kosong), dan kutipan kalimat aslinya.
     Usulan, laporan progres, dan diskusi tanpa kesimpulan tidak boleh ikut.
2. tests/tes_ekstraksi.py yang menjalankan kedua tool pada data/catatan/rapat1.txt dan
   rapat3.txt, lalu mencetak keputusan yang ditemukan dan lama prosesnya.

Tulis juga rancangan prompt untuk ekstraksi keputusan dan jelaskan alasan setiap bagiannya
(role, tugas, aturan, contoh, format keluaran). Jangan menulis kode dulu.
```

### Prompt Kerjakan

```text
Rencananya oke. Silakan buat tools.py (dua tool dulu) dan tests/tes_ekstraksi.py.
Setiap tool harus punya type hint dan docstring yang jelas, dan kalau gagal
mengembalikan pesan error, bukan menghentikan program.
```

### Prompt Uji dan Jelaskan

```text
Jalankan tests/tes_ekstraksi.py. Bandingkan hasilnya dengan "Data uji" di CLAUDE.md:
- Rapat 1 harus menghasilkan 2 keputusan (tanggal acara, konsumsi)
- Rapat 3 harus menghasilkan 3 keputusan (tanggal acara, konsumsi, dekorasi)
- Usulan dan laporan progres tidak boleh ikut
Kalau ada yang meleset, perbaiki prompt ekstraksinya lalu uji lagi.
Setelah sesuai, jelaskan cara kerja ekstrak_keputusan dengan bahasa sederhana.
```

### Cek manual

- [ ] Keputusan Rapat 1 dan Rapat 3 sesuai harapan
- [ ] Kalimat usulan tidak ikut terambil
- [ ] Catat lama proses per catatan (berguna untuk bagian latensi di presentasi)

```powershell
git add .
git commit -m "Tahap 2: tool baca_catatan dan ekstrak_keputusan"
```

---

## Tahap 3: Penyimpanan dan perbandingan

Ketik `/clear` dulu.

### Prompt Rencana

```text
Baca CLAUDE.md. Tahap 1 dan 2 sudah selesai. Kita kerjakan Tahap 3 (Perbandingan) saja.
Susun rencana untuk:
1. db.py:
   - membuat database SQLite dengan tabel keputusan dan peringatan sesuai CLAUDE.md
   - koneksi ChromaDB persisten (metrik cosine) dengan embedding qwen3-embedding:0.6b
   - fungsi ubah_status_keputusan (dipakai tombol di antarmuka, BUKAN tool agen)
   - fungsi reset_database untuk mengosongkan data saat pengujian
2. Tiga tool baru di tools.py:
   - simpan_keputusan: simpan ke SQLite dan ChromaDB dengan id yang sama
   - cari_keputusan_lama: cari JUMLAH_KANDIDAT keputusan paling mirip yang statusnya aktif
   - cek_kontradiksi: LLM dengan structured output, label hanya boleh baru / sama /
     memperbarui / bertentangan, ditambah alasan
3. tests/tes_perbandingan.py yang menguji cek_kontradiksi dengan 4 pasangan:
   - "Acara diadakan 13 Desember" vs "Acara diadakan 20 Desember" -> bertentangan
   - "Konsumsi dari katering A" vs "Konsumsi tetap dari katering A" -> sama
   - "Anggaran dekorasi Rp5 juta" vs "Anggaran dekorasi naik menjadi Rp7 juta,
     menggantikan keputusan Rapat 2" -> memperbarui
   - "Konsumsi dari katering A" vs "Publikasi mulai 1 Desember" -> baru
   Lalu menguji simpan_keputusan dan cari_keputusan_lama: simpan 3 keputusan, cari
   keputusan yang mirip dengan "Seminar digeser ke tanggal 20 Desember", pastikan
   keputusan tanggal acara muncul paling atas.

Jelaskan rancangan prompt untuk cek_kontradiksi, terutama cara membedakan
memperbarui dan bertentangan. Jangan menulis kode dulu.
```

### Prompt Kerjakan

```text
Rencananya oke. Silakan buat db.py, tambahkan tiga tool ke tools.py,
dan buat tests/tes_perbandingan.py.
```

### Prompt Uji dan Jelaskan

```text
Jalankan tests/tes_perbandingan.py. Tampilkan hasilnya dalam tabel:
pasangan, label yang diharapkan, label dari model, alasan, benar atau salah.
Jalankan sebanyak 3 kali untuk melihat apakah labelnya konsisten.
Kalau ada yang salah, perbaiki prompt cek_kontradiksi dan uji lagi.
Setelah itu jelaskan cara kerja pencarian makna di cari_keputusan_lama dengan bahasa sederhana.
```

### Cek manual

- [ ] Keempat pasangan berlabel benar, dan labelnya konsisten di 3 kali percobaan
- [ ] Pencarian "Seminar digeser ke tanggal 20 Desember" menemukan keputusan tanggal acara
- [ ] File database muncul di `data/db/`

```powershell
git add .
git commit -m "Tahap 3: database, simpan, cari, dan cek kontradiksi"
```

---

## Tahap 4: Agen dan antarmuka

Ketik `/clear` dulu. Tahap ini dibagi dua bagian supaya tidak terlalu besar.

### Bagian 4A: Agen (tanpa tampilan dulu)

#### Prompt Rencana

```text
Baca CLAUDE.md. Tahap 1 sampai 3 sudah selesai. Kita kerjakan Tahap 4 bagian A: agen.
Susun rencana untuk:
1. Tool keenam buat_laporan di tools.py: daftar keputusan berstatus aktif per topik.
2. agent.py berisi:
   - system prompt agen (role, tugas, aturan: wajib memakai tools, tidak boleh mengubah
     status keputusan, hanya memakai hasil tool, ringkasan akhir dalam Bahasa Indonesia)
   - agent loop dengan Ollama tool calling: berhenti saat tidak ada tool yang diminta atau
     setelah MAX_STEPS
   - fungsi proses_catatan(path, rapat_id, tanggal) yang mengembalikan ringkasan,
     daftar keputusan, dan daftar peringatan; peringatan dengan label bertentangan atau
     memperbarui disimpan ke tabel peringatan
   - log setiap panggilan tool (nama tool, input singkat, output singkat) supaya alur
     agen bisa ditunjukkan saat presentasi
3. tests/tes_agen.py yang mereset database, lalu memproses rapat1, rapat2, rapat3 berurutan
   dan mencetak log serta hasil akhirnya.

Jelaskan juga: bagian mana yang diputuskan LLM dan bagian mana yang dijalankan kode.
Jangan menulis kode dulu.
```

#### Prompt Kerjakan

```text
Rencananya oke. Silakan buat buat_laporan, agent.py, dan tests/tes_agen.py.
```

#### Prompt Uji dan Jelaskan

```text
Jalankan tests/tes_agen.py. Cek apakah saat Rapat 3 diproses:
- tanggal acara diberi label bertentangan dan muncul sebagai peringatan
- konsumsi diberi label sama
- dekorasi diberi label memperbarui
Tampilkan juga urutan tool yang dipanggil agen dan total waktu prosesnya.
Kalau agen memanggil tool dengan urutan aneh atau berhenti terlalu cepat,
perbaiki system prompt atau deskripsi tool, lalu uji lagi.
```

#### Cek manual

- [ ] Hasil Rapat 3 sesuai harapan
- [ ] Log urutan tool terbaca jelas

```powershell
git add .
git commit -m "Tahap 4A: agen dan tool buat_laporan"
```

### Bagian 4B: Tampilan Gradio

Ketik `/clear` dulu.

#### Prompt Rencana

```text
Baca CLAUDE.md. Agen di agent.py sudah berjalan. Kita kerjakan Tahap 4 bagian B: app.py.
Susun rencana tampilan Gradio satu halaman sesuai bagian "Tampilan" di CLAUDE.md:
1. Panel kiri: unggah catatan, isi rapat_id dan tanggal rapat, tombol "Proses dengan agen",
   riwayat rapat yang sudah diproses
2. Panel tengah: daftar keputusan beserta statusnya, bisa disaring per topik
3. Panel kanan: peringatan yang statusnya menunggu, masing-masing dengan tombol
   "Yang baru berlaku", "Yang lama berlaku", "Bukan kontradiksi"
   yang memanggil ubah_status_keputusan lalu menandai peringatan selesai
4. Tampilkan pesan "sedang diproses" karena agen bisa butuh beberapa menit
5. Bagian laporan keputusan yang berlaku (dari buat_laporan)

Jelaskan apa yang terjadi di database untuk setiap tombol. Jangan menulis kode dulu.
```

#### Prompt Kerjakan

```text
Rencananya oke. Silakan buat app.py. Buat tampilannya sederhana dan rapi.
```

#### Prompt Uji dan Jelaskan

```text
Jelaskan cara menjalankan app.py dan langkah mengujinya di browser
dengan rapat1.txt, rapat2.txt, lalu rapat3.txt.
Cek juga dengan membaca kode: apakah setiap tombol konfirmasi mengubah status di SQLite
dengan benar? Tunjukkan bagian kodenya.
```

#### Cek manual (di browser)

- [ ] `python app.py`, lalu buka `http://localhost:7860`
- [ ] Unggah Rapat 1, 2, 3 berurutan; peringatan tanggal acara muncul setelah Rapat 3
- [ ] Klik "Yang baru berlaku": keputusan 13 Desember berubah menjadi dibatalkan
- [ ] Laporan hanya menampilkan keputusan yang masih berlaku

```powershell
git add .
git commit -m "Tahap 4B: tampilan Gradio"
```

---

## Tahap 5: Uji dan persiapan demo

Ketik `/clear` dulu.

### Prompt Kerjakan

```text
Baca CLAUDE.md. Semua fitur V1 sudah dibuat. Kita kerjakan Tahap 5 (Uji dan demo).
1. Buat tests/uji_skenario.py yang mereset database, memproses Rapat 1-3, lalu menulis
   hasilnya ke hasil_uji.md: keputusan per rapat, label setiap perbandingan dibanding
   label yang diharapkan, peringatan, dan waktu proses per rapat.
2. Jalankan uji_skenario.py sebanyak 3 kali dan rangkum: berapa kali hasilnya sesuai,
   rata-rata waktu proses, dan masalah yang muncul.
3. Buat salinan database hasil pengujian yang berhasil di data/db_demo/ sebagai cadangan
   demo, beserta cara memakainya, supaya saat presentasi tidak perlu menunggu proses lama.
4. Buat README.md singkat: deskripsi aplikasi, cara install, cara menjalankan, dan
   struktur folder.
```

### Prompt Jelaskan untuk presentasi

```text
Saya akan mempresentasikan aplikasi ini. Buat penjelasan sederhana dalam Bahasa Indonesia untuk:
1. Alur kerja agen dari catatan diunggah sampai peringatan muncul, dengan menyebut file dan
   fungsi yang terlibat
2. Bagian yang diputuskan LLM dan bagian yang dijalankan kode biasa
3. Lima pertanyaan yang mungkin ditanyakan dosen beserta jawabannya
Simpan ke CATATAN_PRESENTASI.md.
```

### Cek manual

- [ ] `hasil_uji.md` berisi hasil 3 kali pengujian
- [ ] Database cadangan demo bisa dipakai
- [ ] README bisa diikuti dari awal

```powershell
git add .
git commit -m "Tahap 5: pengujian dan persiapan demo"
```

---

## Tambahan opsional: unduh laporan

```text
Baca CLAUDE.md. Tambahkan tombol "Unduh laporan" di app.py yang mengekspor hasil
buat_laporan ke file .docx: judul, tanggal pembuatan, keputusan yang berlaku per topik,
dan riwayat perubahan (misalnya "menggantikan keputusan Rapat 2").
Susun rencananya dulu, lalu kerjakan setelah saya setujui.
```

---

## Kalau ada masalah

**Error saat menjalankan kode:**

```text
Saat menjalankan [nama file], muncul error berikut:
[tempel seluruh pesan error]
Jelaskan penyebabnya dengan bahasa sederhana, lalu perbaiki.
```

**Hasil tidak sesuai harapan:**

```text
Hasil [nama uji] tidak sesuai. Yang diharapkan: [...]. Yang muncul: [...].
Cari penyebabnya (prompt, deskripsi tool, atau kode), jelaskan, lalu perbaiki.
```

**Proses terlalu lambat:**

```text
Proses satu catatan butuh [X] menit. Cari bagian yang paling lama dengan menambahkan
pengukuran waktu per panggilan LLM, lalu usulkan cara mempercepat tanpa mengganti
model ke layanan online.
```

**Bingung dengan kode:**

```text
Jelaskan file [nama file] bagian per bagian dengan bahasa sederhana,
seolah menjelaskan ke orang yang baru belajar Python.
```
