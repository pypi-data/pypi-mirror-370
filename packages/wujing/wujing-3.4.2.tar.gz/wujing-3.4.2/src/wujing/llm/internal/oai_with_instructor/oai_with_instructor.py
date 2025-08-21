import logging
import time
from typing import Any, Dict, List, Type

import instructor
from openai import OpenAI

from wujing.llm.types import ResponseModelType

logger = logging.getLogger(__name__)


def oai_with_instructor(
    *,
    api_key: str,
    api_base: str,
    model: str,
    messages: List[Dict[str, str]],
    response_model: Type[ResponseModelType] | None = None,
    **kwargs: Any,
) -> str:
    logger.debug(f"开始 Instructor 调用: model={model}, api_base={api_base}, "
                f"messages_count={len(messages)}, response_model={response_model.__name__ if response_model else None}")
    
    client = instructor.from_openai(
        client=OpenAI(api_key=api_key, base_url=api_base),
        mode=instructor.Mode.JSON,
    )

    # 记录请求参数（不包含敏感数据）
    safe_kwargs = {k: v for k, v in kwargs.items() if k != "api_key"}
    logger.debug(f"请求参数: {safe_kwargs}")
    
    call_start_time = time.time()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_model=response_model,
            **kwargs,
        )
        
        elapsed_time = time.time() - call_start_time
        result = response.model_dump_json()
        logger.debug(f"Instructor 调用成功，耗时: {elapsed_time:.3f}秒, 响应长度: {len(result)}")
        
        return result

    except Exception as e:
        elapsed_time = time.time() - call_start_time
        logger.error(f"Instructor 调用失败，耗时: {elapsed_time:.3f}秒，错误: {e}")
        raise RuntimeError(f"Failed to send request: {e}") from e
