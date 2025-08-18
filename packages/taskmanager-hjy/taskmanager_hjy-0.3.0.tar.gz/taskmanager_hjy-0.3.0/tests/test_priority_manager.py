"""
优先级管理测试

测试PriorityQueue和PriorityManager的功能。
"""

import os
import time
import pytest
from unittest.mock import Mock, patch

from taskmanager_hjy.core.config import get_config
from taskmanager_hjy.manager.priority_manager import (
    PriorityQueue,
    PriorityManager,
    PriorityTask,
    TaskPriority,
    get_priority_manager
)


class TestTaskPriority:
    """任务优先级测试"""
    
    def test_task_priority_values(self):
        """测试任务优先级值"""
        assert TaskPriority.LOW == 1
        assert TaskPriority.NORMAL == 2
        assert TaskPriority.HIGH == 3
        assert TaskPriority.URGENT == 4
        assert TaskPriority.CRITICAL == 5


class TestPriorityTask:
    """优先级任务测试"""
    
    def test_priority_task_creation(self):
        """测试优先级任务创建"""
        task = PriorityTask(
            task_id="test-123",
            priority=TaskPriority.HIGH,
            created_at=time.time(),
            user_id="user_123",
            task_type="test"
        )
        
        assert task.task_id == "test-123"
        assert task.priority == TaskPriority.HIGH
        assert task.user_id == "user_123"
        assert task.task_type == "test"
    
    def test_priority_task_comparison(self):
        """测试优先级任务比较"""
        # 高优先级任务应该排在前面
        high_task = PriorityTask(
            task_id="high",
            priority=TaskPriority.HIGH,
            created_at=time.time()
        )
        
        low_task = PriorityTask(
            task_id="low",
            priority=TaskPriority.LOW,
            created_at=time.time()
        )
        
        assert high_task < low_task  # 高优先级在前
        assert not low_task < high_task
    
    def test_priority_task_same_priority_comparison(self):
        """测试相同优先级任务的比较"""
        # 相同优先级时，先创建的排在前面
        task1 = PriorityTask(
            task_id="task1",
            priority=TaskPriority.NORMAL,
            created_at=time.time()
        )
        
        time.sleep(0.1)  # 确保时间戳不同
        
        task2 = PriorityTask(
            task_id="task2",
            priority=TaskPriority.NORMAL,
            created_at=time.time()
        )
        
        assert task1 < task2  # 先创建的在前


