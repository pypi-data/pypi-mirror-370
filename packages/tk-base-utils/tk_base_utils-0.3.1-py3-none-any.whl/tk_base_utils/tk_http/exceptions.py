"""HTTP客户端异常定义"""

from typing import Optional


class HttpClientError(Exception):
    """HTTP客户端基础异常类"""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class TimeoutError(HttpClientError):
    """超时异常"""
    
    def __init__(self, message: str = "Request timeout"):
        super().__init__(message)


class ConnectionError(HttpClientError):
    """连接异常"""
    
    def __init__(self, message: str = "Connection error"):
        super().__init__(message)


class RetryExhaustedError(HttpClientError):
    """重试次数耗尽异常"""
    
    def __init__(self, message: str = "Maximum retry attempts exceeded"):
        super().__init__(message)


class ValidationError(HttpClientError):
    """数据校验异常"""
    
    def __init__(self, message: str = "Data validation failed"):
        super().__init__(message)


class HttpStatusError(HttpClientError):
    """HTTP状态码异常"""
    
    def __init__(self, message: str, status_code: int):
        super().__init__(message, status_code)
        self.status_code = status_code