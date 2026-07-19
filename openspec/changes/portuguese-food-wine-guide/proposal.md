## Why

Build a Portuguese Food & Wine Guide as the final project for the LLM Zoomcamp 2026 course. The goal is to demonstrate an end-to-end RAG system — from data ingestion through retrieval, LLM integration, evaluation, and monitoring — that answers questions about Portuguese cuisine, traditional recipes, wine regions, and food-wine pairings. This fills a gap: no existing assistant covers Portuguese gastronomy in a Q&A RAG format using both academic recipe data and curated wine knowledge.

## What Changes

- Add a new RAG system service with the following components:
  - **Data ingestion pipeline** — fetches, parses, chunks, and indexes documents from both academic (MDPI recipe dataset) and non-academic (Wikipedia, Infovini) sources into a vector database with metadata
  - **Hybrid search** — combines semantic search (with sentence-transformers embeddings) and keyword search (BM25-style) with re-ranking for retrieval quality
  - **Query rewriting** — rewrites user queries to improve retrieval accuracy
  - **LLM-based answer generation** — uses OpenAI API (GPT-4o) to synthesize answers from retrieved chunks, with citations
  - **REST API** — Flask-based API serving the chat interface
  - **Chat UI** — simple web interface for interactive Q&A
  - **Monitoring** — Grafana dashboards with 5+ metrics (retrieval latency, LLM latency, token usage, error rates, user satisfaction proxies)
  - **Evaluation pipeline** — offline evaluation of retrieval quality (hit rate, MRR) and LLM answer quality (relevance, faithfulness)
  - **Cloud deployment** — same Docker Compose stack deployable to a cloud VM (DigitalOcean / AWS EC2) with a single script, keeping local `docker compose up` as the primary dev workflow
- Containerize all services with Docker Compose
- Add retrieval evaluation notebook and LLM evaluation notebook

## Capabilities

### New Capabilities
- `document-ingestion`: Pipeline to scrape, parse, chunk, embed, and index documents from Wikipedia (PT/EN), Infovini (wine data), and the MDPI recipe dataset
- `hybrid-search`: Combined dense + sparse retrieval with re-ranking for high-quality document retrieval
- `query-rewriting`: Rewrite user questions for improved retrieval performance
- `answer-generation`: LLM-based answer synthesis from retrieved context with citation support
- `chat-api`: Flask REST API with conversation endpoint, history tracking, and metadata logging
- `chat-ui`: Browser-based chat interface for interacting with the assistant
- `evaluation-pipeline`: Offline retrieval and LLM evaluation with notebooks and metrics
- `monitoring`: Grafana dashboards tracking system and LLM metrics
- `cloud-deployment`: Scripted deployment to a cloud VM using the same docker-compose stack

### Modified Capabilities

None — no existing specs to modify.

## Impact

- **New Python dependencies**: `flask`, `openai`, `sentence-transformers`, `pandas`, `numpy`, `scikit-learn`, `psycopg2` or async equivalent, `beautifulsoup4`, `requests`, `tiktoken`
- **Infrastructure**: PostgreSQL for metadata/logging, Qdrant or pgvector for vector storage, Grafana + PostgreSQL for dashboards, all containerized via Docker Compose
- **Repository additions**: New directories for services (`src/ingestion/`, `src/search/`, `src/api/`, `src/evaluation/`), notebooks (`notebooks/`), dashboards (`dashboards/`), Dockerfiles (`docker/`), deployment scripts (`deploy/`)
- **Cloud infra**: Single cloud VM with Docker (e.g., DigitalOcean droplet, AWS EC2); SSH + `docker compose up` for deployment; no managed services — keeps the same stack as local dev
- **No breaking changes** — this is purely additive
