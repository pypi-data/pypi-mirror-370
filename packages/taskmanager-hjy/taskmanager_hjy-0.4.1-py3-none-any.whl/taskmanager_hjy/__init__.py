#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全独立的 taskmanager-hjy 包
基于新包架构，无旧包依赖
"""

from .core.manager import TaskManager
from .core.models import TaskModel, TaskStatus, TaskType, TaskPriority
from .core.utils import create_task, execute_task, get_task, list_tasks, get_task_statistics

__version__ = "0.4.1"
__author__ = "hjy"
__description__ = "完全独立的任务管理包 - 基于新包架构，无旧包依赖"

__all__ = [
    "TaskManager",
    "TaskModel", 
    "TaskStatus",
    "TaskType",
    "TaskPriority",
    "create_task",
    "execute_task", 
    "get_task",
    "list_tasks",
    "get_task_statistics",
]
