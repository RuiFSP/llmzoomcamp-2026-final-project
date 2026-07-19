import logging

from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

_model = None


def _get_model(model_name: str) -> CrossEncoder:
    global _model
    if _model is None:
        _model = CrossEncoder(model_name)
        logger.info("Loaded cross-encoder model: %s", model_name)
    return _model


class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = _get_model(self.model_name)
        return self._model

    def rerank(self, query: str, documents: list[dict], top_k: int = 5) -> list[dict]:
        if not documents:
            return []
        pairs = [(query, doc["text"]) for doc in documents]
        try:
            scores = self.model.predict(pairs)
        except Exception:
            logger.exception("Cross-encoder prediction failed")
            return documents[:top_k]

        indexed = list(enumerate(scores))
        indexed.sort(key=lambda x: x[1], reverse=True)
        results = []
        for rank, (idx, score) in enumerate(indexed[:top_k]):
            doc = documents[idx]
            results.append({
                "id": doc["id"],
                "text": doc["text"],
                "metadata": doc["metadata"],
                "score": float(score),
                "rank": rank + 1,
            })
        return results
