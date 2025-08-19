**语言**: [English](../api-reference.md) | [中文](api-reference.md)

---

# Anges API 参考

## 概述

本文档为 Anges 项目核心类及其使用模式提供全面的 API 参考文档。Anges 是一个通过事件驱动架构实现自主任务执行的 AI 代理框架。

## 目录

- [核心类](#核心类)
  - [BaseAgent](#baseagent)
  - [EventStream](#eventstream)
  - [Event](#event)
  - [Action](#action)
- [配置系统](#配置系统)
  - [AgentConfig](#agentconfig)
  - [全局配置](#全局配置)
- [实用工具](#实用工具)
  - [Shell 包装器](#shell-包装器)
  - [文件操作](#文件操作)
  - [ID 生成](#id-生成)
- [使用示例](#使用示例)
- [最佳实践](#最佳实践)

## 核心类

### BaseAgent

`BaseAgent` 类是所有 Anges 代理的基础类，提供核心功能和生命周期管理。

#### 类定义

```python
from anges.agents.agent_utils.base_agent import BaseAgent

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

#### 参数

- **parent_ids** (`List[str]`, 可选): 父事件流 UID 列表，用于分层代理关系
- **inference_func** (`Callable`, 可选): 用于 LLM 推理调用的函数
- **event_stream** (`EventStream`, 可选): 现有事件流实例
- **cmd_init_dir** (`str`): 命令执行的初始目录
- **prefix_cmd** (`str`): shell 操作的命令前缀
- **interrupt_check** (`Callable`, 可选): 检查用户中断请求的函数
- **max_consecutive_actions_to_summarize** (`int`): 事件摘要的阈值
- **logging_level** (`int`): 日志记录级别
- **auto_entitle** (`bool`): 是否自动生成对话标题

#### 属性

- **uid** (`str`): 唯一标识符（继承自 event_stream.uid）
- **status** (`str`): 当前代理状态（"new"、"running"、"completed" 等）
- **event_stream** (`EventStream`): 管理执行历史的事件流实例
- **agent_config** (`AgentConfig`): 代理行为的配置对象
- **registered_actions** (`List[Action]`): 可用动作类型列表
- **message_handlers** (`List[Callable]`): 处理用户可见消息的函数列表
- **agent_prompt_template** (`str`): 构建代理提示的模板
- **logger** (`Logger`): 日志记录实例

#### 方法

##### `run_with_new_request(task_description: str, event_stream: EventStream = None) -> EventStream`

主执行方法，使用新任务描述启动代理执行。

**参数:**
- `task_description`: 要执行的任务的描述
- `event_stream`: 可选的现有事件流

**返回:**
- `EventStream`: 包含执行历史的更新事件流

**示例:**
```python
agent = BaseAgent()
result_stream = agent.run_with_new_request(
    "分析项目中的 Python 文件并生成代码质量报告"
)
```

##### `handle_user_visible_messages(message: str)`

通过调用所有注册的消息处理器来处理用户可见消息。

**参数:**
- `message`: 要处理的用户可见消息

**示例:**
```python
agent.handle_user_visible_messages("任务已完成")
```

##### `add_message_handler(handler: Callable[[str], None])`

添加消息处理器函数以处理用户可见消息。

**参数:**
- `handler`: 接受字符串消息的可调用函数

**示例:**
```python
def my_handler(message):
    print(f"代理消息: {message}")

agent.add_message_handler(my_handler)
```

##### `update_agent_config(config_updates: dict)`

使用提供的更新字典更新代理配置。

**参数:**
- `config_updates`: 包含配置更新的字典

**示例:**
```python
agent.update_agent_config({
    "max_iterations": 50,
    "timeout": 300
})
```

### EventStream

`EventStream` 类管理代理执行期间的事件历史和状态。

#### 类定义

```python
from anges.agents.agent_utils.events import EventStream

class EventStream:
    def __init__(
        self,
        title=None,
        uid=None,
        parent_event_stream_uids=None,
        agent_type=""
    )
```

#### 参数

- **title** (`str`, 可选): 事件流的人类可读标题
- **uid** (`str`, 可选): 唯一标识符（如果未提供则自动生成）
- **parent_event_stream_uids** (`List[str]`, 可选): 父事件流 UID 列表
- **agent_type** (`str`): 创建此流的代理类型

#### 属性

- **events_list** (`List[Event]`): 事件的时间顺序列表
- **event_summaries_list** (`List[dict]`): 摘要事件组
- **created_at** (`datetime`): 创建时间戳
- **uid** (`str`): 唯一标识符
- **title** (`str`): 人类可读标题
- **parent_event_stream_uids** (`List[str]`): 父关系
- **agent_type** (`str`): 代理类型标识符
- **agent_settings** (`dict`): 代理配置设置

#### 方法

##### `add_event(event: Event)`

向事件流添加新事件。

**参数:**
- `event`: 要添加的 Event 实例

**示例:**
```python
event = Event("action", reasoning="执行文件列表", content="ls -la")
event_stream.add_event(event)
```

##### `get_event_list_including_children_events(starting_from: int = 0) -> List[Event]`

检索包括子代理事件的扁平化事件列表。

**参数:**
- `starting_from`: 开始检索的事件索引

**返回:**
- `List[Event]`: 扁平化的事件列表

##### `update_settings(settings: dict)`

更新代理配置设置。

**参数:**
- `settings`: 包含设置更新的字典

##### `get_settings() -> dict`

返回当前代理设置。

**返回:**
- `dict`: 当前代理设置

##### `to_dict() -> dict`

将事件流序列化为字典以进行持久化。

**返回:**
- `dict`: 序列化的事件流数据

##### `from_dict(data: dict) -> EventStream`

从字典数据创建 EventStream 实例。

**参数:**
- `data`: 序列化的事件流数据

**返回:**
- `EventStream`: 反序列化的事件流实例

##### `save(file_path: str = None)`

将事件流保存到文件。

**参数:**
- `file_path`: 可选的文件路径（如果未提供则使用默认位置）

##### `load(file_path: str) -> EventStream`

从文件加载事件流。

**参数:**
- `file_path`: 要加载的文件路径

**返回:**
- `EventStream`: 加载的事件流实例

### Event

`Event` 类表示代理执行期间的单个事件或动作。

#### 类定义

```python
from anges.agents.agent_utils.events import Event

class Event:
    def __init__(
        self,
        type,
        reasoning="",
        content="",
        title=None,
        message="",
        analysis="",
        est_input_token=0,
        est_output_token=0
    )
```

#### 参数

- **type** (`str`): 事件类型标识符
- **reasoning** (`str`): 代理执行此动作的推理
- **content** (`str`): 动作特定内容
- **title** (`str`, 可选): 可选事件标题
- **message** (`str`): 用户可见消息
- **analysis** (`str`): 内部分析（不显示给用户）
- **est_input_token** (`int`): 估计的输入令牌数
- **est_output_token** (`int`): 估计的输出令牌数

#### 属性

- **id** (`str`): 唯一事件标识符
- **timestamp** (`str`): ISO 格式的时间戳
- **created_at** (`datetime`): 创建时间

#### 事件类型

支持的事件类型包括：

- **`new_request`**: 启动新任务的初始用户输入
- **`follow_up_request`**: 现有对话中的额外用户输入
- **`action`**: 代理执行的 shell 命令及其结果
- **`edit_file`**: 文件修改操作
- **`READ_MIME_FILES`**: 多模态文件分析操作
- **`task_completion`**: 成功任务完成及摘要
- **`agent_requested_help`**: 代理请求人工干预
- **`agent_text_response`**: 代理提供信息性响应
- **`task_interrupted`**: 由于错误、中断或耗尽导致的任务终止

### Action

`Action` 类是所有代理动作的基类。

#### 类定义

```python
from anges.agents.agent_utils.agent_actions import Action

class Action:
    def __init__(self):
        self.type = ""  # 唯一动作标识符
        self.guide_prompt = ""  # 代理文档
        self.user_visible = False  # 动作结果是否显示给用户
        self.unique_action = False  # 动作是否必须单独使用
        self.returning_action = False  # 动作是否终止执行
```

#### 属性

- **type** (`str`): 唯一动作标识符
- **guide_prompt** (`str`): 提供给代理的文档和使用指南
- **user_visible** (`bool`): 动作结果是否对用户可见
- **unique_action** (`bool`): 动作是否必须单独使用
- **returning_action** (`bool`): 动作是否终止执行循环

#### 方法

##### `handle_action_in_parsed_response(run_config: dict, parsed_response_dict: dict, action_json: dict)`

处理解析响应中的动作执行。子类必须实现此方法。

**参数:**
- `run_config`: 运行时配置字典
- `parsed_response_dict`: 解析的 LLM 响应
- `action_json`: 动作特定的 JSON 数据

## 配置系统

### AgentConfig

`AgentConfig` 类管理代理行为配置。

#### 类定义

```python
from anges.agents.agent_utils.agent_config import AgentConfig

class AgentConfig:
    def __init__(
        self,
        max_iterations=50,
        timeout=300,
        enable_auto_save=True,
        save_interval=10
    )
```

#### 参数

- **max_iterations** (`int`): 最大执行迭代次数
- **timeout** (`int`): 执行超时时间（秒）
- **enable_auto_save** (`bool`): 是否启用自动保存
- **save_interval** (`int`): 自动保存间隔（事件数）

### 全局配置

全局配置通过 `anges.config` 模块管理。

```python
from anges import config

# 访问配置值
default_dir = config.agents.default_agent.cmd_init_dir
max_actions = config.agents.default_agent.max_consecutive_actions_to_summarize

# 更新配置
config.update({
    "agents": {
        "default_agent": {
            "cmd_init_dir": "/custom/path",
            "max_consecutive_actions_to_summarize": 25
        }
    }
})
```

## 实用工具

### Shell 包装器

#### `run_shell_command(command: str, cwd: str = None, timeout: int = None) -> dict`

执行 shell 命令并返回结果。

**参数:**
- `command`: 要执行的 shell 命令
- `cwd`: 工作目录
- `timeout`: 超时时间（秒）

**返回:**
- `dict`: 包含 `stdout`、`stderr`、`exit_code` 和 `execution_time` 的字典

**示例:**
```python
from anges.agents.agent_utils.shell_wrapper import run_shell_command

result = run_shell_command("ls -la", cwd="/home/user")
print(f"退出码: {result['exit_code']}")
print(f"输出: {result['stdout']}")
```

### 文件操作

#### `safe_read_file(file_path: str, encoding: str = 'utf-8') -> str`

安全地读取文件内容。

**参数:**
- `file_path`: 要读取的文件路径
- `encoding`: 文件编码

**返回:**
- `str`: 文件内容

#### `safe_write_file(file_path: str, content: str, encoding: str = 'utf-8')`

安全地写入文件内容。

**参数:**
- `file_path`: 要写入的文件路径
- `content`: 要写入的内容
- `encoding`: 文件编码

### ID 生成

#### `generate_random_id(length: int = 8) -> str`

生成随机标识符。

**参数:**
- `length`: 标识符长度

**返回:**
- `str`: 随机标识符

## 使用示例

### 基本代理使用

```python
from anges.agents.agent_utils.base_agent import BaseAgent
from anges.inference.anthropic_inference import anthropic_inference

# 创建代理
agent = BaseAgent(
    inference_func=anthropic_inference,
    cmd_init_dir="/workspace",
    auto_entitle=True
)

# 执行任务
result = agent.run_with_new_request(
    "分析当前目录中的 Python 文件并生成代码质量报告"
)

# 访问结果
print(f"任务状态: {agent.status}")
print(f"事件数量: {len(result.events_list)}")
```

### 自定义动作创建

```python
from anges.agents.agent_utils.agent_actions import Action
from anges.agents.agent_utils.events import Event

class CustomAnalysisAction(Action):
    def __init__(self):
        super().__init__()
        self.type = "CUSTOM_ANALYSIS"
        self.guide_prompt = "执行自定义分析操作"
        self.user_visible = True
        self.unique_action = False
        self.returning_action = False
    
    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        # 实现自定义逻辑
        analysis_result = "分析完成"
        
        # 创建事件
        event = Event(
            type="custom_analysis",
            reasoning="执行自定义分析",
            content=analysis_result,
            message="自定义分析已完成"
        )
        
        # 添加到事件流
        run_config["event_stream"].add_event(event)
```

### 事件流操作

```python
from anges.agents.agent_utils.events import EventStream, Event

# 创建事件流
stream = EventStream(title="数据分析任务")

# 添加事件
event1 = Event("new_request", content="开始数据分析")
event2 = Event("action", reasoning="列出文件", content="ls -la")

stream.add_event(event1)
stream.add_event(event2)

# 保存事件流
stream.save("analysis_session.json")

# 稍后加载
loaded_stream = EventStream.load("analysis_session.json")
```

## 最佳实践

### 错误处理

```python
try:
    result = agent.run_with_new_request(task_description)
except Exception as e:
    print(f"代理执行失败: {e}")
    # 处理错误或重试
```

### 资源管理

```python
# 设置适当的超时
agent.update_agent_config({
    "timeout": 600,  # 10 分钟
    "max_iterations": 100
})

# 启用自动保存
agent.update_agent_config({
    "enable_auto_save": True,
    "save_interval": 5
})
```

### 日志记录

```python
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO)

# 创建带有自定义日志级别的代理
agent = BaseAgent(
    logging_level=logging.DEBUG,
    inference_func=anthropic_inference
)
```

### 消息处理

```python
def custom_message_handler(message):
    # 自定义消息处理逻辑
    print(f"[代理] {message}")
    # 可以发送到 UI、日志文件等

agent.add_message_handler(custom_message_handler)
```

### 性能优化

```python
# 调整摘要阈值以管理内存使用
agent = BaseAgent(
    max_consecutive_actions_to_summarize=20,  # 较低的值 = 更频繁的摘要
    inference_func=anthropic_inference
)

# 使用适当的工作目录
agent = BaseAgent(
    cmd_init_dir="/tmp/agent_workspace",  # 使用临时目录
    inference_func=anthropic_inference
)
```

这个 API 参考提供了使用 Anges 框架开发 AI 代理应用程序的全面指南。有关更高级的使用模式和扩展，请参阅实现指南和架构文档。
