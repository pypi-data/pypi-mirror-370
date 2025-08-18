"""
模型管理器

提供模型的高级管理功能，包括模型操作、关系管理、版本控制等。
"""

from typing import Dict, Any, List, Optional, Type, Union
from .base import BaseModel
from .registry import ModelRegistry, get_registry
from ..utils.exceptions import ModelError
from loguru import logger


class ModelManager:
    """模型管理器"""
    
    def __init__(self, registry: Optional[ModelRegistry] = None):
        """
        初始化模型管理器
        
        Args:
            registry: 模型注册器，如果为None则使用全局注册器
        """
        self.registry = registry or get_registry()
        self.logger = logger.bind(component="model_manager")
    
    def register_model(self, model_class: Type[BaseModel], metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        注册模型
        
        Args:
            model_class: 模型类
            metadata: 模型元数据
        """
        self.registry.register(model_class, metadata)
    
    def get_model(self, table_name: str) -> Optional[Type[BaseModel]]:
        """
        获取模型
        
        Args:
            table_name: 表名
            
        Returns:
            模型类
        """
        return self.registry.get_model(table_name)
    
    def list_models(self) -> List[str]:
        """
        列出所有模型
        
        Returns:
            模型表名列表
        """
        return self.registry.list_models()
    
    def validate_model(self, table_name: str) -> Dict[str, Any]:
        """
        验证模型
        
        Args:
            table_name: 表名
            
        Returns:
            验证结果
        """
        return self.registry.validate_model(table_name)
    
    def validate_all_models(self) -> Dict[str, Dict[str, Any]]:
        """
        验证所有模型
        
        Returns:
            所有模型验证结果
        """
        return self.registry.validate_all_models()
    
    def get_model_info(self, table_name: str) -> Dict[str, Any]:
        """
        获取模型信息
        
        Args:
            table_name: 表名
            
        Returns:
            模型信息
        """
        return self.registry.get_model_info(table_name)
    
    def get_all_model_info(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有模型信息
        
        Returns:
            所有模型信息
        """
        return self.registry.get_all_model_info()
    
    def create_instance(self, table_name: str, data: Dict[str, Any]) -> BaseModel:
        """
        创建模型实例
        
        Args:
            table_name: 表名
            data: 数据字典
            
        Returns:
            模型实例
            
        Raises:
            ModelError: 模型不存在或数据验证失败
        """
        model_class = self.get_model(table_name)
        if not model_class:
            raise ModelError(f"模型不存在: {table_name}")
        
        # 验证数据
        errors = model_class.validate_data(data)
        if errors:
            error_messages = []
            for field, field_errors in errors.items():
                error_messages.extend(f"{field}: {', '.join(field_errors)}")
            raise ModelError(f"数据验证失败: {'; '.join(error_messages)}")
        
        return model_class.from_dict(data)
    
    def create_table_sql(self, table_name: str) -> str:
        """
        生成创建表的SQL语句
        
        Args:
            table_name: 表名
            
        Returns:
            创建表的SQL语句
            
        Raises:
            ModelError: 模型不存在
        """
        model_class = self.get_model(table_name)
        if not model_class:
            raise ModelError(f"模型不存在: {table_name}")
        
        return model_class.create_table_sql()
    
    def create_all_tables_sql(self, table_names: Optional[List[str]] = None) -> Dict[str, str]:
        """
        生成所有表的创建SQL语句
        
        Args:
            table_names: 表名列表，如果为None则生成所有表
            
        Returns:
            表名到SQL语句的映射
        """
        return self.registry.create_tables_sql(table_names)
    
    def get_model_relationships(self, table_name: str) -> Dict[str, Any]:
        """
        获取模型关系信息
        
        Args:
            table_name: 表名
            
        Returns:
            关系信息字典
        """
        model_class = self.get_model(table_name)
        if not model_class:
            return {}
        
        schema = model_class.get_schema()
        relationships = {
            'foreign_keys': schema.get('foreign_keys', {}),
            'references': {},
            'referenced_by': {}
        }
        
        # 查找被其他表引用的关系
        for other_table in self.list_models():
            if other_table != table_name:
                other_model = self.get_model(other_table)
                if other_model:
                    other_schema = other_model.get_schema()
                    for fk_name, fk_def in other_schema.get('foreign_keys', {}).items():
                        if fk_def['reference_table'] == table_name:
                            if other_table not in relationships['referenced_by']:
                                relationships['referenced_by'][other_table] = []
                            relationships['referenced_by'][other_table].append({
                                'foreign_key': fk_name,
                                'column': fk_def['column'],
                                'reference_column': fk_def['reference_column']
                            })
        
        return relationships
    
    def get_model_dependencies(self, table_name: str) -> List[str]:
        """
        获取模型依赖关系
        
        Args:
            table_name: 表名
            
        Returns:
            依赖的表名列表
        """
        model_class = self.get_model(table_name)
        if not model_class:
            return []
        
        schema = model_class.get_schema()
        dependencies = set()
        
        for fk_def in schema.get('foreign_keys', {}).values():
            dependencies.add(fk_def['reference_table'])
        
        return list(dependencies)
    
    def get_model_dependents(self, table_name: str) -> List[str]:
        """
        获取依赖该模型的表
        
        Args:
            table_name: 表名
            
        Returns:
            依赖该模型的表名列表
        """
        dependents = []
        
        for other_table in self.list_models():
            if other_table != table_name:
                dependencies = self.get_model_dependencies(other_table)
                if table_name in dependencies:
                    dependents.append(other_table)
        
        return dependents
    
    def get_creation_order(self) -> List[str]:
        """
        获取表的创建顺序（考虑依赖关系）
        
        Returns:
            表名列表，按创建顺序排列
        """
        all_tables = set(self.list_models())
        created_tables = set()
        creation_order = []
        
        while all_tables:
            # 找到没有未创建依赖的表
            ready_tables = []
            for table in all_tables:
                dependencies = set(self.get_model_dependencies(table))
                if dependencies.issubset(created_tables):
                    ready_tables.append(table)
            
            if not ready_tables:
                # 存在循环依赖，按字母顺序处理
                ready_tables = sorted(all_tables)
            
            # 创建找到的表
            for table in ready_tables:
                creation_order.append(table)
                created_tables.add(table)
                all_tables.remove(table)
        
        return creation_order
    
    def validate_model_relationships(self, table_name: str) -> Dict[str, Any]:
        """
        验证模型关系
        
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
        schema = model_class.get_schema()
        
        # 验证外键引用的表是否存在
        for fk_name, fk_def in schema.get('foreign_keys', {}).items():
            referenced_table = fk_def['reference_table']
            if not self.get_model(referenced_table):
                errors.append(f"外键 {fk_name} 引用的表不存在: {referenced_table}")
        
        # 验证外键引用的列是否存在
        for fk_name, fk_def in schema.get('foreign_keys', {}).items():
            referenced_table = fk_def['reference_table']
            referenced_column = fk_def['reference_column']
            
            referenced_model = self.get_model(referenced_table)
            if referenced_model:
                referenced_schema = referenced_model.get_schema()
                if referenced_column not in referenced_schema.get('columns', {}):
                    errors.append(f"外键 {fk_name} 引用的列不存在: {referenced_table}.{referenced_column}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_all_relationships(self) -> Dict[str, Dict[str, Any]]:
        """
        验证所有模型的关系
        
        Returns:
            所有模型关系验证结果
        """
        return {
            table_name: self.validate_model_relationships(table_name)
            for table_name in self.list_models()
        }
    
    def export_model_schema(self, table_name: str) -> Dict[str, Any]:
        """
        导出模型结构
        
        Args:
            table_name: 表名
            
        Returns:
            模型结构字典
        """
        model_class = self.get_model(table_name)
        if not model_class:
            return {}
        
        schema = model_class.get_schema()
        metadata = self.registry.get_metadata(table_name)
        
        return {
            'table_name': table_name,
            'class_name': model_class.__name__,
            'module': model_class.__module__,
            'schema': schema,
            'metadata': metadata,
            'relationships': self.get_model_relationships(table_name),
            'dependencies': self.get_model_dependencies(table_name),
            'dependents': self.get_model_dependents(table_name),
            'create_sql': model_class.create_table_sql()
        }
    
    def export_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """
        导出所有模型结构
        
        Returns:
            所有模型结构字典
        """
        return {
            table_name: self.export_model_schema(table_name)
            for table_name in self.list_models()
        }
    
    def generate_migration_sql(self, from_schemas: Dict[str, Dict[str, Any]], 
                              to_schemas: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        生成迁移SQL语句
        
        Args:
            from_schemas: 原始模型结构
            to_schemas: 目标模型结构
            
        Returns:
            SQL语句列表
        """
        migration_sql = []
        
        # 这里可以实现复杂的迁移逻辑
        # 目前只是简单的实现
        for table_name, to_schema in to_schemas.items():
            if table_name not in from_schemas:
                # 新表
                migration_sql.append(to_schema['create_sql'])
            else:
                # 表已存在，需要比较差异
                from_schema = from_schemas[table_name]
                # 这里可以添加ALTER TABLE语句
                pass
        
        return migration_sql
    
    def clear(self) -> None:
        """清空所有模型"""
        self.registry.clear()
    
    def __len__(self) -> int:
        """返回模型数量"""
        return len(self.registry)
    
    def __contains__(self, table_name: str) -> bool:
        """检查是否包含指定模型"""
        return table_name in self.registry
