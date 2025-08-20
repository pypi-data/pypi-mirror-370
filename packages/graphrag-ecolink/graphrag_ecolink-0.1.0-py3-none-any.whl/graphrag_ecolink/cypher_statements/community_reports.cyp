UNWIND $rows AS row
MERGE (c:__Community__ {community: row.community})
SET c.level = row.level,
    c.title = row.title,
    c.rank = row.rank,
    c.rating_explanation = row.rating_explanation,
    c.full_content = row.full_content,
    c.summary = row.summary,
    c.title_embedding = row.title_embedding,
    c.summary_embedding = row.summary_embedding,
    c.full_content_embedding = row.full_content_embedding,
    c.tenant_id = row.tenant_id,
    c.user_id = row.user_id,
    c.biz_code = row.biz_code

// 处理 parent 层级关系
WITH c, row
WHERE row.parent IS NOT NULL AND toString(row.parent) <> "-1"
MERGE (p:__Community__ {community: row.parent})
MERGE (c)-[:HAS_PARENT]->(p)

// 处理 findings 列表（假设为 [{id: ..., content: ...}, ...]）
WITH c, row
UNWIND range(0, size(row.findings) - 1) AS idx
WITH c, row, row.findings[idx] AS finding, idx
MERGE (f:Finding {composite_id: c.community + "_" + idx})
SET f += finding
MERGE (c)-[:HAS_FINDING]->(f)


RETURN count(DISTINCT c) AS createdReports
