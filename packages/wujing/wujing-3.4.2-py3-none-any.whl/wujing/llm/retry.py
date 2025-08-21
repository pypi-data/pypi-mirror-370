"""重试管理器"""

import logging
from typing import Any, Callable

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log,
    RetryError,
)

from wujing.llm.config import LLMConfig, LLMRequest
from wujing.llm.exceptions import ValidationError, RetryExhaustedError
from wujing.llm.types import ResponseModelType

logger = logging.getLogger(__name__)


class RetryManager:
    """重试管理器"""

    def __init__(self, config: LLMConfig):
        self.config = config

    def create_retry_decorator(self):
        """创建重试装饰器"""
        return retry(
            stop=stop_after_attempt(self.config.max_retry_attempts),
            wait=wait_exponential(
                multiplier=self.config.retry_multiplier, min=self.config.retry_min_wait, max=self.config.retry_max_wait
            ),
            retry=retry_if_exception_type(ValidationError),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            after=after_log(logger, logging.INFO),
            reraise=True,
        )

    def execute_with_validation_retry(
        self, llm_call_func: Callable, request: LLMRequest, clean_model: type[ResponseModelType], **kwargs
    ) -> str:
        """执行带验证重试的 LLM 调用"""
        logger.debug(f"开始执行重试调用，{self.config.max_retry_attempts=}")

        if not self.config.retry_enabled or request.response_model is None:
            logger.debug(f"跳过重试机制：{self.config.retry_enabled=} 或 {request.response_model=}")
            return llm_call_func(messages=request.messages, response_model=request.response_model, **kwargs)

        messages_copy = request.messages.copy()
        attempt_count = {"count": 0, "original_length": len(request.messages)}

        msg_count = len(request.messages)
        model_name = getattr(request.response_model, "__name__", str(request.response_model))
        logger.debug(f"初始化重试参数：{msg_count=}, response_model={model_name}")

        retry_func = self.create_retry_decorator()(self._llm_call_with_validation)

        try:
            result = retry_func(
                llm_call_func=llm_call_func,
                clean_model=clean_model,
                response_model=request.response_model,
                context=request.context,
                messages=messages_copy,
                attempt_count=attempt_count,
                **kwargs,
            )
            logger.debug(f"重试调用成功，{attempt_count['count']=}")
            return result
        except RetryError as e:
            logger.error(f"所有重试尝试都失败了，{self.config.max_retry_attempts=}")

            # 尝试返回最后一次的结果
            last_result = None
            if hasattr(e.last_attempt, "result") and e.last_attempt.result():
                last_result = e.last_attempt.result()
                logger.debug("获取到最后一次尝试的结果")
            else:
                # 最后尝试不带验证的调用
                logger.debug("执行最后的无验证调用")
                last_result = llm_call_func(messages=messages_copy, response_model=clean_model, **kwargs)

            raise RetryExhaustedError(
                f"All retry attempts failed after {self.config.max_retry_attempts} attempts",
                last_result=last_result,
                attempts=self.config.max_retry_attempts,
            )

    def _llm_call_with_validation(
        self,
        llm_call_func: Callable,
        clean_model: type[ResponseModelType],
        response_model: type[ResponseModelType],
        context: dict[str, Any] | None,
        messages: list[dict[str, str]],
        attempt_count: dict[str, int],
        **kwargs,
    ) -> str:
        """带验证的 LLM 调用"""
        attempt_count["count"] += 1
        current_attempt = attempt_count["count"]
        current_msg_count = len(messages)
        logger.debug(f"开始第 {current_attempt} 次验证调用，{current_msg_count=}")

        result = llm_call_func(messages=messages, response_model=clean_model, **kwargs)
        result_length = len(result) if result else 0
        logger.debug(f"第 {current_attempt} 次调用完成，{result_length=}")

        try:
            # 构建验证参数，只有当 context 不为 None 时才传递
            validate_kwargs = {}
            if context is not None:
                validate_kwargs["context"] = context

            response_model.model_validate_json(result, **validate_kwargs)
            logger.debug(f"第 {current_attempt} 次调用验证成功")
            return result
        except Exception as e:
            error_str = str(e)[:200]  # 限制错误信息长度
            logger.warning(f"第 {current_attempt} 次调用验证失败：{error_str}")

            # 添加模型的返回作为 assistant 消消息
            assistant_msg = {
                "role": "assistant",
                "content": result,
            }

            # 安全地获取错误信息
            try:
                err_msg = e.errors()[0]["msg"] if hasattr(e, "errors") and e.errors() else str(e)[:200]
            except (AttributeError, IndexError, KeyError):
                err_msg = "未知验证错误"
            logger.debug(f"验证错误详情：{err_msg}")

            # 添加用户反馈消息
            feedback_msg = {
                "role": "user",
                "content": err_msg,
            }

            # 如果已经有重试的消息历史，需要移除之前的反馈消息，但保留模型返回
            current_length = len(messages)
            original_length = attempt_count.get("original_length", 0)

            if current_length > original_length:
                # 移除之前的反馈消息对（assistant + user），保持消息列表回到原始对话状态
                logger.debug(f"清理之前的重试消息：{current_length=} -> {original_length=}")
                messages = messages[:original_length]

            # 添加当前模型返回和用户反馈
            messages.extend([assistant_msg, feedback_msg])
            new_msg_count = len(messages)
            logger.debug(f"添加反馈消息后，{new_msg_count=}")

            raise ValidationError(
                f"Validation failed on attempt {current_attempt}: {error_str}",
                validation_error=e,
                attempt_count=current_attempt,
            )


