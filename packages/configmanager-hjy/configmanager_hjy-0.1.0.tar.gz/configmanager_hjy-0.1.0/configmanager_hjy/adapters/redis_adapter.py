"""
Redis适配器 - 负责配置的缓存和事件通知
"""

import json
import time
from typing import Dict, Any, List, Optional, Callable
import redis
from loguru import logger


class RedisAdapter:
    """Redis适配器类"""
    
    def __init__(self, config_dict: Dict[str, Any]):
        """
        初始化Redis适配器
        
        Args:
            config_dict: Redis配置字典
        """
        self.config = config_dict
        self.client = None
        self.pubsub = None
        self._init_client()
    
    def _init_client(self):
        """初始化Redis客户端"""
        try:
            self.client = redis.Redis(**self.config)
            # 测试连接
            self.client.ping()
            logger.info("Redis连接初始化成功")
        except Exception as e:
            logger.error(f"Redis连接初始化失败: {e}")
            raise
    
    def _get_cache_key(self, key_path: str, environment: str = "default") -> str:
        """生成缓存键"""
        return f"config:{environment}:{key_path}"
    
    def _get_version_key(self, key_path: str, environment: str = "default") -> str:
        """生成版本缓存键"""
        return f"config:version:{environment}:{key_path}"
    
    def _get_channel(self, environment: str = "default") -> str:
        """生成配置变更通知频道"""
        return f"config:changes:{environment}"
    
    def set_cache(self, key_path: str, value: Any, value_type: str = "string",
                  environment: str = "default", ttl: int = 300) -> bool:
        """
        设置缓存
        
        Args:
            key_path: 配置键路径
            value: 配置值
            value_type: 值类型
            environment: 环境标识
            ttl: 缓存时间（秒）
            
        Returns:
            bool: 操作结果
        """
        try:
            cache_key = self._get_cache_key(key_path, environment)
            cache_data = {
                "value": value,
                "type": value_type,
                "environment": environment,
                "cached_at": time.time()
            }
            
            self.client.hset(cache_key, mapping=cache_data)
            self.client.expire(cache_key, ttl)
            
            logger.debug(f"缓存设置成功: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False
    
    def get_cache(self, key_path: str, environment: str = "default") -> Optional[Dict[str, Any]]:
        """
        获取缓存
        
        Args:
            key_path: 配置键路径
            environment: 环境标识
            
        Returns:
            Dict: 缓存数据
        """
        try:
            cache_key = self._get_cache_key(key_path, environment)
            cache_data = self.client.hgetall(cache_key)
            
            if not cache_data:
                return None
            
            # 转换字节为字符串
            result = {}
            for key, value in cache_data.items():
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                if isinstance(value, bytes):
                    value = value.decode('utf-8')
                result[key] = value
            
            # 解析值
            if result.get('type') == 'json' and result.get('value'):
                try:
                    result['value'] = json.loads(result['value'])
                except json.JSONDecodeError:
                    logger.warning(f"JSON解析失败: {result['value']}")
                    return None
            elif result.get('type') == 'int' and result.get('value'):
                try:
                    result['value'] = int(result['value'])
                except ValueError:
                    logger.warning(f"整数解析失败: {result['value']}")
                    return None
            elif result.get('type') == 'float' and result.get('value'):
                try:
                    result['value'] = float(result['value'])
                except ValueError:
                    logger.warning(f"浮点数解析失败: {result['value']}")
                    return None
            elif result.get('type') == 'bool' and result.get('value'):
                result['value'] = result['value'].lower() == 'true'
            
            return result
            
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return None
    
    def delete_cache(self, key_path: str, environment: str = "default") -> bool:
        """
        删除缓存
        
        Args:
            key_path: 配置键路径
            environment: 环境标识
            
        Returns:
            bool: 操作结果
        """
        try:
            cache_key = self._get_cache_key(key_path, environment)
            version_key = self._get_version_key(key_path, environment)
            
            self.client.delete(cache_key, version_key)
            
            logger.debug(f"缓存删除成功: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False
    
    def clear_cache(self, environment: str = "default") -> bool:
        """
        清除环境的所有缓存
        
        Args:
            environment: 环境标识
            
        Returns:
            bool: 操作结果
        """
        try:
            pattern = f"config:{environment}:*"
            keys = self.client.keys(pattern)
            
            if keys:
                self.client.delete(*keys)
                logger.info(f"清除缓存成功: {len(keys)} 个键")
            
            return True
            
        except Exception as e:
            logger.error(f"清除缓存失败: {e}")
            return False
    
    def set_version_cache(self, key_path: str, version: int, 
                         environment: str = "default", ttl: int = 3600) -> bool:
        """
        设置版本缓存
        
        Args:
            key_path: 配置键路径
            version: 版本号
            environment: 环境标识
            ttl: 缓存时间（秒）
            
        Returns:
            bool: 操作结果
        """
        try:
            version_key = self._get_version_key(key_path, environment)
            self.client.setex(version_key, ttl, version)
            
            logger.debug(f"版本缓存设置成功: {version_key} = {version}")
            return True
            
        except Exception as e:
            logger.error(f"设置版本缓存失败: {e}")
            return False
    
    def get_version_cache(self, key_path: str, environment: str = "default") -> Optional[int]:
        """
        获取版本缓存
        
        Args:
            key_path: 配置键路径
            environment: 环境标识
            
        Returns:
            int: 版本号
        """
        try:
            version_key = self._get_version_key(key_path, environment)
            version = self.client.get(version_key)
            
            if version is not None:
                return int(version)
            
            return None
            
        except Exception as e:
            logger.error(f"获取版本缓存失败: {e}")
            return None
    
    def publish_change(self, key_path: str, old_value: Any, new_value: Any,
                      environment: str = "default", change_type: str = "update") -> bool:
        """
        发布配置变更事件
        
        Args:
            key_path: 配置键路径
            old_value: 旧值
            new_value: 新值
            environment: 环境标识
            change_type: 变更类型
            
        Returns:
            bool: 操作结果
        """
        try:
            channel = self._get_channel(environment)
            message = {
                "key_path": key_path,
                "old_value": old_value,
                "new_value": new_value,
                "environment": environment,
                "change_type": change_type,
                "timestamp": time.time()
            }
            
            self.client.publish(channel, json.dumps(message))
            
            logger.debug(f"配置变更事件发布成功: {key_path}")
            return True
            
        except Exception as e:
            logger.error(f"发布配置变更事件失败: {e}")
            return False
    
    def subscribe_changes(self, callback: Callable[[Dict[str, Any]], None],
                         environment: str = "default") -> bool:
        """
        订阅配置变更事件
        
        Args:
            callback: 回调函数
            environment: 环境标识
            
        Returns:
            bool: 操作结果
        """
        try:
            channel = self._get_channel(environment)
            
            if self.pubsub is None:
                self.pubsub = self.client.pubsub()
            
            self.pubsub.subscribe(channel)
            
            # 启动监听线程
            def listen_thread():
                for message in self.pubsub.listen():
                    if message['type'] == 'message':
                        try:
                            data = json.loads(message['data'])
                            callback(data)
                        except Exception as e:
                            logger.error(f"处理配置变更事件失败: {e}")
            
            import threading
            thread = threading.Thread(target=listen_thread, daemon=True)
            thread.start()
            
            logger.info(f"配置变更订阅成功: {channel}")
            return True
            
        except Exception as e:
            logger.error(f"订阅配置变更事件失败: {e}")
            return False
    
    def unsubscribe_changes(self, environment: str = "default") -> bool:
        """
        取消订阅配置变更事件
        
        Args:
            environment: 环境标识
            
        Returns:
            bool: 操作结果
        """
        try:
            if self.pubsub is not None:
                channel = self._get_channel(environment)
                self.pubsub.unsubscribe(channel)
                logger.info(f"配置变更取消订阅成功: {channel}")
            
            return True
            
        except Exception as e:
            logger.error(f"取消订阅配置变更事件失败: {e}")
            return False
    
    def get_cache_stats(self, environment: str = "default") -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Args:
            environment: 环境标识
            
        Returns:
            Dict: 统计信息
        """
        try:
            pattern = f"config:{environment}:*"
            keys = self.client.keys(pattern)
            
            stats = {
                "total_keys": len(keys),
                "config_keys": 0,
                "version_keys": 0,
                "memory_usage": 0
            }
            
            for key in keys:
                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                if key_str.endswith(':version'):
                    stats["version_keys"] += 1
                else:
                    stats["config_keys"] += 1
                
                # 获取内存使用
                memory = self.client.memory_usage(key)
                if memory:
                    stats["memory_usage"] += memory
            
            return stats
            
        except Exception as e:
            logger.error(f"获取缓存统计信息失败: {e}")
            return {}
    
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
            logger.error(f"Redis连接测试失败: {e}")
            return False
