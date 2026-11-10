"""Tes Tahap 1: cek Ollama berjalan, model terpasang, dan ukur waktu jawab.
Jalankan dari folder proyek:  python tests\\tes_ollama.py"""
import sys
import time
from pathlib import Path

# Supaya "import config" bisa jalan walau script dijalankan dari folder tests/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

import ollama


def cek_model_terpasang() -> bool:
    """Pastikan Ollama hidup dan kedua model sudah diunduh."""
    try:
        daftar = [m.model for m in ollama.list().models]
    except Exception as e:
        print(f"GAGAL: Ollama tidak bisa dihubungi ({e}). Pastikan aplikasi Ollama berjalan.")
        return False

    ok = True
    for nama in (config.MODEL_LLM, config.MODEL_EMBEDDING):
        if nama in daftar:
            print(f"OK    : model {nama} terpasang")
        else:
            print(f"GAGAL : model {nama} belum ada. Jalankan: ollama pull {nama}")
            ok = False
    return ok


def tes_jawaban() -> None:
    """Kirim satu pertanyaan (thinking mati, temperature 0) dan cetak waktunya."""
    pertanyaan = "Sebutkan 3 manfaat rapat yang efektif, singkat saja."
    print(f"\nPertanyaan: {pertanyaan}")
    mulai = time.perf_counter()
    respons = ollama.chat(
        model=config.MODEL_LLM,
        messages=[{"role": "user", "content": pertanyaan}],
        think=config.THINK,                          # matikan mode thinking
        options={"temperature": config.TEMPERATURE},
    )
    detik = time.perf_counter() - mulai

    print(f"Jawaban:\n{respons.message.content}\n")
    # Kalau thinking benar-benar mati, kolom thinking harus kosong
    print(f"Thinking kosong : {not respons.message.thinking}")
    print(f"Waktu jawab     : {detik:.1f} detik")
    if respons.eval_count and respons.eval_duration:
        print(f"Kecepatan       : {respons.eval_count / (respons.eval_duration / 1e9):.1f} token/detik")


def tes_embedding() -> None:
    """Pastikan model embedding juga bisa dipakai (dipakai ChromaDB di Tahap 3)."""
    mulai = time.perf_counter()
    hasil = ollama.embed(model=config.MODEL_EMBEDDING, input="Acara diadakan 13 Desember")
    print(f"Embedding OK, panjang vektor {len(hasil.embeddings[0])}, "
          f"waktu {time.perf_counter() - mulai:.1f} detik")


if __name__ == "__main__":
    if cek_model_terpasang():
        tes_jawaban()
        tes_embedding()
    else:
        sys.exit(1)
