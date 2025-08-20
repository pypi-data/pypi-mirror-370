UNWIND $rows AS row
MATCH (source:__Entity__ {title: row.source})
MATCH (target:__Entity__ {title: row.target})
MERGE (source)-[rel:RELATED {id: row.id}]->(target)
SET rel.combined_degree = row.combined_degree,
    rel.weight = row.weight,
    rel.human_readable_id = row.human_readable_id,
    rel.description = row.description,
    rel.text_unit_ids = row.text_unit_ids,
    rel.description_embedding = row.description_embedding,
    rel.tenant_id = row.tenant_id,
    rel.user_id = row.user_id,
    rel.biz_code = row.biz_code

RETURN count(rel) AS createdRels
