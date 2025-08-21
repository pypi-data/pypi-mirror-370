"""HTTP客户端配置管理"""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class ClientConfig(BaseModel):
    """HTTP客户端配置类"""
    
    # 超时配置
    timeout: float = Field(default=30.0, description="总超时时间（秒）")
    connect_timeout: float = Field(default=10.0, description="连接超时时间（秒）")
    read_timeout: float = Field(default=30.0, description="读取超时时间（秒）")
    
    # 重试配置
    max_retries: int = Field(default=3, description="最大重试次数")
    retry_delay: float = Field(default=1.0, description="重试基础延迟时间（秒）")
    retry_backoff_factor: float = Field(default=2.0, description="重试退避因子")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_requests: bool = Field(default=True, description="是否记录请求日志")
    log_responses: bool = Field(default=True, description="是否记录响应日志")
    log_file_path: Optional[str] = Field(default=None, description="日志文件路径，如果设置则持久化到文件")
    log_file_max_size: int = Field(default=10*1024*1024, description="日志文件最大大小（字节），默认10MB")
    log_file_backup_count: int = Field(default=5, description="日志文件备份数量")
    log_file_rotation_enabled: bool = Field(default=True, description="是否启用日志文件轮转，当日志文件被多个组件共享时建议设为False")
    
    # 请求配置
    headers: Dict[str, str] = Field(default_factory=dict, description="默认请求头")
    user_agent: str = Field(
        default="HttpClient/0.1.0", 
        description="用户代理"
    )
    
    # HTTP配置
    follow_redirects: bool = Field(default=True, description="是否跟随重定向")
    verify_ssl: bool = Field(default=True, description="是否验证SSL证书")
    
    def model_post_init(self, __context) -> None:
        """模型初始化后处理"""
        # 设置默认User-Agent
        if "User-Agent" not in self.headers:
            self.headers["User-Agent"] = self.user_agent
    
    def get_timeout_config(self) -> Dict[str, float]:
        """获取超时配置"""
        return {
            "timeout": self.timeout,
            "connect": self.connect_timeout,
            "read": self.read_timeout
        }
    
    def get_retry_config(self) -> Dict[str, float]:
        """获取重试配置"""
        return {
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "backoff_factor": self.retry_backoff_factor
        }