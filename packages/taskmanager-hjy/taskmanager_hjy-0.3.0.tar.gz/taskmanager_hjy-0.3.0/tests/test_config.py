"""
配置管理模块测试

测试配置加载、验证、环境变量覆盖和热重载功能。
"""

import os
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open
import pytest

from taskmanager_hjy.core.config import (
    ConfigManager,
    TaskManagerConfig,
    RedisConfig,
    RQConfig,
    get_config_manager,
    get_config
)


class TestRedisConfig:
    """Redis配置测试"""
    
    def test_valid_redis_url(self):
        """测试有效的Redis URL"""
        config = RedisConfig(url="redis://localhost:6379/0")
        assert config.url == "redis://localhost:6379/0"
    
    def test_valid_redis_ssl_url(self):
        """测试有效的Redis SSL URL"""
        config = RedisConfig(url="rediss://localhost:6379/0")
        assert config.url == "rediss://localhost:6379/0"
    
    def test_invalid_redis_url(self):
        """测试无效的Redis URL"""
        with pytest.raises(ValueError, match="Redis URL must start with redis:// or rediss://"):
            RedisConfig(url="http://localhost:6379/0")
    
    def test_default_values(self):
        """测试默认值"""
        config = RedisConfig(url="redis://localhost:6379/0")
        assert config.connection_pool_size == 10
        assert config.socket_timeout == 5
        assert config.socket_connect_timeout == 5
        assert config.retry_on_timeout is True
        assert config.health_check_interval == 30


class TestRQConfig:
    """RQ配置测试"""
    
    def test_default_values(self):
        """测试默认值"""
        config = RQConfig()
        assert config.default_timeout == 300
        assert config.max_retries == 3
        assert config.retry_delay == 3
        assert config.job_monitoring_interval == 1
        assert config.result_ttl == 3600
        assert config.job_ttl == 3600


class TestTaskManagerConfig:
    """任务管理器配置测试"""
    
    def test_minimal_config(self):
        """测试最小配置"""
        config = TaskManagerConfig(
            redis={"url": "redis://localhost:6379/0"}
        )
        assert config.redis.url == "redis://localhost:6379/0"
        assert config.rq.default_timeout == 300
        assert config.ai_service.runner_package == "ai_runner_hjy"
    
    def test_full_config(self):
        """测试完整配置"""
        config_dict = {
            "redis": {
                "url": "redis://localhost:6379/0",
                "connection_pool_size": 20,
                "socket_timeout": 10
            },
            "rq": {
                "default_timeout": 600,
                "max_retries": 5
            },
            "tasks": {
                "audio_analysis": {
                    "max_retry": 3,
                    "timeout": 300,
                    "priority": 2
                }
            },
            "ai_service": {
                "runner_package": "custom_ai_runner",
                "timeout": 600
            },
            "logging": {
                "level": "DEBUG",
                "file": "logs/taskmanager.log"
            }
        }
        
        config = TaskManagerConfig(**config_dict)
        assert config.redis.connection_pool_size == 20
        assert config.redis.socket_timeout == 10
        assert config.rq.default_timeout == 600
        assert config.rq.max_retries == 5
        assert "audio_analysis" in config.tasks
        assert config.tasks["audio_analysis"].priority == 2
        assert config.ai_service.runner_package == "custom_ai_runner"
        assert config.ai_service.timeout == 600
        assert config.logging.level == "DEBUG"
        assert config.logging.file == "logs/taskmanager.log"
    
    def test_extra_fields_forbidden(self):
        """测试禁止额外字段"""
        config_dict = {
            "redis": {"url": "redis://localhost:6379/0"},
            "unknown_field": "value"
        }
        
        with pytest.raises(ValueError):
            TaskManagerConfig(**config_dict)


