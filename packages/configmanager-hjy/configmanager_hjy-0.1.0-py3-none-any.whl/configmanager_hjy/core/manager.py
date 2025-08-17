"""
配置管理器核心类
"""

import json
from typing import Dict, Any, List, Optional, Callable, Union
from loguru import logger

from ..adapters.database import DatabaseAdapter
from ..adapters.redis_adapter import RedisAdapter
from ..adapters.oss_adapter import OSSAdapter
from .config import init, get_config, validate_required_fields


class ConfigManager:
    """配置管理器核心类"""
    
    def __init__(self, config_dict: Dict[str, Any]):
        """
        初始化配置管理器
        
        Args:
            config_dict: 配置字典
        """
        # 初始化配置
        self.config = init(config_dict)
        self.environment = self.config.system.environment
        
        # 初始化适配器
        self.db_adapter = DatabaseAdapter(self.config.database.dict())
        self.redis_adapter = RedisAdapter(self.config.redis.dict())
        self.oss_adapter = OSSAdapter(self.config.oss.dict())
        
        # 监听器管理
        self._watchers: Dict[str, List[Callable]] = {}
        
        # 启动配置变更监听
        self._start_change_listener()
        
        logger.info("ConfigManager初始化成功")
    
    def _start_change_listener(self):
        """启动配置变更监听"""
        try:
            self.redis_adapter.subscribe_changes(self._on_config_change, self.environment)
            logger.info("配置变更监听启动成功")
        except Exception as e:
            logger.error(f"启动配置变更监听失败: {e}")
    
    def _on_config_change(self, change_data: Dict[str, Any]):
        """处理配置变更事件"""
        try:
            key_path = change_data.get('key_path')
            old_value = change_data.get('old_value')
            new_value = change_data.get('new_value')
            
            if key_path in self._watchers:
                for callback in self._watchers[key_path]:
                    try:
                        callback(old_value, new_value)
                    except Exception as e:
                        logger.error(f"配置变更回调执行失败: {e}")
            
            logger.info(f"配置变更处理完成: {key_path}")
            
        except Exception as e:
            logger.error(f"处理配置变更事件失败: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key_path: 配置键路径
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        try:
            # 先从缓存获取
            cache_data = self.redis_adapter.get_cache(key_path, self.environment)
            if cache_data:
                return cache_data.get('value', default)
            
            # 从数据库获取
            db_data = self.db_adapter.get_config(key_path, self.environment)
            if db_data:
                # 更新缓存
                self.redis_adapter.set_cache(
                    key_path, 
                    db_data['value'], 
                    db_data['value_type'], 
                    self.environment
                )
                return db_data['value']
            
            return default
            
        except Exception as e:
            logger.error(f"获取配置失败: {e}")
            return default
    
    def get_int(self, key_path: str, default: int = 0) -> int:
        """
        获取整数配置值
        
        Args:
            key_path: 配置键路径
            default: 默认值
            
        Returns:
            int: 配置值
        """
        value = self.get(key_path, default)
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            logger.warning(f"配置值不是有效的整数: {key_path} = {value}")
            return default
    
    def get_float(self, key_path: str, default: float = 0.0) -> float:
        """
        获取浮点数配置值
        
        Args:
            key_path: 配置键路径
            default: 默认值
            
        Returns:
            float: 配置值
        """
        value = self.get(key_path, default)
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            logger.warning(f"配置值不是有效的浮点数: {key_path} = {value}")
            return default
    
    def get_bool(self, key_path: str, default: bool = False) -> bool:
        """
        获取布尔值配置值
        
        Args:
            key_path: 配置键路径
            default: 默认值
            
        Returns:
            bool: 配置值
        """
        value = self.get(key_path, default)
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        elif isinstance(value, (int, float)):
            return bool(value)
        else:
            return default
    
    def get_json(self, key_path: str, default: Dict = None) -> Dict:
        """
        获取JSON配置值
        
        Args:
            key_path: 配置键路径
            default: 默认值
            
        Returns:
            Dict: 配置值
        """
        value = self.get(key_path, default)
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.warning(f"配置值不是有效的JSON: {key_path} = {value}")
                return default or {}
        else:
            return default or {}
    
    def set(self, key_path: str, value: Any, description: str = "", 
            is_encrypted: bool = False, is_sensitive: bool = False,
            user: str = "system") -> bool:
        """
        设置配置值
        
        Args:
            key_path: 配置键路径
            value: 配置值
            description: 描述
            is_encrypted: 是否加密
            is_sensitive: 是否敏感
            user: 操作用户
            
        Returns:
            bool: 操作结果
        """
        try:
            # 确定值类型
            if isinstance(value, dict):
                value_type = 'json'
            elif isinstance(value, int):
                value_type = 'int'
            elif isinstance(value, float):
                value_type = 'float'
            elif isinstance(value, bool):
                value_type = 'bool'
            else:
                value_type = 'string'
            
            # 获取旧值用于事件通知
            old_value = self.get(key_path)
            
            # 保存到数据库
            success = self.db_adapter.set_config(
                key_path, value, value_type, self.environment,
                description, is_encrypted, is_sensitive, user
            )
            
            if success:
                # 更新缓存
                self.redis_adapter.set_cache(key_path, value, value_type, self.environment)
                
                # 发布变更事件
                self.redis_adapter.publish_change(
                    key_path, old_value, value, self.environment, 'update'
                )
                
                logger.info(f"配置设置成功: {key_path}")
                return True
            else:
                logger.error(f"配置设置失败: {key_path}")
                return False
                
        except Exception as e:
            logger.error(f"设置配置失败: {e}")
            return False
    
    def delete(self, key_path: str, user: str = "system") -> bool:
        """
        删除配置
        
        Args:
            key_path: 配置键路径
            user: 操作用户
            
        Returns:
            bool: 操作结果
        """
        try:
            # 获取旧值用于事件通知
            old_value = self.get(key_path)
            
            # 从数据库删除
            success = self.db_adapter.delete_config(key_path, self.environment, user)
            
            if success:
                # 删除缓存
                self.redis_adapter.delete_cache(key_path, self.environment)
                
                # 发布变更事件
                self.redis_adapter.publish_change(
                    key_path, old_value, None, self.environment, 'delete'
                )
                
                logger.info(f"配置删除成功: {key_path}")
                return True
            else:
                logger.error(f"配置删除失败: {key_path}")
                return False
                
        except Exception as e:
            logger.error(f"删除配置失败: {e}")
            return False
    
    def update(self, updates: Dict[str, Any], user: str = "system") -> bool:
        """
        批量更新配置
        
        Args:
            updates: 更新字典
            user: 操作用户
            
        Returns:
            bool: 操作结果
        """
        try:
            success_count = 0
            total_count = len(updates)
            
            for key_path, value in updates.items():
                if self.set(key_path, value, user=user):
                    success_count += 1
            
            logger.info(f"批量更新配置完成: {success_count}/{total_count}")
            return success_count == total_count
            
        except Exception as e:
            logger.error(f"批量更新配置失败: {e}")
            return False
    
    def watch(self, key_path: str, callback: Callable[[Any, Any], None]) -> None:
        """
        监听配置变更
        
        Args:
            key_path: 配置键路径
            callback: 回调函数
        """
        if key_path not in self._watchers:
            self._watchers[key_path] = []
        
        self._watchers[key_path].append(callback)
        logger.info(f"配置监听注册成功: {key_path}")
    
    def unwatch(self, key_path: str, callback: Callable[[Any, Any], None]) -> None:
        """
        取消监听配置变更
        
        Args:
            key_path: 配置键路径
            callback: 回调函数
        """
        if key_path in self._watchers:
            if callback in self._watchers[key_path]:
                self._watchers[key_path].remove(callback)
                logger.info(f"配置监听取消成功: {key_path}")
    
    def get_version(self, key_path: str) -> int:
        """
        获取配置版本
        
        Args:
            key_path: 配置键路径
            
        Returns:
            int: 版本号
        """
        try:
            # 先从缓存获取
            cached_version = self.redis_adapter.get_version_cache(key_path, self.environment)
            if cached_version is not None:
                return cached_version
            
            # 从数据库获取
            db_data = self.db_adapter.get_config(key_path, self.environment)
            if db_data:
                version = db_data.get('version', 1)
                # 更新缓存
                self.redis_adapter.set_version_cache(key_path, version, self.environment)
                return version
            
            return 1
            
        except Exception as e:
            logger.error(f"获取配置版本失败: {e}")
            return 1
    
    def rollback(self, key_path: str, version: int, user: str = "system") -> bool:
        """
        回滚配置到指定版本
        
        Args:
            key_path: 配置键路径
            version: 目标版本
            user: 操作用户
            
        Returns:
            bool: 操作结果
        """
        try:
            success = self.db_adapter.rollback_config(key_path, version, self.environment, user)
            
            if success:
                # 清除缓存
                self.redis_adapter.delete_cache(key_path, self.environment)
                
                logger.info(f"配置回滚成功: {key_path} -> 版本 {version}")
                return True
            else:
                logger.error(f"配置回滚失败: {key_path}")
                return False
                
        except Exception as e:
            logger.error(f"回滚配置失败: {e}")
            return False
    
    def get_history(self, key_path: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取配置历史
        
        Args:
            key_path: 配置键路径
            limit: 限制数量
            
        Returns:
            List: 历史记录列表
        """
        try:
            return self.db_adapter.get_config_history(key_path, self.environment, limit)
        except Exception as e:
            logger.error(f"获取配置历史失败: {e}")
            return []
    
    def get_environment(self) -> str:
        """
        获取当前环境
        
        Returns:
            str: 环境标识
        """
        return self.environment
    
    def set_environment(self, env: str) -> None:
        """
        设置当前环境
        
        Args:
            env: 环境标识
        """
        self.environment = env
        logger.info(f"环境切换为: {env}")
    
    def validate_config(self) -> bool:
        """
        验证配置
        
        Returns:
            bool: 验证结果
        """
        try:
            # 验证数据库连接
            if not self.db_adapter.test_connection():
                logger.error("数据库连接验证失败")
                return False
            
            # 验证Redis连接
            if not self.redis_adapter.test_connection():
                logger.error("Redis连接验证失败")
                return False
            
            # 验证OSS连接
            if not self.oss_adapter.test_connection():
                logger.error("OSS连接验证失败")
                return False
            
            logger.info("配置验证成功")
            return True
            
        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            Dict: 健康状态
        """
        try:
            health = {
                "config_valid": True,
                "db_connected": self.db_adapter.test_connection(),
                "redis_connected": self.redis_adapter.test_connection(),
                "oss_connected": self.oss_adapter.test_connection(),
                "environment": self.environment,
                "watchers_count": len(self._watchers)
            }
            
            health["overall_healthy"] = all([
                health["config_valid"],
                health["db_connected"],
                health["redis_connected"],
                health["oss_connected"]
            ])
            
            return health
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {
                "config_valid": False,
                "db_connected": False,
                "redis_connected": False,
                "oss_connected": False,
                "environment": self.environment,
                "watchers_count": 0,
                "overall_healthy": False,
                "error": str(e)
            }
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取当前配置
        
        Returns:
            Dict: 配置信息
        """
        return self.config.dict()
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: list) -> bool:
        """
        验证必需字段
        
        Args:
            data: 数据字典
            required_fields: 必需字段列表
            
        Returns:
            bool: 验证结果
        """
        return validate_required_fields(data, required_fields)
    
    def backup_configs(self) -> bool:
        """
        备份所有配置
        
        Returns:
            bool: 操作结果
        """
        try:
            configs = self.db_adapter.get_all_configs(self.environment)
            success = self.oss_adapter.backup_configs(configs, self.environment)
            
            if success:
                logger.info(f"配置备份成功: {len(configs)} 个配置")
            else:
                logger.error("配置备份失败")
            
            return success
            
        except Exception as e:
            logger.error(f"备份配置失败: {e}")
            return False
    
    def restore_configs(self, date: str) -> bool:
        """
        恢复配置
        
        Args:
            date: 备份日期
            
        Returns:
            bool: 操作结果
        """
        try:
            configs = self.oss_adapter.restore_configs(date, self.environment)
            
            if configs:
                success_count = 0
                total_count = len(configs)
                
                for config in configs:
                    if self.set(config['key_path'], config['value'], 
                               description=f"从备份恢复: {date}", user="system"):
                        success_count += 1
                
                logger.info(f"配置恢复完成: {success_count}/{total_count}")
                return success_count == total_count
            else:
                logger.error("配置恢复失败: 未找到备份数据")
                return False
                
        except Exception as e:
            logger.error(f"恢复配置失败: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        列出备份文件
        
        Returns:
            List: 备份文件列表
        """
        try:
            return self.oss_adapter.list_backups(self.environment)
        except Exception as e:
            logger.error(f"列出备份文件失败: {e}")
            return []
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            return self.redis_adapter.get_cache_stats(self.environment)
        except Exception as e:
            logger.error(f"获取缓存统计信息失败: {e}")
            return {}
    
    def clear_cache(self) -> bool:
        """
        清除缓存
        
        Returns:
            bool: 操作结果
        """
        try:
            success = self.redis_adapter.clear_cache(self.environment)
            
            if success:
                logger.info("缓存清除成功")
            else:
                logger.error("缓存清除失败")
            
            return success
            
        except Exception as e:
            logger.error(f"清除缓存失败: {e}")
            return False
