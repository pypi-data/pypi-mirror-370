"""
数据库适配器工厂

根据配置自动创建对应的数据库适配器实例。
"""

from typing import Dict, Any, Type
from .base import DatabaseAdapter
from .mysql import MySQLAdapter
from .postgresql import PostgreSQLAdapter
from .sqlite import SQLiteAdapter
from ..utils.exceptions import ConfigurationError


class AdapterFactory:
    """数据库适配器工厂"""
    
    # 支持的数据库类型映射
    _ADAPTER_MAP: Dict[str, Type[DatabaseAdapter]] = {
        'mysql': MySQLAdapter,
        'postgresql': PostgreSQLAdapter,
        'sqlite': SQLiteAdapter,
        'postgres': PostgreSQLAdapter,  # 别名支持
        'sqlite3': SQLiteAdapter,       # 别名支持
    }
    
    @classmethod
    def create_adapter(cls, config: Dict[str, Any]) -> DatabaseAdapter:
        """
        根据配置创建数据库适配器
        
        Args:
            config: 数据库配置
            
        Returns:
            数据库适配器实例
            
        Raises:
            ConfigurationError: 配置错误或不支持的数据库类型
        """
        if not config:
            raise ConfigurationError("数据库配置不能为空")
        
        # 获取数据库类型
        db_type = config.get('type', '').lower()
        if not db_type:
            raise ConfigurationError("数据库配置中缺少 'type' 字段")
        
        # 检查是否支持该数据库类型
        if db_type not in cls._ADAPTER_MAP:
            supported_types = list(cls._ADAPTER_MAP.keys())
            raise ConfigurationError(
                f"不支持的数据库类型: {db_type}. "
                f"支持的数据库类型: {', '.join(supported_types)}"
            )
        
        # 创建适配器实例
        adapter_class = cls._ADAPTER_MAP[db_type]
        return adapter_class(config)
    
    @classmethod
    def get_supported_types(cls) -> list:
        """
        获取支持的数据库类型列表
        
        Returns:
            支持的数据库类型列表
        """
        return list(cls._ADAPTER_MAP.keys())
    
    @classmethod
    def register_adapter(cls, db_type: str, adapter_class: Type[DatabaseAdapter]) -> None:
        """
        注册新的数据库适配器
        
        Args:
            db_type: 数据库类型名称
            adapter_class: 适配器类
        """
        if not issubclass(adapter_class, DatabaseAdapter):
            raise ValueError(f"适配器类必须继承自 DatabaseAdapter: {adapter_class}")
        
        cls._ADAPTER_MAP[db_type.lower()] = adapter_class
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> bool:
        """
        验证数据库配置
        
        Args:
            config: 数据库配置
            
        Returns:
            配置是否有效
        """
        try:
            # 检查必需字段
            if not config:
                return False
            
            db_type = config.get('type', '').lower()
            if not db_type:
                return False
            
            if db_type not in cls._ADAPTER_MAP:
                return False
            
            # 根据数据库类型验证特定字段
            if db_type in ['mysql', 'postgresql']:
                required_fields = ['host', 'database', 'username', 'password']
                for field in required_fields:
                    if field not in config or not config[field]:
                        return False
            
            elif db_type == 'sqlite':
                if 'database' not in config or not config['database']:
                    return False
            
            return True
            
        except Exception:
            return False
    
    @classmethod
    def get_adapter_info(cls, db_type: str) -> Dict[str, Any]:
        """
        获取适配器信息
        
        Args:
            db_type: 数据库类型
            
        Returns:
            适配器信息字典
        """
        if db_type not in cls._ADAPTER_MAP:
            return {}
        
        adapter_class = cls._ADAPTER_MAP[db_type]
        
        # 创建临时实例获取信息
        temp_config = {
            'type': db_type,
            'host': 'localhost',
            'database': 'temp_db',
            'username': 'temp_user',
            'password': 'temp_pass'
        }
        
        try:
            adapter = adapter_class(temp_config)
            return {
                'type': db_type,
                'class_name': adapter_class.__name__,
                'module': adapter_class.__module__,
                'features': adapter.get_mysql_specific_features() if hasattr(adapter, 'get_mysql_specific_features') else {},
                'connection_string_template': adapter.get_connection_string()
            }
        except Exception:
            return {
                'type': db_type,
                'class_name': adapter_class.__name__,
                'module': adapter_class.__module__,
                'features': {},
                'connection_string_template': ''
            }


# 便捷函数
def create_adapter(config: Dict[str, Any]) -> DatabaseAdapter:
    """
    便捷函数：创建数据库适配器
    
    Args:
        config: 数据库配置
        
    Returns:
        数据库适配器实例
    """
    return AdapterFactory.create_adapter(config)


def get_supported_types() -> list:
    """
    便捷函数：获取支持的数据库类型
    
    Returns:
        支持的数据库类型列表
    """
    return AdapterFactory.get_supported_types()


def validate_config(config: Dict[str, Any]) -> bool:
    """
    便捷函数：验证数据库配置
    
    Args:
        config: 数据库配置
        
    Returns:
        配置是否有效
    """
    return AdapterFactory.validate_config(config)
