"""HTTP客户端核心实现"""

import time
from typing import Dict, Any, Optional, Union
from contextlib import asynccontextmanager, contextmanager

import httpx

from .config import ClientConfig
from .models import Response, RequestModel
from .logger import HttpLogger
from .retry import RetryStrategy, with_retry, with_async_retry
from .exceptions import (
    HttpClientError,
    ValidationError,
    HttpStatusError
)


class HttpClient:
    """HTTP客户端类
    
    基于httpx和pydantic的HTTP客户端，支持同步和异步调用，
    具备完善的请求响应校验、日志记录、超时控制和智能重试机制。
    请求中的headers会和默认headers合并，且默认同时生效.
    如果要禁用默认headers, 可以在请求中传入default_headers = False

    
    """
    
    def __init__(self, config: Optional[ClientConfig] = None):
        """初始化HTTP客户端
        
        Args:
            config: 客户端配置，如果为None则使用默认配置
        """
        self.config = config or ClientConfig()
        self.logger = HttpLogger(self.config)
        self.retry_strategy = RetryStrategy(self.config, self.logger)
        
        # 创建httpx客户端配置
        self._client_kwargs = self._build_client_kwargs()
        
        # 同步和异步客户端将在需要时创建
        self._sync_client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None
    
    def _build_client_kwargs(self) -> Dict[str, Any]:
        """构建httpx客户端参数"""
        timeout_config = httpx.Timeout(
            connect=self.config.connect_timeout,
            read=self.config.read_timeout,
            write=self.config.timeout,
            pool=self.config.timeout
        )
        
        return {
            "timeout": timeout_config,
            "headers": self.config.headers,
            "follow_redirects": self.config.follow_redirects,
            "verify": self.config.verify_ssl
        }
    
    @property
    def sync_client(self) -> httpx.Client:
        """获取同步客户端"""
        if self._sync_client is None:
            self._sync_client = httpx.Client(**self._client_kwargs)
        return self._sync_client
    
    @property
    def async_client(self) -> httpx.AsyncClient:
        """获取异步客户端"""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(**self._client_kwargs)
        return self._async_client
    
    def close(self) -> None:
        """关闭同步客户端"""
        if self._sync_client is not None:
            self._sync_client.close()
            self._sync_client = None
    
    async def aclose(self) -> None:
        """关闭异步客户端"""
        if self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.aclose()
    
    def _prepare_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """准备请求参数"""
        # 检查是否禁用默认headers
        disable_default_headers = kwargs.pop('default_headers', True) is False
        
        # 验证请求模型
        try:
            request_model = RequestModel(
                method=method,
                url=url,
                headers=kwargs.get('headers'),
                params=kwargs.get('params'),
                data=kwargs.get('data'),
                json_data=kwargs.get('json'),
                timeout=kwargs.get('timeout')
            )
        except Exception as e:
            raise ValidationError(f"Request validation failed: {e}")
        
        # 构建请求参数
        request_kwargs = {
            'method': request_model.method,
            'url': request_model.url
        }
        
        # 处理headers
        if disable_default_headers:
            # 如果禁用默认headers，总是传递headers参数来覆盖默认行为
            if request_model.headers:
                # 有自定义headers时使用自定义headers
                request_kwargs['headers'] = request_model.headers
            else:
                # 没有自定义headers时传递空字典来禁用默认headers
                request_kwargs['headers'] = {}
            request_kwargs['disable_default_headers'] = True

        else:
            # 正常情况下，只有在有请求级别headers时才添加
            if request_model.headers:
                request_kwargs['headers'] = request_model.headers
        
        if request_model.params:
            request_kwargs['params'] = request_model.params
        
        if request_model.data is not None:
            request_kwargs['data'] = request_model.data
        
        if request_model.json_data is not None:
            request_kwargs['json'] = request_model.json_data
        
        if request_model.timeout is not None:
            request_kwargs['timeout'] = request_model.timeout
        
        # 添加其他httpx支持的参数
        for key in ['cookies', 'auth', 'files', 'content']:
            if key in kwargs:
                request_kwargs[key] = kwargs[key]
        
        return request_kwargs
    
    def _make_sync_request(self, **request_kwargs) -> Response:
        """执行同步请求（带重试）"""
        method = request_kwargs['method']
        url = request_kwargs['url']
        
        # 记录请求日志
        self.logger.log_request(
            method=method,
            url=url,
            headers=request_kwargs.get('headers'),
            data=request_kwargs.get('data') or request_kwargs.get('json')
        )
        
        start_time = time.time()
        
        try:
            # 检查是否需要使用无默认headers的客户端
            if request_kwargs.pop('disable_default_headers', False):
                # 创建临时的无默认headers的客户端
                temp_kwargs = self._client_kwargs.copy()
                temp_kwargs['headers'] = request_kwargs.pop('headers', {})
                with httpx.Client(**temp_kwargs) as temp_client:
                    httpx_response = temp_client.request(**request_kwargs)
            else:
                # 使用正常的客户端
                httpx_response = self.sync_client.request(**request_kwargs)
            
            elapsed = time.time() - start_time
            
            # 记录响应日志
            self.logger.log_response(
                status_code=httpx_response.status_code,
                url=url,
                elapsed=elapsed,
                headers=dict(httpx_response.headers),
                content_length=len(httpx_response.content)
            )
            
            # 创建响应对象
            response = Response.from_httpx_response(httpx_response, elapsed)
            
            return response
            
        except Exception as e:
            elapsed = time.time() - start_time
            self.logger.log_error(e, url, method)
            raise
    
    async def _make_async_request(self, **request_kwargs) -> Response:
        """执行异步请求（带重试）"""
        method = request_kwargs['method']
        url = request_kwargs['url']
        
        # 记录请求日志
        self.logger.log_request(
            method=method,
            url=url,
            headers=request_kwargs.get('headers'),
            data=request_kwargs.get('data') or request_kwargs.get('json')
        )
        
        start_time = time.time()
        
        try:
            # 检查是否需要使用无默认headers的客户端
            if request_kwargs.pop('disable_default_headers', False):
                # 创建临时的无默认headers的客户端
                temp_kwargs = self._client_kwargs.copy()
                temp_kwargs['headers'] = request_kwargs.pop('headers', {})
                async with httpx.AsyncClient(**temp_kwargs) as temp_client:
                    httpx_response = await temp_client.request(**request_kwargs)
            else:
                # 使用正常的客户端
                httpx_response = await self.async_client.request(**request_kwargs)
            
            elapsed = time.time() - start_time
            
            # 记录响应日志
            self.logger.log_response(
                status_code=httpx_response.status_code,
                url=url,
                elapsed=elapsed,
                headers=dict(httpx_response.headers),
                content_length=len(httpx_response.content)
            )
            
            # 创建响应对象
            response = Response.from_httpx_response(httpx_response, elapsed)
            
            return response
            
        except Exception as e:
            elapsed = time.time() - start_time
            self.logger.log_error(e, url, method)
            raise
    
    # 同步方法
    def request(self, method: str, url: str, **kwargs) -> Response:
        """发送HTTP请求
        
        Args:
            method: HTTP方法
            url: 请求URL
            **kwargs: 其他请求参数
            
        Returns:
            Response: 响应对象
        """
        request_kwargs = self._prepare_request(method, url, **kwargs)
        # 应用重试装饰器
        retry_func = with_retry(self.retry_strategy)(self._make_sync_request)
        return retry_func(**request_kwargs)
    
    def get(self, url: str, **kwargs) -> Response:
        """发送GET请求"""
        return self.request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> Response:
        """发送POST请求"""
        return self.request('POST', url, **kwargs)
    
    def put(self, url: str, **kwargs) -> Response:
        """发送PUT请求"""
        return self.request('PUT', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> Response:
        """发送DELETE请求"""
        return self.request('DELETE', url, **kwargs)
    
    def patch(self, url: str, **kwargs) -> Response:
        """发送PATCH请求"""
        return self.request('PATCH', url, **kwargs)
    
    def head(self, url: str, **kwargs) -> Response:
        """发送HEAD请求"""
        return self.request('HEAD', url, **kwargs)
    
    def options(self, url: str, **kwargs) -> Response:
        """发送OPTIONS请求"""
        return self.request('OPTIONS', url, **kwargs)
    
    # 异步方法
    async def arequest(self, method: str, url: str, **kwargs) -> Response:
        """发送异步HTTP请求
        
        Args:
            method: HTTP方法
            url: 请求URL
            **kwargs: 其他请求参数
            
        Returns:
            Response: 响应对象
        """
        request_kwargs = self._prepare_request(method, url, **kwargs)
        # 应用重试装饰器
        retry_func = with_async_retry(self.retry_strategy)(self._make_async_request)
        return await retry_func(**request_kwargs)
    
    async def aget(self, url: str, **kwargs) -> Response:
        """发送异步GET请求"""
        return await self.arequest('GET', url, **kwargs)
    
    async def apost(self, url: str, **kwargs) -> Response:
        """发送异步POST请求"""
        return await self.arequest('POST', url, **kwargs)
    
    async def aput(self, url: str, **kwargs) -> Response:
        """发送异步PUT请求"""
        return await self.arequest('PUT', url, **kwargs)
    
    async def adelete(self, url: str, **kwargs) -> Response:
        """发送异步DELETE请求"""
        return await self.arequest('DELETE', url, **kwargs)
    
    async def apatch(self, url: str, **kwargs) -> Response:
        """发送异步PATCH请求"""
        return await self.arequest('PATCH', url, **kwargs)
    
    async def ahead(self, url: str, **kwargs) -> Response:
        """发送异步HEAD请求"""
        return await self.arequest('HEAD', url, **kwargs)
    
    async def aoptions(self, url: str, **kwargs) -> Response:
        """发送异步OPTIONS请求"""
        return await self.arequest('OPTIONS', url, **kwargs)