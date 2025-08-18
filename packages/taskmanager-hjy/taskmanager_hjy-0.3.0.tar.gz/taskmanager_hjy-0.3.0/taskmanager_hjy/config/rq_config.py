"""
RQ队列配置模块

提供RQ队列配置、工作进程管理和任务调度功能。
严格遵循云原生公民原则：配置驱动、依赖注入、生命周期管理。
"""

import os
import time
from typing import Optional, Dict, Any, List, Callable
from rq import Queue, Worker
from rq.job import Job, JobStatus
from rq.registry import FailedJobRegistry, FinishedJobRegistry
from loguru import logger

from ..core.config import RQConfig, TaskManagerConfig
from ..utils.redis_helper import RedisHelper, get_redis_helper


class RQConnectionError(Exception):
    """RQ连接错误"""
    pass


class RQQueueManager:
    """
    RQ队列管理器
    
    负责RQ队列的创建、配置和管理。
    提供队列监控、任务调度和工作进程管理。
    """
    
    def __init__(self, config: TaskManagerConfig):
        """
        初始化RQ队列管理器
        
        Args:
            config: 任务管理器配置对象
        """
        self.config = config
        self.redis_helper = get_redis_helper(config.redis)
        self._queues: Dict[str, Queue] = {}
        self._workers: List[Worker] = []
        
        logger.info("RQQueueManager initialized")
    
    def get_queue(self, name: str = "default") -> Queue:
        """
        获取RQ队列
        
        Args:
            name: 队列名称
            
        Returns:
            RQ队列实例
        """
        if name not in self._queues:
            try:
                # 创建Redis连接
                redis_client = self.redis_helper.connection_manager.get_redis_client()
                
                # 创建队列
                queue = Queue(name, connection=redis_client)
                self._queues[name] = queue
                
                logger.info(f"RQ queue '{name}' created successfully")
                
            except Exception as e:
                logger.error(f"Failed to create RQ queue '{name}': {e}")
                raise RQConnectionError(f"Failed to create RQ queue '{name}': {e}")
        
        return self._queues[name]
    
    def enqueue_job(self, func: Callable, args: tuple = None, kwargs: dict = None,
                   queue_name: str = "default", timeout: Optional[int] = None,
                   result_ttl: Optional[int] = None, job_ttl: Optional[int] = None,
                   **job_kwargs) -> Job:
        """
        将任务加入队列
        
        Args:
            func: 要执行的函数
            args: 函数参数
            kwargs: 函数关键字参数
            queue_name: 队列名称
            timeout: 任务超时时间
            result_ttl: 结果缓存时间
            job_ttl: 任务缓存时间
            **job_kwargs: 其他任务参数
            
        Returns:
            任务对象
            
        Raises:
            RQConnectionError: 队列操作失败时抛出
        """
        try:
            queue = self.get_queue(queue_name)
            
            # 使用配置中的默认值
            if timeout is None:
                timeout = self.config.rq.default_timeout
            if result_ttl is None:
                result_ttl = self.config.rq.result_ttl
            if job_ttl is None:
                job_ttl = self.config.rq.job_ttl
            
            # 创建任务
            job = queue.enqueue(
                func,
                args=args or (),
                kwargs=kwargs or {},
                timeout=timeout,
                result_ttl=result_ttl,
                job_ttl=job_ttl,
                **job_kwargs
            )
            
            logger.info(f"Job {job.id} enqueued to queue '{queue_name}'")
            return job
            
        except Exception as e:
            logger.error(f"Failed to enqueue job: {e}")
            raise RQConnectionError(f"Failed to enqueue job: {e}")
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """
        获取任务
        
        Args:
            job_id: 任务ID
            
        Returns:
            任务对象，如果不存在返回None
        """
        try:
            redis_client = self.redis_helper.connection_manager.get_redis_client()
            return Job.fetch(job_id, connection=redis_client)
        except Exception as e:
            logger.error(f"Failed to fetch job {job_id}: {e}")
            return None
    
    def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """
        获取任务状态
        
        Args:
            job_id: 任务ID
            
        Returns:
            任务状态，如果任务不存在返回None
        """
        job = self.get_job(job_id)
        return job.get_status() if job else None
    
    def get_job_result(self, job_id: str) -> Any:
        """
        获取任务结果
        
        Args:
            job_id: 任务ID
            
        Returns:
            任务结果，如果任务不存在或未完成返回None
        """
        job = self.get_job(job_id)
        if job and job.is_finished:
            return job.result
        return None
    
    def cancel_job(self, job_id: str) -> bool:
        """
        取消任务
        
        Args:
            job_id: 任务ID
            
        Returns:
            是否成功取消
        """
        try:
            job = self.get_job(job_id)
            if job and job.get_status() in [JobStatus.QUEUED, JobStatus.STARTED]:
                job.cancel()
                logger.info(f"Job {job_id} cancelled successfully")
                return True
            else:
                logger.warning(f"Cannot cancel job {job_id}: status is {job.get_status() if job else 'not found'}")
                return False
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            return False
    
    def delete_job(self, job_id: str) -> bool:
        """
        删除任务
        
        Args:
            job_id: 任务ID
            
        Returns:
            是否成功删除
        """
        try:
            job = self.get_job(job_id)
            if job:
                job.delete()
                logger.info(f"Job {job_id} deleted successfully")
                return True
            else:
                logger.warning(f"Job {job_id} not found")
                return False
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            return False
    
    def get_queue_stats(self, queue_name: str = "default") -> Dict[str, Any]:
        """
        获取队列统计信息
        
        Args:
            queue_name: 队列名称
            
        Returns:
            队列统计信息
        """
        try:
            queue = self.get_queue(queue_name)
            
            stats = {
                "queue_name": queue_name,
                "length": len(queue),
                "is_empty": queue.is_empty(),
                "job_ids": queue.job_ids,
            }
            
            # 获取失败任务统计
            failed_registry = FailedJobRegistry(queue=queue)
            stats["failed_count"] = len(failed_registry)
            
            # 获取已完成任务统计
            finished_registry = FinishedJobRegistry(queue=queue)
            stats["finished_count"] = len(finished_registry)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get queue stats for '{queue_name}': {e}")
            return {
                "queue_name": queue_name,
                "error": str(e)
            }
    
    def get_all_queue_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有队列的统计信息
        
        Returns:
            所有队列的统计信息
        """
        stats = {}
        for queue_name in self._queues.keys():
            stats[queue_name] = self.get_queue_stats(queue_name)
        return stats
    
    def clear_queue(self, queue_name: str = "default") -> bool:
        """
        清空队列
        
        Args:
            queue_name: 队列名称
            
        Returns:
            是否成功清空
        """
        try:
            queue = self.get_queue(queue_name)
            queue.empty()
            logger.info(f"Queue '{queue_name}' cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to clear queue '{queue_name}': {e}")
            return False
    
    def start_worker(self, queue_names: List[str] = None, **worker_kwargs) -> Worker:
        """
        启动工作进程
        
        Args:
            queue_names: 要监听的队列名称列表
            **worker_kwargs: 工作进程参数
            
        Returns:
            工作进程实例
        """
        try:
            if queue_names is None:
                queue_names = ["default"]
            
            # 获取Redis连接
            redis_client = self.redis_helper.connection_manager.get_redis_client()
            
            # 获取队列列表
            queues = [self.get_queue(name) for name in queue_names]
            
            # 创建并启动工作进程
            worker = Worker(queues, connection=redis_client, **worker_kwargs)
            self._workers.append(worker)
            
            logger.info(f"Worker started for queues: {queue_names}")
            return worker
            
        except Exception as e:
            logger.error(f"Failed to start worker: {e}")
            raise RQConnectionError(f"Failed to start worker: {e}")
    
    def stop_all_workers(self) -> None:
        """停止所有工作进程"""
        for worker in self._workers:
            try:
                worker.shutdown()
                logger.info("Worker stopped")
            except Exception as e:
                logger.error(f"Failed to stop worker: {e}")
        
        self._workers.clear()
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            队列系统是否健康
        """
        try:
            # 检查Redis连接
            if not self.redis_helper.health_check():
                return False
            
            # 检查默认队列
            queue = self.get_queue("default")
            if queue is None:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"RQ health check failed: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        info = {
            "queues": list(self._queues.keys()),
            "workers_count": len(self._workers),
            "redis_connected": self.redis_helper.health_check(),
            "queue_stats": self.get_all_queue_stats()
        }
        
        # 添加Redis连接信息
        redis_info = self.redis_helper.get_connection_info()
        info["redis_info"] = redis_info
        
        return info
    
    def close(self) -> None:
        """关闭队列管理器"""
        try:
            # 停止所有工作进程
            self.stop_all_workers()
            
            # 关闭Redis连接
            self.redis_helper.close()
            
            logger.info("RQQueueManager closed")
            
        except Exception as e:
            logger.error(f"Error closing RQQueueManager: {e}")


# 全局RQ队列管理器实例
_rq_queue_manager: Optional[RQQueueManager] = None


def get_rq_queue_manager(config: TaskManagerConfig) -> RQQueueManager:
    """
    获取RQ队列管理器实例
    
    Args:
        config: 任务管理器配置对象
        
    Returns:
        RQ队列管理器实例
    """
    global _rq_queue_manager
    if _rq_queue_manager is None:
        _rq_queue_manager = RQQueueManager(config)
    return _rq_queue_manager


def close_rq_queue_manager() -> None:
    """关闭RQ队列管理器"""
    global _rq_queue_manager
    if _rq_queue_manager:
        _rq_queue_manager.close()
        _rq_queue_manager = None
