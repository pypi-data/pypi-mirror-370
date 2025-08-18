"""
任务调度器模块

实现任务调度器，支持定时任务、周期性任务和条件触发任务。
严格遵循苹果产品原则：高内聚、低耦合、简洁接口。
"""

import time
import threading
import asyncio
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from croniter import croniter
from loguru import logger

from ..core.config import TaskManagerConfig
from ..manager.task_manager import get_task_manager
from ..manager.priority_manager import get_priority_manager, TaskPriority
from ..utils.redis_helper import get_redis_helper


class ScheduleType(str, Enum):
    """调度类型枚举"""
    ONCE = "once"              # 一次性任务
    INTERVAL = "interval"       # 间隔任务
    CRON = "cron"              # Cron表达式任务
    CONDITIONAL = "conditional"  # 条件触发任务


class ScheduleStatus(str, Enum):
    """调度状态枚举"""
    ACTIVE = "active"      # 活跃
    PAUSED = "paused"      # 暂停
    COMPLETED = "completed"  # 完成
    FAILED = "failed"      # 失败


@dataclass
class ScheduleConfig:
    """调度配置"""
    schedule_type: ScheduleType
    schedule_id: str
    task_type: str
    input_data: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 一次性任务配置
    execute_at: Optional[datetime] = None
    
    # 间隔任务配置
    interval_seconds: Optional[int] = None
    max_executions: Optional[int] = None
    
    # Cron任务配置
    cron_expression: Optional[str] = None
    
    # 条件任务配置
    condition_func: Optional[Callable] = None
    check_interval: Optional[int] = 60  # 检查间隔（秒）
    
    # 通用配置
    enabled: bool = True
    retry_on_failure: bool = True
    max_retries: int = 3
    retry_delay: int = 300  # 重试延迟（秒）


@dataclass
class ScheduleInfo:
    """调度信息"""
    schedule_id: str
    config: ScheduleConfig
    status: ScheduleStatus = ScheduleStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    last_execution: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    execution_count: int = 0
    failure_count: int = 0
    last_error: Optional[str] = None
    
    def is_due(self) -> bool:
        """检查是否到期执行"""
        if not self.config.enabled or self.status != ScheduleStatus.ACTIVE:
            return False
        
        if self.next_execution is None:
            return False
        
        return datetime.now() >= self.next_execution
    
    def calculate_next_execution(self) -> Optional[datetime]:
        """计算下次执行时间"""
        if self.config.schedule_type == ScheduleType.ONCE:
            return self.config.execute_at
        
        elif self.config.schedule_type == ScheduleType.INTERVAL:
            if self.last_execution is None:
                return datetime.now()
            return self.last_execution + timedelta(seconds=self.config.interval_seconds)
        
        elif self.config.schedule_type == ScheduleType.CRON:
            if self.last_execution is None:
                cron = croniter(self.config.cron_expression, datetime.now())
                return cron.get_next(datetime)
            else:
                cron = croniter(self.config.cron_expression, self.last_execution)
                return cron.get_next(datetime)
        
        elif self.config.schedule_type == ScheduleType.CONDITIONAL:
            # 条件任务需要定期检查
            return datetime.now() + timedelta(seconds=self.config.check_interval)
        
        return None
    
    def should_stop(self) -> bool:
        """检查是否应该停止"""
        if self.config.schedule_type == ScheduleType.ONCE:
            return self.execution_count >= 1
        
        elif self.config.schedule_type == ScheduleType.INTERVAL:
            if self.config.max_executions and self.execution_count >= self.config.max_executions:
                return True
        
        return False


