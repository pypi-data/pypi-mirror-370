from dataclasses import dataclass, field

"""
用户上下文相关信息
"""
@dataclass
class PipelineUseInfo:
    """User-related information for the current pipeline run."""
    tenant_id: str = field(default="0")  # 默认值
    user_id: str = field(default="")  # 可选：为空字符串或其他默认值
    biz_code: str = field(default="")  # 可选：为空字符串或其他默认值
