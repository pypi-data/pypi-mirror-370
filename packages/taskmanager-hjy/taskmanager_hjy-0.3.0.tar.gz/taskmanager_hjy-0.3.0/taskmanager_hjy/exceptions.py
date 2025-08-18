"""
taskmanager_hjy 异常定义

提供优雅的、人类可读的错误信息。
"""

from typing import Optional, Any, Dict


class TaskManagerError(Exception):
    """任务管理器基础异常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        return f"TaskManagerError: {self.message}"


class ConfigurationError(TaskManagerError):
    """配置错误"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message)
        self.config_key = config_key
    
    def __str__(self) -> str:
        if self.config_key:
            return f"ConfigurationError: {self.message} (key: {self.config_key})"
        return f"ConfigurationError: {self.message}"


class RedisConnectionError(TaskManagerError):
    """Redis连接错误"""
    
    def __init__(self, message: str, redis_url: Optional[str] = None):
        super().__init__(message)
        self.redis_url = redis_url
    
    def __str__(self) -> str:
        if self.redis_url:
            return f"RedisConnectionError: {self.message} (URL: {self.redis_url})"
        return f"RedisConnectionError: {self.message}"


class TaskNotFoundError(TaskManagerError):
    """任务未找到错误"""
    
    def __init__(self, task_id: str):
        super().__init__(f"Task not found: {task_id}")
        self.task_id = task_id
    
    def __str__(self) -> str:
        return f"TaskNotFoundError: Task '{self.task_id}' not found"


class TaskValidationError(TaskManagerError):
    """任务验证错误"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        super().__init__(message)
        self.field = field
        self.value = value
    
    def __str__(self) -> str:
        if self.field and self.value:
            return f"TaskValidationError: {self.message} (field: {self.field}, value: {self.value})"
        elif self.field:
            return f"TaskValidationError: {self.message} (field: {self.field})"
        return f"TaskValidationError: {self.message}"


class TaskExecutionError(TaskManagerError):
    """任务执行错误"""
    
    def __init__(self, message: str, task_id: Optional[str] = None, task_type: Optional[str] = None):
        super().__init__(message)
        self.task_id = task_id
        self.task_type = task_type
    
    def __str__(self) -> str:
        details = []
        if self.task_id:
            details.append(f"task_id: {self.task_id}")
        if self.task_type:
            details.append(f"task_type: {self.task_type}")
        
        if details:
            return f"TaskExecutionError: {self.message} ({', '.join(details)})"
        return f"TaskExecutionError: {self.message}"


class AIServiceError(TaskManagerError):
    """AI服务错误"""
    
    def __init__(self, message: str, service_name: Optional[str] = None, route: Optional[str] = None):
        super().__init__(message)
        self.service_name = service_name
        self.route = route
    
    def __str__(self) -> str:
        details = []
        if self.service_name:
            details.append(f"service: {self.service_name}")
        if self.route:
            details.append(f"route: {self.route}")
        
        if details:
            return f"AIServiceError: {self.message} ({', '.join(details)})"
        return f"AIServiceError: {self.message}"


class QueueError(TaskManagerError):
    """队列操作错误"""
    
    def __init__(self, message: str, queue_name: Optional[str] = None, operation: Optional[str] = None):
        super().__init__(message)
        self.queue_name = queue_name
        self.operation = operation
    
    def __str__(self) -> str:
        details = []
        if self.queue_name:
            details.append(f"queue: {self.queue_name}")
        if self.operation:
            details.append(f"operation: {self.operation}")
        
        if details:
            return f"QueueError: {self.message} ({', '.join(details)})"
        return f"QueueError: {self.message}"


class PermissionError(TaskManagerError):
    """权限错误"""
    
    def __init__(self, message: str, user_id: Optional[str] = None, resource: Optional[str] = None):
        super().__init__(message)
        self.user_id = user_id
        self.resource = resource
    
    def __str__(self) -> str:
        details = []
        if self.user_id:
            details.append(f"user_id: {self.user_id}")
        if self.resource:
            details.append(f"resource: {self.resource}")
        
        if details:
            return f"PermissionError: {self.message} ({', '.join(details)})"
        return f"PermissionError: {self.message}"


# 便捷的错误创建函数
def create_validation_error(field: str, message: str, value: Optional[Any] = None) -> TaskValidationError:
    """创建验证错误"""
    return TaskValidationError(message, field, value)


def create_task_not_found_error(task_id: str) -> TaskNotFoundError:
    """创建任务未找到错误"""
    return TaskNotFoundError(task_id)


def create_redis_connection_error(message: str, redis_url: Optional[str] = None) -> RedisConnectionError:
    """创建Redis连接错误"""
    return RedisConnectionError(message, redis_url)


def create_ai_service_error(message: str, service_name: Optional[str] = None, route: Optional[str] = None) -> AIServiceError:
    """创建AI服务错误"""
    return AIServiceError(message, service_name, route)
