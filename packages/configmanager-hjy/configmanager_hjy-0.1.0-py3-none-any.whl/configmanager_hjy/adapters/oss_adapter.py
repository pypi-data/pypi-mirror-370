"""
OSS适配器 - 负责配置的备份和模板管理
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import oss2
from loguru import logger


class OSSAdapter:
    """OSS适配器类"""
    
    def __init__(self, config_dict: Dict[str, Any]):
        """
        初始化OSS适配器
        
        Args:
            config_dict: OSS配置字典
        """
        self.config = config_dict
        self.auth = None
        self.bucket = None
        self._init_client()
    
    def _init_client(self):
        """初始化OSS客户端"""
        try:
            self.auth = oss2.Auth(
                self.config['access_key_id'],
                self.config['access_key_secret']
            )
            
            self.bucket = oss2.Bucket(
                self.auth,
                self.config['endpoint'],
                self.config['bucket']
            )
            
            # 测试连接
            self.bucket.get_bucket_info()
            logger.info("OSS连接初始化成功")
            
        except Exception as e:
            logger.error(f"OSS连接初始化失败: {e}")
            raise
    
    def _get_backup_path(self, date: str, environment: str = "default") -> str:
        """生成备份路径"""
        return f"configs/backup/{date}/{environment}/configs.json"
    
    def _get_template_path(self, template_name: str) -> str:
        """生成模板路径"""
        return f"configs/templates/{template_name}.json"
    
    def backup_configs(self, configs: List[Dict[str, Any]], 
                      environment: str = "default") -> bool:
        """
        备份配置到OSS
        
        Args:
            configs: 配置列表
            environment: 环境标识
            
        Returns:
            bool: 操作结果
        """
        try:
            date = datetime.now().strftime("%Y-%m-%d")
            backup_path = self._get_backup_path(date, environment)
            
            # 准备备份数据
            backup_data = {
                "environment": environment,
                "backup_date": date,
                "backup_time": datetime.now().isoformat(),
                "config_count": len(configs),
                "configs": configs
            }
            
            # 上传到OSS
            json_data = json.dumps(backup_data, ensure_ascii=False, indent=2)
            self.bucket.put_object(backup_path, json_data.encode('utf-8'))
            
            logger.info(f"配置备份成功: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"配置备份失败: {e}")
            return False
    
    def restore_configs(self, date: str, environment: str = "default") -> Optional[List[Dict[str, Any]]]:
        """
        从OSS恢复配置
        
        Args:
            date: 备份日期
            environment: 环境标识
            
        Returns:
            List: 配置列表
        """
        try:
            backup_path = self._get_backup_path(date, environment)
            
            # 从OSS下载
            result = self.bucket.get_object(backup_path)
            backup_data = json.loads(result.read().decode('utf-8'))
            
            logger.info(f"配置恢复成功: {backup_path}")
            return backup_data.get('configs', [])
            
        except Exception as e:
            logger.error(f"配置恢复失败: {e}")
            return None
    
    def list_backups(self, environment: str = "default") -> List[Dict[str, Any]]:
        """
        列出备份文件
        
        Args:
            environment: 环境标识
            
        Returns:
            List: 备份文件列表
        """
        try:
            prefix = f"configs/backup/"
            backups = []
            
            for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
                if environment in obj.key:
                    # 解析路径获取日期
                    parts = obj.key.split('/')
                    if len(parts) >= 4:
                        date = parts[2]
                        backups.append({
                            "date": date,
                            "path": obj.key,
                            "size": obj.size,
                            "last_modified": obj.last_modified
                        })
            
            # 按日期排序
            backups.sort(key=lambda x: x['date'], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"列出备份文件失败: {e}")
            return []
    
    def save_template(self, template_name: str, template_data: Dict[str, Any]) -> bool:
        """
        保存配置模板
        
        Args:
            template_name: 模板名称
            template_data: 模板数据
            
        Returns:
            bool: 操作结果
        """
        try:
            template_path = self._get_template_path(template_name)
            
            # 准备模板数据
            template = {
                "name": template_name,
                "description": template_data.get("description", ""),
                "created_at": datetime.now().isoformat(),
                "data": template_data.get("data", {})
            }
            
            # 上传到OSS
            json_data = json.dumps(template, ensure_ascii=False, indent=2)
            self.bucket.put_object(template_path, json_data.encode('utf-8'))
            
            logger.info(f"配置模板保存成功: {template_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存配置模板失败: {e}")
            return False
    
    def load_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        加载配置模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            Dict: 模板数据
        """
        try:
            template_path = self._get_template_path(template_name)
            
            # 从OSS下载
            result = self.bucket.get_object(template_path)
            template = json.loads(result.read().decode('utf-8'))
            
            logger.info(f"配置模板加载成功: {template_path}")
            return template
            
        except Exception as e:
            logger.error(f"加载配置模板失败: {e}")
            return None
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        列出所有模板
        
        Returns:
            List: 模板列表
        """
        try:
            prefix = "configs/templates/"
            templates = []
            
            for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
                if obj.key.endswith('.json'):
                    template_name = os.path.basename(obj.key).replace('.json', '')
                    templates.append({
                        "name": template_name,
                        "path": obj.key,
                        "size": obj.size,
                        "last_modified": obj.last_modified
                    })
            
            return templates
            
        except Exception as e:
            logger.error(f"列出模板失败: {e}")
            return []
    
    def delete_template(self, template_name: str) -> bool:
        """
        删除配置模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            bool: 操作结果
        """
        try:
            template_path = self._get_template_path(template_name)
            
            # 检查文件是否存在
            if not self.bucket.object_exists(template_path):
                logger.warning(f"模板不存在: {template_path}")
                return False
            
            # 删除文件
            self.bucket.delete_object(template_path)
            
            logger.info(f"配置模板删除成功: {template_path}")
            return True
            
        except Exception as e:
            logger.error(f"删除配置模板失败: {e}")
            return False
    
    def export_configs(self, configs: List[Dict[str, Any]], 
                      filename: str, environment: str = "default") -> bool:
        """
        导出配置到OSS
        
        Args:
            configs: 配置列表
            filename: 文件名
            environment: 环境标识
            
        Returns:
            bool: 操作结果
        """
        try:
            export_path = f"configs/exports/{environment}/{filename}"
            
            # 准备导出数据
            export_data = {
                "environment": environment,
                "export_time": datetime.now().isoformat(),
                "config_count": len(configs),
                "configs": configs
            }
            
            # 上传到OSS
            json_data = json.dumps(export_data, ensure_ascii=False, indent=2)
            self.bucket.put_object(export_path, json_data.encode('utf-8'))
            
            logger.info(f"配置导出成功: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"配置导出失败: {e}")
            return False
    
    def import_configs(self, filename: str, environment: str = "default") -> Optional[List[Dict[str, Any]]]:
        """
        从OSS导入配置
        
        Args:
            filename: 文件名
            environment: 环境标识
            
        Returns:
            List: 配置列表
        """
        try:
            import_path = f"configs/exports/{environment}/{filename}"
            
            # 从OSS下载
            result = self.bucket.get_object(import_path)
            import_data = json.loads(result.read().decode('utf-8'))
            
            logger.info(f"配置导入成功: {import_path}")
            return import_data.get('configs', [])
            
        except Exception as e:
            logger.error(f"配置导入失败: {e}")
            return None
    
    def list_exports(self, environment: str = "default") -> List[Dict[str, Any]]:
        """
        列出导出文件
        
        Args:
            environment: 环境标识
            
        Returns:
            List: 导出文件列表
        """
        try:
            prefix = f"configs/exports/{environment}/"
            exports = []
            
            for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
                if obj.key.endswith('.json'):
                    filename = os.path.basename(obj.key)
                    exports.append({
                        "filename": filename,
                        "path": obj.key,
                        "size": obj.size,
                        "last_modified": obj.last_modified
                    })
            
            return exports
            
        except Exception as e:
            logger.error(f"列出导出文件失败: {e}")
            return []
    
    def test_connection(self) -> bool:
        """
        测试OSS连接
        
        Returns:
            bool: 连接状态
        """
        try:
            self.bucket.get_bucket_info()
            return True
        except Exception as e:
            logger.error(f"OSS连接测试失败: {e}")
            return False