class TestPriorityQueue:
    """优先级队列测试"""
    
    def test_priority_queue_initialization(self):
        """测试优先级队列初始化"""
        queue = PriorityQueue()
        assert queue.size() == 0
        assert queue.is_empty() is True
    
    def test_priority_queue_push_and_pop(self):
        """测试优先级队列的push和pop操作"""
        queue = PriorityQueue()
        
        # 添加任务
        task1 = PriorityTask("task1", TaskPriority.LOW, time.time())
        task2 = PriorityTask("task2", TaskPriority.HIGH, time.time())
        task3 = PriorityTask("task3", TaskPriority.NORMAL, time.time())
        
        queue.push(task1)
        queue.push(task2)
        queue.push(task3)
        
        assert queue.size() == 3
        
        # 应该按优先级顺序弹出
        popped_task = queue.pop()
        assert popped_task.task_id == "task2"  # HIGH优先级
        assert popped_task.priority == TaskPriority.HIGH
        
        popped_task = queue.pop()
        assert popped_task.task_id == "task3"  # NORMAL优先级
        assert popped_task.priority == TaskPriority.NORMAL
        
        popped_task = queue.pop()
        assert popped_task.task_id == "task1"  # LOW优先级
        assert popped_task.priority == TaskPriority.LOW
        
        assert queue.is_empty() is True
    
    def test_priority_queue_peek(self):
        """测试优先级队列的peek操作"""
        queue = PriorityQueue()
        
        # 空队列
        assert queue.peek() is None
        
        # 添加任务
        task = PriorityTask("task1", TaskPriority.HIGH, time.time())
        queue.push(task)
        
        # peek应该返回任务但不移除
        peeked_task = queue.peek()
        assert peeked_task.task_id == "task1"
        assert queue.size() == 1  # 大小不变
    
    def test_priority_queue_remove(self):
        """测试优先级队列的remove操作"""
        queue = PriorityQueue()
        
        # 添加任务
        task1 = PriorityTask("task1", TaskPriority.HIGH, time.time())
        task2 = PriorityTask("task2", TaskPriority.LOW, time.time())
        
        queue.push(task1)
        queue.push(task2)
        
        assert queue.size() == 2
        
        # 移除任务
        success = queue.remove("task1")
        assert success is True
        assert queue.size() == 1
        
        # 移除不存在的任务
        success = queue.remove("nonexistent")
        assert success is False
    
    def test_priority_queue_update_priority(self):
        """测试优先级队列的优先级更新"""
        queue = PriorityQueue()
        
        # 添加任务
        task = PriorityTask("task1", TaskPriority.LOW, time.time())
        queue.push(task)
        
        # 更新优先级
        success = queue.update_priority("task1", TaskPriority.HIGH)
        assert success is True
        
        # 验证优先级已更新
        updated_task = queue.get_task("task1")
        assert updated_task.priority == TaskPriority.HIGH
    
    def test_priority_queue_get_task(self):
        """测试优先级队列的get_task操作"""
        queue = PriorityQueue()
        
        # 获取不存在的任务
        task = queue.get_task("nonexistent")
        assert task is None
        
        # 添加任务
        original_task = PriorityTask("task1", TaskPriority.HIGH, time.time())
        queue.push(original_task)
        
        # 获取任务
        retrieved_task = queue.get_task("task1")
        assert retrieved_task.task_id == "task1"
        assert retrieved_task.priority == TaskPriority.HIGH
    
    def test_priority_queue_get_all_tasks(self):
        """测试优先级队列的get_all_tasks操作"""
        queue = PriorityQueue()
        
        # 添加任务
        task1 = PriorityTask("task1", TaskPriority.LOW, time.time())
        task2 = PriorityTask("task2", TaskPriority.HIGH, time.time())
        task3 = PriorityTask("task3", TaskPriority.NORMAL, time.time())
        
        queue.push(task1)
        queue.push(task2)
        queue.push(task3)
        
        # 获取所有任务（应该按优先级排序）
        all_tasks = queue.get_all_tasks()
        assert len(all_tasks) == 3
        
        # 验证排序
        assert all_tasks[0].priority == TaskPriority.HIGH
        assert all_tasks[1].priority == TaskPriority.NORMAL
        assert all_tasks[2].priority == TaskPriority.LOW
    
    def test_priority_queue_get_tasks_by_priority(self):
        """测试优先级队列的get_tasks_by_priority操作"""
        queue = PriorityQueue()
        
        # 添加不同优先级的任务
        task1 = PriorityTask("task1", TaskPriority.HIGH, time.time())
        task2 = PriorityTask("task2", TaskPriority.HIGH, time.time())
        task3 = PriorityTask("task3", TaskPriority.LOW, time.time())
        
        queue.push(task1)
        queue.push(task2)
        queue.push(task3)
        
        # 获取HIGH优先级的任务
        high_tasks = queue.get_tasks_by_priority(TaskPriority.HIGH)
        assert len(high_tasks) == 2
        
        # 获取LOW优先级的任务
        low_tasks = queue.get_tasks_by_priority(TaskPriority.LOW)
        assert len(low_tasks) == 1
    
    def test_priority_queue_get_priority_stats(self):
        """测试优先级队列的get_priority_stats操作"""
        queue = PriorityQueue()
        
        # 添加任务
        task1 = PriorityTask("task1", TaskPriority.HIGH, time.time())
        task2 = PriorityTask("task2", TaskPriority.HIGH, time.time())
        task3 = PriorityTask("task3", TaskPriority.LOW, time.time())
        
        queue.push(task1)
        queue.push(task2)
        queue.push(task3)
        
        # 获取统计
        stats = queue.get_priority_stats()
        
        assert stats[TaskPriority.HIGH] == 2
        assert stats[TaskPriority.LOW] == 1
        assert stats[TaskPriority.NORMAL] == 0


