"""
任务优先级管理模块

实现任务优先级管理，支持优先级队列和智能调度。
严格遵循苹果产品原则：高内聚、低耦合、简洁接口。
"""

import time
import heapq
from typing import Dict, List, Optional, Tuple, Any
from enum import IntEnum
from dataclasses import dataclass, field
from loguru import logger

from ..core.config import TaskManagerConfig
from ..manager.task_manager import TaskStatus, TaskInfo
from ..utils.redis_helper import get_redis_helper


class TaskPriority(IntEnum):
    """任务优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class PriorityTask:
    """优先级任务"""
    task_id: str
    priority: TaskPriority
    created_at: float
    scheduled_at: Optional[float] = None
    user_id: Optional[str] = None
    task_type: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other):
        """优先级比较（数值越大优先级越高）"""
        if self.priority != other.priority:
            return self.priority > other.priority
        # 优先级相同时，按创建时间排序（先创建的优先）
        return self.created_at < other.created_at


class PriorityQueue:
    """
    优先级队列
    
    基于堆的优先级队列实现，支持动态优先级调整。
    """
    
    def __init__(self):
        """初始化优先级队列"""
        self._queue: List[PriorityTask] = []
        self._task_map: Dict[str, PriorityTask] = {}
        self.logger = logger.bind(component="priority_queue")
        
        self.logger.info("PriorityQueue initialized")
    
    def push(self, task: PriorityTask) -> None:
        """
        添加任务到优先级队列
        
        Args:
            task: 优先级任务
        """
        if task.task_id in self._task_map:
            self.logger.warning(f"Task {task.task_id} already exists in queue")
            return
        
        self._task_map[task.task_id] = task
        heapq.heappush(self._queue, task)
        self.logger.debug(f"Task {task.task_id} pushed to queue with priority {task.priority}")
    
    def pop(self) -> Optional[PriorityTask]:
        """
        获取最高优先级的任务
        
        Returns:
            最高优先级的任务，如果队列为空返回None
        """
        if not self._queue:
            return None
        
        task = heapq.heappop(self._queue)
        del self._task_map[task.task_id]
        self.logger.debug(f"Task {task.task_id} popped from queue")
        return task
    
    def peek(self) -> Optional[PriorityTask]:
        """
        查看最高优先级的任务（不移除）
        
        Returns:
            最高优先级的任务，如果队列为空返回None
        """
        if not self._queue:
            return None
        return self._queue[0]
    
    def remove(self, task_id: str) -> bool:
        """
        从队列中移除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功移除
        """
        if task_id not in self._task_map:
            return False
        
        # 标记任务为已移除
        task = self._task_map[task_id]
        task.scheduled_at = None
        
        # 重建队列（移除标记的任务）
        self._queue = [t for t in self._queue if t.task_id != task_id]
        heapq.heapify(self._queue)
        
        del self._task_map[task_id]
        self.logger.debug(f"Task {task_id} removed from queue")
        return True
    
    def update_priority(self, task_id: str, new_priority: TaskPriority) -> bool:
        """
        更新任务优先级
        
        Args:
            task_id: 任务ID
            new_priority: 新优先级
            
        Returns:
            是否成功更新
        """
        if task_id not in self._task_map:
            return False
        
        # 移除旧任务
        self.remove(task_id)
        
        # 创建新任务
        old_task = self._task_map.get(task_id)
        if old_task:
            new_task = PriorityTask(
                task_id=task_id,
                priority=new_priority,
                created_at=old_task.created_at,
                user_id=old_task.user_id,
                task_type=old_task.task_type,
                metadata=old_task.metadata
            )
            self.push(new_task)
            
            self.logger.info(f"Task {task_id} priority updated from {old_task.priority} to {new_priority}")
            return True
        
        return False
    
    def get_task(self, task_id: str) -> Optional[PriorityTask]:
        """
        获取指定任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务对象，如果不存在返回None
        """
        return self._task_map.get(task_id)
    
    def size(self) -> int:
        """
        获取队列大小
        
        Returns:
            队列中的任务数量
        """
        return len(self._queue)
    
    def is_empty(self) -> bool:
        """
        检查队列是否为空
        
        Returns:
            是否为空
        """
        return len(self._queue) == 0
    
    def get_all_tasks(self) -> List[PriorityTask]:
        """
        获取所有任务（按优先级排序）
        
        Returns:
            任务列表
        """
        return sorted(self._queue, key=lambda x: (x.priority, x.created_at))
    
    def get_tasks_by_priority(self, priority: TaskPriority) -> List[PriorityTask]:
        """
        获取指定优先级的任务
        
        Args:
            priority: 优先级
            
        Returns:
            任务列表
        """
        return [task for task in self._queue if task.priority == priority]
    
    def get_priority_stats(self) -> Dict[TaskPriority, int]:
        """
        获取优先级统计
        
        Returns:
            各优先级的任务数量
        """
        stats = {}
        for priority in TaskPriority:
            stats[priority] = len(self.get_tasks_by_priority(priority))
        return stats


class PriorityManager:
    """
    任务优先级管理器
    
    管理任务的优先级分配、调度和监控。
    """
    
    def __init__(self, config: TaskManagerConfig):
        """
        初始化优先级管理器
        
        Args:
            config: 任务管理器配置
        """
        self.config = config
        self.redis_helper = get_redis_helper(config.redis)
        
        # 优先级队列
        self.priority_queue = PriorityQueue()
        
        # Redis键前缀
        self.priority_key_prefix = "taskmanager_hjy:priority:"
        self.stats_key_prefix = "taskmanager_hjy:priority_stats:"
        
        # 优先级配置
        self.priority_config = {
            TaskPriority.LOW: {"weight": 1, "max_wait_time": 3600},      # 1小时
            TaskPriority.NORMAL: {"weight": 2, "max_wait_time": 1800},   # 30分钟
            TaskPriority.HIGH: {"weight": 4, "max_wait_time": 900},      # 15分钟
            TaskPriority.URGENT: {"weight": 8, "max_wait_time": 300},    # 5分钟
            TaskPriority.CRITICAL: {"weight": 16, "max_wait_time": 60}   # 1分钟
        }
        
        self.logger = logger.bind(component="priority_manager")
        self.logger.info("PriorityManager initialized")
    
    def add_task(self, task_id: str, priority: TaskPriority, 
                 user_id: Optional[str] = None, task_type: str = "",
                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        添加任务到优先级队列
        
        Args:
            task_id: 任务ID
            priority: 优先级
            user_id: 用户ID
            task_type: 任务类型
            metadata: 元数据
            
        Returns:
            是否成功添加
        """
        try:
            # 创建优先级任务
            priority_task = PriorityTask(
                task_id=task_id,
                priority=priority,
                created_at=time.time(),
                user_id=user_id,
                task_type=task_type,
                metadata=metadata or {}
            )
            
            # 添加到队列
            self.priority_queue.push(priority_task)
            
            # 保存到Redis
            self._save_priority_task(priority_task)
            
            # 更新统计
            self._update_stats()
            
            self.logger.info(f"Task {task_id} added with priority {priority}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add task {task_id}: {e}")
            return False
    
    def get_next_task(self) -> Optional[str]:
        """
        获取下一个要执行的任务
        
        Returns:
            任务ID，如果没有任务返回None
        """
        try:
            # 从队列获取最高优先级任务
            priority_task = self.priority_queue.pop()
            if not priority_task:
                return None
            
            # 从Redis移除
            self._remove_priority_task(priority_task.task_id)
            
            # 更新统计
            self._update_stats()
            
            self.logger.info(f"Next task: {priority_task.task_id} (priority: {priority_task.priority})")
            return priority_task.task_id
            
        except Exception as e:
            self.logger.error(f"Failed to get next task: {e}")
            return None
    
    def update_task_priority(self, task_id: str, new_priority: TaskPriority) -> bool:
        """
        更新任务优先级
        
        Args:
            task_id: 任务ID
            new_priority: 新优先级
            
        Returns:
            是否成功更新
        """
        try:
            # 更新队列中的优先级
            success = self.priority_queue.update_priority(task_id, new_priority)
            if not success:
                return False
            
            # 更新Redis中的优先级
            self._update_priority_in_redis(task_id, new_priority)
            
            # 更新统计
            self._update_stats()
            
            self.logger.info(f"Task {task_id} priority updated to {new_priority}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update task priority: {e}")
            return False
    
    def remove_task(self, task_id: str) -> bool:
        """
        从优先级队列移除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功移除
        """
        try:
            # 从队列移除
            success = self.priority_queue.remove(task_id)
            if not success:
                return False
            
            # 从Redis移除
            self._remove_priority_task(task_id)
            
            # 更新统计
            self._update_stats()
            
            self.logger.info(f"Task {task_id} removed from priority queue")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove task: {e}")
            return False
    
    def get_task_priority(self, task_id: str) -> Optional[TaskPriority]:
        """
        获取任务优先级
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务优先级，如果任务不存在返回None
        """
        priority_task = self.priority_queue.get_task(task_id)
        return priority_task.priority if priority_task else None
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        获取队列统计信息
        
        Returns:
            统计信息
        """
        try:
            stats = {
                "total_tasks": self.priority_queue.size(),
                "priority_distribution": self.priority_queue.get_priority_stats(),
                "queue_status": "empty" if self.priority_queue.is_empty() else "active",
                "next_task": None
            }
            
            # 获取下一个任务信息
            next_task = self.priority_queue.peek()
            if next_task:
                stats["next_task"] = {
                    "task_id": next_task.task_id,
                    "priority": next_task.priority.value,
                    "wait_time": time.time() - next_task.created_at
                }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get queue stats: {e}")
            return {}
    
    def get_tasks_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户的任务列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            任务列表
        """
        try:
            tasks = []
            for task in self.priority_queue.get_all_tasks():
                if task.user_id == user_id:
                    tasks.append({
                        "task_id": task.task_id,
                        "priority": task.priority.value,
                        "created_at": task.created_at,
                        "task_type": task.task_type,
                        "wait_time": time.time() - task.created_at
                    })
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Failed to get user tasks: {e}")
            return []
    
    def get_priority_config(self, priority: TaskPriority) -> Dict[str, Any]:
        """
        获取优先级配置
        
        Args:
            priority: 优先级
            
        Returns:
            优先级配置
        """
        return self.priority_config.get(priority, {})
    
    def calculate_priority_score(self, task_id: str) -> float:
        """
        计算任务优先级分数
        
        Args:
            task_id: 任务ID
            
        Returns:
            优先级分数
        """
        try:
            priority_task = self.priority_queue.get_task(task_id)
            if not priority_task:
                return 0.0
            
            # 基础分数
            base_score = priority_task.priority.value
            
            # 等待时间分数
            wait_time = time.time() - priority_task.created_at
            max_wait_time = self.priority_config[priority_task.priority]["max_wait_time"]
            wait_score = min(wait_time / max_wait_time, 1.0)
            
            # 总分数 = 基础分数 * (1 + 等待时间分数)
            total_score = base_score * (1 + wait_score)
            
            return total_score
            
        except Exception as e:
            self.logger.error(f"Failed to calculate priority score: {e}")
            return 0.0
    
    def _save_priority_task(self, priority_task: PriorityTask) -> None:
        """保存优先级任务到Redis"""
        try:
            key = f"{self.priority_key_prefix}{priority_task.task_id}"
            data = {
                "task_id": priority_task.task_id,
                "priority": priority_task.priority.value,
                "created_at": priority_task.created_at,
                "user_id": priority_task.user_id,
                "task_type": priority_task.task_type,
                "metadata": priority_task.metadata
            }
            
            self.redis_helper.set(key, str(data), ex=86400)  # 24小时过期
            
        except Exception as e:
            self.logger.error(f"Failed to save priority task: {e}")
    
    def _remove_priority_task(self, task_id: str) -> None:
        """从Redis移除优先级任务"""
        try:
            key = f"{self.priority_key_prefix}{task_id}"
            self.redis_helper.delete(key)
            
        except Exception as e:
            self.logger.error(f"Failed to remove priority task: {e}")
    
    def _update_priority_in_redis(self, task_id: str, new_priority: TaskPriority) -> None:
        """更新Redis中的优先级"""
        try:
            key = f"{self.priority_key_prefix}{task_id}"
            data = self.redis_helper.get(key)
            if data:
                # 这里应该解析和更新数据
                # 简化实现
                pass
                
        except Exception as e:
            self.logger.error(f"Failed to update priority in Redis: {e}")
    
    def _update_stats(self) -> None:
        """更新统计信息"""
        try:
            stats = self.get_queue_stats()
            key = f"{self.stats_key_prefix}current"
            self.redis_helper.set(key, str(stats), ex=3600)  # 1小时过期
            
        except Exception as e:
            self.logger.error(f"Failed to update stats: {e}")
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            # 检查Redis连接
            if not self.redis_helper.health_check():
                return False
            
            # 检查队列状态
            queue_size = self.priority_queue.size()
            self.logger.debug(f"Priority queue size: {queue_size}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Priority manager health check failed: {e}")
            return False


# 全局优先级管理器实例
_priority_manager: Optional[PriorityManager] = None


def get_priority_manager(config: TaskManagerConfig) -> PriorityManager:
    """
    获取优先级管理器实例
    
    Args:
        config: 任务管理器配置
        
    Returns:
        优先级管理器实例
    """
    global _priority_manager
    if _priority_manager is None:
        _priority_manager = PriorityManager(config)
    return _priority_manager


def close_priority_manager() -> None:
    """关闭优先级管理器"""
    global _priority_manager
    if _priority_manager:
        _priority_manager = None
