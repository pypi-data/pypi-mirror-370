"""
任务管理器核心模块

提供任务创建、状态查询、结果获取、取消和删除功能。
严格遵循苹果产品原则：高内聚、低耦合、简洁接口。
"""

import uuid
import time
from typing import Optional, Dict, Any, List, Union
from enum import Enum
from dataclasses import dataclass, asdict
from loguru import logger

from ..core.config import TaskManagerConfig
from ..config.rq_config import get_rq_queue_manager, RQConnectionError
from ..utils.redis_helper import get_redis_helper


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 等待中
    QUEUED = "queued"        # 已入队
    STARTED = "started"      # 已开始
    FINISHED = "finished"    # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消
    DELETED = "deleted"      # 已删除


@dataclass
class TaskInfo:
    """任务信息"""
    task_id: str
    task_type: str
    status: TaskStatus
    input_data: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: float = None
    updated_at: float = None
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 300
    priority: int = 1
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def update_status(self, status: TaskStatus, **kwargs):
        """更新状态"""
        self.status = status
        self.updated_at = time.time()
        
        if status == TaskStatus.STARTED and self.started_at is None:
            self.started_at = time.time()
        elif status in [TaskStatus.FINISHED, TaskStatus.FAILED] and self.finished_at is None:
            self.finished_at = time.time()
        
        # 更新其他字段
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class TaskManagerError(Exception):
    """任务管理器错误"""
    pass