def create_clean_model(model_class: type[ResponseModelType]) -> type[ResponseModelType]:
    """创建去除自定义验证器的模型类，保留字段定义和描述信息"""
    from pydantic import BaseModel, RootModel, Field

    # 检查是否是 RootModel 的子类
    if issubclass(model_class, RootModel):
        # 对于 RootModel，我们需要保持其 RootModel 特性
        # 获取原始的 root 字段信息
        root_field = model_class.model_fields["root"]
        root_type = root_field.annotation

        # 创建新的 RootModel 类，保留描述信息
        if root_field.description:
            # 创建一个带有描述的 RootModel 子类
            class CleanRootModel(RootModel[root_type]):
                """Clean version of the original RootModel"""

                def __init__(self, root=None):
                    if root is not None:
                        super().__init__(root)
                    else:
                        super().__init__()

            # 手动设置 root 字段的描述
            CleanRootModel.model_fields["root"] = Field(description=root_field.description)
        else:
            # 创建简单的 RootModel 子类
            class CleanRootModel(RootModel[root_type]):
                """Clean version of the original RootModel"""

                pass

        # 重命名类并保留文档字符串
        CleanRootModel.__name__ = f"Clean{model_class.__name__}"
        CleanRootModel.__qualname__ = f"Clean{model_class.__name__}"
        if model_class.__doc__:
            CleanRootModel.__doc__ = model_class.__doc__

        return CleanRootModel
    else:
        # 对于普通的 BaseModel，保持原有逻辑但保留字段描述
        # 获取原始模型的字段信息
        fields = model_class.model_fields

        # 创建一个新的类，只包含字段定义，不包含验证器
        class_dict = {}

        # 添加字段的类型注解和字段定义
        annotations = {}
        for field_name, field_info in fields.items():
            # 从字段信息中获取类型
            annotations[field_name] = field_info.annotation

            # 检查是否需要保留字段信息
            needs_field = False
            field_kwargs = {}

            # 检查描述信息
            if field_info.description:
                field_kwargs["description"] = field_info.description
                needs_field = True

            # 检查默认值
            if hasattr(field_info, "default") and field_info.default is not None:
                if hasattr(field_info, "default_factory") and field_info.default_factory is not None:
                    # 有 default_factory
                    field_kwargs["default_factory"] = field_info.default_factory
                else:
                    # 有 default 值
                    field_kwargs["default"] = field_info.default
                needs_field = True
            elif hasattr(field_info, "is_required") and callable(field_info.is_required) and field_info.is_required():
                field_kwargs["default"] = ...
                needs_field = True

            # 保留基本约束但移除自定义验证器
            if hasattr(field_info, "constraints") and field_info.constraints:
                constraints = field_info.constraints
                # 保留基本约束如 min_length, max_length, ge, le 等
                basic_constraints = ["min_length", "max_length", "ge", "le", "gt", "lt"]
                for constraint in basic_constraints:
                    if hasattr(constraints, constraint):
                        constraint_value = getattr(constraints, constraint)
                        if constraint_value is not None:
                            field_kwargs[constraint] = constraint_value
                            needs_field = True

            if needs_field and field_kwargs:
                class_dict[field_name] = Field(**field_kwargs)

        class_dict["__annotations__"] = annotations

        # 保留原始类的文档字符串
        if model_class.__doc__:
            class_dict["__doc__"] = model_class.__doc__

        # 使用type()动态创建新类，只继承BaseModel，不继承原始类
        CleanModel = type(f"Clean{model_class.__name__}", (BaseModel,), class_dict)

        return CleanModel
