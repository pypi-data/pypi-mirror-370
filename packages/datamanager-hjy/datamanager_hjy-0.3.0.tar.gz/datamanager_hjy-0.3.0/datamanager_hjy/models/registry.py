"""
模型注册器

管理所有数据模型的注册、发现和访问。
"""

from typing import Dict, Any, Type, List, Optional
from .base import BaseModel
from loguru import logger


class ModelRegistry:
    """模型注册器"""
    
    def __init__(self):
        """初始化模型注册器"""
        self._models: Dict[str, Type[BaseModel]] = {}
        self._model_metadata: Dict[str, Dict[str, Any]] = {}
        self.logger = logger.bind(component="model_registry")
    
    def register(self, model_class: Type[BaseModel], metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        注册模型
        
        Args:
            model_class: 模型类
            metadata: 模型元数据
        """
        if not issubclass(model_class, BaseModel):
            raise ValueError(f"模型类必须继承自 BaseModel: {model_class}")
        
        table_name = model_class.get_table_name()
        
        if table_name in self._models:
            self.logger.warning(f"模型已存在，将被覆盖: {table_name}")
        
        self._models[table_name] = model_class
        self._model_metadata[table_name] = metadata or {}
        
        self.logger.info(f"模型注册成功: {table_name} -> {model_class.__name__}")
    
    def unregister(self, table_name: str) -> bool:
        """
        注销模型
        
        Args:
            table_name: 表名
            
        Returns:
            是否成功注销
        """
        if table_name in self._models:
            del self._models[table_name]
            if table_name in self._model_metadata:
                del self._model_metadata[table_name]
            
            self.logger.info(f"模型注销成功: {table_name}")
            return True
        
        return False
    
    def get_model(self, table_name: str) -> Optional[Type[BaseModel]]:
        """
        获取模型类
        
        Args:
            table_name: 表名
            
        Returns:
            模型类
        """
        return self._models.get(table_name)
    
    def get_metadata(self, table_name: str) -> Dict[str, Any]:
        """
        获取模型元数据
        
        Args:
            table_name: 表名
            
        Returns:
            模型元数据
        """
        return self._model_metadata.get(table_name, {})
    
    def list_models(self) -> List[str]:
        """
        列出所有注册的模型
        
        Returns:
            模型表名列表
        """
        return list(self._models.keys())
    
    def list_model_classes(self) -> List[Type[BaseModel]]:
        """
        列出所有注册的模型类
        
        Returns:
            模型类列表
        """
        return list(self._models.values())
    
    def get_model_info(self, table_name: str) -> Dict[str, Any]:
        """
        获取模型信息
        
        Args:
            table_name: 表名
            
        Returns:
            模型信息字典
        """
        model_class = self.get_model(table_name)
        if not model_class:
            return {}
        
        metadata = self.get_metadata(table_name)
        schema = model_class.get_schema()
        
        return {
            'table_name': table_name,
            'class_name': model_class.__name__,
            'module': model_class.__module__,
            'metadata': metadata,
            'schema': schema,
            'columns': list(schema.get('columns', {}).keys()),
            'indexes': list(schema.get('indexes', {}).keys()),
            'foreign_keys': list(schema.get('foreign_keys', {}).keys())
        }
    
    def get_all_model_info(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有模型信息
        
        Returns:
            所有模型信息字典
        """
        return {
            table_name: self.get_model_info(table_name)
            for table_name in self.list_models()
        }
    
    def validate_model(self, table_name: str) -> Dict[str, Any]:
        """
        验证模型
        
        Args:
            table_name: 表名
            
        Returns:
            验证结果
        """
        model_class = self.get_model(table_name)
        if not model_class:
            return {
                'valid': False,
                'errors': [f"模型不存在: {table_name}"]
            }
        
        errors = []
        
        # 检查必需方法
        required_methods = ['get_table_name', 'get_schema']
        for method in required_methods:
            if not hasattr(model_class, method):
                errors.append(f"缺少必需方法: {method}")
        
        # 检查表结构
        try:
            schema = model_class.get_schema()
            if not isinstance(schema, dict):
                errors.append("get_schema() 必须返回字典")
            elif 'columns' not in schema:
                errors.append("schema 中缺少 'columns' 字段")
        except Exception as e:
            errors.append(f"获取表结构失败: {e}")
        
        # 检查表名
        try:
            actual_table_name = model_class.get_table_name()
            if actual_table_name != table_name:
                errors.append(f"表名不匹配: 期望 {table_name}, 实际 {actual_table_name}")
        except Exception as e:
            errors.append(f"获取表名失败: {e}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_all_models(self) -> Dict[str, Dict[str, Any]]:
        """
        验证所有模型
        
        Returns:
            所有模型验证结果
        """
        return {
            table_name: self.validate_model(table_name)
            for table_name in self.list_models()
        }
    
    def auto_discover(self, module_path: str) -> List[str]:
        """
        自动发现模型
        
        Args:
            module_path: 模块路径
            
        Returns:
            发现的模型表名列表
        """
        discovered_models = []
        
        try:
            import importlib
            import inspect
            
            module = importlib.import_module(module_path)
            
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseModel) and 
                    obj != BaseModel):
                    
                    table_name = obj.get_table_name()
                    self.register(obj)
                    discovered_models.append(table_name)
                    
                    self.logger.info(f"自动发现模型: {table_name} -> {obj.__name__}")
        
        except Exception as e:
            self.logger.error(f"自动发现模型失败: {e}")
        
        return discovered_models
    
    def create_tables_sql(self, table_names: Optional[List[str]] = None) -> Dict[str, str]:
        """
        生成创建表的SQL语句
        
        Args:
            table_names: 表名列表，如果为None则生成所有表
            
        Returns:
            表名到SQL语句的映射
        """
        if table_names is None:
            table_names = self.list_models()
        
        sql_statements = {}
        
        for table_name in table_names:
            model_class = self.get_model(table_name)
            if model_class:
                try:
                    sql = model_class.create_table_sql()
                    sql_statements[table_name] = sql
                except Exception as e:
                    self.logger.error(f"生成表 {table_name} 的SQL失败: {e}")
        
        return sql_statements
    
    def clear(self) -> None:
        """清空所有注册的模型"""
        self._models.clear()
        self._model_metadata.clear()
        self.logger.info("模型注册器已清空")
    
    def __len__(self) -> int:
        """返回注册的模型数量"""
        return len(self._models)
    
    def __contains__(self, table_name: str) -> bool:
        """检查是否包含指定模型"""
        return table_name in self._models
    
    def __iter__(self):
        """迭代器"""
        return iter(self._models.items())


# 全局模型注册器实例
_global_registry = ModelRegistry()


def get_registry() -> ModelRegistry:
    """
    获取全局模型注册器
    
    Returns:
        全局模型注册器实例
    """
    return _global_registry


def register_model(model_class: Type[BaseModel], metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    注册模型到全局注册器
    
    Args:
        model_class: 模型类
        metadata: 模型元数据
    """
    _global_registry.register(model_class, metadata)


def get_model(table_name: str) -> Optional[Type[BaseModel]]:
    """
    从全局注册器获取模型
    
    Args:
        table_name: 表名
        
    Returns:
        模型类
    """
    return _global_registry.get_model(table_name)


def list_models() -> List[str]:
    """
    列出全局注册器中的所有模型
    
    Returns:
        模型表名列表
    """
    return _global_registry.list_models()
