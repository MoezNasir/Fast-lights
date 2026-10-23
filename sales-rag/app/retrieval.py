import os
import pickle
import numpy as np
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

from indexing.embed import embed_texts
import faiss

INDEX_DIR = Path("data/faiss")

STOPWORDS = {
    "what", "is", "the", "of", "for", "in", "on", "a", "an", "and", "to", "with", 
    "can", "you", "tell", "me", "do", "does", "have", "has", "are", "which", "give", 
    "about", "how", "much", "many", "all"
}

SPEC_TYPE_KEYWORDS = {
    "specifications": ["beam", "angle", "cct", "kelvin", "cri", "sdcm", "lumen", "flux", "efficacy", "voltage", "watt", "wattage", "lifespan", "warranty", "triac", "dali", "dimming"],
    "dimensions": ["dimension", "dimensions", "cutout", "size", "dxh", "height", "diameter", "width", "depth", "mm"],
    "mechanical_compliance": ["housing", "material", "finish", "trim", "optic", "ip", "ik", "ingress", "protection", "rohs", "cb", "ce", "iec", "installation", "recessed"],
    "overview": ["describe", "overview", "what is", "features", "benefits", "application", "applications", "suitable", "luxury", "retail", "residential", "hotel", "office", "museum"]
}

def tokenize(text: str) -> list[str]:
    words = re.findall(r"\w+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]

def load_indexes():
    index_path = INDEX_DIR / "faiss.index"
    chunks_path = INDEX_DIR / "chunks_ref.pkl"
    bm25_path = INDEX_DIR / "bm25.pkl"

    if not index_path.exists() or not chunks_path.exists() or not bm25_path.exists():
        from ingestion.ingest import ingest_all_pdfs
        ingest_all_pdfs()

    index = faiss.read_index(str(index_path))
    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)
    with open(bm25_path, "rb") as f:
        bm25_data = pickle.load(f)
    return index, chunks, bm25_data["bm25"]

INDEX, CHUNKS, BM25 = load_indexes()

def hybrid_search(
    query: str, 
    category_filter: Optional[str] = None, 
    product_key_filter: Optional[str] = None,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Performs hybrid search combining dense semantic search (FAISS)
    and lexical search (BM25) with metadata filtering, query intent routing, and soft boosting.
    """
    q_lower = query.lower()
    tokens = tokenize(query)
    bm25_scores = BM25.get_scores(tokens)
    
    max_bm25 = np.max(bm25_scores) if np.max(bm25_scores) > 0 else 1.0
    norm_bm25 = bm25_scores / max_bm25

    q_emb = embed_texts([query]).astype(np.float32)
    faiss_scores, faiss_indices = INDEX.search(q_emb, len(CHUNKS))
    
    faiss_score_map = {idx: score for idx, score in zip(faiss_indices[0], faiss_scores[0])}

    # Determine query intent affinity for chunk types
    intent_chunk_boost = {}
    for ctype, keywords in SPEC_TYPE_KEYWORDS.items():
        if any(re.search(rf"\b{re.escape(kw)}\b", q_lower) for kw in keywords):
            intent_chunk_boost[ctype] = 0.25

    results = []
    for idx, chunk in enumerate(CHUNKS):
        chunk_prod_key = chunk.get("product_key")
        chunk_cat = chunk.get("category")
        chunk_type = chunk.get("type")
        chunk_text_lower = chunk["text"].lower()

        boost = 0.0
        # Product filter / boost
        if product_key_filter:
            if chunk_prod_key == product_key_filter:
                boost += 0.35
            else:
                boost -= 0.30

        # Category boost
        if category_filter and chunk_cat == category_filter:
            boost += 0.05

        # Chunk type intent boost
        if chunk_type in intent_chunk_boost:
            boost += intent_chunk_boost[chunk_type]

        # Exact keyword occurrence boost in chunk text
        matched_kw_count = sum(1 for t in tokens if t in chunk_text_lower)
        if matched_kw_count > 0:
            boost += min(matched_kw_count * 0.04, 0.20)

        b_score = float(norm_bm25[idx])
        f_score = float(faiss_score_map.get(idx, 0.0))
        
        # Combined weighted score
        combined_score = (0.45 * f_score) + (0.55 * b_score) + boost
        
        results.append({
            "chunk": chunk,
            "score": float(combined_score),
            "dense_score": f_score,
            "bm25_score": b_score,
            "evidence": chunk["text"],
            "document": chunk["document"],
            "page": chunk["page"],
            "product_family": chunk.get("product_family"),
            "category": chunk.get("category"),
            "chunk_type": chunk.get("type")
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]