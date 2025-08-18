"""
子任务管理器测试

测试SubTaskManager的功能，包括子任务创建、依赖关系、并行和串行执行。
"""

import os
import time
import pytest
from unittest.mock import Mock, patch

from taskmanager_hjy.core.config import get_config
from taskmanager_hjy.manager.subtask_manager import (
    SubTaskManager,
    SubTask,
    ParentTask,
    DependencyType,
    SubTaskStatus,
    get_subtask_manager
)


class TestSubTask:
    """子任务测试"""
    
    def test_subtask_creation(self):
        """测试子任务创建"""
        subtask = SubTask(
            task_id="subtask-123",
            parent_task_id="parent-123",
            task_type="test",
            input_data={"test": "data"}
        )
        
        assert subtask.task_id == "subtask-123"
        assert subtask.parent_task_id == "parent-123"
        assert subtask.task_type == "test"
        assert subtask.input_data == {"test": "data"}
        assert subtask.status == SubTaskStatus.PENDING
        assert subtask.dependencies == []
        assert subtask.dependency_type == DependencyType.SEQUENTIAL
    
    def test_subtask_is_ready_no_dependencies(self):
        """测试无依赖的子任务准备状态"""
        subtask = SubTask(
            task_id="subtask-123",
            parent_task_id="parent-123",
            task_type="test",
            input_data={"test": "data"}
        )
        
        # 无依赖时应该准备就绪
        assert subtask.is_ready(set()) is True
        assert subtask.is_ready({"other-task"}) is True
    
    def test_subtask_is_ready_sequential_dependencies(self):
        """测试串行依赖的子任务准备状态"""
        subtask = SubTask(
            task_id="subtask-123",
            parent_task_id="parent-123",
            task_type="test",
            input_data={"test": "data"},
            dependencies=["dep1", "dep2"],
            dependency_type=DependencyType.SEQUENTIAL
        )
        
        # 所有依赖都完成时准备就绪
        assert subtask.is_ready({"dep1", "dep2"}) is True
        # 部分依赖完成时不准备就绪
        assert subtask.is_ready({"dep1"}) is False
        # 无依赖完成时不准备就绪
        assert subtask.is_ready(set()) is False
    
    def test_subtask_is_ready_parallel_dependencies(self):
        """测试并行依赖的子任务准备状态"""
        subtask = SubTask(
            task_id="subtask-123",
            parent_task_id="parent-123",
            task_type="test",
            input_data={"test": "data"},
            dependencies=["dep1", "dep2"],
            dependency_type=DependencyType.PARALLEL
        )
        
        # 至少一个依赖完成时准备就绪
        assert subtask.is_ready({"dep1"}) is True
        assert subtask.is_ready({"dep2"}) is True
        assert subtask.is_ready({"dep1", "dep2"}) is True
        # 无依赖完成时不准备就绪
        assert subtask.is_ready(set()) is False
    
    def test_subtask_status_transitions(self):
        """测试子任务状态转换"""
        subtask = SubTask(
            task_id="subtask-123",
            parent_task_id="parent-123",
            task_type="test",
            input_data={"test": "data"}
        )
        
        # 初始状态
        assert subtask.status == SubTaskStatus.PENDING
        assert subtask.started_at is None
        assert subtask.completed_at is None
        
        # 标记开始
        subtask.mark_started()
        assert subtask.status == SubTaskStatus.RUNNING
        assert subtask.started_at is not None
        
        # 标记完成
        result = {"success": True}
        subtask.mark_completed(result)
        assert subtask.status == SubTaskStatus.COMPLETED
        assert subtask.completed_at is not None
        assert subtask.result == result
    
    def test_subtask_mark_failed(self):
        """测试子任务标记失败"""
        subtask = SubTask(
            task_id="subtask-123",
            parent_task_id="parent-123",
            task_type="test",
            input_data={"test": "data"}
        )
        
        error_message = "Task failed"
        subtask.mark_failed(error_message)
        
        assert subtask.status == SubTaskStatus.FAILED
        assert subtask.completed_at is not None
        assert subtask.error_message == error_message
    
    def test_subtask_mark_skipped(self):
        """测试子任务标记跳过"""
        subtask = SubTask(
            task_id="subtask-123",
            parent_task_id="parent-123",
            task_type="test",
            input_data={"test": "data"}
        )
        
        subtask.mark_skipped()
        
        assert subtask.status == SubTaskStatus.SKIPPED
        assert subtask.completed_at is not None


