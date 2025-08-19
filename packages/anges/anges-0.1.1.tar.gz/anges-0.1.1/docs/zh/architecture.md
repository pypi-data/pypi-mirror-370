**语言**: [English](../architecture.md) | [中文](architecture.md)

---

# Anges 架构文档

## 概述

本文档为 Anges 项目的核心架构组件提供详细的技术文档。Anges 是一个专为 Linux 环境中多步骤任务执行而设计的 AI 代理框架。

## 目录

- [事件循环系统](#事件循环系统)
- [动作系统架构](#动作系统架构)
- [提示构建](#提示构建)
- [系统集成](#系统集成)
- [设计模式](#设计模式)
- [扩展点](#扩展点)

## 事件循环系统

事件循环系统是管理代理交互生命周期的核心编排机制，从用户输入到任务完成。

### 事件架构

#### 事件类结构

`Event` 类（定义在 `anges/agents/agent_utils/events.py` 中）作为交互跟踪的基本单元：

```python
class Event:
    def __init__(self, type, reasoning="", content="", analysis="", message="", 
                 est_input_token=0, est_output_token=0):
        self.id = generate_random_id()
        self.type = type  # 事件类型标识符
        self.reasoning = reasoning  # 代理执行动作的推理
        self.content = content  # 动作输出或用户输入
        self.analysis = analysis  # 内部分析（不显示给用户）
        self.message = message  # 用户可见消息
        self.timestamp = datetime.now().isoformat()
        self.est_input_token = est_input_token
        self.est_output_token = est_output_token
```

#### 事件类型

系统定义了几种控制代理行为的关键事件类型：

- **`new_request`**: 启动新任务的初始用户输入
- **`action`**: 代理执行的 shell 命令及其结果
- **`edit_file`**: 文件修改操作
- **`task_completion`**: 成功任务完成及摘要
- **`agent_requested_help`**: 代理请求人工干预

## BaseAgent 类架构

`BaseAgent` 类是 Anges 框架中所有代理实现的基础。它为事件处理、动作执行和任务管理提供核心功能。

### 类定义

```python
class BaseAgent:
    def __init__(
        self,
        parent_ids=[],
        inference_func=None,
        event_stream=None,
        cmd_init_dir=config.agents.default_agent.cmd_init_dir,
        prefix_cmd="",
        interrupt_check=None,
        max_consecutive_actions_to_summarize=config.agents.default_agent.max_consecutive_actions_to_summarize,
        logging_level=logging.DEBUG,
        auto_entitle=False,
    )
```

### 关键属性

- **parent_ids**: 用于分层代理关系的父事件流 UID 列表
- **event_stream**: 管理执行历史的 EventStream 实例
- **inference_func**: 用于 LLM 推理调用的函数
- **cmd_init_dir**: 命令执行的初始目录
- **prefix_cmd**: shell 操作的命令前缀
- **interrupt_check**: 检查用户中断请求的函数
- **status**: 当前代理状态（"new"、"running"、"completed" 等）
- **uid**: 唯一标识符（继承自 event_stream.uid）
- **max_consecutive_actions_to_summarize**: 事件摘要的阈值
- **message_handlers**: 处理用户可见消息的函数列表
- **agent_prompt_template**: 构建代理提示的模板
- **auto_entitle**: 是否自动生成对话标题
- **agent_config**: 代理行为的配置对象
- **registered_actions**: 可用动作类型列表

### 核心方法

#### `handle_user_visible_messages(message: str)`
通过调用所有注册的消息处理器来处理用户可见消息。为前端接口提供直接消息传递。

#### `run_with_new_request(task_description, event_stream=None)`
主执行方法，执行以下操作：
1. 向事件流添加新请求事件
2. 进入主执行循环
3. 检查中断和耗尽条件
4. 预测和处理下一个动作
5. 返回最终事件流

#### `_build_run_config(task_description, event_stream)`
构建包含动作执行所需所有上下文的运行时配置字典。

#### `_handle_received_new_request(run_config)`
处理新任务请求并向流中添加适当的事件。如果启用，处理自动标题生成。

#### `_check_interruption(run_config)`
检查用户中断请求并处理优雅的任务终止。

#### `_check_exhausted(run_config)`
监控事件计数限制并防止无限执行循环。

#### `_prompt_and_get_action_from_response(event_stream)`
从事件历史构建提示并将 LLM 响应解析为可执行命令。

#### `_prefict_next_event_and_handle_actions(event_stream, run_config)`
执行预测的动作并管理动作执行流程。

### 代理生命周期

1. **初始化**: 使用配置参数创建代理
2. **请求处理**: 接收并处理新任务请求
3. **执行循环**: 代理持续预测和执行动作
4. **中断检查**: 定期检查用户中断或耗尽
5. **动作执行**: 基于 LLM 预测执行单个动作
6. **完成**: 任务完成并返回最终事件流状态

### 事件流集成

BaseAgent 与 EventStream 系统紧密集成：
- 所有动作生成添加到流中的事件
- 当达到连续动作限制时创建事件摘要
- 通过事件流 UID 维护父子关系
- 通过保存操作自动处理事件持久化

所有动作都继承自基础 `Action` 类（定义在 `anges/agents/agent_utils/agent_actions.py` 中）：

```python
class Action:
    def __init__(self):
        self.type = ""  # 唯一动作标识符
        self.guide_prompt = ""  # 代理文档
        self.user_visible = False  # 动作结果是否显示给用户
        self.unique_action = False  # 动作是否必须单独使用
        self.returning_action = False  # 动作是否终止循环

    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        raise NotImplementedError("子类必须实现此方法")
```

### 动作系统架构

动作系统通过基于类的架构为代理能力提供模块化、可扩展的框架。

### 动作基类

所有动作都继承自基础 `Action` 类（定义在 `anges/agents/agent_utils/agent_actions.py` 中）：

```python
class Action:
    def __init__(self):
        self.type = ""  # 唯一动作标识符
        self.guide_prompt = ""  # 代理文档
        self.user_visible = False  # 动作结果是否显示给用户
        self.unique_action = False  # 动作是否必须单独使用
        self.returning_action = False  # 动作是否终止执行

    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        raise NotImplementedError("子类必须实现此方法")
```

### 可用动作

#### TASK_COMPLETE
- **类型**: `TASK_COMPLETE`
- **用户可见**: 是
- **唯一动作**: 是（必须单独使用）
- **返回动作**: 是（终止执行）
- **目的**: 标示成功任务完成及摘要
- **创建的事件类型**: `task_completion`

#### RUN_SHELL_CMD
- **类型**: `RUN_SHELL_CMD`
- **用户可见**: 否
- **唯一动作**: 否
- **返回动作**: 否
- **目的**: 在系统中执行 shell 命令
- **创建的事件类型**: `action`
- **特殊功能**: 支持后台执行和超时配置

#### HELP_NEEDED
- **类型**: `HELP_NEEDED`
- **用户可见**: 是
- **唯一动作**: 是（必须单独使用）
- **返回动作**: 是（终止执行）
- **目的**: 当代理遇到困难时请求人工干预
- **创建的事件类型**: `agent_requested_help`

#### AGENT_TEXT_RESPONSE
- **类型**: `AGENT_TEXT_RESPONSE`
- **用户可见**: 是
- **唯一动作**: 是（必须单独使用）
- **返回动作**: 是（终止执行）
- **目的**: 为用户问题提供信息性响应
- **创建的事件类型**: `agent_text_response`

#### EDIT_FILE
- **类型**: `EDIT_FILE`
- **用户可见**: 否
- **唯一动作**: 否
- **返回动作**: 否
- **目的**: 创建、修改或删除文件内容
- **创建的事件类型**: `edit_file`
- **操作**: NEW_FILE、INSERT_LINES、REMOVE_LINES、REPLACE_LINES

#### READ_MIME_FILES
- **类型**: `READ_MIME_FILES`
- **用户可见**: 否
- **唯一动作**: 否
- **返回动作**: 否
- **目的**: 使用多模态 AI 分析文件（图像、PDF）和 YouTube 链接的内容
- **创建的事件类型**: `READ_MIME_FILES`
- **支持格式**: 图像、PDF、YouTube 视频
- **功能**: 可选输出文件保存、多模态内容分析

### 动作执行流程

1. **动作预测**: 代理 LLM 基于事件历史预测下一个动作
2. **动作验证**: 响应被解析并根据可用动作进行验证
3. **动作执行**: 调用每个动作的 `handle_action_in_parsed_response` 方法
4. **事件创建**: 动作创建适当的事件并将其添加到事件流
5. **流持久化**: 动作执行后保存事件流
6. **终止检查**: 返回动作导致执行循环退出

### 动作注册

动作通过 `registered_actions` 属性向代理注册。每个代理维护一个可动态配置的可用动作列表。

### 事件系统文档

#### 完整事件类型

系统支持以下事件类型：

- **`new_request`**: 启动新任务的初始用户输入
- **`follow_up_request`**: 现有对话中的额外用户输入
- **`action`**: 代理执行的 shell 命令及其结果
- **`edit_file`**: 文件修改操作
- **`READ_MIME_FILES`**: 多模态文件分析操作
- **`task_completion`**: 成功任务完成及摘要
- **`agent_requested_help`**: 代理请求人工干预
- **`agent_text_response`**: 代理提供信息性响应
- **`task_interrupted`**: 由于错误、中断或耗尽导致的任务终止
- **`child_agent_running`**: 子代理执行跟踪
- **`new_request_from_parent`**: 从父代理接收的请求
- **`follow_up_request_from_parent`**: 来自父代理的后续请求

#### 事件类结构

```python
class Event:
    def __init__(self, type, reasoning="", content="", title=None, message="", analysis="", est_input_token=0, est_output_token=0):
        self.type = type  # 必需：事件类型标识符
        self.reasoning = reasoning  # 必需：代理执行此动作的推理
        self.content = content  # 动作特定内容
        self.title = title  # 可选事件标题
        self.message = message  # 必需：用户可见消息
        self.analysis = analysis  # 内部分析（不显示给用户）
        self.est_input_token = est_input_token  # 令牌使用跟踪
        self.est_output_token = est_output_token  # 令牌使用跟踪
        self.created_at = datetime.now()  # 时间戳
```

#### EventStream 类结构

```python
class EventStream:
    def __init__(self, title=None, uid=None, parent_event_stream_uids=None, agent_type=""):
        self.events_list = []  # 事件的时间顺序列表
        self.event_summaries_list = []  # 摘要事件组
        self.created_at = datetime.now()
        self.uid = uid or generate_random_id()  # 唯一标识符
        self.title = title or self.uid  # 人类可读标题
        self.parent_event_stream_uids = parent_event_stream_uids or []  # 父关系
        self.agent_type = agent_type  # 创建此流的代理类型
        self.agent_settings = {}  # 代理配置设置
```

#### 关键 EventStream 方法

- **`add_event(event)`**: 向流中添加新事件
- **`get_event_list_including_children_events(starting_from=0)`**: 检索包括子代理事件的扁平化事件列表
- **`update_settings(settings)`**: 更新代理配置设置
- **`get_settings()`**: 返回当前代理设置
- **`to_dict()`** / **`from_dict()`**: 用于持久化的序列化方法

#### 返回父级事件类型

某些事件类型导致子代理将控制权返回给其父级：

```python
RETURN_TO_PARENT_EVENT_TYPES = [
    "task_interrupted", 
    "task_completion", 
    "agent_requested_help", 
    "agent_text_response"
]
```

这些事件表示子代理已完成其执行，控制权应返回给父代理。

#### 返回动作
标记为 `returning_action=True` 的动作终止代理循环：
- 所有唯一动作都是返回动作
- 这些动作代表完成状态或用户交互点

## 提示构建

提示构建系统动态构建上下文感知的提示，指导代理行为并为决策提供必要信息。

### 提示模板架构

#### 基础模板结构

核心提示模板定义在 `anges/prompt_templates/common_prompts.py` 中：

```python
DEFAULT_AGENT_PROMPT_TEMPLATE = r"""
# 指令
您是最优秀的 AI 代理。您在 Linux 环境中运行，具有一些动作选项。

您将获得一个事件列表，其中包含您与用户之间的先前交互。

您的总体目标是执行多步骤动作，帮助用户实现其请求或回答其问题。

## 响应格式规则
您需要以 *JSON* 格式响应，包含以下键：
- `analysis`: 内部思维链思考
- `action`: 作为下一步要采取的动作列表
- `reasoning`: 用户可见的动作解释

## 可用动作标签
PLACEHOLDER_ACTION_INSTRUCTIONS

######### 以下是实际请求 #########
# 事件流
PLACEHOLDER_EVENT_STREAM

# 下一步
<现在以 JSON 格式输出下一步动作。不要包含 ``` 引号。您的整个响应需要是 JSON 可解析的。>
"""
```

#### 模板占位符

系统使用两个动态替换的关键占位符：

1. **`PLACEHOLDER_ACTION_INSTRUCTIONS`**: 替换为所有可用动作的连接 `guide_prompt` 内容
2. **`PLACEHOLDER_EVENT_STREAM`**: 替换为提供上下文的格式化事件流

### 动态内容注入

#### 动作指令生成

动作指令通过连接每个注册动作的 `guide_prompt` 字段动态生成：

```python
def generate_action_instructions(action_registry):
    instructions = []
    for action_name, action_obj in action_registry.items():
        instructions.append(action_obj.guide_prompt)
    return "\n\n".join(instructions)
```

这为代理提供：
- 完整的动作文档
- 使用示例
- 参数规范
- 约束信息

#### 事件流格式化

事件流使用 `construct_event_stream_for_agent()` 进行格式化，该函数：

1. **处理事件历史**: 将事件转换为人类可读格式
2. **应用摘要**: 压缩长事件序列
3. **维护上下文**: 保留决策所需的关键信息
4. **格式化输出**: 创建结构化文本表示

格式化事件流示例：
```
## Event 1 TYPE: NEW_REQUEST
CONTENT:
用户想要分析日志文件并创建摘要报告。

## Event 2 TYPE: ACTION
REASONING:
我需要首先检查日志文件以了解其结构。
CONTENT:
******
- COMMAND_EXECUTED: ls -la /var/log/
- EXIT_CODE: 0
- STDOUT: [日志文件列表]
******
```

### 提示组装过程

#### 1. 模板加载
从提示模板模块加载基础模板。

#### 2. 动作指令注入
连接所有可用动作的指导提示并注入到 `PLACEHOLDER_ACTION_INSTRUCTIONS` 位置。

#### 3. 事件流构建
处理并格式化当前事件流，然后注入到 `PLACEHOLDER_EVENT_STREAM` 位置。

#### 4. 最终提示生成
组装完整提示，包含：
- 系统指令
- 响应格式要求
- 可用动作文档
- 当前上下文（事件流）
- 执行指令

### 上下文管理

#### 令牌优化
系统通过以下方式管理提示长度：
- **事件摘要**: 较旧的事件被摘要以减少令牌数量
- **内容截断**: 长命令输出用 "..." 指示符截断
- **选择性包含**: 只有相关事件包含在上下文中

#### 上下文连续性
尽管有摘要，系统仍维护：
- **任务连续性**: 当前任务目标保持清晰
- **状态感知**: 代理了解当前系统状态
- **错误上下文**: 最近的错误及其解决尝试
- **进度跟踪**: 了解已完成与剩余工作

### 专用提示模板

系统包含针对不同场景的专用模板：

#### 编排器提示
(`anges/prompt_templates/orchestrator_prompts.py`)
- 多代理协调
- 任务委托
- 资源管理

#### 任务分析器提示
(`anges/prompt_templates/task_analyzer_prompts.py`)
- 任务分解
- 复杂性评估
- 方法规划

## 系统集成

三个核心系统协同工作创建一个内聚的代理框架：

### 集成流程

1. **提示构建** 使用当前事件流创建上下文感知提示
2. **代理处理** 基于提示生成包含动作的响应
3. **动作系统** 执行指定动作并创建新事件
4. **事件循环** 管理循环并确定继续或终止

### 配置管理

`run_config` 字典提供系统范围的配置：

```python
run_config = {
    "event_stream": current_event_stream,
    "inference_func": ai_model_function,
    "message_handler_func": user_notification_function,
    "cmd_init_dir": working_directory,
    "prefix_cmd": command_prefix,
    "agent_config": configuration_object,
    "max_consecutive_actions_to_summarize": 30,
    "logger": logging_instance
}
```

## 设计模式

### 策略模式
动作系统使用策略模式，允许不同的动作实现同时保持一致的接口。

### 观察者模式
事件生成遵循观察者模式，多个组件对事件创建做出反应。

### 模板方法模式
提示构建使用模板方法模式，具有固定结构和可变内容注入。

### 工厂模式
动作注册和发现遵循工厂模式以实现可扩展的动作管理。

## 扩展点

### 添加新动作

1. **创建动作类**: 继承 `Action` 基类
2. **实现处理器**: 定义 `handle_action_in_parsed_response()` 方法
3. **设置属性**: 配置 `user_visible`、`unique_action`、`returning_action`
4. **编写指导提示**: 提供全面文档
5. **注册动作**: 添加到动作注册表

### 自定义事件类型

1. **定义事件类型**: 向事件类型常量添加新类型
2. **更新处理**: 如需要，修改事件流构建
3. **处理终止**: 如果是终端类型，添加到 `RETURN_TO_PARENT_EVENT_TYPES`

### 提示模板自定义

1. **创建模板**: 定义带占位符的新模板
2. **实现注入**: 创建内容注入逻辑
3. **注册模板**: 使其可用于代理配置

此架构为 AI 代理开发提供了强大、可扩展的基础，具有清晰的关注点分离和明确定义的集成点。