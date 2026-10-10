# ==============================================================================
# Novelis Remote GPU Worker (Google Colab / Kaggle)
# File: notebooks/novelis_colab_worker.py
# 
# USAGE GUIDE FOR GOOGLE COLAB / KAGGLE:
# 1. Open Google Colab (Ensure Runtime -> Change runtime type -> T4 GPU is active).
# 2. Open a terminal or create a code cell, then run dependency installation:
#    !pip install fastapi uvicorn transformers torch accelerate pyngrok
# 3. Run this script:
#    !python novelis_colab_worker.py
# 4. Copy the generated public URL (ngrok / Cloudflare tunnel) and paste it into
#    the .env file on your local machine: REMOTE_WORKER_URL=https://xxxx.ngrok-free.app
# ==============================================================================

import os
import sys
from typing import List, Dict, Any, Optional
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# ------------------------------------------------------------------------------
# 1. FastAPI Application Initialization
# ------------------------------------------------------------------------------
app = FastAPI(
    title="Novelis Remote GPU Worker",
    description="GPU-accelerated embedding (BGE-M3) and reranker inference service for Novelis Core",
    version="1.0.0"
)

# ------------------------------------------------------------------------------
# 2. Model Management & GPU Acceleration (CUDA)
# ------------------------------------------------------------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[Novelis Worker] Using compute device: {DEVICE}")
if DEVICE == "cpu":
    print("[WARNING] GPU not detected! Inference will run on CPU and may be slow.")

# Global model references
embedding_model = None
embedding_tokenizer = None
reranker_model = None
reranker_tokenizer = None


def load_models():
    """
    Loads BGE-M3 and BGE-Reranker-v2-M3 directly into GPU VRAM.
    Models are automatically downloaded from Hugging Face Hub on first run.
    """
    global embedding_model, embedding_tokenizer, reranker_model, reranker_tokenizer
    from transformers import AutoModel, AutoTokenizer, AutoModelForSequenceClassification

    print("[Novelis Worker] Loading BAAI/bge-m3 into VRAM...")
    embedding_tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-m3")
    embedding_model = AutoModel.from_pretrained("BAAI/bge-m3").to(DEVICE)
    embedding_model.eval()

    print("[Novelis Worker] Loading BAAI/bge-reranker-v2-m3 into VRAM...")
    reranker_tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-reranker-v2-m3")
    reranker_model = AutoModelForSequenceClassification.from_pretrained("BAAI/bge-reranker-v2-m3").to(DEVICE)
    reranker_model.eval()

    print("[Novelis Worker] All neural models successfully loaded and ready for requests!")


# ------------------------------------------------------------------------------
# 3. Pydantic Request & Response Schemas
# ------------------------------------------------------------------------------
class EmbeddingRequest(BaseModel):
    texts: List[str]
    model: Optional[str] = "BAAI/bge-m3"


class RerankRequest(BaseModel):
    query: str
    candidates: List[str]
    top_k: Optional[int] = 5


# ------------------------------------------------------------------------------
# 4. API Endpoints
# ------------------------------------------------------------------------------
@app.get("/health")
def health_check():
    """Checks worker health status and GPU availability."""
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
    Generates 1024-dimensional dense vectors for candidate scene texts.
    Processes inputs in batches on GPU for optimal throughput.
    """
    if embedding_model is None:
        raise HTTPException(status_code=503, detail="Embedding model is not loaded yet")

    with torch.no_grad():
        inputs = embedding_tokenizer(
            req.texts,
            padding=True,
            truncation=True,
            max_length=8192,
            return_tensors="pt"
        ).to(DEVICE)
        
        outputs = embedding_model(**inputs)
        # Extract [CLS] token representation and perform L2 normalization
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
    Reranks candidate text relevance with respect to a query using a Cross-Encoder.
    Sorts candidates from highest to lowest score.
    """
    if reranker_model is None:
        raise HTTPException(status_code=503, detail="Reranker model is not loaded yet")

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

    # Combine with candidate text and sort by descending score
    ranked = sorted(
        [{"index": i, "score": s, "text": req.candidates[i]} for i, s in enumerate(scores_list)],
        key=lambda x: x["score"],
        reverse=True
    )

    return {
        "ranked_candidates": ranked[:req.top_k]
    }


# ------------------------------------------------------------------------------
# 5. Server Startup & Public Tunnel (ngrok)
# ------------------------------------------------------------------------------
def start_public_tunnel(port: int = 8000):
    """
    Opens a public ngrok tunnel to connect local clients to the Colab worker.
    """
    try:
        from pyngrok import ngrok
        # Set auth token if configured:
        # ngrok.set_auth_token("YOUR_TOKEN")
        tunnel = ngrok.connect(port)
        print("=" * 60)
        print(f"[Novelis Worker] Public Tunnel Active!")
        print(f"Copy this URL to your local .env file:")
        print(f"REMOTE_WORKER_URL={tunnel.public_url}")
        print("=" * 60)
    except Exception as e:
        print(f"[Info] Ngrok did not start automatically: {e}")
        print(f"[Info] On Colab, you may alternatively use 'localtunnel' or 'cloudflared'.")


if __name__ == "__main__":
    load_models()
    start_public_tunnel(8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)
