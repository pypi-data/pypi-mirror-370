"""
SQLite 数据库适配器

提供 SQLite 数据库的连接和操作接口。
"""

import os
from typing import Dict, Any
from .base import DatabaseAdapter


class SQLiteAdapter(DatabaseAdapter):
    """SQLite 数据库适配器"""
    
    def get_database_type(self) -> str:
        """获取数据库类型"""
        return "sqlite"
    
    def get_connection_string(self) -> str:
        """获取 SQLite 连接字符串"""
        database_path = self.config.get('database', ':memory:')
        
        # 如果是内存数据库
        if database_path == ':memory:':
            return "sqlite:///:memory:"
        
        # 如果是文件路径，确保目录存在
        if not database_path.startswith('/'):
            # 相对路径，转换为绝对路径
            database_path = os.path.abspath(database_path)
        
        # 确保数据库文件所在目录存在
        db_dir = os.path.dirname(database_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # 构建连接字符串
        connection_string = f"sqlite:///{database_path}"
        
        # 添加额外的连接参数
        extra_params = []
        
        # 检查外键约束
        if self.config.get('foreign_keys', True):
            extra_params.append("check_same_thread=False")
        
        # 超时设置
        if self.config.get('timeout'):
            extra_params.append(f"timeout={self.config['timeout']}")
        
        # 添加额外参数到连接字符串
        if extra_params:
            connection_string += "?" + "&".join(extra_params)
        
        return connection_string
    
    def get_sqlite_specific_features(self) -> Dict[str, Any]:
        """
        获取 SQLite 特定功能
        
        Returns:
            SQLite 特定功能字典
        """
        return {
            'supports_json': True,
            'supports_fulltext': True,
            'supports_spatial': False,  # 需要扩展
            'supports_partitioning': False,
            'supports_foreign_keys': True,
            'supports_check_constraints': True,
            'supports_views': True,
            'supports_stored_procedures': False,
            'supports_triggers': True,
            'supports_functions': True,
            'supports_extensions': True,
            'supports_schemas': False,
            'supports_sequences': False,
            'supports_arrays': False,
            'supports_uuid': True,
            'supports_concurrent_access': False,
            'supports_transactions': True
        }
    
    def get_version_info(self) -> Dict[str, Any]:
        """
        获取 SQLite 版本信息
        
        Returns:
            版本信息字典
        """
        try:
            with self.get_session() as session:
                result = session.execute(text("SELECT sqlite_version() as version"))
                version = result.scalar()
                
                # 解析版本信息
                version_parts = version.split('.')
                return {
                    'full_version': version,
                    'major_version': int(version_parts[0]),
                    'minor_version': int(version_parts[1]),
                    'patch_version': int(version_parts[2]) if len(version_parts) > 2 else 0
                }
        except Exception as e:
            self.logger.error(f"获取 SQLite 版本信息失败: {e}")
            return {}
    
    def get_pragma_info(self) -> Dict[str, Any]:
        """
        获取 PRAGMA 信息
        
        Returns:
            PRAGMA 信息字典
        """
        try:
            with self.get_session() as session:
                pragmas = {}
                
                # 获取各种 PRAGMA 设置
                pragma_queries = [
                    "PRAGMA foreign_keys",
                    "PRAGMA journal_mode",
                    "PRAGMA synchronous",
                    "PRAGMA cache_size",
                    "PRAGMA temp_store",
                    "PRAGMA mmap_size",
                    "PRAGMA page_size",
                    "PRAGMA max_page_count"
                ]
                
                for query in pragma_queries:
                    try:
                        result = session.execute(query)
                        value = result.scalar()
                        pragma_name = query.split()[1]
                        pragmas[pragma_name] = value
                    except Exception:
                        continue
                
                return pragmas
        except Exception as e:
            self.logger.error(f"获取 PRAGMA 信息失败: {e}")
            return {}
    
    def get_database_size(self) -> int:
        """
        获取数据库大小（字节）
        
        Returns:
            数据库大小
        """
        try:
            database_path = self.config.get('database', ':memory:')
            
            # 内存数据库
            if database_path == ':memory:':
                return 0
            
            # 文件数据库
            if os.path.exists(database_path):
                return os.path.getsize(database_path)
            else:
                return 0
        except Exception as e:
            self.logger.error(f"获取数据库大小失败: {e}")
            return 0
    
    def get_table_count(self) -> int:
        """
        获取表数量
        
        Returns:
            表数量
        """
        try:
            with self.get_session() as session:
                result = session.execute(text("""
                    SELECT COUNT(*) as count
                    FROM sqlite_master
                    WHERE type = 'table'
                """))
                count = result.scalar()
                return count or 0
        except Exception as e:
            self.logger.error(f"获取表数量失败: {e}")
            return 0
    
    def get_table_info(self) -> Dict[str, Any]:
        """
        获取表信息
        
        Returns:
            表信息字典
        """
        try:
            with self.get_session() as session:
                result = session.execute(text("""
                    SELECT 
                        name as table_name,
                        type,
                        sql
                    FROM sqlite_master
                    WHERE type = 'table'
                    ORDER BY name
                """))
                
                tables = {}
                for row in result:
                    table_name = row[0]
                    
                    # 获取表的行数
                    try:
                        count_result = session.execute(f"SELECT COUNT(*) FROM {table_name}")
                        row_count = count_result.scalar()
                    except Exception:
                        row_count = 0
                    
                    # 获取表的页面数（用于估算大小）
                    try:
                        page_result = session.execute(f"PRAGMA page_count")
                        page_count = page_result.scalar()
                        page_size_result = session.execute(f"PRAGMA page_size")
                        page_size = page_size_result.scalar()
                        estimated_size = page_count * page_size
                    except Exception:
                        estimated_size = 0
                    
                    tables[table_name] = {
                        'type': row[1],
                        'sql': row[2],
                        'row_count': row_count,
                        'estimated_size': estimated_size
                    }
                
                return tables
        except Exception as e:
            self.logger.error(f"获取表信息失败: {e}")
            return {}
    
    def get_index_info(self) -> Dict[str, Any]:
        """
        获取索引信息
        
        Returns:
            索引信息字典
        """
        try:
            with self.get_session() as session:
                result = session.execute(text("""
                    SELECT 
                        name as index_name,
                        tbl_name as table_name,
                        sql
                    FROM sqlite_master
                    WHERE type = 'index'
                    ORDER BY name
                """))
                
                indexes = {}
                for row in result:
                    indexes[row[0]] = {
                        'table_name': row[1],
                        'sql': row[2]
                    }
                
                return indexes
        except Exception as e:
            self.logger.error(f"获取索引信息失败: {e}")
            return {}
    
    def get_view_info(self) -> Dict[str, Any]:
        """
        获取视图信息
        
        Returns:
            视图信息字典
        """
        try:
            with self.get_session() as session:
                result = session.execute(text("""
                    SELECT 
                        name as view_name,
                        sql
                    FROM sqlite_master
                    WHERE type = 'view'
                    ORDER BY name
                """))
                
                views = {}
                for row in result:
                    views[row[0]] = {
                        'sql': row[1]
                    }
                
                return views
        except Exception as e:
            self.logger.error(f"获取视图信息失败: {e}")
            return {}
    
    def get_trigger_info(self) -> Dict[str, Any]:
        """
        获取触发器信息
        
        Returns:
            触发器信息字典
        """
        try:
            with self.get_session() as session:
                result = session.execute(text("""
                    SELECT 
                        name as trigger_name,
                        tbl_name as table_name,
                        sql
                    FROM sqlite_master
                    WHERE type = 'trigger'
                    ORDER BY name
                """))
                
                triggers = {}
                for row in result:
                    triggers[row[0]] = {
                        'table_name': row[1],
                        'sql': row[2]
                    }
                
                return triggers
        except Exception as e:
            self.logger.error(f"获取触发器信息失败: {e}")
            return {}
    
    def optimize_database(self) -> bool:
        """
        优化数据库
        
        Returns:
            是否成功
        """
        try:
            with self.get_session() as session:
                # 执行 VACUUM 操作
                session.execute(text("VACUUM"))
                
                # 重新分析统计信息
                session.execute(text("ANALYZE"))
                
                self.logger.info("数据库优化完成")
                return True
        except Exception as e:
            self.logger.error(f"数据库优化失败: {e}")
            return False
    
    def backup_database(self, backup_path: str) -> bool:
        """
        备份数据库
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            是否成功
        """
        try:
            import shutil
            
            database_path = self.config.get('database', ':memory:')
            
            # 内存数据库无法备份
            if database_path == ':memory:':
                self.logger.warning("内存数据库无法备份")
                return False
            
            # 确保备份目录存在
            backup_dir = os.path.dirname(backup_path)
            if backup_dir and not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)
            
            # 复制数据库文件
            shutil.copy2(database_path, backup_path)
            
            self.logger.info(f"数据库备份完成: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"数据库备份失败: {e}")
            return False
