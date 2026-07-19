## ADDED Requirements

### Requirement: System logs structured metrics to PostgreSQL
The system SHALL log per-request metrics including query text, retrieval latency, LLM latency, token counts, error status, and number of retrieved chunks.

#### Scenario: Metrics logged per request
- **WHEN** a chat request completes
- **THEN** a row is inserted into the metrics table with all latency breakdowns and token counts

### Requirement: Grafana displays 5+ dashboard panels
The system SHALL provide a pre-configured Grafana dashboard with at least 5 panels tracking system performance.

#### Scenario: Dashboard shows query throughput
- **WHEN** Grafana is accessed
- **THEN** the dashboard includes a panel showing requests per minute over time

#### Scenario: Dashboard shows latency breakdown
- **WHEN** Grafana is accessed
- **THEN** the dashboard includes panels for retrieval latency (p50/p95/p99), LLM latency, and total response time

#### Scenario: Dashboard shows token usage
- **WHEN** Grafana is accessed
- **THEN** the dashboard includes a panel for prompt and completion token counts over time

#### Scenario: Dashboard shows error rate
- **WHEN** Grafana is accessed
- **THEN** the dashboard includes a panel showing the error rate (5xx, 4xx) over time

#### Scenario: Dashboard shows user feedback
- **WHEN** Grafana is accessed and user feedback is logged
- **THEN** the dashboard includes a panel showing the average feedback score over time

### Requirement: Grafana is pre-configured
The Grafana instance SHALL be pre-configured with the PostgreSQL data source and the dashboard imported at startup.

#### Scenario: Dashboard auto-provisions
- **WHEN** `docker compose up` starts Grafana
- **THEN** the PostgreSQL data source and food-wine dashboard are provisioned automatically
