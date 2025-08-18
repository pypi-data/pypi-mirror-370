"""
datamanager_hjy - 通用的数据管理脚手架

支持多数据库、配置驱动、高性能的数据管理解决方案。
"""

from typing import Dict, Any, Optional, List

# 版本信息
__version__ = "0.0.1"
__author__ = "hjy"
__email__ = "hjy@example.com"

# 主要API类
class DataManager:
    """
    数据管理器 - 主要的用户接口
    
    提供简洁优雅的API来管理数据库操作。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, config_path: Optional[str] = None):
        """
        初始化数据管理器
        
        Args:
            config: 配置字典，如果为None则使用默认配置
            config_path: 配置文件路径，如果为None则使用默认配置文件
        """
        from .core.config import ConfigManager
        from .core.connection import ConnectionManager
        from .core.manager import DataManager as CoreDataManager
        
        self.config_manager = ConfigManager(config_path)
        self.connection_manager = ConnectionManager(config or {})
        self._manager = CoreDataManager(self.config_manager, self.connection_manager)
    
    def create(self, table: str, data: Dict[str, Any], database: str = 'default') -> Dict[str, Any]:
        """
        创建数据
        
        Args:
            table: 表名
            data: 数据字典
            database: 数据库名称
            
        Returns:
            创建的数据记录
        """
        return self._manager.create(table, data, database)
    
    def query(self, table: str, database: str = 'default'):
        """
        查询数据
        
        Args:
            table: 表名
            database: 数据库名称
            
        Returns:
            查询构建器
        """
        return self._manager.query(table, database)
    
    def update(self, table: str, data: Dict[str, Any], condition: Dict[str, Any], 
               database: str = 'default') -> bool:
        """
        更新数据
        
        Args:
            table: 表名
            data: 更新的数据
            condition: 更新条件
            database: 数据库名称
            
        Returns:
            是否更新成功
        """
        return self._manager.update(table, data, condition, database)
    
    def delete(self, table: str, condition: Dict[str, Any], database: str = 'default') -> bool:
        """
        删除数据
        
        Args:
            table: 表名
            condition: 删除条件
            database: 数据库名称
            
        Returns:
            是否删除成功
        """
        return self._manager.delete(table, condition, database)
    
    def batch_create(self, table: str, data_list: List[Dict[str, Any]], 
                     database: str = 'default') -> List[Dict[str, Any]]:
        """
        批量创建数据
        
        Args:
            table: 表名
            data_list: 数据列表
            database: 数据库名称
            
        Returns:
            创建的数据记录列表
        """
        return self._manager.batch_create(table, data_list, database)
    
    def transaction(self, database: str = 'default'):
        """
        事务管理器
        
        Args:
            database: 数据库名称
            
        Returns:
            事务管理器
        """
        return self._manager.transaction(database)
    
    def multi_database_transaction(self, databases: List[str]):
        """
        跨数据库事务管理器
        
        Args:
            databases: 数据库名称列表
            
        Returns:
            跨数据库事务管理器
        """
        return self._manager.multi_database_transaction(databases)
    
    def get_config(self, key: str) -> Any:
        """
        获取配置
        
        Args:
            key: 配置键
            
        Returns:
            配置值
        """
        return self._manager.get_config(key)
    
    def update_config(self, key: str, value: Any) -> bool:
        """
        更新配置
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            是否更新成功
        """
        return self._manager.update_config(key, value)
    
    def reload_config(self) -> bool:
        """
        重新加载配置
        
        Returns:
            是否重新加载成功
        """
        return self._manager.reload_config()
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        获取性能指标
        
        Returns:
            性能指标字典
        """
        return self._manager.get_metrics()
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        获取连接状态
        
        Returns:
            连接状态字典
        """
        return self._manager.get_connection_status()
    
    def get_slow_queries(self) -> List[Dict[str, Any]]:
        """
        获取慢查询列表
        
        Returns:
            慢查询列表
        """
        return self._manager.get_slow_queries()
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            系统是否健康
        """
        return self._manager.health_check()

# 便捷函数
def create_data_manager(config: Optional[Dict[str, Any]] = None) -> DataManager:
    """
    创建数据管理器的便捷函数
    
    Args:
        config: 配置字典
        
    Returns:
        数据管理器实例
    """
    return DataManager(config)

# 导出主要类
__all__ = [
    "DataManager",
    "create_data_manager",
    "ConfigManager",
    "ConnectionManager"
]

# 确保DataManager可以被直接导入
from .core.config import ConfigManager
from .core.connection import ConnectionManager
