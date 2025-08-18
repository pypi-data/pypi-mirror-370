"""
PostgreSQL 数据库适配器

提供 PostgreSQL 数据库的连接和操作接口。
"""

from typing import Dict, Any
from .base import DatabaseAdapter


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL 数据库适配器"""
    
    def get_database_type(self) -> str:
        """获取数据库类型"""
        return "postgresql"
    
    def get_connection_string(self) -> str:
        """获取 PostgreSQL 连接字符串"""
        host = self.config.get('host', 'localhost')
        port = self.config.get('port', 5432)
        database = self.config.get('database', '')
        username = self.config.get('username', '')
        password = self.config.get('password', '')
        
        # 构建连接字符串
        connection_string = (
            f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
        )
        
        # 添加额外的连接参数
        extra_params = []
        
        # SSL 配置
        if self.config.get('sslmode'):
            extra_params.append(f"sslmode={self.config['sslmode']}")
        
        # 时区配置
        if self.config.get('timezone'):
            extra_params.append(f"timezone={self.config['timezone']}")
        
        # 连接超时
        if self.config.get('connect_timeout'):
            extra_params.append(f"connect_timeout={self.config['connect_timeout']}")
        
        # 应用名称
        if self.config.get('application_name'):
            extra_params.append(f"application_name={self.config['application_name']}")
        
        # 客户端编码
        if self.config.get('client_encoding'):
            extra_params.append(f"client_encoding={self.config['client_encoding']}")
        
        # 添加额外参数到连接字符串
        if extra_params:
            connection_string += "?" + "&".join(extra_params)
        
        return connection_string
    
    def get_postgresql_specific_features(self) -> Dict[str, Any]:
        """
        获取 PostgreSQL 特定功能
        
        Returns:
            PostgreSQL 特定功能字典
        """
        return {
            'supports_json': True,
            'supports_jsonb': True,
            'supports_fulltext': True,
            'supports_spatial': True,
            'supports_partitioning': True,
            'supports_foreign_keys': True,
            'supports_check_constraints': True,
            'supports_views': True,
            'supports_materialized_views': True,
            'supports_stored_procedures': True,
            'supports_triggers': True,
            'supports_functions': True,
            'supports_extensions': True,
            'supports_schemas': True,
            'supports_sequences': True,
            'supports_arrays': True,
            'supports_hstore': True,
            'supports_uuid': True
        }
    
    def get_version_info(self) -> Dict[str, Any]:
        """
        获取 PostgreSQL 版本信息
        
        Returns:
            版本信息字典
        """
        try:
            with self.get_session() as session:
                result = session.execute(text("SELECT version() as version"))
                version = result.scalar()
                
                # 解析版本信息
                version_parts = version.split(' ')[1].split('.')
                return {
                    'full_version': version,
                    'major_version': int(version_parts[0]),
                    'minor_version': int(version_parts[1]),
                    'patch_version': int(version_parts[2]) if len(version_parts) > 2 else 0
                }
        except Exception as e:
            self.logger.error(f"获取 PostgreSQL 版本信息失败: {e}")
            return {}
    
    def get_server_settings(self) -> Dict[str, Any]:
        """
        获取 PostgreSQL 服务器设置
        
        Returns:
            服务器设置字典
        """
        try:
            with self.get_session() as session:
                result = session.execute(text("SHOW ALL"))
                settings = {}
                for row in result:
                    settings[row[0]] = row[1]
                return settings
        except Exception as e:
            self.logger.error(f"获取 PostgreSQL 服务器设置失败: {e}")
            return {}
    
    def get_database_size(self) -> int:
        """
        获取数据库大小（字节）
        
        Returns:
            数据库大小
        """
        try:
            with self.get_session() as session:
                database = self.config.get('database', '')
                result = session.execute(f"""
                    SELECT pg_database_size('{database}') as size
                """)
                size = result.scalar()
                return size or 0
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
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
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
                        t.table_name,
                        t.table_type,
                        pg_total_relation_size(quote_ident(t.table_name)) as total_size,
                        pg_relation_size(quote_ident(t.table_name)) as data_size,
                        pg_indexes_size(quote_ident(t.table_name)) as index_size,
                        c.reltuples as estimated_rows
                    FROM information_schema.tables t
                    LEFT JOIN pg_class c ON c.relname = t.table_name
                    WHERE t.table_schema = 'public'
                    ORDER BY t.table_name
                """))
                
                tables = {}
                for row in result:
                    tables[row[0]] = {
                        'type': row[1],
                        'total_size': row[2],
                        'data_size': row[3],
                        'index_size': row[4],
                        'estimated_rows': int(row[5]) if row[5] else 0
                    }
                return tables
        except Exception as e:
            self.logger.error(f"获取表信息失败: {e}")
            return {}
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        获取模式信息
        
        Returns:
            模式信息字典
        """
        try:
            with self.get_session() as session:
                result = session.execute(text("""
                    SELECT 
                        schema_name,
                        schema_owner
                    FROM information_schema.schemata
                    ORDER BY schema_name
                """))
                
                schemas = {}
                for row in result:
                    schemas[row[0]] = {
                        'owner': row[1]
                    }
                return schemas
        except Exception as e:
            self.logger.error(f"获取模式信息失败: {e}")
            return {}
    
    def get_extension_info(self) -> Dict[str, Any]:
        """
        获取扩展信息
        
        Returns:
            扩展信息字典
        """
        try:
            with self.get_session() as session:
                result = session.execute(text("""
                    SELECT 
                        extname as name,
                        extversion as version,
                        extowner::regrole as owner
                    FROM pg_extension
                    ORDER BY extname
                """))
                
                extensions = {}
                for row in result:
                    extensions[row[0]] = {
                        'version': row[1],
                        'owner': row[2]
                    }
                return extensions
        except Exception as e:
            self.logger.error(f"获取扩展信息失败: {e}")
            return {}
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """
        获取连接统计信息
        
        Returns:
            连接统计信息字典
        """
        try:
            with self.get_session() as session:
                result = session.execute(text("""
                    SELECT 
                        count(*) as total_connections,
                        count(*) FILTER (WHERE state = 'active') as active_connections,
                        count(*) FILTER (WHERE state = 'idle') as idle_connections,
                        count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                """))
                
                row = result.fetchone()
                return {
                    'total_connections': row[0],
                    'active_connections': row[1],
                    'idle_connections': row[2],
                    'idle_in_transaction': row[3]
                }
        except Exception as e:
            self.logger.error(f"获取连接统计信息失败: {e}")
            return {}
