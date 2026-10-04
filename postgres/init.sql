-- Provision pg_jieba for future Chinese full-text search.
-- The current search path is ILIKE on title (see article_service); nothing
-- consumes jiebacfg yet. If the extension is unavailable we just skip it.
DO $$
BEGIN
    BEGIN
        CREATE EXTENSION IF NOT EXISTS pg_jieba;
        RAISE NOTICE 'pg_jieba extension loaded';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'pg_jieba not available, using simple text search config';
    END;
END $$;
