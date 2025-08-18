#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理器工具函数
"""

from typing import Any, Dict, List, Optional

from .manager import TaskManager
from .models import TaskModel, TaskStatus, TaskType, TaskPriority

# 全局任务管理器实例
_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    """获取全局任务管理器实例"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager


def create_task(
    name: str,
    task_type: TaskType,
    parameters: Dict[str, Any] = None,
    priority: TaskPriority = TaskPriority.NORMAL
) -> TaskModel:
    """创建新任务（便捷函数）"""
    manager = get_task_manager()
    return manager.create_task(name, task_type, parameters, priority)


async def execute_task(task_id: str) -> bool:
    """执行任务（便捷函数）"""
    manager = get_task_manager()
    return await manager.execute_task(task_id)


def get_task(task_id: str) -> Optional[TaskModel]:
    """获取任务信息（便捷函数）"""
    manager = get_task_manager()
    return manager.get_task(task_id)


def list_tasks(
    status: Optional[TaskStatus] = None,
    task_type: Optional[TaskType] = None
) -> List[TaskModel]:
    """列出任务（便捷函数）"""
    manager = get_task_manager()
    return manager.list_tasks(status, task_type)


def cancel_task(task_id: str) -> bool:
    """取消任务（便捷函数）"""
    manager = get_task_manager()
    return manager.cancel_task(task_id)


def get_task_statistics() -> Dict[str, Any]:
    """获取任务统计信息（便捷函数）"""
    manager = get_task_manager()
    return manager.get_task_statistics()
