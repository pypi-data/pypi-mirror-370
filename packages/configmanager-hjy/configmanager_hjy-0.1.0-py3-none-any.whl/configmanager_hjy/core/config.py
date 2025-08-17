"""
配置模型和初始化函数
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from loguru import logger


class DatabaseConfig(BaseModel):
    """数据库配置模型"""
    host: str = Field(..., description="数据库主机地址")
    port: int = Field(3306, description="数据库端口")
    name: str = Field(..., description="数据库名称")
    user: str = Field(..., description="数据库用户名")
    password: str = Field(..., description="数据库密码")
    charset: str = Field("utf8mb4", description="字符集")


class RedisConfig(BaseModel):
    """Redis配置模型"""
    host: str = Field(..., description="Redis主机地址")
    port: int = Field(6379, description="Redis端口")
    password: Optional[str] = Field(None, description="Redis密码")
    db: int = Field(0, description="Redis数据库编号")
    decode_responses: bool = Field(True, description="是否自动解码响应")


class OSSConfig(BaseModel):
    """OSS配置模型"""
    access_key_id: str = Field(..., description="访问密钥ID")
    access_key_secret: str = Field(..., description="访问密钥Secret")
    endpoint: str = Field(..., description="OSS端点")
    bucket: str = Field(..., description="存储桶名称")


class AIServiceConfig(BaseModel):
    """AI服务配置模型"""
    url: str = Field(..., description="AI服务URL")
    timeout: int = Field(30, description="超时时间（秒）")
    retry_count: int = Field(3, description="重试次数")
    retry_delay: int = Field(1, description="重试延迟（秒）")


class SystemConfig(BaseModel):
    """系统配置模型"""
    environment: str = Field("development", description="环境标识")
    debug: bool = Field(False, description="调试模式")
    log_level: str = Field("INFO", description="日志级别")


class AppConfig(BaseModel):
    """应用配置模型"""
    database: DatabaseConfig
    redis: RedisConfig
    oss: OSSConfig
    ai_service: AIServiceConfig
    system: SystemConfig = Field(default_factory=SystemConfig)


# 全局配置实例
_config: Optional[AppConfig] = None


def init(config_dict: Dict[str, Any]) -> AppConfig:
    """
    初始化配置
    
    Args:
        config_dict: 配置字典
        
    Returns:
        AppConfig: 配置实例
        
    Raises:
        ValueError: 配置验证失败
    """
    global _config
    
    try:
        _config = AppConfig(**config_dict)
        logger.info("配置初始化成功")
        return _config
    except Exception as e:
        logger.error(f"配置初始化失败: {e}")
        raise ValueError(f"配置初始化失败: {e}")


def get_config() -> AppConfig:
    """
    获取配置实例
    
    Returns:
        AppConfig: 配置实例
        
    Raises:
        RuntimeError: 配置未初始化
    """
    if _config is None:
        raise RuntimeError("配置未初始化，请先调用 init() 函数")
    return _config


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> bool:
    """
    验证必需字段
    
    Args:
        data: 数据字典
        required_fields: 必需字段列表
        
    Returns:
        bool: 验证结果
    """
    for field in required_fields:
        if field not in data or data[field] is None:
            logger.error(f"缺少必需字段: {field}")
            return False
    return True
