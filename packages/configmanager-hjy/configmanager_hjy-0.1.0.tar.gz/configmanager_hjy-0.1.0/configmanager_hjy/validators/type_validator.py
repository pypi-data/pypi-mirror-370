"""
配置类型验证器
"""

import re
from typing import Any, Dict, List, Optional, Union
from loguru import logger


class TypeValidator:
    """配置类型验证器"""
    
    def __init__(self):
        """初始化类型验证器"""
        self.type_validators = {
            'string': self._validate_string,
            'integer': self._validate_integer,
            'float': self._validate_float,
            'boolean': self._validate_boolean,
            'email': self._validate_email,
            'url': self._validate_url,
            'ip': self._validate_ip,
            'json': self._validate_json,
            'list': self._validate_list,
            'dict': self._validate_dict,
            'file_path': self._validate_file_path,
            'port': self._validate_port,
            'hostname': self._validate_hostname,
            'uuid': self._validate_uuid,
            'date': self._validate_date,
            'datetime': self._validate_datetime
        }
    
    def validate(self, value: Any, expected_type: str, **kwargs) -> Dict[str, Any]:
        """
        验证值类型
        
        Args:
            value: 要验证的值
            expected_type: 期望类型
            **kwargs: 额外参数
            
        Returns:
            Dict: 验证结果
        """
        try:
            if expected_type not in self.type_validators:
                return {
                    "valid": False,
                    "error": f"不支持的类型: {expected_type}"
                }
            
            validator = self.type_validators[expected_type]
            return validator(value, **kwargs)
            
        except Exception as e:
            logger.error(f"类型验证失败: {e}")
            return {
                "valid": False,
                "error": f"验证过程出错: {str(e)}"
            }
    
    def _validate_string(self, value: Any, **kwargs) -> Dict[str, Any]:
        """验证字符串类型"""
        if not isinstance(value, str):
            return {
                "valid": False,
                "error": f"期望字符串类型，实际类型: {type(value).__name__}"
            }
        
        # 检查长度
        min_length = kwargs.get('min_length')
        max_length = kwargs.get('max_length')
        
        if min_length is not None and len(value) < min_length:
            return {
                "valid": False,
                "error": f"字符串长度不能小于 {min_length}"
            }
        
        if max_length is not None and len(value) > max_length:
            return {
                "valid": False,
                "error": f"字符串长度不能大于 {max_length}"
            }
        
        # 检查模式
        pattern = kwargs.get('pattern')
        if pattern:
            if not re.match(pattern, value):
                return {
                    "valid": False,
                    "error": f"字符串不匹配模式: {pattern}"
                }
        
        return {"valid": True}
    
    def _validate_integer(self, value: Any, **kwargs) -> Dict[str, Any]:
        """验证整数类型"""
        try:
            if isinstance(value, str):
                int_value = int(value)
            elif isinstance(value, (int, float)):
                int_value = int(value)
            else:
                return {
                    "valid": False,
                    "error": f"无法转换为整数: {value}"
                }
        except (ValueError, TypeError):
            return {
                "valid": False,
                "error": f"无法转换为整数: {value}"
            }
        
        # 检查范围
        min_value = kwargs.get('min_value')
        max_value = kwargs.get('max_value')
        
        if min_value is not None and int_value < min_value:
            return {
                "valid": False,
                "error": f"整数值不能小于 {min_value}"
            }
        
        if max_value is not None and int_value > max_value:
            return {
                "valid": False,
                "error": f"整数值不能大于 {max_value}"
            }
        
        return {"valid": True}
    
    def _validate_float(self, value: Any, **kwargs) -> Dict[str, Any]:
        """验证浮点数类型"""
        try:
            if isinstance(value, str):
                float_value = float(value)
            elif isinstance(value, (int, float)):
                float_value = float(value)
            else:
                return {
                    "valid": False,
                    "error": f"无法转换为浮点数: {value}"
                }
        except (ValueError, TypeError):
            return {
                "valid": False,
                "error": f"无法转换为浮点数: {value}"
            }
        
        # 检查范围
        min_value = kwargs.get('min_value')
        max_value = kwargs.get('max_value')
        
        if min_value is not None and float_value < min_value:
            return {
                "valid": False,
                "error": f"浮点数值不能小于 {min_value}"
            }
        
        if max_value is not None and float_value > max_value:
            return {
                "valid": False,
                "error": f"浮点数值不能大于 {max_value}"
            }
        
        return {"valid": True}
    
    def _validate_boolean(self, value: Any, **kwargs) -> Dict[str, Any]:
        """验证布尔类型"""
        if isinstance(value, bool):
            return {"valid": True}
        
        if isinstance(value, str):
            if value.lower() in ('true', '1', 'yes', 'on'):
                return {"valid": True}
            elif value.lower() in ('false', '0', 'no', 'off'):
                return {"valid": True}
        
        if isinstance(value, (int, float)):
            if value in (0, 1):
                return {"valid": True}
        
        return {
            "valid": False,
            "error": f"无法转换为布尔值: {value}"
        }
    
    def _validate_email(self, value: Any, **kwargs) -> Dict[str, Any]:
        """验证邮箱类型"""
        if not isinstance(value, str):
            return {
                "valid": False,
                "error": "邮箱必须是字符串类型"
            }
        
        # 简单的邮箱验证正则表达式
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, value):
            return {
                "valid": False,
                "error": f"无效的邮箱格式: {value}"
            }
        
        return {"valid": True}
    
    def _validate_url(self, value: Any, **kwargs) -> Dict[str, Any]:
        """验证URL类型"""
        if not isinstance(value, str):
            return {
                "valid": False,
                "error": "URL必须是字符串类型"
            }
        
        # 简单的URL验证正则表达式
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        
        if not re.match(url_pattern, value):
            return {
                "valid": False,
                "error": f"无效的URL格式: {value}"
            }
        
        return {"valid": True}
    
    def _validate_ip(self, value: Any, **kwargs) -> Dict[str, Any]:
        """验证IP地址类型"""
        if not isinstance(value, str):
            return {
                "valid": False,
                "error": "IP地址必须是字符串类型"
            }
        
        # IPv4验证
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ipv4_pattern, value):
            parts = value.split('.')
            for part in parts:
                if not (0 <= int(part) <= 255):
                    return {
                        "valid": False,
                        "error": f"无效的IPv4地址: {value}"
                    }
            return {"valid": True}
        
        # IPv6验证（简化版）
        ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        if re.match(ipv6_pattern, value):
            return {"valid": True}
        
        return {
            "valid": False,
            "error": f"无效的IP地址格式: {value}"
        }
    
    def _validate_json(self, value: Any, **kwargs) -> Dict[str, Any]:
        """验证JSON类型"""
        if isinstance(value, dict):
            return {"valid": True}
        
        if isinstance(value, str):
            try:
                import json
                json.loads(value)
                return {"valid": True}
            except json.JSONDecodeError:
                return {
                    "valid": False,
                    "error": f"无效的JSON格式: {value}"
                }
        
        return {
            "valid": False,
            "error": f"无法转换为JSON: {value}"
        }
    
    def _validate_list(self, value: Any, **kwargs) -> Dict[str, Any]:
        """验证列表类型"""
        if not isinstance(value, list):
            return {
                "valid": False,
                "error": f"期望列表类型，实际类型: {type(value).__name__}"
            }
        
        # 检查长度
        min_length = kwargs.get('min_length')
        max_length = kwargs.get('max_length')
        
        if min_length is not None and len(value) < min_length:
            return {
                "valid": False,
                "error": f"列表长度不能小于 {min_length}"
            }
        
        if max_length is not None and len(value) > max_length:
            return {
                "valid": False,
                "error": f"列表长度不能大于 {max_length}"
            }
        
        return {"valid": True}
    
    def _validate_dict(self, value: Any, **kwargs) -> Dict[str, Any]:
        """验证字典类型"""
        if not isinstance(value, dict):
            return {
                "valid": False,
                "error": f"期望字典类型，实际类型: {type(value).__name__}"
            }
        
        # 检查必需键
        required_keys = kwargs.get('required_keys', [])
        for key in required_keys:
            if key not in value:
                return {
                    "valid": False,
                    "error": f"缺少必需的键: {key}"
                }
        
        return {"valid": True}
    
    def _validate_file_path(self, value: Any, **kwargs) -> Dict[str, Any]:
        """验证文件路径类型"""
        if not isinstance(value, str):
            return {
                "valid": False,
                "error": "文件路径必须是字符串类型"
            }
        
        # 检查路径格式
        import os
        if os.path.isabs(value) or os.path.normpath(value) == value:
            return {"valid": True}
        
        return {
            "valid": False,
            "error": f"无效的文件路径格式: {value}"
        }
    
    def _validate_port(self, value: Any, **kwargs) -> Dict[str, Any]:
        """验证端口类型"""
        try:
            if isinstance(value, str):
                port = int(value)
            elif isinstance(value, (int, float)):
                port = int(value)
            else:
                return {
                    "valid": False,
                    "error": f"无法转换为端口号: {value}"
                }
        except (ValueError, TypeError):
            return {
                "valid": False,
                "error": f"无法转换为端口号: {value}"
            }
        
        if not (1 <= port <= 65535):
            return {
                "valid": False,
                "error": f"端口号必须在1-65535范围内: {port}"
            }
        
        return {"valid": True}
    
    def _validate_hostname(self, value: Any, **kwargs) -> Dict[str, Any]:
        """验证主机名类型"""
        if not isinstance(value, str):
            return {
                "valid": False,
                "error": "主机名必须是字符串类型"
            }
        
        # 主机名验证正则表达式
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        
        if not re.match(hostname_pattern, value):
            return {
                "valid": False,
                "error": f"无效的主机名格式: {value}"
            }
        
        return {"valid": True}
    
    def _validate_uuid(self, value: Any, **kwargs) -> Dict[str, Any]:
        """验证UUID类型"""
        if not isinstance(value, str):
            return {
                "valid": False,
                "error": "UUID必须是字符串类型"
            }
        
        # UUID验证正则表达式
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        
        if not re.match(uuid_pattern, value.lower()):
            return {
                "valid": False,
                "error": f"无效的UUID格式: {value}"
            }
        
        return {"valid": True}
    
    def _validate_date(self, value: Any, **kwargs) -> Dict[str, Any]:
        """验证日期类型"""
        if not isinstance(value, str):
            return {
                "valid": False,
                "error": "日期必须是字符串类型"
            }
        
        try:
            from datetime import datetime
            datetime.strptime(value, '%Y-%m-%d')
            return {"valid": True}
        except ValueError:
            return {
                "valid": False,
                "error": f"无效的日期格式，期望YYYY-MM-DD: {value}"
            }
    
    def _validate_datetime(self, value: Any, **kwargs) -> Dict[str, Any]:
        """验证日期时间类型"""
        if not isinstance(value, str):
            return {
                "valid": False,
                "error": "日期时间必须是字符串类型"
            }
        
        try:
            from datetime import datetime
            # 尝试多种格式
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%d %H:%M:%S.%f'
            ]
            
            for fmt in formats:
                try:
                    datetime.strptime(value, fmt)
                    return {"valid": True}
                except ValueError:
                    continue
            
            return {
                "valid": False,
                "error": f"无效的日期时间格式: {value}"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"日期时间验证失败: {str(e)}"
            }
    
    def register_custom_validator(self, type_name: str, validator_func: callable) -> bool:
        """
        注册自定义验证器
        
        Args:
            type_name: 类型名称
            validator_func: 验证函数
            
        Returns:
            bool: 注册结果
        """
        try:
            if not callable(validator_func):
                return False
            
            self.type_validators[type_name] = validator_func
            logger.info(f"自定义验证器注册成功: {type_name}")
            return True
            
        except Exception as e:
            logger.error(f"注册自定义验证器失败: {e}")
            return False
    
    def get_supported_types(self) -> List[str]:
        """
        获取支持的类型列表
        
        Returns:
            List: 支持的类型列表
        """
        return list(self.type_validators.keys())
