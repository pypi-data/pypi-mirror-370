"""协议处理器"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Type

from wujing.llm.config import LLMConfig, LLMRequest
from wujing.llm.exceptions import ProtocolError
from wujing.llm.internal.azure_oai.azure_oai import azure_oai
from wujing.llm.internal.oai.oai import oai
from wujing.llm.internal.oai_with_instructor.oai_with_instructor import oai_with_instructor
from wujing.llm.types import ResponseModelType

logger = logging.getLogger(__name__)


class ProtocolHandler(ABC):
    """协议处理器基类"""

    @abstractmethod
    def call(self, config: LLMConfig, request: LLMRequest, **kwargs) -> str:
        """执行 LLM 调用"""
        pass


class OpenAIProtocolHandler(ProtocolHandler):
    """OpenAI 协议处理器"""

    def call(self, config: LLMConfig, request: LLMRequest, **kwargs) -> str:
        """执行 OpenAI LLM 调用"""
        logger.debug(f"OpenAI 协议处理器开始调用，formatter: {config.formatter}")
        
        base_params = {
            "api_key": config.api_key,
            "api_base": config.api_base,
            "model": config.model,
            "messages": request.messages,
            **config.extra_kwargs,
            **kwargs
        }
        
        # 记录关键参数（不包含敏感信息）
        logger.debug(f"调用参数: model={config.model}, api_base={config.api_base}, "
                    f"messages_count={len(request.messages)}, extra_kwargs={list(config.extra_kwargs.keys())}, "
                    f"kwargs={list(kwargs.keys())}")

        match config.formatter:
            case "prompt":
                logger.debug("使用 oai_with_instructor 调用")
                return oai_with_instructor(
                    response_model=request.response_model,
                    context=request.context,
                    **base_params,
                )
            case "vllm":
                logger.debug("使用 vLLM 调用")
                return self._handle_vllm_call(base_params, request.response_model)
            case None:
                logger.debug("使用标准 OpenAI 调用")
                return oai(**base_params)
            case _:
                error_msg = f"Unsupported formatter for OpenAI: {config.formatter}"
                logger.error(error_msg)
                raise ProtocolError(error_msg)

    def _handle_vllm_call(self, base_params: dict[str, Any], response_model: Type[ResponseModelType] | None) -> str:
        """处理 vLLM 调用"""
        logger.debug("开始处理 vLLM 调用")
        
        if response_model is None:
            error_msg = "vLLM formatter requires response_model"
            logger.error(error_msg)
            raise ProtocolError(error_msg)

        extra_body = base_params.get("extra_body", {})
        if not isinstance(extra_body, dict):
            error_msg = "extra_body must be a dictionary"
            logger.error(error_msg)
            raise ProtocolError(error_msg)

        chat_template_kwargs = extra_body.get("chat_template_kwargs", {})
        chat_template_kwargs.update({"enable_thinking": False})

        schema = response_model.model_json_schema()
        logger.debug(f"生成 JSON schema，字段数量: {len(schema.get('properties', {}))}")
        
        extra_body.update({
            "guided_json": schema,
            "chat_template_kwargs": chat_template_kwargs,
        })
        
        base_params["extra_body"] = extra_body
        logger.debug(f"vLLM 调用参数准备完成，extra_body 包含: {list(extra_body.keys())}")
        return oai(**base_params)


class AzureProtocolHandler(ProtocolHandler):
    """Azure 协议处理器"""

    def call(self, config: LLMConfig, request: LLMRequest, **kwargs) -> str:
        """执行 Azure LLM 调用"""
        logger.debug(f"Azure 协议处理器开始调用，formatter: {config.formatter}")
        
        if config.api_version is None:
            error_msg = "Azure protocol requires api_version"
            logger.error(error_msg)
            raise ProtocolError(error_msg)

        # 记录关键参数（不包含敏感信息）
        logger.debug(f"调用参数: model={config.model}, azure_endpoint={config.api_base}, "
                    f"api_version={config.api_version}, messages_count={len(request.messages)}, "
                    f"has_response_model={request.response_model is not None}")

        match config.formatter:
            case None | "azure":
                logger.debug("使用 Azure OpenAI 调用")
                return azure_oai(
                    azure_endpoint=config.api_base,
                    api_key=config.api_key,
                    api_version=config.api_version,
                    model=config.model,
                    messages=request.messages,
                    response_model=request.response_model,
                    **config.extra_kwargs,
                    **kwargs,
                )
            case _:
                error_msg = f"Unsupported formatter for Azure: {config.formatter}"
                logger.error(error_msg)
                raise ProtocolError(error_msg)


class ProtocolHandlerFactory:
    """协议处理器工厂"""

    _handlers = {
        "openai": OpenAIProtocolHandler(),
        "azure": AzureProtocolHandler(),
    }

    @classmethod
    def get_handler(cls, protocol: str) -> ProtocolHandler:
        """获取协议处理器"""
        if protocol not in cls._handlers:
            raise ProtocolError(f"Unsupported protocol: {protocol}")
        return cls._handlers[protocol]

    @classmethod
    def register_handler(cls, protocol: str, handler: ProtocolHandler) -> None:
        """注册新的协议处理器"""
        cls._handlers[protocol] = handler
