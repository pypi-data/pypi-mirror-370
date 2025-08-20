# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing load method definition for OSS inputs."""

import logging
from pathlib import Path

import pandas as pd
import oss2

from graphrag_ecolink.config.models.input_config import InputConfig
from graphrag_ecolink.index.input.util import load_files
from graphrag_ecolink.index.utils.hashing import gen_sha512_hash
from graphrag_ecolink.logger.base import ProgressLogger
from graphrag_ecolink.storage.oss_pipeline_storage import OssPipelineStorage

log = logging.getLogger(__name__)


async def load_oss_text(
    config: InputConfig,
    progress: ProgressLogger | None,
    storage: OssPipelineStorage,
) -> pd.DataFrame:
    """Load text inputs from Alibaba Cloud OSS."""
    async def load_file(path: str, group: dict | None = None) -> pd.DataFrame:
        if group is None:
            group = {}

        # 从OSS下载文件内容
        obj =storage.bucket.get_object(path)
        text = obj.read().decode(config.encoding or "utf-8")

        new_item = {**group, "text": text}
        new_item["id"] = gen_sha512_hash(new_item, new_item.keys())
        new_item["title"] = str(Path(path).name)
        return pd.DataFrame([new_item])

    return await load_files(load_file, config, storage, progress)
