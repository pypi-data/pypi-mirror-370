import re
from pathlib import Path
from neo4j import AsyncGraphDatabase, GraphDatabase
from neo4j.graph import Node, Relationship
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings
from neo4j_graphrag.llm import OpenAILLM
import threading


from graphrag_ecolink.config.defaults import DEFAULT_EMBEDDING_MODEL_ID, DEFAULT_CHAT_MODEL_ID
from graphrag_ecolink.config.load_config import load_config


class Neo4jRAGClient:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        # 这里到时候可以优化一下，从环境变量或者配置文件中读取 Neo4j 的连接信息: 同步驱动更简单，适合一般项目；异步驱动更灵活、可扩展，适合高并发/异步框架（如 FastAPI、aiohttp）。
        self.driver = AsyncGraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        self.sync_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        # 从 settings 文件中初始化 embedder（这里后面也可以优化一下，从环境变量里面读取）
        # root_dir = Path("/Users/lvshuai/PycharmProjects/graphrag-khoj/ragtest")
        # 获取当前文件所在目录
        current_file_path = Path(__file__)
        # 设置项目根目录为当前文件的上三级目录（可根据实际结构调整）
        root_dir = current_file_path.parent.parent.parent
        # 构造配置文件路径
        config_filepath = root_dir / "ragtest" / "settings.yaml"

        # 加载配置
        config = load_config(root_dir=root_dir, config_filepath=config_filepath)
        # 使用方法读取模型配置
        embedder_config = config.get_language_model_config(DEFAULT_EMBEDDING_MODEL_ID)
        llm_config = config.get_language_model_config(DEFAULT_CHAT_MODEL_ID)

        self.embedder = OpenAIEmbeddings(model=embedder_config.model, api_key=embedder_config.api_key, base_url=embedder_config.api_base)
        # 从 settings 文件中初始化 llm
        self.llm = OpenAILLM(
            model_name=llm_config.model,
            api_key=llm_config.api_key,
            base_url=llm_config.api_base,
            model_params={
                "max_tokens": llm_config.max_tokens or 2000,
                "response_format": None,
                "temperature": llm_config.temperature or 0
            }
        )

    @classmethod
    def instance(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = cls()
        return cls._instance

    async def execute_transaction(self, transaction_function, *args, **kwargs):
        """
        执行一个异步事务函数。
        :param transaction_function: 接受一个 AsyncTransaction 对象的函数
        """
        async with self.driver.session() as session:
            return await session.execute_write(transaction_function, *args, **kwargs)

    def get_rag_by_index(self, index_name: str) -> VectorRetriever:
        return VectorRetriever(self.sync_driver, index_name, self.embedder)

    async def _run_query(self, cypher: str, parameters: dict = None) -> list[dict]:
        try:
            """实例方法：执行 Cypher 查询"""
            result  = await self.driver.execute_query(cypher, parameters,database="neo4j")
            records = result.records
            parsed = []
            for record in records:
                row = {}
                for key, value in record.items():
                    if isinstance(value, (Node, Relationship)):
                        row[key] = dict(value)  # 只保留属性
                    else:
                        row[key] = value  # 其他类型直接返回
                parsed.append(row)
            print(f"[DEBUG] Fetched {len(parsed)} records from Neo4j")
            return parsed

        except Exception as e:
            print(f"[ERROR] Cypher query failed: {e}")
            return []

        # for record in records:
        #     node = record.get("n")
        #     if isinstance(node, Node):
        #         parsed.append(dict(node))  # 把 Node 转成 dict（只保留属性）
        #     else:
        #         parsed.append(node)  # fallback
        # print(f"[DEBUG] Fetched {len(parsed)} nodes from Neo4j")
        # return parsed

    @classmethod
    async def run_query(cls, cypher: str, parameters: dict = None) -> list[dict]:
        """类方法：获取实例后执行查询"""
        print(f"Running query: {cypher} with parameters: {parameters}")
        records = await cls.instance()._run_query(cypher, parameters)
        return records

    def query_vector(self, query: str, top_k: int = 10, index_name: str = "entity_title_desc_index"):
        rag = self.get_rag_by_index(index_name)
        results = rag.search(query_text=query, top_k=top_k*2)
        # 拿到 items 列表
        items = results.items

        # 按 score 降序排序
        sorted_results = sorted(
            items,
            key=lambda x: x.metadata.get("score", float("inf")),
            reverse=True
        )

        # 添加 score 筛选
        # filtered_results = [
        #     x for x in sorted_results
        #     if x.metadata.get("score", float("inf")) >= 0.82
        # ]

        def extract_node_id(node_id_str):
            # 例如 '4:00fae040-c4de-492d-b684-0da745925a76:4679' 提取最后一个冒号后的数值
            match = re.search(r":(\d+)$", node_id_str)
            return int(match.group(1)) if match else None

        # 解析 content（是 str 类型，需要转成 dict）
        return [
            {
                "content": eval(x.content),  # 或用 json.loads(x.content)（更安全）
                "score": x.metadata.get("score"),
                "neo4j_id": extract_node_id(x.metadata.get("id", ""))
            }
            for x in sorted_results[:top_k]
        ]

    def close(self):
        self.driver.close()