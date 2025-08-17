"""
配置管理装饰器
"""

import functools
from typing import Callable, Any, Dict, Optional
from loguru import logger


# 全局配置管理器实例
_global_config_manager = None


def set_global_config_manager(config_manager):
    """设置全局配置管理器"""
    global _global_config_manager
    _global_config_manager = config_manager


def get_global_config_manager():
    """获取全局配置管理器"""
    return _global_config_manager


def config_watch(key_path: str):
    """
    配置监听装饰器
    
    Args:
        key_path: 配置键路径
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # 注册监听器
        if _global_config_manager:
            _global_config_manager.watch(key_path, func)
            logger.info(f"配置监听装饰器注册成功: {key_path} -> {func.__name__}")
        else:
            logger.warning(f"全局配置管理器未设置，无法注册监听器: {key_path}")
        
        return wrapper
    return decorator


def config_required(key_path: str, default: Any = None):
    """
    配置必需装饰器
    
    Args:
        key_path: 配置键路径
        default: 默认值
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 检查配置是否存在
            if _global_config_manager:
                config_value = _global_config_manager.get(key_path, default)
                if config_value is None:
                    raise ValueError(f"必需的配置项不存在: {key_path}")
                
                # 将配置值作为第一个参数传递给函数
                return func(config_value, *args, **kwargs)
            else:
                logger.warning(f"全局配置管理器未设置，使用默认值: {key_path}")
                return func(default, *args, **kwargs)
        
        return wrapper
    return decorator


def config_dependent(*key_paths: str):
    """
    配置依赖装饰器
    
    Args:
        *key_paths: 依赖的配置键路径
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if _global_config_manager:
                # 检查所有依赖的配置是否存在
                missing_configs = []
                config_values = {}
                
                for key_path in key_paths:
                    config_value = _global_config_manager.get(key_path)
                    if config_value is None:
                        missing_configs.append(key_path)
                    else:
                        config_values[key_path] = config_value
                
                if missing_configs:
                    raise ValueError(f"缺少必需的配置项: {', '.join(missing_configs)}")
                
                # 将配置值作为关键字参数传递给函数
                kwargs.update(config_values)
                return func(*args, **kwargs)
            else:
                logger.warning(f"全局配置管理器未设置，跳过配置依赖检查")
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def config_validator(validation_func: Callable[[Any], bool]):
    """
    配置验证装饰器
    
    Args:
        validation_func: 验证函数
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 执行验证
            if not validation_func(*args, **kwargs):
                raise ValueError(f"配置验证失败: {func.__name__}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def config_cache(ttl: int = 300):
    """
    配置缓存装饰器
    
    Args:
        ttl: 缓存时间（秒）
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if _global_config_manager:
                # 生成缓存键
                cache_key = f"func_cache:{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                # 尝试从缓存获取
                cached_result = _global_config_manager.redis_adapter.get_cache(
                    cache_key, _global_config_manager.environment
                )
                
                if cached_result:
                    logger.debug(f"从缓存获取函数结果: {func.__name__}")
                    return cached_result.get('value')
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 缓存结果
                _global_config_manager.redis_adapter.set_cache(
                    cache_key, result, 'json', _global_config_manager.environment, ttl
                )
                
                logger.debug(f"函数结果已缓存: {func.__name__}")
                return result
            else:
                logger.warning(f"全局配置管理器未设置，跳过缓存")
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def config_logger(log_level: str = "INFO"):
    """
    配置日志装饰器
    
    Args:
        log_level: 日志级别
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.log(log_level, f"开始执行函数: {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                logger.log(log_level, f"函数执行成功: {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"函数执行失败: {func.__name__} - {e}")
                raise
        
        return wrapper
    return decorator


def config_retry(max_retries: int = 3, delay: float = 1.0):
    """
    配置重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 重试延迟（秒）
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"函数执行失败，准备重试 ({attempt + 1}/{max_retries}): {func.__name__} - {e}")
                        import time
                        time.sleep(delay)
                    else:
                        logger.error(f"函数执行失败，已达到最大重试次数: {func.__name__} - {e}")
            
            raise last_exception
        
        return wrapper
    return decorator


def config_monitor(metric_name: str = None):
    """
    配置监控装饰器
    
    Args:
        metric_name: 指标名称
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # 记录成功指标
                metric = metric_name or f"{func.__name__}_success"
                logger.info(f"监控指标 - {metric}: 执行时间={execution_time:.3f}s")
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                
                # 记录失败指标
                metric = metric_name or f"{func.__name__}_failure"
                logger.error(f"监控指标 - {metric}: 执行时间={execution_time:.3f}s, 错误={e}")
                
                raise
        
        return wrapper
    return decorator
