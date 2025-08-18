"""
事务管理器

提供事务管理和跨数据库事务支持。
"""

from typing import Dict, Any, Optional, List, Union
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy import text
from loguru import logger


class TransactionManager:
    """事务管理器"""
    
    def __init__(self, connection_manager, databases: Union[str, List[str]] = 'default'):
        """
        初始化事务管理器
        
        Args:
            connection_manager: 连接管理器
            databases: 数据库名称或数据库名称列表
        """
        self.connection_manager = connection_manager
        self.databases = [databases] if isinstance(databases, str) else databases
        self.logger = logger.bind(component="transaction_manager")
        
        # 事务状态
        self._sessions = {}
        self._committed = False
        self._rolled_back = False
    
    def __enter__(self):
        """上下文管理器入口"""
        self.begin()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
    
    def begin(self):
        """开始事务"""
        try:
            for database in self.databases:
                session = self.connection_manager.get_session(database)
                self._sessions[database] = session
            
            self.logger.debug(f"事务开始: {self.databases}")
            
        except Exception as e:
            self.logger.error(f"事务开始失败: {e}")
            self.rollback()
            raise
    
    def commit(self):
        """提交事务"""
        if self._committed or self._rolled_back:
            return
        
        try:
            for database, session in self._sessions.items():
                session.commit()
                self.logger.debug(f"事务提交成功: {database}")
            
            self._committed = True
            self.logger.info("所有事务提交成功")
            
        except Exception as e:
            self.logger.error(f"事务提交失败: {e}")
            self.rollback()
            raise
        finally:
            self._close_sessions()
    
    def rollback(self):
        """回滚事务"""
        if self._committed or self._rolled_back:
            return
        
        try:
            for database, session in self._sessions.items():
                session.rollback()
                self.logger.debug(f"事务回滚成功: {database}")
            
            self._rolled_back = True
            self.logger.info("所有事务回滚成功")
            
        except Exception as e:
            self.logger.error(f"事务回滚失败: {e}")
            raise
        finally:
            self._close_sessions()
    
    def _close_sessions(self):
        """关闭所有会话"""
        for database, session in self._sessions.items():
            try:
                session.close()
            except Exception as e:
                self.logger.error(f"关闭会话失败: {database}, 错误: {e}")
        
        self._sessions.clear()
    
    def get_session(self, database: str = None) -> Session:
        """
        获取事务会话
        
        Args:
            database: 数据库名称，如果为None则返回第一个数据库的会话
            
        Returns:
            数据库会话
        """
        if not database:
            database = self.databases[0]
        
        if database not in self._sessions:
            raise ValueError(f"数据库 {database} 不在当前事务中")
        
        return self._sessions[database]
    
    def execute(self, sql: str, params: Dict[str, Any] = None, database: str = None):
        """
        执行SQL语句
        
        Args:
            sql: SQL语句
            params: 参数
            database: 数据库名称
            
        Returns:
            执行结果
        """
        session = self.get_session(database)
        return session.execute(text(sql), params or {})
    
    def create(self, table: str, data: Dict[str, Any], database: str = None) -> Dict[str, Any]:
        """
        在事务中创建数据
        
        Args:
            table: 表名
            data: 数据字典
            database: 数据库名称
            
        Returns:
            创建的数据记录
        """
        from sqlalchemy import insert
        
        session = self.get_session(database)
        
        # 构建插入语句
        stmt = insert(table).values(**data)
        
        # 执行插入
        result = session.execute(stmt)
        
        # 获取插入的ID
        inserted_id = result.inserted_primary_key[0] if result.inserted_primary_key else None
        
        # 构建返回数据
        result_data = data.copy()
        if inserted_id:
            result_data['id'] = inserted_id
        
        self.logger.debug(f"事务中创建数据: {table}, ID: {inserted_id}")
        return result_data
    
    def update(self, table: str, data: Dict[str, Any], condition: Dict[str, Any], 
               database: str = None) -> bool:
        """
        在事务中更新数据
        
        Args:
            table: 表名
            data: 更新的数据
            condition: 更新条件
            database: 数据库名称
            
        Returns:
            是否更新成功
        """
        from sqlalchemy import update
        
        session = self.get_session(database)
        
        # 构建更新语句
        stmt = update(table).values(**data)
        
        # 添加条件
        for key, value in condition.items():
            stmt = stmt.where(text(f"{key} = :{key}"))
        
        # 执行更新
        result = session.execute(stmt, condition)
        
        affected_rows = result.rowcount
        self.logger.debug(f"事务中更新数据: {table}, 影响行数: {affected_rows}")
        return affected_rows > 0
    
    def delete(self, table: str, condition: Dict[str, Any], database: str = None) -> bool:
        """
        在事务中删除数据
        
        Args:
            table: 表名
            condition: 删除条件
            database: 数据库名称
            
        Returns:
            是否删除成功
        """
        from sqlalchemy import delete
        
        session = self.get_session(database)
        
        # 构建删除语句
        stmt = delete(table)
        
        # 添加条件
        for key, value in condition.items():
            stmt = stmt.where(text(f"{key} = :{key}"))
        
        # 执行删除
        result = session.execute(stmt, condition)
        
        affected_rows = result.rowcount
        self.logger.debug(f"事务中删除数据: {table}, 影响行数: {affected_rows}")
        return affected_rows > 0
    
    def query(self, table: str, database: str = None):
        """
        在事务中查询数据
        
        Args:
            table: 表名
            database: 数据库名称
            
        Returns:
            查询结果
        """
        from sqlalchemy import select
        
        session = self.get_session(database)
        
        # 构建查询语句
        stmt = select(text('*')).select_from(text(table))
        
        # 执行查询
        result = session.execute(stmt)
        
        # 转换为字典列表
        rows = []
        for row in result:
            if hasattr(row, '_mapping'):
                rows.append(dict(row._mapping))
            else:
                rows.append(dict(row))
        
        self.logger.debug(f"事务中查询数据: {table}, 结果数量: {len(rows)}")
        return rows
    
    def is_active(self) -> bool:
        """
        检查事务是否活跃
        
        Returns:
            事务是否活跃
        """
        return bool(self._sessions) and not self._committed and not self._rolled_back
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取事务状态
        
        Returns:
            事务状态字典
        """
        return {
            'databases': self.databases,
            'active': self.is_active(),
            'committed': self._committed,
            'rolled_back': self._rolled_back,
            'session_count': len(self._sessions)
        }
