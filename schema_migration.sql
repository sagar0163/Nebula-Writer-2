-- Schema migration: pgvector tables with 384 dimensions and unique constraints
-- Run with: psql -d postgres -h host -U user -f schema_migration.sql

DROP TABLE IF EXISTS chapter_vectors CASCADE;
DROP TABLE IF EXISTS entity_vectors CASCADE;

CREATE TABLE chapter_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id UUID REFERENCES chapters(id) ON DELETE CASCADE UNIQUE,
    content TEXT NOT NULL,
    embedding vector(384),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE entity_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID REFERENCES entities(id) ON DELETE CASCADE UNIQUE,
    content TEXT NOT NULL,
    embedding vector(384),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_chapter_vectors_embedding 
ON chapter_vectors USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_entity_vectors_embedding 
ON entity_vectors USING hnsw (embedding vector_cosine_ops);