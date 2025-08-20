UNWIND $rows AS row
MERGE (c:__Community__ {community: row.community})
SET c.level = row.level,
    c.title = row.title,
    c.tenant_id = row.tenant_id,
    c.user_id = row.user_id,
    c.biz_code = row.biz_code,
    c.entity_ids=row.entity_ids

WITH c, row
UNWIND row.relationship_ids AS rel_id
MATCH (start:__Entity__)-[:RELATED {id: rel_id}]->(end:__Entity__)
MERGE (start)-[:IN_COMMUNITY]->(c)
MERGE (end)-[:IN_COMMUNITY]->(c)

RETURN count(DISTINCT c) AS createdCommunities
