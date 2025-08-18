"""
性能监控模块

提供数据库操作性能监控和慢查询检测。
"""

import time
import threading
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class QueryMetrics:
    """查询指标"""
    operation: str
    table: str
    execution_time: float
    timestamp: float = field(default_factory=time.time)
    record_count: int = 0
    error: Optional[str] = None


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, slow_query_threshold: float = 1.0, max_queries: int = 1000):
        """
        初始化性能监控器
        
        Args:
            slow_query_threshold: 慢查询阈值（秒）
            max_queries: 最大保存查询数量
        """
        self.slow_query_threshold = slow_query_threshold
        self.max_queries = max_queries
        self.logger = logger.bind(component="performance_monitor")
        
        # 性能指标存储
        self._metrics = deque(maxlen=max_queries)
        self._slow_queries = deque(maxlen=max_queries)
        self._operation_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'avg_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'errors': 0
        })
        
        self._lock = threading.Lock()
    
    def record_operation(self, operation: str, table: str, execution_time: float, 
                        record_count: int = 0, error: Optional[str] = None):
        """
        记录操作指标
        
        Args:
            operation: 操作类型
            table: 表名
            execution_time: 执行时间
            record_count: 记录数量
            error: 错误信息
        """
        with self._lock:
            # 创建指标记录
            metric = QueryMetrics(
                operation=operation,
                table=table,
                execution_time=execution_time,
                record_count=record_count,
                error=error
            )
            
            # 添加到指标列表
            self._metrics.append(metric)
            
            # 检查是否为慢查询
            if execution_time >= self.slow_query_threshold:
                self._slow_queries.append(metric)
                self.logger.warning(f"慢查询检测: {operation} {table}, 耗时: {execution_time:.3f}秒")
            
            # 更新操作统计
            stats = self._operation_stats[operation]
            stats['count'] += 1
            stats['total_time'] += execution_time
            stats['avg_time'] = stats['total_time'] / stats['count']
            stats['min_time'] = min(stats['min_time'], execution_time)
            stats['max_time'] = max(stats['max_time'], execution_time)
            
            if error:
                stats['errors'] += 1
                self.logger.error(f"操作错误: {operation} {table}, 错误: {error}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        获取性能指标
        
        Returns:
            性能指标字典
        """
        with self._lock:
            # 计算总体统计
            total_operations = sum(stats['count'] for stats in self._operation_stats.values())
            total_time = sum(stats['total_time'] for stats in self._operation_stats.values())
            total_errors = sum(stats['errors'] for stats in self._operation_stats.values())
            
            # 获取最近的指标
            recent_metrics = list(self._metrics)[-100:] if self._metrics else []
            
            return {
                'overview': {
                    'total_operations': total_operations,
                    'total_time': total_time,
                    'avg_time': total_time / total_operations if total_operations > 0 else 0,
                    'total_errors': total_errors,
                    'error_rate': total_errors / total_operations if total_operations > 0 else 0
                },
                'operation_stats': dict(self._operation_stats),
                'slow_queries_count': len(self._slow_queries),
                'recent_metrics': [
                    {
                        'operation': m.operation,
                        'table': m.table,
                        'execution_time': m.execution_time,
                        'timestamp': m.timestamp,
                        'record_count': m.record_count,
                        'error': m.error
                    }
                    for m in recent_metrics
                ]
            }
    
    def get_slow_queries(self) -> List[Dict[str, Any]]:
        """
        获取慢查询列表
        
        Returns:
            慢查询列表
        """
        with self._lock:
            return [
                {
                    'operation': m.operation,
                    'table': m.table,
                    'execution_time': m.execution_time,
                    'timestamp': m.timestamp,
                    'record_count': m.record_count,
                    'error': m.error
                }
                for m in self._slow_queries
            ]
    
    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """
        获取特定操作的统计信息
        
        Args:
            operation: 操作类型
            
        Returns:
            操作统计信息
        """
        with self._lock:
            return dict(self._operation_stats.get(operation, {}))
    
    def get_table_stats(self, table: str) -> Dict[str, Any]:
        """
        获取特定表的统计信息
        
        Args:
            table: 表名
            
        Returns:
            表统计信息
        """
        with self._lock:
            table_metrics = [m for m in self._metrics if m.table == table]
            
            if not table_metrics:
                return {
                    'count': 0,
                    'total_time': 0.0,
                    'avg_time': 0.0,
                    'min_time': 0.0,
                    'max_time': 0.0,
                    'errors': 0
                }
            
            total_time = sum(m.execution_time for m in table_metrics)
            errors = sum(1 for m in table_metrics if m.error)
            
            return {
                'count': len(table_metrics),
                'total_time': total_time,
                'avg_time': total_time / len(table_metrics),
                'min_time': min(m.execution_time for m in table_metrics),
                'max_time': max(m.execution_time for m in table_metrics),
                'errors': errors,
                'error_rate': errors / len(table_metrics)
            }
    
    def clear_metrics(self):
        """清除所有指标"""
        with self._lock:
            self._metrics.clear()
            self._slow_queries.clear()
            self._operation_stats.clear()
            self.logger.info("性能指标已清除")
    
    def is_healthy(self) -> bool:
        """
        检查监控器是否健康
        
        Returns:
            是否健康
        """
        try:
            # 检查错误率
            total_operations = sum(stats['count'] for stats in self._operation_stats.values())
            total_errors = sum(stats['errors'] for stats in self._operation_stats.values())
            
            if total_operations > 0:
                error_rate = total_errors / total_operations
                if error_rate > 0.1:  # 错误率超过10%
                    self.logger.warning(f"错误率过高: {error_rate:.2%}")
                    return False
            
            # 检查慢查询数量
            if len(self._slow_queries) > 100:  # 慢查询过多
                self.logger.warning(f"慢查询数量过多: {len(self._slow_queries)}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            return False
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        获取性能摘要
        
        Returns:
            性能摘要
        """
        metrics = self.get_metrics()
        
        # 计算性能等级
        avg_time = metrics['overview']['avg_time']
        if avg_time < 0.1:
            performance_grade = 'A'
        elif avg_time < 0.5:
            performance_grade = 'B'
        elif avg_time < 1.0:
            performance_grade = 'C'
        else:
            performance_grade = 'D'
        
        return {
            'performance_grade': performance_grade,
            'overview': metrics['overview'],
            'slow_queries_count': metrics['slow_queries_count'],
            'health_status': 'healthy' if self.is_healthy() else 'unhealthy'
        }
