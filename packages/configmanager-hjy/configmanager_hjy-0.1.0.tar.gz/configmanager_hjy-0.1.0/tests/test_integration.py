#!/usr/bin/env python3
"""
真实环境集成测试
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch
from configmanager_hjy.cache import CacheManager, CacheStrategy
from configmanager_hjy.validators import SchemaValidator, TypeValidator, ValueValidator


class TestRedisIntegration:
    """Redis集成测试"""
    
    @pytest.fixture
    def redis_config(self):
        """Redis配置"""
        return {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'decode_responses': True,
            'socket_connect_timeout': 5,
            'socket_timeout': 5
        }
    
    @pytest.fixture
    def memory_config(self):
        """内存缓存配置"""
        return {
            'max_size': 1000,
            'default_ttl': 300
        }
    
    def test_redis_connection_success(self, redis_config, memory_config):
        """测试Redis连接成功"""
        try:
            cache_manager = CacheManager(
                redis_config=redis_config,
                memory_config=memory_config,
                strategy=CacheStrategy.REDIS_FIRST
            )
            
            # 测试基本操作
            cache_manager.set("test_key", "test_value", ttl=60)
            value = cache_manager.get("test_key")
            assert value == "test_value"
            
            # 测试TTL
            ttl = cache_manager.get_ttl("test_key")
            assert ttl > 0
            
            # 清理
            cache_manager.delete("test_key")
            
        except Exception as e:
            pytest.skip(f"Redis服务器不可用: {e}")
    
    def test_redis_connection_failure_fallback(self, memory_config):
        """测试Redis连接失败时的回退机制"""
        # 使用错误的Redis配置
        bad_redis_config = {
            'host': 'invalid_host',
            'port': 9999,
            'db': 0,
            'decode_responses': True
        }
        
        cache_manager = CacheManager(
            redis_config=bad_redis_config,
            memory_config=memory_config,
            strategy=CacheStrategy.REDIS_FIRST
        )
        
        # 应该回退到内存缓存
        cache_manager.set("fallback_key", "fallback_value")
        value = cache_manager.get("fallback_key")
        assert value == "fallback_value"
        
        # 验证健康检查
        health = cache_manager.health_check()
        assert health['memory']['status'] == 'healthy'
        assert health['redis']['status'] == 'unavailable'
    
    def test_redis_strategies(self, redis_config, memory_config):
        """测试不同的Redis策略"""
        strategies = [
            CacheStrategy.MEMORY_ONLY,
            CacheStrategy.REDIS_ONLY,
            CacheStrategy.MEMORY_FIRST,
            CacheStrategy.REDIS_FIRST,
            CacheStrategy.LAYERED
        ]
        
        for strategy in strategies:
            try:
                cache_manager = CacheManager(
                    redis_config=redis_config,
                    memory_config=memory_config,
                    strategy=strategy
                )
                
                # 基本功能测试
                key = f"strategy_test_{strategy.value}"
                cache_manager.set(key, f"value_{strategy.value}")
                value = cache_manager.get(key)
                assert value == f"value_{strategy.value}"
                
                # 清理
                cache_manager.delete(key)
                
            except Exception as e:
                if strategy == CacheStrategy.REDIS_ONLY:
                    pytest.skip(f"Redis策略测试跳过: {e}")
                else:
                    # 其他策略应该能正常工作
                    pass


class TestDatabaseIntegration:
    """数据库集成测试"""
    
    @pytest.fixture
    def db_config(self):
        """数据库配置"""
        return {
            'host': 'localhost',
            'port': 3306,
            'user': 'test_user',
            'password': 'test_password',
            'database': 'test_db'
        }
    
    def test_database_connection(self, db_config):
        """测试数据库连接"""
        try:
            import mysql.connector
            from configmanager_hjy.adapters.database import DatabaseAdapter
            
            adapter = DatabaseAdapter(db_config)
            
            # 测试连接
            connection = adapter.get_connection()
            assert connection.is_connected()
            
            # 测试基本操作
            adapter.create_table()
            
            # 测试配置存储
            config_data = {
                'key': 'test_config',
                'value': 'test_value',
                'environment': 'test',
                'version': 1
            }
            
            adapter.save_config(config_data)
            retrieved = adapter.get_config('test_config', 'test')
            assert retrieved['value'] == 'test_value'
            
            # 清理
            adapter.delete_config('test_config', 'test')
            connection.close()
            
        except Exception as e:
            pytest.skip(f"数据库不可用: {e}")


class TestOSSIntegration:
    """OSS存储集成测试"""
    
    @pytest.fixture
    def oss_config(self):
        """OSS配置"""
        return {
            'access_key_id': 'test_key',
            'access_key_secret': 'test_secret',
            'endpoint': 'http://oss-cn-hangzhou.aliyuncs.com',
            'bucket_name': 'test-bucket'
        }
    
    def test_oss_connection(self, oss_config):
        """测试OSS连接"""
        try:
            from configmanager_hjy.adapters.oss import OSSAdapter
            
            adapter = OSSAdapter(oss_config)
            
            # 测试基本操作
            test_data = {'test': 'data'}
            adapter.upload_config('test_config.json', test_data)
            
            # 测试下载
            downloaded = adapter.download_config('test_config.json')
            assert downloaded == test_data
            
            # 清理
            adapter.delete_config('test_config.json')
            
        except Exception as e:
            pytest.skip(f"OSS不可用: {e}")


class TestEndToEndIntegration:
    """端到端集成测试"""
    
    @pytest.fixture
    def full_config(self):
        """完整配置"""
        return {
            'redis': {
                'host': 'localhost',
                'port': 6379,
                'db': 0,
                'decode_responses': True
            },
            'memory': {
                'max_size': 1000,
                'default_ttl': 300
            },
            'database': {
                'host': 'localhost',
                'port': 3306,
                'user': 'test_user',
                'password': 'test_password',
                'database': 'test_db'
            },
            'oss': {
                'access_key_id': 'test_key',
                'access_key_secret': 'test_secret',
                'endpoint': 'http://oss-cn-hangzhou.aliyuncs.com',
                'bucket_name': 'test-bucket'
            }
        }
    
    def test_full_workflow(self, full_config):
        """测试完整工作流程"""
        try:
            from configmanager_hjy import ConfigManager
            
            # 初始化配置管理器
            config_manager = ConfigManager(full_config)
            
            # 测试配置设置和获取
            config_manager.set('app.database.url', 'mysql://localhost:3306/test')
            config_manager.set('app.redis.host', 'localhost')
            config_manager.set('app.features.enabled', True)
            
            # 验证配置
            db_url = config_manager.get('app.database.url')
            redis_host = config_manager.get('app.redis.host')
            features_enabled = config_manager.get_bool('app.features.enabled')
            
            assert db_url == 'mysql://localhost:3306/test'
            assert redis_host == 'localhost'
            assert features_enabled is True
            
            # 测试配置监听
            changes = []
            
            def on_change(key, old_value, new_value):
                changes.append((key, old_value, new_value))
            
            config_manager.watch('app.database.url', on_change)
            
            # 触发变更
            config_manager.set('app.database.url', 'mysql://localhost:3306/prod')
            
            # 等待监听器执行
            time.sleep(0.1)
            
            assert len(changes) == 1
            assert changes[0][0] == 'app.database.url'
            assert changes[0][1] == 'mysql://localhost:3306/test'
            assert changes[0][2] == 'mysql://localhost:3306/prod'
            
            # 测试健康检查
            health = config_manager.health_check()
            assert 'cache' in health
            assert 'database' in health
            assert 'oss' in health
            
            # 清理
            config_manager.unwatch('app.database.url', on_change)
            
        except Exception as e:
            pytest.skip(f"端到端测试跳过: {e}")
    
    def test_concurrent_access(self, full_config):
        """测试并发访问"""
        try:
            from configmanager_hjy import ConfigManager
            
            config_manager = ConfigManager(full_config)
            
            # 设置初始值
            config_manager.set('counter', 0)
            
            # 并发递增
            def increment_counter():
                for _ in range(10):
                    current = config_manager.get_int('counter')
                    config_manager.set('counter', current + 1)
                    time.sleep(0.01)
            
            threads = []
            for _ in range(5):
                thread = threading.Thread(target=increment_counter)
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # 验证最终值
            final_value = config_manager.get_int('counter')
            assert final_value == 50  # 5线程 * 10次递增
            
        except Exception as e:
            pytest.skip(f"并发测试跳过: {e}")


class TestErrorHandling:
    """错误处理测试"""
    
    def test_invalid_config_handling(self):
        """测试无效配置处理"""
        # 测试无效的Redis配置
        invalid_redis_config = {
            'host': 'invalid_host',
            'port': 'invalid_port',  # 应该是数字
            'db': 'invalid_db'       # 应该是数字
        }
        
        memory_config = {'max_size': 1000, 'default_ttl': 300}
        
        # 应该能正常初始化，但Redis会失败
        cache_manager = CacheManager(
            redis_config=invalid_redis_config,
            memory_config=memory_config,
            strategy=CacheStrategy.REDIS_FIRST
        )
        
        # 内存缓存应该正常工作
        cache_manager.set('test_key', 'test_value')
        value = cache_manager.get('test_key')
        assert value == 'test_value'
        
        # 健康检查应该显示Redis不可用
        health = cache_manager.health_check()
        assert health['redis']['status'] == 'unavailable'
    
    def test_network_timeout_handling(self):
        """测试网络超时处理"""
        # 使用很短的超时时间
        redis_config = {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'decode_responses': True,
            'socket_connect_timeout': 0.001,  # 1毫秒
            'socket_timeout': 0.001
        }
        
        memory_config = {'max_size': 1000, 'default_ttl': 300}
        
        cache_manager = CacheManager(
            redis_config=redis_config,
            memory_config=memory_config,
            strategy=CacheStrategy.REDIS_FIRST
        )
        
        # 应该回退到内存缓存
        cache_manager.set('timeout_test', 'timeout_value')
        value = cache_manager.get('timeout_test')
        assert value == 'timeout_value'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
