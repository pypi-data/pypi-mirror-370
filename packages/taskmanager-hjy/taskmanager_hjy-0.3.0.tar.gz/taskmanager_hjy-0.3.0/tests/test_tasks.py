"""
任务类型测试

测试BaseTask、AITask和AudioAnalysisTask的功能。
"""

import os
import time
import pytest
from unittest.mock import Mock, patch

from taskmanager_hjy.core.config import get_config
from taskmanager_hjy.tasks.base import (
    BaseTask, 
    AITask, 
    SimpleTask,
    TaskType, 
    TaskContext, 
    TaskError, 
    ValidationError,
    TaskFactory
)
from taskmanager_hjy.tasks.audio_analysis import AudioAnalysisTask


class TestTaskType:
    """任务类型测试"""
    
    def test_task_type_values(self):
        """测试任务类型值"""
        assert TaskType.BASE == "base"
        assert TaskType.AI == "ai"
        assert TaskType.AUDIO_ANALYSIS == "audio_analysis"
        assert TaskType.TEXT_ANALYSIS == "text_analysis"
        assert TaskType.IMAGE_ANALYSIS == "image_analysis"
        assert TaskType.CUSTOM == "custom"


class TestTaskContext:
    """任务上下文测试"""
    
    def test_task_context_creation(self):
        """测试任务上下文创建"""
        config = get_config()
        context = TaskContext(
            task_id="test-123",
            task_type="test",
            config=config
        )
        
        assert context.task_id == "test-123"
        assert context.task_type == "test"
        assert context.config == config
        assert context.start_time is not None
        assert context.end_time is None
        assert context.retry_count == 0
        assert context.max_retries == 3
    
    def test_task_context_mark_completed(self):
        """测试任务上下文标记完成"""
        config = get_config()
        context = TaskContext(
            task_id="test-123",
            task_type="test",
            config=config
        )
        
        start_time = context.start_time
        time.sleep(0.1)  # 确保时间戳不同
        
        context.mark_completed()
        
        assert context.end_time is not None
        assert context.end_time > start_time
    
    def test_task_context_execution_time(self):
        """测试任务上下文执行时间"""
        config = get_config()
        context = TaskContext(
            task_id="test-123",
            task_type="test",
            config=config
        )
        
        # 未完成时应该返回None
        assert context.get_execution_time() is None
        
        # 标记完成后应该返回执行时间
        context.mark_completed()
        execution_time = context.get_execution_time()
        assert execution_time is not None
        assert execution_time > 0


class TestSimpleTask:
    """简单任务测试"""
    
    @pytest.fixture
    def config(self):
        """测试配置"""
        os.environ['TASKMANAGER_HJY_REDIS_URL'] = "redis://:N9%24v%238qP%40Xz%217Lm%263rG%5EFw%2AYk2T%23bJs6@r-bp1idjfe6bu4sbbf81pd.redis.rds.aliyuncs.com:6379/0"
        return get_config()
    
    @pytest.fixture
    def simple_task(self, config):
        """简单任务实例"""
        return SimpleTask(config)
    
    def test_simple_task_initialization(self, config):
        """测试简单任务初始化"""
        task = SimpleTask(config)
        assert task.config == config
        assert task.task_type == TaskType.BASE
    
    def test_simple_task_validate_input_valid(self, simple_task):
        """测试简单任务输入验证 - 有效输入"""
        input_data = {"message": "Hello, World!"}
        assert simple_task.validate_input(input_data) is True
    
    def test_simple_task_validate_input_invalid(self, simple_task):
        """测试简单任务输入验证 - 无效输入"""
        input_data = {"other_field": "value"}
        assert simple_task.validate_input(input_data) is False
    
    def test_simple_task_execute(self, simple_task):
        """测试简单任务执行"""
        context = TaskContext(
            task_id="test-123",
            task_type="test",
            config=simple_task.config
        )
        
        input_data = {"message": "Hello, World!"}
        result = simple_task.execute(context, input_data)
        
        assert result["success"] is True
        assert result["message"] == "Processed: Hello, World!"
        assert result["task_id"] == "test-123"
        assert "timestamp" in result
    
    def test_simple_task_run(self, simple_task):
        """测试简单任务运行"""
        input_data = {"message": "Hello, World!"}
        result = simple_task.run("test-123", input_data)
        
        assert result["success"] is True
        assert result["message"] == "Processed: Hello, World!"
        assert result["task_id"] == "test-123"
        assert "execution_time" in result


