## ADDED Requirements

### Requirement: System generates answers from retrieved context
The system SHALL use GPT-4o to synthesize a natural language answer based on the top 5 retrieved chunks.

#### Scenario: Answer with citations
- **WHEN** the LLM generates an answer
- **THEN** the response includes inline citations referencing source documents (e.g., "[1] Gastronomia de Portugal - Wikipedia")

### Requirement: System handles insufficient context
The system SHALL respond truthfully when retrieved chunks lack sufficient information to answer the question.

#### Scenario: No relevant context
- **WHEN** no relevant chunks are found for a query
- **THEN** the LLM responds that the information is not available in the knowledge base

### Requirement: System supports conversation history
The system SHALL pass the last N turns of conversation history to the LLM for context-aware answers.

#### Scenario: Follow-up question with conversation context
- **WHEN** a user asks a follow-up question
- **THEN** the LLM receives the conversation history to provide a coherent answer

### Requirement: System logs generation metadata
The system SHALL log token usage, model version, and latency for each answer generation.

#### Scenario: Generation metadata logging
- **WHEN** an answer is generated
- **THEN** prompt tokens, completion tokens, model name, and response time are logged to PostgreSQL
