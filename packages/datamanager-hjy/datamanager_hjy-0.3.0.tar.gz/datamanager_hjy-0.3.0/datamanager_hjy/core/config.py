"""
配置管理模块

负责配置的加载、验证、更新和管理。
"""

import os
import yaml
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from pydantic import BaseModel, Field, validator
from loguru import logger


class DatabaseConfig(BaseModel):
    """数据库配置模型"""
    type: str = Field(..., description="数据库类型")
    host: str = Field(..., description="数据库主机")
    port: int = Field(3306, description="数据库端口")
    database: str = Field(..., description="数据库名称")
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    pool_size: int = Field(10, description="连接池大小")
    max_overflow: int = Field(20, description="最大溢出连接数")
    pool_timeout: int = Field(30, description="连接池超时时间")
    pool_recycle: int = Field(3600, description="连接回收时间")
    
    @validator('type')
    def validate_type(cls, v):
        """验证数据库类型"""
        valid_types = ['mysql', 'postgresql', 'sqlite']
        if v not in valid_types:
            raise ValueError(f'不支持的数据库类型: {v}')
        return v


class ModelConfig(BaseModel):
    """模型配置"""
    auto_discover: bool = Field(True, description="自动发现模型")
    base_path: str = Field("models", description="模型基础路径")
    cache_enabled: bool = Field(True, description="启用缓存")
    cache_ttl: int = Field(3600, description="缓存TTL")
    relationship_auto_load: bool = Field(True, description="自动加载关系")


class MonitoringConfig(BaseModel):
    """监控配置"""
    enabled: bool = Field(True, description="启用监控")
    metrics_collection: bool = Field(True, description="收集指标")
    slow_query_threshold: int = Field(1000, description="慢查询阈值(ms)")
    connection_monitoring: bool = Field(True, description="连接监控")
    performance_tracking: bool = Field(True, description="性能跟踪")


class CacheConfig(BaseModel):
    """缓存配置"""
    enabled: bool = Field(True, description="启用缓存")
    redis_url: str = Field("redis://localhost:6379/0", description="Redis URL")
    default_ttl: int = Field(3600, description="默认TTL")
    key_prefix: str = Field("datamanager:", description="键前缀")


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = Field("INFO", description="日志级别")
    format: str = Field(
        "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        description="日志格式"
    )
    file: str = Field("logs/datamanager.log", description="日志文件")


class DataManagerConfig(BaseModel):
    """数据管理器配置"""
    databases: Dict[str, DatabaseConfig] = Field(..., description="数据库配置")
    models: ModelConfig = Field(default_factory=ModelConfig, description="模型配置")
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig, description="监控配置")
    cache: CacheConfig = Field(default_factory=CacheConfig, description="缓存配置")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="日志配置")


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config: Optional[DataManagerConfig] = None
        self.db_config: Optional[Dict[str, Any]] = None
        self.logger = logger.bind(component="config_manager")
        
        # 设置配置文件路径
        self.config_path = config_path or self._get_default_config_path()
        
        # 加载配置
        self.load_config()
    
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        # 查找配置文件
        possible_paths = [
            "config.yaml",
            "config.yml", 
            "datamanager_config.yaml",
            "datamanager_config.yml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"找到配置文件: {path}")
                return path
        
        # 如果没找到，创建默认配置
        default_config = self._create_default_config()
        with open("config.yaml", "w", encoding="utf-8") as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
        
        self.logger.info("创建默认配置文件: config.yaml")
        return "config.yaml"
    
    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        return {
            "databases": {
                "default": {
                    "type": "mysql",
                    "host": "${DB_HOST}",
                    "port": "${DB_PORT}",
                    "database": "${DB_NAME}",
                    "username": "${DB_USER}",
                    "password": "${DB_PASSWORD}",
                    "pool_size": 10,
                    "max_overflow": 20,
                    "pool_timeout": 30,
                    "pool_recycle": 3600
                }
            },
            "models": {
                "auto_discover": True,
                "base_path": "models",
                "cache_enabled": True,
                "cache_ttl": 3600,
                "relationship_auto_load": True
            },
            "monitoring": {
                "enabled": True,
                "metrics_collection": True,
                "slow_query_threshold": 1000,
                "connection_monitoring": True,
                "performance_tracking": True
            },
            "cache": {
                "enabled": True,
                "redis_url": "${REDIS_URL}",
                "default_ttl": 3600,
                "key_prefix": "datamanager:"
            },
            "logging": {
                "level": "INFO",
                "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
                "file": "logs/datamanager.log"
            }
        }
    
    def _load_yaml_config(self) -> Dict[str, Any]:
        """加载YAML配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            self.logger.info(f"配置文件加载成功: {self.config_path}")
            return config_data
        except Exception as e:
            self.logger.error(f"配置文件加载失败: {e}")
            raise
    
    def _replace_env_vars(self, value: Any) -> Any:
        """替换环境变量"""
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            env_value = os.getenv(env_var)
            if env_value is None:
                self.logger.warning(f"环境变量未设置: {env_var}")
                return value
            return env_value
        elif isinstance(value, dict):
            return {k: self._replace_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._replace_env_vars(v) for v in value]
        else:
            return value
    
    def load_config(self) -> DataManagerConfig:
        """
        加载配置
        
        Returns:
            配置对象
        """
        try:
            # 加载YAML配置
            config_data = self._load_yaml_config()
            
            # 替换环境变量
            config_data = self._replace_env_vars(config_data)
            
            # 验证配置
            self.config = DataManagerConfig(**config_data)
            
            self.logger.info("配置加载和验证成功")
            return self.config
            
        except Exception as e:
            self.logger.error(f"配置加载失败: {e}")
            raise
    
    def get_database_config(self, name: str = 'default') -> DatabaseConfig:
        """
        获取数据库配置
        
        Args:
            name: 数据库名称
            
        Returns:
            数据库配置
        """
        if not self.config:
            raise ValueError("配置未加载")
        
        if name not in self.config.databases:
            raise ValueError(f"数据库配置不存在: {name}")
        
        return self.config.databases[name]
    
    def get_config(self, key: str) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔
            
        Returns:
            配置值
        """
        if not self.config:
            raise ValueError("配置未加载")
        
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            elif isinstance(value, dict) and k in value:
                value = value[k]
            else:
                raise KeyError(f"配置键不存在: {key}")
        
        return value
    
    def update_config(self, key: str, value: Any) -> bool:
        """
        更新配置
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            是否更新成功
        """
        try:
            # 这里应该实现配置的动态更新
            # 暂时只记录日志
            self.logger.info(f"配置更新: {key} = {value}")
            return True
        except Exception as e:
            self.logger.error(f"配置更新失败: {e}")
            return False
    
    def reload_config(self) -> bool:
        """
        重新加载配置
        
        Returns:
            是否重新加载成功
        """
        try:
            self.load_config()
            self.logger.info("配置重新加载成功")
            return True
        except Exception as e:
            self.logger.error(f"配置重新加载失败: {e}")
            return False
    
    def validate_config(self) -> bool:
        """
        验证配置
        
        Returns:
            配置是否有效
        """
        try:
            if not self.config:
                return False
            
            # 验证数据库配置
            for name, db_config in self.config.databases.items():
                if not db_config.host or not db_config.database:
                    self.logger.error(f"数据库配置无效: {name}")
                    return False
            
            self.logger.info("配置验证通过")
            return True
            
        except Exception as e:
            self.logger.error(f"配置验证失败: {e}")
            return False
