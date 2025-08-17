"""
内存缓存实现
"""

import time
import threading
from typing import Dict, Any, Optional, List
from loguru import logger


class MemoryCache:
    """内存缓存实现"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        初始化内存缓存
        
        Args:
            max_size: 最大缓存项数
            default_ttl: 默认TTL（秒）
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        
        # 启动清理线程
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
        
        logger.info(f"内存缓存初始化成功，最大大小: {max_size}, 默认TTL: {default_ttl}s")
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            Any: 缓存值
        """
        with self.lock:
            if key not in self.cache:
                return None
            
            cache_item = self.cache[key]
            
            # 检查是否过期
            if self._is_expired(cache_item):
                del self.cache[key]
                return None
            
            # 更新访问时间
            cache_item['last_accessed'] = time.time()
            cache_item['access_count'] += 1
            
            return cache_item['value']
    
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
            with self.lock:
                # 检查缓存大小
                if len(self.cache) >= self.max_size and key not in self.cache:
                    self._evict_least_used()
                
                ttl = ttl or self.default_ttl
                expire_time = time.time() + ttl
                
                self.cache[key] = {
                    'value': value,
                    'expire_time': expire_time,
                    'created_time': time.time(),
                    'last_accessed': time.time(),
                    'access_count': 0,
                    'ttl': ttl
                }
                
                logger.debug(f"内存缓存设置成功: {key}")
                return True
                
        except Exception as e:
            logger.error(f"内存缓存设置失败: {e}")
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
            with self.lock:
                if key in self.cache:
                    del self.cache[key]
                    logger.debug(f"内存缓存删除成功: {key}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"内存缓存删除失败: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        检查缓存键是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否存在
        """
        with self.lock:
            if key not in self.cache:
                return False
            
            # 检查是否过期
            if self._is_expired(self.cache[key]):
                del self.cache[key]
                return False
            
            return True
    
    def clear(self) -> bool:
        """
        清空缓存
        
        Returns:
            bool: 操作结果
        """
        try:
            with self.lock:
                self.cache.clear()
                logger.info("内存缓存清空成功")
                return True
                
        except Exception as e:
            logger.error(f"内存缓存清空失败: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict: 统计信息
        """
        with self.lock:
            total_items = len(self.cache)
            expired_items = 0
            total_access_count = 0
            total_size = 0
            
            for key, item in self.cache.items():
                if self._is_expired(item):
                    expired_items += 1
                else:
                    total_access_count += item['access_count']
                    total_size += self._estimate_size(item['value'])
            
            return {
                'total_items': total_items,
                'expired_items': expired_items,
                'active_items': total_items - expired_items,
                'max_size': self.max_size,
                'usage_percent': (total_items / self.max_size) * 100 if self.max_size > 0 else 0,
                'total_access_count': total_access_count,
                'average_access_count': total_access_count / (total_items - expired_items) if (total_items - expired_items) > 0 else 0,
                'estimated_size_bytes': total_size
            }
    
    def get_keys(self, pattern: str = "*") -> List[str]:
        """
        获取匹配模式的缓存键
        
        Args:
            pattern: 匹配模式（支持简单的通配符）
            
        Returns:
            List: 匹配的键列表
        """
        with self.lock:
            import fnmatch
            keys = []
            
            for key in self.cache.keys():
                if not self._is_expired(self.cache[key]) and fnmatch.fnmatch(key, pattern):
                    keys.append(key)
            
            return keys
    
    def get_ttl(self, key: str) -> Optional[int]:
        """
        获取缓存项的剩余TTL
        
        Args:
            key: 缓存键
            
        Returns:
            int: 剩余TTL（秒），-1表示永不过期，None表示不存在
        """
        with self.lock:
            if key not in self.cache:
                return None
            
            item = self.cache[key]
            if self._is_expired(item):
                del self.cache[key]
                return None
            
            remaining = int(item['expire_time'] - time.time())
            return max(0, remaining)
    
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
            with self.lock:
                if key not in self.cache:
                    return False
                
                item = self.cache[key]
                if self._is_expired(item):
                    del self.cache[key]
                    return False
                
                item['expire_time'] = time.time() + ttl
                item['ttl'] = ttl
                
                logger.debug(f"内存缓存TTL设置成功: {key} -> {ttl}s")
                return True
                
        except Exception as e:
            logger.error(f"内存缓存TTL设置失败: {e}")
            return False
    
    def _is_expired(self, cache_item: Dict[str, Any]) -> bool:
        """
        检查缓存项是否过期
        
        Args:
            cache_item: 缓存项
            
        Returns:
            bool: 是否过期
        """
        return time.time() > cache_item['expire_time']
    
    def _evict_least_used(self):
        """驱逐最少使用的缓存项"""
        if not self.cache:
            return
        
        # 按访问次数和最后访问时间排序
        sorted_items = sorted(
            self.cache.items(),
            key=lambda x: (x[1]['access_count'], x[1]['last_accessed'])
        )
        
        # 删除最少的项
        items_to_remove = len(self.cache) - self.max_size + 1
        for i in range(items_to_remove):
            if i < len(sorted_items):
                key = sorted_items[i][0]
                del self.cache[key]
                logger.debug(f"内存缓存驱逐项: {key}")
    
    def _cleanup_loop(self):
        """清理过期项的循环"""
        while True:
            try:
                time.sleep(60)  # 每分钟清理一次
                self._cleanup_expired()
            except Exception as e:
                logger.error(f"内存缓存清理循环出错: {e}")
    
    def _cleanup_expired(self):
        """清理过期的缓存项"""
        with self.lock:
            expired_keys = []
            for key, item in self.cache.items():
                if self._is_expired(item):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
            
            if expired_keys:
                logger.debug(f"内存缓存清理了 {len(expired_keys)} 个过期项")
    
    def _estimate_size(self, value: Any) -> int:
        """
        估算值的大小（字节）
        
        Args:
            value: 要估算的值
            
        Returns:
            int: 估算的大小
        """
        try:
            import sys
            return sys.getsizeof(value)
        except:
            return 0
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有缓存项（不包括过期的）
        
        Returns:
            Dict: 所有缓存项
        """
        with self.lock:
            result = {}
            expired_keys = []
            
            for key, item in self.cache.items():
                if self._is_expired(item):
                    expired_keys.append(key)
                else:
                    result[key] = item['value']
            
            # 清理过期项
            for key in expired_keys:
                del self.cache[key]
            
            return result
    
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
            success_count = 0
            total_count = len(items)
            
            for key, value in items.items():
                if self.set(key, value, ttl):
                    success_count += 1
            
            logger.info(f"内存缓存批量设置完成: {success_count}/{total_count}")
            return success_count == total_count
            
        except Exception as e:
            logger.error(f"内存缓存批量设置失败: {e}")
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
            success_count = 0
            total_count = len(keys)
            
            for key in keys:
                if self.delete(key):
                    success_count += 1
            
            logger.info(f"内存缓存批量删除完成: {success_count}/{total_count}")
            return success_count == total_count
            
        except Exception as e:
            logger.error(f"内存缓存批量删除失败: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict: 统计信息
        """
        with self.lock:
            total_items = len(self.cache)
            total_size = sum(self._estimate_size(item['value']) for item in self.cache.values())
            
            # 计算访问统计
            total_access = sum(item.get('access_count', 0) for item in self.cache.values())
            avg_access = total_access / total_items if total_items > 0 else 0
            
            return {
                'total_items': total_items,
                'total_size_bytes': total_size,
                'total_access_count': total_access,
                'average_access_count': avg_access,
                'max_size': self.max_size,
                'default_ttl': self.default_ttl
            }
    
    def get_size(self) -> int:
        """
        获取缓存大小
        
        Returns:
            int: 缓存项数量
        """
        with self.lock:
            return len(self.cache)
    
    def get_keys(self, pattern: str = "*") -> List[str]:
        """
        获取匹配模式的缓存键
        
        Args:
            pattern: 键模式（支持简单通配符）
            
        Returns:
            List[str]: 匹配的键列表
        """
        with self.lock:
            if pattern == "*":
                return list(self.cache.keys())
            
            # 简单的模式匹配
            import fnmatch
            return [key for key in self.cache.keys() if fnmatch.fnmatch(key, pattern)]