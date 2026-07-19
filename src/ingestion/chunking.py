import logging

logger = logging.getLogger(__name__)

_SENTENCE_SEPS = [". ", "! ", "? ", ".\n", "!\n", "?\n"]


def _find_break(text: str, start: int, end: int, min_chunk: int = 200) -> int:
    segment = text[start:end]

    pos = segment.rfind("\n\n")
    if pos >= min_chunk:
        return start + pos + 2

    for sep in _SENTENCE_SEPS:
        pos = segment.rfind(sep)
        if pos >= min_chunk:
            return start + pos + len(sep)

    pos = segment.rfind("\n")
    if pos >= min_chunk:
        return start + pos + 1

    pos = segment.rfind(" ")
    if pos >= min_chunk:
        return start + pos

    return end


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))

        if end < len(text):
            end = _find_break(text, start, end)

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        next_start = end - overlap
        if next_start <= start:
            next_start = start + chunk_size // 2
        start = next_start

    return chunks


def chunk_document(doc: dict, chunk_size: int = 1024, overlap: int = 128) -> list[dict]:
    text = doc.get("text", "")
    doc_id = doc.get("id", "unknown")
    metadata = doc.get("metadata", {})

    raw_chunks = _split_text(text, chunk_size, overlap)

    chunks: list[dict] = []
    for i, chunk_text in enumerate(raw_chunks):
        chunks.append({
            "id": f"{doc_id}_chunk_{i}",
            "text": chunk_text,
            "metadata": {**metadata},
        })

    return chunks
