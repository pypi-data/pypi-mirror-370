**语言**: [English](../README.md) | [中文](README.md)

---
# Anges 文档

欢迎来到 **Anges** 的综合文档，这是一个专为 Linux 环境中多步骤任务执行而设计的 AI 代理框架。此文档中心提供了理解、使用和扩展 Anges 框架所需的一切内容。

## 🚀 快速开始

初次接触 Anges？请按照以下推荐的学习路径：

1. **从这里开始**：阅读[架构概述](#架构文档)了解核心概念
2. **实际演示**：探索[代码示例](#代码示例)查看实际实现
3. **构建您自己的**：遵循[实现指南](#实现指南)创建自定义代理和操作
4. **参考**：使用 [API 参考](#api-参考)获取详细的技术规范

## 📚 文档结构

### 架构文档
**文件**: [`architecture.md`](./architecture.md)

**内容**：涵盖 Anges 核心架构组件的综合技术文档，包括：
- 事件循环系统和执行流程
- 操作系统架构和生命周期
- 代理框架设计模式
- 核心抽象和接口
- 系统集成模式

**适合**：想要了解 Anges 底层工作原理的开发者、系统架构师和项目贡献者。

### API 参考
**文件**: [`api-reference.md`](./api-reference.md)

**内容**：完整的 API 文档框架，提供：
- 核心 API 规范
- 方法签名和参数
- 返回类型和错误处理
- 每个 API 端点的使用示例
- 集成指南

**适合**：将 Anges 集成到现有系统的开发者、API 使用者以及开发过程中需要快速参考的人员。

### 实现指南
**文件**: [`implementation-guide.md`](./implementation-guide.md)

**内容**：使用自定义功能扩展 Anges 的分步说明：
- 创建具有专门行为的自定义代理
- 为特定用例开发自定义操作
- 扩展开发的最佳实践
- 测试和验证策略
- 真实世界的实现模式

**适合**：构建自定义解决方案的开发者、为特定领域扩展 Anges 的团队以及创建专门工作流程的高级用户。

### 文档示例
**目录**: [`examples/`](./examples/)

**内容**：文档中的精选示例和演示：
- 代码片段和使用模式
- 配置示例
- 集成场景
- 最佳实践演示

**适合**：通过示例学习、快速参考和理解文档模式。

## 💻 代码示例

### 项目示例目录
**位置**: [`../examples/`](../examples/)

主要示例目录包含实用的、可运行的代码演示：

#### 可用示例

- **[`basic_usage.py`](../examples/basic_usage.py)**
  - 简单的代理设置和基本任务执行
  - 新用户的完美起点
  - 演示核心工作流程模式

- **[`custom_agent.py`](../examples/custom_agent.py)**
  - 完整的自定义代理实现
  - 展示高级代理自定义技术
  - 包括错误处理和状态管理

- **[`custom_action.py`](../examples/custom_action.py)**
  - 自定义操作开发示例
  - 演示操作生命周期和集成
  - 展示参数处理和验证

- **[`orchestrator_demo.py`](../examples/orchestrator_demo.py)**
  - 高级编排模式
  - 多代理协调示例
  - 复杂工作流程演示

## 🗺️ 文档导航指南

### 新用户
1. **了解基础**：从 [`architecture.md`](./architecture.md) - 事件循环系统部分开始
2. **查看运行**：运行 [`../examples/basic_usage.py`](../examples/basic_usage.py)
3. **学习 API**：浏览 [`api-reference.md`](./api-reference.md) - 入门部分

### 开发者
1. **架构深入**：完整阅读 [`architecture.md`](./architecture.md)
2. **API 精通**：学习 [`api-reference.md`](./api-reference.md) - 核心 API 部分
3. **自定义开发**：遵循 [`implementation-guide.md`](./implementation-guide.md)
4. **高级示例**：探索 [`../examples/custom_agent.py`](../examples/custom_agent.py) 和 [`../examples/custom_action.py`](../examples/custom_action.py)

### 系统集成者
1. **集成模式**：[`architecture.md`](./architecture.md) - 系统集成部分
2. **API 集成**：[`api-reference.md`](./api-reference.md) - 集成指南
3. **编排**：[`../examples/orchestrator_demo.py`](../examples/orchestrator_demo.py)

### 贡献者
1. **完整架构**：[`architecture.md`](./architecture.md)
2. **扩展模式**：[`implementation-guide.md`](./implementation-guide.md)
3. **所有示例**：查看整个 [`../examples/`](../examples/) 目录

## 🔧 快速参考

### 关键概念
- **代理 (Agent)**：处理任务并做出决策的核心 AI 实体
- **操作 (Action)**：代理可以执行的单个操作（shell 命令、文件操作等）
- **事件循环 (Event Loop)**：管理代理-操作交互的执行引擎
- **任务 (Task)**：可能需要多个步骤才能完成的用户请求

### 常见用例
- **系统管理**：自动化复杂的多步骤操作
- **开发工作流程**：智能代码分析和修改
- **数据处理**：多阶段数据转换管道
- **基础设施管理**：自动化部署和配置

## 📖 其他资源

### 文档维护
此文档积极维护和更新。每个文件包括：
- 最后更新时间戳
- 版本兼容性信息
- 主要更新的变更日志

### 获取帮助
- **问题**：报告文档问题或请求改进
- **示例**：为特定用例请求额外示例
- **贡献**：贡献文档的指南

### 文档标准
所有文档遵循一致的格式并包括：
- 清晰的章节标题和导航
- 带有解释的实际示例
- 相关概念之间的交叉引用
- 从基础到高级主题的渐进复杂性

---

**下一步**：根据您的角色和经验水平选择上述路径。每个文档文件都设计为自包含的，同时链接到整个文档集中的相关概念。

*使用 Anges 愉快构建！🚀*