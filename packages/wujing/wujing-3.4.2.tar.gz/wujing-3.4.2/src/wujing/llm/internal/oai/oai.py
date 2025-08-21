import logging
import time
from typing import Dict, List, Any

from openai import OpenAI

logger = logging.getLogger(__name__)


def oai(
    *,
    api_key: str,
    api_base: str,
    model: str,
    messages: List[Dict[str, str]],
    **kwargs: Any,
) -> str:
    logger.debug(f"开始 OpenAI 调用: model={model}, api_base={api_base}, messages_count={len(messages)}")
    
    client = OpenAI(
        api_key=api_key,
        base_url=api_base,
    )

    # 记录请求参数（不包含敏感数据）
    safe_kwargs = {k: v for k, v in kwargs.items() if k != "api_key"}
    logger.debug(f"请求参数: {safe_kwargs}")
    
    call_start_time = time.time()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )
        
        elapsed_time = time.time() - call_start_time
        content = resp.choices[0].message.content
        logger.debug(f"OpenAI 调用成功，耗时: {elapsed_time:.3f}秒, 响应长度: {len(content) if content else 0}")
        
        if hasattr(resp, 'usage') and resp.usage:
            logger.debug(f"Token 使用情况: prompt={resp.usage.prompt_tokens}, "
                        f"completion={resp.usage.completion_tokens}, total={resp.usage.total_tokens}")
        
        return content

    except Exception as e:
        elapsed_time = time.time() - call_start_time
        logger.error(f"OpenAI 调用失败，耗时: {elapsed_time:.3f}秒，错误: {e}")
        raise RuntimeError(f"Failed to send request: {e}") from e
