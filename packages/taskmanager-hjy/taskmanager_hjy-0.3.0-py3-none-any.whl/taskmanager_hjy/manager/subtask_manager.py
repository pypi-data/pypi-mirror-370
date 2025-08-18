"""
子任务管理器模块

实现子任务管理和依赖关系处理，支持并行和串行执行。
严格遵循苹果产品原则：高内聚、低耦合、简洁接口。
"""

import time
import asyncio
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger

from ..core.config import TaskManagerConfig
from ..manager.task_manager import TaskStatus, TaskInfo
from ..utils.redis_helper import get_redis_helper


class DependencyType(str, Enum):
    """依赖类型枚举"""
    SEQUENTIAL = "sequential"  # 串行依赖
    PARALLEL = "parallel"      # 并行依赖
    CONDITIONAL = "conditional"  # 条件依赖


class SubTaskStatus(str, Enum):
    """子任务状态枚举"""
    PENDING = "pending"      # 等待中
    READY = "ready"          # 准备就绪
    RUNNING = "running"      # 运行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    SKIPPED = "skipped"      # 跳过


@dataclass
class SubTask:
    """子任务"""
    task_id: str
    parent_task_id: str
    task_type: str
    input_data: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    dependency_type: DependencyType = DependencyType.SEQUENTIAL
    status: SubTaskStatus = SubTaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_ready(self, completed_dependencies: Set[str]) -> bool:
        """
        检查子任务是否准备就绪
        
        Args:
            completed_dependencies: 已完成的依赖任务集合
            
        Returns:
            是否准备就绪
        """
        if not self.dependencies:
            return True
        
        if self.dependency_type == DependencyType.SEQUENTIAL:
            # 串行依赖：所有依赖都必须完成
            return all(dep in completed_dependencies for dep in self.dependencies)
        
        elif self.dependency_type == DependencyType.PARALLEL:
            # 并行依赖：至少一个依赖完成
            return any(dep in completed_dependencies for dep in self.dependencies)
        
        elif self.dependency_type == DependencyType.CONDITIONAL:
            # 条件依赖：根据条件判断
            condition = self.metadata.get('condition', 'all')
            if condition == 'all':
                return all(dep in completed_dependencies for dep in self.dependencies)
            elif condition == 'any':
                return any(dep in completed_dependencies for dep in self.dependencies)
            else:
                # 自定义条件
                return self._evaluate_custom_condition(completed_dependencies)
        
        return False
    
    def _evaluate_custom_condition(self, completed_dependencies: Set[str]) -> bool:
        """评估自定义条件"""
        condition_func = self.metadata.get('condition_func')
        if condition_func and callable(condition_func):
            return condition_func(completed_dependencies)
        return False
    
    def mark_started(self) -> None:
        """标记开始执行"""
        self.status = SubTaskStatus.RUNNING
        self.started_at = time.time()
    
    def mark_completed(self, result: Optional[Dict[str, Any]] = None) -> None:
        """标记完成"""
        self.status = SubTaskStatus.COMPLETED
        self.completed_at = time.time()
        self.result = result
    
    def mark_failed(self, error_message: str) -> None:
        """标记失败"""
        self.status = SubTaskStatus.FAILED
        self.completed_at = time.time()
        self.error_message = error_message
    
    def mark_skipped(self) -> None:
        """标记跳过"""
        self.status = SubTaskStatus.SKIPPED
        self.completed_at = time.time()


@dataclass
class ParentTask:
    """父任务"""
    task_id: str
    subtasks: Dict[str, SubTask] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    completed_subtasks: Set[str] = field(default_factory=set)
    failed_subtasks: Set[str] = field(default_factory=set)
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_subtask(self, subtask: SubTask) -> None:
        """添加子任务"""
        self.subtasks[subtask.task_id] = subtask
    
    def get_ready_subtasks(self) -> List[SubTask]:
        """获取准备就绪的子任务"""
        ready_subtasks = []
        for subtask in self.subtasks.values():
            if (subtask.status == SubTaskStatus.PENDING and 
                subtask.is_ready(self.completed_subtasks)):
                ready_subtasks.append(subtask)
        return ready_subtasks
    
    def update_subtask_status(self, subtask_id: str, status: SubTaskStatus, 
                            result: Optional[Dict[str, Any]] = None,
                            error_message: Optional[str] = None) -> None:
        """更新子任务状态"""
        if subtask_id not in self.subtasks:
            return
        
        subtask = self.subtasks[subtask_id]
        subtask.status = status
        
        if status == SubTaskStatus.COMPLETED:
            subtask.mark_completed(result)
            self.completed_subtasks.add(subtask_id)
        elif status == SubTaskStatus.FAILED:
            subtask.mark_failed(error_message or "Unknown error")
            self.failed_subtasks.add(subtask_id)
        elif status == SubTaskStatus.RUNNING:
            subtask.mark_started()
    
    def is_completed(self) -> bool:
        """检查父任务是否完成"""
        return len(self.completed_subtasks) == len(self.subtasks)
    
    def is_failed(self) -> bool:
        """检查父任务是否失败"""
        return len(self.failed_subtasks) > 0 and len(self.completed_subtasks) == 0
    
    def is_partially_completed(self) -> bool:
        """检查父任务是否部分完成"""
        return len(self.completed_subtasks) > 0 and len(self.failed_subtasks) > 0
    
    def get_completion_percentage(self) -> float:
        """获取完成百分比"""
        if not self.subtasks:
            return 100.0
        return (len(self.completed_subtasks) / len(self.subtasks)) * 100.0


