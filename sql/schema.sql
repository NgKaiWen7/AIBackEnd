-- AIBackEnd PostgreSQL schema
--
-- Bootstrap a new database with:
--   psql -d knowledge_db -f sql/schema.sql
--
-- This is deliberately additive/idempotent for a new database.  Use a proper
-- migration for destructive changes to an existing database.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS study_source (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT,
    category TEXT[] DEFAULT '{}',
    status TEXT DEFAULT 'Want to Read',
    last_read TIMESTAMPTZ,
    description TEXT,
    source TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID NOT NULL REFERENCES study_source(id) ON DELETE CASCADE,
    position INTEGER,
    level INTEGER NOT NULL DEFAULT -1,
    raw_text TEXT NOT NULL,
    meta_data JSONB,
    card_path TEXT,
    generate BOOLEAN NOT NULL DEFAULT TRUE,
    -- No dimension is declared because the embedding model is configurable.
    embeddings VECTOR,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Keeps existing databases compatible with the chunk image scheduler.
ALTER TABLE chunks
    ADD COLUMN IF NOT EXISTS generate BOOLEAN NOT NULL DEFAULT TRUE;

CREATE INDEX IF NOT EXISTS chunks_book_position_idx
    ON chunks (book_id, position, id);

CREATE INDEX IF NOT EXISTS chunks_book_level_idx
    ON chunks (book_id, level, id);

CREATE INDEX IF NOT EXISTS chunks_raw_text_fts_idx
    ON chunks
    USING GIN (to_tsvector('english', COALESCE(raw_text, '')));

-- Legacy/imported decks are retained independently from chunk-backed cards.
CREATE TABLE IF NOT EXISTS card_decks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Not a foreign key: imported decks can have a source ID outside study_source.
    source_id UUID NOT NULL,
    title TEXT,
    style TEXT,
    domain TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deck_id UUID NOT NULL REFERENCES card_decks(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    image_prompt TEXT NOT NULL,
    generate BOOLEAN NOT NULL DEFAULT TRUE,
    image_path TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS cards_deck_created_idx
    ON cards (deck_id, created_at);

CREATE INDEX IF NOT EXISTS cards_pending_generation_idx
    ON cards (id)
    WHERE image_path IS NULL AND generate = TRUE;
