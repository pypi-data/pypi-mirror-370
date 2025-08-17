"""
配置值验证器
"""

import re
from typing import Any, Dict, List, Optional, Union, Callable
from loguru import logger


class ValueValidator:
    """配置值验证器"""
    
    def __init__(self):
        """初始化值验证器"""
        self.custom_validators: Dict[str, Callable] = {}
        self.validation_rules: Dict[str, Dict[str, Any]] = {}
    
    def validate(self, value: Any, rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证配置值
        
        Args:
            value: 要验证的值
            rules: 验证规则
            
        Returns:
            Dict: 验证结果
        """
        try:
            errors = []
            
            # 检查是否为空
            if rules.get('required', False) and value is None:
                errors.append("值不能为空")
                return {"valid": False, "errors": errors}
            
            # 如果值为空且不是必需的，直接通过
            if value is None:
                return {"valid": True, "errors": []}
            
            # 执行各种验证规则
            if 'min_length' in rules:
                result = self._validate_min_length(value, rules['min_length'])
                if not result['valid']:
                    errors.append(result['error'])
            
            if 'max_length' in rules:
                result = self._validate_max_length(value, rules['max_length'])
                if not result['valid']:
                    errors.append(result['error'])
            
            if 'min_value' in rules:
                result = self._validate_min_value(value, rules['min_value'])
                if not result['valid']:
                    errors.append(result['error'])
            
            if 'max_value' in rules:
                result = self._validate_max_value(value, rules['max_value'])
                if not result['valid']:
                    errors.append(result['error'])
            
            if 'pattern' in rules:
                result = self._validate_pattern(value, rules['pattern'])
                if not result['valid']:
                    errors.append(result['error'])
            
            if 'enum' in rules:
                result = self._validate_enum(value, rules['enum'])
                if not result['valid']:
                    errors.append(result['error'])
            
            if 'custom' in rules:
                result = self._validate_custom(value, rules['custom'])
                if not result['valid']:
                    errors.append(result['error'])
            
            if 'format' in rules:
                result = self._validate_format(value, rules['format'])
                if not result['valid']:
                    errors.append(result['error'])
            
            if 'range' in rules:
                result = self._validate_range(value, rules['range'])
                if not result['valid']:
                    errors.append(result['error'])
            
            return {
                "valid": len(errors) == 0,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"值验证失败: {e}")
            return {
                "valid": False,
                "errors": [f"验证过程出错: {str(e)}"]
            }
    
    def _validate_min_length(self, value: Any, min_length: int) -> Dict[str, Any]:
        """验证最小长度"""
        if not hasattr(value, '__len__'):
            return {
                "valid": False,
                "error": "值没有长度属性"
            }
        
        if len(value) < min_length:
            return {
                "valid": False,
                "error": f"长度不能小于 {min_length}"
            }
        
        return {"valid": True}
    
    def _validate_max_length(self, value: Any, max_length: int) -> Dict[str, Any]:
        """验证最大长度"""
        if not hasattr(value, '__len__'):
            return {
                "valid": False,
                "error": "值没有长度属性"
            }
        
        if len(value) > max_length:
            return {
                "valid": False,
                "error": f"长度不能大于 {max_length}"
            }
        
        return {"valid": True}
    
    def _validate_min_value(self, value: Any, min_value: Union[int, float]) -> Dict[str, Any]:
        """验证最小值"""
        try:
            if isinstance(value, str):
                num_value = float(value)
            elif isinstance(value, (int, float)):
                num_value = float(value)
            else:
                return {
                    "valid": False,
                    "error": "值无法转换为数值"
                }
            
            if num_value < min_value:
                return {
                    "valid": False,
                    "error": f"值不能小于 {min_value}"
                }
            
            return {"valid": True}
            
        except (ValueError, TypeError):
            return {
                "valid": False,
                "error": "值无法转换为数值"
            }
    
    def _validate_max_value(self, value: Any, max_value: Union[int, float]) -> Dict[str, Any]:
        """验证最大值"""
        try:
            if isinstance(value, str):
                num_value = float(value)
            elif isinstance(value, (int, float)):
                num_value = float(value)
            else:
                return {
                    "valid": False,
                    "error": "值无法转换为数值"
                }
            
            if num_value > max_value:
                return {
                    "valid": False,
                    "error": f"值不能大于 {max_value}"
                }
            
            return {"valid": True}
            
        except (ValueError, TypeError):
            return {
                "valid": False,
                "error": "值无法转换为数值"
            }
    
    def _validate_pattern(self, value: Any, pattern: str) -> Dict[str, Any]:
        """验证正则表达式模式"""
        if not isinstance(value, str):
            return {
                "valid": False,
                "error": "模式验证只能用于字符串"
            }
        
        try:
            if not re.match(pattern, value):
                return {
                    "valid": False,
                    "error": f"值不匹配模式: {pattern}"
                }
            
            return {"valid": True}
            
        except re.error:
            return {
                "valid": False,
                "error": f"无效的正则表达式: {pattern}"
            }
    
    def _validate_enum(self, value: Any, enum_values: List[Any]) -> Dict[str, Any]:
        """验证枚举值"""
        if value not in enum_values:
            return {
                "valid": False,
                "error": f"值不在允许的枚举中: {enum_values}"
            }
        
        return {"valid": True}
    
    def _validate_custom(self, value: Any, validator_name: str) -> Dict[str, Any]:
        """验证自定义验证器"""
        if validator_name not in self.custom_validators:
            return {
                "valid": False,
                "error": f"自定义验证器未注册: {validator_name}"
            }
        
        try:
            validator_func = self.custom_validators[validator_name]
            result = validator_func(value)
            
            if isinstance(result, bool):
                return {
                    "valid": result,
                    "error": "自定义验证失败" if not result else None
                }
            elif isinstance(result, dict):
                return result
            else:
                return {
                    "valid": False,
                    "error": "自定义验证器返回格式错误"
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": f"自定义验证器执行失败: {str(e)}"
            }
    
    def _validate_format(self, value: Any, format_name: str) -> Dict[str, Any]:
        """验证格式"""
        if not isinstance(value, str):
            return {
                "valid": False,
                "error": "格式验证只能用于字符串"
            }
        
        format_validators = {
            'email': self._validate_email_format,
            'url': self._validate_url_format,
            'ip': self._validate_ip_format,
            'uuid': self._validate_uuid_format,
            'date': self._validate_date_format,
            'datetime': self._validate_datetime_format,
            'hostname': self._validate_hostname_format,
            'port': self._validate_port_format
        }
        
        if format_name not in format_validators:
            return {
                "valid": False,
                "error": f"不支持的格式: {format_name}"
            }
        
        validator_func = format_validators[format_name]
        return validator_func(value)
    
    def _validate_email_format(self, value: str) -> Dict[str, Any]:
        """验证邮箱格式"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, value):
            return {
                "valid": False,
                "error": f"无效的邮箱格式: {value}"
            }
        
        return {"valid": True}
    
    def _validate_url_format(self, value: str) -> Dict[str, Any]:
        """验证URL格式"""
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        
        if not re.match(url_pattern, value):
            return {
                "valid": False,
                "error": f"无效的URL格式: {value}"
            }
        
        return {"valid": True}
    
    def _validate_ip_format(self, value: str) -> Dict[str, Any]:
        """验证IP地址格式"""
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
    
    def _validate_uuid_format(self, value: str) -> Dict[str, Any]:
        """验证UUID格式"""
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        
        if not re.match(uuid_pattern, value.lower()):
            return {
                "valid": False,
                "error": f"无效的UUID格式: {value}"
            }
        
        return {"valid": True}
    
    def _validate_date_format(self, value: str) -> Dict[str, Any]:
        """验证日期格式"""
        try:
            from datetime import datetime
            datetime.strptime(value, '%Y-%m-%d')
            return {"valid": True}
        except ValueError:
            return {
                "valid": False,
                "error": f"无效的日期格式，期望YYYY-MM-DD: {value}"
            }
    
    def _validate_datetime_format(self, value: str) -> Dict[str, Any]:
        """验证日期时间格式"""
        try:
            from datetime import datetime
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
    
    def _validate_hostname_format(self, value: str) -> Dict[str, Any]:
        """验证主机名格式"""
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        
        if not re.match(hostname_pattern, value):
            return {
                "valid": False,
                "error": f"无效的主机名格式: {value}"
            }
        
        return {"valid": True}
    
    def _validate_port_format(self, value: str) -> Dict[str, Any]:
        """验证端口格式"""
        try:
            port = int(value)
            if not (1 <= port <= 65535):
                return {
                    "valid": False,
                    "error": f"端口号必须在1-65535范围内: {port}"
                }
            return {"valid": True}
        except ValueError:
            return {
                "valid": False,
                "error": f"无效的端口号: {value}"
            }
    
    def _validate_range(self, value: Any, range_spec: Dict[str, Any]) -> Dict[str, Any]:
        """验证范围"""
        try:
            if isinstance(value, str):
                num_value = float(value)
            elif isinstance(value, (int, float)):
                num_value = float(value)
            else:
                return {
                    "valid": False,
                    "error": "值无法转换为数值"
                }
            
            min_val = range_spec.get('min')
            max_val = range_spec.get('max')
            step = range_spec.get('step')
            
            if min_val is not None and num_value < min_val:
                return {
                    "valid": False,
                    "error": f"值不能小于 {min_val}"
                }
            
            if max_val is not None and num_value > max_val:
                return {
                    "valid": False,
                    "error": f"值不能大于 {max_val}"
                }
            
            if step is not None:
                remainder = (num_value - (min_val or 0)) % step
                if abs(remainder) > 1e-10:  # 浮点数精度处理
                    return {
                        "valid": False,
                        "error": f"值不符合步长 {step}"
                    }
            
            return {"valid": True}
            
        except (ValueError, TypeError):
            return {
                "valid": False,
                "error": "值无法转换为数值"
            }
    
    def register_custom_validator(self, name: str, validator_func: Callable) -> bool:
        """
        注册自定义验证器
        
        Args:
            name: 验证器名称
            validator_func: 验证函数
            
        Returns:
            bool: 注册结果
        """
        try:
            if not callable(validator_func):
                return False
            
            self.custom_validators[name] = validator_func
            logger.info(f"自定义验证器注册成功: {name}")
            return True
            
        except Exception as e:
            logger.error(f"注册自定义验证器失败: {e}")
            return False
    
    def register_validation_rule(self, rule_name: str, rule_definition: Dict[str, Any]) -> bool:
        """
        注册验证规则
        
        Args:
            rule_name: 规则名称
            rule_definition: 规则定义
            
        Returns:
            bool: 注册结果
        """
        try:
            self.validation_rules[rule_name] = rule_definition
            logger.info(f"验证规则注册成功: {rule_name}")
            return True
            
        except Exception as e:
            logger.error(f"注册验证规则失败: {e}")
            return False
    
    def validate_with_rule(self, value: Any, rule_name: str) -> Dict[str, Any]:
        """
        使用预定义规则验证值
        
        Args:
            value: 要验证的值
            rule_name: 规则名称
            
        Returns:
            Dict: 验证结果
        """
        if rule_name not in self.validation_rules:
            return {
                "valid": False,
                "errors": [f"验证规则未注册: {rule_name}"]
            }
        
        rules = self.validation_rules[rule_name]
        return self.validate(value, rules)
    
    def get_custom_validators(self) -> List[str]:
        """
        获取自定义验证器列表
        
        Returns:
            List: 验证器名称列表
        """
        return list(self.custom_validators.keys())
    
    def get_validation_rules(self) -> List[str]:
        """
        获取验证规则列表
        
        Returns:
            List: 规则名称列表
        """
        return list(self.validation_rules.keys())
