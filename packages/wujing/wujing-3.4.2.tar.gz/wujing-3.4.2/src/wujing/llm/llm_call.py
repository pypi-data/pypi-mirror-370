"""优化后的 LLM 调用模块"""

import logging
import time
from typing import Any, Type

from pydantic import validate_call

from wujing.llm.cache import CacheManager, CacheKeyGenerator
from wujing.llm.config import LLMConfig, LLMRequest
from wujing.llm.exceptions import ConfigurationError, LLMCallError
from wujing.llm.protocol import ProtocolHandlerFactory
from wujing.llm.retry import RetryManager, create_clean_model
from wujing.llm.types import ResponseModelType

logger = logging.getLogger(__name__)

# 允许的额外参数
ALLOWED_KWARGS = frozenset(["extra_body", "temperature", "max_tokens"])


class LLMService:
    """LLM 服务类"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.retry_manager = RetryManager(config)
        self.protocol_handler = ProtocolHandlerFactory.get_handler(config.protocol)
        self.cache_manager = CacheManager() if config.cache_enabled else None

    def call(self, request: LLMRequest, **kwargs) -> str:
        """执行 LLM 调用"""
        call_start_time = logger.isEnabledFor(logging.DEBUG) and time.time()
        
        try:
            # 记录调用开始的详细信息
            logger.debug(
                f"开始 LLM 调用: model={self.config.model}, protocol={self.config.protocol}, "
                f"formatter={self.config.formatter}, messages_count={len(request.messages)}, "
                f"has_response_model={request.response_model is not None}, "
                f"kwargs={kwargs}"
            )
            
            self._validate_kwargs(kwargs)
            self._validate_request(request)

            # 检查缓存
            cache_hit = False
            if self.cache_manager:
                logger.debug("检查缓存中...")
                cached_result = self._get_cached_result(request, kwargs)
                if cached_result is not None:
                    cache_hit = True
                    logger.debug(f"缓存命中，返回缓存结果，长度: {len(cached_result)}")
                    return cached_result
                else:
                    logger.debug("缓存未命中")

            # 执行调用
            use_retry = self._should_use_retry(request)
            logger.debug(f"使用重试机制: {use_retry}")
            
            if use_retry:
                clean_model = create_clean_model(request.response_model)
                logger.debug(f"创建清理模型: {clean_model.__name__ if clean_model else None}")
                result = self.retry_manager.execute_with_validation_retry(
                    llm_call_func=self._call_llm_internal,
                    request=request,
                    clean_model=clean_model,
                    **kwargs
                )
            else:
                result = self._call_llm_internal(
                    messages=request.messages,
                    response_model=request.response_model,
                    **kwargs
                )

            # 记录调用结果
            logger.debug(f"LLM 调用成功，结果长度: {len(result)}")
            
            # 缓存结果
            if self.cache_manager and not cache_hit:
                logger.debug("缓存调用结果...")
                self._cache_result(request, kwargs, result)

            if call_start_time:
                elapsed_time = time.time() - call_start_time
                logger.debug(f"LLM 调用总耗时: {elapsed_time:.3f}秒")

            return result

        except Exception as e:
            if call_start_time:
                elapsed_time = time.time() - call_start_time
                logger.error(f"LLM 调用失败，耗时: {elapsed_time:.3f}秒，错误: {e}")
            else:
                logger.error(f"LLM 调用失败: {e}")
            raise LLMCallError(f"LLM call failed: {e}") from e

    def _validate_kwargs(self, kwargs: dict[str, Any]) -> None:
        """验证额外参数"""
        invalid_kwargs = set(kwargs.keys()) - ALLOWED_KWARGS
        if invalid_kwargs:
            raise ConfigurationError(
                f"Invalid kwargs parameters: {invalid_kwargs}. "
                f"Allowed parameters are: {ALLOWED_KWARGS}"
            )

    def _validate_request(self, request: LLMRequest) -> None:
        """验证请求参数"""
        has_response_model = request.response_model is not None
        has_formatter = self.config.formatter is not None

        if has_response_model != has_formatter:
            raise ConfigurationError(
                "Both response_model and formatter must be either set or unset"
            )

    def _should_use_retry(self, request: LLMRequest) -> bool:
        """判断是否应该使用重试机制"""
        return (
            self.config.retry_enabled
            and request.response_model is not None
        )

    def _get_cached_result(self, request: LLMRequest, kwargs: dict[str, Any]) -> str | None:
        """获取缓存结果"""
        if not self.cache_manager:
            return None

        try:
            cache = self.cache_manager.get_cache(self.config.cache_directory)
            cache_key = CacheKeyGenerator.generate_cache_key(
                api_key=self.config.api_key,
                api_version=self.config.api_version,
                api_base=self.config.api_base,
                model=self.config.model,
                messages=request.messages,
                response_model=request.response_model,
                formatter=self.config.formatter,
                protocol=self.config.protocol,
                **self.config.extra_kwargs,
                **kwargs,
            )
            logger.debug(f"生成缓存键: {cache_key[:16]}...")
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"缓存命中，键: {cache_key[:16]}..., 结果长度: {len(result)}")
            else:
                logger.debug(f"缓存未命中，键: {cache_key[:16]}...")
            return result
        except Exception as e:
            logger.warning(f"获取缓存结果失败: {e}")
            return None

    def _cache_result(self, request: LLMRequest, kwargs: dict[str, Any], result: str) -> None:
        """缓存结果"""
        if not self.cache_manager:
            return

        try:
            cache = self.cache_manager.get_cache(self.config.cache_directory)
            cache_key = CacheKeyGenerator.generate_cache_key(
                api_key=self.config.api_key,
                api_version=self.config.api_version,
                api_base=self.config.api_base,
                model=self.config.model,
                messages=request.messages,
                response_model=request.response_model,
                formatter=self.config.formatter,
                protocol=self.config.protocol,
                **self.config.extra_kwargs,
                **kwargs,
            )

            logger.debug(f"缓存结果，键: {cache_key[:16]}..., 结果长度: {len(result)}, TTL: {self.config.cache_ttl}")
            
            if self.config.cache_ttl is not None:
                cache.set(cache_key, result, expire=self.config.cache_ttl)
            else:
                cache.set(cache_key, result)
                
            logger.debug(f"结果已缓存，键: {cache_key[:16]}...")
        except Exception as e:
            logger.warning(f"缓存结果失败: {e}")

    def _call_llm_internal(self, **kwargs) -> str:
        """内部 LLM 调用"""
        logger.debug(f"开始内部 LLM 调用，参数: {list(kwargs.keys())}")
        
        # 移除不需要传递给协议处理器的参数
        request_kwargs = kwargs.copy()
        messages = request_kwargs.pop("messages")
        response_model = request_kwargs.pop("response_model", None)
        
        logger.debug(f"消息数量: {len(messages)}, 响应模型: {response_model.__name__ if response_model else None}")
        
        request = LLMRequest(
            messages=messages,
            response_model=response_model,
            context=request_kwargs.pop("context", None)
        )
        
        call_start_time = time.time()
        try:
            result = self.protocol_handler.call(self.config, request, **request_kwargs)
            elapsed_time = time.time() - call_start_time
            logger.debug(f"协议处理器调用成功，耗时: {elapsed_time:.3f}秒，结果长度: {len(result)}")
            return result
        except Exception as e:
            elapsed_time = time.time() - call_start_time
            logger.error(f"协议处理器调用失败，耗时: {elapsed_time:.3f}秒，错误: {e}")
            raise


@validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
def llm_call(
    *,
    api_key: str,
    api_version: str | None = None,
    api_base: str,
    model: str,
    messages: list[dict[str, str]],
    response_model: Type[ResponseModelType] | None = None,
    context: dict[str, Any] | None = None,
    formatter: str | None = None,
    protocol: str = "openai",
    cache_enabled: bool = True,
    cache_directory: str = "./.diskcache/llm_cache",
    cache_ttl: int | None = None,
    retry_enabled: bool = True,
    max_retry_attempts: int = 3,
    retry_min_wait: float = 1.0,
    retry_max_wait: float = 10.0,
    retry_multiplier: float = 1.0,
    **kwargs: Any,
) -> str:
    """LLM 调用函数（向后兼容接口）"""
    config = LLMConfig(
        api_key=api_key,
        api_version=api_version,
        api_base=api_base,
        model=model,
        protocol=protocol,
        formatter=formatter,
        cache_enabled=cache_enabled,
        cache_directory=cache_directory,
        cache_ttl=cache_ttl,
        retry_enabled=retry_enabled,
        max_retry_attempts=max_retry_attempts,
        retry_min_wait=retry_min_wait,
        retry_max_wait=retry_max_wait,
        retry_multiplier=retry_multiplier,
        extra_kwargs=kwargs,
    )

    request = LLMRequest(
        messages=messages,
        response_model=response_model,
        context=context,
    )

    service = LLMService(config)
    return service.call(request)


# 便利函数
def clear_llm_cache(cache_directory: str = "./.diskcache/llm_cache") -> None:
    """清除 LLM 调用缓存"""
    CacheManager.clear_cache(cache_directory)


def get_llm_cache_stats(cache_directory: str = "./.diskcache/llm_cache") -> dict[str, Any]:
    """获取 LLM 缓存统计信息"""
    return CacheManager.get_cache_stats(cache_directory)


def cleanup_schema_cache() -> None:
    """清理 schema 缓存，释放内存"""
    CacheKeyGenerator.clear_schema_cache()