class SubTaskManager:
    """
    子任务管理器
    
    管理子任务的创建、依赖关系、执行和状态同步。
    """
    
    def __init__(self, config: TaskManagerConfig):
        """
        初始化子任务管理器
        
        Args:
            config: 任务管理器配置
        """
        self.config = config
        self.redis_helper = get_redis_helper(config.redis)
        
        # 父任务存储
        self.parent_tasks: Dict[str, ParentTask] = {}
        
        # Redis键前缀
        self.parent_task_prefix = "taskmanager_hjy:parent_task:"
        self.subtask_prefix = "taskmanager_hjy:subtask:"
        
        self.logger = logger.bind(component="subtask_manager")
        self.logger.info("SubTaskManager initialized")
    
    def create_parent_task(self, task_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        创建父任务
        
        Args:
            task_id: 任务ID
            metadata: 元数据
            
        Returns:
            父任务ID
        """
        try:
            parent_task = ParentTask(
                task_id=task_id,
                metadata=metadata or {}
            )
            
            self.parent_tasks[task_id] = parent_task
            self._save_parent_task(parent_task)
            
            self.logger.info(f"Parent task {task_id} created")
            return task_id
            
        except Exception as e:
            self.logger.error(f"Failed to create parent task {task_id}: {e}")
            raise
    
    def add_subtask(self, parent_task_id: str, subtask_id: str, task_type: str,
                   input_data: Dict[str, Any], dependencies: Optional[List[str]] = None,
                   dependency_type: DependencyType = DependencyType.SEQUENTIAL,
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        添加子任务
        
        Args:
            parent_task_id: 父任务ID
            subtask_id: 子任务ID
            task_type: 任务类型
            input_data: 输入数据
            dependencies: 依赖任务列表
            dependency_type: 依赖类型
            metadata: 元数据
            
        Returns:
            是否成功添加
        """
        try:
            if parent_task_id not in self.parent_tasks:
                self.logger.error(f"Parent task {parent_task_id} not found")
                return False
            
            subtask = SubTask(
                task_id=subtask_id,
                parent_task_id=parent_task_id,
                task_type=task_type,
                input_data=input_data,
                dependencies=dependencies or [],
                dependency_type=dependency_type,
                metadata=metadata or {}
            )
            
            self.parent_tasks[parent_task_id].add_subtask(subtask)
            self._save_subtask(subtask)
            
            self.logger.info(f"Subtask {subtask_id} added to parent task {parent_task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add subtask {subtask_id}: {e}")
            return False
    
    def get_ready_subtasks(self, parent_task_id: str) -> List[SubTask]:
        """
        获取准备就绪的子任务
        
        Args:
            parent_task_id: 父任务ID
            
        Returns:
            准备就绪的子任务列表
        """
        try:
            if parent_task_id not in self.parent_tasks:
                return []
            
            parent_task = self.parent_tasks[parent_task_id]
            return parent_task.get_ready_subtasks()
            
        except Exception as e:
            self.logger.error(f"Failed to get ready subtasks: {e}")
            return []
    
    def update_subtask_status(self, parent_task_id: str, subtask_id: str,
                            status: SubTaskStatus, result: Optional[Dict[str, Any]] = None,
                            error_message: Optional[str] = None) -> bool:
        """
        更新子任务状态
        
        Args:
            parent_task_id: 父任务ID
            subtask_id: 子任务ID
            status: 新状态
            result: 执行结果
            error_message: 错误信息
            
        Returns:
            是否成功更新
        """
        try:
            if parent_task_id not in self.parent_tasks:
                return False
            
            parent_task = self.parent_tasks[parent_task_id]
            parent_task.update_subtask_status(subtask_id, status, result, error_message)
            
            # 更新Redis
            self._update_subtask_in_redis(parent_task_id, subtask_id, status, result, error_message)
            
            # 检查父任务状态
            self._update_parent_task_status(parent_task_id)
            
            self.logger.info(f"Subtask {subtask_id} status updated to {status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update subtask status: {e}")
            return False
    
    def get_parent_task_status(self, parent_task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取父任务状态
        
        Args:
            parent_task_id: 父任务ID
            
        Returns:
            父任务状态信息
        """
        try:
            if parent_task_id not in self.parent_tasks:
                return None
            
            parent_task = self.parent_tasks[parent_task_id]
            
            return {
                "task_id": parent_task_id,
                "status": parent_task.status.value,
                "total_subtasks": len(parent_task.subtasks),
                "completed_subtasks": len(parent_task.completed_subtasks),
                "failed_subtasks": len(parent_task.failed_subtasks),
                "completion_percentage": parent_task.get_completion_percentage(),
                "is_completed": parent_task.is_completed(),
                "is_failed": parent_task.is_failed(),
                "is_partially_completed": parent_task.is_partially_completed(),
                "created_at": parent_task.created_at,
                "started_at": parent_task.started_at,
                "completed_at": parent_task.completed_at
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get parent task status: {e}")
            return None
    
    def get_subtask_status(self, parent_task_id: str, subtask_id: str) -> Optional[Dict[str, Any]]:
        """
        获取子任务状态
        
        Args:
            parent_task_id: 父任务ID
            subtask_id: 子任务ID
            
        Returns:
            子任务状态信息
        """
        try:
            if parent_task_id not in self.parent_tasks:
                return None
            
            parent_task = self.parent_tasks[parent_task_id]
            if subtask_id not in parent_task.subtasks:
                return None
            
            subtask = parent_task.subtasks[subtask_id]
            
            return {
                "task_id": subtask_id,
                "parent_task_id": parent_task_id,
                "task_type": subtask.task_type,
                "status": subtask.status.value,
                "dependencies": subtask.dependencies,
                "dependency_type": subtask.dependency_type.value,
                "result": subtask.result,
                "error_message": subtask.error_message,
                "created_at": subtask.created_at,
                "started_at": subtask.started_at,
                "completed_at": subtask.completed_at,
                "retry_count": subtask.retry_count
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get subtask status: {e}")
            return None
    
    def execute_subtasks_parallel(self, parent_task_id: str, 
                                executor_func: Callable[[SubTask], Dict[str, Any]]) -> bool:
        """
        并行执行子任务
        
        Args:
            parent_task_id: 父任务ID
            executor_func: 执行函数
            
        Returns:
            是否成功执行
        """
        try:
            ready_subtasks = self.get_ready_subtasks(parent_task_id)
            if not ready_subtasks:
                return True
            
            # 创建异步任务
            async def execute_subtask(subtask: SubTask):
                try:
                    # 标记开始
                    self.update_subtask_status(parent_task_id, subtask.task_id, 
                                             SubTaskStatus.RUNNING)
                    
                    # 执行任务
                    result = executor_func(subtask)
                    
                    # 标记完成
                    self.update_subtask_status(parent_task_id, subtask.task_id,
                                             SubTaskStatus.COMPLETED, result)
                    
                except Exception as e:
                    # 标记失败
                    self.update_subtask_status(parent_task_id, subtask.task_id,
                                             SubTaskStatus.FAILED, error_message=str(e))
            
            # 并行执行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            tasks = [execute_subtask(subtask) for subtask in ready_subtasks]
            loop.run_until_complete(asyncio.gather(*tasks))
            loop.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to execute subtasks in parallel: {e}")
            return False
    
    def execute_subtasks_sequential(self, parent_task_id: str,
                                  executor_func: Callable[[SubTask], Dict[str, Any]]) -> bool:
        """
        串行执行子任务
        
        Args:
            parent_task_id: 父任务ID
            executor_func: 执行函数
            
        Returns:
            是否成功执行
        """
        try:
            while True:
                ready_subtasks = self.get_ready_subtasks(parent_task_id)
                if not ready_subtasks:
                    break
                
                # 串行执行每个准备就绪的子任务
                for subtask in ready_subtasks:
                    try:
                        # 标记开始
                        self.update_subtask_status(parent_task_id, subtask.task_id,
                                                 SubTaskStatus.RUNNING)
                        
                        # 执行任务
                        result = executor_func(subtask)
                        
                        # 标记完成
                        self.update_subtask_status(parent_task_id, subtask.task_id,
                                                 SubTaskStatus.COMPLETED, result)
                        
                    except Exception as e:
                        # 标记失败
                        self.update_subtask_status(parent_task_id, subtask.task_id,
                                                 SubTaskStatus.FAILED, error_message=str(e))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to execute subtasks sequentially: {e}")
            return False
    
    def retry_failed_subtask(self, parent_task_id: str, subtask_id: str,
                           executor_func: Callable[[SubTask], Dict[str, Any]]) -> bool:
        """
        重试失败的子任务
        
        Args:
            parent_task_id: 父任务ID
            subtask_id: 子任务ID
            executor_func: 执行函数
            
        Returns:
            是否成功重试
        """
        try:
            if parent_task_id not in self.parent_tasks:
                return False
            
            parent_task = self.parent_tasks[parent_task_id]
            if subtask_id not in parent_task.subtasks:
                return False
            
            subtask = parent_task.subtasks[subtask_id]
            if subtask.status != SubTaskStatus.FAILED:
                return False
            
            if subtask.retry_count >= subtask.max_retries:
                self.logger.warning(f"Subtask {subtask_id} has reached max retries")
                return False
            
            # 重置状态
            subtask.status = SubTaskStatus.PENDING
            subtask.retry_count += 1
            subtask.error_message = None
            subtask.started_at = None
            subtask.completed_at = None
            
            # 执行任务
            try:
                self.update_subtask_status(parent_task_id, subtask_id, SubTaskStatus.RUNNING)
                result = executor_func(subtask)
                self.update_subtask_status(parent_task_id, subtask_id, SubTaskStatus.COMPLETED, result)
                return True
                
            except Exception as e:
                self.update_subtask_status(parent_task_id, subtask_id, SubTaskStatus.FAILED, error_message=str(e))
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to retry subtask: {e}")
            return False
    
    def _update_parent_task_status(self, parent_task_id: str) -> None:
        """更新父任务状态"""
        try:
            if parent_task_id not in self.parent_tasks:
                return
            
            parent_task = self.parent_tasks[parent_task_id]
            
            if parent_task.is_completed():
                parent_task.status = TaskStatus.FINISHED
                parent_task.completed_at = time.time()
            elif parent_task.is_failed():
                parent_task.status = TaskStatus.FAILED
                parent_task.completed_at = time.time()
            elif parent_task.is_partially_completed():
                parent_task.status = TaskStatus.STARTED
                if not parent_task.started_at:
                    parent_task.started_at = time.time()
            
            # 更新Redis
            self._save_parent_task(parent_task)
            
        except Exception as e:
            self.logger.error(f"Failed to update parent task status: {e}")
    
    def _save_parent_task(self, parent_task: ParentTask) -> None:
        """保存父任务到Redis"""
        try:
            key = f"{self.parent_task_prefix}{parent_task.task_id}"
            data = {
                "task_id": parent_task.task_id,
                "status": parent_task.status.value,
                "created_at": parent_task.created_at,
                "started_at": parent_task.started_at,
                "completed_at": parent_task.completed_at,
                "metadata": parent_task.metadata
            }
            
            self.redis_helper.set(key, str(data), ex=86400)  # 24小时过期
            
        except Exception as e:
            self.logger.error(f"Failed to save parent task: {e}")
    
    def _save_subtask(self, subtask: SubTask) -> None:
        """保存子任务到Redis"""
        try:
            key = f"{self.subtask_prefix}{subtask.parent_task_id}:{subtask.task_id}"
            data = {
                "task_id": subtask.task_id,
                "parent_task_id": subtask.parent_task_id,
                "task_type": subtask.task_type,
                "status": subtask.status.value,
                "dependencies": subtask.dependencies,
                "dependency_type": subtask.dependency_type.value,
                "created_at": subtask.created_at,
                "metadata": subtask.metadata
            }
            
            self.redis_helper.set(key, str(data), ex=86400)  # 24小时过期
            
        except Exception as e:
            self.logger.error(f"Failed to save subtask: {e}")
    
    def _update_subtask_in_redis(self, parent_task_id: str, subtask_id: str,
                                status: SubTaskStatus, result: Optional[Dict[str, Any]] = None,
                                error_message: Optional[str] = None) -> None:
        """更新Redis中的子任务"""
        try:
            key = f"{self.subtask_prefix}{parent_task_id}:{subtask_id}"
            data = self.redis_helper.get(key)
            if data:
                # 这里应该解析和更新数据
                # 简化实现
                pass
                
        except Exception as e:
            self.logger.error(f"Failed to update subtask in Redis: {e}")
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            # 检查Redis连接
            if not self.redis_helper.health_check():
                return False
            
            # 检查父任务数量
            parent_task_count = len(self.parent_tasks)
            self.logger.debug(f"Parent tasks count: {parent_task_count}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"SubTask manager health check failed: {e}")
            return False


# 全局子任务管理器实例
_subtask_manager: Optional[SubTaskManager] = None


def get_subtask_manager(config: TaskManagerConfig) -> SubTaskManager:
    """
    获取子任务管理器实例
    
    Args:
        config: 任务管理器配置
        
    Returns:
        子任务管理器实例
    """
    global _subtask_manager
    if _subtask_manager is None:
        _subtask_manager = SubTaskManager(config)
    return _subtask_manager


def close_subtask_manager() -> None:
    """关闭子任务管理器"""
    global _subtask_manager
    if _subtask_manager:
        _subtask_manager = None
