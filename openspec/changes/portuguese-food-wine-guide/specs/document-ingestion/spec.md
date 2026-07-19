## ADDED Requirements

### Requirement: System ingests Wikipedia PT documents
The system SHALL fetch, parse, and index the Wikipedia PT "Gastronomia de Portugal" article via the Wikipedia API.

#### Scenario: Successful Wikipedia PT ingestion
- **WHEN** the ingestion pipeline processes the "Gastronomia de Portugal" article
- **THEN** the article text is chunked, embedded, and stored in Qdrant with source metadata

### Requirement: System ingests Wikipedia EN documents
The system SHALL fetch, parse, and index Wikipedia EN articles for "Portuguese cuisine" and "List of Portuguese dishes".

#### Scenario: Successful Wikipedia EN ingestion
- **WHEN** the ingestion pipeline processes the specified EN articles
- **THEN** each article is chunked, embedded, and stored in Qdrant with language and source metadata

### Requirement: System ingests MDPI recipe dataset
The system SHALL attempt to download and parse the MDPI recipe dataset CSV. If unavailable, the system SHALL log a warning and continue with available data.

#### Scenario: MDPI dataset ingestion
- **WHEN** the MDPI CSV is accessible
- **THEN** each recipe is parsed into structured fields (name, province, ingredients, instructions), chunked, embedded, and indexed
- **WHEN** the MDPI CSV returns 403 or 404
- **THEN** the pipeline logs a warning and continues without MDPI data

### Requirement: System scrapes Infovini wine data
The system SHALL scrape structured wine data from Infovini (wine regions, grape varieties, wine types).

#### Scenario: Infovini data ingestion
- **WHEN** the pipeline runs the Infovini scraper
- **THEN** wine pages are parsed into structured records, chunked, embedded, and indexed with source metadata

### Requirement: Ingestion is idempotent
The system SHALL support re-running ingestion without duplicating documents.

#### Scenario: Idempotent re-ingestion
- **WHEN** ingestion is run a second time
- **THEN** existing documents are updated rather than duplicated, using a content hash or document ID to detect changes
