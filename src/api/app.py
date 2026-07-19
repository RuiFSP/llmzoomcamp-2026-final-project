import logging
import os

from flask import Flask, send_from_directory
from openai import OpenAI
from sentence_transformers import SentenceTransformer

from src.api.db import init_db
from src.api.routes import api_bp
from src.search.bm25 import BM25Retriever
from src.search.dense import DenseRetriever
from src.search.reranker import Reranker

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", static_url_path="")

    app.config["OPENAI_CHAT_MODEL"] = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")
    app.config["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

    dense_retriever = DenseRetriever()
    bm25_retriever = BM25Retriever()
    reranker = Reranker()
    openai_client = OpenAI(api_key=app.config["OPENAI_API_KEY"])
    embedder = SentenceTransformer("intfloat/multilingual-e5-small")

    try:
        points, _ = dense_retriever.client.scroll(
            collection_name=dense_retriever.collection,
            limit=10000,
        )
        if points:
            docs = []
            for point in points:
                payload = point.payload or {}
                docs.append({
                    "id": point.id,
                    "text": payload.get("text", ""),
                    "metadata": {
                        "source": payload.get("source", ""),
                        "title": payload.get("title", ""),
                        "language": payload.get("language", ""),
                        "url": payload.get("url", ""),
                    },
                })
            bm25_retriever.index(docs)
            logger.info("BM25 index rebuilt from %d Qdrant documents", len(docs))
    except Exception:
        logger.warning("Could not rebuild BM25 index from Qdrant, BM25 will be empty")

    try:
        init_db()
        logger.info("Database initialized")
    except Exception:
        logger.exception("Database initialization failed")

    app.extensions["dense_retriever"] = dense_retriever
    app.extensions["bm25_retriever"] = bm25_retriever
    app.extensions["reranker"] = reranker
    app.extensions["openai_client"] = openai_client
    app.extensions["embedder"] = embedder

    app.register_blueprint(api_bp)

    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    logger.info("Application created")
    return app