class TestParentTask:
    """父任务测试"""
    
    def test_parent_task_creation(self):
        """测试父任务创建"""
        parent_task = ParentTask(task_id="parent-123")
        
        assert parent_task.task_id == "parent-123"
        assert len(parent_task.subtasks) == 0
        assert parent_task.status.value == "pending"
        assert len(parent_task.completed_subtasks) == 0
        assert len(parent_task.failed_subtasks) == 0
    
    def test_parent_task_add_subtask(self):
        """测试父任务添加子任务"""
        parent_task = ParentTask(task_id="parent-123")
        
        subtask = SubTask(
            task_id="subtask-123",
            parent_task_id="parent-123",
            task_type="test",
            input_data={"test": "data"}
        )
        
        parent_task.add_subtask(subtask)
        
        assert len(parent_task.subtasks) == 1
        assert "subtask-123" in parent_task.subtasks
        assert parent_task.subtasks["subtask-123"] == subtask
    
    def test_parent_task_get_ready_subtasks(self):
        """测试父任务获取准备就绪的子任务"""
        parent_task = ParentTask(task_id="parent-123")
        
        # 添加无依赖的子任务
        subtask1 = SubTask(
            task_id="subtask-1",
            parent_task_id="parent-123",
            task_type="test",
            input_data={"test": "data"}
        )
        
        # 添加有依赖的子任务
        subtask2 = SubTask(
            task_id="subtask-2",
            parent_task_id="parent-123",
            task_type="test",
            input_data={"test": "data"},
            dependencies=["subtask-1"]
        )
        
        parent_task.add_subtask(subtask1)
        parent_task.add_subtask(subtask2)
        
        # 初始状态：只有无依赖的子任务准备就绪
        ready_subtasks = parent_task.get_ready_subtasks()
        assert len(ready_subtasks) == 1
        assert ready_subtasks[0].task_id == "subtask-1"
        
        # 完成依赖后：两个子任务都准备就绪
        parent_task.completed_subtasks.add("subtask-1")
        ready_subtasks = parent_task.get_ready_subtasks()
        assert len(ready_subtasks) == 2
    
    def test_parent_task_update_subtask_status(self):
        """测试父任务更新子任务状态"""
        parent_task = ParentTask(task_id="parent-123")
        
        subtask = SubTask(
            task_id="subtask-123",
            parent_task_id="parent-123",
            task_type="test",
            input_data={"test": "data"}
        )
        
        parent_task.add_subtask(subtask)
        
        # 更新为运行状态
        parent_task.update_subtask_status("subtask-123", SubTaskStatus.RUNNING)
        assert parent_task.subtasks["subtask-123"].status == SubTaskStatus.RUNNING
        assert parent_task.subtasks["subtask-123"].started_at is not None
        
        # 更新为完成状态
        result = {"success": True}
        parent_task.update_subtask_status("subtask-123", SubTaskStatus.COMPLETED, result)
        assert parent_task.subtasks["subtask-123"].status == SubTaskStatus.COMPLETED
        assert parent_task.subtasks["subtask-123"].result == result
        assert "subtask-123" in parent_task.completed_subtasks
        
        # 更新为失败状态
        error_message = "Task failed"
        parent_task.update_subtask_status("subtask-123", SubTaskStatus.FAILED, error_message=error_message)
        assert parent_task.subtasks["subtask-123"].status == SubTaskStatus.FAILED
        assert parent_task.subtasks["subtask-123"].error_message == error_message
        assert "subtask-123" in parent_task.failed_subtasks
    
    def test_parent_task_completion_status(self):
        """测试父任务完成状态"""
        parent_task = ParentTask(task_id="parent-123")
        
        # 添加两个子任务
        subtask1 = SubTask("subtask-1", "parent-123", "test", {"test": "data"})
        subtask2 = SubTask("subtask-2", "parent-123", "test", {"test": "data"})
        
        parent_task.add_subtask(subtask1)
        parent_task.add_subtask(subtask2)
        
        # 初始状态
        assert parent_task.is_completed() is False
        assert parent_task.is_failed() is False
        assert parent_task.is_partially_completed() is False
        assert parent_task.get_completion_percentage() == 0.0
        
        # 完成一个子任务
        parent_task.completed_subtasks.add("subtask-1")
        assert parent_task.is_completed() is False
        assert parent_task.is_failed() is False
        assert parent_task.is_partially_completed() is False
        assert parent_task.get_completion_percentage() == 50.0
        
        # 完成所有子任务
        parent_task.completed_subtasks.add("subtask-2")
        assert parent_task.is_completed() is True
        assert parent_task.is_failed() is False
        assert parent_task.is_partially_completed() is False
        assert parent_task.get_completion_percentage() == 100.0
        
        # 失败一个子任务
        parent_task.completed_subtasks.clear()
        parent_task.failed_subtasks.add("subtask-1")
        assert parent_task.is_completed() is False
        assert parent_task.is_failed() is True
        assert parent_task.is_partially_completed() is False
        
        # 部分完成
        parent_task.completed_subtasks.add("subtask-2")
        assert parent_task.is_completed() is False
        assert parent_task.is_failed() is False
        assert parent_task.is_partially_completed() is True


