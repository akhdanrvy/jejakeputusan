"""Pengaturan JejakKeputusan. Semua nama model dan lokasi file diatur di sini,
bukan ditulis langsung di kode lain."""
from pathlib import Path

# --- Model (semua jalan lokal lewat Ollama) ---
MODEL_LLM = "qwen3:4b"
MODEL_EMBEDDING = "qwen3-embedding:0.6b"
TEMPERATURE = 0          # 0 = jawaban stabil, tidak acak
THINK = False            # mode thinking qwen3 dimatikan (CPU lambat)

# --- Pengaturan agen ---
JUMLAH_KANDIDAT = 3      # berapa keputusan lama yang dibandingkan (nanti bisa 5)
MAX_STEPS = 20           # batas langkah agen supaya tidak berputar selamanya

# --- Lokasi folder/file (dihitung dari lokasi config.py, jadi aman dari folder mana pun) ---
FOLDER_PROYEK = Path(__file__).resolve().parent
FOLDER_DATA = FOLDER_PROYEK / "data"
FOLDER_CATATAN = FOLDER_DATA / "catatan"
FOLDER_DB = FOLDER_DATA / "db"
FILE_SQLITE = FOLDER_DB / "keputusan.sqlite"
FOLDER_CHROMA = FOLDER_DB / "chroma"