class TestAITask:
    """AI任务测试"""
    
    @pytest.fixture
    def config(self):
        """测试配置"""
        os.environ['TASKMANAGER_HJY_REDIS_URL'] = "redis://:N9%24v%238qP%40Xz%217Lm%263rG%5EFw%2AYk2T%23bJs6@r-bp1idjfe6bu4sbbf81pd.redis.rds.aliyuncs.com:6379/0"
        return get_config()
    
    @pytest.fixture
    def ai_task(self, config):
        """AI任务实例"""
        return AITask(config)
    
    def test_ai_task_initialization(self, config):
        """测试AI任务初始化"""
        task = AITask(config)
        assert task.config == config
        assert task.task_type == TaskType.AI
        assert task.ai_config == config.ai_service
    
    def test_ai_task_validate_input_valid(self, ai_task):
        """测试AI任务输入验证 - 有效输入"""
        input_data = {"input": "test data"}
        assert ai_task.validate_input(input_data) is True
    
    def test_ai_task_validate_input_invalid(self, ai_task):
        """测试AI任务输入验证 - 无效输入"""
        input_data = {"other_field": "value"}
        assert ai_task.validate_input(input_data) is False
    
    def test_ai_task_get_required_fields(self, ai_task):
        """测试AI任务获取必需字段"""
        required_fields = ai_task.get_required_fields()
        assert "input" in required_fields
    
    def test_ai_task_get_ai_route(self, ai_task):
        """测试AI任务获取AI路由"""
        input_data = {"input": "test"}
        route = ai_task.get_ai_route(input_data)
        assert route == "ai.default"
    
    def test_ai_task_call_ai_service(self, ai_task):
        """测试AI任务调用AI服务"""
        route = "ai.test"
        input_data = {"input": "test"}
        
        result = ai_task.call_ai_service(route, input_data)
        
        assert result["success"] is True
        assert result["route"] == route
        assert "result" in result
        assert "confidence" in result
    
    def test_ai_task_handle_ai_error(self, ai_task):
        """测试AI任务处理AI错误"""
        context = TaskContext(
            task_id="test-123",
            task_type="test",
            config=ai_task.config
        )
        
        error = Exception("AI service error")
        result = ai_task.handle_ai_error(error, context)
        
        assert result["success"] is False
        assert "error" in result
        assert "fallback_result" in result
        assert result["confidence"] == 0.5
    
    def test_ai_task_execute(self, ai_task):
        """测试AI任务执行"""
        context = TaskContext(
            task_id="test-123",
            task_type="test",
            config=ai_task.config
        )
        
        input_data = {"input": "test data"}
        result = ai_task.execute(context, input_data)
        
        assert "success" in result
        assert "result" in result
        assert "confidence" in result
        assert "input_data" in result


