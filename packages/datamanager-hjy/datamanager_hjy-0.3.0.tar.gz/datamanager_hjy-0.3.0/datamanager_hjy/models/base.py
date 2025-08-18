"""
基础模型类

提供所有数据模型的基础功能和通用方法。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from loguru import logger


class BaseModel(ABC):
    """基础模型抽象类"""
    
    @classmethod
    @abstractmethod
    def get_table_name(cls) -> str:
        """
        获取表名
        
        Returns:
            表名
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        获取表结构定义
        
        Returns:
            表结构字典
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            字典表示
        """
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                if isinstance(value, datetime):
                    value = value.isoformat()
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """
        从字典创建实例
        
        Args:
            data: 数据字典
            
        Returns:
            模型实例
        """
        instance = cls()
        for key, value in data.items():
            setattr(instance, key, value)
        return instance
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """
        从字典更新实例
        
        Args:
            data: 数据字典
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def create_table_sql(cls) -> str:
        """
        生成创建表的SQL语句
        
        Returns:
            创建表的SQL语句
        """
        table_name = cls.get_table_name()
        schema = cls.get_schema()
        
        columns = []
        for column_name, column_def in schema['columns'].items():
            column_type = column_def['type']
            nullable = 'NOT NULL' if not column_def.get('nullable', True) else ''
            default = f"DEFAULT {column_def['default']}" if 'default' in column_def else ''
            comment = f"COMMENT '{column_def['comment']}'" if 'comment' in column_def else ''
            
            column_sql = f"{column_name} {column_type} {nullable} {default} {comment}".strip()
            columns.append(column_sql)
        
        # 添加主键
        if 'primary_key' in schema:
            columns.append(f"PRIMARY KEY ({schema['primary_key']})")
        
        # 添加索引
        if 'indexes' in schema:
            for index_name, index_def in schema['indexes'].items():
                columns.append(f"INDEX {index_name} ({index_def['columns']})")
        
        # 添加外键
        if 'foreign_keys' in schema:
            for fk_name, fk_def in schema['foreign_keys'].items():
                columns.append(
                    f"FOREIGN KEY ({fk_def['column']}) "
                    f"REFERENCES {fk_def['reference_table']}({fk_def['reference_column']})"
                )
        
        sql = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(columns) + "\n)"
        
        # 添加表注释
        if 'comment' in schema:
            sql += f" COMMENT '{schema['comment']}'"
        
        return sql
    
    @classmethod
    def validate_data(cls, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        验证数据
        
        Args:
            data: 待验证的数据
            
        Returns:
            验证错误信息字典
        """
        errors = {}
        schema = cls.get_schema()
        
        # 检查必需字段
        for column_name, column_def in schema['columns'].items():
            if not column_def.get('nullable', True) and column_name not in data:
                if column_name not in errors:
                    errors[column_name] = []
                errors[column_name].append(f"字段 '{column_name}' 是必需的")
        
        # 检查字段类型和长度
        for column_name, value in data.items():
            if column_name in schema['columns']:
                column_def = schema['columns'][column_name]
                
                # 检查字符串长度
                if column_def['type'].startswith('VARCHAR') and isinstance(value, str):
                    max_length = int(column_def['type'].split('(')[1].split(')')[0])
                    if len(value) > max_length:
                        if column_name not in errors:
                            errors[column_name] = []
                        errors[column_name].append(f"字段 '{column_name}' 长度不能超过 {max_length}")
        
        return errors
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', 'N/A')})>"
    
    def __str__(self) -> str:
        """字符串表示"""
        return self.__repr__()


class TimestampMixin:
    """时间戳混入类"""
    
    def __init__(self):
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_timestamp(self):
        """更新时间戳"""
        self.updated_at = datetime.utcnow()


class SoftDeleteMixin:
    """软删除混入类"""
    
    def __init__(self):
        self.deleted_at = None
        self.is_deleted = False
    
    def soft_delete(self) -> None:
        """软删除"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """恢复删除"""
        self.is_deleted = False
        self.deleted_at = None


class AuditMixin:
    """审计混入类"""
    
    def __init__(self):
        self.created_by = None
        self.updated_by = None
    
    def set_created_by(self, user_id: str) -> None:
        """设置创建者"""
        self.created_by = user_id
    
    def set_updated_by(self, user_id: str) -> None:
        """设置更新者"""
        self.updated_by = user_id
