"""
AI集成模块

实现与ai_runner_hjy的集成，提供AI服务调用和结果处理功能。
严格遵循苹果产品原则：高内聚、低耦合、简洁接口。
"""

import time
from typing import Any, Dict, Optional, List
from loguru import logger

try:
    from ai_runner_hjy import run_route
    AI_RUNNER_AVAILABLE = True
except ImportError:
    AI_RUNNER_AVAILABLE = False
    logger.warning("ai_runner_hjy not available, using mock implementation")

from .base import AITask, TaskContext, TaskError


class AIIntegrationError(Exception):
    """AI集成错误"""
    pass


class AIServiceClient:
    """
    AI服务客户端
    
    封装与ai_runner_hjy的交互，提供统一的AI服务调用接口。
    """
    
    def __init__(self, config):
        """
        初始化AI服务客户端
        
        Args:
            config: 任务管理器配置
        """
        self.config = config
        self.ai_config = config.ai_service
        self.logger = logger.bind(service="ai_client")
        
        if not AI_RUNNER_AVAILABLE:
            self.logger.warning("Using mock AI service client")
        
        self.logger.info("AIServiceClient initialized")
    
    def call_route(self, route: str, input_data: Dict[str, Any], 
                  timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        调用AI服务路由
        
        Args:
            route: AI服务路由
            input_data: 输入数据
            timeout: 超时时间（秒）
            
        Returns:
            AI服务响应
            
        Raises:
            AIIntegrationError: AI服务调用失败时抛出
        """
        try:
            self.logger.info(f"Calling AI route: {route}")
            
            if AI_RUNNER_AVAILABLE:
                # 使用真实的ai_runner_hjy
                return self._call_real_ai_service(route, input_data, timeout)
            else:
                # 使用模拟实现
                return self._call_mock_ai_service(route, input_data, timeout)
                
        except Exception as e:
            self.logger.error(f"AI service call failed: {e}")
            raise AIIntegrationError(f"AI service call failed: {e}")
    
    def _call_real_ai_service(self, route: str, input_data: Dict[str, Any], 
                             timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        调用真实的AI服务
        
        Args:
            route: AI服务路由
            input_data: 输入数据
            timeout: 超时时间
            
        Returns:
            AI服务响应
        """
        try:
            # 准备调用参数
            call_kwargs = {
                'route': route,
                'input_data': input_data
            }
            
            # 添加超时配置
            if timeout:
                call_kwargs['timeout'] = timeout
            elif self.ai_config.timeout:
                call_kwargs['timeout'] = self.ai_config.timeout
            
            # 调用ai_runner_hjy
            start_time = time.time()
            result = run_route(**call_kwargs)
            end_time = time.time()
            
            # 处理响应
            response = {
                'success': True,
                'route': route,
                'result': result,
                'processing_time': end_time - start_time,
                'timestamp': end_time
            }
            
            self.logger.info(f"AI service call successful: {route}")
            return response
            
        except Exception as e:
            self.logger.error(f"Real AI service call failed: {e}")
            raise AIIntegrationError(f"Real AI service call failed: {e}")
    
    def _call_mock_ai_service(self, route: str, input_data: Dict[str, Any], 
                             timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        调用模拟AI服务
        
        Args:
            route: AI服务路由
            input_data: 输入数据
            timeout: 超时时间
            
        Returns:
            模拟AI服务响应
        """
        import random
        
        # 模拟网络延迟
        delay = random.uniform(0.1, 0.5)
        if timeout and delay > timeout:
            raise AIIntegrationError("Request timeout")
        
        time.sleep(delay)
        
        # 根据路由生成不同的模拟结果
        mock_results = {
            'ai.audio.analysis.general': {
                'analysis_type': 'general',
                'confidence': random.uniform(0.7, 0.95),
                'summary': 'General audio analysis completed',
                'features': ['duration', 'format', 'quality']
            },
            'ai.audio.analysis.emotion': {
                'analysis_type': 'emotion',
                'primary_emotion': random.choice(['happy', 'sad', 'excited', 'calm']),
                'emotion_scores': {
                    'happy': random.uniform(0.0, 1.0),
                    'sad': random.uniform(0.0, 1.0),
                    'excited': random.uniform(0.0, 1.0),
                    'calm': random.uniform(0.0, 1.0)
                },
                'confidence': random.uniform(0.7, 0.95),
                'intensity': random.choice(['low', 'medium', 'high'])
            },
            'ai.audio.analysis.breed': {
                'analysis_type': 'breed',
                'primary_breed': random.choice(['Golden Retriever', 'Labrador', 'German Shepherd', 'Poodle']),
                'breed_scores': {
                    'Golden Retriever': random.uniform(0.0, 1.0),
                    'Labrador': random.uniform(0.0, 1.0),
                    'German Shepherd': random.uniform(0.0, 1.0),
                    'Poodle': random.uniform(0.0, 1.0)
                },
                'confidence': random.uniform(0.7, 0.95),
                'mixed_breed': random.choice([True, False])
            },
            'ai.audio.analysis.health': {
                'analysis_type': 'health',
                'health_status': random.choice(['healthy', 'attention_needed', 'warning']),
                'anomalies': random.sample(['breathing_irregular', 'coughing', 'whining'], random.randint(0, 2)),
                'confidence': random.uniform(0.7, 0.95),
                'recommendations': ['Regular checkup recommended']
            },
            'ai.audio.analysis.behavior': {
                'analysis_type': 'behavior',
                'behavior_type': random.choice(['playful', 'aggressive', 'fearful', 'curious']),
                'behavior_scores': {
                    'playful': random.uniform(0.0, 1.0),
                    'aggressive': random.uniform(0.0, 1.0),
                    'fearful': random.uniform(0.0, 1.0),
                    'curious': random.uniform(0.0, 1.0)
                },
                'confidence': random.uniform(0.7, 0.95),
                'context': {'environment': 'indoor', 'time_of_day': 'afternoon'}
            }
        }
        
        # 获取模拟结果
        mock_result = mock_results.get(route, {
            'analysis_type': 'unknown',
            'confidence': random.uniform(0.5, 0.8),
            'message': f'Mock analysis for route: {route}'
        })
        
        response = {
            'success': True,
            'route': route,
            'result': mock_result,
            'processing_time': delay,
            'timestamp': time.time(),
            'model_version': 'mock-v1.0',
            'confidence_threshold': 0.7
        }
        
        self.logger.info(f"Mock AI service call successful: {route}")
        return response
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            是否健康
        """
        try:
            if AI_RUNNER_AVAILABLE:
                # 尝试调用一个简单的测试路由
                test_result = self._call_real_ai_service('ai.test', {'test': True}, timeout=5)
                return test_result.get('success', False)
            else:
                # 模拟健康检查
                return True
        except Exception as e:
            self.logger.error(f"AI service health check failed: {e}")
            return False
    
    def get_available_routes(self) -> List[str]:
        """
        获取可用的AI路由
        
        Returns:
            可用路由列表
        """
        if AI_RUNNER_AVAILABLE:
            # 这里应该从ai_runner_hjy获取可用路由
            # 暂时返回预定义的路由
            return [
                'ai.audio.analysis.general',
                'ai.audio.analysis.emotion',
                'ai.audio.analysis.breed',
                'ai.audio.analysis.health',
                'ai.audio.analysis.behavior'
            ]
        else:
            # 返回模拟路由
            return [
                'ai.audio.analysis.general',
                'ai.audio.analysis.emotion',
                'ai.audio.analysis.breed',
                'ai.audio.analysis.health',
                'ai.audio.analysis.behavior'
            ]


class EnhancedAITask(AITask):
    """
    增强的AI任务
    
    集成ai_runner_hjy的AI任务基类。
    提供更强大的AI服务调用和错误处理功能。
    """
    
    def __init__(self, config, task_type: str = "enhanced_ai"):
        """
        初始化增强AI任务
        
        Args:
            config: 任务管理器配置
            task_type: 任务类型
        """
        super().__init__(config, task_type)
        
        # 创建AI服务客户端
        self.ai_client = AIServiceClient(config)
        
        self.logger.info(f"EnhancedAITask initialized for type: {task_type}")
    
    def call_ai_service(self, route: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用AI服务
        
        Args:
            route: AI服务路由
            input_data: 输入数据
            
        Returns:
            AI服务响应
        """
        try:
            # 使用AI服务客户端
            timeout = getattr(self.ai_config, 'timeout', None)
            return self.ai_client.call_route(route, input_data, timeout)
            
        except Exception as e:
            self.logger.error(f"Enhanced AI service call failed: {e}")
            raise TaskError(f"Enhanced AI service call failed: {e}")
    
    def handle_ai_error(self, error: Exception, context: TaskContext) -> Dict[str, Any]:
        """
        处理AI服务错误
        
        Args:
            error: 错误信息
            context: 任务执行上下文
            
        Returns:
            错误处理结果
        """
        self.logger.warning(f"Handling enhanced AI error for task {context.task_id}: {error}")
        
        # 检查是否是AI集成错误
        if isinstance(error, AIIntegrationError):
            # AI服务不可用，返回降级结果
            return {
                'success': False,
                'error': str(error),
                'error_type': 'ai_service_unavailable',
                'fallback_result': 'Service temporarily unavailable',
                'confidence': 0.0,
                'recommendation': 'Please try again later'
            }
        else:
            # 其他错误，使用默认处理
            return super().handle_ai_error(error, context)
    
    def validate_ai_service(self) -> bool:
        """
        验证AI服务可用性
        
        Returns:
            是否可用
        """
        return self.ai_client.health_check()
    
    def get_ai_routes(self) -> List[str]:
        """
        获取可用的AI路由
        
        Returns:
            可用路由列表
        """
        return self.ai_client.get_available_routes()
    
    def pre_execute(self, context: TaskContext, input_data: Dict[str, Any]) -> None:
        """
        增强AI任务预处理
        
        Args:
            context: 任务执行上下文
            input_data: 输入数据
        """
        super().pre_execute(context, input_data)
        
        # 验证AI服务可用性
        if not self.validate_ai_service():
            self.logger.warning(f"AI service not available for task {context.task_id}")
            context.metadata['ai_service_available'] = False
        else:
            context.metadata['ai_service_available'] = True
        
        # 记录可用路由
        available_routes = self.get_ai_routes()
        context.metadata['available_routes'] = available_routes
        
        self.logger.info(f"Enhanced AI task pre-execution completed for {context.task_id}")


class AIErrorHandler:
    """
    AI错误处理器
    
    提供统一的AI错误处理和重试机制。
    """
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        """
        初始化AI错误处理器
        
        Args:
            max_retries: 最大重试次数
            base_delay: 基础延迟时间
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.logger = logger.bind(handler="ai_error")
    
    def should_retry(self, error: Exception, retry_count: int) -> bool:
        """
        判断是否应该重试
        
        Args:
            error: 错误信息
            retry_count: 当前重试次数
            
        Returns:
            是否应该重试
        """
        if retry_count >= self.max_retries:
            return False
        
        # 检查错误类型
        if isinstance(error, AIIntegrationError):
            # AI集成错误可以重试
            return True
        elif isinstance(error, TaskError):
            # 任务错误根据retryable属性决定
            return getattr(error, 'retryable', True)
        else:
            # 其他错误默认不重试
            return False
    
    def get_retry_delay(self, retry_count: int) -> float:
        """
        获取重试延迟时间
        
        Args:
            retry_count: 当前重试次数
            
        Returns:
            重试延迟时间
        """
        # 指数退避策略
        return self.base_delay * (2 ** retry_count)
    
    def handle_error(self, error: Exception, context: TaskContext) -> Dict[str, Any]:
        """
        处理错误
        
        Args:
            error: 错误信息
            context: 任务执行上下文
            
        Returns:
            错误处理结果
        """
        self.logger.error(f"Handling AI error: {error}")
        
        # 根据错误类型返回不同的处理结果
        if isinstance(error, AIIntegrationError):
            return {
                'success': False,
                'error_type': 'ai_service_error',
                'error_message': str(error),
                'retryable': True,
                'recommendation': 'Check AI service availability'
            }
        elif isinstance(error, TaskError):
            return {
                'success': False,
                'error_type': 'task_error',
                'error_message': str(error),
                'retryable': getattr(error, 'retryable', True),
                'recommendation': 'Review task configuration'
            }
        else:
            return {
                'success': False,
                'error_type': 'unknown_error',
                'error_message': str(error),
                'retryable': False,
                'recommendation': 'Contact support'
            }


# 全局AI服务客户端实例
_ai_client: Optional[AIServiceClient] = None


def get_ai_client(config) -> AIServiceClient:
    """
    获取AI服务客户端实例
    
    Args:
        config: 任务管理器配置
        
    Returns:
        AI服务客户端实例
    """
    global _ai_client
    if _ai_client is None:
        _ai_client = AIServiceClient(config)
    return _ai_client


def close_ai_client() -> None:
    """关闭AI服务客户端"""
    global _ai_client
    if _ai_client:
        _ai_client = None
