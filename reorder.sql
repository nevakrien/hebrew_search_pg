ALTER SEQUENCE snippets_id_seq RESTART WITH 1;

UPDATE snippets
SET id = DEFAULT
RETURNING id;

REINDEX INDEX idx_generation_strategy;
