# Limitations & Future Improvements

## Current Limitations

- **No food-wine pairing data** — The knowledge base does not contain explicit pairing information. Questions like "which wine goes with bacalhau?" cannot be answered.
- **Slow response times (15–30s)** — On a 1GB RAM droplet, loading ML models and calling GPT-4o takes significant time. A 2GB+ VM would cut this in half.
- **Limited knowledge base** — Only 1514 chunks from 3 sources. Does not cover all Portuguese dishes or wine varieties.
- **MDPI recipes have no instructions** — The dataset only contains ingredient matrices, not preparation steps.
- **No HTTPS without a domain** — Caddy can only provision TLS certificates when a real domain is configured.
- **Cross-encoder trained on English** — The re-ranker model (`ms-marco-MiniLM-L-6-v2`) was trained on English data and may not score Portuguese text optimally. A multi-language alternative (e.g., `BAAI/bge-reranker-v2-m3`) would require ~600 MB more disk and ~2x more RAM — a trade-off we chose not to make on a 1 GB VM.
- **Single gunicorn worker** — Only one request can be processed at a time. Concurrent users will be queued.
- **Error logging depends on database** — If PostgreSQL is unreachable, application errors cannot be persisted.
- **Python 3.14 (pre-release)** — The project uses a pre-release Python version, which may cause dependency issues with some packages.

## Future Improvements

- **Add food-wine pairing data** — Extract pairing information from specialized sources or use LLM knowledge directly.
- **2GB+ VM** — Upgrade to a droplet with more RAM for faster inference.
- **More data sources** — Add recipe websites, wine blogs, and gastronomy forums.
- **MDPI recipe instructions** — Parse the PDF included in the MDPI dataset for actual preparation steps.
- **Streaming responses** — Show the answer incrementally as GPT-4o generates it.
- **Query caching** — Cache frequent queries for instant responses.
- **Async workers** — Switch to async gunicorn workers to handle concurrent requests.
- **Automated tests** — Add unit tests and integration tests.
- **CI/CD improvements** — Add automated testing to the GitHub Actions pipeline.
- **Multi-language support** — Expand to English and other languages.
