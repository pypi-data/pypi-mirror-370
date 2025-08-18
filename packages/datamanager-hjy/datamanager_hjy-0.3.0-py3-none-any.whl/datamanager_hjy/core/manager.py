"""
数据管理器核心模块

提供统一的数据操作接口，包括CRUD、事务、批量操作等。
"""

import time
from typing import Dict, Any, Optional, List, Union
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy import text, select, update, delete, insert
from loguru import logger

from .config import ConfigManager
from .connection import ConnectionManager
from ..operations.query_builder import QueryBuilder
from ..operations.transaction_manager import TransactionManager
from ..operations.batch_operator import BatchOperator
from ..utils.monitoring import PerformanceMonitor


class DataManager:
    """数据管理器核心类"""
    
    def __init__(self, config_manager: ConfigManager, connection_manager: ConnectionManager):
        """
        初始化数据管理器
        
        Args:
            config_manager: 配置管理器
            connection_manager: 连接管理器
        """
        self.config_manager = config_manager
        self.connection_manager = connection_manager
        self.logger = logger.bind(component="data_manager")
        
        # 性能监控
        self.monitor = PerformanceMonitor()
        
        # 初始化组件
        self._initialize_components()
    
    def _initialize_components(self):
        """初始化各个组件"""
        try:
            # 验证配置
            if not self.config_manager.validate_config():
                raise ValueError("配置验证失败")
            
            # 测试连接
            if not self.connection_manager.health_check():
                raise RuntimeError("数据库连接健康检查失败")
            
            self.logger.info("数据管理器初始化成功")
            
        except Exception as e:
            self.logger.error(f"数据管理器初始化失败: {e}")
            raise
    
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
        start_time = time.time()
        
        try:
            with self.connection_manager.get_session_context(database) as session:
                # 构建插入语句
                stmt = insert(table).values(**data)
                
                # 执行插入
                result = session.execute(stmt)
                session.commit()
                
                # 获取插入的ID
                inserted_id = result.inserted_primary_key[0] if result.inserted_primary_key else None
                
                # 构建返回数据
                result_data = data.copy()
                if inserted_id:
                    result_data['id'] = inserted_id
                
                # 记录性能指标
                execution_time = time.time() - start_time
                self.monitor.record_operation('create', table, execution_time)
                
                self.logger.info(f"数据创建成功: {table}, ID: {inserted_id}")
                return result_data
                
        except Exception as e:
            self.logger.error(f"数据创建失败: {table}, 错误: {e}")
            raise
    
    def query(self, table: str, database: str = 'default') -> QueryBuilder:
        """
        查询数据
        
        Args:
            table: 表名
            database: 数据库名称
            
        Returns:
            查询构建器
        """
        return QueryBuilder(table, self.connection_manager, database)
    
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
        start_time = time.time()
        
        try:
            with self.connection_manager.get_session_context(database) as session:
                # 构建更新语句
                stmt = update(table).values(**data)
                
                # 添加条件
                for key, value in condition.items():
                    stmt = stmt.where(text(f"{key} = :{key}"))
                
                # 执行更新
                result = session.execute(stmt, condition)
                session.commit()
                
                # 记录性能指标
                execution_time = time.time() - start_time
                self.monitor.record_operation('update', table, execution_time)
                
                affected_rows = result.rowcount
                self.logger.info(f"数据更新成功: {table}, 影响行数: {affected_rows}")
                return affected_rows > 0
                
        except Exception as e:
            self.logger.error(f"数据更新失败: {table}, 错误: {e}")
            raise
    
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
        start_time = time.time()
        
        try:
            with self.connection_manager.get_session_context(database) as session:
                # 构建删除语句
                stmt = delete(table)
                
                # 添加条件
                for key, value in condition.items():
                    stmt = stmt.where(text(f"{key} = :{key}"))
                
                # 执行删除
                result = session.execute(stmt, condition)
                session.commit()
                
                # 记录性能指标
                execution_time = time.time() - start_time
                self.monitor.record_operation('delete', table, execution_time)
                
                affected_rows = result.rowcount
                self.logger.info(f"数据删除成功: {table}, 影响行数: {affected_rows}")
                return affected_rows > 0
                
        except Exception as e:
            self.logger.error(f"数据删除失败: {table}, 错误: {e}")
            raise
    
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
        start_time = time.time()
        
        try:
            batch_operator = BatchOperator(self.connection_manager)
            result = batch_operator.batch_insert(table, data_list, database)
            
            # 记录性能指标
            execution_time = time.time() - start_time
            self.monitor.record_operation('batch_create', table, execution_time, len(data_list))
            
            self.logger.info(f"批量数据创建成功: {table}, 数量: {len(result)}")
            return result
            
        except Exception as e:
            self.logger.error(f"批量数据创建失败: {table}, 错误: {e}")
            raise
    
    def transaction(self, database: str = 'default') -> TransactionManager:
        """
        事务管理器
        
        Args:
            database: 数据库名称
            
        Returns:
            事务管理器
        """
        return TransactionManager(self.connection_manager, database)
    
    def multi_database_transaction(self, databases: List[str]):
        """
        跨数据库事务管理器
        
        Args:
            databases: 数据库名称列表
            
        Returns:
            跨数据库事务管理器
        """
        return TransactionManager(self.connection_manager, databases)
    
    def get_config(self, key: str) -> Any:
        """
        获取配置
        
        Args:
            key: 配置键
            
        Returns:
            配置值
        """
        return self.config_manager.get_config(key)
    
    def update_config(self, key: str, value: Any) -> bool:
        """
        更新配置
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            是否更新成功
        """
        return self.config_manager.update_config(key, value)
    
    def reload_config(self) -> bool:
        """
        重新加载配置
        
        Returns:
            是否重新加载成功
        """
        return self.config_manager.reload_config()
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        获取性能指标
        
        Returns:
            性能指标字典
        """
        metrics = {
            'performance': self.monitor.get_metrics(),
            'connections': self.connection_manager.get_all_stats(),
            'config': {
                'databases': list(self.config_manager.config.databases.keys()),
                'monitoring_enabled': self.config_manager.config.monitoring.enabled,
                'cache_enabled': self.config_manager.config.cache.enabled
            }
        }
        
        return metrics
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        获取连接状态
        
        Returns:
            连接状态字典
        """
        return self.connection_manager.get_all_stats()
    
    def get_slow_queries(self) -> List[Dict[str, Any]]:
        """
        获取慢查询列表
        
        Returns:
            慢查询列表
        """
        return self.monitor.get_slow_queries()
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            系统是否健康
        """
        try:
            # 检查配置
            if not self.config_manager.validate_config():
                self.logger.error("配置健康检查失败")
                return False
            
            # 检查连接
            if not self.connection_manager.health_check():
                self.logger.error("连接健康检查失败")
                return False
            
            # 检查性能监控
            if not self.monitor.is_healthy():
                self.logger.error("性能监控健康检查失败")
                return False
            
            self.logger.debug("健康检查通过")
            return True
            
        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            return False
    
    def close(self):
        """关闭数据管理器"""
        try:
            self.connection_manager.close_all()
            self.logger.info("数据管理器已关闭")
        except Exception as e:
            self.logger.error(f"关闭数据管理器失败: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
