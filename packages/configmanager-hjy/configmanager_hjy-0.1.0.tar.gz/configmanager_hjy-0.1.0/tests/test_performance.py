#!/usr/bin/env python3
"""
性能测试
"""

import time
import pytest
import threading
from configmanager_hjy.cache import CacheManager, CacheStrategy
from configmanager_hjy.validators import SchemaValidator, TypeValidator, ValueValidator


class TestCachePerformance:
    """缓存性能测试类"""
    
    @pytest.fixture
    def cache_manager(self):
        """缓存管理器实例"""
        redis_config = {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'decode_responses': True
        }
        
        memory_config = {
            'max_size': 10000,
            'default_ttl': 300
        }
        
        return CacheManager(
            redis_config=redis_config,
            memory_config=memory_config,
            strategy=CacheStrategy.MEMORY_ONLY
        )
    
    def test_set_performance(self, cache_manager):
        """测试设置性能"""
        print("\n🧪 测试缓存设置性能...")
        
        # 测试单次设置性能
        start_time = time.time()
        cache_manager.set("test_key", "test_value")
        end_time = time.time()
        
        single_set_time = (end_time - start_time) * 1000  # 毫秒
        print(f"  单次设置耗时: {single_set_time:.3f}ms")
        
        # 测试批量设置性能
        batch_size = 1000
        start_time = time.time()
        
        for i in range(batch_size):
            cache_manager.set(f"key_{i}", f"value_{i}")
        
        end_time = time.time()
        batch_time = (end_time - start_time) * 1000
        ops_per_second = batch_size / (batch_time / 1000)
        
        print(f"  批量设置 {batch_size} 项耗时: {batch_time:.3f}ms")
        print(f"  设置性能: {ops_per_second:.0f} ops/s")
        
        # 性能要求：单次设置 < 1ms，批量设置 > 1000 ops/s
        assert single_set_time < 1.0, f"单次设置性能不达标: {single_set_time:.3f}ms"
        assert ops_per_second > 1000, f"批量设置性能不达标: {ops_per_second:.0f} ops/s"
    
    def test_get_performance(self, cache_manager):
        """测试获取性能"""
        print("\n🧪 测试缓存获取性能...")
        
        # 预先设置一些数据
        for i in range(1000):
            cache_manager.set(f"key_{i}", f"value_{i}")
        
        # 测试单次获取性能
        start_time = time.time()
        value = cache_manager.get("key_0")
        end_time = time.time()
        
        single_get_time = (end_time - start_time) * 1000
        print(f"  单次获取耗时: {single_get_time:.3f}ms")
        
        # 测试批量获取性能
        batch_size = 1000
        start_time = time.time()
        
        for i in range(batch_size):
            cache_manager.get(f"key_{i % 1000}")
        
        end_time = time.time()
        batch_time = (end_time - start_time) * 1000
        ops_per_second = batch_size / (batch_time / 1000)
        
        print(f"  批量获取 {batch_size} 项耗时: {batch_time:.3f}ms")
        print(f"  获取性能: {ops_per_second:.0f} ops/s")
        
        # 性能要求：单次获取 < 0.1ms，批量获取 > 10000 ops/s
        assert single_get_time < 0.1, f"单次获取性能不达标: {single_get_time:.3f}ms"
        assert ops_per_second > 10000, f"批量获取性能不达标: {ops_per_second:.0f} ops/s"
    
    def test_concurrent_performance(self, cache_manager):
        """测试并发性能"""
        print("\n🧪 测试并发性能...")
        
        def worker(thread_id, operations):
            """工作线程"""
            for i in range(operations):
                key = f"thread_{thread_id}_key_{i}"
                value = f"thread_{thread_id}_value_{i}"
                
                # 设置缓存
                cache_manager.set(key, value, ttl=10)
                
                # 获取缓存
                retrieved = cache_manager.get(key)
                
                # 验证数据一致性
                if retrieved != value:
                    raise ValueError(f"数据不一致: {retrieved} != {value}")
        
        # 并发测试参数
        num_threads = 10
        operations_per_thread = 100
        
        start_time = time.time()
        
        # 创建并启动线程
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(
                target=worker, 
                args=(i, operations_per_thread)
            )
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        total_time = (end_time - start_time) * 1000
        total_operations = num_threads * operations_per_thread * 2  # 设置 + 获取
        ops_per_second = total_operations / (total_time / 1000)
        
        print(f"  并发线程数: {num_threads}")
        print(f"  每线程操作数: {operations_per_thread}")
        print(f"  总操作数: {total_operations}")
        print(f"  总耗时: {total_time:.3f}ms")
        print(f"  并发性能: {ops_per_second:.0f} ops/s")
        
        # 性能要求：并发性能 > 5000 ops/s
        assert ops_per_second > 5000, f"并发性能不达标: {ops_per_second:.0f} ops/s"
    
    def test_memory_usage(self, cache_manager):
        """测试内存使用"""
        print("\n🧪 测试内存使用...")
        
        import psutil
        import os
        
        # 获取初始内存使用
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 添加大量数据
        for i in range(10000):
            cache_manager.set(f"large_key_{i}", f"large_value_{i}" * 100)  # 较大的值
        
        # 获取最终内存使用
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"  初始内存: {initial_memory:.2f}MB")
        print(f"  最终内存: {final_memory:.2f}MB")
        print(f"  内存增长: {memory_increase:.2f}MB")
        
        # 获取缓存统计
        stats = cache_manager.get_stats()
        cache_size = stats['memory_cache_stats']['total_size_bytes'] / 1024 / 1024  # MB
        
        print(f"  缓存数据大小: {cache_size:.2f}MB")
        print(f"  内存效率: {cache_size/memory_increase*100:.1f}%" if memory_increase > 0 else "内存效率: N/A")
        
        # 性能要求：内存增长 < 100MB
        assert memory_increase < 100, f"内存使用过高: {memory_increase:.2f}MB"