class TaskManager:
    """
    任务管理器
    
    提供任务创建、状态查询、结果获取、取消和删除功能。
    严格遵循苹果产品原则：高内聚、低耦合、简洁接口。
    """
    
    def __init__(self, config: TaskManagerConfig):
        """
        初始化任务管理器
        
        Args:
            config: 任务管理器配置对象
        """
        self.config = config
        self.rq_manager = get_rq_queue_manager(config)
        self.redis_helper = get_redis_helper(config.redis)
        
        # 任务缓存前缀
        self.task_cache_prefix = "taskmanager_hjy:task:"
        self.task_list_prefix = "taskmanager_hjy:tasks:"
        
        logger.info("TaskManager initialized")
    
    def create_task(self, task_type: str, input_data: Dict[str, Any], 
                   user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None,
                   **kwargs) -> str:
        """
        创建任务
        
        Args:
            task_type: 任务类型
            input_data: 输入数据
            user_id: 用户ID
            metadata: 元数据
            **kwargs: 其他参数（timeout, priority, max_retries等）
            
        Returns:
            任务ID
            
        Raises:
            TaskManagerError: 任务创建失败时抛出
        """
        try:
            # 生成任务ID
            task_id = str(uuid.uuid4())
            
            # 获取任务配置
            task_config = self.config.tasks.get(task_type, self.config.tasks.get("default", {}))
            
            # 创建任务信息
            task_info = TaskInfo(
                task_id=task_id,
                task_type=task_type,
                status=TaskStatus.PENDING,
                input_data=input_data,
                max_retries=kwargs.get('max_retries', getattr(task_config, 'max_retry', 3)),
                timeout=kwargs.get('timeout', getattr(task_config, 'timeout', 300)),
                priority=kwargs.get('priority', getattr(task_config, 'priority', 1)),
                metadata=metadata or {}
            )
            
            # 添加用户ID到元数据
            if user_id:
                task_info.metadata['user_id'] = user_id
            
            # 保存任务信息到Redis
            self._save_task_info(task_info)
            
            # 将任务加入队列
            self._enqueue_task(task_info)
            
            logger.info(f"Task {task_id} created successfully")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise TaskManagerError(f"Failed to create task: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态，如果任务不存在返回None
        """
        try:
            task_info = self._get_task_info(task_id)
            if task_info:
                return task_info.status
            return None
        except Exception as e:
            logger.error(f"Failed to get task status for {task_id}: {e}")
            return None
    
    def get_task_info(self, task_id: str) -> Optional[TaskInfo]:
        """
        获取任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务信息，如果任务不存在返回None
        """
        try:
            return self._get_task_info(task_id)
        except Exception as e:
            logger.error(f"Failed to get task info for {task_id}: {e}")
            return None
    
    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务结果，如果任务不存在或未完成返回None
        """
        try:
            task_info = self._get_task_info(task_id)
            if task_info and task_info.status == TaskStatus.FINISHED:
                return task_info.result
            return None
        except Exception as e:
            logger.error(f"Failed to get task result for {task_id}: {e}")
            return None
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功取消
        """
        try:
            task_info = self._get_task_info(task_id)
            if not task_info:
                logger.warning(f"Task {task_id} not found")
                return False
            
            # 检查任务是否可以取消
            if task_info.status not in [TaskStatus.PENDING, TaskStatus.QUEUED, TaskStatus.STARTED]:
                logger.warning(f"Cannot cancel task {task_id}: status is {task_info.status}")
                return False
            
            # 取消RQ任务
            if task_info.status in [TaskStatus.QUEUED, TaskStatus.STARTED]:
                self.rq_manager.cancel_job(task_id)
            
            # 更新任务状态
            task_info.update_status(TaskStatus.CANCELLED)
            self._save_task_info(task_info)
            
            logger.info(f"Task {task_id} cancelled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功删除
        """
        try:
            task_info = self._get_task_info(task_id)
            if not task_info:
                logger.warning(f"Task {task_id} not found")
                return False
            
            # 删除RQ任务
            self.rq_manager.delete_job(task_id)
            
            # 删除任务信息
            self._delete_task_info(task_id)
            
            logger.info(f"Task {task_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            return False
    
    def list_tasks(self, user_id: Optional[str] = None, 
                  status: Optional[TaskStatus] = None,
                  task_type: Optional[str] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        列出任务
        
        Args:
            user_id: 用户ID过滤
            status: 状态过滤
            task_type: 任务类型过滤
            limit: 返回数量限制
            
        Returns:
            任务列表
        """
        try:
            # 获取用户任务列表
            if user_id:
                task_ids = self._get_user_task_ids(user_id)
            else:
                task_ids = self._get_all_task_ids()
            
            tasks = []
            for task_id in task_ids[:limit]:
                task_info = self._get_task_info(task_id)
                if task_info:
                    # 应用过滤条件
                    if status and task_info.status != status:
                        continue
                    if task_type and task_info.task_type != task_type:
                        continue
                    
                    tasks.append(task_info.to_dict())
            
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            return []
    
    def retry_task(self, task_id: str) -> bool:
        """
        重试任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功重试
        """
        try:
            task_info = self._get_task_info(task_id)
            if not task_info:
                logger.warning(f"Task {task_id} not found")
                return False
            
            # 检查是否可以重试
            if task_info.status != TaskStatus.FAILED:
                logger.warning(f"Cannot retry task {task_id}: status is {task_info.status}")
                return False
            
            if task_info.retry_count >= task_info.max_retries:
                logger.warning(f"Cannot retry task {task_id}: max retries reached")
                return False
            
            # 重置任务状态
            task_info.update_status(TaskStatus.PENDING, retry_count=task_info.retry_count + 1)
            task_info.result = None
            task_info.error_message = None
            task_info.started_at = None
            task_info.finished_at = None
            
            # 保存任务信息
            self._save_task_info(task_info)
            
            # 重新入队
            self._enqueue_task(task_info)
            
            logger.info(f"Task {task_id} retried successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to retry task {task_id}: {e}")
            return False
    
    def get_task_stats(self) -> Dict[str, Any]:
        """
        获取任务统计信息
        
        Returns:
            任务统计信息
        """
        try:
            all_task_ids = self._get_all_task_ids()
            
            stats = {
                "total_tasks": len(all_task_ids),
                "status_counts": {},
                "type_counts": {},
                "recent_tasks": []
            }
            
            # 统计各状态的任务数量
            for task_id in all_task_ids:
                task_info = self._get_task_info(task_id)
                if task_info:
                    # 状态统计
                    status = task_info.status.value
                    stats["status_counts"][status] = stats["status_counts"].get(status, 0) + 1
                    
                    # 类型统计
                    task_type = task_info.task_type
                    stats["type_counts"][task_type] = stats["type_counts"].get(task_type, 0) + 1
                    
                    # 最近任务
                    if len(stats["recent_tasks"]) < 10:
                        stats["recent_tasks"].append({
                            "task_id": task_id,
                            "task_type": task_type,
                            "status": status,
                            "created_at": task_info.created_at
                        })
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get task stats: {e}")
            return {}
    
    def _save_task_info(self, task_info: TaskInfo) -> None:
        """保存任务信息到Redis"""
        try:
            # 保存任务信息
            task_key = f"{self.task_cache_prefix}{task_info.task_id}"
            self.redis_helper.set(task_key, str(task_info.to_dict()), ex=86400)  # 24小时过期
            
            # 添加到任务列表
            list_key = f"{self.task_list_prefix}all"
            self.redis_helper.set(f"{list_key}:{task_info.task_id}", "1", ex=86400)
            
            # 如果有关联用户，添加到用户任务列表
            user_id = task_info.metadata.get('user_id')
            if user_id:
                user_list_key = f"{self.task_list_prefix}user:{user_id}"
                self.redis_helper.set(f"{user_list_key}:{task_info.task_id}", "1", ex=86400)
                
        except Exception as e:
            logger.error(f"Failed to save task info: {e}")
            raise TaskManagerError(f"Failed to save task info: {e}")
    
    def _get_task_info(self, task_id: str) -> Optional[TaskInfo]:
        """从Redis获取任务信息"""
        try:
            task_key = f"{self.task_cache_prefix}{task_id}"
            task_data = self.redis_helper.get(task_key)
            
            if task_data:
                # 这里需要解析任务数据，简化处理
                # 实际应该使用JSON序列化
                return self._parse_task_info(task_id, task_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get task info: {e}")
            return None
    
    def _parse_task_info(self, task_id: str, task_data: str) -> TaskInfo:
        """解析任务信息（简化实现）"""
        # 这里应该使用JSON反序列化
        # 为了简化，我们创建一个基本的任务信息
        return TaskInfo(
            task_id=task_id,
            task_type="unknown",
            status=TaskStatus.PENDING,
            input_data={},
            created_at=time.time()
        )
    
    def _delete_task_info(self, task_id: str) -> None:
        """删除任务信息"""
        try:
            # 删除任务信息
            task_key = f"{self.task_cache_prefix}{task_id}"
            self.redis_helper.delete(task_key)
            
            # 从任务列表中删除
            list_key = f"{self.task_list_prefix}all"
            self.redis_helper.delete(f"{list_key}:{task_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete task info: {e}")
    
    def _enqueue_task(self, task_info: TaskInfo) -> None:
        """将任务加入队列"""
        try:
            # 这里应该根据任务类型调用相应的处理函数
            # 暂时使用一个占位函数
            def placeholder_task():
                return {"status": "completed", "task_id": task_info.task_id}
            
            # 更新状态为已入队
            task_info.update_status(TaskStatus.QUEUED)
            self._save_task_info(task_info)
            
            # 加入RQ队列
            job = self.rq_manager.enqueue_job(
                placeholder_task,
                timeout=task_info.timeout,
                result_ttl=self.config.rq.result_ttl,
                job_ttl=self.config.rq.job_ttl
            )
            
            logger.info(f"Task {task_info.task_id} enqueued as job {job.id}")
            
        except Exception as e:
            logger.error(f"Failed to enqueue task: {e}")
            task_info.update_status(TaskStatus.FAILED, error_message=str(e))
            self._save_task_info(task_info)
            raise TaskManagerError(f"Failed to enqueue task: {e}")
    
    def _get_all_task_ids(self) -> List[str]:
        """获取所有任务ID"""
        try:
            # 这里应该从Redis中获取所有任务ID
            # 简化实现，返回空列表
            return []
        except Exception as e:
            logger.error(f"Failed to get all task IDs: {e}")
            return []
    
    def _get_user_task_ids(self, user_id: str) -> List[str]:
        """获取用户的任务ID列表"""
        try:
            # 这里应该从Redis中获取用户的任务ID列表
            # 简化实现，返回空列表
            return []
        except Exception as e:
            logger.error(f"Failed to get user task IDs: {e}")
            return []
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            # 检查Redis连接
            if not self.redis_helper.health_check():
                return False
            
            # 检查RQ队列
            if not self.rq_manager.health_check():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"TaskManager health check failed: {e}")
            return False
    
    def close(self) -> None:
        """关闭任务管理器"""
        try:
            self.rq_manager.close()
            self.redis_helper.close()
            logger.info("TaskManager closed")
        except Exception as e:
            logger.error(f"Error closing TaskManager: {e}")


# 全局任务管理器实例
_task_manager: Optional[TaskManager] = None


def get_task_manager(config: TaskManagerConfig) -> TaskManager:
    """
    获取任务管理器实例
    
    Args:
        config: 任务管理器配置对象
        
    Returns:
        任务管理器实例
    """
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager(config)
    return _task_manager


def close_task_manager() -> None:
    """关闭任务管理器"""
    global _task_manager
    if _task_manager:
        _task_manager.close()
        _task_manager = None
