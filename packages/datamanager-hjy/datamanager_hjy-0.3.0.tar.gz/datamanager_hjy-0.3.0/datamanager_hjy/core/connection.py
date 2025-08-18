"""
连接管理模块

负责数据库连接的创建、管理和监控。
"""

import time
import threading
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from sqlalchemy import create_engine, Engine, event
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

# 导入适配器
from ..adapters import MySQLAdapter, PostgreSQLAdapter, SQLiteAdapter


class ConnectionPool:
    """连接池管理器"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        初始化连接池
        
        Args:
            name: 连接池名称
            config: 连接配置
        """
        self.name = name
        self.config = config
        self.adapter = None
        self.logger = logger.bind(component=f"connection_pool_{name}")
        
        # 连接统计
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'idle_connections': 0,
            'failed_connections': 0,
            'last_connection_time': None,
            'last_error_time': None,
            'last_error_message': None
        }
        
        self._lock = threading.Lock()
        self._initialize_adapter()
    
    def _get_connection_url(self) -> str:
        """获取连接URL"""
        db_type = self.config['type']
        
        if db_type == 'mysql':
            return (
                f"mysql+pymysql://{self.config['username']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
                f"?charset=utf8mb4"
            )
        elif db_type == 'postgresql':
            return (
                f"postgresql://{self.config['username']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
            )
        elif db_type == 'sqlite':
            return f"sqlite:///{self.config['database']}"
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")
    
    def _initialize_adapter(self):
        """初始化数据库适配器"""
        try:
            db_type = self.config.get('type', 'mysql')
            
            # 根据数据库类型创建适配器
            if db_type == 'mysql':
                self.adapter = MySQLAdapter(self.config)
            elif db_type == 'postgresql':
                self.adapter = PostgreSQLAdapter(self.config)
            elif db_type == 'sqlite':
                self.adapter = SQLiteAdapter(self.config)
            else:
                raise ValueError(f"不支持的数据库类型: {db_type}")
            
            self.logger.info(f"数据库适配器初始化成功: {self.name} ({db_type})")
            
        except Exception as e:
            self.logger.error(f"数据库适配器初始化失败: {e}")
            raise
    
    def _register_engine_events(self):
        """注册引擎事件监听器"""
        if not self.engine:
            return
        
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            with self._lock:
                self.stats['total_connections'] += 1
                self.stats['last_connection_time'] = time.time()
            self.logger.debug(f"数据库连接建立: {self.name}")
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            with self._lock:
                self.stats['active_connections'] += 1
                self.stats['idle_connections'] = max(0, self.stats['idle_connections'] - 1)
            self.logger.debug(f"数据库连接检出: {self.name}")
        
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            with self._lock:
                self.stats['active_connections'] = max(0, self.stats['active_connections'] - 1)
                self.stats['idle_connections'] += 1
            self.logger.debug(f"数据库连接归还: {self.name}")
        
        @event.listens_for(self.engine, "disconnect")
        def receive_disconnect(dbapi_connection, connection_record):
            with self._lock:
                self.stats['failed_connections'] += 1
                self.stats['last_error_time'] = time.time()
            self.logger.warning(f"数据库连接断开: {self.name}")
    
    def get_session(self) -> Session:
        """
        获取数据库会话
        
        Returns:
            数据库会话
        """
        if not self.adapter:
            raise RuntimeError("数据库适配器未初始化")
        
        return self.adapter.get_session()
    
    @contextmanager
    def get_session_context(self):
        """
        获取数据库会话上下文管理器
        
        Yields:
            数据库会话
        """
        if not self.adapter:
            raise RuntimeError("数据库适配器未初始化")
        
        with self.adapter.get_session() as session:
            yield session
    
    def test_connection(self) -> bool:
        """
        测试数据库连接
        
        Returns:
            连接是否正常
        """
        try:
            if not self.adapter:
                return False
            
            result = self.adapter.test_connection()
            if result:
                self.logger.debug(f"数据库连接测试成功: {self.name}")
            return result
        except Exception as e:
            self.logger.error(f"数据库连接测试失败: {self.name}, 错误: {e}")
            with self._lock:
                self.stats['last_error_time'] = time.time()
                self.stats['last_error_message'] = str(e)
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取连接池统计信息
        
        Returns:
            统计信息字典
        """
        with self._lock:
            stats = self.stats.copy()
        
        # 添加适配器统计信息
        if self.adapter:
            pool_stats = self.adapter.get_pool_stats()
            stats.update(pool_stats)
        
        return stats
    
    def close(self):
        """关闭连接池"""
        if self.adapter:
            self.adapter.close()
        self.logger.info(f"数据库连接池已关闭: {self.name}")


class ConnectionManager:
    """连接管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化连接管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.pools: Dict[str, ConnectionPool] = {}
        self.logger = logger.bind(component="connection_manager")
        
        # 初始化连接池
        self._initialize_pools()
    
    def _initialize_pools(self):
        """初始化所有连接池"""
        databases = self.config.get('databases', {})
        
        for name, db_config in databases.items():
            try:
                pool = ConnectionPool(name, db_config)
                self.pools[name] = pool
                self.logger.info(f"连接池初始化成功: {name}")
            except Exception as e:
                self.logger.error(f"连接池初始化失败: {name}, 错误: {e}")
                raise
    
    def get_pool(self, name: str = 'default') -> ConnectionPool:
        """
        获取连接池
        
        Args:
            name: 连接池名称
            
        Returns:
            连接池实例
        """
        if name not in self.pools:
            raise ValueError(f"连接池不存在: {name}")
        
        return self.pools[name]
    
    def get_session(self, database: str = 'default') -> Session:
        """
        获取数据库会话
        
        Args:
            database: 数据库名称
            
        Returns:
            数据库会话
        """
        pool = self.get_pool(database)
        return pool.get_session()
    
    @contextmanager
    def get_session_context(self, database: str = 'default'):
        """
        获取数据库会话上下文管理器
        
        Args:
            database: 数据库名称
            
        Yields:
            数据库会话
        """
        pool = self.get_pool(database)
        with pool.get_session_context() as session:
            yield session
    
    def test_all_connections(self) -> Dict[str, bool]:
        """
        测试所有数据库连接
        
        Returns:
            连接测试结果字典
        """
        results = {}
        
        for name, pool in self.pools.items():
            try:
                results[name] = pool.test_connection()
            except Exception as e:
                self.logger.error(f"连接测试失败: {name}, 错误: {e}")
                results[name] = False
        
        return results
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有连接池的统计信息
        
        Returns:
            统计信息字典
        """
        stats = {}
        
        for name, pool in self.pools.items():
            stats[name] = pool.get_stats()
        
        return stats
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            系统是否健康
        """
        try:
            # 测试所有连接
            results = self.test_all_connections()
            
            # 检查是否有连接失败
            failed_connections = [name for name, success in results.items() if not success]
            
            if failed_connections:
                self.logger.warning(f"连接健康检查失败: {failed_connections}")
                return False
            
            self.logger.debug("连接健康检查通过")
            return True
            
        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            return False
    
    def close_all(self):
        """关闭所有连接池"""
        for name, pool in self.pools.items():
            try:
                pool.close()
                self.logger.info(f"连接池已关闭: {name}")
            except Exception as e:
                self.logger.error(f"关闭连接池失败: {name}, 错误: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close_all()
