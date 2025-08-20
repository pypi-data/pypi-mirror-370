# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""LocalSearch implementation."""
import json
import logging
import random
import time
from collections import defaultdict
from collections.abc import AsyncGenerator
from typing import Any, List

import tiktoken

from graphrag_ecolink.callbacks.query_callbacks import QueryCallbacks
from graphrag_ecolink.config.models.graph_rag_config import GraphRagConfig
from graphrag_ecolink.data_model.community import Community
from graphrag_ecolink.data_model.entity import Entity
from graphrag_ecolink.data_model.relationship import Relationship
from graphrag_ecolink.data_model.text_unit import TextUnit
from graphrag_ecolink.db import Neo4jRAGClient
from graphrag_ecolink.language_model.protocol.base import ChatModel
from graphrag_ecolink.prompts.query.local_search_system_prompt import (
    LOCAL_SEARCH_SYSTEM_PROMPT,
)
from graphrag_ecolink.query.context_builder.builders import LocalContextBuilder
from graphrag_ecolink.query.context_builder.conversation_history import (
    ConversationHistory,
)
from graphrag_ecolink.query.llm.text_utils import num_tokens
from graphrag_ecolink.query.structured_search.base import BaseSearch, SearchResult

log = logging.getLogger(__name__)


class LocalSearch(BaseSearch[LocalContextBuilder]):
    """Search orchestration for local search mode."""

    def __init__(
        self,
        model: ChatModel,
        context_builder: LocalContextBuilder,
        token_encoder: tiktoken.Encoding | None = None,
        system_prompt: str | None = None,
        response_type: str = "multiple paragraphs",
        callbacks: list[QueryCallbacks] | None = None,
        model_params: dict[str, Any] | None = None,
        context_builder_params: dict | None = None,
    ):
        super().__init__(
            model=model,
            context_builder=context_builder,
            token_encoder=token_encoder,
            model_params=model_params,
            context_builder_params=context_builder_params or {},
        )
        self.system_prompt = system_prompt or LOCAL_SEARCH_SYSTEM_PROMPT
        self.callbacks = callbacks or []
        self.response_type = response_type

    async def search(
        self,
        query: str,
        conversation_history: ConversationHistory | None = None,
        **kwargs,
    ) -> SearchResult:
        """Build local search context that fits a single context window and generate answer for the user query."""
        start_time = time.time()
        search_prompt = ""
        llm_calls, prompt_tokens, output_tokens = {}, {}, {}
        context_result = self.context_builder.build_context(
            query=query,
            conversation_history=conversation_history,
            **kwargs,
            **self.context_builder_params,
        )
        llm_calls["build_context"] = context_result.llm_calls
        prompt_tokens["build_context"] = context_result.prompt_tokens
        output_tokens["build_context"] = context_result.output_tokens

        log.info("GENERATE ANSWER: %s. QUERY: %s", start_time, query)
        try:
            if "drift_query" in kwargs:
                drift_query = kwargs["drift_query"]
                search_prompt = self.system_prompt.format(
                    context_data=context_result.context_chunks,
                    response_type=self.response_type,
                    global_query=drift_query,
                )
            else:
                search_prompt = self.system_prompt.format(
                    context_data=context_result.context_chunks,
                    response_type=self.response_type,
                )
            history_messages = [
                {"role": "system", "content": search_prompt},
            ]

            full_response = ""

            async for response in self.model.achat_stream(
                prompt=query,
                history=history_messages,
                model_parameters=self.model_params,
            ):
                full_response += response
                for callback in self.callbacks:
                    callback.on_llm_new_token(response)

            llm_calls["response"] = 1
            prompt_tokens["response"] = num_tokens(search_prompt, self.token_encoder)
            output_tokens["response"] = num_tokens(full_response, self.token_encoder)

            for callback in self.callbacks:
                callback.on_context(context_result.context_records)

            return SearchResult(
                response=full_response,
                context_data=context_result.context_records,
                context_text=context_result.context_chunks,
                completion_time=time.time() - start_time,
                llm_calls=sum(llm_calls.values()),
                prompt_tokens=sum(prompt_tokens.values()),
                output_tokens=sum(output_tokens.values()),
                llm_calls_categories=llm_calls,
                prompt_tokens_categories=prompt_tokens,
                output_tokens_categories=output_tokens,
            )

        except Exception:
            log.exception("Exception in _asearch")
            return SearchResult(
                response="",
                context_data=context_result.context_records,
                context_text=context_result.context_chunks,
                completion_time=time.time() - start_time,
                llm_calls=1,
                prompt_tokens=num_tokens(search_prompt, self.token_encoder),
                output_tokens=0,
            )

    async def stream_search(
        self,
        query: str,
        conversation_history: ConversationHistory | None = None,
    ) -> AsyncGenerator:
        """Build local search context that fits a single context window and generate answer for the user query."""
        start_time = time.time()

        context_result = self.context_builder.build_context(
            query=query,
            conversation_history=conversation_history,
            **self.context_builder_params,
        )
        log.info("GENERATE ANSWER: %s. QUERY: %s", start_time, query)

        search_prompt = self.system_prompt.format(
            context_data=context_result.context_chunks, response_type=self.response_type
        )
        history_messages = [
            {"role": "system", "content": search_prompt},
        ]

        for callback in self.callbacks:
            callback.on_context(context_result.context_records)

        async for response in self.model.achat_stream(
            prompt=query,
            history=history_messages,
            model_parameters=self.model_params,
        ):
            for callback in self.callbacks:
                callback.on_llm_new_token(response)
            yield response


    async def stream_search_for_ecolink(
        self,
        query: str,
        config:GraphRagConfig = None
    ):
        model_settings = config.get_language_model_config(config.local_search.chat_model_id)
        token_encoder = tiktoken.get_encoding(model_settings.encoding_model)

        # 根据实体的描述和query，向量查询，取2*10的结果，去掉比如0分的数据
        client = Neo4jRAGClient.instance()
        result = client.query_vector(query, top_k=10, index_name="entity_title_desc_index")
        # 数据结构：[{'content': {'id': 'ce9b486b-0f8b-4091-8c9e-4af50fdb0baa', 'title': '深龋近髓', 'title_description_embedding': None, 'description': '', 'human_readable_id': 69}, 'score': 0.9698965549468994, 'neo4j_id': 131}, ...]
        entities_result = [item["content"] for item in result if item.get("content") is not None]
        for item in result:
            c = item["content"]
            print(f"向量查询:   [{c.get('title')}] ID: {c.get('id')} | Desc: {c.get('description')} | Score: {item.get('score')}")
        entity_list = [Entity(**item) for item in entities_result]

        # 关系，
        relationships_cypher = """
                    MATCH (e:__Entity__)
                    WHERE id(e) IN $ids
                    MATCH (e)-[r]-(related:__Entity__)
                    RETURN e.title AS source, type(r) AS rel_type, related.title AS target, e.id as id, e.human_readable_id as short_id,r.description AS description
                """
        entity_ids_for_neo4j = [item["neo4j_id"] for item in result if item.get("neo4j_id") is not None]
        related_entities = await client.run_query(relationships_cypher, {"ids": entity_ids_for_neo4j})

        relationship_list = [
            Relationship(**item) for item in related_entities
            if isinstance(item, dict)
        ]
        # 排序
        relationship_tokens = max(int(12000 * 0.35), 0)  # 这两个值是参考了源码的默认值，1-community-text
        sorted_relationships = self.sort_and_limit_relationships(selected_entities=entity_list,
                                                             relationships=relationship_list,
                                                             token_encoder=token_encoder,
                                                             max_context_tokens=relationship_tokens)

        # 社区（包含了社区报告）(entity_ids)
        related_titles = set()
        for rel in related_entities:
            if isinstance(rel, dict):
                related_titles.add(rel["source"])
                related_titles.add(rel["target"])
        # title_to_custom_id = {
        #     eval(item["content"]).get("title"): eval(item["content"]).get("id")
        #     for item in result
        #     if item.get("content")
        # }


        title_to_custom_id = {}
        for item in result:
            content = item.get("content")
            if not content:
                continue
            # 如果是字符串，尝试解析
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except Exception:
                    logging.warning(f"Failed to parse content: {content}")
            # 如果现在是 dict，就提取
            if isinstance(content, dict):
                title = content.get("title")
                id_ = content.get("id")
                if title and id_:
                    title_to_custom_id[title] = id_
        related_ids = [
            title_to_custom_id.get(title)
            for title in related_titles
            if title_to_custom_id.get(title)
        ]
        # entity_ids_from_result = [eval(item["content"]).get("id") for item in result if item.get("content")]

        entity_ids_from_result = []
        for item in result:
            content = item.get("content")
            if not content:
                continue
            # 如果是字符串，尝试解析为 dict
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except Exception:
                    logging.warning(f"Failed to parse content: {content}")

            # 如果已经是 dict 类型，直接提取
            if isinstance(content, dict):
                entity_id = content.get("id")
                if entity_id:
                    entity_ids_from_result.append(entity_id)

        all_custom_entity_ids = list(set(entity_ids_from_result + related_ids))
        community_cypher = """
                    MATCH (c:__Community__)
                    WHERE ANY(eid IN c.entity_ids WHERE eid IN $ids)
                    RETURN c
                """
        communities_result = await client.run_query(community_cypher, {"ids": all_custom_entity_ids})
        # 排序(匹配数量排序)
        community_tokens = max(int(12000 * 0.15), 0)  # 这两个值是参考了源码的默认值，如果有历史数据的话，8000要减去历史数据计算出来的token
        sorted_communities = self.sort_and_limit_community_reports(community_result=communities_result,
                                                                   token_encoder=token_encoder,
                                                                   max_context_tokens=community_tokens,
                                                                   entities=entities_result)
        # 切片(不用排序,按照实体排序即可),（假设entity已经和text_unit建立了关系）
        text_unit_cypher = """
                    WITH $ids AS entity_ids
                    MATCH (e:__Entity__)-[:IN_CHUNK]->(c:__Chunk__)
                    WHERE id(e) IN entity_ids
                    RETURN id(e) AS entity_id, e.title AS entity_title, c.id AS id, c.text AS text,c.human_readable_id AS short_id
                """
        text_unit_result = await client.run_query(text_unit_cypher, {"ids": entity_ids_for_neo4j})
        text_unit: list[TextUnit] = [TextUnit(**item) for item in text_unit_result]
        text_unit_tokens = max(int(12000 * 0.5), 0)  # 这两个值是参考了源码的默认值，如果有历史数据的话
        processed_text_units = self.build_text_unit_context(text_units=text_unit,
                                                        token_encoder=token_encoder,
                                                        max_context_tokens=text_unit_tokens)
        # token比例，切片=50%，社区=10%，实体和关系=40%? 目前看来，切片=50%，然后社区=15%，关系=35%

        # 筛选文本切片，仅保留 text 字段
        seen_texts = set()
        simplified_text_units = [
            {"text": unit["text"]}
            for unit in processed_text_units
            if unit.get("text") and not (unit["text"] in seen_texts or seen_texts.add(unit["text"]))
        ]
        # 筛选社区报告，仅保留 summary, full_content, title
        simplified_communities = [
            {
                "summary": c.get("summary"),
                "full_content": c.get("full_content"),
                "title": c.get("title"),
            }
            for item in sorted_communities
            if (c := item.get("c")) and (c.get("summary") or c.get("full_content") or c.get("title"))
        ]

        simplified_relationships = [
            {
                "source": rel.get("source"),
                "target": rel.get("target"),
                "description": rel.get("description")
            }
            for rel in sorted_relationships
            if rel.get("source") and rel.get("target") and rel.get("description")
        ]

        simplified_entity_list = [{"title": item.get("title"), "description": item.get("description")} for item in entities_result]

        # 把上面的的内容组装好，返回
        result_str = json.dumps({
            "实体": simplified_entity_list,
            "实体之间的关系": simplified_relationships,
            "社区和社区报告": simplified_communities,
            "文本切片": simplified_text_units
        }, ensure_ascii=False, indent=2)
        yield result_str

    def sort_and_limit_community_reports(
            self,
            community_result: List[dict],
            token_encoder: tiktoken.Encoding,
            max_context_tokens: int = 8000,
            weight_column: str = "occurrence weight",
            rank_column: str = "rank",
            random_state: int = 86,
            entities: List[dict] = None,
            normalize_weights: bool = True,
    ) -> List[dict]:
        """
        根据权重和排名对社区报告进行排序，并限制总 token 数量。

        Args:
            community_result: 社区报告字典列表。
            token_encoder: 用于计算 token 数量的编码器。
            max_context_tokens: 最大允许的 token 数量。
            weight_column: 权重列的名称。
            rank_column: 排名列的名称。
            random_state: 随机种子以确保结果可复现。
            entities: 用于计算权重的实体列表。
            normalize_weights: 是否对权重进行归一化。

        Returns:
            排序并限制 token 数量的社区报告列表。
        """
        # 确保随机性可复现
        random.seed(random_state)

        # 如果提供了实体，则计算权重
        if entities:
            community_text_units = {}
            for entity in entities:
                if "community_ids" in entity:
                    for community_id in entity["community_ids"]:
                        if community_id not in community_text_units:
                            community_text_units[community_id] = []
                        community_text_units[community_id].extend(entity.get("text_unit_ids", []))

            for report in community_result:
                report[weight_column] = len(set(community_text_units.get(report.get("id"), [])))

            # if normalize_weights:
            #     # 对权重进行归一化
            #     max_weight = max(report[weight_column] for report in community_result if weight_column in report)
            #     for report in community_result:
            #         if weight_column in report:
            #             report[weight_column] /= max_weight

            if normalize_weights:
                try:
                    max_weight = max(
                        report[weight_column]
                        for report in community_result
                        if weight_column in report and isinstance(report[weight_column], (int, float))
                    )

                    if max_weight > 0:
                        for report in community_result:
                            if weight_column in report and isinstance(report[weight_column], (int, float)):
                                report[weight_column] /= max_weight
                    else:
                        print("⚠️ 最大权重为 0，跳过归一化")

                except ValueError:
                    print("⚠️ 没有有效的权重字段，跳过归一化")

        # 按权重和排名降序排序
        community_result.sort(
            key=lambda x: (-x.get(weight_column, 0), -x.get(rank_column, 0))
        )

        # 初始化 token 计数和结果列表
        total_tokens = 0
        limited_reports = []

        for report in community_result:
            # 将报告转换为字符串并计算 token 数量
            report_text = f"{report.get('id', '')} {report.get('title', '')} {report.get('summary', '')}"
            report_tokens = len(token_encoder.encode(report_text))

            # 检查添加此报告是否会超出 token 限制
            if total_tokens + report_tokens > max_context_tokens:
                break

            # 将报告添加到结果中并更新 token 计数
            limited_reports.append(report)
            total_tokens += report_tokens

        return limited_reports

    def sort_and_limit_relationships(
            self,
            selected_entities: List[Entity],
            relationships: List[Relationship],
            token_encoder: tiktoken.Encoding,
            max_context_tokens: int = 8000,
            relationship_ranking_attribute: str = "rank",
            top_k_relationships: int = 10,
    ) -> List[dict]:
        """Sort relationships based on ranking attribute and limit total tokens."""
        # Filter in-network relationships
        in_network_relationships = [
            rel for rel in relationships
            if rel.source in [entity.title for entity in selected_entities]
               and rel.target in [entity.title for entity in selected_entities]
        ]

        # Filter out-of-network relationships
        out_network_relationships = [
            rel for rel in relationships
            if rel.source in [entity.title for entity in selected_entities]
               or rel.target in [entity.title for entity in selected_entities]
        ]

        # Prioritize mutual relationships in out-of-network relationships
        selected_entity_names = [entity.title for entity in selected_entities]
        out_network_entity_links = defaultdict(int)
        for rel in out_network_relationships:
            if rel.source not in selected_entity_names:
                out_network_entity_links[rel.source] += 1
            if rel.target not in selected_entity_names:
                out_network_entity_links[rel.target] += 1

        for rel in out_network_relationships:
            if rel.attributes is None:
                rel.attributes = {}
            rel.attributes["links"] = max(
                out_network_entity_links.get(rel.source, 0),
                out_network_entity_links.get(rel.target, 0),
            )

        # Sort out-of-network relationships by links and ranking attribute
        out_network_relationships.sort(
            key=lambda x: (
                x.attributes.get("links", 0),
                x.attributes.get(relationship_ranking_attribute, 0),
            ),
            reverse=True,
        )

        # Combine in-network and top-k out-of-network relationships
        relationship_budget = top_k_relationships * len(selected_entities)
        sorted_relationships = in_network_relationships + out_network_relationships[:relationship_budget]

        # Limit relationships by token count
        total_tokens = 0
        limited_relationships = []
        for rel in sorted_relationships:
            # Convert relationship to string and calculate token count
            rel_text = f"{rel.short_id} {rel.source} {rel.target} {rel.description}"
            rel_tokens = len(token_encoder.encode(rel_text))

            # Check if adding this relationship exceeds the token limit
            if total_tokens + rel_tokens > max_context_tokens:
                break

            limited_relationships.append(rel)
            total_tokens += rel_tokens

        return [rel.__dict__ for rel in limited_relationships]

    def build_text_unit_context(
            self,
            text_units: list[TextUnit],
            token_encoder: tiktoken.Encoding | None = None,
            max_context_tokens: int = 8000,
            sort_key: str = None,  # 可选排序字段
    ) -> list[dict]:
        """Prepare text-unit data table with optional sorting and token limitation."""
        if not text_units:
            return []

        # 如果指定了排序字段，则按该字段排序
        if sort_key:
            text_units.sort(key=lambda unit: getattr(unit, sort_key, 0), reverse=True)

        attribute_cols = (
            list(text_units[0].attributes.keys()) if text_units[0].attributes else []
        )
        result = []
        current_tokens = 0
        # 遍历文本单元并添加到上下文中，直到达到 token 限制
        for unit in text_units:
            row = {
                "id": unit.short_id,
                "text": unit.text,
                **{
                    field: str(unit.attributes.get(field, "")) if unit.attributes else ""
                    for field in attribute_cols
                },
            }
            row_text = "|".join([str(value) for value in row.values()]) + "\n"
            new_tokens = num_tokens(row_text, token_encoder)

            if current_tokens + new_tokens > max_context_tokens:
                break

            result.append(row)
            current_tokens += new_tokens

        return result