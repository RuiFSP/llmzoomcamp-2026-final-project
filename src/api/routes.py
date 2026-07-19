import logging
import time
import uuid

from flask import Blueprint, current_app, jsonify, request

from src.api.answer import generate_answer
from src.api.db import get_conversation_history, log_conversation, update_feedback
from src.search.hybrid import hybrid_fusion
from src.search.query_rewriter import rewrite_query

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _embed_query(text: str) -> list[float]:
    model = current_app.extensions["embedder"]
    return model.encode(text, normalize_embeddings=True).tolist()


@api_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    if not data or "question" not in data:
        return jsonify({"error": "Campo 'question' é obrigatório"}), 400

    question = data["question"].strip()
    if not question:
        return jsonify({"error": "A pergunta não pode estar vazia"}), 400

    conversation_id = data.get("conversation_id") or str(uuid.uuid4())
    total_start = time.time()

    try:
        history = None
        if data.get("conversation_id"):
            history = get_conversation_history(conversation_id)

        rewritten = rewrite_query(question, history)

        embed_start = time.time()
        query_vector = _embed_query(rewritten)
        embed_end = time.time()
        logger.debug("Embedding took %.2fms", (embed_end - embed_start) * 1000)

        dense_retriever = current_app.extensions["dense_retriever"]
        bm25_retriever = current_app.extensions["bm25_retriever"]
        reranker = current_app.extensions["reranker"]

        retrieval_start = time.time()
        dense_results = dense_retriever.search(query_vector, k=50)
        sparse_results = bm25_retriever.search(rewritten, k=50)
        fused = hybrid_fusion(dense_results, sparse_results, k=50)
        top_docs = reranker.rerank(rewritten, fused, top_k=5)
        retrieval_latency = (time.time() - retrieval_start) * 1000

        if not top_docs:
            answer = "Não tenho informação suficiente na base de conhecimento para responder a essa pergunta."
            citations = []
            llm_latency = 0.0
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0
            model = ""
        else:
            llm_start = time.time()
            openai_client = current_app.extensions["openai_client"]
            chat_model = current_app.config["OPENAI_CHAT_MODEL"]
            answer, citations, prompt_tokens, completion_tokens, total_tokens = generate_answer(
                question,
                top_docs,
                history=history,
                model=chat_model,
                client=openai_client,
            )
            llm_latency = (time.time() - llm_start) * 1000
            model = chat_model

        total_latency = (time.time() - total_start) * 1000
        log_conversation(
            conversation_id=conversation_id,
            question=question,
            rewritten_question=rewritten,
            answer=answer,
            sources=citations,
            retrieval_latency_ms=retrieval_latency,
            llm_latency_ms=llm_latency,
            total_latency_ms=total_latency,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            model=model,
            error=None,
        )

        return jsonify({
            "answer": answer,
            "citations": citations,
            "conversation_id": conversation_id,
            "latency_ms": round(total_latency, 2),
        })

    except Exception as exc:
        error_msg = f"{type(exc).__name__}: {exc}"[:255]
        logger.exception("Chat request failed: %s", error_msg)
        total_latency = (time.time() - total_start) * 1000

        try:
            log_conversation(
                conversation_id=conversation_id,
                question=question,
                rewritten_question="",
                answer="",
                sources=None,
                retrieval_latency_ms=0,
                llm_latency_ms=0,
                total_latency_ms=total_latency,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model="",
                error=error_msg,
            )
        except Exception:
            logger.exception("Failed to log error to database")

        return jsonify({
            "answer": "Ocorreu um erro ao processar a sua pergunta. Por favor tente novamente.",
            "citations": [],
            "conversation_id": conversation_id,
            "error": error_msg,
        }), 500


@api_bp.route("/health", methods=["GET"])
def health():
    services = {"qdrant": False, "postgres": False}

    try:
        dr = current_app.extensions["dense_retriever"]
        dr.client.get_collections()
        services["qdrant"] = True
    except Exception:
        logger.exception("Qdrant health check failed")

    try:
        from src.api.db import _get_conn
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            services["postgres"] = True
    except Exception:
        logger.exception("PostgreSQL health check failed")

    all_ok = all(services.values())
    status_code = 200 if all_ok else 503
    return jsonify({"status": "ok" if all_ok else "degraded", "services": services}), status_code


@api_bp.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json(silent=True)
    if not data or "conversation_id" not in data or "score" not in data:
        return jsonify({"error": "Campos 'conversation_id' e 'score' são obrigatórios"}), 400

    try:
        update_feedback(data["conversation_id"], int(data["score"]))
        return jsonify({"status": "ok"})
    except Exception:
        logger.exception("Failed to update feedback")
        return jsonify({"error": "Erro ao registar feedback"}), 500
