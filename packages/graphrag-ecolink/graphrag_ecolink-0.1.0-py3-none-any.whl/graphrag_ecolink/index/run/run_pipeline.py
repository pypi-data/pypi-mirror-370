# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Different methods to run the pipeline."""

import json
import logging
import re
import time
import traceback
from collections.abc import AsyncIterable
from dataclasses import asdict

import pandas as pd
from numba.core.types import Boolean

from graphrag_ecolink.callbacks.workflow_callbacks import WorkflowCallbacks
from graphrag_ecolink.config.models.graph_rag_config import GraphRagConfig
from graphrag_ecolink.index.input.factory import create_input
from graphrag_ecolink.index.run.utils import create_run_context
from graphrag_ecolink.index.typing.context import PipelineRunContext
from graphrag_ecolink.index.typing.pipeline import Pipeline
from graphrag_ecolink.index.typing.pipeline_run_result import PipelineRunResult
from graphrag_ecolink.index.update.incremental_index import get_delta_docs
from graphrag_ecolink.logger.base import ProgressLogger
from graphrag_ecolink.logger.progress import Progress
from graphrag_ecolink.storage.pipeline_storage import PipelineStorage
from graphrag_ecolink.utils.api import create_cache_from_config, create_storage_from_config
from graphrag_ecolink.utils.storage import load_table_from_storage, write_table_to_storage

log = logging.getLogger(__name__)


async def run_pipeline(
    pipeline: Pipeline,
    config: GraphRagConfig,
    callbacks: WorkflowCallbacks,
    logger: ProgressLogger,
    is_update_run: bool = False
) -> AsyncIterable[PipelineRunResult]:
    """运行所有工作流的简化管道。

    参数
    ----------
    pipeline : Pipeline
        要运行的管道对象。
    config : GraphRagConfig
        配置对象，包含管道运行所需的参数。
    callbacks : WorkflowCallbacks
        工作流回调，用于监控管道执行。
    logger : ProgressLogger
        日志记录器，用于记录进度和日志信息。
    is_update_run : bool default=False
        是否为增量更新运行。

    返回值
    -------
    AsyncIterable[PipelineRunResult]
        异步生成的管道运行结果。
    """
    root_dir = config.root_dir  # 获取根目录

    # 创建存储和缓存对象
    storage = create_storage_from_config(config.output)
    cache = create_cache_from_config(config.cache, root_dir)

    # 加载输入数据集
    dataset = await create_input(config.input, logger, root_dir)

    # 加载现有状态（如果工作流是有状态的）
    state_json = await storage.get("context.json")
    state = json.loads(state_json) if state_json else {}

    if is_update_run:
        logger.info("运行增量索引。")  # 记录增量索引的日志

        # 获取增量数据集
        delta_dataset = await get_delta_docs(dataset, storage)

        # 如果增量数据集为空，记录警告并退出
        if delta_dataset.new_inputs.empty:
            warning_msg = "增量索引未找到新文档，退出。"
            logger.warning(warning_msg)
        else:
            # 创建更新存储对象
            update_storage = create_storage_from_config(config.update_index_output)
            update_timestamp = time.strftime("%Y%m%d-%H%M%S")  # 生成时间戳
            timestamped_storage = update_storage.child(update_timestamp)
            delta_storage = timestamped_storage.child("delta")
            previous_storage = timestamped_storage.child("previous")

            # 备份之前的输出
            await _copy_previous_output(storage, previous_storage)

            # 更新状态中的时间戳
            state["update_timestamp"] = update_timestamp

            # 创建运行上下文
            context = create_run_context(
                storage=delta_storage, cache=cache, callbacks=callbacks, state=state,mock_user_info=True
            )

            # 在新文档上运行管道
            async for table in _run_pipeline(
                pipeline=pipeline,
                config=config,
                dataset=delta_dataset.new_inputs,
                logger=logger,
                context=context,
            ):
                yield table

            logger.success("完成新文档的工作流运行。")  # 记录成功日志

    else:
        logger.info("运行标准索引。")  # 记录标准索引的日志

        # 创建运行上下文
        context = create_run_context(
            storage=storage, cache=cache, callbacks=callbacks, state=state,mock_user_info=True
        )

        # 运行管道
        async for table in _run_pipeline(
            pipeline=pipeline,
            config=config,
            dataset=dataset,
            logger=logger,
            context=context,
        ):
            yield table


async def _run_pipeline(
    pipeline: Pipeline,
    config: GraphRagConfig,
    dataset: pd.DataFrame,
    logger: ProgressLogger,
    context: PipelineRunContext,
) -> AsyncIterable[PipelineRunResult]:
    start_time = time.time()

    log.info("Final # of rows loaded: %s", len(dataset))
    context.stats.num_documents = len(dataset)
    last_workflow = "starting documents"

    try:
        await _dump_json(context)
        await write_table_to_storage(dataset, "documents", context.storage)

        for name, workflow_function in pipeline.run():
            last_workflow = name
            progress = logger.child(name, transient=False)
            context.callbacks.workflow_start(name, None)
            work_time = time.time()
            result = await workflow_function(config, context)
            progress(Progress(percent=1))
            context.callbacks.workflow_end(name, result)
            yield PipelineRunResult(
                workflow=name, result=result.result, state=context.state, errors=None
            )

            context.stats.workflows[name] = {"overall": time.time() - work_time}

        context.stats.total_runtime = time.time() - start_time
        await _dump_json(context)

    except Exception as e:
        log.exception("error running workflow %s", last_workflow)
        context.callbacks.error("Error running pipeline!", e, traceback.format_exc())
        yield PipelineRunResult(
            workflow=last_workflow, result=None, state=context.state, errors=[e]
        )


async def _dump_json(context: PipelineRunContext) -> None:
    """Dump the stats and context state to the storage."""
    await context.storage.set(
        "stats.json", json.dumps(asdict(context.stats), indent=4, ensure_ascii=False)
    )
    await context.storage.set(
        "context.json", json.dumps(context.state, indent=4, ensure_ascii=False)
    )


async def _copy_previous_output(
    storage: PipelineStorage,
    copy_storage: PipelineStorage,
):
    for file in storage.find(re.compile(r"\.parquet$")):
        base_name = file[0].replace(".parquet", "")
        table = await load_table_from_storage(base_name, storage)
        await write_table_to_storage(table, base_name, copy_storage)
