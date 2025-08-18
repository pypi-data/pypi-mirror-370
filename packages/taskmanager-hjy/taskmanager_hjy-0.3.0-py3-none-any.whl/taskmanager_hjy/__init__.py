"""
taskmanager_hjy - 基于RQ + ai_runner_hjy + 云Redis的通用任务管理解决方案

让异步任务处理变得毫不费力。
"""

import uuid
from typing import Dict, Any, Optional, List
from .core.config import get_config
from .manager.task_manager import TaskManager as _TaskManager
from .tasks.base import BaseTask, TaskType, TaskPriority
from .manager.task_manager import TaskStatus
from .tasks.audio_analysis import AudioAnalysisTask

# 版本信息
__version__ = "0.0.1"
__author__ = "hjy"
__email__ = "hjy@example.com"

# 主要API类
class TaskManager:
    """
    任务管理器 - 主要的用户接口
    
    提供简洁优雅的API来管理异步任务。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化任务管理器
        
        Args:
            config: 配置字典，如果为None则使用默认配置
        """
        if config is None:
            config = get_config()
        self._manager = _TaskManager(config)
    
    def create_task(self, task_type: str, input_data: Dict[str, Any], 
                   user_id: Optional[str] = None, priority: int = 1, 
                   **kwargs) -> str:
        """
        创建任务
        
        Args:
            task_type: 任务类型
            input_data: 输入数据
            user_id: 用户ID
            priority: 优先级 (1-3)
            **kwargs: 其他参数
            
        Returns:
            任务ID
            
        Raises:
            TaskManagerError: 任务创建失败
        """
        return self._manager.create_task(
            task_type=task_type,
            input_data=input_data,
            user_id=user_id,
            priority=priority,
            **kwargs
        )
    
    def get_status(self, task_id: str) -> TaskStatus:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态
        """
        return self._manager.get_task_status(task_id)
    
    def get_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务结果，如果任务未完成则返回None
        """
        return self._manager.get_task_result(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功取消
        """
        return self._manager.cancel_task(task_id)
    
    def delete_task(self, task_id: str) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功删除
        """
        return self._manager.delete_task(task_id)
    
    def list_tasks(self, user_id: Optional[str] = None, 
                  status: Optional[TaskStatus] = None) -> List[Dict[str, Any]]:
        """
        列出任务
        
        Args:
            user_id: 用户ID过滤
            status: 状态过滤
            
        Returns:
            任务列表
        """
        return self._manager.list_tasks(user_id=user_id, status=status)
    
    def create_subtask(self, parent_task_id: str, task_type: str, 
                      input_data: Dict[str, Any], **kwargs) -> str:
        """
        创建子任务
        
        Args:
            parent_task_id: 父任务ID
            task_type: 任务类型
            input_data: 输入数据
            **kwargs: 其他参数
            
        Returns:
            子任务ID
        """
        from .manager.subtask_manager import SubTaskManager
        subtask_manager = SubTaskManager(self._manager.config)
        
        # 先创建父任务（如果不存在）
        subtask_manager.create_parent_task(parent_task_id)
        
        # 创建子任务
        subtask_id = str(uuid.uuid4())
        success = subtask_manager.add_subtask(
            parent_task_id=parent_task_id,
            subtask_id=subtask_id,
            task_type=task_type,
            input_data=input_data,
            **kwargs
        )
        
        if success:
            return subtask_id
        else:
            raise Exception(f"Failed to create subtask for parent task {parent_task_id}")
    
    def batch_create(self, tasks: List[Dict[str, Any]], 
                    user_id: Optional[str] = None) -> List[str]:
        """
        批量创建任务
        
        Args:
            tasks: 任务列表，每个任务包含task_type和input_data
            user_id: 用户ID
            
        Returns:
            任务ID列表
        """
        task_ids = []
        for task_data in tasks:
            task_id = self.create_task(
                task_type=task_data["task_type"],
                input_data=task_data["input_data"],
                user_id=user_id,
                **task_data.get("kwargs", {})
            )
            task_ids.append(task_id)
        return task_ids
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            系统是否健康
        """
        return self._manager.health_check()
    
    def register_task_type(self, task_type: str, task_class: type) -> None:
        """
        注册自定义任务类型
        
        Args:
            task_type: 任务类型名称
            task_class: 任务类
        """
        from .tasks.base import TaskFactory
        TaskFactory.register(task_type, task_class)

# 便捷函数
def create_task_manager(config: Optional[Dict[str, Any]] = None) -> TaskManager:
    """
    创建任务管理器的便捷函数
    
    Args:
        config: 配置字典
        
    Returns:
        任务管理器实例
    """
    return TaskManager(config)

# 导出主要类和类型
__all__ = [
    "TaskManager",
    "BaseTask", 
    "AudioAnalysisTask",
    "TaskType",
    "TaskStatus", 
    "TaskPriority",
    "create_task_manager"
]
