"""
异常定义模块

提供统一的异常处理机制，确保错误信息清晰、可操作、人类可读。
"""

from typing import Optional, Dict, Any


class DataManagerException(Exception):
    """数据管理器基础异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        return self.message


class ConfigurationError(DataManagerException):
    """配置错误"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if config_key:
            message = f"配置错误 [{config_key}]: {message}"
        super().__init__(message, details)
        self.config_key = config_key


class ConnectionError(DataManagerException):
    """连接错误"""
    
    def __init__(self, message: str, database: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if database:
            message = f"数据库连接错误 [{database}]: {message}"
        super().__init__(message, details)
        self.database = database


class QueryError(DataManagerException):
    """查询错误"""
    
    def __init__(self, message: str, table: Optional[str] = None, query: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if table:
            message = f"查询错误 [{table}]: {message}"
        if query:
            message += f"\n执行的查询: {query}"
        super().__init__(message, details)
        self.table = table
        self.query = query


class TransactionError(DataManagerException):
    """事务错误"""
    
    def __init__(self, message: str, transaction_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if transaction_id:
            message = f"事务错误 [{transaction_id}]: {message}"
        super().__init__(message, details)
        self.transaction_id = transaction_id


class ValidationError(DataManagerException):
    """数据验证错误"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, details: Optional[Dict[str, Any]] = None):
        if field:
            message = f"数据验证错误 [{field}]: {message}"
            if value is not None:
                message += f"\n提供的值: {value}"
        super().__init__(message, details)
        self.field = field
        self.value = value


class AdapterError(DataManagerException):
    """适配器错误"""
    
    def __init__(self, message: str, adapter_type: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if adapter_type:
            message = f"适配器错误 [{adapter_type}]: {message}"
        super().__init__(message, details)
        self.adapter_type = adapter_type


class ModelError(DataManagerException):
    """模型错误"""
    
    def __init__(self, message: str, model_name: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if model_name:
            message = f"模型错误 [{model_name}]: {message}"
        super().__init__(message, details)
        self.model_name = model_name


class CacheError(DataManagerException):
    """缓存错误"""
    
    def __init__(self, message: str, cache_key: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if cache_key:
            message = f"缓存错误 [{cache_key}]: {message}"
        super().__init__(message, details)
        self.cache_key = cache_key


class MonitoringError(DataManagerException):
    """监控错误"""
    
    def __init__(self, message: str, metric_name: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if metric_name:
            message = f"监控错误 [{metric_name}]: {message}"
        super().__init__(message, details)
        self.metric_name = metric_name


# 便捷的错误创建函数
def create_configuration_error(message: str, config_key: Optional[str] = None, **kwargs) -> ConfigurationError:
    """创建配置错误"""
    return ConfigurationError(message, config_key, kwargs)


def create_connection_error(message: str, database: Optional[str] = None, **kwargs) -> ConnectionError:
    """创建连接错误"""
    return ConnectionError(message, database, kwargs)


def create_query_error(message: str, table: Optional[str] = None, query: Optional[str] = None, **kwargs) -> QueryError:
    """创建查询错误"""
    return QueryError(message, table, query, kwargs)


def create_validation_error(message: str, field: Optional[str] = None, value: Optional[Any] = None, **kwargs) -> ValidationError:
    """创建验证错误"""
    return ValidationError(message, field, value, kwargs)


# 错误代码定义
class ErrorCodes:
    """错误代码常量"""
    
    # 配置相关 (1000-1999)
    CONFIG_FILE_NOT_FOUND = 1001
    CONFIG_INVALID_FORMAT = 1002
    CONFIG_MISSING_REQUIRED = 1003
    CONFIG_VALIDATION_FAILED = 1004
    
    # 连接相关 (2000-2999)
    CONNECTION_FAILED = 2001
    CONNECTION_TIMEOUT = 2002
    CONNECTION_POOL_EXHAUSTED = 2003
    CONNECTION_INVALID_CREDENTIALS = 2004
    
    # 查询相关 (3000-3999)
    QUERY_SYNTAX_ERROR = 3001
    QUERY_TABLE_NOT_FOUND = 3002
    QUERY_COLUMN_NOT_FOUND = 3003
    QUERY_PERMISSION_DENIED = 3004
    
    # 事务相关 (4000-4999)
    TRANSACTION_ALREADY_STARTED = 4001
    TRANSACTION_NOT_STARTED = 4002
    TRANSACTION_COMMIT_FAILED = 4003
    TRANSACTION_ROLLBACK_FAILED = 4004
    
    # 验证相关 (5000-5999)
    VALIDATION_REQUIRED_FIELD_MISSING = 5001
    VALIDATION_INVALID_TYPE = 5002
    VALIDATION_CONSTRAINT_VIOLATION = 5003
    VALIDATION_UNIQUE_CONSTRAINT_VIOLATION = 5004
    
    # 适配器相关 (6000-6999)
    ADAPTER_NOT_SUPPORTED = 6001
    ADAPTER_INITIALIZATION_FAILED = 6002
    ADAPTER_OPERATION_FAILED = 6003
    
    # 模型相关 (7000-7999)
    MODEL_NOT_FOUND = 7001
    MODEL_ALREADY_EXISTS = 7002
    MODEL_VALIDATION_FAILED = 7003
    
    # 缓存相关 (8000-8999)
    CACHE_CONNECTION_FAILED = 8001
    CACHE_KEY_NOT_FOUND = 8002
    CACHE_OPERATION_FAILED = 8003
    
    # 监控相关 (9000-9999)
    MONITORING_INITIALIZATION_FAILED = 9001
    MONITORING_METRIC_COLLECTION_FAILED = 9002


# 错误消息模板
class ErrorMessages:
    """错误消息模板"""
    
    @staticmethod
    def config_file_not_found(file_path: str) -> str:
        return f"配置文件未找到: {file_path}\n请检查文件路径是否正确，或创建配置文件。"
    
    @staticmethod
    def config_invalid_format(file_path: str, error: str) -> str:
        return f"配置文件格式错误: {file_path}\n错误详情: {error}\n请检查YAML格式是否正确。"
    
    @staticmethod
    def config_missing_required(key: str) -> str:
        return f"缺少必需的配置项: {key}\n请检查配置文件并添加此配置项。"
    
    @staticmethod
    def connection_failed(database: str, error: str) -> str:
        return f"数据库连接失败 [{database}]: {error}\n请检查数据库配置和网络连接。"
    
    @staticmethod
    def connection_timeout(database: str, timeout: int) -> str:
        return f"数据库连接超时 [{database}]: {timeout}秒\n请检查数据库是否可访问，或增加超时时间。"
    
    @staticmethod
    def connection_pool_exhausted(database: str) -> str:
        return f"连接池已耗尽 [{database}]\n请增加连接池大小或检查是否有连接泄漏。"
    
    @staticmethod
    def query_table_not_found(table: str) -> str:
        return f"表不存在: {table}\n请检查表名是否正确，或确保表已创建。"
    
    @staticmethod
    def query_column_not_found(table: str, column: str) -> str:
        return f"列不存在 [{table}.{column}]\n请检查列名是否正确。"
    
    @staticmethod
    def validation_required_field_missing(field: str) -> str:
        return f"缺少必需字段: {field}\n请提供此字段的值。"
    
    @staticmethod
    def validation_invalid_type(field: str, expected_type: str, actual_value: Any) -> str:
        return f"字段类型错误 [{field}]: 期望 {expected_type}，实际值 {actual_value}"
    
    @staticmethod
    def validation_unique_constraint_violation(field: str, value: Any) -> str:
        return f"唯一性约束违反 [{field}]: 值 {value} 已存在\n请使用不同的值。"
