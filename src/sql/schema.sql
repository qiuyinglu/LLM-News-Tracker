-- Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create Threads table
CREATE TABLE Threads (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(100) NOT NULL,
    country VARCHAR(10) NOT NULL,
    language VARCHAR(10) NOT NULL,
    llm_title TEXT NOT NULL,
    llm_summary TEXT NOT NULL,
    llm_embedding vector(3072) NOT NULL,
    status VARCHAR(50) CHECK (status IN ('started', 'evolving', 'stale', 'likely resolved')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create News table
CREATE TABLE News (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(100) NOT NULL,
    country VARCHAR(10) NOT NULL,
    language VARCHAR(10) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    content TEXT,
    url TEXT UNIQUE NOT NULL,
    image TEXT,
    published_at TIMESTAMPTZ NOT NULL,
    source_name VARCHAR(255),
    source_url TEXT,
    llm_summary TEXT NOT NULL,
    llm_embedding vector(3072) NOT NULL
);

-- Create ThreadsToNews table
CREATE TABLE ThreadsToNews (
    thread_uuid UUID NOT NULL REFERENCES Threads(uuid) ON DELETE CASCADE,
    news_uuid UUID NOT NULL REFERENCES News(uuid) ON DELETE CASCADE,
    embedding_cos_similarity DOUBLE PRECISION NOT NULL,
    llm_similarity_score INTEGER CHECK (llm_similarity_score >= 0 AND llm_similarity_score <= 101) NOT NULL,
    llm_similarity_justification TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (thread_uuid, news_uuid)
);

-- Create indexes
CREATE INDEX idx_news_url ON News(url);
CREATE INDEX idx_threads_to_news_thread_uuid ON ThreadsToNews(thread_uuid);
CREATE INDEX idx_threads_to_news_news_uuid ON ThreadsToNews(news_uuid);
CREATE INDEX idx_threads_created_at ON Threads(created_at);
CREATE INDEX idx_threads_updated_at ON Threads(updated_at);