class TestValidatorPerformance:
    """验证器性能测试类"""
    
    @pytest.fixture
    def schema_validator(self):
        """SchemaValidator实例"""
        return SchemaValidator()
    
    @pytest.fixture
    def type_validator(self):
        """TypeValidator实例"""
        return TypeValidator()
    
    @pytest.fixture
    def value_validator(self):
        """ValueValidator实例"""
        return ValueValidator()
    
    def test_schema_validation_performance(self, schema_validator):
        """测试模式验证性能"""
        print("\n🧪 测试模式验证性能...")
        
        # 复杂模式
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string", "minLength": 1},
                        "email": {"type": "string", "format": "email"},
                        "age": {"type": "integer", "minimum": 0, "maximum": 150}
                    },
                    "required": ["id", "name", "email"]
                },
                "settings": {
                    "type": "object",
                    "properties": {
                        "theme": {"type": "string", "enum": ["light", "dark"]},
                        "language": {"type": "string"},
                        "notifications": {"type": "boolean"}
                    }
                }
            }
        }
        
        # 有效数据
        valid_data = {
            "user": {
                "id": 1,
                "name": "张三",
                "email": "zhangsan@example.com",
                "age": 25
            },
            "settings": {
                "theme": "dark",
                "language": "zh-CN",
                "notifications": True
            }
        }
        
        # 测试单次验证性能
        start_time = time.time()
        result = schema_validator.validate(valid_data, schema)
        end_time = time.time()
        
        single_validation_time = (end_time - start_time) * 1000
        print(f"  单次验证耗时: {single_validation_time:.3f}ms")
        assert result.is_valid is True
        
        # 测试批量验证性能
        batch_size = 1000
        start_time = time.time()
        
        for i in range(batch_size):
            data = valid_data.copy()
            data["user"]["id"] = i
            result = schema_validator.validate(data, schema)
            assert result.is_valid is True
        
        end_time = time.time()
        batch_time = (end_time - start_time) * 1000
        ops_per_second = batch_size / (batch_time / 1000)
        
        print(f"  批量验证 {batch_size} 项耗时: {batch_time:.3f}ms")
        print(f"  验证性能: {ops_per_second:.0f} ops/s")
        
        # 性能要求：单次验证 < 10ms，批量验证 > 100 ops/s
        assert single_validation_time < 10, f"单次验证性能不达标: {single_validation_time:.3f}ms"
        assert ops_per_second > 100, f"批量验证性能不达标: {ops_per_second:.0f} ops/s"
    
    def test_type_validation_performance(self, type_validator):
        """测试类型验证性能"""
        print("\n🧪 测试类型验证性能...")
        
        # 测试基本类型验证性能
        test_cases = [
            ("test_string", str),
            (123, int),
            (3.14, float),
            (True, bool),
            ([1, 2, 3], list),
            ({"key": "value"}, dict)
        ]
        
        batch_size = 1000
        start_time = time.time()
        
        for i in range(batch_size):
            for value, expected_type in test_cases:
                result = type_validator.validate(value, expected_type)
                assert result.is_valid is True
        
        end_time = time.time()
        batch_time = (end_time - start_time) * 1000
        total_operations = batch_size * len(test_cases)
        ops_per_second = total_operations / (batch_time / 1000)
        
        print(f"  批量类型验证 {total_operations} 项耗时: {batch_time:.3f}ms")
        print(f"  类型验证性能: {ops_per_second:.0f} ops/s")
        
        # 性能要求：类型验证 > 1000 ops/s
        assert ops_per_second > 1000, f"类型验证性能不达标: {ops_per_second:.0f} ops/s"
    
    def test_value_validation_performance(self, value_validator):
        """测试值验证性能"""
        print("\n🧪 测试值验证性能...")
        
        # 测试范围验证性能
        batch_size = 1000
        start_time = time.time()
        
        for i in range(batch_size):
            # 数值范围验证
            result = value_validator.validate_range(i, 0, batch_size)
            assert result.is_valid is True
            
            # 字符串长度验证
            test_string = "test" * (i % 10 + 1)
            result = value_validator.validate_range(test_string, 1, 50)
            assert result.is_valid is True
        
        end_time = time.time()
        batch_time = (end_time - start_time) * 1000
        total_operations = batch_size * 2  # 数值 + 字符串验证
        ops_per_second = total_operations / (batch_time / 1000)
        
        print(f"  批量值验证 {total_operations} 项耗时: {batch_time:.3f}ms")
        print(f"  值验证性能: {ops_per_second:.0f} ops/s")
        
        # 性能要求：值验证 > 2000 ops/s
        assert ops_per_second > 2000, f"值验证性能不达标: {ops_per_second:.0f} ops/s"


