"""
基础任务类型模块

提供BaseTask基类和AITask基类，定义任务的基本接口和行为。
严格遵循苹果产品原则：高内聚、低耦合、简洁接口。
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger

from ..core.config import TaskManagerConfig


class TaskType(str, Enum):
    """任务类型枚举"""
    BASE = "base"
    AI = "ai"
    AUDIO_ANALYSIS = "audio_analysis"
    TEXT_ANALYSIS = "text_analysis"
    IMAGE_ANALYSIS = "image_analysis"
    CUSTOM = "custom"


class TaskPriority(int, Enum):
    """任务优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class TaskContext:
    """任务执行上下文"""
    task_id: str
    task_type: str
    config: TaskManagerConfig
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = time.time()
    
    def mark_completed(self):
        """标记任务完成"""
        self.end_time = time.time()
    
    def get_execution_time(self) -> Optional[float]:
        """获取执行时间"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class TaskError(Exception):
    """任务执行错误"""
    def __init__(self, message: str, task_id: str = None, retryable: bool = True):
        super().__init__(message)
        self.task_id = task_id
        self.retryable = retryable


class ValidationError(TaskError):
    """输入验证错误"""
    def __init__(self, message: str, task_id: str = None):
        super().__init__(message, task_id, retryable=False)


class BaseTask(ABC):
    """
    任务基类
    
    定义任务的基本接口和行为。
    所有任务类型都应该继承此类。
    """
    
    def __init__(self, config: TaskManagerConfig, task_type: str = TaskType.BASE):
        """
        初始化基础任务
        
        Args:
            config: 任务管理器配置
            task_type: 任务类型
        """
        self.config = config
        self.task_type = task_type
        self.logger = logger.bind(task_type=task_type)
        
        self.logger.info(f"BaseTask initialized for type: {task_type}")
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            是否有效
            
        Raises:
            ValidationError: 输入数据无效时抛出
        """
        pass
    
    @abstractmethod
    def execute(self, context: TaskContext, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务
        
        Args:
            context: 任务执行上下文
            input_data: 输入数据
            
        Returns:
            执行结果
            
        Raises:
            TaskError: 任务执行失败时抛出
        """
        pass
    
    def pre_execute(self, context: TaskContext, input_data: Dict[str, Any]) -> None:
        """
        任务执行前的准备工作
        
        Args:
            context: 任务执行上下文
            input_data: 输入数据
        """
        self.logger.info(f"Pre-executing task {context.task_id}")
        # 子类可以重写此方法进行预处理
    
    def post_execute(self, context: TaskContext, result: Dict[str, Any]) -> None:
        """
        任务执行后的清理工作
        
        Args:
            context: 任务执行上下文
            result: 执行结果
        """
        self.logger.info(f"Post-executing task {context.task_id}")
        context.mark_completed()
        # 子类可以重写此方法进行后处理
    
    def cleanup(self, context: TaskContext) -> None:
        """
        清理资源
        
        Args:
            context: 任务执行上下文
        """
        self.logger.info(f"Cleaning up task {context.task_id}")
        # 子类可以重写此方法进行资源清理
    
    def should_retry(self, context: TaskContext, error: TaskError) -> bool:
        """
        判断是否应该重试
        
        Args:
            context: 任务执行上下文
            error: 执行错误
            
        Returns:
            是否应该重试
        """
        if not error.retryable:
            return False
        
        if context.retry_count >= context.max_retries:
            return False
        
        return True
    
    def get_retry_delay(self, context: TaskContext) -> float:
        """
        获取重试延迟时间
        
        Args:
            context: 任务执行上下文
            
        Returns:
            重试延迟时间（秒）
        """
        # 指数退避策略
        base_delay = self.config.rq.retry_delay
        return base_delay * (2 ** context.retry_count)
    
    def run(self, task_id: str, input_data: Dict[str, Any], 
           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        运行任务
        
        Args:
            task_id: 任务ID
            input_data: 输入数据
            metadata: 元数据
            
        Returns:
            执行结果
            
        Raises:
            ValidationError: 输入验证失败
            TaskError: 任务执行失败
        """
        # 创建执行上下文
        context = TaskContext(
            task_id=task_id,
            task_type=self.task_type,
            config=self.config,
            metadata=metadata or {}
        )
        
        try:
            # 验证输入
            if not self.validate_input(input_data):
                raise ValidationError("Input validation failed", task_id)
            
            # 预处理
            self.pre_execute(context, input_data)
            
            # 执行任务
            result = self.execute(context, input_data)
            
            # 后处理
            self.post_execute(context, result)
            
            # 添加执行时间到结果
            execution_time = context.get_execution_time()
            if execution_time:
                result["execution_time"] = execution_time
            
            self.logger.info(f"Task {task_id} completed successfully in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Task {task_id} failed: {e}")
            
            # 判断是否应该重试
            if isinstance(e, TaskError) and self.should_retry(context, e):
                retry_delay = self.get_retry_delay(context)
                self.logger.info(f"Task {task_id} will be retried in {retry_delay}s")
                raise e
            else:
                # 清理资源
                self.cleanup(context)
                raise e


class AITask(BaseTask):
    """
    AI任务基类
    
    专门用于AI相关任务的基类。
    提供AI服务集成和错误处理。
    """
    
    def __init__(self, config: TaskManagerConfig, task_type: str = TaskType.AI):
        """
        初始化AI任务
        
        Args:
            config: 任务管理器配置
            task_type: 任务类型
        """
        super().__init__(config, task_type)
        self.ai_config = config.ai_service
        
        self.logger.info(f"AITask initialized for type: {task_type}")
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证AI任务输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            是否有效
        """
        # 基本验证：检查必要字段
        required_fields = self.get_required_fields()
        for field in required_fields:
            if field not in input_data:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        # 子类可以重写此方法进行更详细的验证
        return True
    
    def get_required_fields(self) -> List[str]:
        """
        获取必需的输入字段
        
        Returns:
            必需字段列表
        """
        return ["input"]  # 默认只需要input字段
    
    def call_ai_service(self, route: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用AI服务
        
        Args:
            route: AI服务路由
            input_data: 输入数据
            
        Returns:
            AI服务响应
            
        Raises:
            TaskError: AI服务调用失败时抛出
        """
        try:
            # 这里应该调用ai_runner_hjy.run_route()
            # 暂时使用模拟实现
            self.logger.info(f"Calling AI service route: {route}")
            
            # 模拟AI服务调用
            import random
            time.sleep(random.uniform(0.1, 0.5))  # 模拟网络延迟
            
            # 模拟成功响应
            return {
                "success": True,
                "route": route,
                "result": f"AI analysis result for {route}",
                "confidence": random.uniform(0.7, 0.95)
            }
            
        except Exception as e:
            self.logger.error(f"AI service call failed: {e}")
            raise TaskError(f"AI service call failed: {e}")
    
    def handle_ai_error(self, error: Exception, context: TaskContext) -> Dict[str, Any]:
        """
        处理AI服务错误
        
        Args:
            error: 错误信息
            context: 任务执行上下文
            
        Returns:
            错误处理结果
        """
        self.logger.warning(f"Handling AI error for task {context.task_id}: {error}")
        
        # 返回默认结果
        return {
            "success": False,
            "error": str(error),
            "fallback_result": "Default analysis result due to AI service error",
            "confidence": 0.5
        }
    
    def execute(self, context: TaskContext, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行AI任务
        
        Args:
            context: 任务执行上下文
            input_data: 输入数据
            
        Returns:
            执行结果
        """
        try:
            # 获取AI服务路由
            route = self.get_ai_route(input_data)
            
            # 调用AI服务
            ai_result = self.call_ai_service(route, input_data)
            
            # 处理AI服务结果
            result = self.process_ai_result(ai_result, input_data)
            
            return result
            
        except Exception as e:
            # 处理AI服务错误
            return self.handle_ai_error(e, context)
    
    def get_ai_route(self, input_data: Dict[str, Any]) -> str:
        """
        获取AI服务路由
        
        Args:
            input_data: 输入数据
            
        Returns:
            AI服务路由
        """
        # 子类应该重写此方法
        return "ai.default"
    
    def process_ai_result(self, ai_result: Dict[str, Any], 
                         input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理AI服务结果
        
        Args:
            ai_result: AI服务结果
            input_data: 原始输入数据
            
        Returns:
            处理后的结果
        """
        # 子类可以重写此方法进行结果处理
        return {
            "success": ai_result.get("success", False),
            "result": ai_result.get("result", ""),
            "confidence": ai_result.get("confidence", 0.0),
            "input_data": input_data
        }


class SimpleTask(BaseTask):
    """
    简单任务实现
    
    用于测试和演示的简单任务。
    """
    
    def __init__(self, config: TaskManagerConfig):
        super().__init__(config, TaskType.BASE)
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        return "message" in input_data
    
    def execute(self, context: TaskContext, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行简单任务"""
        message = input_data.get("message", "")
        
        # 模拟处理时间
        import time
        time.sleep(0.1)
        
        return {
            "success": True,
            "message": f"Processed: {message}",
            "task_id": context.task_id,
            "timestamp": time.time()
        }


# 任务工厂
class TaskFactory:
    """任务工厂类"""
    
    _task_registry: Dict[str, type] = {}
    
    @classmethod
    def register(cls, task_type: str, task_class: type):
        """注册任务类型"""
        cls._task_registry[task_type] = task_class
        logger.info(f"Registered task type: {task_type}")
    
    @classmethod
    def create(cls, task_type: str, config: TaskManagerConfig) -> BaseTask:
        """创建任务实例"""
        if task_type not in cls._task_registry:
            raise ValueError(f"Unknown task type: {task_type}")
        
        task_class = cls._task_registry[task_type]
        return task_class(config)
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        """获取可用的任务类型"""
        return list(cls._task_registry.keys())


# 注册默认任务类型
TaskFactory.register(TaskType.BASE, SimpleTask)