class TestSubTaskManager:
    """子任务管理器测试"""
    
    @pytest.fixture
    def config(self):
        """测试配置"""
        os.environ['TASKMANAGER_HJY_REDIS_URL'] = "redis://:N9%24v%238qP%40Xz%217Lm%263rG%5EFw%2AYk2T%23bJs6@r-bp1idjfe6bu4sbbf81pd.redis.rds.aliyuncs.com:6379/0"
        return get_config()
    
    @pytest.fixture
    def subtask_manager(self, config):
        """子任务管理器实例"""
        return SubTaskManager(config)
    
    def test_subtask_manager_initialization(self, config):
        """测试子任务管理器初始化"""
        manager = SubTaskManager(config)
        assert manager.config == config
        assert len(manager.parent_tasks) == 0
    
    def test_create_parent_task(self, subtask_manager):
        """测试创建父任务"""
        task_id = subtask_manager.create_parent_task("parent-123", {"test": "metadata"})
        
        assert task_id == "parent-123"
        assert "parent-123" in subtask_manager.parent_tasks
        assert subtask_manager.parent_tasks["parent-123"].task_id == "parent-123"
        assert subtask_manager.parent_tasks["parent-123"].metadata == {"test": "metadata"}
    
    def test_add_subtask(self, subtask_manager):
        """测试添加子任务"""
        # 创建父任务
        subtask_manager.create_parent_task("parent-123")
        
        # 添加子任务
        success = subtask_manager.add_subtask(
            parent_task_id="parent-123",
            subtask_id="subtask-123",
            task_type="test",
            input_data={"test": "data"},
            dependencies=["dep1", "dep2"],
            dependency_type=DependencyType.SEQUENTIAL
        )
        
        assert success is True
        
        # 验证子任务已添加
        parent_task = subtask_manager.parent_tasks["parent-123"]
        assert "subtask-123" in parent_task.subtasks
        
        subtask = parent_task.subtasks["subtask-123"]
        assert subtask.task_id == "subtask-123"
        assert subtask.parent_task_id == "parent-123"
        assert subtask.task_type == "test"
        assert subtask.input_data == {"test": "data"}
        assert subtask.dependencies == ["dep1", "dep2"]
        assert subtask.dependency_type == DependencyType.SEQUENTIAL
    
    def test_add_subtask_parent_not_found(self, subtask_manager):
        """测试添加子任务到不存在的父任务"""
        success = subtask_manager.add_subtask(
            parent_task_id="nonexistent",
            subtask_id="subtask-123",
            task_type="test",
            input_data={"test": "data"}
        )
        
        assert success is False
    
    def test_get_ready_subtasks(self, subtask_manager):
        """测试获取准备就绪的子任务"""
        # 创建父任务和子任务
        subtask_manager.create_parent_task("parent-123")
        
        # 添加无依赖的子任务
        subtask_manager.add_subtask("parent-123", "subtask-1", "test", {"test": "data"})
        
        # 添加有依赖的子任务
        subtask_manager.add_subtask(
            "parent-123", "subtask-2", "test", {"test": "data"},
            dependencies=["subtask-1"]
        )
        
        # 获取准备就绪的子任务
        ready_subtasks = subtask_manager.get_ready_subtasks("parent-123")
        assert len(ready_subtasks) == 1
        assert ready_subtasks[0].task_id == "subtask-1"
        
        # 完成依赖后再次获取
        subtask_manager.update_subtask_status("parent-123", "subtask-1", SubTaskStatus.COMPLETED)
        ready_subtasks = subtask_manager.get_ready_subtasks("parent-123")
        assert len(ready_subtasks) == 1
        assert ready_subtasks[0].task_id == "subtask-2"
    
    def test_update_subtask_status(self, subtask_manager):
        """测试更新子任务状态"""
        # 创建父任务和子任务
        subtask_manager.create_parent_task("parent-123")
        subtask_manager.add_subtask("parent-123", "subtask-123", "test", {"test": "data"})
        
        # 更新状态
        success = subtask_manager.update_subtask_status(
            "parent-123", "subtask-123", SubTaskStatus.RUNNING
        )
        assert success is True
        
        # 验证状态已更新
        parent_task = subtask_manager.parent_tasks["parent-123"]
        assert parent_task.subtasks["subtask-123"].status == SubTaskStatus.RUNNING
        
        # 更新为完成状态
        result = {"success": True}
        success = subtask_manager.update_subtask_status(
            "parent-123", "subtask-123", SubTaskStatus.COMPLETED, result
        )
        assert success is True
        assert parent_task.subtasks["subtask-123"].status == SubTaskStatus.COMPLETED
        assert parent_task.subtasks["subtask-123"].result == result
        assert "subtask-123" in parent_task.completed_subtasks
    
    def test_get_parent_task_status(self, subtask_manager):
        """测试获取父任务状态"""
        # 创建父任务和子任务
        subtask_manager.create_parent_task("parent-123")
        subtask_manager.add_subtask("parent-123", "subtask-1", "test", {"test": "data"})
        subtask_manager.add_subtask("parent-123", "subtask-2", "test", {"test": "data"})
        
        # 获取状态
        status = subtask_manager.get_parent_task_status("parent-123")
        assert status is not None
        assert status["task_id"] == "parent-123"
        assert status["total_subtasks"] == 2
        assert status["completed_subtasks"] == 0
        assert status["completion_percentage"] == 0.0
        assert status["is_completed"] is False
        
        # 完成一个子任务
        subtask_manager.update_subtask_status("parent-123", "subtask-1", SubTaskStatus.COMPLETED)
        status = subtask_manager.get_parent_task_status("parent-123")
        assert status["completed_subtasks"] == 1
        assert status["completion_percentage"] == 50.0
    
    def test_get_subtask_status(self, subtask_manager):
        """测试获取子任务状态"""
        # 创建父任务和子任务
        subtask_manager.create_parent_task("parent-123")
        subtask_manager.add_subtask("parent-123", "subtask-123", "test", {"test": "data"})
        
        # 获取状态
        status = subtask_manager.get_subtask_status("parent-123", "subtask-123")
        assert status is not None
        assert status["task_id"] == "subtask-123"
        assert status["parent_task_id"] == "parent-123"
        assert status["task_type"] == "test"
        assert status["status"] == "pending"
        
        # 更新状态后再次获取
        subtask_manager.update_subtask_status("parent-123", "subtask-123", SubTaskStatus.RUNNING)
        status = subtask_manager.get_subtask_status("parent-123", "subtask-123")
        assert status["status"] == "running"
    
    def test_execute_subtasks_sequential(self, subtask_manager):
        """测试串行执行子任务"""
        # 创建父任务和子任务
        subtask_manager.create_parent_task("parent-123")
        subtask_manager.add_subtask("parent-123", "subtask-1", "test", {"test": "data"})
        subtask_manager.add_subtask("parent-123", "subtask-2", "test", {"test": "data"})
        
        # 定义执行函数
        def executor_func(subtask):
            return {"result": f"executed {subtask.task_id}"}
        
        # 串行执行
        success = subtask_manager.execute_subtasks_sequential("parent-123", executor_func)
        assert success is True
        
        # 验证所有子任务都已完成
        parent_task = subtask_manager.parent_tasks["parent-123"]
        assert len(parent_task.completed_subtasks) == 2
    
    def test_retry_failed_subtask(self, subtask_manager):
        """测试重试失败的子任务"""
        # 创建父任务和子任务
        subtask_manager.create_parent_task("parent-123")
        subtask_manager.add_subtask("parent-123", "subtask-123", "test", {"test": "data"})
        
        # 先标记为失败
        subtask_manager.update_subtask_status("parent-123", "subtask-123", SubTaskStatus.FAILED, error_message="Test error")
        
        # 定义执行函数
        def executor_func(subtask):
            return {"result": "retry successful"}
        
        # 重试
        success = subtask_manager.retry_failed_subtask("parent-123", "subtask-123", executor_func)
        assert success is True
        
        # 验证子任务已完成
        parent_task = subtask_manager.parent_tasks["parent-123"]
        assert "subtask-123" in parent_task.completed_subtasks
    
    def test_health_check(self, subtask_manager):
        """测试健康检查"""
        health = subtask_manager.health_check()
        assert isinstance(health, bool)


class TestGlobalFunctions:
    """全局函数测试"""
    
    def test_get_subtask_manager_singleton(self):
        """测试子任务管理器单例模式"""
        # 设置测试环境变量
        os.environ['TASKMANAGER_HJY_REDIS_URL'] = "redis://:N9%24v%238qP%40Xz%217Lm%263rG%5EFw%2AYk2T%23bJs6@r-bp1idjfe6bu4sbbf81pd.redis.rds.aliyuncs.com:6379/0"
        config = get_config()
        
        manager1 = get_subtask_manager(config)
        manager2 = get_subtask_manager(config)
        assert manager1 is manager2


if __name__ == "__main__":
    pytest.main([__file__])