class TestIntegrationPerformance:
    """集成性能测试类"""
    
    def test_end_to_end_performance(self):
        """测试端到端性能"""
        print("\n🧪 测试端到端性能...")
        
        # 创建缓存管理器
        redis_config = {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'decode_responses': True
        }
        
        memory_config = {
            'max_size': 1000,
            'default_ttl': 300
        }
        
        cache = CacheManager(
            redis_config=redis_config,
            memory_config=memory_config,
            strategy=CacheStrategy.MEMORY_ONLY
        )
        
        # 创建验证器
        schema_validator = SchemaValidator()
        type_validator = TypeValidator()
        value_validator = ValueValidator()
        
        # 定义验证模式
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string", "minLength": 1},
                "email": {"type": "string", "format": "email"},
                "age": {"type": "integer", "minimum": 0, "maximum": 150}
            },
            "required": ["id", "name", "email"]
        }
        
        # 端到端测试
        batch_size = 100
        start_time = time.time()
        
        for i in range(batch_size):
            # 1. 创建数据
            data = {
                "id": i,
                "name": f"User_{i}",
                "email": f"user{i}@example.com",
                "age": 20 + (i % 50)
            }
            
            # 2. 验证数据
            schema_result = schema_validator.validate(data, schema)
            assert schema_result.is_valid is True
            
            type_result = type_validator.validate(data["id"], int)
            assert type_result.is_valid is True
            
            value_result = value_validator.validate_range(data["age"], 0, 150)
            assert value_result.is_valid is True
            
            # 3. 缓存数据
            cache.set(f"user_{i}", data, ttl=300)
            
            # 4. 获取并验证缓存数据
            cached_data = cache.get(f"user_{i}")
            assert cached_data == data
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        total_operations = batch_size * 6  # 验证 + 缓存 + 获取
        ops_per_second = total_operations / (total_time / 1000)
        
        print(f"  端到端测试 {batch_size} 项耗时: {total_time:.3f}ms")
        print(f"  总操作数: {total_operations}")
        print(f"  端到端性能: {ops_per_second:.0f} ops/s")
        
        # 性能要求：端到端性能 > 500 ops/s
        assert ops_per_second > 500, f"端到端性能不达标: {ops_per_second:.0f} ops/s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
