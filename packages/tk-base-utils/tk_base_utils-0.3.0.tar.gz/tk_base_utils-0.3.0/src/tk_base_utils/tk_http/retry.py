"""HTTP客户端重试策略"""

import asyncio
import time
from typing import Callable, Any, Awaitable, Union, Type
from functools import wraps

import httpx

from .config import ClientConfig
from .logger import HttpLogger
from .exceptions import (
    RetryExhaustedError,
    TimeoutError as ClientTimeoutError,
    ConnectionError as ClientConnectionError
)


class RetryStrategy:
    """重试策略类"""
    
    def __init__(self, config: ClientConfig, logger: HttpLogger):
        self.config = config
        self.logger = logger
    
    def should_retry(self, exception: Exception) -> bool:
        """判断是否应该重试"""
        # 网络连接错误 - 重试
        if isinstance(exception, (httpx.ConnectError, httpx.NetworkError)):
            return True
        
        # 超时错误 - 重试
        if isinstance(exception, (httpx.TimeoutException, httpx.ReadTimeout, 
                                httpx.ConnectTimeout, httpx.PoolTimeout)):
            return True
        
        # HTTP状态码错误 - 不重试
        if isinstance(exception, httpx.HTTPStatusError):
            return False
        
        # 其他错误 - 不重试
        return False
    
    def get_delay(self, attempt: int) -> float:
        """计算重试延迟时间（指数退避）"""
        delay = self.config.retry_delay * (self.config.retry_backoff_factor ** (attempt - 1))
        return min(delay, 60.0)  # 最大延迟60秒
    
    def convert_exception(self, exception: Exception) -> Exception:
        """转换httpx异常为客户端异常"""
        if isinstance(exception, (httpx.TimeoutException, httpx.ReadTimeout, 
                                httpx.ConnectTimeout, httpx.PoolTimeout)):
            return ClientTimeoutError(str(exception))
        
        if isinstance(exception, (httpx.ConnectError, httpx.NetworkError)):
            return ClientConnectionError(str(exception))
        
        return exception


def with_retry(retry_strategy: RetryStrategy):
    """同步重试装饰器"""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, retry_strategy.config.max_retries + 2):  # +1 for initial attempt
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # 如果是最后一次尝试，直接抛出异常
                    if attempt > retry_strategy.config.max_retries:
                        converted_exception = retry_strategy.convert_exception(e)
                        if attempt > 1:  # 如果进行了重试
                            raise RetryExhaustedError(
                                f"Maximum retry attempts ({retry_strategy.config.max_retries}) "
                                f"exceeded. Last error: {converted_exception}"
                            ) from converted_exception
                        else:
                            raise converted_exception
                    
                    # 判断是否应该重试
                    if not retry_strategy.should_retry(e):
                        raise retry_strategy.convert_exception(e)
                    
                    # 计算延迟时间并等待
                    delay = retry_strategy.get_delay(attempt)
                    
                    # 记录重试日志
                    url = kwargs.get('url', args[1] if len(args) > 1 else 'unknown')
                    retry_strategy.logger.log_retry(
                        attempt, retry_strategy.config.max_retries, delay, e, url
                    )
                    
                    time.sleep(delay)
            
            # 理论上不会到达这里
            raise RetryExhaustedError("Unexpected retry loop exit")
        
        return wrapper
    return decorator


def with_async_retry(retry_strategy: RetryStrategy):
    """异步重试装饰器"""
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, retry_strategy.config.max_retries + 2):  # +1 for initial attempt
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # 如果是最后一次尝试，直接抛出异常
                    if attempt > retry_strategy.config.max_retries:
                        converted_exception = retry_strategy.convert_exception(e)
                        if attempt > 1:  # 如果进行了重试
                            raise RetryExhaustedError(
                                f"Maximum retry attempts ({retry_strategy.config.max_retries}) "
                                f"exceeded. Last error: {converted_exception}"
                            ) from converted_exception
                        else:
                            raise converted_exception
                    
                    # 判断是否应该重试
                    if not retry_strategy.should_retry(e):
                        raise retry_strategy.convert_exception(e)
                    
                    # 计算延迟时间并等待
                    delay = retry_strategy.get_delay(attempt)
                    
                    # 记录重试日志
                    url = kwargs.get('url', args[1] if len(args) > 1 else 'unknown')
                    retry_strategy.logger.log_retry(
                        attempt, retry_strategy.config.max_retries, delay, e, url
                    )
                    
                    await asyncio.sleep(delay)
            
            # 理论上不会到达这里
            raise RetryExhaustedError("Unexpected retry loop exit")
        
        return wrapper
    return decorator