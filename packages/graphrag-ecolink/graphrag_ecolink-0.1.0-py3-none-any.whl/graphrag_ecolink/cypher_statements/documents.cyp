UNWIND $rows AS row
MERGE (d:__Document__ {id: row.id})
SET d.title = row.title,
    d.tenant_id = row.tenant_id,
    d.user_id = row.user_id,
    d.biz_code = row.biz_code
RETURN count(d) AS createdDocuments
