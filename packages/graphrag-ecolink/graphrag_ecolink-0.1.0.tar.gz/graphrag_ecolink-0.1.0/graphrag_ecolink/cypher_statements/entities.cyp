UNWIND $rows AS row
MERGE (e:__Entity__ {id: row.id})
SET e.human_readable_id = row.human_readable_id,
    e.description = row.description,
    e.title = row.title,
    e.text_unit_ids = row.text_unit_ids,
    e.title_description_embedding = row.title_description_embedding,
    e.tenant_id = row.tenant_id,
    e.user_id = row.user_id,
    e.biz_code = row.biz_code

WITH e, row
UNWIND row.text_unit_ids AS text_unit
MATCH (c:__Chunk__ {id:text_unit})
MERGE (e)-[:IN_CHUNK]->(c)

WITH e, row
CALL apoc.create.addLabels(e,
    CASE
        WHEN coalesce(row.type, '') = '' THEN []
        ELSE [apoc.text.upperCamelCase(row.type)]
    END
) YIELD node

RETURN count(DISTINCT e) AS createdEntities
