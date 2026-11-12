-- Full-text search index for lexical searches on chunks.raw_text.
CREATE INDEX IF NOT EXISTS chunks_raw_text_fts_idx
ON chunks
USING gin (to_tsvector('english', coalesce(raw_text, '')));

-- Optional: refresh planner statistics after creating the index.
ANALYZE chunks;