class TaskScheduler:
    """
    任务调度器
    
    管理定时任务、周期性任务和条件触发任务的调度。
    """
    
    def __init__(self, config: TaskManagerConfig):
        """
        初始化任务调度器
        
        Args:
            config: 任务管理器配置
        """
        self.config = config
        self.redis_helper = get_redis_helper(config.redis)
        self.task_manager = get_task_manager(config)
        self.priority_manager = get_priority_manager(config)
        
        # 调度存储
        self.schedules: Dict[str, ScheduleInfo] = {}
        
        # 调度线程
        self.scheduler_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Redis键前缀
        self.schedule_prefix = "taskmanager_hjy:schedule:"
        
        self.logger = logger.bind(component="task_scheduler")
        self.logger.info("TaskScheduler initialized")
    
    def add_schedule(self, schedule_config: ScheduleConfig) -> bool:
        """
        添加调度任务
        
        Args:
            schedule_config: 调度配置
            
        Returns:
            是否成功添加
        """
        try:
            # 创建调度信息
            schedule_info = ScheduleInfo(
                schedule_id=schedule_config.schedule_id,
                config=schedule_config
            )
            
            # 计算下次执行时间
            schedule_info.next_execution = schedule_info.calculate_next_execution()
            
            # 添加到调度器
            self.schedules[schedule_config.schedule_id] = schedule_info
            
            # 保存到Redis
            self._save_schedule(schedule_info)
            
            self.logger.info(f"Schedule {schedule_config.schedule_id} added")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add schedule {schedule_config.schedule_id}: {e}")
            return False
    
    def remove_schedule(self, schedule_id: str) -> bool:
        """
        移除调度任务
        
        Args:
            schedule_id: 调度ID
            
        Returns:
            是否成功移除
        """
        try:
            if schedule_id not in self.schedules:
                return False
            
            # 从调度器移除
            del self.schedules[schedule_id]
            
            # 从Redis移除
            self._remove_schedule(schedule_id)
            
            self.logger.info(f"Schedule {schedule_id} removed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove schedule {schedule_id}: {e}")
            return False
    
    def pause_schedule(self, schedule_id: str) -> bool:
        """
        暂停调度任务
        
        Args:
            schedule_id: 调度ID
            
        Returns:
            是否成功暂停
        """
        try:
            if schedule_id not in self.schedules:
                return False
            
            schedule_info = self.schedules[schedule_id]
            schedule_info.status = ScheduleStatus.PAUSED
            
            # 更新Redis
            self._save_schedule(schedule_info)
            
            self.logger.info(f"Schedule {schedule_id} paused")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pause schedule {schedule_id}: {e}")
            return False
    
    def resume_schedule(self, schedule_id: str) -> bool:
        """
        恢复调度任务
        
        Args:
            schedule_id: 调度ID
            
        Returns:
            是否成功恢复
        """
        try:
            if schedule_id not in self.schedules:
                return False
            
            schedule_info = self.schedules[schedule_id]
            schedule_info.status = ScheduleStatus.ACTIVE
            
            # 重新计算下次执行时间
            schedule_info.next_execution = schedule_info.calculate_next_execution()
            
            # 更新Redis
            self._save_schedule(schedule_info)
            
            self.logger.info(f"Schedule {schedule_id} resumed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resume schedule {schedule_id}: {e}")
            return False
    
    def update_schedule(self, schedule_id: str, **kwargs) -> bool:
        """
        更新调度配置
        
        Args:
            schedule_id: 调度ID
            **kwargs: 更新的配置参数
            
        Returns:
            是否成功更新
        """
        try:
            if schedule_id not in self.schedules:
                return False
            
            schedule_info = self.schedules[schedule_id]
            
            # 更新配置
            for key, value in kwargs.items():
                if hasattr(schedule_info.config, key):
                    setattr(schedule_info.config, key, value)
            
            # 重新计算下次执行时间
            schedule_info.next_execution = schedule_info.calculate_next_execution()
            
            # 更新Redis
            self._save_schedule(schedule_info)
            
            self.logger.info(f"Schedule {schedule_id} updated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update schedule {schedule_id}: {e}")
            return False
    
    def get_schedule(self, schedule_id: str) -> Optional[ScheduleInfo]:
        """
        获取调度信息
        
        Args:
            schedule_id: 调度ID
            
        Returns:
            调度信息
        """
        return self.schedules.get(schedule_id)
    
    def get_all_schedules(self) -> List[ScheduleInfo]:
        """
        获取所有调度信息
        
        Returns:
            调度信息列表
        """
        return list(self.schedules.values())
    
    def get_active_schedules(self) -> List[ScheduleInfo]:
        """
        获取活跃的调度信息
        
        Returns:
            活跃的调度信息列表
        """
        return [s for s in self.schedules.values() if s.status == ScheduleStatus.ACTIVE]
    
    def get_due_schedules(self) -> List[ScheduleInfo]:
        """
        获取到期的调度信息
        
        Returns:
            到期的调度信息列表
        """
        return [s for s in self.schedules.values() if s.is_due()]
    
    def execute_schedule(self, schedule_info: ScheduleInfo) -> bool:
        """
        执行调度任务
        
        Args:
            schedule_info: 调度信息
            
        Returns:
            是否成功执行
        """
        try:
            # 检查条件任务
            if schedule_info.config.schedule_type == ScheduleType.CONDITIONAL:
                if not self._check_condition(schedule_info):
                    return True  # 条件不满足，不算失败
            
            # 创建任务
            task_id = self.task_manager.create_task(
                task_type=schedule_info.config.task_type,
                input_data=schedule_info.config.input_data,
                user_id=schedule_info.config.user_id,
                metadata={
                    **schedule_info.config.metadata,
                    "schedule_id": schedule_info.schedule_id,
                    "scheduled_execution": True
                }
            )
            
            # 添加到优先级队列
            self.priority_manager.add_task(
                task_id=task_id,
                priority=schedule_info.config.priority,
                user_id=schedule_info.config.user_id,
                task_type=schedule_info.config.task_type,
                metadata=schedule_info.config.metadata
            )
            
            # 更新调度信息
            schedule_info.last_execution = datetime.now()
            schedule_info.execution_count += 1
            schedule_info.next_execution = schedule_info.calculate_next_execution()
            
            # 检查是否应该停止
            if schedule_info.should_stop():
                schedule_info.status = ScheduleStatus.COMPLETED
            
            # 更新Redis
            self._save_schedule(schedule_info)
            
            self.logger.info(f"Schedule {schedule_info.schedule_id} executed, task {task_id} created")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to execute schedule {schedule_info.schedule_id}: {e}")
            
            # 更新失败信息
            schedule_info.failure_count += 1
            schedule_info.last_error = str(e)
            
            # 检查重试
            if (schedule_info.config.retry_on_failure and 
                schedule_info.failure_count < schedule_info.config.max_retries):
                # 设置重试时间
                schedule_info.next_execution = datetime.now() + timedelta(seconds=schedule_info.config.retry_delay)
            else:
                schedule_info.status = ScheduleStatus.FAILED
            
            # 更新Redis
            self._save_schedule(schedule_info)
            return False
    
    def start(self) -> None:
        """启动调度器"""
        if self.running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("TaskScheduler started")
    
    def stop(self) -> None:
        """停止调度器"""
        if not self.running:
            return
        
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("TaskScheduler stopped")
    
    def _scheduler_loop(self) -> None:
        """调度器主循环"""
        while self.running:
            try:
                # 获取到期的调度
                due_schedules = self.get_due_schedules()
                
                # 执行到期的调度
                for schedule_info in due_schedules:
                    self.execute_schedule(schedule_info)
                
                # 休眠一段时间
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(5)  # 出错时等待更长时间
    
    def _check_condition(self, schedule_info: ScheduleInfo) -> bool:
        """
        检查条件任务的条件
        
        Args:
            schedule_info: 调度信息
            
        Returns:
            条件是否满足
        """
        try:
            if schedule_info.config.condition_func and callable(schedule_info.config.condition_func):
                return schedule_info.config.condition_func()
            return False
        except Exception as e:
            self.logger.error(f"Error checking condition for schedule {schedule_info.schedule_id}: {e}")
            return False
    
    def _save_schedule(self, schedule_info: ScheduleInfo) -> None:
        """保存调度信息到Redis"""
        try:
            key = f"{self.schedule_prefix}{schedule_info.schedule_id}"
            data = {
                "schedule_id": schedule_info.schedule_id,
                "schedule_type": schedule_info.config.schedule_type.value,
                "task_type": schedule_info.config.task_type,
                "status": schedule_info.status.value,
                "created_at": schedule_info.created_at.isoformat(),
                "last_execution": schedule_info.last_execution.isoformat() if schedule_info.last_execution else None,
                "next_execution": schedule_info.next_execution.isoformat() if schedule_info.next_execution else None,
                "execution_count": schedule_info.execution_count,
                "failure_count": schedule_info.failure_count,
                "last_error": schedule_info.last_error
            }
            
            self.redis_helper.set(key, str(data), ex=86400)  # 24小时过期
            
        except Exception as e:
            self.logger.error(f"Failed to save schedule: {e}")
    
    def _remove_schedule(self, schedule_id: str) -> None:
        """从Redis移除调度信息"""
        try:
            key = f"{self.schedule_prefix}{schedule_id}"
            self.redis_helper.delete(key)
            
        except Exception as e:
            self.logger.error(f"Failed to remove schedule: {e}")
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """
        获取调度器统计信息
        
        Returns:
            统计信息
        """
        try:
            all_schedules = self.get_all_schedules()
            active_schedules = self.get_active_schedules()
            due_schedules = self.get_due_schedules()
            
            stats = {
                "total_schedules": len(all_schedules),
                "active_schedules": len(active_schedules),
                "due_schedules": len(due_schedules),
                "scheduler_running": self.running,
                "schedule_types": {},
                "status_distribution": {}
            }
            
            # 按类型统计
            for schedule in all_schedules:
                schedule_type = schedule.config.schedule_type.value
                stats["schedule_types"][schedule_type] = stats["schedule_types"].get(schedule_type, 0) + 1
            
            # 按状态统计
            for schedule in all_schedules:
                status = schedule.status.value
                stats["status_distribution"][status] = stats["status_distribution"].get(status, 0) + 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get scheduler stats: {e}")
            return {}
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            # 检查Redis连接
            if not self.redis_helper.health_check():
                return False
            
            # 检查调度器状态
            if self.running and not self.scheduler_thread.is_alive():
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Scheduler health check failed: {e}")
            return False


