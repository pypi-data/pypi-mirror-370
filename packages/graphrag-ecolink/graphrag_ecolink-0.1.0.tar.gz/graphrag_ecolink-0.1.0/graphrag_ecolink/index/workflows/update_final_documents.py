# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing run_workflow method definition."""

import logging

from graphrag_ecolink.config.models.graph_rag_config import GraphRagConfig
from graphrag_ecolink.index.run.utils import get_update_storages
from graphrag_ecolink.index.typing.context import PipelineRunContext
from graphrag_ecolink.index.typing.workflow import WorkflowFunctionOutput
from graphrag_ecolink.index.update.incremental_index import concat_dataframes

logger = logging.getLogger(__name__)


async def run_workflow(
    config: GraphRagConfig,
    context: PipelineRunContext,
) -> WorkflowFunctionOutput:
    """Update the documents from a incremental index run."""
    logger.info("Updating Documents")
    output_storage, previous_storage, delta_storage = get_update_storages(
        config, context.state["update_timestamp"]
    )

    final_documents = await concat_dataframes(
        "documents", previous_storage, delta_storage, output_storage
    )

    context.state["incremental_update_final_documents"] = final_documents

    return WorkflowFunctionOutput(result=None)