class TestConfigManager:
    """配置管理器测试"""
    
    def test_init_with_default_path(self):
        """测试使用默认路径初始化"""
        manager = ConfigManager()
        assert manager.config_path is not None
    
    def test_init_with_custom_path(self):
        """测试使用自定义路径初始化"""
        custom_path = Path("/tmp/custom_config.yaml")
        manager = ConfigManager(custom_path)
        assert manager.config_path == custom_path
    
    def test_load_config_file_not_found(self):
        """测试配置文件不存在的情况"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent.yaml"
            manager = ConfigManager(config_path)
            
            # 应该使用默认配置
            config = manager.load_config()
            assert config.redis.url == "redis://localhost:6379/0"
            assert config.rq.default_timeout == 300
    
    def test_load_config_file_empty(self):
        """测试配置文件为空的情况"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "empty.yaml"
            config_path.write_text("")
            
            manager = ConfigManager(config_path)
            config = manager.load_config()
            
            # 应该使用默认配置
            assert config.redis.url == "redis://localhost:6379/0"
    
    def test_load_config_file_invalid_yaml(self):
        """测试无效的YAML文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "invalid.yaml"
            config_path.write_text("invalid: yaml: content: [")
            
            manager = ConfigManager(config_path)
            
            with pytest.raises(yaml.YAMLError):
                manager.load_config()
    
    def test_load_config_file_valid(self):
        """测试有效的配置文件"""
        config_dict = {
            "redis": {
                "url": "redis://test-host:6379/1",
                "connection_pool_size": 15
            },
            "rq": {
                "default_timeout": 500,
                "max_retries": 4
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "valid.yaml"
            with open(config_path, 'w') as f:
                yaml.dump(config_dict, f)
            
            manager = ConfigManager(config_path)
            config = manager.load_config()
            
            assert config.redis.url == "redis://test-host:6379/1"
            assert config.redis.connection_pool_size == 15
            assert config.rq.default_timeout == 500
            assert config.rq.max_retries == 4
    
    def test_env_overrides(self):
        """测试环境变量覆盖"""
        config_dict = {
            "redis": {"url": "redis://default:6379/0"},
            "rq": {"default_timeout": 300}
        }
        
        env_vars = {
            "TASKMANAGER_HJY_REDIS_URL": "redis://env-override:6379/1",
            "TASKMANAGER_HJY_RQ_TIMEOUT": "600",
            "TASKMANAGER_HJY_LOG_LEVEL": "DEBUG"
        }
        
        with patch.dict(os.environ, env_vars):
            with tempfile.TemporaryDirectory() as temp_dir:
                config_path = Path(temp_dir) / "config.yaml"
                with open(config_path, 'w') as f:
                    yaml.dump(config_dict, f)
                
                manager = ConfigManager(config_path)
                config = manager.load_config()
                
                # 环境变量应该覆盖配置文件
                assert config.redis.url == "redis://env-override:6379/1"
                assert config.rq.default_timeout == 600
                assert config.logging.level == "DEBUG"
    
    def test_config_caching(self):
        """测试配置缓存"""
        config_dict = {
            "redis": {"url": "redis://localhost:6379/0"}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            with open(config_path, 'w') as f:
                yaml.dump(config_dict, f)
            
            manager = ConfigManager(config_path)
            
            # 第一次加载
            config1 = manager.load_config()
            
            # 第二次加载应该使用缓存
            config2 = manager.load_config()
            
            assert config1 is config2
    
    def test_force_reload(self):
        """测试强制重新加载"""
        config_dict = {
            "redis": {"url": "redis://localhost:6379/0"}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            with open(config_path, 'w') as f:
                yaml.dump(config_dict, f)
            
            manager = ConfigManager(config_path)
            
            # 第一次加载
            config1 = manager.load_config()
            
            # 强制重新加载
            config2 = manager.load_config(force_reload=True)
            
            # 应该创建新的配置对象
            assert config1 is not config2
    
    def test_validate_config(self):
        """测试配置验证"""
        manager = ConfigManager()
        
        # 有效配置
        valid_config = {
            "redis": {"url": "redis://localhost:6379/0"}
        }
        assert manager.validate_config(valid_config) is True
        
        # 无效配置
        invalid_config = {
            "redis": {"url": "invalid-url"}
        }
        assert manager.validate_config(invalid_config) is False
    
    def test_create_sample_config(self):
        """测试创建示例配置"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "sample_config.yaml"
            manager = ConfigManager()
            manager.create_sample_config(output_path)
            
            assert output_path.exists()
            
            # 验证生成的配置文件
            with open(output_path, 'r') as f:
                sample_config = yaml.safe_load(f)
            
            assert "redis" in sample_config
            assert "rq" in sample_config
            assert "tasks" in sample_config
            assert "ai_service" in sample_config
            assert "logging" in sample_config
    
    def test_get_config_summary(self):
        """测试获取配置摘要"""
        config_dict = {
            "redis": {"url": "redis://test-host:6379/1"},
            "rq": {"default_timeout": 500, "max_retries": 4},
            "tasks": {
                "audio_analysis": {"max_retry": 3},
                "text_analysis": {"max_retry": 2}
            },
            "ai_service": {"runner_package": "custom_runner"},
            "logging": {"level": "DEBUG"}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            with open(config_path, 'w') as f:
                yaml.dump(config_dict, f)
            
            manager = ConfigManager(config_path)
            summary = manager.get_config_summary()
            
            assert summary["redis_url"] == "redis://test-host:6379/1"
            assert summary["rq_timeout"] == 500
            assert summary["rq_max_retries"] == 4
            assert summary["ai_runner_package"] == "custom_runner"
            assert summary["log_level"] == "DEBUG"
            assert "audio_analysis" in summary["task_types"]
            assert "text_analysis" in summary["task_types"]


class TestGlobalFunctions:
    """全局函数测试"""
    
    def test_get_config_manager_singleton(self):
        """测试配置管理器单例模式"""
        manager1 = get_config_manager()
        manager2 = get_config_manager()
        assert manager1 is manager2
    
    def test_get_config(self):
        """测试获取配置便捷函数"""
        config_dict = {
            "redis": {"url": "redis://localhost:6379/0"}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            with open(config_path, 'w') as f:
                yaml.dump(config_dict, f)
            
            config = get_config(config_path)
            assert config.redis.url == "redis://localhost:6379/0"
            assert isinstance(config, TaskManagerConfig)


if __name__ == "__main__":
    pytest.main([__file__])
