"""
Redis缓存实现
"""

import json
import time
from typing import Dict, Any, Optional, List
import redis
from loguru import logger


class RedisCache:
    """Redis缓存实现"""
    
    def __init__(self, config_dict: Dict[str, Any]):
        """
        初始化Redis缓存
        
        Args:
            config_dict: Redis配置字典
        """
        self.config = config_dict
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """初始化Redis客户端"""
        try:
            self.client = redis.Redis(**self.config)
            # 测试连接
            self.client.ping()
            logger.info("Redis缓存连接初始化成功")
        except Exception as e:
            logger.error(f"Redis缓存连接初始化失败: {e}")
            raise
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            Any: 缓存值
        """
        try:
            value = self.client.get(key)
            if value is None:
                return None
            
            # 尝试解析JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # 如果不是JSON，返回原始值
                return value.decode('utf-8') if isinstance(value, bytes) else value
                
        except Exception as e:
            logger.error(f"Redis缓存获取失败: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: TTL（秒）
            
        Returns:
            bool: 操作结果
        """
        try:
            # 序列化值
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, ensure_ascii=False)
            else:
                serialized_value = str(value)
            
            if ttl is not None:
                self.client.setex(key, ttl, serialized_value)
            else:
                self.client.set(key, serialized_value)
            
            logger.debug(f"Redis缓存设置成功: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Redis缓存设置失败: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 操作结果
        """
        try:
            result = self.client.delete(key)
            logger.debug(f"Redis缓存删除成功: {key}")
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis缓存删除失败: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        检查缓存键是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否存在
        """
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis缓存检查存在失败: {e}")
            return False
    
    def clear(self) -> bool:
        """
        清空缓存
        
        Returns:
            bool: 操作结果
        """
        try:
            self.client.flushdb()
            logger.info("Redis缓存清空成功")
            return True
            
        except Exception as e:
            logger.error(f"Redis缓存清空失败: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            info = self.client.info()
            
            return {
                'total_keys': info.get('db0', {}).get('keys', 0),
                'used_memory': info.get('used_memory', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'connected_clients': info.get('connected_clients', 0),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0)
            }
            
        except Exception as e:
            logger.error(f"获取Redis缓存统计信息失败: {e}")
            return {}
    
    def get_keys(self, pattern: str = "*") -> List[str]:
        """
        获取匹配模式的缓存键
        
        Args:
            pattern: 匹配模式
            
        Returns:
            List: 匹配的键列表
        """
        try:
            keys = self.client.keys(pattern)
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
            
        except Exception as e:
            logger.error(f"获取Redis缓存键失败: {e}")
            return []
    
    def get_ttl(self, key: str) -> Optional[int]:
        """
        获取缓存项的剩余TTL
        
        Args:
            key: 缓存键
            
        Returns:
            int: 剩余TTL（秒），-1表示永不过期，None表示不存在
        """
        try:
            ttl = self.client.ttl(key)
            return ttl if ttl != -2 else None  # -2表示键不存在
            
        except Exception as e:
            logger.error(f"获取Redis缓存TTL失败: {e}")
            return None
    
    def set_ttl(self, key: str, ttl: int) -> bool:
        """
        设置缓存项的TTL
        
        Args:
            key: 缓存键
            ttl: 新的TTL（秒）
            
        Returns:
            bool: 操作结果
        """
        try:
            result = self.client.expire(key, ttl)
            logger.debug(f"Redis缓存TTL设置成功: {key} -> {ttl}s")
            return result
            
        except Exception as e:
            logger.error(f"Redis缓存TTL设置失败: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有缓存项
        
        Returns:
            Dict: 所有缓存项
        """
        try:
            keys = self.client.keys("*")
            result = {}
            
            for key in keys:
                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                value = self.get(key_str)
                if value is not None:
                    result[key_str] = value
            
            return result
            
        except Exception as e:
            logger.error(f"获取Redis缓存所有项失败: {e}")
            return {}
    
    def set_many(self, items: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        批量设置缓存项
        
        Args:
            items: 缓存项字典
            ttl: TTL（秒）
            
        Returns:
            bool: 操作结果
        """
        try:
            pipeline = self.client.pipeline()
            
            for key, value in items.items():
                if isinstance(value, (dict, list)):
                    serialized_value = json.dumps(value, ensure_ascii=False)
                else:
                    serialized_value = str(value)
                
                if ttl is not None:
                    pipeline.setex(key, ttl, serialized_value)
                else:
                    pipeline.set(key, serialized_value)
            
            pipeline.execute()
            logger.info(f"Redis缓存批量设置完成: {len(items)} 项")
            return True
            
        except Exception as e:
            logger.error(f"Redis缓存批量设置失败: {e}")
            return False
    
    def delete_many(self, keys: List[str]) -> bool:
        """
        批量删除缓存项
        
        Args:
            keys: 要删除的键列表
            
        Returns:
            bool: 操作结果
        """
        try:
            if not keys:
                return True
            
            result = self.client.delete(*keys)
            logger.info(f"Redis缓存批量删除完成: {result}/{len(keys)} 项")
            return result == len(keys)
            
        except Exception as e:
            logger.error(f"Redis缓存批量删除失败: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        递增计数器
        
        Args:
            key: 缓存键
            amount: 递增数量
            
        Returns:
            int: 递增后的值
        """
        try:
            return self.client.incr(key, amount)
        except Exception as e:
            logger.error(f"Redis缓存递增失败: {e}")
            return None
    
    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """
        递减计数器
        
        Args:
            key: 缓存键
            amount: 递减数量
            
        Returns:
            int: 递减后的值
        """
        try:
            return self.client.decr(key, amount)
        except Exception as e:
            logger.error(f"Redis缓存递减失败: {e}")
            return None
    
    def get_hash(self, key: str, field: str) -> Optional[Any]:
        """
        获取哈希表字段值
        
        Args:
            key: 哈希表键
            field: 字段名
            
        Returns:
            Any: 字段值
        """
        try:
            value = self.client.hget(key, field)
            if value is None:
                return None
            
            # 尝试解析JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value.decode('utf-8') if isinstance(value, bytes) else value
                
        except Exception as e:
            logger.error(f"Redis缓存获取哈希字段失败: {e}")
            return None
    
    def set_hash(self, key: str, field: str, value: Any) -> bool:
        """
        设置哈希表字段值
        
        Args:
            key: 哈希表键
            field: 字段名
            value: 字段值
            
        Returns:
            bool: 操作结果
        """
        try:
            # 序列化值
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, ensure_ascii=False)
            else:
                serialized_value = str(value)
            
            result = self.client.hset(key, field, serialized_value)
            logger.debug(f"Redis缓存设置哈希字段成功: {key}.{field}")
            return True
            
        except Exception as e:
            logger.error(f"Redis缓存设置哈希字段失败: {e}")
            return False
    
    def get_hash_all(self, key: str) -> Dict[str, Any]:
        """
        获取哈希表所有字段
        
        Args:
            key: 哈希表键
            
        Returns:
            Dict: 所有字段
        """
        try:
            hash_data = self.client.hgetall(key)
            result = {}
            
            for field, value in hash_data.items():
                field_str = field.decode('utf-8') if isinstance(field, bytes) else field
                
                # 尝试解析JSON
                try:
                    result[field_str] = json.loads(value)
                except json.JSONDecodeError:
                    result[field_str] = value.decode('utf-8') if isinstance(value, bytes) else value
            
            return result
            
        except Exception as e:
            logger.error(f"Redis缓存获取哈希表失败: {e}")
            return {}
    
    def set_hash_many(self, key: str, fields: Dict[str, Any]) -> bool:
        """
        批量设置哈希表字段
        
        Args:
            key: 哈希表键
            fields: 字段字典
            
        Returns:
            bool: 操作结果
        """
        try:
            # 序列化所有值
            serialized_fields = {}
            for field, value in fields.items():
                if isinstance(value, (dict, list)):
                    serialized_fields[field] = json.dumps(value, ensure_ascii=False)
                else:
                    serialized_fields[field] = str(value)
            
            self.client.hset(key, mapping=serialized_fields)
            logger.info(f"Redis缓存批量设置哈希字段完成: {key} -> {len(fields)} 字段")
            return True
            
        except Exception as e:
            logger.error(f"Redis缓存批量设置哈希字段失败: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        测试Redis连接
        
        Returns:
            bool: 连接状态
        """
        try:
            self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis缓存连接测试失败: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            info = self.client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory', 0),
                'used_memory_peak': info.get('used_memory_peak', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            logger.error(f"获取Redis统计信息失败: {e}")
            return {}
    
    def get_size(self) -> int:
        """
        获取缓存大小
        
        Returns:
            int: 缓存项数量
        """
        try:
            return self.client.dbsize()
        except Exception as e:
            logger.error(f"获取Redis缓存大小失败: {e}")
            return 0
    
    def get_keys(self, pattern: str = "*") -> List[str]:
        """
        获取匹配模式的缓存键
        
        Args:
            pattern: 键模式
            
        Returns:
            List[str]: 匹配的键列表
        """
        try:
            keys = self.client.keys(pattern)
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
        except Exception as e:
            logger.error(f"获取Redis缓存键失败: {e}")
            return []