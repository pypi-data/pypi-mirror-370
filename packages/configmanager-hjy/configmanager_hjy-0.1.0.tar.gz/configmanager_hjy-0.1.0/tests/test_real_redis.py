#!/usr/bin/env python3
"""
真实Redis环境测试
"""

import os
import pytest
from configmanager_hjy.cache import CacheManager, CacheStrategy


class TestRealRedis:
    """真实Redis环境测试"""
    
    @pytest.fixture
    def real_redis_config(self):
        """真实Redis配置"""
        return {
            'host': 'r-bp1idjfe6bu4sbbf81pd.redis.rds.aliyuncs.com',
            'port': 6379,
            'username': 'r-bp1idjfe6bu4sbbf81',
            'password': 'N9$v#8qP@Xz!7Lm&3rG^Fw*Yk2T#bJs6',
            'db': 0,
            'decode_responses': True,
            'socket_connect_timeout': 10,
            'socket_timeout': 10
        }
    
    @pytest.fixture
    def memory_config(self):
        """内存缓存配置"""
        return {
            'max_size': 1000,
            'default_ttl': 300
        }
    
    def test_real_redis_connection(self, real_redis_config, memory_config):
        """测试真实Redis连接"""
        cache_manager = CacheManager(
            redis_config=real_redis_config,
            memory_config=memory_config,
            strategy=CacheStrategy.REDIS_FIRST
        )
        
        # 测试基本操作
        cache_manager.set("real_test_key", "real_test_value", ttl=60)
        value = cache_manager.get("real_test_key")
        assert value == "real_test_value"
        
        # 测试TTL
        ttl = cache_manager.get_ttl("real_test_key")
        assert ttl > 0
        
        # 测试存在性
        assert cache_manager.exists("real_test_key") is True
        
        # 测试健康检查
        health = cache_manager.health_check()
        assert health['redis']['status'] == 'healthy'
        assert health['memory']['status'] == 'healthy'
        
        # 清理
        cache_manager.delete("real_test_key")
        assert cache_manager.exists("real_test_key") is False
    
    def test_real_redis_strategies(self, real_redis_config, memory_config):
        """测试真实Redis的不同策略"""
        strategies = [
            CacheStrategy.MEMORY_ONLY,
            CacheStrategy.REDIS_ONLY,
            CacheStrategy.MEMORY_FIRST,
            CacheStrategy.REDIS_FIRST,
            CacheStrategy.LAYERED
        ]
        
        for strategy in strategies:
            cache_manager = CacheManager(
                redis_config=real_redis_config,
                memory_config=memory_config,
                strategy=strategy
            )
            
            # 基本功能测试
            key = f"strategy_test_{strategy.value}"
            cache_manager.set(key, f"value_{strategy.value}", ttl=30)
            value = cache_manager.get(key)
            assert value == f"value_{strategy.value}"
            
            # 测试统计信息
            stats = cache_manager.get_stats()
            assert 'memory_hits' in stats
            assert 'redis_hits' in stats
            assert 'misses' in stats
            
            # 清理
            cache_manager.delete(key)
    
    def test_real_redis_performance(self, real_redis_config, memory_config):
        """测试真实Redis性能"""
        cache_manager = CacheManager(
            redis_config=real_redis_config,
            memory_config=memory_config,
            strategy=CacheStrategy.REDIS_FIRST
        )
        
        import time
        
        # 测试设置性能
        start_time = time.time()
        for i in range(100):
            cache_manager.set(f"perf_test_{i}", f"value_{i}", ttl=60)
        set_time = time.time() - start_time
        set_ops_per_sec = 100 / set_time
        
        print(f"Redis设置性能: {set_ops_per_sec:.2f} ops/s")
        assert set_ops_per_sec > 10  # 至少10 ops/s
        
        # 测试获取性能
        start_time = time.time()
        for i in range(100):
            value = cache_manager.get(f"perf_test_{i}")
            assert value == f"value_{i}"
        get_time = time.time() - start_time
        get_ops_per_sec = 100 / get_time
        
        print(f"Redis获取性能: {get_ops_per_sec:.2f} ops/s")
        assert get_ops_per_sec > 20  # 至少20 ops/s (云Redis网络延迟影响)
        
        # 清理
        for i in range(100):
            cache_manager.delete(f"perf_test_{i}")
    
    def test_real_redis_complex_data(self, real_redis_config, memory_config):
        """测试真实Redis复杂数据"""
        cache_manager = CacheManager(
            redis_config=real_redis_config,
            memory_config=memory_config,
            strategy=CacheStrategy.REDIS_FIRST
        )
        
        # 测试复杂数据结构
        complex_data = {
            'string': 'test_string',
            'number': 123,
            'float': 3.14,
            'boolean': True,
            'list': [1, 2, 3, 'test'],
            'dict': {'nested': 'value', 'count': 42},
            'null': None
        }
        
        cache_manager.set("complex_data", complex_data, ttl=60)
        retrieved = cache_manager.get("complex_data")
        assert retrieved == complex_data
        
        # 测试JSON数据
        import json
        json_data = json.dumps(complex_data)
        cache_manager.set("json_data", json_data, ttl=60)
        retrieved_json = cache_manager.get("json_data")
        # Redis可能会自动解析JSON，所以我们需要重新序列化来比较
        if isinstance(retrieved_json, dict):
            retrieved_json = json.dumps(retrieved_json)
        assert retrieved_json == json_data
        
        # 清理
        cache_manager.delete("complex_data")
        cache_manager.delete("json_data")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
