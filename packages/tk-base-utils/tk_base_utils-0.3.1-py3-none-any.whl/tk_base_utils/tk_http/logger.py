"""HTTP客户端日志管理"""

import logging
import time
import os
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, Optional
from .config import ClientConfig


class HttpLogger:
    """HTTP客户端日志管理器"""
    
    def __init__(self, config: ClientConfig):
        self.config = config
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        # 使用唯一的logger名称避免冲突
        logger_name = f"http_client_{id(self)}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, self.config.log_level.upper()))
        
        # 清除现有handlers
        logger.handlers.clear()
        
        # 控制台handler
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 文件handler（如果配置了日志文件路径）
        if self.config.log_file_path:
            self._add_file_handler(logger, formatter)
        
        return logger
    
    def _add_file_handler(self, logger: logging.Logger, formatter: logging.Formatter) -> None:
        """添加文件日志处理器"""
        try:
            # 确保日志目录存在
            log_dir = os.path.dirname(self.config.log_file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # 根据配置决定使用哪种文件处理器
            if self.config.log_file_rotation_enabled:
                # 使用RotatingFileHandler进行日志轮转
                file_handler = RotatingFileHandler(
                    filename=self.config.log_file_path,
                    maxBytes=self.config.log_file_max_size,
                    backupCount=self.config.log_file_backup_count,
                    encoding='utf-8'
                )
            else:
                # 使用普通FileHandler，不进行轮转（适用于共享日志文件的场景）
                file_handler = logging.FileHandler(
                    filename=self.config.log_file_path,
                    encoding='utf-8'
                )
            
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            # 如果文件handler创建失败，记录警告但不影响程序运行
            logger.warning(f"Failed to create file handler for {self.config.log_file_path}: {e}")
    
    def log_request(self, method: str, url: str, headers: Optional[Dict[str, str]] = None, 
                   data: Any = None) -> None:
        """记录请求日志"""
        if not self.config.log_requests:
            return
        
        log_data = {
            "type": "request",
            "method": method,
            "url": url,
            "timestamp": time.time()
        }
        
        if headers:
            # 过滤敏感信息
            safe_headers = self._filter_sensitive_headers(headers)
            log_data["headers"] = safe_headers
        
        if data and self.logger.isEnabledFor(logging.DEBUG):
            log_data["data"] = str(data)[:500]  # 限制数据长度
        
        self.logger.info(f"Request: {method} {url}")
        self.logger.debug(f"Request details: {log_data}")
    
    def log_response(self, status_code: int, url: str, elapsed: float, 
                    headers: Optional[Dict[str, str]] = None, 
                    content_length: Optional[int] = None) -> None:
        """记录响应日志"""
        if not self.config.log_responses:
            return
        
        log_data = {
            "type": "response",
            "status_code": status_code,
            "url": url,
            "elapsed": elapsed,
            "timestamp": time.time()
        }
        
        if headers:
            safe_headers = self._filter_sensitive_headers(headers)
            log_data["headers"] = safe_headers
        
        if content_length is not None:
            log_data["content_length"] = content_length
        
        level = logging.INFO if 200 <= status_code < 400 else logging.WARNING
        self.logger.log(level, f"Response: {status_code} {url} ({elapsed:.3f}s)")
        self.logger.debug(f"Response details: {log_data}")
    
    def log_retry(self, attempt: int, max_retries: int, delay: float, 
                 error: Exception, url: str) -> None:
        """记录重试日志"""
        self.logger.warning(
            f"Retry {attempt}/{max_retries} for {url} after {delay:.1f}s delay. "
            f"Error: {type(error).__name__}: {error}"
        )
    
    def log_error(self, error: Exception, url: str, method: str) -> None:
        """记录错误日志"""
        self.logger.error(
            f"Error in {method} {url}: {type(error).__name__}: {error}"
        )
    
    def log_timeout(self, url: str, method: str, timeout: float) -> None:
        """记录超时日志"""
        self.logger.warning(
            f"Timeout ({timeout}s) for {method} {url}"
        )
    
    def log_connection_error(self, url: str, method: str, error: Exception) -> None:
        """记录连接错误日志"""
        self.logger.warning(
            f"Connection error for {method} {url}: {error}"
        )
    
    def _filter_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """过滤敏感的请求头信息"""
        sensitive_keys = {
            'authorization', 'cookie', 'x-api-key', 'x-auth-token',
            'x-access-token', 'bearer', 'api-key', 'auth-token'
        }
        
        filtered = {}
        for key, value in headers.items():
            if key.lower() in sensitive_keys:
                filtered[key] = "***REDACTED***"
            else:
                filtered[key] = value
        
        return filtered