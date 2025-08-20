# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Storage functions for the GraphRAG run module."""

import logging
from io import BytesIO
from typing import cast
import pandas as pd

from graphrag_ecolink.db.neo4j_connector import Neo4jRAGClient
from graphrag_ecolink.storage.pipeline_storage import PipelineStorage

log = logging.getLogger(__name__)


async def load_table_from_storage(name: str, storage: PipelineStorage) -> pd.DataFrame:
    """Load a parquet from the storage instance."""
    filename = f"{name}.parquet"
    if not await storage.has(filename):
        msg = f"Could not find {filename} in storage!"
        raise ValueError(msg)
    try:
        log.info("reading table from storage: %s", filename)
        return pd.read_parquet(BytesIO(await storage.get(filename, as_bytes=True)))
    except Exception:
        log.exception("error loading table from storage: %s", filename)
        raise

async def load_table_from_neo4j(name: str) -> pd.DataFrame:
    """从 Neo4j 中查询 {name} 节点数据，返回 DataFrame。"""
    # 构造标签名（必须是字母数字，避免注入风险）
    if not name.isidentifier():
        raise ValueError("非法的标签名")

    # 拼接 Cypher 查询字符串
    query = f"MATCH (n:`{name}`) RETURN n"
    query_literal = cast(str, query)
    records = await Neo4jRAGClient.run_query(query_literal)

    if not records:
        raise ValueError("No nodes found in Neo4j.")

    return pd.DataFrame(records)
async def load_table_from_file_path(file_path: str,file_name: str) -> pd.DataFrame:
    """Load a parquet file from the specified file path in storage."""
    try:
        file=file_path + "/" + file_name+".parquet"
        log.info("reading table from storage at path: %s", file)
        return pd.read_parquet(file)
    except Exception:
        log.exception("error loading table from storage at path: %s", file)
        raise

async def write_table_to_storage(
    table: pd.DataFrame, name: str, storage: PipelineStorage
) -> None:
    """Write a table to storage."""
    await storage.set(f"{name}.parquet", table.to_parquet())


async def delete_table_from_storage(name: str, storage: PipelineStorage) -> None:
    """Delete a table to storage."""
    await storage.delete(f"{name}.parquet")


async def storage_has_table(name: str, storage: PipelineStorage) -> bool:
    """Check if a table exists in storage."""
    return await storage.has(f"{name}.parquet")
