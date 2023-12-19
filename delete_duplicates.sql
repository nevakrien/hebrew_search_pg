WITH duplicates_to_delete AS (
    SELECT id
    FROM (
        SELECT id,
               ROW_NUMBER() OVER (
                   PARTITION BY document_id, generation_strategy_id, text, token_ids, embedding
                   ORDER BY id
               ) as rnum
        FROM snippets
    ) t
    WHERE t.rnum > 1
)
DELETE FROM snippets
WHERE id IN (SELECT id FROM duplicates_to_delete);
