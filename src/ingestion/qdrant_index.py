import logging
import os

from qdrant_client import QdrantClient
from qdrant_client.http import models

logger = logging.getLogger(__name__)


def _get_client() -> QdrantClient:
    host = os.environ.get("QDRANT_HOST", "localhost")
    port = int(os.environ.get("QDRANT_PORT", "6333"))
    return QdrantClient(host=host, port=port, prefer_grpc=False)


def create_collection(collection_name: str, vector_size: int = 384) -> None:
    client = _get_client()

    try:
        client.delete_collection(collection_name)
        logger.info("Deleted existing collection: %s", collection_name)
    except Exception:
        pass

    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=vector_size,
            distance=models.Distance.COSINE,
        ),
    )
    logger.info("Created collection: %s (size=%d)", collection_name, vector_size)


def upload_documents(docs: list[dict], collection_name: str) -> None:
    client = _get_client()

    points: list[models.PointStruct] = []
    for doc in docs:
        point_id = doc.get("id")
        vector = doc.get("vector")
        payload = doc.get("payload", {})

        points.append(
            models.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload,
            )
        )

    if not points:
        logger.warning("No points to upload")
        return

    batch_size = 256
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        client.upsert(collection_name=collection_name, points=batch)

    logger.info("Uploaded %d points to collection '%s'", len(points), collection_name)
