"""缓存管理器"""

import hashlib
import json
import logging
import threading
from typing import Any, Type

from diskcache import FanoutCache as Cache

from wujing.llm.exceptions import CacheError
from wujing.llm.types import ResponseModelType

logger = logging.getLogger(__name__)


class CacheManager:
    """线程安全的缓存管理器"""

    _instances: dict[str, Cache] = {}
    _lock = threading.Lock()

    @classmethod
    def get_cache(cls, directory: str) -> Cache:
        """获取缓存实例"""
        logger.debug(f"获取缓存实例: {directory}")

        if directory not in cls._instances:
            with cls._lock:
                if directory not in cls._instances:
                    try:
                        logger.debug(f"创建新的缓存实例: {directory}")
                        cls._instances[directory] = Cache(directory=directory)
                        logger.debug(f"缓存实例创建成功: {directory}")
                    except Exception as e:
                        logger.error(f"创建缓存实例失败: {directory}, 错误: {e}")
                        raise CacheError(f"Failed to create cache: {e}") from e
        return cls._instances[directory]

    @classmethod
    def clear_cache(cls, directory: str | None = None) -> None:
        """清除缓存"""
        try:
            if directory is None:
                for cache in cls._instances.values():
                    cache.clear()
            elif directory in cls._instances:
                cls._instances[directory].clear()
        except Exception as e:
            raise CacheError(f"Failed to clear cache: {e}") from e

    @classmethod
    def get_cache_stats(cls, directory: str) -> dict[str, Any]:
        """获取缓存统计信息"""
        if directory in cls._instances:
            cache = cls._instances[directory]
            try:
                return {"size": len(cache), "volume": cache.volume(), "directory": directory}
            except Exception as e:
                raise CacheError(f"Failed to get cache stats: {e}") from e
        return {"size": 0, "volume": 0, "directory": directory}


class CacheKeyGenerator:
    """缓存键生成器"""

    # 缓存相关参数
    CACHE_RELEVANT_PARAMS = frozenset(
        [
            "api_key",
            "api_version",
            "api_base",
            "model",
            "messages",
            "response_model",
            "formatter",
            "protocol",
            "extra_body",
            "temperature",
            "max_tokens",
            "max_completion_tokens",
            "reasoning_effort",
            "verbosity",
            "top_p",
            "top_k",
        ]
    )

    # 模型 schema 缓存
    _schema_hash_cache: dict[Type, str] = {}
    _cache_lock = threading.Lock()

    @classmethod
    def generate_cache_key(cls, **kwargs: Any) -> str:
        """生成缓存键"""
        logger.debug(f"生成缓存键，输入参数: {list(kwargs.keys())}")

        cache_relevant_params = {}

        for param_name, value in kwargs.items():
            if param_name not in cls.CACHE_RELEVANT_PARAMS:
                logger.debug(f"跳过非缓存相关参数: {param_name}")
                continue

            if param_name == "api_key" and isinstance(value, str):
                cache_relevant_params["api_key_hash"] = cls._hash_api_key(value)
                logger.debug("已处理 API key 哈希")
            elif param_name == "response_model":
                hashed = cls._hash_response_model(value)
                cache_relevant_params[param_name] = hashed
                logger.debug(f"已处理响应模型哈希: {hashed}")
            else:
                cache_relevant_params[param_name] = cls._serialize_value(value)

        cache_str = json.dumps(cache_relevant_params, sort_keys=True, ensure_ascii=False)
        cache_key = hashlib.sha256(cache_str.encode("utf-8")).hexdigest()
        logger.debug(f"生成缓存键: {cache_key[:16]}..., 参数数量: {len(cache_relevant_params)}")
        return cache_key

    @classmethod
    def _hash_api_key(cls, api_key: str) -> str:
        """对 API 密钥进行哈希处理"""
        return hashlib.sha256(api_key.encode("utf-8")).hexdigest()[:16]

    @classmethod
    def _hash_response_model(cls, model: Type[ResponseModelType] | None) -> str | None:
        """对响应模型进行哈希处理"""
        if model is None:
            return None

        if hasattr(model, "model_json_schema"):
            return cls._get_schema_hash(model)
        elif hasattr(model, "__name__"):
            return f"{getattr(model, '__module__', '')}.{model.__name__}"
        else:
            return str(model)

    @classmethod
    def _get_schema_hash(cls, model: Type[ResponseModelType]) -> str:
        """获取模型 schema 的哈希值（带缓存）"""
        if model not in cls._schema_hash_cache:
            with cls._cache_lock:
                if model not in cls._schema_hash_cache:
                    try:
                        schema_str = json.dumps(model.model_json_schema(), sort_keys=True)
                        cls._schema_hash_cache[model] = hashlib.sha256(schema_str.encode()).hexdigest()[:16]
                    except Exception:
                        # 降级处理
                        model_identifier = (
                            f"{getattr(model, '__module__', '')}.{getattr(model, '__name__', str(model))}"
                        )
                        cls._schema_hash_cache[model] = hashlib.sha256(model_identifier.encode()).hexdigest()[:16]

        return cls._schema_hash_cache[model]

    @classmethod
    def _serialize_value(cls, value: Any) -> Any:
        """序列化值用于缓存键生成"""
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, (list, tuple)):
            try:
                return [cls._serialize_value(item) for item in value]
            except (TypeError, ValueError, RecursionError):
                return str(value)
        elif isinstance(value, dict):
            try:
                return {k: cls._serialize_value(v) for k, v in value.items()}
            except (TypeError, ValueError, RecursionError):
                return str(value)
        else:
            return str(value)

    @classmethod
    def clear_schema_cache(cls) -> None:
        """清理 schema 缓存"""
        with cls._cache_lock:
            cls._schema_hash_cache.clear()