class TestAudioAnalysisTask:
    """音频分析任务测试"""
    
    @pytest.fixture
    def config(self):
        """测试配置"""
        os.environ['TASKMANAGER_HJY_REDIS_URL'] = "redis://:N9%24v%238qP%40Xz%217Lm%263rG%5EFw%2AYk2T%23bJs6@r-bp1idjfe6bu4sbbf81pd.redis.rds.aliyuncs.com:6379/0"
        return get_config()
    
    @pytest.fixture
    def audio_task(self, config):
        """音频分析任务实例"""
        return AudioAnalysisTask(config)
    
    def test_audio_task_initialization(self, config):
        """测试音频分析任务初始化"""
        task = AudioAnalysisTask(config)
        assert task.config == config
        assert task.task_type == TaskType.AUDIO_ANALYSIS
        assert len(task.supported_formats) > 0
        assert task.max_file_size == 100
    
    def test_audio_task_validate_input_valid(self, audio_task):
        """测试音频分析任务输入验证 - 有效输入"""
        input_data = {
            "audio_url": "https://example.com/audio.mp3",
            "analysis_type": "general"
        }
        assert audio_task.validate_input(input_data) is True
    
    def test_audio_task_validate_input_missing_url(self, audio_task):
        """测试音频分析任务输入验证 - 缺少URL"""
        input_data = {"analysis_type": "general"}
        assert audio_task.validate_input(input_data) is False
    
    def test_audio_task_validate_input_invalid_url(self, audio_task):
        """测试音频分析任务输入验证 - 无效URL"""
        input_data = {
            "audio_url": "invalid-url",
            "analysis_type": "general"
        }
        assert audio_task.validate_input(input_data) is False
    
    def test_audio_task_validate_input_unsupported_format(self, audio_task):
        """测试音频分析任务输入验证 - 不支持格式"""
        input_data = {
            "audio_url": "https://example.com/audio.xyz",
            "analysis_type": "general"
        }
        assert audio_task.validate_input(input_data) is False
    
    def test_audio_task_validate_input_invalid_analysis_type(self, audio_task):
        """测试音频分析任务输入验证 - 无效分析类型"""
        input_data = {
            "audio_url": "https://example.com/audio.mp3",
            "analysis_type": "invalid_type"
        }
        assert audio_task.validate_input(input_data) is False
    
    def test_audio_task_get_required_fields(self, audio_task):
        """测试音频分析任务获取必需字段"""
        required_fields = audio_task.get_required_fields()
        assert "audio_url" in required_fields
    
    def test_audio_task_is_valid_url(self, audio_task):
        """测试音频分析任务URL验证"""
        assert audio_task._is_valid_url("https://example.com/audio.mp3") is True
        assert audio_task._is_valid_url("http://example.com/audio.wav") is True
        assert audio_task._is_valid_url("invalid-url") is False
        assert audio_task._is_valid_url("") is False
    
    def test_audio_task_is_supported_format(self, audio_task):
        """测试音频分析任务格式验证"""
        assert audio_task._is_supported_format("https://example.com/audio.mp3") is True
        assert audio_task._is_supported_format("https://example.com/audio.wav") is True
        assert audio_task._is_supported_format("https://example.com/audio.xyz") is False
    
    def test_audio_task_get_ai_route(self, audio_task):
        """测试音频分析任务获取AI路由"""
        # 测试不同分析类型的路由
        route_mapping = {
            "general": "ai.audio.analysis.general",
            "emotion": "ai.audio.analysis.emotion",
            "breed": "ai.audio.analysis.breed",
            "health": "ai.audio.analysis.health",
            "behavior": "ai.audio.analysis.behavior"
        }
        
        for analysis_type, expected_route in route_mapping.items():
            input_data = {
                "audio_url": "https://example.com/audio.mp3",
                "analysis_type": analysis_type
            }
            route = audio_task.get_ai_route(input_data)
            assert route == expected_route
    
    def test_audio_task_get_audio_format(self, audio_task):
        """测试音频分析任务获取音频格式"""
        assert audio_task._get_audio_format("https://example.com/audio.mp3") == "mp3"
        assert audio_task._get_audio_format("https://example.com/audio.wav") == "wav"
        assert audio_task._get_audio_format("https://example.com/audio.xyz") == "unknown"
    
    def test_audio_task_prepare_ai_input(self, audio_task):
        """测试音频分析任务准备AI输入"""
        input_data = {
            "audio_url": "https://example.com/audio.mp3",
            "analysis_type": "emotion",
            "file_size": 1024000,
            "duration": 30.5
        }
        
        ai_input = audio_task._prepare_ai_input(input_data)
        
        assert ai_input["audio_url"] == "https://example.com/audio.mp3"
        assert ai_input["analysis_type"] == "emotion"
        assert ai_input["format"] == "mp3"
        assert ai_input["file_size"] == 1024000
        assert ai_input["duration"] == 30.5
        assert ai_input["channels"] == 1
    
    def test_audio_task_process_emotion_result(self, audio_task):
        """测试音频分析任务处理情绪分析结果"""
        result = {
            "primary_emotion": "happy",
            "emotion_scores": {"happy": 0.8, "sad": 0.2},
            "confidence": 0.85,
            "intensity": "high"
        }
        
        processed = audio_task._process_emotion_result(result)
        
        assert processed["primary_emotion"] == "happy"
        assert processed["emotion_scores"] == {"happy": 0.8, "sad": 0.2}
        assert processed["confidence"] == 0.85
        assert processed["intensity"] == "high"
    
    def test_audio_task_execute(self, audio_task):
        """测试音频分析任务执行"""
        context = TaskContext(
            task_id="test-123",
            task_type="audio_analysis",
            config=audio_task.config
        )
        
        input_data = {
            "audio_url": "https://example.com/audio.mp3",
            "analysis_type": "general"
        }
        
        result = audio_task.execute(context, input_data)
        
        assert "success" in result
        assert "audio_info" in result
        assert "analysis_metadata" in result
        assert result["audio_info"]["url"] == "https://example.com/audio.mp3"
        assert result["audio_info"]["format"] == "mp3"


class TestTaskFactory:
    """任务工厂测试"""
    
    def test_task_factory_register(self):
        """测试任务工厂注册"""
        # 清除之前的注册
        TaskFactory._task_registry.clear()
        
        # 注册任务类型
        TaskFactory.register("test_task", SimpleTask)
        
        assert "test_task" in TaskFactory._task_registry
        assert TaskFactory._task_registry["test_task"] == SimpleTask
    
    def test_task_factory_create(self):
        """测试任务工厂创建"""
        config = get_config()
        
        # 注册任务类型
        TaskFactory.register("test_task", SimpleTask)
        
        # 创建任务实例
        task = TaskFactory.create("test_task", config)
        
        assert isinstance(task, SimpleTask)
        assert task.config == config
    
    def test_task_factory_create_unknown_type(self):
        """测试任务工厂创建未知类型"""
        config = get_config()
        
        with pytest.raises(ValueError, match="Unknown task type"):
            TaskFactory.create("unknown_task", config)
    
    def test_task_factory_get_available_types(self):
        """测试任务工厂获取可用类型"""
        # 清除之前的注册
        TaskFactory._task_registry.clear()
        
        # 注册多个任务类型
        TaskFactory.register("task1", SimpleTask)
        TaskFactory.register("task2", AITask)
        
        available_types = TaskFactory.get_available_types()
        
        assert "task1" in available_types
        assert "task2" in available_types
        assert len(available_types) == 2


if __name__ == "__main__":
    pytest.main([__file__])
