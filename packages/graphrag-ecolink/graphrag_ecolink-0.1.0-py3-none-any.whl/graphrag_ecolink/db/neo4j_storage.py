import pandas as pd
import time

from graphrag_ecolink.db import Neo4jRAGClient
from neo4j import GraphDatabase
import os

from graphrag_ecolink.index.typing.user_info import PipelineUseInfo

NEO4J_URI = "bolt://localhost"  # or neo4j+s://xxxx.databases.neo4j.io
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password"  # your password
NEO4J_DATABASE = "neo4j"


# Create a Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
# 获取当前文件所在目录的绝对路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 构建 cypher_statements 目录的绝对路径
CYBER_DIR = os.path.join(CURRENT_DIR, "..", "cypher_statements")

def create_neo4j_constraint():
    statements = [
        "\ncreate constraint chunk_id if not exists for (c:__Chunk__) require c.id is unique",
        "\ncreate constraint document_id if not exists for (d:__Document__) require d.id is unique",
        "\ncreate constraint entity_id if not exists for (c:__Community__) require c.community is unique",
        "\ncreate constraint entity_id if not exists for (e:__Entity__) require e.id is unique",
        "\ncreate constraint entity_title if not exists for (e:__Entity__) require e.name is unique",
        "\ncreate constraint entity_title if not exists for (e:__Covariate__) require e.title is unique",
        "\ncreate constraint related_id if not exists for ()-[rel:RELATED]->() require rel.id is unique",
        "\n",
    ]

    for statement in statements:
        if len((statement or "").strip()) > 0:
            print(statement)
            driver.execute_query(statement)

async def write_table_2_neo4j(table: pd.DataFrame, table_name: str, user_info: PipelineUseInfo):
    """
    高性能版本：使用 UNWIND 批量写入 Neo4j。
    :param table: 要写入的数据表
    :param table_name: 表名（决定使用哪个 .cyp 文件）
    :param user_info: 用户信息对象
    """
    # 加载对应的 Cypher 脚本
    cypher_script = _get_cypher_script(table_name)
    with open(cypher_script, "r", encoding="utf-8") as f:
        cypher_query = f.read().strip()

    # 添加 user_info 到每行数据
    records = table.to_dict('records')
    if user_info:
        for row in records:
            row["tenant_id"] = user_info.tenant_id
            row["user_id"] = user_info.user_id
            row["biz_code"] = user_info.biz_code

    # 初始化 Neo4j 客户端
    client = Neo4jRAGClient.instance()

    # 执行批量事务
    await client.execute_transaction(lambda tx: tx.run(cypher_query, rows=records))


def _get_cypher_script(table_name: str) -> str:
    """
    根据表名获取对应的Cypher脚本路径。
    :param table_name: 表名
    :return: Cypher脚本路径
    """
    # 使用绝对路径来确保文件路径正确
    return os.path.join(CYBER_DIR, f"{table_name}.cyp")


async def write_table_to_neo4j(
        table: pd.DataFrame,
        name: str
) -> None:
    """
    直接对DataFrame执行批量导入（跳过文件读写步骤）

    参数:
        table: 要导入的Pandas DataFrame
        statement: Cypher导入语句
        batch_size: 每批次处理的行数
    """
    statement = get_statement(name)
    batched_import(statement, table)



def batched_import(statement, df, batch_size=1000):
    """
    Import a dataframe into Neo4j using a batched approach.

    Parameters: statement is the Cypher query to execute, df is the dataframe to import, and batch_size is the number of rows to import in each batch.
    """
    total = len(df)
    start_s = time.time()
    for start in range(0, total, batch_size):
        batch = df.iloc[start: min(start + batch_size, total)]
        result = driver.execute_query(
            "UNWIND $rows AS value " + statement,
            rows=batch.to_dict("records"),
            database_=NEO4J_DATABASE,
        )
        print(result.summary.counters)
    print(f"{total} rows in {time.time() - start_s} s.")
    return total



def get_statement(name: str) -> str:
    """
    从 cypher_statements 目录加载指定名称的 Cypher 语句。
    参数:
        name (str): parquet 文件名前缀，如 'documents', 'entities' 等。
    返回:
        str: 对应的 Cypher 插入语句。
    """
    # 获取当前文件所在目录
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    CYBER_DIR = os.path.join(CURRENT_DIR, "..", "cypher_statements")
    filename = os.path.join(CYBER_DIR, f"{name}.cyp")

    if not os.path.exists(filename):
        raise FileNotFoundError(f"No Cypher statement found for '{name}' (expected file: {filename})")

    with open(filename, "r", encoding="utf-8") as f:
        statement = f.read().strip()

    return statement

def create_indexes_from_file(file_name: str):
    """
    从指定路径读取 Cypher 索引创建文件并逐条执行。

    参数:
        index_file_path (str): create_index.cyp 文件的完整路径
    """
        # 使用默认路径（相对于当前文件）

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    CYBER_DIR = os.path.join(CURRENT_DIR, "..", "cypher_statements")
    index_file_path = os.path.join(CYBER_DIR, f"{file_name}.cyp")

    if not os.path.exists(index_file_path):
        raise FileNotFoundError(f"Index file not found: {index_file_path}")

    with open(index_file_path, 'r', encoding='utf-8') as f:
        cypher_statements = f.read().strip().split(';')

    print(f"Found {len(cypher_statements)} index statements. Executing...")

    executed = 0
    for stmt in cypher_statements:
        clean_stmt = stmt.strip()
        if not clean_stmt:
            continue

        try:
            result = driver.execute_query(
                clean_stmt,
                database_=NEO4J_DATABASE
            )
            print(f"Executed: {clean_stmt[:60]}... | Records affected: {result.summary.counters._contains_updates}")
            executed += 1
        except Exception as e:
            print(f"Failed to execute statement:\n{clean_stmt}\nError: {e}")

    print(f"Successfully executed {executed} out of {len(cypher_statements)} index statements.")



