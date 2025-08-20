from graphrag_ecolink.db.neo4j_connector import Neo4jRAGClient


# 测试代码
# def insert_text_with_embedding(self, node_id: str, text: str):
    # 1. 生成文本向量
    # embedding = self.embedder.embed(text)
    #
    # # 2. 插入到 Neo4j
    # cypher = """
    # CREATE (n:Document {id: $id, content: $content, vector: $vector})
    # """
    # with self.driver.session() as session:
    #     session.run(cypher, id=node_id, content=text, vector=embedding)
    #     print(f"✅ 成功插入节点 {node_id}，文本为: {text}")




# if __name__ == "__main__":
#     client = Neo4jRAGClient.instance()

    # 示例文本
    # test_text = "什么是 GraphRAG?"
    # node_id = "doc_002"

    # 插入数据
    # client.insert_text_with_embedding(node_id=node_id, text=test_text)
    # 删除数据
    # client.delete_node_by_id(node_id="node_id")

    # 可选：查询回答
    # result = client.query_vector("红烧肉", top_k=2, index_name="index_4f994e4")
    # print("Answer:\n", result)

    # client.close()

