# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing the pipeline reporter factory."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from graphrag_ecolink.callbacks.blob_workflow_callbacks import BlobWorkflowCallbacks
from graphrag_ecolink.callbacks.console_workflow_callbacks import ConsoleWorkflowCallbacks
from graphrag_ecolink.callbacks.file_workflow_callbacks import FileWorkflowCallbacks
from graphrag_ecolink.config.enums import ReportingType
from graphrag_ecolink.config.models.reporting_config import ReportingConfig

if TYPE_CHECKING:
    from graphrag_ecolink.callbacks.workflow_callbacks import WorkflowCallbacks


def create_pipeline_reporter(
    config: ReportingConfig | None, root_dir: str | None
) -> WorkflowCallbacks:
    """Create a logger for the given pipeline config."""
    config = config or ReportingConfig(base_dir="logs", type=ReportingType.file)
    match config.type:
        case ReportingType.file:
            return FileWorkflowCallbacks(
                str(Path(root_dir or "") / (config.base_dir or ""))
            )
        case ReportingType.console:
            return ConsoleWorkflowCallbacks()
        case ReportingType.blob:
            return BlobWorkflowCallbacks(
                config.connection_string,
                config.container_name,
                base_dir=config.base_dir,
                storage_account_blob_url=config.storage_account_blob_url,
            )
