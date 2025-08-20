# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

# isort: skip_file
"""A module containing the 'PipelineRunContext' models."""

from dataclasses import dataclass

from graphrag_ecolink.cache.pipeline_cache import PipelineCache
from graphrag_ecolink.callbacks.workflow_callbacks import WorkflowCallbacks
from graphrag_ecolink.index.typing.state import PipelineState
from graphrag_ecolink.index.typing.stats import PipelineRunStats
from graphrag_ecolink.index.typing.user_info import PipelineUseInfo
from graphrag_ecolink.storage.pipeline_storage import PipelineStorage


@dataclass
class PipelineRunContext:
    """Provides the context for the current pipeline run."""

    user_info: PipelineUseInfo
    stats: PipelineRunStats
    storage: PipelineStorage
    "Long-term storage for pipeline verbs to use. Items written here will be written to the storage provider."
    cache: PipelineCache
    "Cache instance for reading previous LLM responses."
    callbacks: WorkflowCallbacks
    "Callbacks to be called during the pipeline run."
    state: PipelineState
    "Arbitrary property bag for runtime state, persistent pre-computes, or experimental features."
