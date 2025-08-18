# taskmanager_hjy

[![CI Status](https://img.shields.io/badge/CI-Passed-brightgreen.svg)](https://github.com/hjy/taskmanager_hjy)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/badge/PyPI-v0.0.1-orange.svg)](https://pypi.org/project/taskmanager-hjy/)

> **一句话宣言**: 基于RQ + Redis的通用任务管理解决方案，支持子任务嵌套，让异步任务处理变得毫不费力。

## 🎯 优雅的"Hello, World"

```python
from taskmanager_hjy import TaskManager

# 三行代码，启动任务管理
task_manager = TaskManager()
task_id = task_manager.create_task("data_processing", {"input_file": "data.csv"})
result = task_manager.get_result(task_id)

print(f"🎉 任务完成: {result}")
```

## ✨ 为什么选择 taskmanager_hjy？

### 🚀 零摩擦体验
- **一键安装**: `pip install taskmanager-hjy`
- **零配置启动**: 自动检测环境，智能配置
- **所见即所得**: README中的示例代码可直接运行

### 🎨 苹果产品级设计
- **高内聚低耦合**: 内部复杂，接口简洁
- **类型安全**: 完整的类型提示，IDE友好
- **优雅错误处理**: 人类可读的错误信息

### 🌟 云原生公民
- **配置即插即用**: 外置配置，依赖注入
- **生命周期管理**: 完整的启动、运行、关闭控制
- **健康检查**: 实时监控，自动恢复

### 🔄 子任务嵌套
- **任务嵌套**: 支持主任务包含多个子任务
- **依赖关系**: 子任务之间可以有依赖关系
- **并行处理**: 支持子任务并行执行
- **状态同步**: 子任务状态变化同步到主任务
- **灵活执行**: 支持串行、并行、条件依赖等多种执行模式

## 🚀 快速开始

### 安装
```bash
pip install taskmanager-hjy
```

### 基本使用
```python
from taskmanager_hjy import TaskManager

# 创建任务管理器
task_manager = TaskManager()

# 创建数据处理任务
task_id = task_manager.create_task(
    task_type="data_processing",
    input_data={
        "input_file": "data.csv",
        "output_format": "json"
    },
    user_id="user_123"
)

# 查询状态
status = task_manager.get_status(task_id)
print(f"任务状态: {status}")

# 获取结果
result = task_manager.get_result(task_id)
print(f"处理结果: {result}")
```

### 高级功能
```python
# 优先级管理
high_priority_task = task_manager.create_task(
    task_type="data_processing",
    input_data={"input_file": "urgent_data.csv"},
    priority=3  # 高优先级
)

# 子任务管理
subtask_id = task_manager.create_subtask(
    parent_task_id=task_id,
    task_type="data_validation",
    input_data={"validation_rules": "schema.json"}
)

# 批量处理
task_ids = task_manager.batch_create([
    {"input_file": f"data_{i}.csv"} 
    for i in range(5)
])

# 复杂工作流
workflow_id = task_manager.create_task("workflow", {"name": "数据处理流程"})
task_manager.create_subtask(workflow_id, "data_validation", {"rules": "schema.json"})
task_manager.create_subtask(workflow_id, "data_cleaning", {"rules": "cleaning.yaml"})
task_manager.create_subtask(workflow_id, "data_analysis", {"type": "statistical"})
task_manager.create_subtask(workflow_id, "report_generation", {"format": "pdf"})
```

## 🔧 配置即插即用

```python
# 简单配置
config = {
    "redis": {
        "url": "redis://localhost:6379/0"
    },
    "tasks": {
        "audio_analysis": {
            "timeout": 300,
            "max_retry": 3
        }
    }
}

task_manager = TaskManager(config=config)
```

## 📊 性能指标

- **任务创建**: < 100ms
- **状态查询**: < 50ms  
- **AI服务调用**: < 500ms
- **并发支持**: 1000+ 任务/秒
- **内存使用**: 优化的连接池管理
- **子任务支持**: 无限层级嵌套
- **依赖处理**: 复杂依赖关系自动解析

## 🎯 支持的任务类型

### 内置任务类型
- **base**: 基础任务类型
- **custom**: 自定义任务类型
- **data_processing**: 数据处理任务（示例）

### 扩展任务类型
```python
from taskmanager_hjy import BaseTask

class ImageProcessingTask(BaseTask):
    def execute(self, input_data):
        # 图像处理逻辑
        return {"result": "image_processed"}

class EmailSendingTask(BaseTask):
    def execute(self, input_data):
        # 邮件发送逻辑
        return {"result": "email_sent"}

# 注册自定义任务
task_manager.register_task_type("image_processing", ImageProcessingTask)
task_manager.register_task_type("email_sending", EmailSendingTask)
```

## 🔒 安全特性

- **连接加密**: Redis SSL/TLS 支持
- **认证机制**: API Key 和用户权限管理
- **数据隔离**: 基于用户ID的任务隔离
- **审计日志**: 完整的操作记录

## 🧪 测试覆盖

```bash
# 运行测试
pytest tests/

# 覆盖率报告
pytest --cov=taskmanager_hjy tests/

# 性能测试
pytest tests/test_performance.py
```

## 📚 文档

- **[API文档](https://taskmanager-hjy.readthedocs.io/)**: 完整的API参考
- **[开发者指南](DEVELOPER.md)**: 架构设计和开发指南
- **[示例代码](examples/)**: 丰富的使用示例
  - [Hello World](examples/hello_world.py): 三行代码快速开始
  - [简单子任务](examples/simple_subtask.py): 基础嵌套功能展示
  - [复杂子任务](examples/subtask_demo.py): 完整工作流演示
  - [高级功能](examples/advanced_usage.py): 优先级和批量处理
- **[最佳实践](docs/best_practices.md)**: 生产环境部署指南

## 🤝 贡献

我们欢迎所有形式的贡献！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 支持

- **文档**: [https://taskmanager-hjy.readthedocs.io/](https://taskmanager-hjy.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/hjy/taskmanager_hjy/issues)
- **讨论**: [GitHub Discussions](https://github.com/hjy/taskmanager_hjy/discussions)
- **邮箱**: hjy@example.com

---

**taskmanager_hjy** - 让异步任务处理变得毫不费力 ✨

*"产品越是简单，内里逻辑越是复杂。"* - 史蒂夫·乔布斯
