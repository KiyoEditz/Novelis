# Novelis: Fiction Operating System (FOS)

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Architecture: NSPEC](https://img.shields.io/badge/Architecture-NSPEC--000--007-green.svg)](docs/NSPEC-000.md)
[![Model: Gemini 3.8](https://img.shields.io/badge/Model-Gemini%203.8%20Flash-orange.svg)](https://ai.google.dev/)

**Novelis** adalah sistem operasi dan *compiler* naratif deterministik (**Fiction Operating System / FOS**) yang dirancang untuk menghasilkan karya fiksi dan novel skala panjang (50.000 hingga 100.000+ kata) tanpa mengalami degradasi konsistensi, halusinasi fakta, atau penyimpangan karakter (*character drift*).

Sistem ini memisahkan secara tegas antara perencanaan kreatif (*Thinking*) dan eksekusi deterministik (*Executing*), dilengkapi dengan memori jangka panjang relasional (*Story Bible*) dan pengambilan konteks semantik hibrida.

---

## 🌟 Fitur Utama

* **📖 Relational Story Bible (SQLite Hard Canon):**
  Menyimpan kebenaran faktual cerita yang tak terbantahkan (*Hard Canon*) ke dalam tabel relasional: profil fisik karakter, rahasia/pengetahuan yang diketahui tokoh (*No Metagaming*), lokasi & aturan dunia, directed relational matrix, dan janji cerita/Chekhov's Gun (*Plot Threads*).
* **🔍 Hybrid Retrieval & Reranker (LanceDB + BGE-M3):**
  Pencarian cuplikan adegan masa lalu menggabungkan vektor semantik (*Dense*) dan kata kunci leksikal (*Sparse*) untuk akurasi nama tokoh 100%, disaring melalui *cross-encoder reranker* (`bge-reranker-v2-m3`).
* **🌲 Hierarchical Summarization Tree (Ringkasan Berlapis):**
  Pohon ringkasan 4-tier (Adegan $\to$ Bab $\to$ Arc $\to$ Buku) yang menjaga *global awareness* model tanpa menghabiskan batas context window.
* **🔄 5-Step Scene Generation Pipeline:**
  Siklus eksekusi deterministik per adegan:
  1. *Outline:* Perumusan beat adegan.
  2. *Retrieve:* Pengambilan entitas Bible, ringkasan adegan sebelumnya, dan 3–5 adegan lama yang relevan.
  3. *Draft:* Sintesis prosa sastra menggunakan LLM (konteks 32k–128k).
  4. *Consistency Check:* Validasi kepatuhan Rule Engine & koreksi otomatis (*Self-Healing Loop*).
  5. *Fact Ingestion:* Ekstraksi fakta baru ke Story Bible dan pengindeksan ke LanceDB.
* **⚡ Klien LLM Fleksibel (Default: Google Gemini 3.8):**
  Dukungan native untuk Google **Gemini 3.8** (`gemini-3.8-flash` / `gemini-3.8-pro`) dengan context window raksasa, serta penyedia alternatif yang kompatibel dengan OpenAI (OpenRouter, Groq, Ollama).
* **🖥️ Remote GPU Worker Script (Google Colab / Kaggle):**
  Skrip mandiri berekstensi `.py` ([`notebooks/novelis_colab_worker.py`](notebooks/novelis_colab_worker.py)) untuk menjalankan inferensi berat BGE-M3 dan Reranker di GPU cloud gratis, menjaga laptop lokal tetap ringan.
* **📚 Subsistem Ekspor EPUB:**
  Mengemas seluruh bab, adegan, tipografi novel standar, dan daftar isi menjadi berkas digital `.epub` siap baca di e-reader (Kindle, Google Play Books, Apple Books, Kobo).

---

## 🏛️ Arsitektur Spesifikasi (NSPEC Suite)

Novelis dibangun berdasarkan standar spesifikasi formal normatif (RFC 2119) yang tersimpan di direktori [`docs/`](docs/):

| Dokumen | Judul Spesifikasi | Deskripsi |
| :--- | :--- | :--- |
| **[GLOSSARY.md](docs/GLOSSARY.md)** | *Lexicon & Master Terms* | Single Source of Truth untuk seluruh definisi teknis ekosistem Novelis. |
| **[NSPEC-000](docs/NSPEC-000.md)** | *Core Philosophy & Constitution* | Hukum dasar, prinsip isolasi 4 layer, dan *Entropy Reduction Pipeline*. |
| **[NSPEC-001](docs/NSPEC-001.md)** | *Domain Ontology & Story Model* | Formulasi matematika universe, dual timeline, dan taksonomi entitas. |
| **[NSPEC-002](docs/NSPEC-002.md)** | *Narrative Memory Architecture* | Story Bible SQLite, pencarian hybrid BGE-M3, dan alur adegan 5-langkah. |
| **[NSPEC-003](docs/NSPEC-003.md)** | *Story Blueprint & DSL Spec* | Skema deklaratif blueprint novel dan format *Novelis Story DSL*. |
| **[NSPEC-004](docs/NSPEC-004.md)** | *CSIR & Compiler Toolchain* | Intermediate representation (CSIR), AST, dan aturan validasi semantik. |
| **[NSPEC-005](docs/NSPEC-005.md)** | *Autonomous Runtime VM* | Mesin eksekusi deterministik, DAG scheduler, dan 3-Phase Commit. |
| **[NSPEC-006](docs/NSPEC-006.md)** | *Rule Engine & Self-Healing* | Taksonomi invarian, verifikasi logika, dan loop koreksi otomatis. |
| **[NSPEC-007](docs/NSPEC-007.md)** | *Renderer Layer & Plugins* | Sintesis prosa, negosiasi kapabilitas model, dan streaming telemetri. |
| **[API-SPEC](docs/API-SPEC.md)** | *Dual-Plane Master Protocol* | Arsitektur [Control Plane](docs/api/control-plane.md), [Telemetry Plane](docs/api/telemetry-plane.md), dan [Data Plane](docs/api/data-plane.md). |

---

## 📁 Struktur Direktori

```plaintext
Novelis/
├── docs/                                  # Spesifikasi arsitektur normatif (NSPEC & API)
│   ├── api/                               # Sub-spesifikasi Control, Telemetry & Data Plane
│   ├── GLOSSARY.md                        # Kamus definisi resmi
│   └── NSPEC-000.md s/d NSPEC-007.md      # Spesifikasi arsitektur lengkap
├── notebooks/
│   └── novelis_colab_worker.py            # Skrip worker GPU FastAPI untuk Google Colab / Kaggle
├── src/
│   └── novelis/
│       ├── config.py                      # Konfigurasi sistem & env loader
│       ├── memory/                        # Story Bible SQLite, LanceDB, & Summary Tree
│       ├── llm/                           # Adapter Gemini 3.8 & OpenAI-compatible
│       ├── pipeline/                      # 5-Step Orchestrator, Validator, & Extractor
│       ├── export/                        # Generator berkas buku digital EPUB
│       └── cli.py                         # Antarmuka Command Line Interface
├── tests/                                 # Unit & integration test suite (pytest)
├── .env.example                           # Template variabel lingkungan
├── pyproject.toml                         # Konfigurasi packaging proyek
├── requirements.txt                       # Dependensi paket Python
├── LICENSE                                # Lisensi open-source MIT
└── README.md                              # Dokumentasi proyek
```

---

## 🚀 Panduan Memulai (Quick Start)

### 1. Prasyarat
* **Python 3.10** (Sangat disarankan untuk kompatibilitas binary wheel LanceDB & FastEmbed di Windows).

### 2. Instalasi & Virtual Environment
```powershell
# Buat dan aktifkan virtual environment Python 3.10
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instal dependensi proyek
pip install -r requirements.txt
```

### 3. Konfigurasi Lingkungan (`.env`)
Salin berkas `.env.example` menjadi `.env`:
```powershell
cp .env.example .env
```
Buka file `.env` dan masukkan API Key Gemini Anda:
```ini
# Primary LLM Provider: Google Gemini API (Default)
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-3.8-flash

# Pilihan mode embedding: "local" (FastEmbed ONNX) atau "remote" (Colab GPU)
EMBEDDING_MODE=local
LOCAL_EMBEDDING_MODEL=BAAI/bge-m3
```

---

## 💻 Penggunaan Melalui Terminal (CLI)

Novelis menyediakan antarmuka CLI terpadu:

### 1. Inisialisasi Database Story Bible & LanceDB
```powershell
$env:PYTHONPATH="src"
python -m novelis.cli init-bible
```

### 2. Memasukkan Data Contoh (Karakter Aria & Kael)
```powershell
python -m novelis.cli seed-sample
```

### 3. Memeriksa Isi Story Bible (Hard Canon Inspector)
```powershell
python -m novelis.cli inspect-bible
```

### 4. Menjalankan Pembuatan Adegan (5-Step Lifecycle)
```powershell
python -m novelis.cli run-scene --beat "Aria dan Kael menyusuri lorong berlumut di kuil bawah tanah untuk mencari segel kekaisaran."
```

### 5. Mengekspor Seluruh Novel ke Format EPUB
```powershell
python -m novelis.cli export-epub --output "dist/Solaris_Chronicles.epub" --title "Solaris: Rahasia Sang Elang" --author "Novelis AI"
```
File EPUB yang dihasilkan di `dist/Solaris_Chronicles.epub` siap dibuka langsung di aplikasi e-reader favorit Anda.

---

## ☁️ Menjalankan Worker GPU di Google Colab / Kaggle

Jika Anda ingin menghemat memori laptop lokal dan mempercepat inferensi embedding BGE-M3 & Reranker menggunakan GPU cloud gratis:

1. Buka [Google Colab](https://colab.research.google.com/) dan pastikan runtime menggunakan **T4 GPU** (*Runtime -> Change runtime type -> T4 GPU*).
2. Unggah atau salin skrip [`notebooks/novelis_colab_worker.py`](notebooks/novelis_colab_worker.py) ke sesi Colab.
3. Instal dependensi worker di cell Colab:
   ```bash
   !pip install fastapi uvicorn transformers torch accelerate pyngrok
   ```
4. Jalankan worker:
   ```bash
   !python novelis_colab_worker.py
   ```
5. Salin URL publik yang dihasilkan (misal `https://xxxx.ngrok-free.app`) ke file `.env` laptop Anda:
   ```ini
   EMBEDDING_MODE=remote
   REMOTE_WORKER_URL=https://xxxx.ngrok-free.app
   ```

---

## 🧪 Menjalankan Pengujian (Testing)

Jalankan rangkaian unit & integration tests menggunakan pytest:
```powershell
$env:PYTHONPATH="src"
pytest tests/ -v
```

Semua tes mencakup:
- Integritas DDL SQLite Story Bible & pelacakan *character knowledge*.
- Pencegahan pelanggaran karakter yang telah mati (*deceased actor check*).
- Siklus orkestrasi 5-langkah end-to-end.
- Validasi struktur dan integritas kontainer ZIP/XML pada berkas EPUB.

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah **[MIT License](LICENSE)**. Anda bebas menggunakan, memodifikasi, dan mendistribusikannya untuk keperluan pribadi maupun komersial.
