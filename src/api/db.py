import logging
import os
from contextlib import contextmanager

import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool

logger = logging.getLogger(__name__)

_pool = None


def _get_pool() -> ThreadedConnectionPool:
    global _pool
    if _pool is None:
        _pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            dbname=os.getenv("POSTGRES_DB", "pgfoodwine"),
            user=os.getenv("POSTGRES_USER", "pgfoodwine"),
            password=os.getenv("POSTGRES_PASSWORD", "pgfoodwine"),
        )
        logger.info("PostgreSQL connection pool created")
    return _pool


@contextmanager
def _get_conn():
    pool = _get_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


def init_db() -> None:
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    conversation_id VARCHAR(64) NOT NULL,
                    question TEXT NOT NULL,
                    rewritten_question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    sources JSONB,
                    retrieval_latency_ms FLOAT,
                    llm_latency_ms FLOAT,
                    total_latency_ms FLOAT,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    total_tokens INTEGER,
                    model VARCHAR(64),
                    error VARCHAR(256),
                    feedback INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_conversations_conversation_id ON conversations(conversation_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_conversations_error ON conversations(error)")
        conn.commit()


def log_conversation(
    conversation_id: str,
    question: str,
    rewritten_question: str,
    answer: str,
    sources: list[dict] | None = None,
    retrieval_latency_ms: float = 0.0,
    llm_latency_ms: float = 0.0,
    total_latency_ms: float = 0.0,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int = 0,
    model: str = "",
    error: str | None = None,
) -> None:
    import json
    sources_json = json.dumps(sources) if sources else "[]"
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO conversations
                    (conversation_id, question, rewritten_question, answer, sources,
                     retrieval_latency_ms, llm_latency_ms, total_latency_ms,
                     prompt_tokens, completion_tokens, total_tokens, model, error)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                conversation_id, question, rewritten_question, answer, sources_json,
                retrieval_latency_ms, llm_latency_ms, total_latency_ms,
                prompt_tokens, completion_tokens, total_tokens, model, error,
            ))
        conn.commit()


def update_feedback(conversation_id: str, feedback: int) -> None:
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE conversations SET feedback = %s WHERE conversation_id = %s",
                (feedback, conversation_id),
            )
        conn.commit()


def get_conversation_history(conversation_id: str, limit: int = 5) -> list[dict]:
    with _get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT question, answer FROM conversations
                WHERE conversation_id = %s
                ORDER BY created_at ASC
            """, (conversation_id,))
            rows = cur.fetchall()
    history = []
    for row in rows[-limit:]:
        history.append({"role": "user", "content": row["question"]})
        history.append({"role": "assistant", "content": row["answer"]})
    return history


def get_metrics(start_time=None, end_time=None) -> list[dict]:
    query = "SELECT * FROM conversations WHERE 1=1"
    params = []
    if start_time:
        query += " AND created_at >= %s"
        params.append(start_time)
    if end_time:
        query += " AND created_at <= %s"
        params.append(end_time)
    query += " ORDER BY created_at"
    with _get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
    return [dict(row) for row in rows]
