## ADDED Requirements

### Requirement: System performs dense retrieval
The system SHALL embed queries using the multilingual-e5-small model and search Qdrant by dense vector similarity.

#### Scenario: Dense retrieval returns relevant chunks
- **WHEN** a user asks "O que é o cozido à portuguesa?"
- **THEN** the dense search returns chunks semantically related to Portuguese stew dishes

### Requirement: System performs sparse retrieval
The system SHALL compute BM25 scores for query terms against indexed documents and return sparse retrieval results.

#### Scenario: Sparse retrieval matches keywords
- **WHEN** a user asks "vinho do Porto"
- **THEN** the sparse search returns chunks containing those exact keywords with high BM25 scores

### Requirement: System combines dense and sparse results
The system SHALL merge dense and sparse search results using reciprocal rank fusion (RRF).

#### Scenario: Hybrid fusion returns combined results
- **WHEN** a user search is performed
- **THEN** the system returns a merged, deduplicated list of candidates ranked by RRF score

### Requirement: System re-ranks top candidates
The system SHALL re-rank the top 20 hybrid search candidates using a cross-encoder model and return the top 5.

#### Scenario: Re-ranking improves result ordering
- **WHEN** top 20 candidates are re-ranked by cross-encoder
- **THEN** the final top 5 results are ordered by cross-encoder relevance score
