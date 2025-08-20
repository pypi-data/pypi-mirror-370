# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""CLI implementation of the query subcommand."""

import asyncio
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import graphrag_ecolink.api as api
from graphrag_ecolink.callbacks.noop_query_callbacks import NoopQueryCallbacks
from graphrag_ecolink.config.load_config import load_config
from graphrag_ecolink.config.models.graph_rag_config import GraphRagConfig
from graphrag_ecolink.logger.print_progress import PrintProgressLogger
from graphrag_ecolink.utils.api import create_storage_from_config
from graphrag_ecolink.utils.storage import load_table_from_storage, storage_has_table

if TYPE_CHECKING:
    import pandas as pd

logger = PrintProgressLogger("")


def run_global_search(
    config_filepath: Path | None,
    data_dir: Path | None,
    root_dir: Path,
    community_level: int | None,
    dynamic_community_selection: bool,
    response_type: str,
    streaming: bool,
    query: str,
):
    """执行全局搜索。

    加载全局搜索所需的索引文件并调用查询 API。
    """
    root = root_dir.resolve()  # 解析根目录路径
    cli_overrides = {}
    if data_dir:
        cli_overrides["output.base_dir"] = str(data_dir)  # 设置输出目录
    config = load_config(root, config_filepath, cli_overrides)  # 加载配置文件

    dataframe_dict = _resolve_output_files(
        config=config,
        output_list=[
            "entities",  # 实体数据
            "communities",  # 社区数据
            "community_reports",  # 社区报告数据
        ],
        optional_list=[],  # 可选文件列表为空
    )

    # 调用多索引全局搜索 API
    if dataframe_dict["multi-index"]:
        final_entities_list = dataframe_dict["entities"]  # 实体列表
        final_communities_list = dataframe_dict["communities"]  # 社区列表
        final_community_reports_list = dataframe_dict["community_reports"]  # 社区报告列表
        index_names = dataframe_dict["index_names"]  # 索引名称

        logger.success(
            f"运行多索引全局搜索: {dataframe_dict['index_names']}"
        )

        # 调用多索引全局搜索 API
        response, context_data = asyncio.run(
            api.multi_index_global_search(
                config=config,
                entities_list=final_entities_list,
                communities_list=final_communities_list,
                community_reports_list=final_community_reports_list,
                index_names=index_names,
                community_level=community_level,  # 社区层级
                dynamic_community_selection=dynamic_community_selection,  # 动态社区选择
                response_type=response_type,  # 响应类型
                streaming=streaming,  # 是否流式处理
                query=query,  # 查询内容
            )
        )
        logger.success(f"全局搜索响应:\n{response}")
        # 注意：返回响应和上下文数据仅用于完整展示 API 的功能。
        # 外部用户应直接使用 API 获取响应和上下文数据。
        return response, context_data

    # 否则，调用单索引全局搜索 API
    final_entities: pd.DataFrame = dataframe_dict["entities"]  # 实体数据
    final_communities: pd.DataFrame = dataframe_dict["communities"]  # 社区数据
    final_community_reports: pd.DataFrame = dataframe_dict["community_reports"]  # 社区报告数据

    if streaming:

        async def run_streaming_search():
            full_response = ""  # 完整响应
            context_data = {}  # 上下文数据

            def on_context(context: Any) -> None:
                nonlocal context_data
                context_data = context  # 更新上下文数据

            callbacks = NoopQueryCallbacks()
            callbacks.on_context = on_context  # 设置上下文回调

            # 调用流式全局搜索 API
            async for stream_chunk in api.global_search_streaming(
                config=config,
                entities=final_entities,
                communities=final_communities,
                community_reports=final_community_reports,
                community_level=community_level,
                dynamic_community_selection=dynamic_community_selection,
                response_type=response_type,
                query=query,
                callbacks=[callbacks],
            ):
                full_response += stream_chunk  # 拼接流式响应
                print(stream_chunk, end="")  # 实时输出流式响应
                sys.stdout.flush()  # 刷新输出缓冲区
            print()  # 输出换行符
            return full_response, context_data

        return asyncio.run(run_streaming_search())
    # 非流式处理
    response, context_data = asyncio.run(
        api.global_search(
            config=config,
            entities=final_entities,
            communities=final_communities,
            community_reports=final_community_reports,
            community_level=community_level,
            dynamic_community_selection=dynamic_community_selection,
            response_type=response_type,
            query=query,
        )
    )
    logger.success(f"全局搜索响应:\n{response}")
    # 注意：返回响应和上下文数据仅用于完整展示 API 的功能。
    # 外部用户应直接使用 API 获取响应和上下文数据。
    return response, context_data


