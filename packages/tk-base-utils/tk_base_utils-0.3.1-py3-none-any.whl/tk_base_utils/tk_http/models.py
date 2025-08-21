"""HTTP客户端数据模型定义"""

import json
from typing import Dict, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator, PrivateAttr
import httpx

class RequestModel(BaseModel):
    """HTTP请求模型"""
    
    url: str = Field(..., description="请求URL")
    method: str = Field(default="GET", description="HTTP方法")
    headers: Optional[Dict[str, str]] = Field(default=None, description="请求头")
    params: Optional[Dict[str, Any]] = Field(default=None, description="查询参数")
    data: Optional[Union[str, bytes, Dict[str, Any]]] = Field(default=None, description="请求体数据")
    json_data: Optional[Dict[str, Any]] = Field(default=None, description="JSON数据")
    timeout: Optional[float] = Field(default=None, description="超时时间")
    
    @field_validator('method')
    def validate_method(cls, v):
        """验证HTTP方法"""
        allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        if v.upper() not in allowed_methods:
            raise ValueError(f"HTTP method must be one of {allowed_methods}")
        return v.upper()
    
    @field_validator('url')
    def validate_url(cls, v):
        """验证URL格式"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v


class Response(BaseModel):
    """HTTP响应模型"""
    
    status_code: int = Field(..., description="HTTP状态码")
    headers: Dict[str, str] = Field(..., description="响应头")
    content: bytes = Field(..., description="响应内容（字节）")
    json_data: Optional[Dict[str, Any]] = Field(default=None, description="JSON数据")
    elapsed: float = Field(..., description="请求耗时（秒）")
    url: str = Field(..., description="最终请求URL")
    encoding: Optional[str] = Field(default=None, description="响应编码")
    
    # 私有属性
    _text: Optional[str] = PrivateAttr(default=None)
    _httpx_response: Optional[httpx.Response] = PrivateAttr(default=None)
    
    class Config:
        arbitrary_types_allowed = True
    
    @property
    def text(self) -> str:
        """获取响应文本内容，按需解码"""
        if self._text is None:
            if self._httpx_response is not None:
                # 使用httpx的解码逻辑
                self._text = self._httpx_response.text
                # 清空原始响应对象，避免内存泄漏
                self._httpx_response = None
            else:
                # 回退到简单解码
                try:
                    if self.encoding:
                        self._text = self.content.decode(self.encoding)
                    else:
                        self._text = self.content.decode('utf-8')
                except UnicodeDecodeError:
                    self._text = self.content.decode('utf-8', errors='replace')
        return self._text
    
    @classmethod
    def from_httpx_response(cls, response: httpx.Response, elapsed: float) -> 'Response':
        """从httpx响应对象创建Response实例"""
        # 尝试解析JSON
        json_data = None
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                json_data = response.json()
        except (json.JSONDecodeError, ValueError):
            pass
        
        instance = cls(
            status_code=response.status_code,
            headers=dict(response.headers),
            content=response.content,
            json_data=json_data,
            elapsed=elapsed,
            url=str(response.url),
            encoding=response.encoding
        )
        
        # 设置私有属性
        instance._text = None  # 延迟解码
        instance._httpx_response = response  # 保存原始响应对象
        
        return instance
    
    def is_success(self) -> bool:
        """判断请求是否成功"""
        return 200 <= self.status_code < 300
    
    def is_client_error(self) -> bool:
        """判断是否为客户端错误"""
        return 400 <= self.status_code < 500
    
    def is_server_error(self) -> bool:
        """判断是否为服务器错误"""
        return 500 <= self.status_code < 600
    
    def json(self) -> Optional[Dict[str, Any]]:
        """获取JSON数据"""
        return self.json_data
    
    def raise_for_status(self) -> None:
        """如果状态码表示错误则抛出异常"""
        from .exceptions import HttpStatusError
        
        if not self.is_success():
            raise HttpStatusError(
                f"HTTP {self.status_code} error for URL {self.url}",
                self.status_code
            )


class ErrorResponse(BaseModel):
    """错误响应模型"""
    
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    status_code: Optional[int] = Field(default=None, description="HTTP状态码")
    details: Optional[Dict[str, Any]] = Field(default=None, description="错误详情")
    timestamp: str = Field(..., description="错误时间戳")
