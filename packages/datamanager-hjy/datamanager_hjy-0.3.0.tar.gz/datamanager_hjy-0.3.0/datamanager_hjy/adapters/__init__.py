"""
数据库适配器模块

提供不同数据库的统一接口，支持MySQL、PostgreSQL、SQLite等数据库。
"""

from .base import DatabaseAdapter
from .mysql import MySQLAdapter
from .postgresql import PostgreSQLAdapter
from .sqlite import SQLiteAdapter
from .factory import AdapterFactory, create_adapter, get_supported_types, validate_config

__all__ = [
    "DatabaseAdapter",
    "MySQLAdapter", 
    "PostgreSQLAdapter",
    "SQLiteAdapter",
    "AdapterFactory",
    "create_adapter",
    "get_supported_types",
    "validate_config"
]
