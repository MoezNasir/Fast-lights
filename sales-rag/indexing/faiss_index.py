from indexing.embed import embed_texts  
import faiss
import pickle
import numpy as np
from pathlib import Path

INDEX_DIR = Path("data/faiss")

def build_and_save_faiss(chunks: list[dict]):
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts).astype(np.float32)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_DIR / "faiss.index"))
    with open(INDEX_DIR / "chunks_ref.pkl", "wb") as f:
        pickle.dump(chunks, f)

    print(f"FAISS index built with {index.ntotal} vectors.")