"""HTTP客户端库

基于httpx和pydantic的HTTP客户端库，支持同步和异步调用，
具备完善的请求响应校验、日志记录、超时控制和智能重试机制。
"""

from .client import HttpClient
from .config import ClientConfig
from .models import Response, RequestModel
from .exceptions import (
    HttpClientError,
    TimeoutError,
    ConnectionError,
    RetryExhaustedError
)

__version__ = "0.1.0"
__all__ = [
    "HttpClient",
    "ClientConfig", 
    "Response",
    "RequestModel",
    "HttpClientError",
    "TimeoutError",
    "ConnectionError",
    "RetryExhaustedError"
]