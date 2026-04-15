-- Full-text search support
-- If pg_jieba is available, use jiebacfg; otherwise fall back to simple config
DO $$
BEGIN
    BEGIN
        CREATE EXTENSION IF NOT EXISTS pg_jieba;
        RAISE NOTICE 'pg_jieba extension loaded';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'pg_jieba not available, using simple text search config';
    END;
END $$;
