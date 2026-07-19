# Evaluation Criteria Checklist

Internal reference for LLM Zoomcamp 2026 final project peer evaluation.

| Criterion | Score | How we meet it |
|---|---|---|
| Problem description | 2 | Well-defined domain (Portuguese food & wine), target users clearly identified (tourists, food enthusiasts), concrete problem statement |
| Retrieval flow | 2 | Knowledge base (Wikipedia + Infovini + MDPI) + LLM generation with hybrid search (dense + sparse), re-ranking, and query rewriting |
| Retrieval evaluation | 2 | Multiple strategies compared: dense-only, sparse-only, hybrid (RRF), and hybrid + reranked; metrics: Hit Rate@k, MRR@k |
| LLM evaluation | 2 | Relevance and faithfulness scored via LLM-as-judge on a 20+ question test set |
| Interface | 2 | Web chat UI (HTML/CSS/JS) + REST API (`POST /api/chat`, `POST /api/feedback`, `GET /api/health`) |
| Ingestion pipeline | 2 | Automated Python CLI (`python -m src.ingestion.run`) with `--reset` flag; scrapes Wikipedia, Infovini, and MDPI |
| Monitoring | 2 | User feedback collected via API + 8 Grafana panels auto-provisioned |
| Containerization | 2 | 4 services (api, qdrant, postgres, grafana) + optional caddy in Docker Compose; health checks on all dependencies |
| Reproducibility | 2 | `.env.example`, Docker Compose one-command startup, all Python deps in `pyproject.toml`, ML models cached in Docker layer |
| Hybrid search | +1 | Dense (e5-small) + sparse (BM25) fused via RRF |
| Re-ranking | +1 | Cross-encoder (`ms-marco-MiniLM-L-6-v2`) re-ranks top-20 candidates |
| Query rewriting | +1 | GPT-4o mini rewrites conversational questions into standalone retrieval queries |
| Cloud deployment | +2 | `provision.sh` + `deploy.sh` scripts; Caddy reverse proxy with auto TLS; `cloud` Compose profile |
| **Total** | **23/23** | |
