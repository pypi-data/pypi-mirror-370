"""
缓存管理模块

提供Redis缓存集成和缓存管理功能。
"""

import json
import time
import hashlib
from typing import Any, Optional, Dict, List
from functools import wraps
import redis
from loguru import logger


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", 
                 key_prefix: str = "datamanager:", default_ttl: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            redis_url: Redis连接URL
            key_prefix: 键前缀
            default_ttl: 默认TTL（秒）
        """
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
        self.logger = logger.bind(component="cache_manager")
        
        # 初始化Redis连接
        self._redis_client = None
        self._initialize_redis()
    
    def _initialize_redis(self):
        """初始化Redis连接"""
        try:
            self._redis_client = redis.from_url(self.redis_url)
            # 测试连接
            self._redis_client.ping()
            self.logger.info(f"Redis连接成功: {self.redis_url}")
        except Exception as e:
            self.logger.warning(f"Redis连接失败: {e}, 缓存功能将不可用")
            self._redis_client = None
    
    def _get_key(self, key: str) -> str:
        """获取完整的缓存键"""
        return f"{self.key_prefix}{key}"
    
    def _serialize_value(self, value: Any) -> str:
        """序列化值"""
        return json.dumps(value, ensure_ascii=False)
    
    def _deserialize_value(self, value: str) -> Any:
        """反序列化值"""
        return json.loads(value)
    
    def is_available(self) -> bool:
        """
        检查缓存是否可用
        
        Returns:
            缓存是否可用
        """
        if not self._redis_client:
            return False
        
        try:
            self._redis_client.ping()
            return True
        except Exception:
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            缓存值
        """
        if not self.is_available():
            return default
        
        try:
            full_key = self._get_key(key)
            value = self._redis_client.get(full_key)
            
            if value is None:
                return default
            
            return self._deserialize_value(value)
            
        except Exception as e:
            self.logger.error(f"获取缓存失败: {key}, 错误: {e}")
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: TTL（秒），如果为None则使用默认TTL
            
        Returns:
            是否设置成功
        """
        if not self.is_available():
            return False
        
        try:
            full_key = self._get_key(key)
            serialized_value = self._serialize_value(value)
            ttl = ttl if ttl is not None else self.default_ttl
            
            self._redis_client.setex(full_key, ttl, serialized_value)
            self.logger.debug(f"缓存设置成功: {key}, TTL: {ttl}秒")
            return True
            
        except Exception as e:
            self.logger.error(f"设置缓存失败: {key}, 错误: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        if not self.is_available():
            return False
        
        try:
            full_key = self._get_key(key)
            result = self._redis_client.delete(full_key)
            self.logger.debug(f"缓存删除成功: {key}")
            return result > 0
            
        except Exception as e:
            self.logger.error(f"删除缓存失败: {key}, 错误: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        检查缓存键是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            是否存在
        """
        if not self.is_available():
            return False
        
        try:
            full_key = self._get_key(key)
            return self._redis_client.exists(full_key) > 0
            
        except Exception as e:
            self.logger.error(f"检查缓存存在失败: {key}, 错误: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """
        设置缓存过期时间
        
        Args:
            key: 缓存键
            ttl: TTL（秒）
            
        Returns:
            是否设置成功
        """
        if not self.is_available():
            return False
        
        try:
            full_key = self._get_key(key)
            result = self._redis_client.expire(full_key, ttl)
            self.logger.debug(f"缓存过期时间设置成功: {key}, TTL: {ttl}秒")
            return result
            
        except Exception as e:
            self.logger.error(f"设置缓存过期时间失败: {key}, 错误: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """
        获取缓存剩余时间
        
        Args:
            key: 缓存键
            
        Returns:
            剩余时间（秒），-1表示永不过期，-2表示不存在
        """
        if not self.is_available():
            return -2
        
        try:
            full_key = self._get_key(key)
            return self._redis_client.ttl(full_key)
            
        except Exception as e:
            self.logger.error(f"获取缓存TTL失败: {key}, 错误: {e}")
            return -2
    
    def clear_pattern(self, pattern: str) -> int:
        """
        清除匹配模式的缓存
        
        Args:
            pattern: 匹配模式
            
        Returns:
            清除的缓存数量
        """
        if not self.is_available():
            return 0
        
        try:
            full_pattern = self._get_key(pattern)
            keys = self._redis_client.keys(full_pattern)
            
            if keys:
                deleted = self._redis_client.delete(*keys)
                self.logger.info(f"清除缓存模式成功: {pattern}, 删除数量: {deleted}")
                return deleted
            
            return 0
            
        except Exception as e:
            self.logger.error(f"清除缓存模式失败: {pattern}, 错误: {e}")
            return 0
    
    def clear_all(self) -> int:
        """
        清除所有缓存
        
        Returns:
            清除的缓存数量
        """
        return self.clear_pattern("*")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            统计信息
        """
        if not self.is_available():
            return {
                'available': False,
                'total_keys': 0,
                'memory_usage': 0,
                'hit_rate': 0
            }
        
        try:
            info = self._redis_client.info()
            
            return {
                'available': True,
                'total_keys': info.get('db0', {}).get('keys', 0),
                'memory_usage': info.get('used_memory_human', '0B'),
                'hit_rate': info.get('keyspace_hits', 0) / max(info.get('keyspace_misses', 1), 1),
                'connected_clients': info.get('connected_clients', 0),
                'uptime': info.get('uptime_in_seconds', 0)
            }
            
        except Exception as e:
            self.logger.error(f"获取缓存统计失败: {e}")
            return {
                'available': False,
                'error': str(e)
            }
    
    def cache_result(self, ttl: Optional[int] = None, key_func=None):
        """
        缓存装饰器
        
        Args:
            ttl: TTL（秒）
            key_func: 键生成函数
            
        Returns:
            装饰器
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 生成缓存键
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # 默认键生成策略
                    key_parts = [func.__name__]
                    key_parts.extend(str(arg) for arg in args)
                    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                    cache_key = hashlib.md5("|".join(key_parts).encode()).hexdigest()
                
                # 尝试从缓存获取
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    self.logger.debug(f"缓存命中: {cache_key}")
                    return cached_result
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 缓存结果
                self.set(cache_key, result, ttl)
                self.logger.debug(f"缓存设置: {cache_key}")
                
                return result
            
            return wrapper
        return decorator
    
    def invalidate_pattern(self, pattern: str):
        """
        缓存失效装饰器
        
        Args:
            pattern: 失效模式
            
        Returns:
            装饰器
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                
                # 清除匹配的缓存
                cleared = self.clear_pattern(pattern)
                if cleared > 0:
                    self.logger.debug(f"缓存失效: {pattern}, 清除数量: {cleared}")
                
                return result
            
            return wrapper
        return decorator
