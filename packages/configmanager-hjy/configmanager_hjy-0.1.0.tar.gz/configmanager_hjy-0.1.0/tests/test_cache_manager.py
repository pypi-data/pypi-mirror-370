#!/usr/bin/env python3
"""
缓存管理器单元测试
"""

import pytest
import time
import json
from unittest.mock import Mock, patch

from configmanager_hjy.cache import CacheManager, CacheStrategy


class TestCacheManager:
    """缓存管理器测试类"""
    
    @pytest.fixture
    def redis_config(self):
        """Redis配置"""
        return {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'decode_responses': True
        }
    
    @pytest.fixture
    def memory_config(self):
        """内存缓存配置"""
        return {
            'max_size': 100,
            'default_ttl': 60
        }
    
    @pytest.fixture
    def cache_manager(self, redis_config, memory_config):
        """缓存管理器实例"""
        return CacheManager(
            redis_config=redis_config,
            memory_config=memory_config,
            strategy=CacheStrategy.MEMORY_ONLY
        )
    
    def test_init_memory_only(self, redis_config, memory_config):
        """测试仅内存缓存策略初始化"""
        cache = CacheManager(
            redis_config=redis_config,
            memory_config=memory_config,
            strategy=CacheStrategy.MEMORY_ONLY
        )
        
        assert cache.strategy == CacheStrategy.MEMORY_ONLY
        assert cache.memory_cache is not None
        assert cache.redis_cache is None
    
    def test_init_with_redis_failure(self, redis_config, memory_config):
        """测试Redis连接失败时的初始化"""
        with patch('configmanager_hjy.cache.redis_cache.RedisCache') as mock_redis:
            mock_redis.side_effect = Exception("Connection failed")
            
            cache = CacheManager(
                redis_config=redis_config,
                memory_config=memory_config,
                strategy=CacheStrategy.LAYERED
            )
            
            assert cache.redis_cache is None
            assert cache.memory_cache is not None
    
    def test_set_and_get(self, cache_manager):
        """测试基本的设置和获取操作"""
        # 设置缓存
        cache_manager.set("test_key", "test_value", ttl=30)
        
        # 获取缓存
        value = cache_manager.get("test_key")
        assert value == "test_value"
        
        # 检查统计
        stats = cache_manager.get_stats()
        assert stats['memory_sets'] == 1
        assert stats['memory_hits'] == 1
    
    def test_get_nonexistent_key(self, cache_manager):
        """测试获取不存在的键"""
        value = cache_manager.get("nonexistent_key")
        assert value is None
        
        # 检查统计
        stats = cache_manager.get_stats()
        assert stats['misses'] == 1
    
    def test_get_with_default(self, cache_manager):
        """测试获取带默认值的操作"""
        value = cache_manager.get("nonexistent_key", default="default_value")
        assert value == "default_value"
    
    def test_delete(self, cache_manager):
        """测试删除操作"""
        # 先设置
        cache_manager.set("test_key", "test_value")
        
        # 验证存在
        assert cache_manager.exists("test_key")
        
        # 删除
        result = cache_manager.delete("test_key")
        assert result is True
        
        # 验证不存在
        assert not cache_manager.exists("test_key")
        assert cache_manager.get("test_key") is None
    
    def test_exists(self, cache_manager):
        """测试存在性检查"""
        # 不存在的键
        assert not cache_manager.exists("nonexistent_key")
        
        # 存在的键
        cache_manager.set("test_key", "test_value")
        assert cache_manager.exists("test_key")
    
    def test_ttl_operations(self, cache_manager):
        """测试TTL操作"""
        # 设置带TTL的缓存
        cache_manager.set("test_key", "test_value", ttl=30)
        
        # 获取TTL
        ttl = cache_manager.get_ttl("test_key")
        assert ttl is not None
        assert 25 <= ttl <= 30  # 允许一些时间误差
        
        # 修改TTL
        cache_manager.set_ttl("test_key", 60)
        new_ttl = cache_manager.get_ttl("test_key")
        assert 55 <= new_ttl <= 60
    
    def test_clear(self, cache_manager):
        """测试清空操作"""
        # 设置多个缓存
        cache_manager.set("key1", "value1")
        cache_manager.set("key2", "value2")
        
        # 验证存在
        assert cache_manager.exists("key1")
        assert cache_manager.exists("key2")
        
        # 清空
        result = cache_manager.clear()
        assert result is True
        
        # 验证不存在
        assert not cache_manager.exists("key1")
        assert not cache_manager.exists("key2")
    
    def test_complex_data(self, cache_manager):
        """测试复杂数据类型"""
        complex_data = {
            'string': 'test_string',
            'number': 123,
            'float': 3.14,
            'boolean': True,
            'list': [1, 2, 3, 'test'],
            'dict': {'nested': 'value', 'count': 42}
        }
        
        # 设置复杂数据
        cache_manager.set("complex_key", complex_data, ttl=60)
        
        # 获取复杂数据
        retrieved_data = cache_manager.get("complex_key")
        
        # 验证数据一致性
        assert retrieved_data == complex_data
    
    def test_batch_operations(self, cache_manager):
        """测试批量操作"""
        batch_data = {
            'batch_key1': 'value1',
            'batch_key2': 'value2',
            'batch_key3': 'value3'
        }
        
        # 批量设置
        for key, value in batch_data.items():
            cache_manager.set(key, value, ttl=60)
        
        # 批量获取
        for key, expected_value in batch_data.items():
            retrieved_value = cache_manager.get(key)
            assert retrieved_value == expected_value
    
    def test_get_keys(self, cache_manager):
        """测试获取键列表"""
        # 设置一些缓存
        cache_manager.set("user:1", "value1")
        cache_manager.set("user:2", "value2")
        cache_manager.set("product:1", "value3")
        
        # 获取所有键
        all_keys = cache_manager.get_keys("*")
        assert "user:1" in all_keys
        assert "user:2" in all_keys
        assert "product:1" in all_keys
        
        # 获取匹配模式的键
        user_keys = cache_manager.get_keys("user:*")
        assert "user:1" in user_keys
        assert "user:2" in user_keys
        assert "product:1" not in user_keys
    
    def test_get_size(self, cache_manager):
        """测试获取缓存大小"""
        # 初始大小
        initial_size = cache_manager.get_size()
        assert initial_size['memory_cache'] == 0
        
        # 设置缓存
        cache_manager.set("key1", "value1")
        cache_manager.set("key2", "value2")
        
        # 检查大小
        size = cache_manager.get_size()
        assert size['memory_cache'] == 2
    
    def test_get_stats(self, cache_manager):
        """测试获取统计信息"""
        # 初始统计
        stats = cache_manager.get_stats()
        assert stats['memory_hits'] == 0
        assert stats['redis_hits'] == 0
        assert stats['misses'] == 0
        assert stats['memory_sets'] == 0
        assert stats['redis_sets'] == 0
        
        # 执行一些操作
        cache_manager.set("test_key", "test_value")
        cache_manager.get("test_key")
        cache_manager.get("nonexistent_key")
        
        # 检查统计
        stats = cache_manager.get_stats()
        assert stats['memory_sets'] == 1
        assert stats['memory_hits'] == 1
        assert stats['misses'] == 1
        
        # 检查命中率
        assert stats['memory_hit_rate'] == 50.0
        assert stats['redis_hit_rate'] == 0.0
        assert stats['miss_rate'] == 50.0
    
    def test_reset_stats(self, cache_manager):
        """测试重置统计信息"""
        # 执行一些操作
        cache_manager.set("test_key", "test_value")
        cache_manager.get("test_key")
        
        # 检查有统计
        stats = cache_manager.get_stats()
        assert stats['memory_sets'] > 0
        assert stats['memory_hits'] > 0
        
        # 重置统计
        cache_manager.reset_stats()
        
        # 检查统计已重置
        stats = cache_manager.get_stats()
        assert stats['memory_sets'] == 0
        assert stats['memory_hits'] == 0
        assert stats['misses'] == 0
    
    def test_health_check(self, cache_manager):
        """测试健康检查"""
        health = cache_manager.health_check()
        
        # 检查返回格式
        assert isinstance(health, dict)
        assert 'memory_cache' in health
        assert 'redis_cache' in health
        
        # 检查内存缓存状态
        assert health['memory_cache'] is True
        
        # 检查Redis缓存状态（应该是False，因为没有Redis连接）
        assert health['redis_cache'] is False
    
    def test_expiration(self, cache_manager):
        """测试过期机制"""
        # 设置短期TTL
        cache_manager.set("expire_key", "expire_value", ttl=1)
        
        # 立即获取应该存在
        assert cache_manager.get("expire_key") == "expire_value"
        
        # 等待过期
        time.sleep(2)
        
        # 获取应该返回None
        assert cache_manager.get("expire_key") is None
    
    def test_memory_strategy_only(self, redis_config, memory_config):
        """测试仅内存策略"""
        cache = CacheManager(
            redis_config=redis_config,
            memory_config=memory_config,
            strategy=CacheStrategy.MEMORY_ONLY
        )
        
        # 设置和获取
        cache.set("test_key", "test_value")
        value = cache.get("test_key")
        assert value == "test_value"
        
        # 检查统计
        stats = cache.get_stats()
        assert stats['memory_hits'] == 1
        assert stats['redis_hits'] == 0
    
    def test_error_handling(self, cache_manager):
        """测试错误处理"""
        # 测试无效的TTL设置
        cache_manager.set("test_key", "test_value")
        
        # 设置无效TTL应该不会抛出异常
        try:
            cache_manager.set_ttl("test_key", -1)
        except Exception:
            pytest.fail("设置无效TTL不应该抛出异常")
        
        # 测试获取不存在的键的TTL
        ttl = cache_manager.get_ttl("nonexistent_key")
        assert ttl is None
    
    def test_thread_safety(self, cache_manager):
        """测试线程安全性"""
        import threading
        import time
        
        results = []
        errors = []
        
        def worker(thread_id):
            try:
                for i in range(10):
                    key = f"thread_{thread_id}_key_{i}"
                    value = f"thread_{thread_id}_value_{i}"
                    
                    # 设置缓存
                    cache_manager.set(key, value, ttl=10)
                    
                    # 获取缓存
                    retrieved = cache_manager.get(key)
                    if retrieved != value:
                        errors.append(f"Thread {thread_id}: Value mismatch for {key}")
                    
                    time.sleep(0.01)  # 小延迟
                
                results.append(f"Thread {thread_id} completed")
            except Exception as e:
                errors.append(f"Thread {thread_id} error: {e}")
        
        # 创建多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 检查结果
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(results) == 5, "All threads should complete"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
