"""
配置模式验证器
"""

import json
from typing import Dict, Any, List, Optional, Union
from loguru import logger


class SchemaValidator:
    """配置模式验证器"""
    
    def __init__(self):
        """初始化模式验证器"""
        self.schemas: Dict[str, Dict[str, Any]] = {}
    
    def register_schema(self, schema_name: str, schema_definition: Dict[str, Any]) -> bool:
        """
        注册配置模式
        
        Args:
            schema_name: 模式名称
            schema_definition: 模式定义
            
        Returns:
            bool: 注册结果
        """
        try:
            # 验证模式定义
            if not self._validate_schema_definition(schema_definition):
                logger.error(f"模式定义无效: {schema_name}")
                return False
            
            self.schemas[schema_name] = schema_definition
            logger.info(f"模式注册成功: {schema_name}")
            return True
            
        except Exception as e:
            logger.error(f"注册模式失败: {e}")
            return False
    
    def _validate_schema_definition(self, schema: Dict[str, Any]) -> bool:
        """
        验证模式定义
        
        Args:
            schema: 模式定义
            
        Returns:
            bool: 验证结果
        """
        try:
            required_fields = ['type', 'properties']
            
            # 检查必需字段
            for field in required_fields:
                if field not in schema:
                    logger.error(f"模式定义缺少必需字段: {field}")
                    return False
            
            # 检查类型
            if schema['type'] not in ['object', 'array', 'string', 'number', 'integer', 'boolean']:
                logger.error(f"无效的模式类型: {schema['type']}")
                return False
            
            # 检查属性定义
            if schema['type'] == 'object' and 'properties' in schema:
                for prop_name, prop_def in schema['properties'].items():
                    if not self._validate_property_definition(prop_def):
                        logger.error(f"属性定义无效: {prop_name}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"验证模式定义失败: {e}")
            return False
    
    def _validate_property_definition(self, prop_def: Dict[str, Any]) -> bool:
        """
        验证属性定义
        
        Args:
            prop_def: 属性定义
            
        Returns:
            bool: 验证结果
        """
        try:
            if 'type' not in prop_def:
                logger.error("属性定义缺少type字段")
                return False
            
            prop_type = prop_def['type']
            if prop_type not in ['string', 'number', 'integer', 'boolean', 'object', 'array']:
                logger.error(f"无效的属性类型: {prop_type}")
                return False
            
            # 检查字符串类型的约束
            if prop_type == 'string':
                if 'minLength' in prop_def and prop_def['minLength'] < 0:
                    logger.error("minLength不能为负数")
                    return False
                if 'maxLength' in prop_def and prop_def['maxLength'] < 0:
                    logger.error("maxLength不能为负数")
                    return False
                if 'pattern' in prop_def:
                    try:
                        import re
                        re.compile(prop_def['pattern'])
                    except re.error:
                        logger.error(f"无效的正则表达式: {prop_def['pattern']}")
                        return False
            
            # 检查数值类型的约束
            elif prop_type in ['number', 'integer']:
                if 'minimum' in prop_def and 'maximum' in prop_def:
                    if prop_def['minimum'] > prop_def['maximum']:
                        logger.error("minimum不能大于maximum")
                        return False
            
            # 检查数组类型的约束
            elif prop_type == 'array':
                if 'items' not in prop_def:
                    logger.error("数组类型缺少items定义")
                    return False
                if not self._validate_property_definition(prop_def['items']):
                    return False
                if 'minItems' in prop_def and prop_def['minItems'] < 0:
                    logger.error("minItems不能为负数")
                    return False
                if 'maxItems' in prop_def and prop_def['maxItems'] < 0:
                    logger.error("maxItems不能为负数")
                    return False
            
            # 检查对象类型的约束
            elif prop_type == 'object':
                if 'properties' in prop_def:
                    for prop_name, nested_prop_def in prop_def['properties'].items():
                        if not self._validate_property_definition(nested_prop_def):
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"验证属性定义失败: {e}")
            return False
    
    def validate_config(self, schema_name: str, config_data: Any) -> Dict[str, Any]:
        """
        验证配置数据
        
        Args:
            schema_name: 模式名称
            config_data: 配置数据
            
        Returns:
            Dict: 验证结果
        """
        try:
            if schema_name not in self.schemas:
                return {
                    "valid": False,
                    "errors": [f"模式未注册: {schema_name}"]
                }
            
            schema = self.schemas[schema_name]
            errors = []
            
            # 执行验证
            self._validate_value(config_data, schema, "", errors)
            
            return {
                "valid": len(errors) == 0,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"验证配置失败: {e}")
            return {
                "valid": False,
                "errors": [f"验证过程出错: {str(e)}"]
            }
    
    def _validate_value(self, value: Any, schema: Dict[str, Any], path: str, errors: List[str]):
        """
        验证值
        
        Args:
            value: 要验证的值
            schema: 模式定义
            path: 当前路径
            errors: 错误列表
        """
        try:
            schema_type = schema.get('type')
            
            # 检查必需字段
            if schema.get('required', False) and value is None:
                errors.append(f"{path}: 字段是必需的")
                return
            
            # 检查类型
            if not self._check_type(value, schema_type):
                errors.append(f"{path}: 类型不匹配，期望 {schema_type}，实际 {type(value).__name__}")
                return
            
            # 根据类型进行具体验证
            if schema_type == 'string':
                self._validate_string(value, schema, path, errors)
            elif schema_type in ['number', 'integer']:
                self._validate_number(value, schema, path, errors)
            elif schema_type == 'boolean':
                self._validate_boolean(value, schema, path, errors)
            elif schema_type == 'array':
                self._validate_array(value, schema, path, errors)
            elif schema_type == 'object':
                self._validate_object(value, schema, path, errors)
                
        except Exception as e:
            errors.append(f"{path}: 验证过程出错: {str(e)}")
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """
        检查类型匹配
        
        Args:
            value: 值
            expected_type: 期望类型
            
        Returns:
            bool: 类型是否匹配
        """
        if value is None:
            return True
        
        type_mapping = {
            'string': str,
            'number': (int, float),
            'integer': int,
            'boolean': bool,
            'array': list,
            'object': dict
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type is None:
            return False
        
        if isinstance(expected_python_type, tuple):
            return isinstance(value, expected_python_type)
        else:
            return isinstance(value, expected_python_type)
    
    def _validate_string(self, value: str, schema: Dict[str, Any], path: str, errors: List[str]):
        """验证字符串"""
        if value is None:
            return
        
        # 检查长度
        if 'minLength' in schema and len(value) < schema['minLength']:
            errors.append(f"{path}: 字符串长度不能小于 {schema['minLength']}")
        
        if 'maxLength' in schema and len(value) > schema['maxLength']:
            errors.append(f"{path}: 字符串长度不能大于 {schema['maxLength']}")
        
        # 检查模式
        if 'pattern' in schema:
            import re
            if not re.match(schema['pattern'], value):
                errors.append(f"{path}: 字符串不匹配模式 {schema['pattern']}")
        
        # 检查枚举值
        if 'enum' in schema and value not in schema['enum']:
            errors.append(f"{path}: 值不在允许的枚举中: {schema['enum']}")
    
    def _validate_number(self, value: Union[int, float], schema: Dict[str, Any], path: str, errors: List[str]):
        """验证数值"""
        if value is None:
            return
        
        # 检查范围
        if 'minimum' in schema and value < schema['minimum']:
            errors.append(f"{path}: 值不能小于 {schema['minimum']}")
        
        if 'maximum' in schema and value > schema['maximum']:
            errors.append(f"{path}: 值不能大于 {schema['maximum']}")
        
        # 检查枚举值
        if 'enum' in schema and value not in schema['enum']:
            errors.append(f"{path}: 值不在允许的枚举中: {schema['enum']}")
    
    def _validate_boolean(self, value: bool, schema: Dict[str, Any], path: str, errors: List[str]):
        """验证布尔值"""
        if value is None:
            return
        
        # 检查枚举值
        if 'enum' in schema and value not in schema['enum']:
            errors.append(f"{path}: 值不在允许的枚举中: {schema['enum']}")
    
    def _validate_array(self, value: list, schema: Dict[str, Any], path: str, errors: List[str]):
        """验证数组"""
        if value is None:
            return
        
        # 检查长度
        if 'minItems' in schema and len(value) < schema['minItems']:
            errors.append(f"{path}: 数组长度不能小于 {schema['minItems']}")
        
        if 'maxItems' in schema and len(value) > schema['maxItems']:
            errors.append(f"{path}: 数组长度不能大于 {schema['maxItems']}")
        
        # 验证数组元素
        if 'items' in schema:
            for i, item in enumerate(value):
                item_path = f"{path}[{i}]"
                self._validate_value(item, schema['items'], item_path, errors)
    
    def _validate_object(self, value: dict, schema: Dict[str, Any], path: str, errors: List[str]):
        """验证对象"""
        if value is None:
            return
        
        # 检查必需属性
        required_props = schema.get('required', [])
        for prop in required_props:
            if prop not in value:
                errors.append(f"{path}.{prop}: 必需属性缺失")
        
        # 验证属性
        if 'properties' in schema:
            for prop_name, prop_value in value.items():
                if prop_name in schema['properties']:
                    prop_path = f"{path}.{prop_name}"
                    self._validate_value(prop_value, schema['properties'][prop_name], prop_path, errors)
                elif not schema.get('additionalProperties', True):
                    errors.append(f"{path}.{prop_name}: 不允许的额外属性")
    
    def get_schema(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """
        获取模式定义
        
        Args:
            schema_name: 模式名称
            
        Returns:
            Dict: 模式定义
        """
        return self.schemas.get(schema_name)
    
    def list_schemas(self) -> List[str]:
        """
        列出所有模式
        
        Returns:
            List: 模式名称列表
        """
        return list(self.schemas.keys())
    
    def remove_schema(self, schema_name: str) -> bool:
        """
        移除模式
        
        Args:
            schema_name: 模式名称
            
        Returns:
            bool: 操作结果
        """
        try:
            if schema_name in self.schemas:
                del self.schemas[schema_name]
                logger.info(f"模式移除成功: {schema_name}")
                return True
            else:
                logger.warning(f"模式不存在: {schema_name}")
                return False
                
        except Exception as e:
            logger.error(f"移除模式失败: {e}")
            return False
