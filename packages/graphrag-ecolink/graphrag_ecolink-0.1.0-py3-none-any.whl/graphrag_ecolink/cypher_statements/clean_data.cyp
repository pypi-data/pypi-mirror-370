// ========== 第一步：删除所有节点和关系 ==========
MATCH (n)
DETACH DELETE n;

// ========== 第二步：列出所有 VECTOR 类型索引 ==========

SHOW INDEXES
YIELD name, type
WHERE type = "VECTOR"
RETURN "DROP INDEX " + name + ";" AS drop_statement;
