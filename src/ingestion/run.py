import argparse
import logging
import os
import sys
import uuid

from src.ingestion.chunking import chunk_document
from src.ingestion.embedding import embed_texts
from src.ingestion.infovini import fetch_all_infovini
from src.ingestion.mdpi import fetch_mdpi_recipes
from src.ingestion.qdrant_index import create_collection, upload_documents
from src.ingestion.wikipedia import fetch_all_wikipedia

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

COLLECTION_NAME = "portuguese_food_wine"


def _source_count(documents: list[dict], source: str) -> int:
    return sum(1 for d in documents if d.get("metadata", {}).get("source") == source)


def main() -> None:
    parser = argparse.ArgumentParser(description="Portuguese Food & Wine Ingestion Pipeline")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Recreate the Qdrant collection (delete and recreate)",
    )
    args = parser.parse_args()

    os.environ.setdefault("QDRANT_HOST", "localhost")
    os.environ.setdefault("QDRANT_PORT", "6333")

    logger.info("Starting ingestion pipeline")

    logger.info("Fetching Wikipedia articles...")
    wiki_docs = fetch_all_wikipedia()
    logger.info("  Fetched %d Wikipedia documents", len(wiki_docs))

    logger.info("Fetching Infovini data...")
    infovini_docs = fetch_all_infovini()
    logger.info("  Fetched %d Infovini documents", len(infovini_docs))

    logger.info("Fetching MDPI recipes...")
    mdpi_docs = fetch_mdpi_recipes()
    logger.info("  Fetched %d MDPI recipes", len(mdpi_docs))

    all_docs = wiki_docs + infovini_docs + mdpi_docs

    if not all_docs:
        logger.error("No documents fetched from any source. Aborting.")
        sys.exit(1)

    logger.info("Chunking %d documents...", len(all_docs))
    all_chunks: list[dict] = []
    for doc in all_docs:
        all_chunks.extend(chunk_document(doc))
    logger.info("  Created %d chunks", len(all_chunks))

    logger.info("Generating embeddings for %d chunks...", len(all_chunks))
    texts = [c["text"] for c in all_chunks]
    embeddings = embed_texts(texts)
    logger.info("  Generated %d embeddings", len(embeddings))

    logger.info("Preparing Qdrant points...")
    points: list[dict] = []
    for chunk, vector in zip(all_chunks, embeddings, strict=True):
        point_id = uuid.uuid5(uuid.NAMESPACE_DNS, chunk["id"])
        payload = {
            "id": chunk["id"],
            "text": chunk["text"],
            "source": chunk["metadata"].get("source", ""),
            "title": chunk["metadata"].get("title", ""),
            "language": chunk["metadata"].get("language", ""),
            "url": chunk["metadata"].get("url", ""),
        }
        optional_fields = ["province", "region", "recipe_name"]
        for field in optional_fields:
            val = chunk["metadata"].get(field)
            if val:
                payload[field] = val

        points.append({
            "id": str(point_id),
            "vector": vector,
            "payload": payload,
        })

    logger.info("Connecting to Qdrant...")
    if args.reset:
        create_collection(COLLECTION_NAME, vector_size=384)
    else:
        from src.ingestion.qdrant_index import _get_client
        client = _get_client()
        collections = client.get_collections()
        exists = any(c.name == COLLECTION_NAME for c in collections.collections)
        if not exists:
            logger.info("Collection does not exist, creating...")
            create_collection(COLLECTION_NAME, vector_size=384)

    upload_documents(points, COLLECTION_NAME)

    logger.info("=== Ingestion Summary ===")
    logger.info("  Wikipedia (pt):    %d documents, %d chunks",
                _source_count(wiki_docs, "wikipedia"),
                sum(1 for c in all_chunks if c["metadata"].get("source") == "wikipedia"))
    logger.info("  Infovini:          %d documents, %d chunks",
                len(infovini_docs),
                sum(1 for c in all_chunks if c["metadata"].get("source") == "infovini"))
    logger.info("  MDPI:              %d documents, %d chunks",
                len(mdpi_docs),
                sum(1 for c in all_chunks if c["metadata"].get("source") == "mdpi"))
    logger.info("  Total:             %d documents, %d chunks, %d vectors",
                len(all_docs), len(all_chunks), len(points))
    logger.info("Ingestion pipeline complete")


if __name__ == "__main__":
    main()
