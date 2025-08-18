#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理器命令行工具
"""

import asyncio
import json
import sys
from typing import Any, Dict

from loguru import logger

from .core.manager import TaskManager
from .core.models import TaskStatus, TaskType, TaskPriority


def print_json(data: Any):
    """打印JSON格式数据"""
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1]
    
    try:
        if command == "create":
            create_task_cli()
        elif command == "list":
            list_tasks_cli()
        elif command == "execute":
            execute_task_cli()
        elif command == "cancel":
            cancel_task_cli()
        elif command == "get":
            get_task_cli()
        elif command == "stats":
            get_stats_cli()
        elif command == "help":
            print_help()
        else:
            print(f"❌ 未知命令: {command}")
            print_help()
    except Exception as e:
        logger.error(f"❌ 命令执行失败: {e}")
        sys.exit(1)


def print_help():
    """打印帮助信息"""
    help_text = """
🚀 TaskManager-HJY 命令行工具 (版本 0.4.0)

用法:
  python -m taskmanager_hjy <命令> [参数]

命令:
  create <名称> <类型> [参数]    创建新任务
  list [状态] [类型]            列出任务
  execute <任务ID>              执行任务
  cancel <任务ID>               取消任务
  get <任务ID>                  获取任务详情
  stats                        获取统计信息
  help                         显示帮助

任务类型:
  audio_analysis     音频分析
  data_processing    数据处理
  ai_inference       AI推理
  system_maintenance 系统维护
  custom            自定义任务

任务状态:
  pending           待执行
  running           执行中
  completed         已完成
  failed            失败
  cancelled         已取消

优先级:
  low               低
  normal            普通
  high              高
  urgent            紧急

示例:
  python -m taskmanager_hjy create "测试任务" audio_analysis
  python -m taskmanager_hjy list pending
  python -m taskmanager_hjy execute task_20241201_12345678_abc12345
  python -m taskmanager_hjy stats
"""
    print(help_text)


def create_task_cli():
    """创建任务CLI"""
    if len(sys.argv) < 4:
        print("❌ 用法: create <名称> <类型> [优先级]")
        return
    
    name = sys.argv[2]
    task_type_str = sys.argv[3]
    priority_str = sys.argv[4] if len(sys.argv) > 4 else "normal"
    
    try:
        task_type = TaskType(task_type_str)
        priority = TaskPriority(priority_str)
    except ValueError as e:
        print(f"❌ 无效的参数: {e}")
        return
    
    manager = TaskManager()
    task = manager.create_task(name, task_type, priority=priority)
    
    print("✅ 任务创建成功:")
    print_json(task.dict())


def list_tasks_cli():
    """列出任务CLI"""
    status_str = sys.argv[2] if len(sys.argv) > 2 else None
    task_type_str = sys.argv[3] if len(sys.argv) > 3 else None
    
    status = None
    task_type = None
    
    if status_str:
        try:
            status = TaskStatus(status_str)
        except ValueError:
            print(f"❌ 无效的状态: {status_str}")
            return
    
    if task_type_str:
        try:
            task_type = TaskType(task_type_str)
        except ValueError:
            print(f"❌ 无效的任务类型: {task_type_str}")
            return
    
    manager = TaskManager()
    tasks = manager.list_tasks(status, task_type)
    
    print(f"📋 找到 {len(tasks)} 个任务:")
    for task in tasks:
        print(f"  {task.id}: {task.name} ({task.status.value})")


def execute_task_cli():
    """执行任务CLI"""
    if len(sys.argv) < 3:
        print("❌ 用法: execute <任务ID>")
        return
    
    task_id = sys.argv[2]
    
    async def run():
        manager = TaskManager()
        success = await manager.execute_task(task_id)
        if success:
            print("✅ 任务执行成功")
        else:
            print("❌ 任务执行失败")
    
    asyncio.run(run())


def cancel_task_cli():
    """取消任务CLI"""
    if len(sys.argv) < 3:
        print("❌ 用法: cancel <任务ID>")
        return
    
    task_id = sys.argv[2]
    
    manager = TaskManager()
    success = manager.cancel_task(task_id)
    if success:
        print("✅ 任务取消成功")
    else:
        print("❌ 任务取消失败")


def get_task_cli():
    """获取任务详情CLI"""
    if len(sys.argv) < 3:
        print("❌ 用法: get <任务ID>")
        return
    
    task_id = sys.argv[2]
    
    manager = TaskManager()
    task = manager.get_task(task_id)
    
    if task:
        print("📋 任务详情:")
        print_json(task.dict())
    else:
        print("❌ 任务不存在")


def get_stats_cli():
    """获取统计信息CLI"""
    manager = TaskManager()
    stats = manager.get_task_statistics()
    
    print("📊 任务统计信息:")
    print_json(stats)


if __name__ == "__main__":
    main()
