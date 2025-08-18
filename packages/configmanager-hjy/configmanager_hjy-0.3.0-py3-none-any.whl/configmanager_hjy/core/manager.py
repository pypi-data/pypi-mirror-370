"""
配置管理器核心类
"""

import os
from typing import Any, Dict, Optional, Callable
from loguru import logger


class ConfigManager:
    """统一配置管理器"""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        初始化配置管理器
        
        Args:
            config_dict: 初始配置字典
        """
        self._config = config_dict or {}
        self._watchers = {}
        logger.info("ConfigManager initialized")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        old_value = config.get(keys[-1])
        config[keys[-1]] = value
        
        # 触发监听器
        if key in self._watchers:
            for callback in self._watchers[key]:
                try:
                    callback(old_value, value)
                except Exception as e:
                    logger.error(f"Error in config watcher: {e}")
    
    def watch(self, key: str) -> Callable:
        """
        装饰器：监听配置变更
        
        Args:
            key: 要监听的配置键
            
        Returns:
            装饰器函数
        """
        def decorator(func: Callable) -> Callable:
            if key not in self._watchers:
                self._watchers[key] = []
            self._watchers[key].append(func)
            return func
        return decorator
    
    def unwatch(self, key: str, func: Callable) -> None:
        """
        取消监听配置变更
        
        Args:
            key: 配置键
            func: 要移除的监听函数
        """
        if key in self._watchers and func in self._watchers[key]:
            self._watchers[key].remove(func)
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            所有配置的字典
        """
        return self._config.copy()
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        批量更新配置
        
        Args:
            config_dict: 要更新的配置字典
        """
        for key, value in config_dict.items():
            self.set(key, value)
    
    def delete(self, key: str) -> None:
        """
        删除配置项
        
        Args:
            key: 要删除的配置键
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if isinstance(config, dict) and k in config:
                config = config[k]
            else:
                return
        
        if isinstance(config, dict) and keys[-1] in config:
            old_value = config[keys[-1]]
            del config[keys[-1]]
            
            # 触发监听器
            if key in self._watchers:
                for callback in self._watchers[key]:
                    try:
                        callback(old_value, None)
                    except Exception as e:
                        logger.error(f"Error in config watcher: {e}")
