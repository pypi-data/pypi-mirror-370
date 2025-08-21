import logging
import time
from typing import Dict, List
from typing import Any
from openai import AzureOpenAI
from wujing.llm.types import ResponseModelType
from typing import Type
from pydantic import validate_call

logger = logging.getLogger(__name__)


@validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
def azure_oai(
    *,
    api_key: str,
    api_version: str,
    azure_endpoint: str,
    model: str,
    messages: List[Dict[str, str]],
    response_model: Type[ResponseModelType] | None = None,
    **kwargs: Any,
) -> str:
    logger.debug(f"开始 Azure OpenAI 调用: model={model}, azure_endpoint={azure_endpoint}, "
                f"api_version={api_version}, messages_count={len(messages)}, "
                f"has_response_model={response_model is not None}")
    
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=azure_endpoint,
    )

    # 记录请求参数（不包含敏感数据）
    safe_kwargs = {k: v for k, v in kwargs.items() if k != "api_key"}
    logger.debug(f"请求参数: {safe_kwargs}")
    
    call_start_time = time.time()
    try:
        if response_model is None:
            logger.debug("使用标准聊天完成")
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs,
            )
            content = resp.choices[0].message.content
        else:
            logger.debug(f"使用结构化响应解析: {response_model.__name__}")
            resp = client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                response_format=response_model,
                **kwargs,
            )
            content = resp.choices[0].message.content

        elapsed_time = time.time() - call_start_time
        logger.debug(f"Azure OpenAI 调用成功，耗时: {elapsed_time:.3f}秒, 响应长度: {len(content) if content else 0}")
        
        if hasattr(resp, 'usage') and resp.usage:
            logger.debug(f"Token 使用情况: prompt={resp.usage.prompt_tokens}, "
                        f"completion={resp.usage.completion_tokens}, total={resp.usage.total_tokens}")
        
        return content

    except Exception as e:
        elapsed_time = time.time() - call_start_time
        logger.error(f"Azure OpenAI 调用失败，耗时: {elapsed_time:.3f}秒，错误: {e}")
        raise RuntimeError(f"Failed to send request: {e}") from e
