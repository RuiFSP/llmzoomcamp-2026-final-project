CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(64) NOT NULL,
    question TEXT NOT NULL,
    rewritten_question TEXT NOT NULL,
    answer TEXT NOT NULL,
    sources JSONB,
    retrieval_latency_ms FLOAT,
    llm_latency_ms FLOAT,
    total_latency_ms FLOAT,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    model VARCHAR(64),
    error VARCHAR(256),
    feedback INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_conversations_conversation_id ON conversations(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversations_error ON conversations(error);
