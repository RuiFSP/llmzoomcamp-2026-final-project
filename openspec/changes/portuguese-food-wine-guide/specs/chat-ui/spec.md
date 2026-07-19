## ADDED Requirements

### Requirement: System serves a chat interface
The system SHALL serve a browser-based chat UI at the root path (`/`) for interactive Q&A.

#### Scenario: User asks a question via UI
- **WHEN** a user types a question in the chat UI and submits it
- **THEN** the answer appears in the chat window with citation links

### Requirement: Chat UI shows conversation history
The UI SHALL display the full conversation turn history during a session.

#### Scenario: Multi-turn display
- **WHEN** a user asks multiple questions in a session
- **THEN** all previous turns are visible in the chat window

### Requirement: Chat UI shows citations as references
The UI SHALL display citation sources alongside each answer.

#### Scenario: Citation display
- **WHEN** an answer with citations is returned
- **THEN** clickable reference numbers are shown for each cited source
