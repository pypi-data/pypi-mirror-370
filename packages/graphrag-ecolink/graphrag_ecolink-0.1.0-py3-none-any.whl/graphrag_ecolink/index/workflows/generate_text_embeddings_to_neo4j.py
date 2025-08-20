# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing run_workflow method definition."""

import logging

import numpy as np
import pandas as pd
import requests

from graphrag_ecolink.config.models.graph_rag_config import GraphRagConfig
from graphrag_ecolink.db.neo4j_storage import write_table_2_neo4j, create_neo4j_constraint, create_indexes_from_file
from graphrag_ecolink.index.typing.context import PipelineRunContext
from graphrag_ecolink.index.typing.workflow import WorkflowFunctionOutput
from graphrag_ecolink.utils.storage import (load_table_from_file_path,
                                            )

log = logging.getLogger(__name__)


async def run_workflow(
    config: GraphRagConfig,
    context: PipelineRunContext,
) -> WorkflowFunctionOutput:
    """All the steps to transform community reports."""
    data_dir = "../../../ragtest/output"  # 替换为你实际的 parquet 文件目录
    documents = await load_table_from_file_path(data_dir,"documents")
    relationships = await load_table_from_file_path(data_dir,"relationships")
    text_units = await load_table_from_file_path(data_dir,"text_units")
    entities = await load_table_from_file_path(data_dir,"entities")
    #entities额外增加一列数据，使用title:description两个字段拼接
    entities["title_description"] = entities["title"].fillna('') + ": " + entities["description"].fillna('')
    communities = await load_table_from_file_path(data_dir,"communities")
    community_reports = await load_table_from_file_path(data_dir,"community_reports")

    output = await generate_text_embeddings(
        documents=documents,
        relationships=relationships,
        text_units=text_units,
        entities=entities,
        communities=communities,
        community_reports=community_reports,
    )
    # 将.parquet文件写入neo4j
    create_neo4j_constraint
    for table_name, table in output.items():
        await write_table_2_neo4j(table, table_name,user_info=context.user_info)
        print(f"write_table_2_neo4j table: {table_name}")

    #创建索引
    create_indexes_from_file("create_index")
    return WorkflowFunctionOutput(result=output)



def extract_grouped_text_unit_ids(table: pd.DataFrame) -> pd.DataFrame:
    """
       将 table 中的 text_unit_ids（ndarray）列转换为原生 list，便于写入 Neo4j 或 JSON 序列化。
       """
    if "text_unit_ids" in table.columns:
        table["text_unit_ids"] = table["text_unit_ids"].apply(
            lambda x: x.tolist() if isinstance(x, np.ndarray) else x
        )
    return table


async def generate_text_embeddings(
    documents: pd.DataFrame | None,
    relationships: pd.DataFrame | None,
    text_units: pd.DataFrame | None,
    entities: pd.DataFrame | None,
    communities: pd.DataFrame | None,
    community_reports: pd.DataFrame | None,
) -> dict[str, pd.DataFrame]:

    outputs = {}

    # 定义每个 DataFrame 及其允许 embedding 的字段列表
    data_frames = [
        ("documents", documents, []),
        ("text_units", text_units, ["text"]),
        ("entities", entities, ["title_description"]),
        ("relationships", relationships, ["description"]),
        ("communities", communities, []),
        ("community_reports", community_reports, ["title","summary", "full_content"]),
    ]

    for name, df, allowed_fields in data_frames:
        if df is None:
            continue  # 跳过空的 DataFrame

        if not allowed_fields:  # 如果没有配置允许 embedding 的字段
            outputs[name] = df
            continue

        # 对所有在 allowed_fields 且存在于 df 中的字段进行 embedding
        field_list = [field for field in allowed_fields if field in df.columns]
        if field_list:
            df = await _run_embeddings(df, field_list)

        outputs[name] = df


    return outputs





async def _run_embeddings(
    data: pd.DataFrame,
    embed_columns: list[str],
) -> pd.DataFrame:
    """All the steps to generate single embedding."""
    for embed_column in embed_columns:
        print("embedding column: ", embed_column)
        data = await embed_custom_text(
            data=data,
            embed_column=embed_column,
            use_mock=False,
        )
    return data


"""对某一列的数据做向量生成,并赋值，如果数量不匹配，填充空list"""
async def embed_custom_text(
    data: pd.DataFrame,
    embed_column: str,
    use_mock: bool = False,
) -> pd.DataFrame:
    """
    根据输入数据生成文本嵌入，如果开启mock逻辑，则返回随机构造的文本向量。
    """
    if use_mock:
        import numpy as np
        mock_embedding = list(np.random.rand(10))  # 假设维度为10
        data[f"{embed_column}_embedding"] = [mock_embedding] * len(data)
        return data

    # 确保输入是字符串类型，并转成 Python 列表
    texts = data[embed_column].astype(str).tolist()

    # 获取嵌入结果
    embeddings = get_embedding_result(texts)

    # 检查是否成功获取嵌入且数量一致
    if embeddings and len(embeddings) == len(texts):
        data[f"{embed_column}_embedding"] = embeddings
    else:
        # 填充空列表占位
        data[f"{embed_column}_embedding"] = [[] for _ in range(len(data))]
        logging.warning("Embedding failed or length mismatch, filled with empty lists.")

    return data





def get_embedding_result(input_texts) -> list[list[float]] | None:
    """
    调用本地接口获取文本嵌入向量。

    :param input_texts: 可以是单个字符串，也可以是字符串列表。
    :return: 嵌入向量列表（每个元素对应一行），失败时返回 None 或空列表。
    """
    url = "http://192.168.1.5:11435/v1/embeddings"
    payload = {
        "input": input_texts,
        "model": "gte-small"
    }
    result=None
    try:

        response = requests.post(url, json=payload)
        response.raise_for_status()  # 检查 HTTP 错误
        result = response.json()
        # 提取 data 中的所有 embedding，并按 index 排序
        embeddings = [None] * len(result.get("data", []))
        for item in result["data"]:
            idx = item.get("index")
            if idx is not None and idx < len(embeddings):
                embeddings[idx] = item.get("embedding")
        return embeddings

    except requests.exceptions.RequestException as e:
        logging.exception("embeddings调用结束, input: %s, result: %s, error: %s", input_texts, result, str(e))
        return None

    except (KeyError, IndexError, TypeError) as e:
        logging.exception("embeddings调用结束, input: %s, result: %s, error: %s", input_texts, result, str(e))
        return None

# 示例调用



