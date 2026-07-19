import logging

logger = logging.getLogger(__name__)


def hybrid_fusion(
    dense_results: list[dict],
    sparse_results: list[dict],
    k: int = 20,
    rrf_k: int = 60,
) -> list[dict]:
    scores: dict[str, dict] = {}

    for rank, doc in enumerate(dense_results):
        doc_id = doc["id"]
        existing = scores.get(doc_id, {
            "id": doc_id,
            "text": doc["text"],
            "metadata": doc["metadata"],
            "dense_score": 0.0,
            "sparse_score": 0.0,
            "rrf_score": 0.0,
        })
        existing["text"] = doc["text"]
        existing["metadata"] = doc["metadata"]
        existing["dense_score"] = doc["score"]
        existing["rrf_score"] += 1.0 / (rrf_k + rank + 1)
        scores[doc_id] = existing

    for rank, doc in enumerate(sparse_results):
        doc_id = doc["id"]
        existing = scores.get(doc_id, {
            "id": doc_id,
            "text": doc["text"],
            "metadata": doc["metadata"],
            "dense_score": 0.0,
            "sparse_score": 0.0,
            "rrf_score": 0.0,
        })
        existing["text"] = doc["text"]
        existing["metadata"] = doc["metadata"]
        existing["sparse_score"] = doc["score"]
        existing["rrf_score"] += 1.0 / (rrf_k + rank + 1)
        scores[doc_id] = existing

    fused = sorted(scores.values(), key=lambda x: x["rrf_score"], reverse=True)
    top = fused[:k]
    for doc in top:
        doc["score"] = doc["rrf_score"]
    logger.info("Hybrid fusion: %d results after RRF", len(top))
    return top
