"""
音频分析任务模块

实现音频分析任务，继承自AITask。
专门用于处理音频文件分析。
"""

import os
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from loguru import logger

from .base import AITask, TaskType, TaskContext, TaskError, ValidationError
from .ai_integration import EnhancedAITask


class AudioAnalysisTask(EnhancedAITask):
    """
    音频分析任务
    
    专门用于音频文件分析的任务类型。
    支持多种音频格式和AI分析功能。
    """
    
    def __init__(self, config):
        """初始化音频分析任务"""
        super().__init__(config, TaskType.AUDIO_ANALYSIS)
        
        # 支持的音频格式
        self.supported_formats = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg']
        
        # 最大文件大小（MB）
        self.max_file_size = 100
        
        logger.info("AudioAnalysisTask initialized")
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证音频分析任务输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            是否有效
        """
        try:
            # 检查必需字段
            if not super().validate_input(input_data):
                return False
            
            # 检查音频URL
            audio_url = input_data.get('audio_url')
            if not audio_url:
                logger.error("Missing audio_url field")
                return False
            
            # 验证URL格式
            if not self._is_valid_url(audio_url):
                logger.error(f"Invalid audio URL: {audio_url}")
                return False
            
            # 检查音频格式
            if not self._is_supported_format(audio_url):
                logger.error(f"Unsupported audio format: {audio_url}")
                return False
            
            # 检查文件大小（如果提供）
            file_size = input_data.get('file_size')
            if file_size and file_size > self.max_file_size * 1024 * 1024:
                logger.error(f"File size too large: {file_size} bytes")
                return False
            
            # 检查分析类型
            analysis_type = input_data.get('analysis_type', 'general')
            if analysis_type not in ['general', 'emotion', 'breed', 'health', 'behavior']:
                logger.error(f"Unsupported analysis type: {analysis_type}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Input validation error: {e}")
            return False
    
    def get_required_fields(self) -> List[str]:
        """获取必需的输入字段"""
        return ['audio_url']
    
    def _is_valid_url(self, url: str) -> bool:
        """检查URL是否有效"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _is_supported_format(self, url: str) -> bool:
        """检查音频格式是否支持"""
        path = urlparse(url).path.lower()
        return any(path.endswith(fmt) for fmt in self.supported_formats)
    
    def get_ai_route(self, input_data: Dict[str, Any]) -> str:
        """
        获取AI服务路由
        
        Args:
            input_data: 输入数据
            
        Returns:
            AI服务路由
        """
        analysis_type = input_data.get('analysis_type', 'general')
        
        # 根据分析类型返回不同的路由
        route_mapping = {
            'general': 'ai.audio.analysis.general',
            'emotion': 'ai.audio.analysis.emotion',
            'breed': 'ai.audio.analysis.breed',
            'health': 'ai.audio.analysis.health',
            'behavior': 'ai.audio.analysis.behavior'
        }
        
        return route_mapping.get(analysis_type, 'ai.audio.analysis.general')
    
    def pre_execute(self, context: TaskContext, input_data: Dict[str, Any]) -> None:
        """
        音频分析任务预处理
        
        Args:
            context: 任务执行上下文
            input_data: 输入数据
        """
        super().pre_execute(context, input_data)
        
        # 记录音频信息
        audio_url = input_data.get('audio_url')
        analysis_type = input_data.get('analysis_type', 'general')
        
        logger.info(f"Starting audio analysis: {audio_url}")
        logger.info(f"Analysis type: {analysis_type}")
        
        # 添加到上下文元数据
        context.metadata.update({
            'audio_url': audio_url,
            'analysis_type': analysis_type,
            'file_size': input_data.get('file_size'),
            'duration': input_data.get('duration')
        })
    
    def execute(self, context: TaskContext, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行音频分析任务
        
        Args:
            context: 任务执行上下文
            input_data: 输入数据
            
        Returns:
            分析结果
        """
        try:
            # 获取AI服务路由
            route = self.get_ai_route(input_data)
            
            # 准备AI服务输入数据
            ai_input = self._prepare_ai_input(input_data)
            
            # 调用AI服务
            ai_result = self.call_ai_service(route, ai_input)
            
            # 处理AI服务结果
            result = self.process_ai_result(ai_result, input_data)
            
            # 添加音频分析特定的结果
            result.update(self._add_audio_specific_results(input_data, ai_result))
            
            return result
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return self.handle_ai_error(e, context)
    
    def _prepare_ai_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备AI服务输入数据
        
        Args:
            input_data: 原始输入数据
            
        Returns:
            处理后的输入数据
        """
        return {
            'audio_url': input_data['audio_url'],
            'analysis_type': input_data.get('analysis_type', 'general'),
            'file_size': input_data.get('file_size'),
            'duration': input_data.get('duration'),
            'sample_rate': input_data.get('sample_rate'),
            'channels': input_data.get('channels', 1),
            'format': self._get_audio_format(input_data['audio_url']),
            'metadata': input_data.get('metadata', {})
        }
    
    def _get_audio_format(self, url: str) -> str:
        """获取音频格式"""
        path = urlparse(url).path.lower()
        for fmt in self.supported_formats:
            if path.endswith(fmt):
                return fmt[1:]  # 去掉点号
        return 'unknown'
    
    def _add_audio_specific_results(self, input_data: Dict[str, Any], 
                                   ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加音频分析特定的结果
        
        Args:
            input_data: 输入数据
            ai_result: AI服务结果
            
        Returns:
            额外的结果数据
        """
        return {
            'audio_info': {
                'url': input_data['audio_url'],
                'format': self._get_audio_format(input_data['audio_url']),
                'file_size': input_data.get('file_size'),
                'duration': input_data.get('duration'),
                'sample_rate': input_data.get('sample_rate'),
                'channels': input_data.get('channels', 1)
            },
            'analysis_metadata': {
                'analysis_type': input_data.get('analysis_type', 'general'),
                'processing_time': ai_result.get('processing_time'),
                'model_version': ai_result.get('model_version'),
                'confidence_threshold': ai_result.get('confidence_threshold', 0.7)
            }
        }
    
    def process_ai_result(self, ai_result: Dict[str, Any], 
                         input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理AI服务结果
        
        Args:
            ai_result: AI服务结果
            input_data: 原始输入数据
            
        Returns:
            处理后的结果
        """
        # 基础结果处理
        result = super().process_ai_result(ai_result, input_data)
        
        # 添加音频分析特定的处理
        if ai_result.get('success'):
            # 处理分析结果
            analysis_result = ai_result.get('result', {})
            
            # 根据分析类型处理结果
            analysis_type = input_data.get('analysis_type', 'general')
            if analysis_type == 'emotion':
                result['emotion_analysis'] = self._process_emotion_result(analysis_result)
            elif analysis_type == 'breed':
                result['breed_analysis'] = self._process_breed_result(analysis_result)
            elif analysis_type == 'health':
                result['health_analysis'] = self._process_health_result(analysis_result)
            elif analysis_type == 'behavior':
                result['behavior_analysis'] = self._process_behavior_result(analysis_result)
            else:
                result['general_analysis'] = analysis_result
        
        return result
    
    def _process_emotion_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """处理情绪分析结果"""
        return {
            'primary_emotion': result.get('primary_emotion'),
            'emotion_scores': result.get('emotion_scores', {}),
            'confidence': result.get('confidence', 0.0),
            'intensity': result.get('intensity', 'medium')
        }
    
    def _process_breed_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """处理品种分析结果"""
        return {
            'primary_breed': result.get('primary_breed'),
            'breed_scores': result.get('breed_scores', {}),
            'confidence': result.get('confidence', 0.0),
            'mixed_breed': result.get('mixed_breed', False)
        }
    
    def _process_health_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """处理健康分析结果"""
        return {
            'health_status': result.get('health_status'),
            'anomalies': result.get('anomalies', []),
            'confidence': result.get('confidence', 0.0),
            'recommendations': result.get('recommendations', [])
        }
    
    def _process_behavior_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """处理行为分析结果"""
        return {
            'behavior_type': result.get('behavior_type'),
            'behavior_scores': result.get('behavior_scores', {}),
            'confidence': result.get('confidence', 0.0),
            'context': result.get('context', {})
        }
    
    def post_execute(self, context: TaskContext, result: Dict[str, Any]) -> None:
        """
        音频分析任务后处理
        
        Args:
            context: 任务执行上下文
            result: 执行结果
        """
        super().post_execute(context, result)
        
        # 记录分析结果摘要
        if result.get('success'):
            analysis_type = context.metadata.get('analysis_type', 'general')
            confidence = result.get('confidence', 0.0)
            
            logger.info(f"Audio analysis completed successfully")
            logger.info(f"Analysis type: {analysis_type}")
            logger.info(f"Confidence: {confidence:.2f}")
        else:
            logger.warning("Audio analysis completed with errors")
    
    def cleanup(self, context: TaskContext) -> None:
        """
        清理音频分析任务资源
        
        Args:
            context: 任务执行上下文
        """
        super().cleanup(context)
        
        # 清理临时文件（如果有）
        # 这里可以添加清理临时下载的音频文件的逻辑
        logger.info(f"Audio analysis task cleanup completed for {context.task_id}")


# 注册音频分析任务类型
from .base import TaskFactory
TaskFactory.register(TaskType.AUDIO_ANALYSIS, AudioAnalysisTask)
