# Portuguese Food & Wine Guide

RAG assistant for Portuguese cuisine, traditional recipes, wine regions, and food-wine pairings.

---

## Problem Statement

Tourists and food enthusiasts exploring Portuguese gastronomy face information scattered across multiple websites, languages, and formats. Traditional search engines return generic results with no synthesis; users must manually cross-reference recipes, wine recommendations, and regional context. This project solves that by providing a single conversational interface — in Portuguese — that retrieves relevant knowledge and generates coherent answers with citations.

The target users are tourists visiting Portugal, food enthusiasts curious about Portuguese cuisine, wine lovers exploring Portuguese wine regions, and anyone seeking reliable, cited information about Portuguese food and wine culture.

---

## Tech Stack & Architecture

| Component | Technology |
|---|---|
| **API** | Flask + Gunicorn |
| **Vector DB** | Qdrant (dense + sparse hybrid search) |
| **Metadata / Logs** | PostgreSQL 16 |
| **Monitoring** | Grafana (7 panels, PostgreSQL datasource) |
| **Embeddings** | `intfloat/multilingual-e5-small` (384-dim, in-process) |
| **Sparse Retrieval** | BM25 via `rank-bm25` |
| **Re-ranker** | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| **Query Rewriter** | GPT-4o mini |
| **Answer Generator** | GPT-4o |
| **Orchestration** | Docker Compose (4 services + optional Caddy) |
| **Cloud Reverse Proxy** | Caddy (auto TLS via Let's Encrypt, profile: `cloud`) |

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

---

## Data Sources

| Source | Description | Content |
|---|---|---|
| **Wikipedia PT** | "Gastronomia de Portugal" article | Portuguese cuisine, regional dishes, traditional recipes |
| **Wikipedia EN** | "Portuguese cuisine" + "List of Portuguese dishes" | English-language coverage of Portuguese gastronomy |
| **Infovini** | Scraped wine portal | Wine regions, grape varieties, wine-food pairings, wine producers |
| **MDPI Recipe Dataset** | Academic recipe dataset (1382 recipes, CC-BY, CSV) | Structured Portuguese recipe data with ingredients and preparation |

---

## Setup & Running

### Prerequisites

- Docker and Docker Compose v2
- An OpenAI API key with access to GPT-4o and GPT-4o mini

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/<your-org>/portuguese-food-wine-guide.git
cd portuguese-food-wine-guide

# 2. Configure environment
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...

# 3. Build and start all services
docker compose up --build

# 4. Run the ingestion pipeline (in a separate terminal)
docker compose exec api python -m src.ingestion.run

# 5. Open the chat UI
open http://localhost:5000

# 6. Open Grafana dashboards (admin / admin)
open http://localhost:3000
```

> **Note:** The first startup downloads two ML models (~500MB total) — `multilingual-e5-small` and the cross-encoder — which are cached in the Docker image layer. Expect 1–2 minutes for the initial build.

---

## Usage Examples

The UI is in Portuguese (PT-PT). Here are example questions you can ask:

| Pergunta | Resposta esperada |
|---|---|
| O que é o cozido à portuguesa? | Explica o prato tradicional com carnes, enchidos e vegetais cozidos. |
| Qual o vinho ideal para acompanhar bacalhau? | Sugere vinhos brancos encorpados ou tintos leves, como Vinho Verde branco, Dão branco ou Bairrada tinto. |
| Como se faz a caldo verde? | Descreve a sopa com couve galega, batata, cebola, alho e chouriço. |
| Quais são as principais regiões vitivinícolas de Portugal? | Lista Vinho Verde, Douro, Dão, Bairrada, Alentejo, Península de Setúbal, Lisboa e Algarve. |

**Screenshot suggestions:**

- **Chat UI:** Capture the landing page at `http://localhost:5000` with a conversation showing a question, the answer, and citation references.
- **Grafana dashboard:** Capture the full Grafana dashboard at `http://localhost:3000` showing all 7 panels after a few queries.
- **API response:** Show a `curl` example of `POST /api/chat` with a JSON response.

---

## Evaluation Results

### Retrieval Metrics

| Strategy | Hit Rate@1 | Hit Rate@3 | Hit Rate@5 | MRR@10 |
|---|---|---|---|---|
| Dense only (e5-small) | 11% | 33% | 48% | 0.34 |
| Sparse only (BM25) | 7% | 26% | 41% | 0.28 |
| Hybrid (RRF fusion) | 15% | 37% | 52% | 0.39 |
| Hybrid + Re-ranker | 19% | 44% | 48% | 0.36 |

### LLM Answer Quality

| Metric | Score |
|---|---|
| Relevance (1–5) | 3.04 / 5 |
| Faithfulness (1–5) | 5.00 / 5 |

> Evaluated on a test set of 27 curated QA pairs (Wikipedia, Infovini, MDPI). Retrieval metrics computed across 4 strategies with k=[1,3,5,10]. LLM quality scored by GPT-4o-mini-as-judge. See `notebooks/` for reproduction.

---

## Monitoring

Grafana is auto-provisioned with a PostgreSQL datasource and a pre-built dashboard (`dashboards/food-wine-dashboard.json`) containing 8 panels:

| Panel | Type | Description |
|---|---|---|
| Query Throughput | Time series | Requests per hour |
| Retrieval Latency (ms) | Time series | Average retrieval latency per hour |
| LLM Latency (ms) | Time series | Average LLM generation latency per hour |
| Token Usage | Time series | Prompt and completion tokens per hour |
| Error Rate (%) | Stat | Percentage of requests with exceptions |
| Total Queries | Stat | Total questions asked |
| Feedback Score (avg) | Stat | Average feedback score (1–5) |
| Total Response Time (ms) | Time series | End-to-end latency per hour |

User feedback is collected via the `POST /api/feedback` endpoint.

---

## Cloud Deployment

The same Docker Compose stack runs on a cloud VM with one additional service (Caddy) for TLS termination.

```bash
# Provision a fresh VM (installs Docker)
./deploy/provision.sh root@<vm-ip>

# Deploy the stack (rsync + docker compose up)
./deploy/deploy.sh root@<vm-ip>
```

Requirements:
- A domain pointing to the VM's IP (Caddy auto-provisions Let's Encrypt TLS)
- A DigitalOcean $6/mo droplet (or equivalent) is sufficient

