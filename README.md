# Novelis: Fiction Operating System (FOS)

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Architecture: NSPEC](https://img.shields.io/badge/Architecture-NSPEC--000--007-green.svg)](docs/NSPEC-000.md)
[![Model: Gemini 3.8](https://img.shields.io/badge/Model-Gemini%203.8%20Flash-orange.svg)](https://ai.google.dev/)

**Novelis** is a deterministic narrative operating system and story compiler (**Fiction Operating System / FOS**) engineered to generate full-length novels (50,000 to 100,000+ words) without consistency decay, factual hallucinations, or character drift.

The architecture strictly decouples creative planning (*Thinking*) from deterministic execution (*Executing*), backed by a relational long-term memory system (*Story Bible*) and hybrid semantic context retrieval.

---

## 🌟 Key Features

* **📖 Relational Story Bible (SQLite Hard Canon):**
  Persists inviolable factual story canon (*Hard Canon*) into structured relational tables: physical character profiles, epistemic knowledge barriers (*No Metagaming*), locations & world constraints, directed relational matrices, and unresolved narrative promises (*Plot Threads / Chekhov's Guns*).
* **🔍 Hybrid Retrieval & Reranker (LanceDB + BGE-M3):**
  Queries past scene snippets by combining semantic dense vectors and lexical sparse representations for 100% character name recall, reranked through a neural cross-encoder (`bge-reranker-v2-m3`).
* **🌲 Hierarchical Summarization Tree (Multi-Tier Memory):**
  A 4-tier summarization tree (Scene $\to$ Chapter $\to$ Arc $\to$ Book) maintaining global narrative awareness across long works without overflowing LLM context windows.
* **🔄 5-Step Scene Generation Pipeline:**
  A deterministic execution lifecycle for every scene:
  1. *Outline:* Formulates the scene beat and objectives.
  2. *Retrieve:* Queries Story Bible entities, prior scene summaries, and 3–5 relevant historical scenes.
  3. *Draft:* Synthesizes literary prose via LLM (32k–128k context).
  4. *Consistency Check:* Programmatic & LLM-based rule validation with an automated self-healing loop.
  5. *Fact Ingestion:* Ingests new assertions into the Story Bible and indexes embeddings in LanceDB.
* **⚡ Flexible LLM Client (Default: Google Gemini 3.8):**
  First-class native support for Google **Gemini 3.8** (`gemini-3.8-flash` / `gemini-3.8-pro`) with massive context windows, alongside secondary support for any OpenAI-compatible provider (OpenRouter, Groq, Ollama).
* **🖥️ Remote GPU Worker Script (Google Colab / Kaggle):**
  A standalone Python script ([`notebooks/novelis_colab_worker.py`](notebooks/novelis_colab_worker.py)) to offload compute-heavy BGE-M3 embeddings and cross-encoder reranking to free cloud GPUs, keeping your local machine responsive.
* **📚 Standard EPUB Export Subsystem:**
  Packages all chapters, scenes, typographically styled body text, and tables of contents into standard `.epub` digital books ready for e-readers (Kindle, Google Play Books, Apple Books, Kobo).

---

## 🏛️ Specification Suite (NSPEC Architecture)

Novelis is built upon formal normative specifications (RFC 2119) maintained in the [`docs/`](docs/) directory:

| Document | Specification Title | Description |
| :--- | :--- | :--- |
| **[GLOSSARY.md](docs/GLOSSARY.md)** | *Lexicon & Master Terms* | Single Source of Truth for all technical definitions across the Novelis ecosystem. |
| **[NSPEC-000](docs/NSPEC-000.md)** | *Core Philosophy & Constitution* | Foundational laws, 4-layer isolation principles, and the *Entropy Reduction Pipeline*. |
| **[NSPEC-001](docs/NSPEC-001.md)** | *Domain Ontology & Story Model* | Mathematical universe formulation, dual timelines, and entity taxonomies. |
| **[NSPEC-002](docs/NSPEC-002.md)** | *Narrative Memory Architecture* | SQLite Story Bible, BGE-M3 hybrid retrieval, and the 5-step scene generation pipeline. |
| **[NSPEC-003](docs/NSPEC-003.md)** | *Story Blueprint & DSL Spec* | Declarative novel blueprint schemas and the *Novelis Story DSL* syntax. |
| **[NSPEC-004](docs/NSPEC-004.md)** | *CSIR & Compiler Toolchain* | Canonical Story Intermediate Representation (CSIR), AST, and semantic validation rules. |
| **[NSPEC-005](docs/NSPEC-005.md)** | *Autonomous Runtime VM* | Deterministic execution engine, DAG scheduler, and 3-Phase Commit protocol. |
| **[NSPEC-006](docs/NSPEC-006.md)** | *Rule Engine & Self-Healing* | Invariant taxonomy, formal logic verification, and automated correction loops. |
| **[NSPEC-007](docs/NSPEC-007.md)** | *Renderer Layer & Plugins* | Prose synthesis, model capability negotiation, and telemetry streaming. |
| **[API-SPEC](docs/API-SPEC.md)** | *Dual-Plane Master Protocol* | System specifications for the [Control Plane](docs/api/control-plane.md), [Telemetry Plane](docs/api/telemetry-plane.md), and [Data Plane](docs/api/data-plane.md). |

---

## 📁 Repository Structure

```plaintext
Novelis/
├── docs/                                  # Normative architectural specifications (NSPEC & API)
│   ├── api/                               # Control, Telemetry & Data Plane sub-specs
│   ├── GLOSSARY.md                        # Master lexicon and official definitions
│   └── NSPEC-000.md to NSPEC-007.md       # Complete architectural specifications
├── notebooks/
│   └── novelis_colab_worker.py            # FastAPI GPU worker script for Google Colab / Kaggle
├── src/
│   └── novelis/
│       ├── config.py                      # Global configuration & environment loader
│       ├── memory/                        # SQLite Story Bible, LanceDB, & Summary Tree
│       ├── llm/                           # Google Gemini 3.8 & OpenAI-compatible client adapters
│       ├── pipeline/                      # 5-Step Orchestrator, Consistency Validator, & Extractor
│       ├── export/                        # EPUB digital book generator
│       └── cli.py                         # Unified Command-Line Interface
├── tests/                                 # Unit & integration test suite (pytest)
├── .env.example                           # Environment configuration template
├── pyproject.toml                         # Project build and packaging metadata
├── requirements.txt                       # Python dependencies
├── LICENSE                                # MIT Open-Source License
└── README.md                              # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
* **Python 3.10** (Recommended for binary wheel compatibility with LanceDB and FastEmbed on Windows).

### 2. Installation & Virtual Environment
```powershell
# Create and activate a Python 3.10 virtual environment
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install project dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration (`.env`)
Copy `.env.example` to create your local `.env`:
```powershell
cp .env.example .env
```
Open `.env` and configure your Gemini API Key:
```ini
# Primary LLM Provider: Google Gemini API (Default)
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-3.8-flash

# Embedding Mode: "local" (FastEmbed ONNX CPU) or "remote" (Colab GPU)
EMBEDDING_MODE=local
LOCAL_EMBEDDING_MODEL=BAAI/bge-m3
```

---

## 💻 Command-Line Interface (CLI)

Novelis provides a unified CLI to initialize, inspect, execute, and export novel projects:

### 1. Initialize Story Bible Database & LanceDB
```powershell
$env:PYTHONPATH="src"
python -m novelis.cli init-bible
```

### 2. Seed Sample Entities (Aria Valen & Kael)
```powershell
python -m novelis.cli seed-sample
```

### 3. Inspect Story Bible Contents (Hard Canon Inspector)
```powershell
python -m novelis.cli inspect-bible
```

### 4. Run 5-Step Scene Generation Pipeline
```powershell
python -m novelis.cli run-scene --beat "Aria and Kael explore the moss-covered hallway in the sunken temple to locate the imperial seal."
```

### 5. Export Complete Novel to EPUB
```powershell
python -m novelis.cli export-epub --output "dist/Solaris_Chronicles.epub" --title "Solaris: Secret of the Hawk" --author "Novelis AI"
```
The compiled EPUB at `dist/Solaris_Chronicles.epub` is ready to open in any standard e-reader application (Kindle, Apple Books, Kobo, etc.).

---

## ☁️ Running the GPU Worker on Google Colab / Kaggle

To offload BGE-M3 dense embeddings and cross-encoder reranking to free cloud GPUs:

1. Open [Google Colab](https://colab.research.google.com/) and verify that the runtime is set to a **T4 GPU** (*Runtime -> Change runtime type -> T4 GPU*).
2. Upload or copy [`notebooks/novelis_colab_worker.py`](notebooks/novelis_colab_worker.py) into the Colab session.
3. Install the worker dependencies in a Colab code cell:
   ```bash
   !pip install fastapi uvicorn transformers torch accelerate pyngrok
   ```
4. Run the worker script:
   ```bash
   !python novelis_colab_worker.py
   ```
5. Copy the generated public tunnel URL (e.g. `https://xxxx.ngrok-free.app`) to your local `.env` file:
   ```ini
   EMBEDDING_MODE=remote
   REMOTE_WORKER_URL=https://xxxx.ngrok-free.app
   ```

---

## 🧪 Running Tests

Execute the unit and integration test suite using `pytest`:
```powershell
$env:PYTHONPATH="src"
pytest tests/ -v
```

Test coverage includes:
- SQLite Story Bible DDL integrity & epistemic character knowledge tracking.
- Deceased actor detection and prevention in narrative prose.
- Full end-to-end 5-step scene generation pipeline execution.
- Standard EPUB ZIP container, manifest, and XML structure validation.

---

## 📄 License

This project is licensed under the **[MIT License](LICENSE)**. You are free to use, modify, and distribute it for personal and commercial purposes.
