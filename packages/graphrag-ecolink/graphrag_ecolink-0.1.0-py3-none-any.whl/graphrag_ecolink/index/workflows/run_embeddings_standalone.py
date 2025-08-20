import asyncio
import os
import pandas as pd

from graphrag_ecolink.db.neo4j_storage import create_indexes_from_file
from graphrag_ecolink.index.typing.user_info import PipelineUseInfo
from graphrag_ecolink.index.workflows.generate_text_embeddings_to_neo4j import run_workflow
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# 模拟 config 对象
class MockGraphRagConfig:
    def __init__(self):
        self.snapshots = type('Snapshots', (), {'embeddings': True})
        self.embed_text = type('EmbedText', (), {'names': [
            'document_text_embedding',
            'relationship_description_embedding',
            'text_unit_text_embedding',
            'entity_title_embedding',
            'entity_description_embedding',
            'community_title_embedding',
            'community_summary_embedding',
            'community_full_content_embedding'
        ]})


# 构造 mock context 对象
class MockPipelineRunContext:
    def __init__(self, storage_path: str,     # user_info 默认值
        tenant_id: str = "test-tenant",
        user_id: str = "test-user",
        biz_code: str = "test-biz_code"):
        self.storage_path = storage_path
        self.storage = self

        self.user_info = PipelineUseInfo(
            tenant_id=tenant_id,
            user_id=user_id,
            biz_code=biz_code
        )



    async def has(self, name: str) -> bool:
        return await self.has_table(name)
    async def has_table(self, name: str) -> bool:
        return os.path.exists(os.path.join(self.storage_path, f"{name}.parquet"))
    async def get_table(self, name: str) -> pd.DataFrame:
        if await self.has_table(name):
            return pd.read_parquet(os.path.join(self.storage_path, f"{name}.parquet"))
        return None


async def main():
    # 设置数据路径
    data_dir = "../../../ragtest/output"  # 替换为你实际的 parquet 文件目录

    # 创建 mock config 和 context
    config = MockGraphRagConfig()
    context = MockPipelineRunContext(data_dir)

    print("✅ 开始运行 generate_text_embeddings_to_neo4j.py ...")
    result = await run_workflow(config, context)
    print("✅ 数据处理完成，开始写入 Neo4j ...")



if __name__ == "__main__":
    asyncio.run(main())
