SELECT
    COUNT(*) as duplicate_sets,
    SUM(duplicate_count) as total_duplicates
FROM (
    SELECT
        COUNT(*) as duplicate_count
    FROM
        snippets
    GROUP BY
        document_id, generation_strategy_id, text, token_ids, embedding
    HAVING
        COUNT(*) > 1
) AS subquery;
