## ADDED Requirements

### Requirement: System rewrites user queries
The system SHALL rewrite user questions using GPT-4o mini to improve retrieval effectiveness before embedding and searching.

#### Scenario: Short query expansion
- **WHEN** a user asks "pastéis de nata"
- **THEN** the rewritten query expands to something like "receita e origem dos pastéis de nata portugueses" before embedding

#### Scenario: Anaphora resolution
- **WHEN** a user asks "E o que acompanha?" in a follow-up question
- **THEN** the system rewrites the query using conversation history to resolve the reference and form a standalone question

### Requirement: Rewritten query replaces original for retrieval
The system SHALL use the rewritten query for embedding and search while preserving the original question in conversation history.

#### Scenario: Rewritten used for search
- **WHEN** a query is rewritten
- **THEN** the rewritten version is used for retrieval while the original is stored in conversation logs
