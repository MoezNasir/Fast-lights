from dotenv import load_dotenv
load_dotenv()

import os
import re
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.schemas import QueryRequest, QueryResponse, SourceCitation
from app.products import identify_product_metadata, PRODUCT_CATALOG
from app.retrieval import hybrid_search
from app.llm import generate_rag_answer

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sales Technical Datasheet RAG API")

# Enable CORS for all origins (supports localhost, 127.0.0.1, file://, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and raw PDFs
app.mount("/static", StaticFiles(directory="static"), name="static")
if os.path.exists("data/raw_pdfs"):
    app.mount("/datasheets", StaticFiles(directory="data/raw_pdfs"), name="datasheets")

CONFIDENCE_THRESHOLD = 0.05

SPEC_CATEGORIES = {
    "beam_angle": ["beam angle", "beam", "degrees", "deg", "°"],
    "voltage": ["voltage", "input voltage", "vac", "220v", "240v", "277v", "85v"],
    "dimming": ["dimming", "dimmable", "triac", "dali", "0-10v"],
    "cct": ["cct", "color temperature", "kelvin", "3000k", "4000k", "5700k", "6500k", "warm white"],
    "cri": ["cri", "color rendering", "ra"],
    "ip": ["ip", "ip rating", "ip20", "ip40", "ingress protection", "protection code"],
    "power": ["power", "wattage", "watt", "watts", "lumens", "lumen", "efficacy"],
    "warranty": ["warranty", "guarantee", "year", "years", "lifetime"],
    "lifespan": ["lifespan", "hours", "l70"],
    "dimensions": ["dimension", "dimensions", "cutout", "size", "height", "diameter", "depth", "mm"],
    "materials": ["housing", "material", "trim", "finish", "optic", "aluminium", "powder coated"],
    "applications": ["application", "applications", "suitable", "recommended", "install", "luxury", "retail", "residential"]
}

def detect_spec_type(query: str) -> str:
    q = query.lower()
    for spec_name, kws in SPEC_CATEGORIES.items():
        if any(re.search(rf"\b{re.escape(kw)}\b", q) for kw in kws):
            return spec_name.upper()
    return "GENERAL_SPECIFICATION"

@app.api_route("/", methods=["GET", "HEAD"])
def serve_index():
    response = FileResponse("static/index.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/catalog")
def get_catalog():
    return PRODUCT_CATALOG

@app.get("/system-stats")
def get_stats():
    chunks_count = 65
    try:
        import json
        if os.path.exists("data/processed/chunks.json"):
            with open("data/processed/chunks.json", "r") as f:
                chunks_count = len(json.load(f))
    except Exception:
        pass
    return {
        "status": "online",
        "datasheets_count": len(PRODUCT_CATALOG),
        "chunks_indexed": chunks_count,
        "dense_index": "FAISS FlatIP (384-dim)",
        "lexical_index": "BM25Okapi",
        "grounding": "Strict Datasheet Context Verification",
        "llm_engine": "Groq Cloud (Fast Inference)"
    }

@app.post("/query", response_model=QueryResponse)
def query_spec(payload: QueryRequest):
    query_text = payload.question.strip()
    if not query_text:
        return QueryResponse(
            status="NOT_FOUND",
            message="Please enter a valid technical question.",
            confidence=0.0
        )

    # 1. Intent & Product Metadata Detection
    intent_meta = identify_product_metadata(filename="", text_content=query_text)
    product_key = intent_meta.get("product_key")
    category = intent_meta.get("category") if intent_meta.get("category") != "lighting" else None
    spec_type = detect_spec_type(query_text)

    # 2. Hybrid Retrieval (FAISS Semantic + BM25 Lexical + Soft Product Boost)
    results = hybrid_search(
        query=query_text,
        category_filter=category,
        product_key_filter=product_key,
        top_k=6
    )

    if not results or results[0]["score"] < CONFIDENCE_THRESHOLD:
        return QueryResponse(
            status="NOT_FOUND",
            message="The requested specification was not found in the approved product datasheets.",
            confidence=0.0
        )

    best_match = results[0]
    top_chunks = [r["chunk"] for r in results[:4]]

    # 3. LLM Natural Response Generation
    natural_ans = generate_rag_answer(
        query=query_text,
        retrieved_chunks=top_chunks
    )

    detected_product = (
        intent_meta.get("product_family") 
        or best_match.get("product_family") 
        or "Product Catalog"
    )

    return QueryResponse(
        status="FOUND",
        natural_response=natural_ans,
        answer=natural_ans,
        product=detected_product,
        specification=spec_type,
        source=SourceCitation(
            document=best_match["document"],
            page=best_match["page"]
        ),
        evidence=best_match["evidence"],
        confidence=round(min(max(best_match["score"], 0.1), 1.0), 2)
    )