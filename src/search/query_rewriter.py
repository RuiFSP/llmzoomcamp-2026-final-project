import logging
import os

from openai import OpenAI

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a search query rewriter for a Portuguese food and wine knowledge base. "
    "Rewrite the user's question into a standalone, detailed search query optimized "
    "for retrieval. If conversation history is provided, use it to resolve references. "
    "Respond with only the rewritten query, no explanation."
)


def rewrite_query(question: str, history: list[dict] | None = None) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set, returning original question")
        return question

    model = os.getenv("OPENAI_REWRITER_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": question})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=128,
        )
        rewritten = response.choices[0].message.content.strip()
        logger.info("Rewrote query: %r -> %r", question, rewritten)
        return rewritten
    except Exception:
        logger.exception("Query rewriting failed, returning original question")
        return question
