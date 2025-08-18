#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理器核心
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from .models import TaskModel, TaskStatus, TaskType, TaskPriority

# 使用新包，不依赖任何旧包
try:
    from configmanager_hjy import ConfigManager
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    logger.warning("configmanager_hjy 不可用，将使用默认配置")

try:
    from datamanager_hjy import DataManager
    DATA_AVAILABLE = True
except ImportError:
    DATA_AVAILABLE = False
    logger.warning("datamanager_hjy 不可用，将使用内存存储")

try:
    from aimanager_hjy import AIManager
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    logger.warning("aimanager_hjy 不可用，将使用模拟AI功能")

try:
    from keymanager_hjy import KeyMaster
    KEY_AVAILABLE = True
except ImportError:
    KEY_AVAILABLE = False
    logger.warning("keymanager_hjy 不可用，将使用默认密钥管理")


class TaskManager:
    """任务管理器 - 完全独立版本"""
    
    def __init__(self):
        """初始化任务管理器"""
        logger.info("🚀 初始化任务管理器（完全独立版本 0.4.0）...")
        
        # 初始化新包组件（可选）
        self.config_manager = None
        self.data_manager = None
        self.ai_manager = None
        self.key_manager = None
        
        if CONFIG_AVAILABLE:
            try:
                self.config_manager = ConfigManager()
                logger.success("✅ 配置管理器初始化成功")
            except Exception as e:
                logger.warning(f"⚠️ 配置管理器初始化失败: {e}")
        
        if DATA_AVAILABLE:
            try:
                self.data_manager = DataManager()
                logger.success("✅ 数据管理器初始化成功")
            except Exception as e:
                logger.warning(f"⚠️ 数据管理器初始化失败: {e}")
        
        if AI_AVAILABLE:
            try:
                self.ai_manager = AIManager()
                logger.success("✅ AI管理器初始化成功")
            except Exception as e:
                logger.warning(f"⚠️ AI管理器初始化失败: {e}")
        
        if KEY_AVAILABLE:
            try:
                self.key_manager = KeyMaster()
                logger.success("✅ 密钥管理器初始化成功")
            except Exception as e:
                logger.warning(f"⚠️ 密钥管理器初始化失败: {e}")
        
        # 任务存储
        self.tasks: Dict[str, TaskModel] = {}
        self.task_queue: List[str] = []
        
        logger.success("✅ 任务管理器初始化完成（完全独立版本 0.4.0）")
    
    def create_task(
        self,
        name: str,
        task_type: TaskType,
        parameters: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> TaskModel:
        """创建新任务"""
        task = TaskModel.create(name, task_type, parameters, priority)
        
        self.tasks[task.id] = task
        self.task_queue.append(task.id)
        
        logger.info(f"📝 创建任务: {task.id} - {name}")
        return task
    
    def get_task(self, task_id: str) -> Optional[TaskModel]:
        """获取任务信息"""
        return self.tasks.get(task_id)
    
    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None
    ) -> List[TaskModel]:
        """列出任务"""
        tasks = list(self.tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        if task_type:
            tasks = [t for t in tasks if t.type == task_type]
        
        return sorted(tasks, key=lambda x: x.created_at, reverse=True)
    
    async def execute_task(self, task_id: str) -> bool:
        """执行任务"""
        task = self.get_task(task_id)
        if not task:
            logger.error(f"❌ 任务不存在: {task_id}")
            return False
        
        if task.status != TaskStatus.PENDING:
            logger.warning(f"⚠️ 任务状态不是待执行: {task_id} - {task.status}")
            return False
        
        try:
            # 更新任务状态
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            task.progress = 0.0
            
            logger.info(f"🔄 开始执行任务: {task_id} - {task.name}")
            
            # 根据任务类型执行不同的逻辑
            if task.type == TaskType.AUDIO_ANALYSIS:
                result = await self._execute_audio_analysis(task)
            elif task.type == TaskType.DATA_PROCESSING:
                result = await self._execute_data_processing(task)
            elif task.type == TaskType.AI_INFERENCE:
                result = await self._execute_ai_inference(task)
            elif task.type == TaskType.SYSTEM_MAINTENANCE:
                result = await self._execute_system_maintenance(task)
            else:
                result = await self._execute_custom_task(task)
            
            # 更新任务结果
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.progress = 100.0
            
            logger.success(f"✅ 任务执行完成: {task_id} - {task.name}")
            return True
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
            
            logger.error(f"❌ 任务执行失败: {task_id} - {task.name} - {e}")
            return False
    
    async def _execute_audio_analysis(self, task: TaskModel) -> Dict[str, Any]:
        """执行音频分析任务"""
        logger.info(f"🎵 执行音频分析任务: {task.name}")
        
        # 模拟音频分析过程
        await asyncio.sleep(1)
        task.progress = 25.0
        
        await asyncio.sleep(1)
        task.progress = 50.0
        
        await asyncio.sleep(1)
        task.progress = 75.0
        
        await asyncio.sleep(1)
        task.progress = 100.0
        
        return {
            "analysis_type": "audio_analysis",
            "duration": "4.0s",
            "result": "音频分析完成",
            "parameters": task.parameters,
            "version": "0.4.0"
        }
    
    async def _execute_data_processing(self, task: TaskModel) -> Dict[str, Any]:
        """执行数据处理任务"""
        logger.info(f"📊 执行数据处理任务: {task.name}")
        
        # 模拟数据处理过程
        await asyncio.sleep(0.5)
        task.progress = 20.0
        
        await asyncio.sleep(0.5)
        task.progress = 40.0
        
        await asyncio.sleep(0.5)
        task.progress = 60.0
        
        await asyncio.sleep(0.5)
        task.progress = 80.0
        
        await asyncio.sleep(0.5)
        task.progress = 100.0
        
        return {
            "processing_type": "data_processing",
            "duration": "2.5s",
            "result": "数据处理完成",
            "parameters": task.parameters,
            "version": "0.4.0"
        }
    
    async def _execute_ai_inference(self, task: TaskModel) -> Dict[str, Any]:
        """执行AI推理任务"""
        logger.info(f"🤖 执行AI推理任务: {task.name}")
        
        # 模拟AI推理过程
        await asyncio.sleep(0.8)
        task.progress = 20.0
        
        await asyncio.sleep(0.8)
        task.progress = 40.0
        
        await asyncio.sleep(0.8)
        task.progress = 60.0
        
        await asyncio.sleep(0.8)
        task.progress = 80.0
        
        await asyncio.sleep(0.8)
        task.progress = 100.0
        
        return {
            "inference_type": "ai_inference",
            "duration": "4.0s",
            "result": "AI推理完成",
            "parameters": task.parameters,
            "version": "0.4.0"
        }
    
    async def _execute_system_maintenance(self, task: TaskModel) -> Dict[str, Any]:
        """执行系统维护任务"""
        logger.info(f"🔧 执行系统维护任务: {task.name}")
        
        await asyncio.sleep(1)
        task.progress = 50.0
        
        await asyncio.sleep(1)
        task.progress = 100.0
        
        return {
            "maintenance_type": "system_maintenance",
            "duration": "2.0s",
            "result": "系统维护完成",
            "parameters": task.parameters,
            "version": "0.4.0"
        }
    
    async def _execute_custom_task(self, task: TaskModel) -> Dict[str, Any]:
        """执行自定义任务"""
        logger.info(f"🎯 执行自定义任务: {task.name}")
        
        await asyncio.sleep(1)
        task.progress = 100.0
        
        return {
            "task_type": "custom",
            "duration": "1.0s",
            "result": "自定义任务完成",
            "parameters": task.parameters,
            "version": "0.4.0"
        }
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = self.get_task(task_id)
        if not task:
            logger.error(f"❌ 任务不存在: {task_id}")
            return False
        
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            logger.warning(f"⚠️ 任务状态不允许取消: {task_id} - {task.status}")
            return False
        
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()
        
        logger.info(f"🚫 任务已取消: {task_id} - {task.name}")
        return True
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
        running_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.RUNNING])
        pending_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "running_tasks": running_tasks,
            "pending_tasks": pending_tasks,
            "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "version": "0.4.0"
        }
