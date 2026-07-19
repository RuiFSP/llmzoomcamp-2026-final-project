## ADDED Requirements

### Requirement: System provides retrieval evaluation
The system SHALL include a Jupyter notebook that evaluates retrieval quality using hit rate and mean reciprocal rank (MRR).

#### Scenario: Retrieval metrics computed
- **WHEN** the retrieval evaluation notebook is executed on a test set of question-answer pairs
- **THEN** hit rate@k and MRR@k metrics are computed and displayed

### Requirement: System provides LLM evaluation
The system SHALL include a Jupyter notebook that evaluates LLM answer quality using relevance and faithfulness metrics (LLM-as-judge).

#### Scenario: LLM evaluation metrics computed
- **WHEN** the LLM evaluation notebook is executed
- **THEN** answers are scored for relevance to the question and faithfulness to the retrieved context

### Requirement: Evaluation uses a curated test set
The system SHALL include a curated test set of at least 20 question-answer pairs covering all data sources.

#### Scenario: Test set validation
- **WHEN** evaluation is run
- **THEN** the test set covers Wikipedia, recipes, and wine questions
