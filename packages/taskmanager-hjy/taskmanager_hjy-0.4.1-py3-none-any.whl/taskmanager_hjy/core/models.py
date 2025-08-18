#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理器核心模型
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """任务类型枚举"""
    AUDIO_ANALYSIS = "audio_analysis"
    DATA_PROCESSING = "data_processing"
    AI_INFERENCE = "ai_inference"
    SYSTEM_MAINTENANCE = "system_maintenance"
    CUSTOM = "custom"


class TaskPriority(str, Enum):
    """任务优先级枚举"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TaskModel(BaseModel):
    """任务模型"""
    id: str = Field(..., description="任务ID")
    name: str = Field(..., description="任务名称")
    type: TaskType = Field(..., description="任务类型")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="任务状态")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="任务优先级")
    
    # 任务参数
    parameters: Dict[str, Any] = Field(default_factory=dict, description="任务参数")
    
    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    
    # 结果信息
    result: Optional[Dict[str, Any]] = Field(None, description="任务结果")
    error_message: Optional[str] = Field(None, description="错误信息")
    
    # 进度信息
    progress: float = Field(default=0.0, description="进度百分比")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def create(cls, name: str, task_type: TaskType, parameters: Dict[str, Any] = None, priority: TaskPriority = TaskPriority.NORMAL) -> "TaskModel":
        """创建新任务"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        return cls(
            id=task_id,
            name=name,
            type=task_type,
            parameters=parameters or {},
            priority=priority
        )
