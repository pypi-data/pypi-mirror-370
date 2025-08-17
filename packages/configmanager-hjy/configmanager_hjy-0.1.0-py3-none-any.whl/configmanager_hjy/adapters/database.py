"""
数据库适配器 - 负责配置的数据库存储和管理
"""

import json
from typing import Dict, Any, List, Optional, Union
import mysql.connector
from mysql.connector import pooling
from loguru import logger


class DatabaseAdapter:
    """数据库适配器类"""
    
    def __init__(self, config_dict: Dict[str, Any]):
        """
        初始化数据库适配器
        
        Args:
            config_dict: 数据库配置字典
        """
        self.config = config_dict
        self.connection_pool = None
        self._init_connection_pool()
        self._create_tables()
    
    def _init_connection_pool(self):
        """初始化连接池"""
        try:
            # 将配置模型的字段名转换为MySQL连接器期望的字段名
            mysql_config = self.config.copy()
            if 'name' in mysql_config:
                mysql_config['database'] = mysql_config.pop('name')
            
            self.connection_pool = pooling.MySQLConnectionPool(
                pool_name="configmanager_pool",
                pool_size=5,
                **mysql_config
            )
            logger.info("数据库连接池初始化成功")
        except Exception as e:
            logger.error(f"数据库连接池初始化失败: {e}")
            raise
    
    def _get_connection(self):
        """获取数据库连接"""
        if self.connection_pool is None:
            raise RuntimeError("数据库连接池未初始化")
        return self.connection_pool.get_connection()
    
    def _create_tables(self):
        """创建配置表"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # 创建配置表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configurations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    key_path VARCHAR(255) NOT NULL UNIQUE,
                    value TEXT,
                    value_type ENUM('string', 'int', 'float', 'bool', 'json') NOT NULL,
                    environment VARCHAR(50) NOT NULL DEFAULT 'default',
                    description TEXT,
                    is_encrypted BOOLEAN DEFAULT FALSE,
                    is_sensitive BOOLEAN DEFAULT FALSE,
                    version INT DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    created_by VARCHAR(100),
                    updated_by VARCHAR(100),
                    INDEX idx_key_env (key_path, environment),
                    INDEX idx_environment (environment)
                )
            """)
            
            # 创建配置历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuration_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    config_id INT NOT NULL,
                    key_path VARCHAR(255) NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    change_type ENUM('create', 'update', 'delete') NOT NULL,
                    change_reason VARCHAR(500),
                    environment VARCHAR(50) NOT NULL,
                    version INT NOT NULL,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    changed_by VARCHAR(100),
                    INDEX idx_config_id (config_id),
                    INDEX idx_key_path (key_path),
                    INDEX idx_changed_at (changed_at)
                )
            """)
            
            # 创建配置模式表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuration_schemas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    schema_name VARCHAR(100) NOT NULL UNIQUE,
                    schema_definition JSON NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            connection.commit()
            cursor.close()
            connection.close()
            logger.info("配置表创建成功")
            
        except Exception as e:
            logger.error(f"创建配置表失败: {e}")
            raise
    
    def get_config(self, key_path: str, environment: str = "default") -> Optional[Dict[str, Any]]:
        """
        获取配置
        
        Args:
            key_path: 配置键路径
            environment: 环境标识
            
        Returns:
            Dict: 配置信息
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM configurations 
                WHERE key_path = %s AND environment = %s
            """, (key_path, environment))
            
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if result:
                # 解析值
                if result['value_type'] == 'json':
                    result['value'] = json.loads(result['value']) if result['value'] else None
                elif result['value_type'] == 'int':
                    result['value'] = int(result['value']) if result['value'] else None
                elif result['value_type'] == 'float':
                    result['value'] = float(result['value']) if result['value'] else None
                elif result['value_type'] == 'bool':
                    result['value'] = result['value'].lower() == 'true' if result['value'] else None
            
            return result
            
        except Exception as e:
            logger.error(f"获取配置失败: {e}")
            return None
    
    def set_config(self, key_path: str, value: Any, value_type: str = "string", 
                   environment: str = "default", description: str = "", 
                   is_encrypted: bool = False, is_sensitive: bool = False,
                   user: str = "system") -> bool:
        """
        设置配置
        
        Args:
            key_path: 配置键路径
            value: 配置值
            value_type: 值类型
            environment: 环境标识
            description: 描述
            is_encrypted: 是否加密
            is_sensitive: 是否敏感
            user: 操作用户
            
        Returns:
            bool: 操作结果
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # 序列化值
            if value_type == 'json':
                serialized_value = json.dumps(value) if value is not None else None
            else:
                serialized_value = str(value) if value is not None else None
            
            # 检查配置是否存在
            cursor.execute("""
                SELECT id, version FROM configurations 
                WHERE key_path = %s AND environment = %s
            """, (key_path, environment))
            
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有配置
                old_value = self.get_config(key_path, environment)
                old_value_str = old_value['value'] if old_value else None
                
                cursor.execute("""
                    UPDATE configurations 
                    SET value = %s, value_type = %s, description = %s, 
                        is_encrypted = %s, is_sensitive = %s, version = version + 1,
                        updated_at = CURRENT_TIMESTAMP, updated_by = %s
                    WHERE key_path = %s AND environment = %s
                """, (serialized_value, value_type, description, is_encrypted, 
                      is_sensitive, user, key_path, environment))
                
                # 记录历史
                cursor.execute("""
                    INSERT INTO configuration_history 
                    (config_id, key_path, old_value, new_value, change_type, 
                     change_reason, environment, version, changed_by)
                    VALUES (%s, %s, %s, %s, 'update', '配置更新', %s, %s, %s)
                """, (existing[0], key_path, old_value_str, serialized_value, 
                      environment, existing[1] + 1, user))
                
            else:
                # 创建新配置
                cursor.execute("""
                    INSERT INTO configurations 
                    (key_path, value, value_type, environment, description, 
                     is_encrypted, is_sensitive, created_by, updated_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (key_path, serialized_value, value_type, environment, 
                      description, is_encrypted, is_sensitive, user, user))
                
                config_id = cursor.lastrowid
                
                # 记录历史
                cursor.execute("""
                    INSERT INTO configuration_history 
                    (config_id, key_path, old_value, new_value, change_type, 
                     change_reason, environment, version, changed_by)
                    VALUES (%s, %s, %s, %s, 'create', '配置创建', %s, 1, %s)
                """, (config_id, key_path, None, serialized_value, environment, user))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            logger.info(f"配置设置成功: {key_path}")
            return True
            
        except Exception as e:
            logger.error(f"设置配置失败: {e}")
            return False
    
    def delete_config(self, key_path: str, environment: str = "default", 
                     user: str = "system") -> bool:
        """
        删除配置
        
        Args:
            key_path: 配置键路径
            environment: 环境标识
            user: 操作用户
            
        Returns:
            bool: 操作结果
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # 获取现有配置
            existing = self.get_config(key_path, environment)
            if not existing:
                logger.warning(f"配置不存在: {key_path}")
                return False
            
            # 删除配置
            cursor.execute("""
                DELETE FROM configurations 
                WHERE key_path = %s AND environment = %s
            """, (key_path, environment))
            
            # 记录历史
            cursor.execute("""
                INSERT INTO configuration_history 
                (config_id, key_path, old_value, new_value, change_type, 
                 change_reason, environment, version, changed_by)
                VALUES (%s, %s, %s, %s, 'delete', '配置删除', %s, %s, %s)
            """, (existing['id'], key_path, existing['value'], None, 
                  environment, existing['version'], user))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            logger.info(f"配置删除成功: {key_path}")
            return True
            
        except Exception as e:
            logger.error(f"删除配置失败: {e}")
            return False
    
    def get_config_history(self, key_path: str, environment: str = "default", 
                          limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取配置历史
        
        Args:
            key_path: 配置键路径
            environment: 环境标识
            limit: 限制数量
            
        Returns:
            List: 历史记录列表
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM configuration_history 
                WHERE key_path = %s AND environment = %s
                ORDER BY changed_at DESC
                LIMIT %s
            """, (key_path, environment, limit))
            
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            
            return results
            
        except Exception as e:
            logger.error(f"获取配置历史失败: {e}")
            return []
    
    def rollback_config(self, key_path: str, version: int, 
                       environment: str = "default", user: str = "system") -> bool:
        """
        回滚配置到指定版本
        
        Args:
            key_path: 配置键路径
            version: 目标版本
            environment: 环境标识
            user: 操作用户
            
        Returns:
            bool: 操作结果
        """
        try:
            # 获取目标版本的历史记录
            connection = self._get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM configuration_history 
                WHERE key_path = %s AND environment = %s AND version = %s
                ORDER BY changed_at DESC
                LIMIT 1
            """, (key_path, environment, version))
            
            history = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if not history:
                logger.error(f"未找到版本 {version} 的历史记录")
                return False
            
            # 回滚到该版本
            return self.set_config(
                key_path=key_path,
                value=history['new_value'],
                value_type='string',  # 简化处理
                environment=environment,
                description=f"回滚到版本 {version}",
                user=user
            )
            
        except Exception as e:
            logger.error(f"回滚配置失败: {e}")
            return False
    
    def get_all_configs(self, environment: str = "default") -> List[Dict[str, Any]]:
        """
        获取所有配置
        
        Args:
            environment: 环境标识
            
        Returns:
            List: 配置列表
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM configurations 
                WHERE environment = %s
                ORDER BY key_path
            """, (environment,))
            
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            
            # 解析值
            for result in results:
                if result['value_type'] == 'json':
                    result['value'] = json.loads(result['value']) if result['value'] else None
                elif result['value_type'] == 'int':
                    result['value'] = int(result['value']) if result['value'] else None
                elif result['value_type'] == 'float':
                    result['value'] = float(result['value']) if result['value'] else None
                elif result['value_type'] == 'bool':
                    result['value'] = result['value'].lower() == 'true' if result['value'] else None
            
            return results
            
        except Exception as e:
            logger.error(f"获取所有配置失败: {e}")
            return []
    
    def test_connection(self) -> bool:
        """
        测试数据库连接
        
        Returns:
            bool: 连接状态
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            return result[0] == 1
            
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
