-- The chunk image queue now uses chunks.card_path directly.
DROP TABLE IF EXISTS memory_card;

ALTER TABLE chunks
    ADD COLUMN IF NOT EXISTS generate BOOLEAN NOT NULL DEFAULT TRUE;
