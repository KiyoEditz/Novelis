# ==============================================================================
# Novelis Remote GPU Worker (Google Colab / Kaggle)
# File: notebooks/novelis_colab_worker.py
# 
# PANDUAN PENGGUNAAN DI GOOGLE COLAB / KAGGLE:
# 1. Buka Google Colab (Pastikan Runtime -> Change runtime type -> T4 GPU aktif).
# 2. Buka terminal atau buat cell code baru, lalu jalankan instalasi dependensi:
#    !pip install fastapi uvicorn transformers torch accelerate pyngrok
# 3. Jalankan skrip ini:
#    !python novelis_colab_worker.py
# 4. Salin URL publik yang dihasilkan (ngrok / cloudflare) dan tempelkan ke file .env
#    di laptop Anda: REMOTE_WORKER_URL=https://xxxx.ngrok-free.app
# ==============================================================================

import os
import sys
from typing import List, Dict, Any, Optional
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# ------------------------------------------------------------------------------
# 1. Inisialisasi Aplikasi FastAPI
# ------------------------------------------------------------------------------
app = FastAPI(
    title="Novelis Remote GPU Worker",
    description="Layanan inferensi embedding (BGE-M3) dan reranker berbasis GPU untuk Novelis Core",
    version="1.0.0"
)

# ------------------------------------------------------------------------------
# 2. Manajemen Model & Akselerasi GPU (CUDA)
# ------------------------------------------------------------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[Novelis Worker] Menggunakan perangkat akselerasi: {DEVICE}")
if DEVICE == "cpu":
    print("[PERINGATAN] GPU tidak terdeteksi! Inferensi akan berjalan lambat di CPU.")

# Variabel global penampung model
embedding_model = None
embedding_tokenizer = None
reranker_model = None
reranker_tokenizer = None


def load_models():
    """
    Memuat model BGE-M3 dan BGE-Reranker-v2-M3 langsung ke VRAM GPU.
    Model diunduh otomatis dari Hugging Face Hub saat skrip dijalankan pertama kali.
    """
    global embedding_model, embedding_tokenizer, reranker_model, reranker_tokenizer
    from transformers import AutoModel, AutoTokenizer, AutoModelForSequenceClassification

    print("[Novelis Worker] Sedang memuat BAAI/bge-m3 ke VRAM...")
    embedding_tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-m3")
    embedding_model = AutoModel.from_pretrained("BAAI/bge-m3").to(DEVICE)
    embedding_model.eval()

    print("[Novelis Worker] Sedang memuat BAAI/bge-reranker-v2-m3 ke VRAM...")
    reranker_tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-reranker-v2-m3")
    reranker_model = AutoModelForSequenceClassification.from_pretrained("BAAI/bge-reranker-v2-m3").to(DEVICE)
    reranker_model.eval()

    print("[Novelis Worker] Seluruh model neural berhasil dimuat siap melayani request!")


# ------------------------------------------------------------------------------
# 3. Skema Data Request & Response (Pydantic)
# ------------------------------------------------------------------------------
class EmbeddingRequest(BaseModel):
    texts: List[str]
    model: Optional[str] = "BAAI/bge-m3"


class RerankRequest(BaseModel):
    query: str
    candidates: List[str]
    top_k: Optional[int] = 5


# ------------------------------------------------------------------------------
# 4. Definisi Endpoint Layanan API
# ------------------------------------------------------------------------------
@app.get("/health")
def health_check():
    """Memeriksa status kesehatan server dan ketersediaan VRAM GPU."""
    gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None (CPU)"
    return {
        "status": "HEALTHY",
        "device": DEVICE,
        "gpu_name": gpu_name,
        "models_loaded": embedding_model is not None
    }


@app.post("/v1/embeddings/hybrid")
def generate_embeddings(req: EmbeddingRequest):
    """
    Menghasilkan dense vector 1024-dim untuk sekumpulan teks adegan.
    Dijalankan secara batch di GPU untuk kecepatan maksimal.
    """
    if embedding_model is None:
        raise HTTPException(status_code=503, detail="Model embedding belum selesai dimuat")

    with torch.no_grad():
        inputs = embedding_tokenizer(
            req.texts,
            padding=True,
            truncation=True,
            max_length=8192,
            return_tensors="pt"
        ).to(DEVICE)
        
        outputs = embedding_model(**inputs)
        # Ambil representasi dense [CLS] token dan normalisasi L2
        dense_vecs = outputs.last_hidden_state[:, 0]
        dense_vecs = torch.nn.functional.normalize(dense_vecs, p=2, dim=1)
        dense_list = dense_vecs.cpu().tolist()

    return {
        "dense_embeddings": dense_list,
        "count": len(req.texts)
    }


@app.post("/v1/rerank")
def rerank_candidates(req: RerankRequest):
    """
    Menilai ulang relevansi kandidat teks terhadap query menggunakan Cross-Encoder.
    Mengurutkan kandidat dari skor paling tinggi ke paling rendah.
    """
    if reranker_model is None:
        raise HTTPException(status_code=503, detail="Model reranker belum selesai dimuat")

    pairs = [[req.query, cand] for cand in req.candidates]
    with torch.no_grad():
        inputs = reranker_tokenizer(
            pairs,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(DEVICE)
        scores = reranker_model(**inputs, return_dict=True).logits.view(-1).float()
        scores_list = scores.cpu().tolist()

    # Gabungkan dengan teks asli dan urutkan
    ranked = sorted(
        [{"index": i, "score": s, "text": req.candidates[i]} for i, s in enumerate(scores_list)],
        key=lambda x: x["score"],
        reverse=True
    )

    return {
        "ranked_candidates": ranked[:req.top_k]
    }


# ------------------------------------------------------------------------------
# 5. Eksekusi Server & Tunnel Publik (ngrok)
# ------------------------------------------------------------------------------
def start_public_tunnel(port: int = 8000):
    """
    Membuka terowongan publik (public tunnel) menggunakan ngrok.
    Memungkinkan laptop lokal terhubung ke sesi Colab tanpa port forwarding manual.
    """
    try:
        from pyngrok import ngrok
        # Jika Anda memiliki auth token ngrok, set di sini:
        # ngrok.set_auth_token("TOKEN_ANDA")
        tunnel = ngrok.connect(port)
        print("=" * 60)
        print(f"[Novelis Worker] Public Tunnel Aktif!")
        print(f"Salin URL ini ke file .env laptop Anda:")
        print(f"REMOTE_WORKER_URL={tunnel.public_url}")
        print("=" * 60)
    except Exception as e:
        print(f"[Info] Ngrok tidak aktif otomatis: {e}")
        print(f"[Info] Jika di Colab, Anda dapat menggunakan 'localtunnel' atau 'cloudflared'.")


if __name__ == "__main__":
    load_models()
    start_public_tunnel(8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)