def run_local_search(
    config_filepath: Path | None,
    data_dir: Path | None,
    root_dir: Path,
    community_level: int,
    response_type: str,
    streaming: bool,
    query: str,
):
    """Perform a local search with a given query.

    Loads index files required for local search and calls the Query API.
    """
    root = root_dir.resolve()
    cli_overrides = {}
    if data_dir:
        cli_overrides["output.base_dir"] = str(data_dir)
    config = load_config(root, config_filepath, cli_overrides)

    dataframe_dict = _resolve_output_files(
        config=config,
        output_list=[
            "communities",
            "community_reports",
            "text_units",
            "relationships",
            "entities",
        ],
        # optional_list=[
        #     "covariates",
        # ],
    )
    # Call the Multi-Index Local Search API
    if dataframe_dict["multi-index"]:
        final_entities_list = dataframe_dict["entities"]
        final_communities_list = dataframe_dict["communities"]
        final_community_reports_list = dataframe_dict["community_reports"]
        final_text_units_list = dataframe_dict["text_units"]
        final_relationships_list = dataframe_dict["relationships"]
        index_names = dataframe_dict["index_names"]

        logger.success(
            f"Running Multi-index Local Search: {dataframe_dict['index_names']}"
        )

        # If any covariates tables are missing from any index, set the covariates list to None
        if len(dataframe_dict["covariates"]) != dataframe_dict["num_indexes"]:
            final_covariates_list = None
        else:
            final_covariates_list = dataframe_dict["covariates"]

        response, context_data = asyncio.run(
            api.multi_index_local_search(
                config=config,
                entities_list=final_entities_list,
                communities_list=final_communities_list,
                community_reports_list=final_community_reports_list,
                text_units_list=final_text_units_list,
                relationships_list=final_relationships_list,
                covariates_list=final_covariates_list,
                index_names=index_names,
                community_level=community_level,
                response_type=response_type,
                streaming=streaming,
                query=query,
            )
        )
        logger.success(f"Local Search Response:\n{response}")
        # NOTE: we return the response and context data here purely as a complete demonstration of the API.
        # External users should use the API directly to get the response and context data.
        return response, context_data

    # Otherwise, call the Single-Index Local Search API
    final_communities: pd.DataFrame = dataframe_dict["communities"]
    final_community_reports: pd.DataFrame = dataframe_dict["community_reports"]
    final_text_units: pd.DataFrame = dataframe_dict["text_units"]
    final_relationships: pd.DataFrame = dataframe_dict["relationships"]
    final_entities: pd.DataFrame = dataframe_dict["entities"]
    # final_covariates: pd.DataFrame | None = dataframe_dict["covariates"]
    final_covariates: pd.DataFrame | None = None

    if streaming:

        async def run_streaming_search():
            full_response = ""
            context_data = {}

            def on_context(context: Any) -> None:
                nonlocal context_data
                context_data = context

            callbacks = NoopQueryCallbacks()
            callbacks.on_context = on_context

            async for stream_chunk in api.local_search_streaming(
                config=config,
                # entities=final_entities,
                # communities=final_communities,
                # community_reports=final_community_reports,
                # text_units=final_text_units,
                # relationships=final_relationships,
                # covariates=final_covariates,
                # community_level=community_level,
                # response_type=response_type,
                query=query,
                # callbacks=[callbacks],
            ):
                full_response += stream_chunk
                print(stream_chunk, end="")  # noqa: T201
                sys.stdout.flush()  # flush output buffer to display text immediately
            print()  # noqa: T201
            return full_response, context_data

        return asyncio.run(run_streaming_search())
    # not streaming
    response, context_data = asyncio.run(
        api.local_search(
            config=config,
            # entities=final_entities,
            # communities=final_communities,
            # community_reports=final_community_reports,
            # text_units=final_text_units,
            # relationships=final_relationships,
            # covariates=final_covariates,
            # community_level=community_level,
            # response_type=response_type,
            query=query,
        )
    )
    logger.success(f"Local Search Response:\n{response}")
    # NOTE: we return the response and context data here purely as a complete demonstration of the API.
    # External users should use the API directly to get the response and context data.
    return response, context_data


