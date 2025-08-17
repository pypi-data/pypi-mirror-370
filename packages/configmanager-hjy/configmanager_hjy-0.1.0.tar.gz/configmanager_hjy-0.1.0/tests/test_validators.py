#!/usr/bin/env python3
"""
配置验证器单元测试
"""

import pytest
from configmanager_hjy.validators import SchemaValidator, TypeValidator, ValueValidator


class TestSchemaValidator:
    """SchemaValidator测试类"""
    
    @pytest.fixture
    def schema_validator(self):
        """SchemaValidator实例"""
        return SchemaValidator()
    
    def test_validate_simple_schema(self, schema_validator):
        """测试简单模式验证"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0}
            },
            "required": ["name"]
        }
        
        # 有效数据
        valid_data = {"name": "张三", "age": 25}
        result = schema_validator.validate(valid_data, schema)
        assert result.is_valid is True
        
        # 无效数据 - 缺少必需字段
        invalid_data = {"age": 25}
        result = schema_validator.validate(invalid_data, schema)
        assert result.is_valid is False
        assert "name" in str(result.errors)
    
    def test_validate_nested_schema(self, schema_validator):
        """测试嵌套模式验证"""
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string", "format": "email"}
                    },
                    "required": ["name", "email"]
                },
                "settings": {
                    "type": "object",
                    "properties": {
                        "theme": {"type": "string", "enum": ["light", "dark"]},
                        "language": {"type": "string"}
                    }
                }
            }
        }
        
        # 有效数据
        valid_data = {
            "user": {
                "name": "张三",
                "email": "zhangsan@example.com"
            },
            "settings": {
                "theme": "dark",
                "language": "zh-CN"
            }
        }
        result = schema_validator.validate(valid_data, schema)
        assert result.is_valid is True
        
        # 无效数据 - 无效邮箱格式
        invalid_data = {
            "user": {
                "name": "张三",
                "email": "invalid-email"
            }
        }
        result = schema_validator.validate(invalid_data, schema)
        assert result.is_valid is False
    
    def test_validate_array_schema(self, schema_validator):
        """测试数组模式验证"""
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"}
                },
                "required": ["id", "name"]
            },
            "minItems": 1,
            "maxItems": 10
        }
        
        # 有效数据
        valid_data = [
            {"id": 1, "name": "张三"},
            {"id": 2, "name": "李四"}
        ]
        result = schema_validator.validate(valid_data, schema)
        assert result.is_valid is True
        
        # 无效数据 - 空数组
        invalid_data = []
        result = schema_validator.validate(invalid_data, schema)
        assert result.is_valid is False
    
    def test_validate_with_custom_rules(self, schema_validator):
        """测试自定义规则验证"""
        schema = {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9_]{3,20}$"
                },
                "password": {
                    "type": "string",
                    "minLength": 8,
                    "maxLength": 50
                }
            }
        }
        
        # 有效数据
        valid_data = {
            "username": "user123",
            "password": "password123"
        }
        result = schema_validator.validate(valid_data, schema)
        assert result.is_valid is True
        
        # 无效数据 - 用户名格式错误
        invalid_data = {
            "username": "user@123",  # 包含特殊字符
            "password": "password123"
        }
        result = schema_validator.validate(invalid_data, schema)
        assert result.is_valid is False


class TestTypeValidator:
    """TypeValidator测试类"""
    
    @pytest.fixture
    def type_validator(self):
        """TypeValidator实例"""
        return TypeValidator()
    
    def test_validate_basic_types(self, type_validator):
        """测试基本类型验证"""
        # 字符串类型
        result = type_validator.validate("test", str)
        assert result.is_valid is True
        
        result = type_validator.validate(123, str)
        assert result.is_valid is False
        
        # 整数类型
        result = type_validator.validate(123, int)
        assert result.is_valid is True
        
        result = type_validator.validate("123", int)
        assert result.is_valid is False
        
        # 浮点数类型
        result = type_validator.validate(3.14, float)
        assert result.is_valid is True
        
        result = type_validator.validate("3.14", float)
        assert result.is_valid is False
        
        # 布尔类型
        result = type_validator.validate(True, bool)
        assert result.is_valid is True
        
        result = type_validator.validate("true", bool)
        assert result.is_valid is False
    
    def test_validate_complex_types(self, type_validator):
        """测试复杂类型验证"""
        # 列表类型
        result = type_validator.validate([1, 2, 3], list)
        assert result.is_valid is True
        
        result = type_validator.validate((1, 2, 3), list)
        assert result.is_valid is False
        
        # 字典类型
        result = type_validator.validate({"key": "value"}, dict)
        assert result.is_valid is True
        
        result = type_validator.validate([{"key": "value"}], dict)
        assert result.is_valid is False
    
    def test_type_conversion(self, type_validator):
        """测试类型转换"""
        # 字符串转整数
        result = type_validator.validate_and_convert("123", int)
        assert result.is_valid is True
        assert result.converted_value == 123
        
        # 字符串转浮点数
        result = type_validator.validate_and_convert("3.14", float)
        assert result.is_valid is True
        assert result.converted_value == 3.14
        
        # 无法转换的情况
        result = type_validator.validate_and_convert("not_a_number", int)
        assert result.is_valid is False
        assert result.converted_value is None
    
    def test_validate_with_constraints(self, type_validator):
        """测试带约束的类型验证"""
        # 字符串长度约束
        result = type_validator.validate("test", str, min_length=3, max_length=10)
        assert result.is_valid is True
        
        result = type_validator.validate("ab", str, min_length=3, max_length=10)
        assert result.is_valid is False
        
        # 数值范围约束
        result = type_validator.validate(5, int, min_value=0, max_value=10)
        assert result.is_valid is True
        
        result = type_validator.validate(15, int, min_value=0, max_value=10)
        assert result.is_valid is False
    
    def test_validate_custom_types(self, type_validator):
        """测试自定义类型验证"""
        # 定义自定义类型
        class User:
            def __init__(self, name, age):
                self.name = name
                self.age = age
        
        # 验证自定义类型
        user = User("张三", 25)
        result = type_validator.validate(user, User)
        assert result.is_valid is True
        
        result = type_validator.validate("not_a_user", User)
        assert result.is_valid is False


class TestValueValidator:
    """ValueValidator测试类"""
    
    @pytest.fixture
    def value_validator(self):
        """ValueValidator实例"""
        return ValueValidator()
    
    def test_validate_range(self, value_validator):
        """测试范围验证"""
        # 数值范围
        result = value_validator.validate_range(5, 0, 10)
        assert result.is_valid is True
        
        result = value_validator.validate_range(15, 0, 10)
        assert result.is_valid is False
        
        # 字符串长度范围
        result = value_validator.validate_range("test", 3, 10)
        assert result.is_valid is True
        
        result = value_validator.validate_range("ab", 3, 10)
        assert result.is_valid is False
    
    def test_validate_format(self, value_validator):
        """测试格式验证"""
        # 邮箱格式
        result = value_validator.validate_format("test@example.com", "email")
        assert result.is_valid is True
        
        result = value_validator.validate_format("invalid-email", "email")
        assert result.is_valid is False
        
        # URL格式
        result = value_validator.validate_format("https://example.com", "url")
        assert result.is_valid is True
        
        result = value_validator.validate_format("not-a-url", "url")
        assert result.is_valid is False
        
        # 日期格式
        result = value_validator.validate_format("2024-08-17", "date")
        assert result.is_valid is True
        
        result = value_validator.validate_format("invalid-date", "date")
        assert result.is_valid is False
    
    def test_validate_pattern(self, value_validator):
        """测试模式验证"""
        # 用户名模式
        pattern = r"^[a-zA-Z0-9_]{3,20}$"
        result = value_validator.validate_pattern("user123", pattern)
        assert result.is_valid is True
        
        result = value_validator.validate_pattern("user@123", pattern)
        assert result.is_valid is False
        
        # 手机号模式
        pattern = r"^1[3-9]\d{9}$"
        result = value_validator.validate_pattern("13812345678", pattern)
        assert result.is_valid is True
        
        result = value_validator.validate_pattern("12345678901", pattern)
        assert result.is_valid is False
    
    def test_validate_enum(self, value_validator):
        """测试枚举验证"""
        enum_values = ["red", "green", "blue"]
        
        result = value_validator.validate_enum("red", enum_values)
        assert result.is_valid is True
        
        result = value_validator.validate_enum("yellow", enum_values)
        assert result.is_valid is False
    
    def test_validate_condition(self, value_validator):
        """测试条件验证"""
        # 条件：如果age >= 18，则必须有身份证号
        data = {"age": 20, "id_card": "123456789012345678"}
        condition = lambda d: d.get("age", 0) >= 18 and "id_card" in d
        result = value_validator.validate_condition(data, condition)
        assert result.is_valid is True
        
        data = {"age": 20}  # 缺少身份证号
        result = value_validator.validate_condition(data, condition)
        assert result.is_valid is False
    
    def test_validate_business_rules(self, value_validator):
        """测试业务规则验证"""
        # 业务规则：密码必须包含字母和数字
        def password_rule(password):
            has_letter = any(c.isalpha() for c in password)
            has_digit = any(c.isdigit() for c in password)
            return has_letter and has_digit
        
        result = value_validator.validate_business_rule("password123", password_rule)
        assert result.is_valid is True
        
        result = value_validator.validate_business_rule("password", password_rule)
        assert result.is_valid is False
    
    def test_validate_complex_rules(self, value_validator):
        """测试复杂规则验证"""
        # 复杂规则：用户配置验证
        user_config = {
            "username": "user123",
            "email": "user@example.com",
            "age": 25,
            "settings": {
                "theme": "dark",
                "notifications": True
            }
        }
        
        rules = [
            lambda c: len(c.get("username", "")) >= 3,
            lambda c: "@" in c.get("email", ""),
            lambda c: 0 <= c.get("age", 0) <= 120,
            lambda c: c.get("settings", {}).get("theme") in ["light", "dark"]
        ]
        
        result = value_validator.validate_complex_rules(user_config, rules)
        assert result.is_valid is True
        
        # 无效配置
        invalid_config = {
            "username": "ab",  # 太短
            "email": "invalid-email",
            "age": 150,  # 超出范围
            "settings": {
                "theme": "invalid-theme"
            }
        }
        
        result = value_validator.validate_complex_rules(invalid_config, rules)
        assert result.is_valid is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
