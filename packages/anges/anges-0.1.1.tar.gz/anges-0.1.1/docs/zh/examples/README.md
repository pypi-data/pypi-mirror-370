<!-- Language: [English](../../examples/README.md) | 中文 -->
# Anges 示例

本目录包含演示 Anges 框架各种功能和使用模式的实用示例代码。

## 可用示例

示例目录包含以下演示文件：

### [`basic_usage.py`](../../../examples/basic_usage.py)
**目的**：演示 Anges 框架的基本用法  
**功能**：创建默认代理、运行简单任务、基本配置  
**适用于**：开始使用 Anges、理解核心概念  

### [`custom_agent.py`](../../../examples/custom_agent.py)
**目的**：展示如何通过扩展 BaseAgent 类创建自定义代理  
**功能**：自定义代理实现、专门行为、代理特定逻辑  
**适用于**：为特定用例构建专门的代理  

### [`custom_action.py`](../../../examples/custom_action.py)
**目的**：演示创建自定义操作来扩展框架功能  
**功能**：自定义操作实现、Git 操作示例、操作集成  
**适用于**：通过自定义操作为代理添加新功能  

### [`orchestrator_demo.py`](../../../examples/orchestrator_demo.py)
**目的**：展示如何使用协调器来协调多个代理  
**功能**：多代理协调、复杂任务委派、编排模式  
**适用于**：使用多个专门代理管理复杂工作流  

## 运行示例

### 前提条件
- 已安装并配置 Anges 框架
- 已设置所需的环境变量（参见主 README.md）
- Python 3.8+ 环境

### 基本用法
```bash
# 从项目根目录运行
cd examples/
python basic_usage.py
```

### 自定义代理示例
```bash
cd examples/
python custom_agent.py
```

### 自定义操作示例
```bash
cd examples/
python custom_action.py
```

### 协调器演示
```bash
cd examples/
python orchestrator_demo.py
```

## 示例结构

每个示例文件包括：
- **头部文档**：示例目的的清晰描述
- **导入语句**：所需的 Anges 框架组件
- **实现**：演示特定功能的工作代码
- **使用函数**：已实现功能的实际演示
- **主执行**：作为脚本运行时的示例用法

## 学习路径

1. **开始**：[`basic_usage.py`](../../../examples/basic_usage.py) 理解核心概念
2. **扩展知识**：[`custom_agent.py`](../../../examples/custom_agent.py) 学习专门代理
3. **添加功能**：[`custom_action.py`](../../../examples/custom_action.py) 学习自定义功能
4. **扩大规模**：[`orchestrator_demo.py`](../../../examples/orchestrator_demo.py) 学习复杂工作流

## 相关文档

- **[实现指南](../implementation-guide.md)**：详细实现说明
- **[API 参考](../api-reference.md)**：完整 API 文档
- **[架构概览](../architecture.md)**：系统设计和概念
- **[主文档](../README.md)**：文档概览和导航