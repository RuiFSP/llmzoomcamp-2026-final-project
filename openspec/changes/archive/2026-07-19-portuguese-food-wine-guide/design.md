## Context

This project builds a Portuguese Food & Wine RAG assistant as the final project for LLM Zoomcamp 2026. The reference architecture is the course's fitness-assistant example: Flask API, PostgreSQL, vector search, Grafana monitoring, and Docker Compose orchestration. The system must use only OpenAI models (user-provided API key) and target PT-PT language queries.

Data sources identified during exploration:
- Wikipedia PT "Gastronomia de Portugal"
- Wikipedia EN "Portuguese cuisine" + "List of Portuguese dishes"
- MDPI academic recipe dataset (1382 recipes, CC-BY, CSV format)
- Infovini wine portal (web scraping required)

## Goals / Non-Goals

**Goals:**
- RAG system answering Portuguese food and wine questions with citations
- Hybrid search (dense + sparse) with re-ranking for retrieval quality
- Query rewriting to improve retrieval for conversational questions
- LLM answer generation via OpenAI GPT-4o
- REST API (Flask) with chat interface (HTML/CSS/JS)
- Offline evaluation: retrieval (hit rate, MRR) and LLM (relevance, faithfulness)
- Grafana monitoring with 5+ metrics dashboards
- Full Docker Compose containerization
- Reproducible: one command to start all services

**Non-Goals:**
- Real user authentication or multi-tenancy
- Streaming responses (simpler synchronous response is fine)
- Handling image data from recipes
- Real-time data updates (batch ingest once)
- Kubernetes or multi-node orchestration (single VM is sufficient for demo)

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **Vector Database** | Qdrant via HTTP client | Simpler than pgvector; standalone service; built-in hybrid search via `query` with dense + sparse mode; no need for async drivers |
| **Embedding Model** | `intfloat/multilingual-e5-small` | Supports Portuguese natively (no language gap); small enough to run in CPU quickly; produces high-quality 384-dim vectors |
| **Chunking Strategy** | RecursiveCharacterTextSplitter on paragraphs, 512-char chunks, 64-char overlap | Start simple; iterate later on semantic chunking if retrieval quality requires it |
| **Sparse Retrieval** | BM25 via `rank-bm25` | Lightweight; no external service needed; fits the hybrid search pattern from the course |
| **Re-ranker** | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Well-known cross-encoder; good balance of quality and speed; English cross-encoder still effective for retrieval ranking |
| **Query Rewriting** | LLM-based (GPT-4o mini, single prompt) | Simple to implement; GPT-4o mini is cheap and fast for reformulation |
| **Metadata Storage** | PostgreSQL | Same as course example; stores conversation logs, query history, evaluation results |
| **Embedding Service** | In-process in the API container | Avoids extra microservice; sentence-transformers loads model at startup and computes embeddings inline |
| **Containerization** | Docker Compose with 4 services: api, qdrant, postgres, grafana | Matches course pattern; clear separation of concerns |
| **Monitoring** | Grafana + PostgreSQL (metrics logged to PG) | Simpler than Prometheus; course uses this pattern; logs serve as the metrics source |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Docker Compose                        │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Flask API   │───▶│   Qdrant     │    │  PostgreSQL  │  │
│  │  (gunicorn)   │    │  (vectors)   │    │  (metadata)  │  │
│  └──────┬───────┘    └──────────────┘    └──────┬───────┘  │
│         │                                       │          │
│         │  ┌──────────────────┐                 │          │
│         ├──▶  Ingestion CLI   │                 │          │
│         │  └──────────────────┘                 │          │
│         │                                       │          │
│         │                              ┌────────┴──────┐  │
│         │                              │    Grafana    │  │
│         │                              │  (dashboards) │  │
│         │                              └───────────────┘  │
│  ┌──────┴───────┐                                         │
│  │   Chat UI    │                                         │
│  │  (static)    │                                         │
│  └──────────────┘                                         │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
User Question
    │
    ▼
[Query Rewriter] ── GPT-4o mini reformulates question
    │
    ▼
[Embedder] ── multilingual-e5-small embeds the rewritten query
    │
    ▼
[Hybrid Search] ── Qdrant search with dense vector + BM25 sparse vector
    │      ┌─ top_k=20 candidates
    ▼
[Re-ranker] ── cross-encoder scores top 20 → returns top 5 chunks
    │
    ▼
[Answer Generator] ── GPT-4o synthesizes answer from 5 chunks with citations
    │
    ▼
[Response] ── answer + citations + chunk metadata
```

## Cloud Deployment

The same docker-compose stack runs locally and on the cloud. The cloud is just a VM with Docker Engine — no managed services, no orchestration changes.

**Approach:**

| Aspect | Choice |
|---|---|
| **Cloud Provider** | DigitalOcean (simplest, $6/mo droplet) or AWS EC2 free tier |
| **Provisioning** | `deploy/provision.sh` script using `docker-machine` or manual SSH setup |
| **Deployment** | `deploy/deploy.sh` — rsyncs docker-compose files and `.env`, runs `docker compose up -d` |
| **HTTPS** | Caddy as a reverse proxy sidecar in docker-compose (auto TLS via Let's Encrypt) |
| **Domain** | Optional — accessible via IP or set up a domain |
| **Data Persistence** | Docker volumes preserved on the VM; export/import for evaluation results |

**Local vs Cloud:**

```
# Local
docker compose up --build

# Cloud (same compose file + Caddy sidecar for TLS)
./deploy/deploy.sh root@<vm-ip>
```

The `docker-compose.yml` has an `nginx` or `caddy` service behind a YAML anchor / profile so it's only active on cloud (`COMPOSE_PROFILES=cloud`).

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| MDPI dataset inaccessible (403) | Wikipedia PT/EN and Infovini are sufficient fallback; can manually curate a small recipe set from open web sources |
| Infovini structure changes | Scraper targets specific CSS selectors; pin the scraper to a version and add a `--validate` flag to check page structure |
| `multilingual-e5-small` size (~500MB download) | Download once; bake into Docker image layer with `pre-commit` cache or load from volume |
| Cross-encoder re-ranker latency (~200ms per pair) | Only re-rank top 20; acceptable at 1-4 seconds total response time for a demo |
| PT-PT query understanding for wine terms | E5 multilingual model handles European Portuguese well; test and adapt if needed |
| Grafana dashboard metrics too simplistic | Log every query with timings, token counts, retrieved chunks, and user feedback proxy (thumbs up/down) for rich dashboards |

## Open Questions

- Does the MDPI dataset download become available? If not, what curated fallback recipe set to use?
- Should we implement user feedback (thumbs up/down) in the UI for the evaluation dashboard?
- Exact Grafana metrics to track — needs final list once data flow is implemented (aiming for 5+: query throughput, retrieval latency, LLM latency, token usage, error rate, feedback score)
- Cloud VM choice: DigitalOcean vs AWS EC2 free tier vs Railway? Finalize based on cost and reproducibility for reviewers
- Caddy vs Nginx for HTTPS reverse proxy — Caddy is simpler (auto TLS), Nginx is more common
