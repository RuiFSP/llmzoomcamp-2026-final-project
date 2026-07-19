import logging

import requests

logger = logging.getLogger(__name__)

WIKI_API = {
    "pt": "https://pt.wikipedia.org/w/api.php",
    "en": "https://en.wikipedia.org/w/api.php",
}


def fetch_wikipedia(lang: str, title: str) -> str:
    api_url = WIKI_API.get(lang)
    if not api_url:
        raise ValueError(f"Unsupported language: {lang}")

    headers = {
        "User-Agent": "PortugueseFoodWineGuide/1.0 (llmzoomcamp-2026-final-project)",
        "Accept": "application/json",
    }

    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "extracts",
        "explaintext": 1,
        "redirects": 1,
    }

    resp = requests.get(api_url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    pages = data.get("query", {}).get("pages", {})

    for page_id, page in pages.items():
        if page_id == "-1":
            logger.warning("Page '%s' not found on %s.wikipedia.org", title, lang)
            return ""
        return page.get("extract", "")

    return ""


def fetch_all_wikipedia() -> list[dict]:
    pages = [
        ("pt", "Gastronomia de Portugal"),
        ("en", "Portuguese cuisine"),
        ("en", "List of Portuguese dishes"),
    ]

    documents: list[dict] = []

    for lang, title in pages:
        try:
            text = fetch_wikipedia(lang, title)
            if not text:
                continue

            doc_id = f"wiki_{lang}_{title.lower().replace(' ', '_').replace('ç', 'c')}"

            documents.append({
                "id": doc_id,
                "text": text,
                "metadata": {
                    "source": "wikipedia",
                    "title": title,
                    "language": lang,
                    "url": f"https://{lang}.wikipedia.org/wiki/{title.replace(' ', '_')}",
                },
            })

            logger.info("Fetched Wikipedia page: %s (%s)", title, lang)

        except Exception:
            logger.warning("Failed to fetch Wikipedia page '%s' (%s)", title, lang, exc_info=True)

    return documents