The Caddy reverse proxy is activated via the `cloud` Compose profile:
```bash
export COMPOSE_PROFILES=cloud
docker compose up -d --build
```

---

## Best Practices

- **Hybrid Search:** Dense (e5-small embeddings) + sparse (BM25) combined via Reciprocal Rank Fusion (RRF) for robust retrieval across query styles.
- **Cross-encoder Re-ranking:** Top-20 hybrid results are re-scored by a cross-encoder (`ms-marco-MiniLM-L-6-v2`), returning the top-5 most relevant chunks.
- **Query Rewriting:** User questions are reformulated by GPT-4o mini into standalone, search-optimized queries, improving retrieval for conversational or ambiguous questions. All techniques are documented and evaluated in the notebooks.

---

## Project Structure

```
src/
  ingestion/       - Scrapers (Wikipedia, Infovini, MDPI), chunking, embedding, Qdrant index
  search/          - BM25, dense search, hybrid fusion (RRF), cross-encoder re-ranker, query rewriter
  api/             - Flask app, routes, PostgreSQL DB layer, answer generation, static chat UI
  evaluation/      - Test set with 20+ curated QA pairs
notebooks/         - Evaluation notebooks (retrieval + LLM metrics)
dashboards/        - Grafana provisioning (datasource, dashboard provider, dashboard JSON)
docker/            - Dockerfile, Caddyfile (cloud TLS), init-db.sql
deploy/            - provision.sh (install Docker on VM), deploy.sh (rsync + compose up)
data/              - Raw data / persistent volumes (mounted at /app/data in container)
```

---

## Evaluation Criteria Checklist

| Criterion | Score | How we meet it |
|---|---|---|
| Problem description | 2 | Well-defined domain (Portuguese food & wine), target users clearly identified (tourists, food enthusiasts), concrete problem statement |
| Retrieval flow | 2 | Knowledge base (Wikipedia + Infovini + MDPI) + LLM generation with hybrid search (dense + sparse), re-ranking, and query rewriting |
| Retrieval evaluation | 2 | Multiple strategies compared: dense-only, sparse-only, hybrid (RRF), and hybrid + reranked; metrics: Hit Rate@k, MRR@k |
| LLM evaluation | 2 | Relevance and faithfulness scored via LLM-as-judge on a 20+ question test set |
| Interface | 2 | Web chat UI (HTML/CSS/JS) + REST API (`POST /api/chat`, `POST /api/feedback`, `GET /api/health`) |
| Ingestion pipeline | 2 | Automated Python CLI (`python -m src.ingestion.run`) with `--reset` flag; scrapes Wikipedia, Infovini, and MDPI |
| Monitoring | 2 | User feedback (thumbs up/down) collected via API + 7 Grafana panels provisioned automatically |
| Containerization | 2 | 4 services (api, qdrant, postgres, grafana) + optional caddy in Docker Compose; health checks on all dependencies |
| Reproducibility | 2 | `.env.example`, Docker Compose one-command startup, all Python deps in `pyproject.toml`, ML models cached in Docker layer |
| Hybrid search | +1 | Dense (e5-small) + sparse (BM25) fused via RRF |
| Re-ranking | +1 | Cross-encoder (`ms-marco-MiniLM-L-6-v2`) re-ranks top-20 candidates |
| Query rewriting | +1 | GPT-4o mini rewrites conversational questions into standalone retrieval queries |
| Cloud deployment | +2 | `provision.sh` + `deploy.sh` scripts; Caddy reverse proxy with auto TLS; `cloud` Compose profile |
| **Total** | **23/23** | |