def run_drift_search(
    config_filepath: Path | None,
    data_dir: Path | None,
    root_dir: Path,
    community_level: int,
    response_type: str,
    streaming: bool,
    query: str,
):
    """Perform a local search with a given query.

    Loads index files required for local search and calls the Query API.
    """
    root = root_dir.resolve()
    cli_overrides = {}
    if data_dir:
        cli_overrides["output.base_dir"] = str(data_dir)
    config = load_config(root, config_filepath, cli_overrides)

    dataframe_dict = _resolve_output_files(
        config=config,
        output_list=[
            "communities",
            "community_reports",
            "text_units",
            "relationships",
            "entities",
        ],
    )

    # Call the Multi-Index Drift Search API
    if dataframe_dict["multi-index"]:
        final_entities_list = dataframe_dict["entities"]
        final_communities_list = dataframe_dict["communities"]
        final_community_reports_list = dataframe_dict["community_reports"]
        final_text_units_list = dataframe_dict["text_units"]
        final_relationships_list = dataframe_dict["relationships"]
        index_names = dataframe_dict["index_names"]

        logger.success(
            f"Running Multi-index Drift Search: {dataframe_dict['index_names']}"
        )

        response, context_data = asyncio.run(
            api.multi_index_drift_search(
                config=config,
                entities_list=final_entities_list,
                communities_list=final_communities_list,
                community_reports_list=final_community_reports_list,
                text_units_list=final_text_units_list,
                relationships_list=final_relationships_list,
                index_names=index_names,
                community_level=community_level,
                response_type=response_type,
                streaming=streaming,
                query=query,
            )
        )
        logger.success(f"DRIFT Search Response:\n{response}")
        # NOTE: we return the response and context data here purely as a complete demonstration of the API.
        # External users should use the API directly to get the response and context data.
        return response, context_data

    # Otherwise, call the Single-Index Drift Search API
    final_communities: pd.DataFrame = dataframe_dict["communities"]
    final_community_reports: pd.DataFrame = dataframe_dict["community_reports"]
    final_text_units: pd.DataFrame = dataframe_dict["text_units"]
    final_relationships: pd.DataFrame = dataframe_dict["relationships"]
    final_entities: pd.DataFrame = dataframe_dict["entities"]

    if streaming:

        async def run_streaming_search():
            full_response = ""
            context_data = {}

            def on_context(context: Any) -> None:
                nonlocal context_data
                context_data = context

            callbacks = NoopQueryCallbacks()
            callbacks.on_context = on_context

            async for stream_chunk in api.drift_search_streaming(
                config=config,
                entities=final_entities,
                communities=final_communities,
                community_reports=final_community_reports,
                text_units=final_text_units,
                relationships=final_relationships,
                community_level=community_level,
                response_type=response_type,
                query=query,
                callbacks=[callbacks],
            ):
                full_response += stream_chunk
                print(stream_chunk, end="")  # noqa: T201
                sys.stdout.flush()  # flush output buffer to display text immediately
            print()  # noqa: T201
            return full_response, context_data

        return asyncio.run(run_streaming_search())

    # not streaming
    response, context_data = asyncio.run(
        api.drift_search(
            config=config,
            entities=final_entities,
            communities=final_communities,
            community_reports=final_community_reports,
            text_units=final_text_units,
            relationships=final_relationships,
            community_level=community_level,
            response_type=response_type,
            query=query,
        )
    )
    logger.success(f"DRIFT Search Response:\n{response}")
    # NOTE: we return the response and context data here purely as a complete demonstration of the API.
    # External users should use the API directly to get the response and context data.
    return response, context_data


