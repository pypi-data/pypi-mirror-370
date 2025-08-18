"""
配置管理模块

提供配置驱动的初始化系统，支持YAML配置文件、环境变量覆盖和配置验证。
严格遵循云原生公民原则：配置驱动、依赖注入、生命周期管理。
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field, validator
from loguru import logger


class RedisConfig(BaseModel):
    """Redis配置模型"""
    url: str = Field(..., description="Redis连接URL")
    connection_pool_size: int = Field(default=10, description="连接池大小")
    socket_timeout: int = Field(default=5, description="Socket超时时间(秒)")
    socket_connect_timeout: int = Field(default=5, description="Socket连接超时时间(秒)")
    retry_on_timeout: bool = Field(default=True, description="超时时是否重试")
    health_check_interval: int = Field(default=30, description="健康检查间隔(秒)")

    @validator('url')
    def validate_redis_url(cls, v):
        """验证Redis URL格式"""
        if not v.startswith(('redis://', 'rediss://')):
            raise ValueError('Redis URL must start with redis:// or rediss://')
        return v


class RQConfig(BaseModel):
    """RQ队列配置模型"""
    default_timeout: int = Field(default=300, description="默认任务超时时间(秒)")
    max_retries: int = Field(default=3, description="最大重试次数")
    retry_delay: int = Field(default=3, description="重试延迟时间(秒)")
    job_monitoring_interval: int = Field(default=1, description="任务监控间隔(秒)")
    result_ttl: int = Field(default=3600, description="结果缓存时间(秒)")
    job_ttl: int = Field(default=3600, description="任务缓存时间(秒)")


class TaskConfig(BaseModel):
    """任务配置模型"""
    max_retry: int = Field(default=3, description="最大重试次数")
    timeout: int = Field(default=300, description="任务超时时间(秒)")
    priority: int = Field(default=1, description="任务优先级")
    result_ttl: int = Field(default=3600, description="结果缓存时间(秒)")


class AIServiceConfig(BaseModel):
    """AI服务配置模型"""
    runner_package: str = Field(default="ai_runner_hjy", description="AI运行器包名")
    config_source: str = Field(default="auto", description="配置来源(auto/manual)")
    timeout: int = Field(default=300, description="AI服务超时时间(秒)")
    max_retries: int = Field(default=3, description="AI服务最大重试次数")


class LoggingConfig(BaseModel):
    """日志配置模型"""
    level: str = Field(default="INFO", description="日志级别")
    format: str = Field(
        default="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        description="日志格式"
    )
    file: Optional[str] = Field(default=None, description="日志文件路径")
    rotation: str = Field(default="1 day", description="日志轮转策略")
    retention: str = Field(default="30 days", description="日志保留策略")
    compression: str = Field(default="gz", description="日志压缩格式")


class TaskManagerConfig(BaseModel):
    """任务管理器配置模型"""
    redis: RedisConfig = Field(..., description="Redis配置")
    rq: RQConfig = Field(default_factory=RQConfig, description="RQ配置")
    tasks: Dict[str, TaskConfig] = Field(default_factory=dict, description="任务类型配置")
    ai_service: AIServiceConfig = Field(default_factory=AIServiceConfig, description="AI服务配置")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="日志配置")

    class Config:
        """Pydantic配置"""
        extra = "forbid"  # 禁止额外字段
        validate_assignment = True  # 赋值时验证


class ConfigManager:
    """
    配置管理器
    
    负责配置的加载、验证、环境变量覆盖和热重载功能。
    严格遵循云原生公民原则。
    """
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        self.config_path = Path(config_path) if config_path else self._get_default_config_path()
        self._config: Optional[TaskManagerConfig] = None
        self._config_file_mtime: Optional[float] = None
        
        logger.info(f"ConfigManager initialized with config path: {self.config_path}")
    
    def _get_default_config_path(self) -> Path:
        """获取默认配置文件路径"""
        # 按优先级查找配置文件
        search_paths = [
            Path("config.yaml"),
            Path("config.yml"),
            Path("taskmanager_hjy.yaml"),
            Path("taskmanager_hjy.yml"),
            Path.home() / ".taskmanager_hjy" / "config.yaml",
            Path.home() / ".taskmanager_hjy" / "config.yml",
        ]
        
        for path in search_paths:
            if path.exists():
                logger.info(f"Found config file: {path}")
                return path
        
        # 如果没找到配置文件，返回默认路径
        default_path = Path("config.yaml")
        logger.warning(f"No config file found, will use default path: {default_path}")
        return default_path
    
    def load_config(self, force_reload: bool = False) -> TaskManagerConfig:
        """
        加载配置
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            配置对象
            
        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML解析错误
            ValueError: 配置验证错误
        """
        # 检查是否需要重新加载
        if not force_reload and self._config is not None:
            if self.config_path.exists():
                current_mtime = self.config_path.stat().st_mtime
                if self._config_file_mtime == current_mtime:
                    logger.debug("Config file unchanged, using cached config")
                    return self._config
        
        # 加载配置文件
        config_dict = self._load_config_file()
        
        # 应用环境变量覆盖
        config_dict = self._apply_env_overrides(config_dict)
        
        # 验证配置
        try:
            self._config = TaskManagerConfig(**config_dict)
            if self.config_path.exists():
                self._config_file_mtime = self.config_path.stat().st_mtime
            
            logger.info("Configuration loaded and validated successfully")
            return self._config
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise ValueError(f"Configuration validation failed: {e}")
    
    def _load_config_file(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
            
            if config_dict is None:
                logger.warning("Config file is empty, using default config")
                return self._get_default_config()
            
            logger.info(f"Config file loaded: {self.config_path}")
            return config_dict
            
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML config file: {e}")
            raise yaml.YAMLError(f"Failed to parse YAML config file: {e}")
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
            raise FileNotFoundError(f"Failed to load config file: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "redis": {
                "url": "redis://localhost:6379/0",
                "connection_pool_size": 10,
                "socket_timeout": 5,
                "socket_connect_timeout": 5,
                "retry_on_timeout": True,
                "health_check_interval": 30
            },
            "rq": {
                "default_timeout": 300,
                "max_retries": 3,
                "retry_delay": 3,
                "job_monitoring_interval": 1,
                "result_ttl": 3600,
                "job_ttl": 3600
            },
            "tasks": {
                "default": {
                    "max_retry": 3,
                    "timeout": 300,
                    "priority": 1,
                    "result_ttl": 3600
                },
                "audio_analysis": {
                    "max_retry": 3,
                    "timeout": 300,
                    "priority": 1,
                    "result_ttl": 3600
                }
            },
            "ai_service": {
                "runner_package": "ai_runner_hjy",
                "config_source": "auto",
                "timeout": 300,
                "max_retries": 3
            },
            "logging": {
                "level": "INFO",
                "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
                "file": None,
                "rotation": "1 day",
                "retention": "30 days",
                "compression": "gz"
            }
        }
    
    def _apply_env_overrides(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """应用环境变量覆盖"""
        env_prefix = "TASKMANAGER_HJY_"
        
        # Redis配置覆盖
        if f"{env_prefix}REDIS_URL" in os.environ:
            config_dict.setdefault("redis", {})["url"] = os.environ[f"{env_prefix}REDIS_URL"]
        
        if f"{env_prefix}REDIS_POOL_SIZE" in os.environ:
            config_dict.setdefault("redis", {})["connection_pool_size"] = int(
                os.environ[f"{env_prefix}REDIS_POOL_SIZE"]
            )
        
        # RQ配置覆盖
        if f"{env_prefix}RQ_TIMEOUT" in os.environ:
            config_dict.setdefault("rq", {})["default_timeout"] = int(
                os.environ[f"{env_prefix}RQ_TIMEOUT"]
            )
        
        if f"{env_prefix}RQ_MAX_RETRIES" in os.environ:
            config_dict.setdefault("rq", {})["max_retries"] = int(
                os.environ[f"{env_prefix}RQ_MAX_RETRIES"]
            )
        
        # AI服务配置覆盖
        if f"{env_prefix}AI_RUNNER_PACKAGE" in os.environ:
            config_dict.setdefault("ai_service", {})["runner_package"] = os.environ[
                f"{env_prefix}AI_RUNNER_PACKAGE"
            ]
        
        # 日志配置覆盖
        if f"{env_prefix}LOG_LEVEL" in os.environ:
            config_dict.setdefault("logging", {})["level"] = os.environ[f"{env_prefix}LOG_LEVEL"]
        
        if f"{env_prefix}LOG_FILE" in os.environ:
            config_dict.setdefault("logging", {})["file"] = os.environ[f"{env_prefix}LOG_FILE"]
        
        logger.debug("Environment variable overrides applied")
        return config_dict
    
    def get_config(self) -> TaskManagerConfig:
        """获取当前配置（支持热重载）"""
        return self.load_config()
    
    def reload_config(self) -> TaskManagerConfig:
        """强制重新加载配置"""
        logger.info("Forcing config reload")
        return self.load_config(force_reload=True)
    
    def validate_config(self, config_dict: Dict[str, Any]) -> bool:
        """
        验证配置字典
        
        Args:
            config_dict: 配置字典
            
        Returns:
            是否有效
        """
        try:
            TaskManagerConfig(**config_dict)
            return True
        except Exception as e:
            logger.error(f"Config validation failed: {e}")
            return False
    
    def create_sample_config(self, output_path: Optional[Union[str, Path]] = None) -> None:
        """
        创建示例配置文件
        
        Args:
            output_path: 输出路径，如果为None则使用默认路径
        """
        if output_path is None:
            output_path = Path("config.yaml")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        sample_config = self._get_default_config()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(sample_config, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        logger.info(f"Sample config created: {output_path}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        config = self.get_config()
        return {
            "redis_url": config.redis.url,
            "rq_timeout": config.rq.default_timeout,
            "rq_max_retries": config.rq.max_retries,
            "ai_runner_package": config.ai_service.runner_package,
            "log_level": config.logging.level,
            "task_types": list(config.tasks.keys())
        }


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: Optional[Union[str, Path]] = None) -> ConfigManager:
    """
    获取全局配置管理器实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager


def get_config(config_path: Optional[Union[str, Path]] = None) -> TaskManagerConfig:
    """
    获取配置（便捷函数）
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置对象
    """
    return get_config_manager(config_path).get_config()
