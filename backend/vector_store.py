import os
import pickle
import numpy as np
from fastembed import TextEmbedding
from backend.config import CHROMA_DB_PATH, EMBEDDING_MODEL_NAME, MODEL_CACHE_DIR

os.makedirs(CHROMA_DB_PATH, exist_ok=True)
STORE_FILE = os.path.join(CHROMA_DB_PATH, "store.pkl")

_embedding_model = None
_chunks = []
_embeddings = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = TextEmbedding(EMBEDDING_MODEL_NAME, cache_dir=MODEL_CACHE_DIR)
    return _embedding_model


def _encode(texts: list) -> np.ndarray:
    """Turn a list of texts into a (n, 384) array of embeddings."""
    model = _get_embedding_model()
    return np.array(list(model.embed(texts, batch_size=32)), dtype=float)


def _cosine(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Cosine similarity of one vector against every row of a matrix."""
    q = query_vec / (np.linalg.norm(query_vec) + 1e-10)
    m = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10)
    return m @ q


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
    new_embeddings = _encode(chunks)

    _chunks.extend(chunks)
    _embeddings = np.vstack([_embeddings, new_embeddings]) if _embeddings.shape[0] > 0 else new_embeddings

    _save_store()


def semantic_search(query: str, top_k: int) -> list:
    if not _chunks:
        return []

    query_embedding = _encode([query])[0]
    scores = _cosine(query_embedding, _embeddings)

    top_indices = np.argsort(scores)[::-1][:top_k]
    return [_chunks[i] for i in top_indices]


def get_all_chunks() -> list:
    return _chunks


def clear_store():
    global _chunks, _embeddings
    _chunks = []
    _embeddings = np.empty((0, 384))
    _save_store()
