"""
批量操作器

提供高效的批量数据操作功能。
"""

import time
from typing import Dict, Any, List, Optional
from sqlalchemy import insert, update, delete, text
from sqlalchemy.orm import Session
from loguru import logger


class BatchOperator:
    """批量操作器"""
    
    def __init__(self, connection_manager):
        """
        初始化批量操作器
        
        Args:
            connection_manager: 连接管理器
        """
        self.connection_manager = connection_manager
        self.logger = logger.bind(component="batch_operator")
    
    def batch_insert(self, table: str, data_list: List[Dict[str, Any]], 
                     database: str = 'default', batch_size: int = 1000) -> List[Dict[str, Any]]:
        """
        批量插入数据
        
        Args:
            table: 表名
            data_list: 数据列表
            database: 数据库名称
            batch_size: 批次大小
            
        Returns:
            插入的数据记录列表
        """
        if not data_list:
            return []
        
        start_time = time.time()
        inserted_records = []
        
        try:
            with self.connection_manager.get_session_context(database) as session:
                # 分批处理
                for i in range(0, len(data_list), batch_size):
                    batch_data = data_list[i:i + batch_size]
                    
                    # 构建批量插入语句
                    stmt = insert(table).values(batch_data)
                    
                    # 执行批量插入
                    result = session.execute(stmt)
                    session.commit()
                    
                    # 获取插入的ID
                    if result.inserted_primary_key:
                        for j, data in enumerate(batch_data):
                            record = data.copy()
                            if len(result.inserted_primary_key) > j:
                                record['id'] = result.inserted_primary_key[j]
                            inserted_records.append(record)
                    else:
                        inserted_records.extend(batch_data)
                    
                    self.logger.debug(f"批量插入批次 {i//batch_size + 1}: {table}, 数量: {len(batch_data)}")
            
            execution_time = time.time() - start_time
            self.logger.info(f"批量插入完成: {table}, 总数: {len(inserted_records)}, 耗时: {execution_time:.2f}秒")
            
            return inserted_records
            
        except Exception as e:
            self.logger.error(f"批量插入失败: {table}, 错误: {e}")
            raise
    
    def batch_update(self, table: str, data_list: List[Dict[str, Any]], 
                     key_field: str = 'id', database: str = 'default', 
                     batch_size: int = 1000) -> int:
        """
        批量更新数据
        
        Args:
            table: 表名
            data_list: 数据列表，每个字典必须包含key_field字段
            key_field: 主键字段名
            database: 数据库名称
            batch_size: 批次大小
            
        Returns:
            更新的记录数
        """
        if not data_list:
            return 0
        
        start_time = time.time()
        updated_count = 0
        
        try:
            with self.connection_manager.get_session_context(database) as session:
                # 分批处理
                for i in range(0, len(data_list), batch_size):
                    batch_data = data_list[i:i + batch_size]
                    
                    for data in batch_data:
                        if key_field not in data:
                            raise ValueError(f"数据缺少主键字段: {key_field}")
                        
                        # 提取主键值
                        key_value = data.pop(key_field)
                        
                        # 构建更新语句
                        stmt = update(table).values(data).where(text(f"{key_field} = :key_value"))
                        
                        # 执行更新
                        result = session.execute(stmt, {'key_value': key_value})
                        updated_count += result.rowcount
                    
                    session.commit()
                    self.logger.debug(f"批量更新批次 {i//batch_size + 1}: {table}, 数量: {len(batch_data)}")
            
            execution_time = time.time() - start_time
            self.logger.info(f"批量更新完成: {table}, 更新数: {updated_count}, 耗时: {execution_time:.2f}秒")
            
            return updated_count
            
        except Exception as e:
            self.logger.error(f"批量更新失败: {table}, 错误: {e}")
            raise
    
    def batch_delete(self, table: str, key_values: List[Any], 
                     key_field: str = 'id', database: str = 'default', 
                     batch_size: int = 1000) -> int:
        """
        批量删除数据
        
        Args:
            table: 表名
            key_values: 主键值列表
            key_field: 主键字段名
            database: 数据库名称
            batch_size: 批次大小
            
        Returns:
            删除的记录数
        """
        if not key_values:
            return 0
        
        start_time = time.time()
        deleted_count = 0
        
        try:
            with self.connection_manager.get_session_context(database) as session:
                # 分批处理
                for i in range(0, len(key_values), batch_size):
                    batch_keys = key_values[i:i + batch_size]
                    
                    # 构建批量删除语句
                    placeholders = ','.join([':key_' + str(j) for j in range(len(batch_keys))])
                    stmt = delete(table).where(text(f"{key_field} IN ({placeholders})"))
                    
                    # 构建参数
                    params = {f'key_{j}': key for j, key in enumerate(batch_keys)}
                    
                    # 执行删除
                    result = session.execute(stmt, params)
                    deleted_count += result.rowcount
                    
                    session.commit()
                    self.logger.debug(f"批量删除批次 {i//batch_size + 1}: {table}, 数量: {len(batch_keys)}")
            
            execution_time = time.time() - start_time
            self.logger.info(f"批量删除完成: {table}, 删除数: {deleted_count}, 耗时: {execution_time:.2f}秒")
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"批量删除失败: {table}, 错误: {e}")
            raise
    
    def batch_upsert(self, table: str, data_list: List[Dict[str, Any]], 
                     key_field: str = 'id', database: str = 'default', 
                     batch_size: int = 1000) -> Dict[str, int]:
        """
        批量插入或更新数据
        
        Args:
            table: 表名
            data_list: 数据列表
            key_field: 主键字段名
            database: 数据库名称
            batch_size: 批次大小
            
        Returns:
            操作结果统计
        """
        if not data_list:
            return {'inserted': 0, 'updated': 0}
        
        start_time = time.time()
        inserted_count = 0
        updated_count = 0
        
        try:
            with self.connection_manager.get_session_context(database) as session:
                # 分批处理
                for i in range(0, len(data_list), batch_size):
                    batch_data = data_list[i:i + batch_size]
                    
                    for data in batch_data:
                        if key_field not in data:
                            raise ValueError(f"数据缺少主键字段: {key_field}")
                        
                        key_value = data[key_field]
                        
                        # 检查记录是否存在
                        check_stmt = text(f"SELECT COUNT(*) FROM {table} WHERE {key_field} = :key_value")
                        result = session.execute(check_stmt, {'key_value': key_value})
                        exists = result.scalar() > 0
                        
                        if exists:
                            # 更新现有记录
                            update_data = data.copy()
                            update_data.pop(key_field)
                            
                            stmt = update(table).values(update_data).where(text(f"{key_field} = :key_value"))
                            result = session.execute(stmt, {'key_value': key_value})
                            updated_count += result.rowcount
                        else:
                            # 插入新记录
                            stmt = insert(table).values(data)
                            session.execute(stmt)
                            inserted_count += 1
                    
                    session.commit()
                    self.logger.debug(f"批量upsert批次 {i//batch_size + 1}: {table}, 数量: {len(batch_data)}")
            
            execution_time = time.time() - start_time
            self.logger.info(f"批量upsert完成: {table}, 插入: {inserted_count}, 更新: {updated_count}, 耗时: {execution_time:.2f}秒")
            
            return {
                'inserted': inserted_count,
                'updated': updated_count
            }
            
        except Exception as e:
            self.logger.error(f"批量upsert失败: {table}, 错误: {e}")
            raise
    
    def execute_batch_sql(self, sql_list: List[str], params_list: List[Dict[str, Any]] = None, 
                          database: str = 'default', batch_size: int = 1000) -> List[Any]:
        """
        批量执行SQL语句
        
        Args:
            sql_list: SQL语句列表
            params_list: 参数列表
            database: 数据库名称
            batch_size: 批次大小
            
        Returns:
            执行结果列表
        """
        if not sql_list:
            return []
        
        if params_list is None:
            params_list = [{}] * len(sql_list)
        
        if len(sql_list) != len(params_list):
            raise ValueError("SQL语句列表和参数列表长度不匹配")
        
        start_time = time.time()
        results = []
        
        try:
            with self.connection_manager.get_session_context(database) as session:
                # 分批执行
                for i in range(0, len(sql_list), batch_size):
                    batch_sql = sql_list[i:i + batch_size]
                    batch_params = params_list[i:i + batch_size]
                    
                    for sql, params in zip(batch_sql, batch_params):
                        result = session.execute(text(sql), params)
                        results.append(result)
                    
                    session.commit()
                    self.logger.debug(f"批量SQL执行批次 {i//batch_size + 1}, 数量: {len(batch_sql)}")
            
            execution_time = time.time() - start_time
            self.logger.info(f"批量SQL执行完成, 总数: {len(results)}, 耗时: {execution_time:.2f}秒")
            
            return results
            
        except Exception as e:
            self.logger.error(f"批量SQL执行失败: {e}")
            raise
