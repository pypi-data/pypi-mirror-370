# configmanager_hjy

统一配置管理包 - 配置的云原生大脑

## 简介

`configmanager_hjy` 是一个高度通用、可复用的配置管理包，专门服务于其他 `_hjy` 包，提供统一的配置管理接口。

## 核心特性

- **统一配置入口** - 为所有 `_hjy` 包提供单一的配置管理接口
- **云原生配置存储** - 配置存储在云端，支持热更新和版本管理
- **高度可复用** - 设计为通用包，可在任何项目中复用
- **完美集成** - 与现有 `_hjy` 包无缝集成

## 安装

```bash
pip install configmanager-hjy==0.3.0
```

## 快速开始

```python
from configmanager_hjy import ConfigManager

# 初始化配置管理器
config_manager = ConfigManager()

# 获取数据库配置
db_config = config_manager.get('database.mysql')

# 获取Redis配置
redis_config = config_manager.get('cache.redis')

# 获取AI服务配置
ai_config = config_manager.get('services.ai_runner')
```

## 配置监听

```python
# 监听配置变更
@config_manager.watch('database.mysql')
def handle_db_config_change(old_value, new_value):
    logger.info("数据库配置已更新", new_config=new_value)
    # 重新初始化数据库连接
```

## 许可证

MIT License