# 全局调度器实例
_scheduler: Optional[TaskScheduler] = None


def get_scheduler(config: TaskManagerConfig) -> TaskScheduler:
    """
    获取调度器实例
    
    Args:
        config: 任务管理器配置
        
    Returns:
        调度器实例
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler(config)
    return _scheduler


def close_scheduler() -> None:
    """关闭调度器"""
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None


# 便捷函数
def schedule_once(schedule_id: str, task_type: str, input_data: Dict[str, Any],
                 execute_at: datetime, priority: TaskPriority = TaskPriority.NORMAL,
                 user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """
    调度一次性任务
    
    Args:
        schedule_id: 调度ID
        task_type: 任务类型
        input_data: 输入数据
        execute_at: 执行时间
        priority: 优先级
        user_id: 用户ID
        metadata: 元数据
        
    Returns:
        是否成功调度
    """
    config = ScheduleConfig(
        schedule_type=ScheduleType.ONCE,
        schedule_id=schedule_id,
        task_type=task_type,
        input_data=input_data,
        priority=priority,
        user_id=user_id,
        metadata=metadata or {},
        execute_at=execute_at
    )
    
    scheduler = get_scheduler(get_config())
    return scheduler.add_schedule(config)


def schedule_interval(schedule_id: str, task_type: str, input_data: Dict[str, Any],
                     interval_seconds: int, max_executions: Optional[int] = None,
                     priority: TaskPriority = TaskPriority.NORMAL,
                     user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """
    调度间隔任务
    
    Args:
        schedule_id: 调度ID
        task_type: 任务类型
        input_data: 输入数据
        interval_seconds: 间隔秒数
        max_executions: 最大执行次数
        priority: 优先级
        user_id: 用户ID
        metadata: 元数据
        
    Returns:
        是否成功调度
    """
    config = ScheduleConfig(
        schedule_type=ScheduleType.INTERVAL,
        schedule_id=schedule_id,
        task_type=task_type,
        input_data=input_data,
        priority=priority,
        user_id=user_id,
        metadata=metadata or {},
        interval_seconds=interval_seconds,
        max_executions=max_executions
    )
    
    scheduler = get_scheduler(get_config())
    return scheduler.add_schedule(config)


def schedule_cron(schedule_id: str, task_type: str, input_data: Dict[str, Any],
                 cron_expression: str, priority: TaskPriority = TaskPriority.NORMAL,
                 user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """
    调度Cron任务
    
    Args:
        schedule_id: 调度ID
        task_type: 任务类型
        input_data: 输入数据
        cron_expression: Cron表达式
        priority: 优先级
        user_id: 用户ID
        metadata: 元数据
        
    Returns:
        是否成功调度
    """
    config = ScheduleConfig(
        schedule_type=ScheduleType.CRON,
        schedule_id=schedule_id,
        task_type=task_type,
        input_data=input_data,
        priority=priority,
        user_id=user_id,
        metadata=metadata or {},
        cron_expression=cron_expression
    )
    
    scheduler = get_scheduler(get_config())
    return scheduler.add_schedule(config)
