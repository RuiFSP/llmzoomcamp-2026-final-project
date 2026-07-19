## ADDED Requirements

### Requirement: System exposes a REST API
The system SHALL provide a Flask-based REST API with a POST `/api/chat` endpoint.

#### Scenario: Chat endpoint returns answer
- **WHEN** a POST request is sent to `/api/chat` with `{"question": "O que é o vinho verde?"}`
- **THEN** the response includes `answer`, `citations`, and `sources` fields

### Requirement: API supports conversation history
The system SHALL accept an optional `conversation_id` parameter to maintain multi-turn conversations.

#### Scenario: Multi-turn conversation
- **WHEN** a POST request includes `conversation_id` from a previous turn
- **THEN** the system uses the conversation history for context-aware answers

### Requirement: API logs all requests
The system SHALL log every request to PostgreSQL including question, rewritten query, answer, latency breakdown, and token counts.

#### Scenario: Request logging
- **WHEN** a chat request is processed
- **THEN** full request and response data is persisted to the logs table

### Requirement: API exposes health endpoint
The system SHALL expose a GET `/health` endpoint returning service status.

#### Scenario: Health check
- **WHEN** a GET request is sent to `/health`
- **THEN** the response returns `{"status": "ok"}` and includes connectivity checks for Qdrant and PostgreSQL
