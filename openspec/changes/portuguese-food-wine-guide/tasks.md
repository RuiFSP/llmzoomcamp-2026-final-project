## 1. Project Setup

- [x] 1.1 Create project structure (directories: `src/`, `data/`, `notebooks/`, `dashboards/`, `docker/`)
- [x] 1.2 Set up Python project with `pyproject.toml` and dependencies (Flask, openai, sentence-transformers, qdrant-client, psycopg2-binary, rank-bm25, beautifulsoup4, tiktoken, gunicorn)
- [x] 1.3 Create Docker Compose file with services: api, qdrant, postgres, grafana
- [x] 1.4 Create Dockerfile for the API service

## 2. Data Ingestion

- [x] 2.1 Implement Wikipedia PT scraper for "Gastronomia de Portugal"
- [x] 2.2 Implement Wikipedia EN scraper for "Portuguese cuisine" and "List of Portuguese dishes"
- [x] 2.3 Implement Infovini wine data scraper
- [x] 2.4 Attempt MDPI recipe dataset download (graceful fallback if 403)
- [x] 2.5 Implement text chunking using RecursiveCharacterTextSplitter (512 chars, 64 overlap)
- [x] 2.6 Implement embedding pipeline with multilingual-e5-small
- [x] 2.7 Implement Qdrant index creation and document upload with metadata
- [x] 2.8 Create ingestion CLI script (`python -m src.ingestion.run`)
- [x] 2.9 Implement idempotent re-ingestion (skip/update existing docs by content hash)

## 3. Search Pipeline

- [x] 3.1 Implement BM25 sparse retrieval module
- [x] 3.2 Implement Qdrant dense vector search client
- [x] 3.3 Implement hybrid fusion using reciprocal rank fusion (RRF)
- [x] 3.4 Implement cross-encoder re-ranker (top 20 → top 5)
- [x] 3.5 Implement query rewriting module using GPT-4o mini

## 4. Answer Generation

- [x] 4.1 Implement LLM answer generation using GPT-4o with retrieved context
- [x] 4.2 Add citation tracking (link answers back to source documents)
- [x] 4.3 Handle insufficient context gracefully (refuse to answer without relevant docs)
- [x] 4.4 Implement conversation history support (last N turns passed to LLM)

## 5. API & Interface

- [x] 5.1 Implement Flask REST API with POST `/api/chat` endpoint
- [x] 5.2 Implement GET `/health` endpoint with service checks
- [x] 5.3 Add request logging to PostgreSQL (question, rewritten query, answer, latencies, tokens)
- [x] 5.4 Build chat UI (HTML/CSS/JS served from Flask at `/`)
- [x] 5.5 Wire UI to API endpoint with conversation_id management

## 6. Database & Monitoring

- [x] 6.1 Create PostgreSQL schema for conversation logs and metrics
- [x] 6.2 Implement metric logging for each request (latencies, tokens, errors)
- [x] 6.3 Create Grafana dashboard JSON with 5+ panels (throughput, retrieval latency, LLM latency, token usage, error rate)
- [x] 6.4 Configure Grafana auto-provisioning (datasource + dashboard at startup)

## 7. Evaluation

- [x] 7.1 Curate test set of 20+ question-answer pairs covering all data sources
- [x] 7.2 Create retrieval evaluation notebook (hit rate@k, MRR@k)
- [x] 7.3 Create LLM evaluation notebook (relevance, faithfulness via LLM-as-judge)

## 8. Cloud Deployment

- [x] 8.1 Add Caddy reverse proxy service to docker-compose behind a `cloud` profile
- [x] 8.2 Create `deploy/provision.sh` — script to bootstrap a cloud VM with Docker Engine
- [x] 8.3 Create `deploy/deploy.sh` — script to rsync the stack to the VM and run `docker compose up -d`
- [x] 8.4 Document cloud deployment steps in README with expected cost and VM specs
- [ ] 8.5 Test deploy to a cloud VM and verify all services accessible via HTTPS

## 9. Containerization & Final Polish

- [x] 9.1 Finalize Docker Compose (ports, volumes, env vars for OpenAI key)
- [x] 9.2 Create `.env.example` with required environment variables
- [x] 9.3 Write README with setup instructions, architecture overview, evaluation results, and cloud deployment guide
- [x] 9.4 End-to-end smoke test: `docker compose up --build` and verify all services
- [ ] 9.5 Run evaluation notebooks and document results
