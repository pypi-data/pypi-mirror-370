"""
查询构建器

提供链式查询接口，支持复杂的查询条件构建。
"""

from typing import Dict, Any, Optional, List, Union
from sqlalchemy import select, text, and_, or_, desc, asc
from sqlalchemy.orm import Session
from loguru import logger


class QueryBuilder:
    """查询构建器"""
    
    def __init__(self, table: str, connection_manager, database: str = 'default'):
        """
        初始化查询构建器
        
        Args:
            table: 表名
            connection_manager: 连接管理器
            database: 数据库名称
        """
        self.table = table
        self.connection_manager = connection_manager
        self.database = database
        self.logger = logger.bind(component=f"query_builder_{table}")
        
        # 查询状态
        self._select_columns = None
        self._where_conditions = []
        self._order_by_columns = []
        self._limit_count = None
        self._offset_count = None
        self._group_by_columns = []
        self._having_conditions = []
    
    def select(self, *columns) -> 'QueryBuilder':
        """
        选择列
        
        Args:
            *columns: 列名列表
            
        Returns:
            查询构建器
        """
        self._select_columns = columns if columns else None
        return self
    
    def filter(self, **conditions) -> 'QueryBuilder':
        """
        添加过滤条件
        
        Args:
            **conditions: 过滤条件
            
        Returns:
            查询构建器
        """
        for key, value in conditions.items():
            if '__' in key:
                # 处理特殊操作符
                field, operator = key.split('__', 1)
                condition = self._build_condition(field, operator, value)
            else:
                # 简单等值条件
                condition = text(f"{key} = :{key}")
            
            self._where_conditions.append((condition, {key: value}))
        
        return self
    
    def _build_condition(self, field: str, operator: str, value: Any):
        """构建查询条件"""
        if operator == 'eq':
            return text(f"{field} = :{field}")
        elif operator == 'ne':
            return text(f"{field} != :{field}")
        elif operator == 'gt':
            return text(f"{field} > :{field}")
        elif operator == 'gte':
            return text(f"{field} >= :{field}")
        elif operator == 'lt':
            return text(f"{field} < :{field}")
        elif operator == 'lte':
            return text(f"{field} <= :{field}")
        elif operator == 'like':
            return text(f"{field} LIKE :{field}")
        elif operator == 'in':
            return text(f"{field} IN :{field}")
        elif operator == 'not_in':
            return text(f"{field} NOT IN :{field}")
        elif operator == 'is_null':
            return text(f"{field} IS NULL")
        elif operator == 'is_not_null':
            return text(f"{field} IS NOT NULL")
        else:
            raise ValueError(f"不支持的操作符: {operator}")
    
    def order_by(self, *columns) -> 'QueryBuilder':
        """
        排序
        
        Args:
            *columns: 排序列，支持 'column' 或 'column DESC' 格式
            
        Returns:
            查询构建器
        """
        for column in columns:
            if ' DESC' in column.upper():
                field = column.replace(' DESC', '').replace(' desc', '')
                self._order_by_columns.append(desc(field))
            elif ' ASC' in column.upper():
                field = column.replace(' ASC', '').replace(' asc', '')
                self._order_by_columns.append(asc(field))
            else:
                self._order_by_columns.append(asc(column))
        
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """
        限制结果数量
        
        Args:
            count: 限制数量
            
        Returns:
            查询构建器
        """
        self._limit_count = count
        return self
    
    def offset(self, count: int) -> 'QueryBuilder':
        """
        偏移结果
        
        Args:
            count: 偏移数量
            
        Returns:
            查询构建器
        """
        self._offset_count = count
        return self
    
    def group_by(self, *columns) -> 'QueryBuilder':
        """
        分组
        
        Args:
            *columns: 分组列
            
        Returns:
            查询构建器
        """
        self._group_by_columns.extend(columns)
        return self
    
    def having(self, **conditions) -> 'QueryBuilder':
        """
        分组后过滤
        
        Args:
            **conditions: 过滤条件
            
        Returns:
            查询构建器
        """
        for key, value in conditions.items():
            condition = text(f"{key} = :{key}")
            self._having_conditions.append((condition, {key: value}))
        
        return self
    
    def _build_query(self) -> tuple:
        """构建SQL查询"""
        # 构建基础查询
        if self._select_columns:
            stmt = select(*[text(col) for col in self._select_columns]).select_from(text(self.table))
        else:
            stmt = select(text('*')).select_from(text(self.table))
        
        # 添加WHERE条件
        params = {}
        if self._where_conditions:
            where_clauses = []
            for condition, param in self._where_conditions:
                where_clauses.append(condition)
                params.update(param)
            
            if len(where_clauses) == 1:
                stmt = stmt.where(where_clauses[0])
            else:
                stmt = stmt.where(and_(*where_clauses))
        
        # 添加GROUP BY
        if self._group_by_columns:
            stmt = stmt.group_by(*[text(col) for col in self._group_by_columns])
        
        # 添加HAVING
        if self._having_conditions:
            having_clauses = []
            for condition, param in self._having_conditions:
                having_clauses.append(condition)
                params.update(param)
            
            if len(having_clauses) == 1:
                stmt = stmt.having(having_clauses[0])
            else:
                stmt = stmt.having(and_(*having_clauses))
        
        # 添加ORDER BY
        if self._order_by_columns:
            stmt = stmt.order_by(*self._order_by_columns)
        
        # 添加LIMIT
        if self._limit_count is not None:
            stmt = stmt.limit(self._limit_count)
        
        # 添加OFFSET
        if self._offset_count is not None:
            stmt = stmt.offset(self._offset_count)
        
        return stmt, params
    
    def all(self) -> List[Dict[str, Any]]:
        """
        获取所有结果
        
        Returns:
            结果列表
        """
        try:
            with self.connection_manager.get_session_context(self.database) as session:
                stmt, params = self._build_query()
                result = session.execute(stmt, params)
                
                # 转换为字典列表
                rows = []
                for row in result:
                    if hasattr(row, '_mapping'):
                        rows.append(dict(row._mapping))
                    else:
                        rows.append(dict(row))
                
                self.logger.debug(f"查询执行成功: {self.table}, 结果数量: {len(rows)}")
                return rows
                
        except Exception as e:
            self.logger.error(f"查询执行失败: {self.table}, 错误: {e}")
            raise
    
    def first(self) -> Optional[Dict[str, Any]]:
        """
        获取第一个结果
        
        Returns:
            第一个结果，如果没有则返回None
        """
        self.limit(1)
        results = self.all()
        return results[0] if results else None
    
    def count(self) -> int:
        """
        获取结果数量
        
        Returns:
            结果数量
        """
        try:
            with self.connection_manager.get_session_context(self.database) as session:
                # 构建COUNT查询
                stmt = select(text('COUNT(*) as count')).select_from(text(self.table))
                
                # 添加WHERE条件
                params = {}
                if self._where_conditions:
                    where_clauses = []
                    for condition, param in self._where_conditions:
                        where_clauses.append(condition)
                        params.update(param)
                    
                    if len(where_clauses) == 1:
                        stmt = stmt.where(where_clauses[0])
                    else:
                        stmt = stmt.where(and_(*where_clauses))
                
                result = session.execute(stmt, params)
                row = result.first()
                
                count = row[0] if row else 0
                self.logger.debug(f"计数查询执行成功: {self.table}, 数量: {count}")
                return count
                
        except Exception as e:
            self.logger.error(f"计数查询执行失败: {self.table}, 错误: {e}")
            raise
    
    def exists(self) -> bool:
        """
        检查是否存在结果
        
        Returns:
            是否存在结果
        """
        return self.count() > 0
    
    def paginate(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        分页查询
        
        Args:
            page: 页码，从1开始
            per_page: 每页数量
            
        Returns:
            分页结果
        """
        offset = (page - 1) * per_page
        
        # 获取总数
        total = self.count()
        
        # 获取当前页数据
        self.offset(offset).limit(per_page)
        items = self.all()
        
        # 计算分页信息
        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_prev': has_prev,
            'has_next': has_next,
            'prev_page': page - 1 if has_prev else None,
            'next_page': page + 1 if has_next else None
        }
