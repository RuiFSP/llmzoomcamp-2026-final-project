# Monitoring

Grafana is auto-provisioned with a PostgreSQL datasource and a pre-built dashboard (`dashboards/food-wine-dashboard.json`) containing 8 panels:

| Panel | Type | Description |
|---|---|---|
| Query Throughput | Time series | Requests per hour |
| Retrieval Latency (ms) | Time series | Average retrieval latency per hour |
| LLM Latency (ms) | Time series | Average LLM generation latency per hour |
| Token Usage | Time series | Prompt and completion tokens per hour |
| Error Rate (%) | Stat | Percentage of requests with exceptions |
| Total Queries | Stat | Total questions asked |
| Feedback Score (avg) | Stat | Average feedback score |
| Total Response Time (ms) | Time series | End-to-end latency per hour |

Access at `http://localhost:3000` (login: `admin` / `admin`).

User feedback is collected via the `POST /api/feedback` endpoint.
