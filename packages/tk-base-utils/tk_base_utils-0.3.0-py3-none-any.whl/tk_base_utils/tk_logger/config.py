"""配置管理模块

负责读取和解析config.toml配置文件。
"""

import tomllib
from typing import Dict, Any
from pathlib import Path

class TkLoggerConfig:
    """日志配置类"""
    
    def __init__(self, config_path: str | Path = "config.toml"):
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "logging": {
                "name": "temp3_logger",
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_path": "logs/app.log",
                "max_bytes": 10485760,  # 10MB
                "backup_count": 5,
                "rotation_type": "size",  # size 或 time
                "rotation_interval": "midnight"
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'rb') as f:
                    config = tomllib.load(f)
                # 合并默认配置和用户配置
                default_config.update(config)
                return default_config
            except Exception as e:
                print(f"警告: 读取配置文件失败 {e}，使用默认配置")
                return default_config
        else:
            # # 如果配置文件不存在，创建默认配置文件
            # self._create_default_config(default_config)
            return default_config
    
    # def _create_default_config(self, config: Dict[str, Any]) -> None:
    #     """创建默认配置文件"""
    #     try:
    #         with open(self.config_path, 'w', encoding='utf-8') as f:
    #             toml.dump(config, f)
    #         print(f"已创建默认配置文件: {self.config_path}")
    #     except Exception as e:
    #         print(f"警告: 创建配置文件失败 {e}")
    
    @property
    def logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self._config.get("logging", {})
    
    @property
    def logger_name(self) -> str:
        """获取日志器名称"""
        return self.logging_config.get("name", "temp3_logger")
    
    @property
    def log_level(self) -> str:
        """获取日志级别"""
        return self.logging_config.get("level", "INFO")
    
    @property
    def log_format(self) -> str:
        """获取日志格式"""
        return self.logging_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    @property
    def log_file_path(self) -> str:
        """获取日志文件路径"""
        return self.logging_config.get("file_path", "logs/app.log")
    
    @property
    def max_bytes(self) -> int:
        """获取日志文件最大字节数"""
        return self.logging_config.get("max_bytes", 10485760)
    
    @property
    def backup_count(self) -> int:
        """获取备份文件数量"""
        return self.logging_config.get("backup_count", 5)
    
    @property
    def rotation_type(self) -> str:
        """获取轮转类型"""
        return self.logging_config.get("rotation_type", "size")
    
    @property
    def rotation_interval(self) -> str:
        """获取轮转时间间隔"""
        return self.logging_config.get("rotation_interval", "midnight")


# 全局配置实例
_config_instance = None


def set_logger_config_path(config_path: str|Path) -> None:
    """设置配置文件路径并重新初始化配置
    
    Args:
        config_path: config.toml文件的路径
    """
    global _config_instance
    _config_instance = TkLoggerConfig(config_path)


def get_logger_config() -> TkLoggerConfig:
    """获取配置实例，如果未初始化则使用默认路径"""
    global _config_instance
    if _config_instance is None:
        _config_instance = TkLoggerConfig()
    return _config_instance


# 为了向后兼容，保持config变量的访问方式
class TkLoggerConfigProxy:
    """配置代理类，确保配置的延迟初始化"""
    
    def __getattr__(self, name):
        return getattr(get_logger_config(), name)


config = TkLoggerConfigProxy()
