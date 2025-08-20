UNWIND $rows AS row
MERGE (c:__Chunk__ {id: row.id})
SET c.text = row.text,
    c.n_tokens = row.n_tokens,
    c.text_embedding = row.text_embedding,
    c.tenant_id = row.tenant_id,
    c.user_id = row.user_id,
    c.biz_code = row.biz_code

WITH c, row
UNWIND row.document_ids AS document_id
MATCH (d:__Document__ {id: document_id})
MERGE (c)-[:PART_OF]->(d)

RETURN count(DISTINCT c) AS createdTextUnits
