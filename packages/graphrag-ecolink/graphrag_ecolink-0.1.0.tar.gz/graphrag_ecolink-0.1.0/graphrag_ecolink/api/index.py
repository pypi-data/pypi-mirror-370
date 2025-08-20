# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""
Indexing API for GraphRAG.

WARNING: This API is under development and may undergo changes in future releases.
Backwards compatibility is not guaranteed at this time.
"""

import logging

from graphrag_ecolink.callbacks.reporting import create_pipeline_reporter
from graphrag_ecolink.callbacks.workflow_callbacks import WorkflowCallbacks
from graphrag_ecolink.config.enums import IndexingMethod
from graphrag_ecolink.config.models.graph_rag_config import GraphRagConfig
from graphrag_ecolink.index.run.run_pipeline import run_pipeline
from graphrag_ecolink.index.run.utils import create_callback_chain
from graphrag_ecolink.index.typing.pipeline_run_result import PipelineRunResult
from graphrag_ecolink.index.typing.workflow import WorkflowFunction
from graphrag_ecolink.index.workflows.factory import PipelineFactory
from graphrag_ecolink.logger.base import ProgressLogger
from graphrag_ecolink.logger.null_progress import NullProgressLogger

log = logging.getLogger(__name__)


async def build_index(
        config: GraphRagConfig,
        method: IndexingMethod = IndexingMethod.Standard,
        is_update_run: bool = False,
        memory_profile: bool = False,
        callbacks: list[WorkflowCallbacks] | None = None,
        progress_logger: ProgressLogger | None = None,
    ) -> list[PipelineRunResult]:
        """根据给定的配置运行管道。

        参数
        ----------
        config : GraphRagConfig
            配置对象。
        method : IndexingMethod default=IndexingMethod.Standard
            要执行的索引方法（例如：完整 LLM，NLP + LLM 等）。
        memory_profile : bool
            是否启用内存分析。
        callbacks : list[WorkflowCallbacks] | None default=None
            要注册的回调列表。
        progress_logger : ProgressLogger | None default=None
            进度日志记录器。

        返回值
        -------
        list[PipelineRunResult]
            管道运行结果的列表。
        """
        logger = progress_logger or NullProgressLogger()
        # 创建管道报告器（日志）并添加到其他回调中
        callbacks = callbacks or []
        callbacks.append(create_pipeline_reporter(config.reporting, None))

        # 创建回调链
        workflow_callbacks = create_callback_chain(callbacks, logger)

        outputs: list[PipelineRunResult] = []

        # 如果启用了内存分析，记录警告日志
        if memory_profile:
            log.warning("新管道尚不支持内存分析。")

        # 根据配置和方法创建管道
        pipeline = PipelineFactory.create_pipeline(config, method, is_update_run)

        # 调用管道开始的回调
        workflow_callbacks.pipeline_start(pipeline.names())

        # 异步运行管道
        async for output in run_pipeline(
            pipeline,
            config,
            callbacks=workflow_callbacks,
            logger=logger,
            is_update_run=is_update_run,
        ):
            outputs.append(output)
            # 如果有错误，记录错误日志；否则记录成功日志
            if output.errors and len(output.errors) > 0:
                logger.error(output.workflow)
            else:
                logger.success(output.workflow)
            # 记录结果信息
            logger.info(str(output.result))

        # 调用管道结束的回调
        workflow_callbacks.pipeline_end(outputs)
        return outputs


def register_workflow_function(name: str, workflow: WorkflowFunction):
    """Register a custom workflow function. You can then include the name in the settings.yaml workflows list."""
    PipelineFactory.register(name, workflow)
