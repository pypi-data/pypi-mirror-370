"""
configmanager_hjy - 统一配置管理包

为所有 _hjy 包提供云原生配置管理服务，支持配置存储、缓存、监听和版本管理。
"""

from .core.manager import ConfigManager
from .core.config import init, get_config
from .core.decorators import config_watch, config_required

__version__ = "0.1.0"
__author__ = "hjy"
__email__ = "hjy@example.com"

__all__ = [
    "ConfigManager",
    "init",
    "get_config",
    "config_watch",
    "config_required",
]
