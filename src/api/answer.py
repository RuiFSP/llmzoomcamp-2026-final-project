import logging
import re

from openai import OpenAI

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a Portuguese Food & Wine Guide assistant. "
    "Answer the user's question in Portuguese (European Portuguese) using ONLY the provided context. "
    "Cite sources using [1], [2], etc. "
    "If the context doesn't contain enough information, say "
    "'Não tenho informação suficiente na base de conhecimento para responder a essa pergunta.' "
    "Always answer in Portuguese."
)


def generate_answer(
    question: str,
    documents: list[dict],
    history: list[dict] | None = None,
    model: str = "gpt-4o",
    client: OpenAI | None = None,
) -> tuple[str, list[dict], int, int, int]:
    context_parts = []
    for i, doc in enumerate(documents):
        source = doc["metadata"].get("source", "Desconhecida")
        context_parts.append(f"[{i + 1}] (Fonte: {source}) {doc['text']}")
    context_text = "\n\n".join(context_parts)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history[-10:])

    messages.append({
        "role": "user",
        "content": f"Contexto:\n{context_text}\n\nPergunta: {question}",
    })

    if client is None:
        client = OpenAI()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
        )
        answer_text = response.choices[0].message.content.strip()
        usage = response.usage
        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0
        total_tokens = usage.total_tokens if usage else 0

        citations = []
        seen = set()
        for match in re.finditer(r"\[(\d+)\]", answer_text):
            idx = int(match.group(1))
            if idx in seen:
                continue
            seen.add(idx)
            doc_idx = idx - 1
            if 0 <= doc_idx < len(documents):
                doc = documents[doc_idx]
                citations.append({
                    "id": idx,
                    "source": doc["metadata"].get("source", ""),
                    "title": doc["metadata"].get("title", ""),
                    "text_preview": doc["text"][:100],
                })

        return answer_text, citations, prompt_tokens, completion_tokens, total_tokens
    except Exception:
        logger.exception("OpenAI API call failed in answer generation")
        return (
            "Desculpe, ocorreu um erro ao gerar a resposta. Por favor, tente novamente.",
            [],
            0, 0, 0,
        )