class TestPriorityManager:
    """优先级管理器测试"""
    
    @pytest.fixture
    def config(self):
        """测试配置"""
        os.environ['TASKMANAGER_HJY_REDIS_URL'] = "redis://:N9%24v%238qP%40Xz%217Lm%263rG%5EFw%2AYk2T%23bJs6@r-bp1idjfe6bu4sbbf81pd.redis.rds.aliyuncs.com:6379/0"
        return get_config()
    
    @pytest.fixture
    def priority_manager(self, config):
        """优先级管理器实例"""
        return PriorityManager(config)
    
    def test_priority_manager_initialization(self, config):
        """测试优先级管理器初始化"""
        manager = PriorityManager(config)
        assert manager.config == config
        assert manager.priority_queue.size() == 0
        assert len(manager.priority_config) == 5  # 5个优先级级别
    
    def test_add_task(self, priority_manager):
        """测试添加任务"""
        success = priority_manager.add_task(
            task_id="test-123",
            priority=TaskPriority.HIGH,
            user_id="user_123",
            task_type="test"
        )
        
        assert success is True
        assert priority_manager.priority_queue.size() == 1
        
        # 验证任务信息
        task = priority_manager.priority_queue.get_task("test-123")
        assert task.task_id == "test-123"
        assert task.priority == TaskPriority.HIGH
        assert task.user_id == "user_123"
        assert task.task_type == "test"
    
    def test_get_next_task(self, priority_manager):
        """测试获取下一个任务"""
        # 添加多个任务
        priority_manager.add_task("task1", TaskPriority.LOW, "user1", "test")
        priority_manager.add_task("task2", TaskPriority.HIGH, "user2", "test")
        priority_manager.add_task("task3", TaskPriority.NORMAL, "user3", "test")
        
        # 应该按优先级顺序获取
        next_task_id = priority_manager.get_next_task()
        assert next_task_id == "task2"  # HIGH优先级
        
        next_task_id = priority_manager.get_next_task()
        assert next_task_id == "task3"  # NORMAL优先级
        
        next_task_id = priority_manager.get_next_task()
        assert next_task_id == "task1"  # LOW优先级
        
        # 队列为空
        next_task_id = priority_manager.get_next_task()
        assert next_task_id is None
    
    def test_update_task_priority(self, priority_manager):
        """测试更新任务优先级"""
        # 添加任务
        priority_manager.add_task("task1", TaskPriority.LOW, "user1", "test")
        
        # 更新优先级
        success = priority_manager.update_task_priority("task1", TaskPriority.HIGH)
        assert success is True
        
        # 验证优先级已更新
        priority = priority_manager.get_task_priority("task1")
        assert priority == TaskPriority.HIGH
    
    def test_remove_task(self, priority_manager):
        """测试移除任务"""
        # 添加任务
        priority_manager.add_task("task1", TaskPriority.HIGH, "user1", "test")
        assert priority_manager.priority_queue.size() == 1
        
        # 移除任务
        success = priority_manager.remove_task("task1")
        assert success is True
        assert priority_manager.priority_queue.size() == 0
        
        # 移除不存在的任务
        success = priority_manager.remove_task("nonexistent")
        assert success is False
    
    def test_get_task_priority(self, priority_manager):
        """测试获取任务优先级"""
        # 获取不存在的任务优先级
        priority = priority_manager.get_task_priority("nonexistent")
        assert priority is None
        
        # 添加任务
        priority_manager.add_task("task1", TaskPriority.URGENT, "user1", "test")
        
        # 获取任务优先级
        priority = priority_manager.get_task_priority("task1")
        assert priority == TaskPriority.URGENT
    
    def test_get_queue_stats(self, priority_manager):
        """测试获取队列统计"""
        # 空队列统计
        stats = priority_manager.get_queue_stats()
        assert stats["total_tasks"] == 0
        assert stats["queue_status"] == "empty"
        assert stats["next_task"] is None
        
        # 添加任务后的统计
        priority_manager.add_task("task1", TaskPriority.HIGH, "user1", "test")
        priority_manager.add_task("task2", TaskPriority.LOW, "user2", "test")
        
        stats = priority_manager.get_queue_stats()
        assert stats["total_tasks"] == 2
        assert stats["queue_status"] == "active"
        assert stats["next_task"] is not None
        assert stats["next_task"]["task_id"] == "task1"  # HIGH优先级
        assert stats["priority_distribution"][TaskPriority.HIGH] == 1
        assert stats["priority_distribution"][TaskPriority.LOW] == 1
    
    def test_get_tasks_by_user(self, priority_manager):
        """测试获取用户任务"""
        # 添加用户任务
        priority_manager.add_task("task1", TaskPriority.HIGH, "user1", "test")
        priority_manager.add_task("task2", TaskPriority.LOW, "user1", "test")
        priority_manager.add_task("task3", TaskPriority.NORMAL, "user2", "test")
        
        # 获取user1的任务
        user1_tasks = priority_manager.get_tasks_by_user("user1")
        assert len(user1_tasks) == 2
        
        # 获取user2的任务
        user2_tasks = priority_manager.get_tasks_by_user("user2")
        assert len(user2_tasks) == 1
        
        # 获取不存在的用户任务
        user3_tasks = priority_manager.get_tasks_by_user("user3")
        assert len(user3_tasks) == 0
    
    def test_get_priority_config(self, priority_manager):
        """测试获取优先级配置"""
        config = priority_manager.get_priority_config(TaskPriority.HIGH)
        assert "weight" in config
        assert "max_wait_time" in config
        assert config["weight"] == 4
        assert config["max_wait_time"] == 900  # 15分钟
    
    def test_calculate_priority_score(self, priority_manager):
        """测试计算优先级分数"""
        # 添加任务
        priority_manager.add_task("task1", TaskPriority.HIGH, "user1", "test")
        
        # 计算分数
        score = priority_manager.calculate_priority_score("task1")
        assert score > 0
        
        # 计算不存在的任务分数
        score = priority_manager.calculate_priority_score("nonexistent")
        assert score == 0.0
    
    def test_health_check(self, priority_manager):
        """测试健康检查"""
        health = priority_manager.health_check()
        assert isinstance(health, bool)


class TestGlobalFunctions:
    """全局函数测试"""
    
    def test_get_priority_manager_singleton(self):
        """测试优先级管理器单例模式"""
        # 设置测试环境变量
        os.environ['TASKMANAGER_HJY_REDIS_URL'] = "redis://:N9%24v%238qP%40Xz%217Lm%263rG%5EFw%2AYk2T%23bJs6@r-bp1idjfe6bu4sbbf81pd.redis.rds.aliyuncs.com:6379/0"
        config = get_config()
        
        manager1 = get_priority_manager(config)
        manager2 = get_priority_manager(config)
        assert manager1 is manager2


if __name__ == "__main__":
    pytest.main([__file__])
