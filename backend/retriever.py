from rank_bm25 import BM25Okapi
from backend.vector_store import semantic_search, get_all_chunks
from backend.config import TOP_K_BM25, TOP_K_SEMANTIC, FINAL_TOP_K


def bm25_search(query: str, top_k: int) -> list:
    chunks = get_all_chunks()
    if not chunks:
        return []

    tokenized_chunks = [chunk.split() for chunk in chunks]
    bm25 = BM25Okapi(tokenized_chunks)

    tokenized_query = query.split()
    top_chunks = bm25.get_top_n(tokenized_query, chunks, n=top_k)

    return top_chunks


def reciprocal_rank_fusion(bm25_ranked: list, semantic_ranked: list, k: int = 60) -> list:
    scores = {}

    for rank, doc in enumerate(bm25_ranked):
        scores[doc] = scores.get(doc, 0) + 1 / (k + rank + 1)

    for rank, doc in enumerate(semantic_ranked):
        scores[doc] = scores.get(doc, 0) + 1 / (k + rank + 1)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked


def hybrid_retrieve(query: str) -> list:
    bm25_results = bm25_search(query, TOP_K_BM25)
    semantic_results = semantic_search(query, TOP_K_SEMANTIC)

    fused_results = reciprocal_rank_fusion(bm25_results, semantic_results)

    return fused_results[:FINAL_TOP_K]