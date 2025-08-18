"""
Redis连接工具模块

提供Redis连接池、连接测试、错误处理和重试机制。
严格遵循云原生公民原则：配置驱动、依赖注入、生命周期管理。
"""

import time
from typing import Optional, Dict, Any, Union
from redis import Redis, ConnectionPool, RedisError
from redis.exceptions import ConnectionError, TimeoutError, AuthenticationError
from loguru import logger

from ..core.config import RedisConfig


class RedisConnectionError(Exception):
    """Redis连接错误"""
    pass


class RedisConnectionManager:
    """
    Redis连接管理器
    
    负责Redis连接池的创建、管理和监控。
    提供连接测试、错误处理和重试机制。
    """
    
    def __init__(self, config: RedisConfig):
        """
        初始化Redis连接管理器
        
        Args:
            config: Redis配置对象
        """
        self.config = config
        self._connection_pool: Optional[ConnectionPool] = None
        self._redis_client: Optional[Redis] = None
        self._last_health_check: float = 0
        self._health_check_interval = config.health_check_interval
        
        logger.info(f"RedisConnectionManager initialized with URL: {config.url}")
    
    def _create_connection_pool(self) -> ConnectionPool:
        """创建Redis连接池"""
        try:
            pool = ConnectionPool.from_url(
                url=self.config.url,
                max_connections=self.config.connection_pool_size,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                retry_on_timeout=self.config.retry_on_timeout,
                decode_responses=True,  # 自动解码响应
                health_check_interval=self.config.health_check_interval
            )
            logger.info(f"Redis connection pool created with {self.config.connection_pool_size} connections")
            return pool
        except Exception as e:
            logger.error(f"Failed to create Redis connection pool: {e}")
            raise RedisConnectionError(f"Failed to create Redis connection pool: {e}")
    
    def get_redis_client(self) -> Redis:
        """
        获取Redis客户端
        
        Returns:
            Redis客户端实例
            
        Raises:
            RedisConnectionError: 连接失败时抛出
        """
        if self._redis_client is None:
            self._connection_pool = self._create_connection_pool()
            self._redis_client = Redis(connection_pool=self._connection_pool)
            
            # 测试连接
            self._test_connection()
        
        return self._redis_client
    
    def _test_connection(self) -> bool:
        """
        测试Redis连接
        
        Returns:
            连接是否正常
            
        Raises:
            RedisConnectionError: 连接失败时抛出
        """
        try:
            client = self._redis_client
            if client is None:
                raise RedisConnectionError("Redis client not initialized")
            
            # 执行PING命令测试连接
            response = client.ping()
            if not response:
                raise RedisConnectionError("Redis PING command failed")
            
            logger.debug("Redis connection test successful")
            return True
            
        except (ConnectionError, TimeoutError, AuthenticationError) as e:
            logger.error(f"Redis connection test failed: {e}")
            raise RedisConnectionError(f"Redis connection test failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during Redis connection test: {e}")
            raise RedisConnectionError(f"Unexpected error during Redis connection test: {e}")
    
    def health_check(self, force: bool = False) -> bool:
        """
        健康检查
        
        Args:
            force: 是否强制检查（忽略时间间隔）
            
        Returns:
            连接是否健康
        """
        current_time = time.time()
        
        # 检查是否需要执行健康检查
        if not force and (current_time - self._last_health_check) < self._health_check_interval:
            return True
        
        try:
            result = self._test_connection()
            self._last_health_check = current_time
            return result
        except RedisConnectionError:
            return False
    
    def execute_with_retry(self, operation: callable, max_retries: int = 3, 
                          retry_delay: float = 1.0, *args, **kwargs) -> Any:
        """
        带重试机制执行Redis操作
        
        Args:
            operation: 要执行的Redis操作函数
            max_retries: 最大重试次数
            retry_delay: 重试延迟时间（秒）
            *args: 操作函数的参数
            **kwargs: 操作函数的关键字参数
            
        Returns:
            操作结果
            
        Raises:
            RedisConnectionError: 所有重试都失败后抛出
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                client = self.get_redis_client()
                result = operation(client, *args, **kwargs)
                return result
                
            except (ConnectionError, TimeoutError, AuthenticationError) as e:
                last_exception = e
                logger.warning(f"Redis operation failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                
                if attempt < max_retries:
                    # 重置连接池
                    self._reset_connection()
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Redis operation failed after {max_retries + 1} attempts")
                    raise RedisConnectionError(f"Redis operation failed after {max_retries + 1} attempts: {e}")
                    
            except Exception as e:
                logger.error(f"Unexpected error during Redis operation: {e}")
                raise RedisConnectionError(f"Unexpected error during Redis operation: {e}")
    
    def _reset_connection(self) -> None:
        """重置连接"""
        try:
            if self._redis_client:
                self._redis_client.close()
            if self._connection_pool:
                self._connection_pool.disconnect()
            
            self._redis_client = None
            self._connection_pool = None
            
            logger.info("Redis connection reset")
            
        except Exception as e:
            logger.error(f"Error resetting Redis connection: {e}")
    
    def close(self) -> None:
        """关闭连接"""
        try:
            if self._redis_client:
                self._redis_client.close()
            if self._connection_pool:
                self._connection_pool.disconnect()
            
            logger.info("Redis connection closed")
            
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")
    
    def get_connection_info(self) -> Dict[str, Any]:
        """获取连接信息"""
        info = {
            "url": self.config.url,
            "pool_size": self.config.connection_pool_size,
            "timeout": self.config.socket_timeout,
            "health_check_interval": self.config.health_check_interval,
            "connected": False,
            "last_health_check": self._last_health_check
        }
        
        try:
            if self._redis_client:
                info["connected"] = self.health_check(force=True)
        except Exception:
            pass
        
        return info


class RedisHelper:
    """
    Redis工具类
    
    提供便捷的Redis操作方法，封装连接管理和错误处理。
    """
    
    def __init__(self, config: RedisConfig):
        """
        初始化Redis工具
        
        Args:
            config: Redis配置对象
        """
        self.connection_manager = RedisConnectionManager(config)
        logger.info("RedisHelper initialized")
    
    def ping(self) -> bool:
        """
        Ping Redis服务器
        
        Returns:
            是否连接正常
        """
        try:
            return self.connection_manager.execute_with_retry(
                lambda client: client.ping()
            )
        except RedisConnectionError:
            return False
    
    def set(self, key: str, value: Union[str, bytes], ex: Optional[int] = None) -> bool:
        """
        设置键值对
        
        Args:
            key: 键
            value: 值
            ex: 过期时间（秒）
            
        Returns:
            是否成功
        """
        try:
            return self.connection_manager.execute_with_retry(
                lambda client: client.set(key, value, ex=ex)
            )
        except RedisConnectionError as e:
            logger.error(f"Failed to set key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[str]:
        """
        获取值
        
        Args:
            key: 键
            
        Returns:
            值，如果键不存在返回None
        """
        try:
            return self.connection_manager.execute_with_retry(
                lambda client: client.get(key)
            )
        except RedisConnectionError as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        删除键
        
        Args:
            key: 键
            
        Returns:
            是否成功
        """
        try:
            result = self.connection_manager.execute_with_retry(
                lambda client: client.delete(key)
            )
            return result > 0
        except RedisConnectionError as e:
            logger.error(f"Failed to delete key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 键
            
        Returns:
            是否存在
        """
        try:
            result = self.connection_manager.execute_with_retry(
                lambda client: client.exists(key)
            )
            return result > 0
        except RedisConnectionError as e:
            logger.error(f"Failed to check existence of key {key}: {e}")
            return False
    
    def expire(self, key: str, time: int) -> bool:
        """
        设置键的过期时间
        
        Args:
            key: 键
            time: 过期时间（秒）
            
        Returns:
            是否成功
        """
        try:
            return self.connection_manager.execute_with_retry(
                lambda client: client.expire(key, time)
            )
        except RedisConnectionError as e:
            logger.error(f"Failed to set expiry for key {key}: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """
        获取键的剩余生存时间
        
        Args:
            key: 键
            
        Returns:
            剩余生存时间（秒），-1表示永不过期，-2表示键不存在
        """
        try:
            return self.connection_manager.execute_with_retry(
                lambda client: client.ttl(key)
            )
        except RedisConnectionError as e:
            logger.error(f"Failed to get TTL for key {key}: {e}")
            return -2
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            连接是否健康
        """
        return self.connection_manager.health_check()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """获取连接信息"""
        return self.connection_manager.get_connection_info()
    
    def close(self) -> None:
        """关闭连接"""
        self.connection_manager.close()


# 全局Redis工具实例
_redis_helper: Optional[RedisHelper] = None


def get_redis_helper(config: RedisConfig) -> RedisHelper:
    """
    获取Redis工具实例
    
    Args:
        config: Redis配置对象
        
    Returns:
        Redis工具实例
    """
    global _redis_helper
    if _redis_helper is None:
        _redis_helper = RedisHelper(config)
    return _redis_helper


def close_redis_helper() -> None:
    """关闭Redis工具连接"""
    global _redis_helper
    if _redis_helper:
        _redis_helper.close()
        _redis_helper = None
