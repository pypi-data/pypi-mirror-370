"""LLM 调用异常类型定义"""


class LLMCallError(Exception):
    """LLM 调用基础异常"""
    pass


class ValidationError(LLMCallError):
    """验证错误异常"""

    def __init__(self, message: str, validation_error: Exception, attempt_count: int = 0):
        super().__init__(message)
        self.validation_error = validation_error
        self.attempt_count = attempt_count


class ConfigurationError(LLMCallError):
    """配置错误异常"""
    pass


class CacheError(LLMCallError):
    """缓存操作异常"""
    pass


class ProtocolError(LLMCallError):
    """协议处理异常"""
    pass


class RetryExhaustedError(LLMCallError):
    """重试次数耗尽异常"""
    
    def __init__(self, message: str, last_result: str | None = None, attempts: int = 0):
        super().__init__(message)
        self.last_result = last_result
        self.attempts = attempts
