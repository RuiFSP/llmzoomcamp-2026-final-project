# Evaluation Criteria Checklist

Internal reference for LLM Zoomcamp 2026 final project peer evaluation.

Each criterion is scored 0–2 by peers. The final three rows are bonus (+1 or +2).

| Criterion | How we meet it |
|---|---|
| Problem description | Well-defined domain (Portuguese food & wine), target users clearly identified (tourists, food enthusiasts), concrete problem statement |
| Retrieval flow | Knowledge base (Wikipedia + Infovini + MDPI) + LLM generation with hybrid search (dense + sparse), re-ranking, and query rewriting |
| Retrieval evaluation | Multiple strategies compared: dense-only, sparse-only, hybrid (RRF), and hybrid + reranked; metrics: Hit Rate@k, MRR@k |
| LLM evaluation | Relevance and faithfulness scored via LLM-as-judge on a 20+ question test set |
| Interface | Web chat UI (HTML/CSS/JS) + REST API (`POST /api/chat`, `POST /api/feedback`, `GET /api/health`) |
| Ingestion pipeline | Automated Python CLI (`python -m src.ingestion.run`) with `--reset` flag; scrapes Wikipedia, Infovini, and MDPI |
| Monitoring | User feedback collected via API + 8 Grafana panels auto-provisioned |
| Containerization | 4 services (api, qdrant, postgres, grafana) + optional caddy in Docker Compose; health checks on all dependencies |
| Reproducibility | `.env.example`, Docker Compose one-command startup, all Python deps in `pyproject.toml`, ML models cached in Docker layer |
| Hybrid search | Dense (e5-small) + sparse (BM25) fused via RRF |
| Re-ranking | Cross-encoder (`ms-marco-MiniLM-L-6-v2`) re-ranks top-20 candidates |
| Query rewriting | GPT-4o mini rewrites conversational questions into standalone retrieval queries |
| Cloud deployment | `provision.sh` + `deploy.sh` scripts; Caddy reverse proxy with auto TLS; `cloud` Compose profile |
