import logging
import re

from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)


class BM25Retriever:
    def __init__(self):
        self.bm25 = None
        self.documents = []

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r'\w+', text.lower())

    def index(self, documents: list[dict]) -> None:
        self.documents = documents
        tokenized_corpus = [self._tokenize(doc["text"]) for doc in documents]
        self.bm25 = BM25Okapi(tokenized_corpus)
        logger.info("Indexed %d documents with BM25", len(documents))

    def search(self, query: str, k: int = 20) -> list[dict]:
        if self.bm25 is None:
            logger.warning("BM25 index not built yet")
            return []
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        indexed = list(enumerate(scores))
        indexed.sort(key=lambda x: x[1], reverse=True)
        top = indexed[:k]
        results = []
        for idx, score in top:
            doc = self.documents[idx]
            results.append({
                "id": doc["id"],
                "text": doc["text"],
                "metadata": doc["metadata"],
                "score": float(score),
            })
        return results
