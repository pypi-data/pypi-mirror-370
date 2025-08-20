# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing 'OssPipelineStorage' model."""

import logging
import re
from collections.abc import Iterator
from typing import Any, cast

import oss2
from oss2 import ObjectIterator
# 在文件顶部添加如下导入语句：
from datetime import datetime
from pathlib import Path

from graphrag_ecolink.logger.base import ProgressLogger
from graphrag_ecolink.storage.pipeline_storage import PipelineStorage

log = logging.getLogger(__name__)


def _create_progress_status(num_loaded, num_filtered, num_total):
    pass


class OssPipelineStorage(PipelineStorage):
    """File storage class definition for Alibaba Cloud OSS."""

    _bucket_name: str
    _endpoint: str
    _access_key_id: str
    _access_key_secret: str
    _root_dir: str
    _encoding: str

    def __init__(
        self,
        bucket_name: str,
        endpoint: str,
        access_key_id: str,
        access_key_secret: str,
        root_dir: str = "",
        encoding: str = "utf-8",
    ):
        """Init method definition."""
        self._bucket_name = bucket_name
        self._endpoint = endpoint
        self._access_key_id = access_key_id
        self._access_key_secret = access_key_secret
        self._root_dir = root_dir
        self._encoding = encoding

        # 初始化OSS Bucket对象
        self.auth = oss2.Auth(self._access_key_id, self._access_key_secret)
        self.bucket = oss2.Bucket(self.auth, self._endpoint, self._bucket_name)

    def find(
        self,
        file_pattern: re.Pattern[str],
        base_dir: str | None = None,
        progress: ProgressLogger | None = None,
        file_filter: dict[str, Any] | None = None,
        max_count=-1,
    ) -> Iterator[tuple[str, dict[str, Any]]]:
        """Find files in the OSS using a file pattern, as well as a custom filter function."""
        prefix = base_dir or "graph_rag"
        log.info("Searching OSS bucket %s with prefix %s", self._bucket_name, prefix)

        all_files = []
        for obj in ObjectIterator(self.bucket, prefix=prefix):
            if re.search(file_pattern, obj.key):
                all_files.append(obj.key)

        num_loaded = 0
        num_total = len(all_files)
        num_filtered = 0

        for file in all_files:
            match = file_pattern.search(file)
            if match:
                group = match.groupdict()
                filename = file.replace(self._root_dir, "")
                yield (filename, group)
                num_loaded += 1
                if max_count > 0 and num_loaded >= max_count:
                    break
            else:
                num_filtered += 1
            if progress is not None:
                progress(_create_progress_status(num_loaded, num_filtered, num_total))

    async def get(
        self, key: str, as_bytes: bool | None = False, encoding: str | None = None
    ) -> Any:
        """Get method definition for reading content from OSS."""
        try:
            obj = self.bucket.get_object(key)
            content = obj.read()
            if not as_bytes:
                encoding = encoding or self._encoding
                return content.decode(encoding)
            return content
        except Exception as e:
            log.error("Error reading file from OSS: %s", e)
            raise

    async def set(self, key: str, value: Any, encoding: str | None = None) -> None:
        """Set method definition (currently unsupported for OSS)."""
        raise NotImplementedError("Writing to OSS is not supported yet.")

    async def has(self, key: str) -> bool:
        """Check if file exists in OSS."""
        return self.bucket.object_exists(key)

    async def delete(self, key: str) -> None:
        """Delete method definition (currently unsupported for OSS)."""
        raise NotImplementedError("Deleting from OSS is not supported yet.")

    async def clear(self) -> None:
        """Clear method definition (currently unsupported for OSS)."""
        raise NotImplementedError("Clearing OSS storage is not supported yet.")

    def child(self, name: str | None) -> "PipelineStorage":
        """Create a child storage instance."""
        if name is None:
            return self
        return OssPipelineStorage(
            bucket_name=self._bucket_name,
            endpoint=self._endpoint,
            access_key_id=self._access_key_id,
            access_key_secret=self._access_key_secret,
            root_dir=str(Path(self._root_dir) / Path(name)),
            encoding=self._encoding,
        )

    def keys(self) -> list[str]:
        """Return the keys in the OSS storage."""
        return [obj.key for obj in ObjectIterator(self.bucket, prefix=self._root_dir)]

    async def get_creation_date(self, key: str) -> str:
        """Get the creation date of a file."""
        obj_info = self.bucket.get_object_meta(key)
        mtime = int(obj_info.headers["Last-Modified"])
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
