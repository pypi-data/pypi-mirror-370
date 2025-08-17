"""
配置适配器包
"""

from .database import DatabaseAdapter
from .redis_adapter import RedisAdapter
from .oss_adapter import OSSAdapter

__all__ = [
    "DatabaseAdapter",
    "RedisAdapter", 
    "OSSAdapter",
]
