"""
Myntra Discovery Engine - Production Web & API Server
Serves the interactive research dashboard and provides REST API endpoints for
dataset metrics, health checks, and grounded BM25 RAG querying.
Designed for zero-downtime deployment on Railway.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Ensure project root is in path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

try:
    from src.rag_engine import DiscoveryRAG
except ImportError:
    DiscoveryRAG = None

# Initialize FastAPI App
app = FastAPI(
    title="Myntra Discovery Engine API",
    description="Empirical research instrumentation and RAG engine analyzing wishlist conversion blockers",
    version="1.0.0",
)

# Enable CORS for external API consumers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load RAG Engine instance
rag_engine: Optional[Any] = None

@app.on_event("startup")
def startup_event():
    global rag_engine
    classified_file = BASE_DIR / "data" / "stages" / "stage_03_classified.jsonl"
    if classified_file.exists() and DiscoveryRAG:
        try:
            rag_engine = DiscoveryRAG(str(classified_file))
            print(f"[Startup] Loaded DiscoveryRAG with {len(rag_engine.records)} classified records.")
        except Exception as e:
            print(f"[Startup Warning] Failed to initialize DiscoveryRAG: {e}")
            rag_engine = None
    else:
        print("[Startup] DiscoveryRAG initialized without stage_03 data.")

# Request models
class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 6
    source_filter: Optional[str] = None

# ----------------- API Endpoints ----------------- #

@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    """Railway healthcheck endpoint."""
    records_count = len(rag_engine.records) if rag_engine and hasattr(rag_engine, "records") else 0
    return {
        "status": "healthy",
        "service": "myntra-discovery-engine",
        "version": "1.0.0",
        "records_loaded": records_count,
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production" if os.getenv("RAILWAY_STATIC_URL") else "development"),
    }

@app.get("/api/metrics", tags=["Analytics"])
def get_metrics():
    """Returns summarized multi-corpus counts, funnel metrics, and opportunity ranking."""
    output_dir = BASE_DIR / "data" / "output"
    
    funnel_path = output_dir / "funnel.json"
    counts_path = output_dir / "counts.json"
    opportunities_path = output_dir / "opportunities.json"
    
    data = {}
    if funnel_path.exists():
        with open(funnel_path, "r", encoding="utf-8") as f:
            data["funnel"] = json.load(f)
    if counts_path.exists():
        with open(counts_path, "r", encoding="utf-8") as f:
            data["counts"] = json.load(f)
    if opportunities_path.exists():
        with open(opportunities_path, "r", encoding="utf-8") as f:
            data["opportunities"] = json.load(f)
            
    return JSONResponse(content=data)

@app.get("/api/rag/presets", tags=["RAG"])
def get_rag_presets():
    """Returns the 10 executive PM grounded Q&A syntheses."""
    if rag_engine and hasattr(rag_engine, "get_preset_qa"):
        return rag_engine.get_preset_qa()
    
    qa_path = BASE_DIR / "data" / "output" / "rag_qa.json"
    if qa_path.exists():
        with open(qa_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@app.post("/api/rag/query", tags=["RAG"])
def query_rag(payload: RAGQueryRequest):
    """Executes BM25 grounded retrieval across the multi-corpus dataset."""
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG Engine records not available.")
    
    retrieved = rag_engine.retrieve(
        query=payload.query,
        top_k=payload.top_k,
        source_filter=payload.source_filter
    )
    
    return {
        "query": payload.query,
        "retrieved_count": len(retrieved),
        "source_filter": payload.source_filter,
        "records": retrieved
    }

@app.get("/api/rag/search", tags=["RAG"])
def search_rag(
    q: str = Query(..., description="Search query string"),
    top_k: int = Query(6, ge=1, le=20),
    source: Optional[str] = Query(None, description="Optional filter: 'interview', 'survey', 'reddit', 'play_store'")
):
    """Quick GET retrieval endpoint."""
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG Engine records not available.")
    
    retrieved = rag_engine.retrieve(
        query=q,
        top_k=top_k,
        source_filter=source
    )
    return {
        "query": q,
        "retrieved_count": len(retrieved),
        "records": retrieved
    }

# ----------------- Serve Dashboard Frontend ----------------- #

dashboard_dir = BASE_DIR / "dashboard"
if dashboard_dir.exists():
    app.mount("/", StaticFiles(directory=str(dashboard_dir), html=True), name="dashboard")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Myntra Discovery Engine on port {port}...")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
