import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from backend.config import CHROMA_DB_PATH, EMBEDDING_MODEL_NAME

os.makedirs(CHROMA_DB_PATH, exist_ok=True)
STORE_FILE = os.path.join(CHROMA_DB_PATH, "store.pkl")

_embedding_model = None
_chunks = []
_embeddings = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def _load_store():
    global _chunks, _embeddings
    if os.path.exists(STORE_FILE):
        with open(STORE_FILE, "rb") as f:
            data = pickle.load(f)
            _chunks = data["chunks"]
            _embeddings = data["embeddings"]
    else:
        _chunks = []
        _embeddings = np.empty((0, 384))


def _save_store():
    with open(STORE_FILE, "wb") as f:
        pickle.dump({"chunks": _chunks, "embeddings": _embeddings}, f)


_load_store()


def add_chunks_to_store(chunks: list, doc_id: str):
    global _chunks, _embeddings

    embedding_model = _get_embedding_model()
    new_embeddings = embedding_model.encode(chunks)

    _chunks.extend(chunks)
    _embeddings = np.vstack([_embeddings, new_embeddings]) if _embeddings.shape[0] > 0 else new_embeddings

    _save_store()


def semantic_search(query: str, top_k: int) -> list:
    if not _chunks:
        return []

    query_embedding = _get_embedding_model().encode([query])
    scores = cosine_similarity(query_embedding, _embeddings)[0]

    top_indices = np.argsort(scores)[::-1][:top_k]
    return [_chunks[i] for i in top_indices]


def get_all_chunks() -> list:
    return _chunks


def clear_store():
    global _chunks, _embeddings
    _chunks = []
    _embeddings = np.empty((0, 384))
    _save_store()