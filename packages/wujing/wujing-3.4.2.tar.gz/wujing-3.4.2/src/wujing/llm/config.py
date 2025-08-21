"""LLM 调用配置管理"""

from dataclasses import dataclass, field
from typing import Any, Literal, Type

from wujing.llm.types import ResponseModelType


@dataclass
class LLMConfig:
    """LLM 调用配置"""
    
    # 基本配置
    api_key: str
    api_base: str
    model: str
    api_version: str | None = None
    protocol: Literal["openai", "azure"] = "openai"
    formatter: Literal["prompt", "vllm", "azure"] | None = None
    
    # 缓存配置
    cache_enabled: bool = True
    cache_directory: str = "./.diskcache/llm_cache"
    cache_ttl: int | None = None
    
    # 重试配置
    retry_enabled: bool = True
    max_retry_attempts: int = 3
    retry_min_wait: float = 1.0
    retry_max_wait: float = 10.0
    retry_multiplier: float = 1.0
    
    # 其他参数
    extra_kwargs: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """验证配置参数"""
        if self.protocol == "azure" and not self.api_version:
            raise ValueError("Azure protocol requires api_version")
        
        if self.max_retry_attempts < 1:
            raise ValueError("max_retry_attempts must be at least 1")


@dataclass 
class LLMRequest:
    """LLM 请求配置"""
    
    messages: list[dict[str, str]]
    response_model: Type[ResponseModelType] | None = None
    context: dict[str, Any] | None = None
