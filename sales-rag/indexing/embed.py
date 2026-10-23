from sentence_transformers import SentenceTransformer

_MODEL = None

def get_embedding_model():
    global _MODEL
    if _MODEL is None:
        # Fast local embedding model
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL

def embed_texts(texts: list[str]):
    model = get_embedding_model()
    return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
