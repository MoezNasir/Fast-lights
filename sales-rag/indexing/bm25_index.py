import pickle
import re
from pathlib import Path
from rank_bm25 import BM25Okapi

INDEX_DIR = Path("data/faiss")

STOPWORDS = {
    "what", "is", "the", "of", "for", "in", "on", "a", "an", "and", "to", "with", 
    "can", "you", "tell", "me", "do", "does", "have", "has", "are", "which", "give", 
    "about", "how", "much", "many", "all"
}

def tokenize(text: str) -> list[str]:
    """Tokenize text into cleaned terms without high-frequency conversational stopwords."""
    words = re.findall(r"\w+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]

def build_and_save_bm25(chunks: list[dict]):
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    tokenized_corpus = [tokenize(c["text"]) for c in chunks]
    bm25 = BM25Okapi(tokenized_corpus)

    with open(INDEX_DIR / "bm25.pkl", "wb") as f:
        pickle.dump({"bm25": bm25, "chunks": chunks}, f)

    print(f"BM25 lexical index built successfully with {len(chunks)} chunks.")