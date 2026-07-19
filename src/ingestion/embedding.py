import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_MODEL: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        logger.info("Loading embedding model: intfloat/multilingual-e5-small")
        _MODEL = SentenceTransformer("intfloat/multilingual-e5-small")
    return _MODEL


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    prefixed = [f"passage: {t}" for t in texts]
    embeddings = model.encode(prefixed, show_progress_bar=False)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    model = _get_model()
    prefixed = f"query: {query}"
    embedding = model.encode([prefixed], show_progress_bar=False)
    return embedding[0].tolist()
