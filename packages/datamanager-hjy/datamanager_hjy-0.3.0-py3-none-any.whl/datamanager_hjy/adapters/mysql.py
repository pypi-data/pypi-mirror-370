"""
MySQL 数据库适配器

提供 MySQL 数据库的连接和操作接口。
"""

import urllib.parse
from typing import Dict, Any
from .base import DatabaseAdapter


class MySQLAdapter(DatabaseAdapter):
    """MySQL 数据库适配器"""
    
    def get_database_type(self) -> str:
        """获取数据库类型"""
        return "mysql"
    
    def get_connection_string(self) -> str:
        """获取 MySQL 连接字符串"""
        host = self.config.get('host', 'localhost')
        port = self.config.get('port', 3306)
        database = self.config.get('database', '')
        username = self.config.get('username', '')
        password = self.config.get('password', '')
        charset = self.config.get('charset', 'utf8mb4')
        
        # URL编码用户名和密码，处理特殊字符
        encoded_username = urllib.parse.quote_plus(username)
        encoded_password = urllib.parse.quote_plus(password)
        
        # 构建连接字符串
        connection_string = (
            f"mysql+pymysql://{encoded_username}:{encoded_password}@{host}:{port}/{database}"
            f"?charset={charset}"
        )
        
        # 添加额外的连接参数
        extra_params = []
        
        # SSL 配置
        if self.config.get('ssl_mode'):
            extra_params.append(f"ssl_mode={self.config['ssl_mode']}")
        
        # 时区配置
        if self.config.get('timezone'):
            timezone_encoded = urllib.parse.quote(self.config['timezone'])
            extra_params.append(f"time_zone={timezone_encoded}")
        
        # 连接超时
        if self.config.get('connect_timeout'):
            extra_params.append(f"connect_timeout={self.config['connect_timeout']}")
        
        # 读取超时
        if self.config.get('read_timeout'):
            extra_params.append(f"read_timeout={self.config['read_timeout']}")
        
        # 写入超时
        if self.config.get('write_timeout'):
            extra_params.append(f"write_timeout={self.config['write_timeout']}")
        
        # 自动提交
        if self.config.get('autocommit'):
            extra_params.append("autocommit=true")
        
        # 添加额外参数到连接字符串
        if extra_params:
            connection_string += "&" + "&".join(extra_params)
        
        return connection_string
    
    def get_mysql_specific_features(self) -> Dict[str, Any]:
        """
        获取 MySQL 特定功能
        
        Returns:
            MySQL 特定功能字典
        """
        return {
            'supports_json': True,
            'supports_fulltext': True,
            'supports_spatial': True,
            'supports_partitioning': True,
            'supports_foreign_keys': True,
            'supports_check_constraints': True,
            'supports_views': True,
            'supports_stored_procedures': True,
            'supports_triggers': True,
            'supports_events': True,
            'supports_user_defined_functions': True
        }
    
    def get_version_info(self) -> Dict[str, Any]:
        """
        获取 MySQL 版本信息
        
        Returns:
            版本信息字典
        """
        try:
            with self.get_session() as session:
                from sqlalchemy import text
                result = session.execute(text("SELECT VERSION() as version"))
                version = result.scalar()
                
                # 解析版本信息
                version_parts = version.split('.')
                return {
                    'full_version': version,
                    'major_version': int(version_parts[0]),
                    'minor_version': int(version_parts[1]),
                    'patch_version': int(version_parts[2].split('-')[0]) if len(version_parts) > 2 else 0
                }
        except Exception as e:
            self.logger.error(f"获取 MySQL 版本信息失败: {e}")
            return {}
    
    def get_server_variables(self) -> Dict[str, Any]:
        """
        获取 MySQL 服务器变量
        
        Returns:
            服务器变量字典
        """
        try:
            with self.get_session() as session:
                from sqlalchemy import text
                result = session.execute(text("SHOW VARIABLES"))
                variables = {}
                for row in result:
                    variables[row[0]] = row[1]
                return variables
        except Exception as e:
            self.logger.error(f"获取 MySQL 服务器变量失败: {e}")
            return {}
    
    def get_status_info(self) -> Dict[str, Any]:
        """
        获取 MySQL 状态信息
        
        Returns:
            状态信息字典
        """
        try:
            with self.get_session() as session:
                result = session.execute(text("SHOW STATUS"))
                status = {}
                for row in result:
                    status[row[0]] = row[1]
                return status
        except Exception as e:
            self.logger.error(f"获取 MySQL 状态信息失败: {e}")
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
                    SELECT SUM(data_length + index_length) as size
                    FROM information_schema.tables
                    WHERE table_schema = '{database}'
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
                database = self.config.get('database', '')
                result = session.execute(f"""
                    SELECT COUNT(*) as count
                    FROM information_schema.tables
                    WHERE table_schema = '{database}'
                """)
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
                database = self.config.get('database', '')
                result = session.execute(f"""
                    SELECT 
                        table_name,
                        table_rows,
                        data_length,
                        index_length,
                        table_collation,
                        engine
                    FROM information_schema.tables
                    WHERE table_schema = '{database}'
                    ORDER BY table_name
                """)
                
                tables = {}
                for row in result:
                    tables[row[0]] = {
                        'rows': row[1],
                        'data_length': row[2],
                        'index_length': row[3],
                        'collation': row[4],
                        'engine': row[5]
                    }
                return tables
        except Exception as e:
            self.logger.error(f"获取表信息失败: {e}")
            return {}
