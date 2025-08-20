# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""CLI implementation of the index subcommand."""

import asyncio
import logging
import sys
import warnings
from pathlib import Path

import graphrag_ecolink.api as api
from graphrag_ecolink.config.enums import CacheType, IndexingMethod
from graphrag_ecolink.config.load_config import load_config
from graphrag_ecolink.config.logging import enable_logging_with_config
from graphrag_ecolink.index.validate_config import validate_config_names
from graphrag_ecolink.logger.base import ProgressLogger
from graphrag_ecolink.logger.factory import LoggerFactory, LoggerType
from graphrag_ecolink.utils.cli import redact

# Ignore warnings from numba
warnings.filterwarnings("ignore", message=".*NumbaDeprecationWarning.*")

log = logging.getLogger(__name__)


def _logger(logger: ProgressLogger):
    def info(msg: str, verbose: bool = False):
        log.info(msg)
        if verbose:
            logger.info(msg)

    def error(msg: str, verbose: bool = False):
        log.error(msg)
        if verbose:
            logger.error(msg)

    def success(msg: str, verbose: bool = False):
        log.info(msg)
        if verbose:
            logger.success(msg)

    return info, error, success


def _register_signal_handlers(logger: ProgressLogger):
    import signal

    def handle_signal(signum, _):
        # 处理信号的回调函数
        logger.info(f"收到信号 {signum}，正在退出...")  # noqa: G004
        logger.dispose()  # 释放日志记录器资源
        for task in asyncio.all_tasks():  # 取消所有异步任务
            task.cancel()
        logger.info("所有任务已取消，正在退出...")

    # 注册信号处理程序，用于处理 SIGINT（中断信号）
    signal.signal(signal.SIGINT, handle_signal)

    # 如果不是 Windows 平台，额外注册 SIGHUP（挂起信号）的处理程序
    if sys.platform != "win32":
        signal.signal(signal.SIGHUP, handle_signal)


def index_cli(
    root_dir: Path,
    method: IndexingMethod,
    verbose: bool,
    memprofile: bool,
    cache: bool,
    logger: LoggerType,
    config_filepath: Path | None,
    dry_run: bool,
    skip_validation: bool,
    output_dir: Path | None,
):
    """Run the pipeline with the given config."""
    cli_overrides = {}
    if output_dir:
        cli_overrides["output.base_dir"] = str(output_dir)
        cli_overrides["reporting.base_dir"] = str(output_dir)
        cli_overrides["update_index_output.base_dir"] = str(output_dir)
    config = load_config(root_dir, config_filepath, cli_overrides)

    _run_index(
        config=config,
        method=method,
        is_update_run=False,
        verbose=verbose,
        memprofile=memprofile,
        cache=cache,
        logger=logger,
        dry_run=dry_run,
        skip_validation=skip_validation,
    )


def update_cli(
    root_dir: Path,
    method: IndexingMethod,
    verbose: bool,
    memprofile: bool,
    cache: bool,
    logger: LoggerType,
    config_filepath: Path | None,
    skip_validation: bool,
    output_dir: Path | None,
):
    """Run the pipeline with the given config."""
    cli_overrides = {}
    if output_dir:
        cli_overrides["output.base_dir"] = str(output_dir)
        cli_overrides["reporting.base_dir"] = str(output_dir)
        cli_overrides["update_index_output.base_dir"] = str(output_dir)

    config = load_config(root_dir, config_filepath, cli_overrides)

    _run_index(
        config=config,
        method=method,
        is_update_run=True,
        verbose=verbose,
        memprofile=memprofile,
        cache=cache,
        logger=logger,
        dry_run=False,
        skip_validation=skip_validation,
    )


def _run_index(
        config,
        method,
        is_update_run,
        verbose,
        memprofile,
        cache,
        logger,
        dry_run,
        skip_validation,
    ):
        # 创建进度日志记录器
        progress_logger = LoggerFactory().create_logger(logger)
        info, error, success = _logger(progress_logger)

        # 如果未启用缓存，则将配置中的缓存类型设置为 none
        if not cache:
            config.cache.type = CacheType.none

        # 启用日志记录并获取日志文件路径
        enabled_logging, log_path = enable_logging_with_config(config, verbose)
        if enabled_logging:
            info(f"Logging enabled at {log_path}", True)
        else:
            info(
                f"Logging not enabled for config {redact(config.model_dump())}",
                True,
            )

        # 如果未跳过验证，则验证大模型配置名称
        if not skip_validation:
            validate_config_names(progress_logger, config)

        # 打印管道运行的开始信息
        info(f"Starting pipeline run. {dry_run=}", verbose)
        info(
            f"Using default configuration: {redact(config.model_dump())}",
            verbose,
        )

        # 如果是 dry_run 模式，直接退出，这个dry_run暂时不知道是什么作用
        if dry_run:
            info("Dry run complete, exiting...", True)
            sys.exit(0)

        # 注册信号处理程序以处理中断信号
        _register_signal_handlers(progress_logger)

        # 异步运行索引构建 API
        outputs = asyncio.run(
            api.build_index(
                config=config,
                method=method,
                is_update_run=is_update_run,
                memory_profile=memprofile,
                progress_logger=progress_logger,
            )
        )

        # 检查是否有错误发生
        encountered_errors = any(
            output.errors and len(output.errors) > 0 for output in outputs
        )

        # 停止进度日志记录器
        progress_logger.stop()

        # 根据是否有错误打印相应的消息
        if encountered_errors:
            error(
                "Errors occurred during the pipeline run, see logs for more details.", True
            )
        else:
            success("All workflows completed successfully.", True)

        # 根据是否有错误退出程序
        sys.exit(1 if encountered_errors else 0)
