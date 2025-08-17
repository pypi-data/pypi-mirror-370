"""
缓存管理器
"""

import time
import threading
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from loguru import logger

from .memory_cache import MemoryCache
from .redis_cache import RedisCache


class CacheStrategy(Enum):
    """缓存策略枚举"""
    MEMORY_ONLY = "memory_only"      # 仅内存缓存
    REDIS_ONLY = "redis_only"        # 仅Redis缓存
    MEMORY_FIRST = "memory_first"    # 内存优先
    REDIS_FIRST = "redis_first"      # Redis优先
    LAYERED = "layered"              # 分层缓存


class CacheManager:
    """缓存管理器 - 统一管理内存缓存和Redis缓存"""
    
    def __init__(self, 
                 redis_config: Dict[str, Any],
                 memory_config: Optional[Dict[str, Any]] = None,
                 strategy: CacheStrategy = CacheStrategy.LAYERED):
        """
        初始化缓存管理器
        
        Args:
            redis_config: Redis配置
            memory_config: 内存缓存配置
            strategy: 缓存策略
        """
        self.strategy = strategy
        self.stats = {
            'memory_hits': 0,
            'redis_hits': 0,
            'misses': 0,
            'memory_sets': 0,
            'redis_sets': 0,
            'memory_deletes': 0,
            'redis_deletes': 0,
            'errors': 0
        }
        self.stats_lock = threading.Lock()
        
        # 初始化缓存实例
        self._init_caches(redis_config, memory_config)
        
        # 启动统计监控线程
        self._start_stats_monitor()
        
        logger.info(f"缓存管理器初始化成功，策略: {strategy.value}")
    
    def _init_caches(self, redis_config: Dict[str, Any], memory_config: Optional[Dict[str, Any]]):
        """初始化缓存实例"""
        try:
            # 初始化内存缓存
            memory_config = memory_config or {}
            self.memory_cache = MemoryCache(
                max_size=memory_config.get('max_size', 1000),
                default_ttl=memory_config.get('default_ttl', 300)
            )
            
            # 根据策略决定是否初始化Redis缓存
            if self.strategy != CacheStrategy.MEMORY_ONLY:
                try:
                    self.redis_cache = RedisCache(redis_config)
                except Exception as e:
                    logger.warning(f"Redis缓存初始化失败，将使用仅内存模式: {e}")
                    self.redis_cache = None
            else:
                self.redis_cache = None
            
        except Exception as e:
            logger.error(f"缓存初始化失败: {e}")
            raise
    
    def _start_stats_monitor(self):
        """启动统计监控线程"""
        def monitor_loop():
            while True:
                try:
                    time.sleep(60)  # 每分钟输出一次统计
                    self._log_stats()
                except Exception as e:
                    logger.error(f"统计监控异常: {e}")
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def _log_stats(self):
        """输出统计信息"""
        with self.stats_lock:
            total_requests = self.stats['memory_hits'] + self.stats['redis_hits'] + self.stats['misses']
            if total_requests > 0:
                memory_hit_rate = self.stats['memory_hits'] / total_requests * 100
                redis_hit_rate = self.stats['redis_hits'] / total_requests * 100
                miss_rate = self.stats['misses'] / total_requests * 100
                
                logger.info(f"缓存统计 - 内存命中率: {memory_hit_rate:.1f}%, "
                          f"Redis命中率: {redis_hit_rate:.1f}%, "
                          f"未命中率: {miss_rate:.1f}%")
    
    def _update_stats(self, stat_name: str, increment: int = 1):
        """更新统计信息"""
        with self.stats_lock:
            self.stats[stat_name] += increment
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            Any: 缓存值
        """
        try:
            if self.strategy == CacheStrategy.MEMORY_ONLY:
                return self._get_memory_only(key, default)
            elif self.strategy == CacheStrategy.REDIS_ONLY:
                return self._get_redis_only(key, default)
            elif self.strategy == CacheStrategy.MEMORY_FIRST:
                return self._get_memory_first(key, default)
            elif self.strategy == CacheStrategy.REDIS_FIRST:
                return self._get_redis_first(key, default)
            elif self.strategy == CacheStrategy.LAYERED:
                return self._get_layered(key, default)
            else:
                return default
                
        except Exception as e:
            logger.error(f"缓存获取失败: {e}")
            self._update_stats('errors')
            return default
    
    def _get_memory_only(self, key: str, default: Any) -> Any:
        """仅内存缓存策略"""
        value = self.memory_cache.get(key)
        if value is not None:
            self._update_stats('memory_hits')
            return value
        else:
            self._update_stats('misses')
            return default
    
    def _get_redis_only(self, key: str, default: Any) -> Any:
        """仅Redis缓存策略"""
        if self.redis_cache is None:
            self._update_stats('misses')
            return default
        
        value = self.redis_cache.get(key)
        if value is not None:
            self._update_stats('redis_hits')
            return value
        else:
            self._update_stats('misses')
            return default
    
    def _get_memory_first(self, key: str, default: Any) -> Any:
        """内存优先策略"""
        # 先从内存获取
        value = self.memory_cache.get(key)
        if value is not None:
            self._update_stats('memory_hits')
            return value
        
        # 从Redis获取
        if self.redis_cache is not None:
            value = self.redis_cache.get(key)
            if value is not None:
                self._update_stats('redis_hits')
                # 更新到内存缓存
                self.memory_cache.set(key, value)
                return value
        
        self._update_stats('misses')
        return default
    
    def _get_redis_first(self, key: str, default: Any) -> Any:
        """Redis优先策略"""
        # 先从Redis获取
        if self.redis_cache is not None:
            value = self.redis_cache.get(key)
            if value is not None:
                self._update_stats('redis_hits')
                return value
        
        # 从内存获取
        value = self.memory_cache.get(key)
        if value is not None:
            self._update_stats('memory_hits')
            # 更新到Redis缓存
            if self.redis_cache is not None:
                self.redis_cache.set(key, value)
            return value
        
        self._update_stats('misses')
        return default
    
    def _get_layered(self, key: str, default: Any) -> Any:
        """分层缓存策略"""
        # 先从内存获取
        value = self.memory_cache.get(key)
        if value is not None:
            self._update_stats('memory_hits')
            return value
        
        # 从Redis获取
        if self.redis_cache is not None:
            value = self.redis_cache.get(key)
            if value is not None:
                self._update_stats('redis_hits')
                # 更新到内存缓存（预热）
                self.memory_cache.set(key, value, ttl=60)  # 短期缓存
                return value
        
        self._update_stats('misses')
        return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            sync: bool = True) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: TTL（秒）
            sync: 是否同步到所有缓存层
            
        Returns:
            bool: 操作结果
        """
        try:
            success = True
            
            if self.strategy == CacheStrategy.MEMORY_ONLY:
                success = self.memory_cache.set(key, value, ttl)
                if success:
                    self._update_stats('memory_sets')
            elif self.strategy == CacheStrategy.REDIS_ONLY:
                if self.redis_cache is not None:
                    success = self.redis_cache.set(key, value, ttl)
                    if success:
                        self._update_stats('redis_sets')
                else:
                    success = False
            else:
                # 多层级策略
                if sync:
                    # 同步到所有缓存层
                    memory_success = self.memory_cache.set(key, value, ttl)
                    redis_success = True
                    if self.redis_cache is not None:
                        redis_success = self.redis_cache.set(key, value, ttl)
                    
                    if memory_success:
                        self._update_stats('memory_sets')
                    if redis_success:
                        self._update_stats('redis_sets')
                    
                    success = memory_success and redis_success
                else:
                    # 根据策略选择缓存层
                    if self.strategy in [CacheStrategy.MEMORY_FIRST, CacheStrategy.LAYERED]:
                        success = self.memory_cache.set(key, value, ttl)
                        if success:
                            self._update_stats('memory_sets')
                    else:
                        if self.redis_cache is not None:
                            success = self.redis_cache.set(key, value, ttl)
                            if success:
                                self._update_stats('redis_sets')
                        else:
                            success = False
            
            if success:
                logger.debug(f"缓存设置成功: {key}")
            else:
                logger.warning(f"缓存设置失败: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"缓存设置异常: {e}")
            self._update_stats('errors')
            return False
    
    def delete(self, key: str, sync: bool = True) -> bool:
        """
        删除缓存值
        
        Args:
            key: 缓存键
            sync: 是否同步删除所有缓存层
            
        Returns:
            bool: 操作结果
        """
        try:
            success = True
            
            if self.strategy == CacheStrategy.MEMORY_ONLY:
                success = self.memory_cache.delete(key)
                if success:
                    self._update_stats('memory_deletes')
            elif self.strategy == CacheStrategy.REDIS_ONLY:
                if self.redis_cache is not None:
                    success = self.redis_cache.delete(key)
                    if success:
                        self._update_stats('redis_deletes')
                else:
                    success = False
            else:
                # 多层级策略
                if sync:
                    # 同步删除所有缓存层
                    memory_success = self.memory_cache.delete(key)
                    redis_success = True
                    if self.redis_cache is not None:
                        redis_success = self.redis_cache.delete(key)
                    
                    if memory_success:
                        self._update_stats('memory_deletes')
                    if redis_success:
                        self._update_stats('redis_deletes')
                    
                    success = memory_success or redis_success  # 任一成功即可
                else:
                    # 根据策略选择缓存层
                    if self.strategy in [CacheStrategy.MEMORY_FIRST, CacheStrategy.LAYERED]:
                        success = self.memory_cache.delete(key)
                        if success:
                            self._update_stats('memory_deletes')
                    else:
                        if self.redis_cache is not None:
                            success = self.redis_cache.delete(key)
                            if success:
                                self._update_stats('redis_deletes')
                        else:
                            success = False
            
            if success:
                logger.debug(f"缓存删除成功: {key}")
            else:
                logger.warning(f"缓存删除失败: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"缓存删除异常: {e}")
            self._update_stats('errors')
            return False
    
    def clear(self, sync: bool = True) -> bool:
        """
        清空所有缓存
        
        Args:
            sync: 是否同步清空所有缓存层
            
        Returns:
            bool: 操作结果
        """
        try:
            success = True
            
            if self.strategy == CacheStrategy.MEMORY_ONLY:
                success = self.memory_cache.clear()
            elif self.strategy == CacheStrategy.REDIS_ONLY:
                if self.redis_cache is not None:
                    success = self.redis_cache.clear()
                else:
                    success = False
            else:
                # 多层级策略
                if sync:
                    memory_success = self.memory_cache.clear()
                    redis_success = True
                    if self.redis_cache is not None:
                        redis_success = self.redis_cache.clear()
                    success = memory_success and redis_success
                else:
                    # 根据策略选择缓存层
                    if self.strategy in [CacheStrategy.MEMORY_FIRST, CacheStrategy.LAYERED]:
                        success = self.memory_cache.clear()
                    else:
                        if self.redis_cache is not None:
                            success = self.redis_cache.clear()
                        else:
                            success = False
            
            if success:
                logger.info("缓存清空成功")
            else:
                logger.warning("缓存清空失败")
            
            return success
            
        except Exception as e:
            logger.error(f"缓存清空异常: {e}")
            self._update_stats('errors')
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
            if self.strategy == CacheStrategy.MEMORY_ONLY:
                return self.memory_cache.exists(key)
            elif self.strategy == CacheStrategy.REDIS_ONLY:
                if self.redis_cache is not None:
                    return self.redis_cache.exists(key)
                else:
                    return False
            else:
                # 多层级策略
                memory_exists = self.memory_cache.exists(key)
                redis_exists = False
                if self.redis_cache is not None:
                    redis_exists = self.redis_cache.exists(key)
                return memory_exists or redis_exists
                
        except Exception as e:
            logger.error(f"缓存存在检查异常: {e}")
            self._update_stats('errors')
            return False
    
    def get_ttl(self, key: str) -> Optional[int]:
        """
        获取缓存键的TTL
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[int]: TTL（秒），-1表示永不过期，None表示不存在
        """
        try:
            if self.strategy == CacheStrategy.MEMORY_ONLY:
                return self.memory_cache.get_ttl(key)
            elif self.strategy == CacheStrategy.REDIS_ONLY:
                if self.redis_cache is not None:
                    return self.redis_cache.get_ttl(key)
                else:
                    return None
            else:
                # 多层级策略，优先返回内存缓存的TTL
                ttl = self.memory_cache.get_ttl(key)
                if ttl is not None:
                    return ttl
                if self.redis_cache is not None:
                    return self.redis_cache.get_ttl(key)
                return None
                
        except Exception as e:
            logger.error(f"获取TTL异常: {e}")
            self._update_stats('errors')
            return None
    
    def set_ttl(self, key: str, ttl: int) -> bool:
        """
        设置缓存键的TTL
        
        Args:
            key: 缓存键
            ttl: TTL（秒）
            
        Returns:
            bool: 操作结果
        """
        try:
            success = True
            
            if self.strategy == CacheStrategy.MEMORY_ONLY:
                success = self.memory_cache.set_ttl(key, ttl)
            elif self.strategy == CacheStrategy.REDIS_ONLY:
                if self.redis_cache is not None:
                    success = self.redis_cache.set_ttl(key, ttl)
                else:
                    success = False
            else:
                # 多层级策略
                memory_success = self.memory_cache.set_ttl(key, ttl)
                redis_success = True
                if self.redis_cache is not None:
                    redis_success = self.redis_cache.set_ttl(key, ttl)
                success = memory_success and redis_success
            
            if success:
                logger.debug(f"TTL设置成功: {key} -> {ttl}s")
            else:
                logger.warning(f"TTL设置失败: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"TTL设置异常: {e}")
            self._update_stats('errors')
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        with self.stats_lock:
            stats = self.stats.copy()
        
        # 添加缓存层统计
        if hasattr(self, 'memory_cache'):
            stats['memory_cache_stats'] = self.memory_cache.get_stats()
        
        if hasattr(self, 'redis_cache') and self.redis_cache is not None:
            stats['redis_cache_stats'] = self.redis_cache.get_stats()
        else:
            stats['redis_cache_stats'] = {}
        
        # 计算命中率
        total_requests = stats['memory_hits'] + stats['redis_hits'] + stats['misses']
        if total_requests > 0:
            stats['memory_hit_rate'] = stats['memory_hits'] / total_requests * 100
            stats['redis_hit_rate'] = stats['redis_hits'] / total_requests * 100
            stats['miss_rate'] = stats['misses'] / total_requests * 100
        else:
            stats['memory_hit_rate'] = 0
            stats['redis_hit_rate'] = 0
            stats['miss_rate'] = 0
        
        return stats
    
    def reset_stats(self):
        """重置统计信息"""
        with self.stats_lock:
            for key in self.stats:
                self.stats[key] = 0
        logger.info("缓存统计已重置")
    
    def health_check(self) -> Dict[str, Dict[str, str]]:
        """
        健康检查
        
        Returns:
            Dict[str, Dict[str, str]]: 各缓存层健康状态
        """
        health_status = {}
        
        try:
            # 检查内存缓存
            if hasattr(self, 'memory_cache'):
                health_status['memory'] = {
                    'status': 'healthy',
                    'message': '内存缓存运行正常'
                }
            else:
                health_status['memory'] = {
                    'status': 'unavailable',
                    'message': '内存缓存未初始化'
                }
        except Exception as e:
            health_status['memory'] = {
                'status': 'error',
                'message': f'内存缓存检查失败: {e}'
            }
        
        try:
            # 检查Redis缓存
            if hasattr(self, 'redis_cache') and self.redis_cache is not None:
                # 尝试ping Redis
                self.redis_cache.client.ping()
                health_status['redis'] = {
                    'status': 'healthy',
                    'message': 'Redis缓存运行正常'
                }
            else:
                health_status['redis'] = {
                    'status': 'unavailable',
                    'message': 'Redis缓存未初始化或连接失败'
                }
        except Exception as e:
            health_status['redis'] = {
                'status': 'unavailable',
                'message': f'Redis缓存检查失败: {e}'
            }
        
        return health_status
    
    def get_keys(self, pattern: str = "*") -> List[str]:
        """
        获取匹配模式的缓存键
        
        Args:
            pattern: 键模式
            
        Returns:
            List[str]: 匹配的键列表
        """
        try:
            keys = set()
            
            if self.strategy != CacheStrategy.REDIS_ONLY:
                # 从内存缓存获取
                memory_keys = self.memory_cache.get_keys(pattern)
                keys.update(memory_keys)
            
            if self.strategy != CacheStrategy.MEMORY_ONLY and self.redis_cache is not None:
                # 从Redis缓存获取
                redis_keys = self.redis_cache.get_keys(pattern)
                keys.update(redis_keys)
            
            return list(keys)
            
        except Exception as e:
            logger.error(f"获取缓存键异常: {e}")
            self._update_stats('errors')
            return []
    
    def get_size(self) -> Dict[str, int]:
        """
        获取各缓存层的大小
        
        Returns:
            Dict[str, int]: 各缓存层的大小
        """
        sizes = {}
        
        try:
            if hasattr(self, 'memory_cache'):
                sizes['memory_cache'] = self.memory_cache.get_size()
        except Exception:
            sizes['memory_cache'] = 0
        
        try:
            if hasattr(self, 'redis_cache') and self.redis_cache is not None:
                sizes['redis_cache'] = self.redis_cache.get_size()
            else:
                sizes['redis_cache'] = 0
        except Exception:
            sizes['redis_cache'] = 0
        
        return sizes