def run_basic_search(
    config_filepath: Path | None,
    data_dir: Path | None,
    root_dir: Path,
    streaming: bool,
    query: str,
):
    """Perform a basics search with a given query.

    Loads index files required for basic search and calls the Query API.
    """
    root = root_dir.resolve()
    cli_overrides = {}
    if data_dir:
        cli_overrides["output.base_dir"] = str(data_dir)
    config = load_config(root, config_filepath, cli_overrides)

    dataframe_dict = _resolve_output_files(
        config=config,
        output_list=[
            "text_units",
        ],
    )

    # Call the Multi-Index Basic Search API
    if dataframe_dict["multi-index"]:
        final_text_units_list = dataframe_dict["text_units"]
        index_names = dataframe_dict["index_names"]

        logger.success(
            f"Running Multi-index Basic Search: {dataframe_dict['index_names']}"
        )

        response, context_data = asyncio.run(
            api.multi_index_basic_search(
                config=config,
                text_units_list=final_text_units_list,
                index_names=index_names,
                streaming=streaming,
                query=query,
            )
        )
        logger.success(f"Basic Search Response:\n{response}")
        # NOTE: we return the response and context data here purely as a complete demonstration of the API.
        # External users should use the API directly to get the response and context data.
        return response, context_data

    # Otherwise, call the Single-Index Basic Search API
    final_text_units: pd.DataFrame = dataframe_dict["text_units"]

    if streaming:

        async def run_streaming_search():
            full_response = ""
            context_data = {}

            def on_context(context: Any) -> None:
                nonlocal context_data
                context_data = context

            callbacks = NoopQueryCallbacks()
            callbacks.on_context = on_context

            async for stream_chunk in api.basic_search_streaming(
                config=config,
                text_units=final_text_units,
                query=query,
            ):
                full_response += stream_chunk
                print(stream_chunk, end="")  # noqa: T201
                sys.stdout.flush()  # flush output buffer to display text immediately
            print()  # noqa: T201
            return full_response, context_data

        return asyncio.run(run_streaming_search())
    # not streaming
    response, context_data = asyncio.run(
        api.basic_search(
            config=config,
            text_units=final_text_units,
            query=query,
        )
    )
    logger.success(f"Basic Search Response:\n{response}")
    # NOTE: we return the response and context data here purely as a complete demonstration of the API.
    # External users should use the API directly to get the response and context data.
    return response, context_data


def _resolve_output_files(
        config: GraphRagConfig,
        output_list: list[str],
        optional_list: list[str] | None = None,
    ) -> dict[str, Any]:
        """读取索引输出文件并返回一个包含数据框的字典。"""
        dataframe_dict = {}

        # 加载多索引搜索的输出文件
        if config.outputs:
            dataframe_dict["multi-index"] = True  # 标记为多索引
            dataframe_dict["num_indexes"] = len(config.outputs)  # 索引数量
            dataframe_dict["index_names"] = config.outputs.keys()  # 索引名称
            for output in config.outputs.values():
                storage_obj = create_storage_from_config(output)  # 创建存储对象
                for name in output_list:
                    if name not in dataframe_dict:
                        dataframe_dict[name] = []
                    # 异步加载表格数据
                    df_value = asyncio.run(
                        load_table_from_storage(name=name, storage=storage_obj)
                    )
                    dataframe_dict[name].append(df_value)

                # 对于可选输出文件，如果文件不存在则不添加
                if optional_list: # 这里暂时先不改，看了一下，目前应该没有这样的本地文件
                    for optional_file in optional_list:
                        if optional_file not in dataframe_dict:
                            dataframe_dict[optional_file] = []
                        file_exists = asyncio.run(
                            storage_has_table(optional_file, storage_obj)
                        )
                        if file_exists:
                            df_value = asyncio.run(
                                load_table_from_storage(
                                    name=optional_file, storage=storage_obj
                                )
                            )
                            dataframe_dict[optional_file].append(df_value)
            return dataframe_dict

        # 加载单索引搜索的输出文件
        dataframe_dict["multi-index"] = False  # 标记为单索引
        storage_obj = create_storage_from_config(config.output)  # 创建存储对象
        for name in output_list:
            # 异步加载表格数据
            df_value = asyncio.run(load_table_from_storage(name=name, storage=storage_obj))
            dataframe_dict[name] = df_value

        # 对于可选输出文件，如果文件不存在则设置为 None
        if optional_list: # 这里暂时先不改，看了一下，目前应该没有这样的本地文件
            for optional_file in optional_list:
                file_exists = asyncio.run(storage_has_table(optional_file, storage_obj))
                if file_exists:
                    df_value = asyncio.run(
                        load_table_from_storage(name=optional_file, storage=storage_obj)
                    )
                    dataframe_dict[optional_file] = df_value
        return dataframe_dict
