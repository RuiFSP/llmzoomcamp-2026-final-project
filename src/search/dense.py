import logging
import os

from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


class DenseRetriever:
    def __init__(self, host: str | None = None, port: int | None = None, collection: str = "portuguese_food_wine"):
        self.host = host or os.getenv("QDRANT_HOST", "localhost")
        self.port = port or int(os.getenv("QDRANT_PORT", "6333"))
        self.collection = collection
        self.client = QdrantClient(host=self.host, port=self.port)
        logger.info("DenseRetriever connected to %s:%s", self.host, self.port)

    def search(self, query_vector: list[float], k: int = 20) -> list[dict]:
        try:
            result = self.client.query_points(
                collection_name=self.collection,
                query=query_vector,
                limit=k,
            )
            points = result.points
        except Exception:
            logger.exception("Qdrant search failed")
            return []

        results = []
        for point in points:
            payload = point.payload or {}
            metadata = {
                "source": payload.get("source", ""),
                "title": payload.get("title", ""),
                "language": payload.get("language", ""),
                "url": payload.get("url", ""),
            }
            results.append({
                "id": point.id,
                "text": payload.get("text", ""),
                "metadata": metadata,
                "score": point.score,
            })
        return results
