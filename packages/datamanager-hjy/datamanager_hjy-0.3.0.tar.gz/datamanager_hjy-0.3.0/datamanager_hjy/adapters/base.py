"""
数据库适配器抽象基类

定义所有数据库适配器必须实现的接口。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from contextlib import contextmanager
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from loguru import logger


class DatabaseAdapter(ABC):
    """数据库适配器抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化数据库适配器
        
        Args:
            config: 数据库配置
        """
        self.config = config
        self.engine: Optional[Engine] = None
        self.session_factory = None
        self.logger = logger.bind(component=f"adapter_{self.get_database_type()}")
        
        # 初始化连接
        self._initialize_connection()
    
    @abstractmethod
    def get_database_type(self) -> str:
        """
        获取数据库类型
        
        Returns:
            数据库类型名称
        """
        pass
    
    @abstractmethod
    def get_connection_string(self) -> str:
        """
        获取连接字符串
        
        Returns:
            数据库连接字符串
        """
        pass
    
    def _initialize_connection(self):
        """初始化数据库连接"""
        try:
            # 创建引擎
            connection_string = self.get_connection_string()
            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=self.config.get('pool_size', 10),
                max_overflow=self.config.get('max_overflow', 20),
                pool_timeout=self.config.get('pool_timeout', 30),
                pool_recycle=self.config.get('pool_recycle', 3600),
                echo=self.config.get('echo', False)
            )
            
            # 创建会话工厂
            self.session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False
            )
            
            self.logger.info(f"{self.get_database_type()} 适配器初始化成功")
            
        except Exception as e:
            self.logger.error(f"{self.get_database_type()} 适配器初始化失败: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Session:
        """
        获取数据库会话
        
        Yields:
            数据库会话
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """
        测试数据库连接
        
        Returns:
            连接是否正常
        """
        try:
            with self.get_session() as session:
                from sqlalchemy import text
                session.execute(text("SELECT 1"))
            self.logger.debug(f"{self.get_database_type()} 连接测试成功")
            return True
        except Exception as e:
            self.logger.error(f"{self.get_database_type()} 连接测试失败: {e}")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        获取连接信息
        
        Returns:
            连接信息字典
        """
        return {
            'type': self.get_database_type(),
            'host': self.config.get('host', 'unknown'),
            'port': self.config.get('port', 'unknown'),
            'database': self.config.get('database', 'unknown'),
            'pool_size': self.config.get('pool_size', 10),
            'max_overflow': self.config.get('max_overflow', 20)
        }
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """
        获取连接池统计信息
        
        Returns:
            连接池统计信息
        """
        if not self.engine:
            return {}
        
        pool = self.engine.pool
        return {
            'total_connections': pool.size(),
            'active_connections': pool.checkedin() + pool.checkedout(),
            'idle_connections': pool.checkedin(),
            'failed_connections': pool.overflow()
        }
    
    def close(self):
        """关闭数据库连接"""
        try:
            if self.engine:
                self.engine.dispose()
            self.logger.info(f"{self.get_database_type()} 适配器已关闭")
        except Exception as e:
            self.logger.error(f"关闭 {self.get_database_type()} 适配器失败: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
