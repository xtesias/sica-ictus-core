-- Install pgvector for embeddings (used from Phase 4 onward)
CREATE EXTENSION IF NOT EXISTS vector;

-- pgcrypto provides gen_random_uuid() for UUID primary keys
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Verify extensions installed correctly
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        RAISE EXCEPTION 'pgvector extension failed to install';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
        RAISE EXCEPTION 'pgcrypto extension failed to install';
    END IF;
    RAISE NOTICE 'Extensions installed: vector, pgcrypto';
END $$;