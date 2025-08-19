**语言**: [English](../utility-functions.md) | [中文](utility-functions.md)

---
# 实用工具函数文档

本文档涵盖为 Anges 代理系统提供核心功能的实用工具函数和模块。这些实用工具处理事件管理、文件处理和其他基本操作。

## 事件方法模块 (`event_methods.py`)

事件方法模块在代理系统内提供了管理事件、事件流和事件摘要的综合实用工具。

### 概述

事件方法模块提供以下功能：
- **事件创建和操作**：创建、修改和验证事件对象
- **事件流管理**：处理事件序列和流操作
- **事件摘要**：生成事件历史的简洁摘要
- **事件过滤和搜索**：基于各种条件查找特定事件
- **事件序列化**：将事件转换为各种格式（JSON、YAML 等）

### 核心事件类

#### Event 类

基础事件类定义了系统中所有事件的结构：

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

@dataclass
class Event:
    """表示系统中单个事件的基础事件类"""
    event_type: str
    timestamp: datetime
    content: Any
    metadata: Optional[Dict[str, Any]] = None
    event_id: Optional[str] = None
    
    def __post_init__(self):
        if self.event_id is None:
            self.event_id = self.generate_event_id()
    
    def generate_event_id(self) -> str:
        """为事件生成唯一标识符"""
        import uuid
        return str(uuid.uuid4())
```

#### 事件类型

系统支持多种事件类型：

```python
class EventType:
    """事件类型常量"""
    USER_INPUT = "user_input"
    AGENT_ACTION = "agent_action"
    SYSTEM_MESSAGE = "system_message"
    ERROR = "error"
    TASK_START = "task_start"
    TASK_COMPLETE = "task_complete"
    FILE_OPERATION = "file_operation"
    COMMAND_EXECUTION = "command_execution"
```

### 事件创建函数

#### create_event()

创建新事件的主要函数：

```python
def create_event(
    event_type: str,
    content: Any,
    metadata: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Event:
    """
    创建新事件
    
    参数:
        event_type: 事件类型标识符
        content: 事件内容（可以是任何类型）
        metadata: 可选的元数据字典
        timestamp: 可选的时间戳（默认为当前时间）
    
    返回:
        Event: 新创建的事件对象
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    return Event(
        event_type=event_type,
        content=content,
        metadata=metadata or {},
        timestamp=timestamp
    )
```

#### 便捷事件创建函数

```python
def create_user_input_event(message: str, user_id: str = None) -> Event:
    """创建用户输入事件"""
    metadata = {"user_id": user_id} if user_id else {}
    return create_event(EventType.USER_INPUT, message, metadata)

def create_agent_action_event(
    action_type: str,
    action_data: Dict[str, Any],
    result: Any = None
) -> Event:
    """创建代理操作事件"""
    content = {
        "action_type": action_type,
        "action_data": action_data,
        "result": result
    }
    return create_event(EventType.AGENT_ACTION, content)

def create_error_event(error_message: str, error_type: str = None) -> Event:
    """创建错误事件"""
    content = {
        "message": error_message,
        "error_type": error_type or "general_error"
    }
    return create_event(EventType.ERROR, content)
```

### 事件流管理

#### EventStream 类

管理事件序列的类：

```python
class EventStream:
    """管理事件序列的类"""
    
    def __init__(self, events: List[Event] = None):
        self.events = events or []
        self._observers = []
    
    def add_event(self, event: Event) -> None:
        """向流中添加事件"""
        self.events.append(event)
        self._notify_observers(event)
    
    def get_events(
        self,
        event_type: str = None,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> List[Event]:
        """根据条件获取事件"""
        filtered_events = self.events
        
        if event_type:
            filtered_events = [
                e for e in filtered_events 
                if e.event_type == event_type
            ]
        
        if start_time:
            filtered_events = [
                e for e in filtered_events 
                if e.timestamp >= start_time
            ]
        
        if end_time:
            filtered_events = [
                e for e in filtered_events 
                if e.timestamp <= end_time
            ]
        
        return filtered_events
    
    def get_latest_events(self, count: int = 10) -> List[Event]:
        """获取最新的 N 个事件"""
        return sorted(self.events, key=lambda e: e.timestamp)[-count:]
```

### 事件摘要功能

#### summarize_events()

生成事件历史摘要：

```python
def summarize_events(
    events: List[Event],
    max_length: int = 500,
    include_details: bool = True
) -> str:
    """
    生成事件列表的摘要
    
    参数:
        events: 要摘要的事件列表
        max_length: 摘要的最大字符长度
        include_details: 是否包含详细信息
    
    返回:
        str: 事件的文本摘要
    """
    if not events:
        return "无事件记录。"
    
    summary_parts = []
    
    # 按类型分组事件
    events_by_type = {}
    for event in events:
        event_type = event.event_type
        if event_type not in events_by_type:
            events_by_type[event_type] = []
        events_by_type[event_type].append(event)
    
    # 生成摘要
    for event_type, type_events in events_by_type.items():
        count = len(type_events)
        summary_parts.append(f"{count} 个 {event_type} 事件")
        
        if include_details and count <= 3:
            for event in type_events:
                detail = _extract_event_detail(event)
                if detail:
                    summary_parts.append(f"  - {detail}")
    
    summary = "\n".join(summary_parts)
    
    # 如果摘要太长，则截断
    if len(summary) > max_length:
        summary = summary[:max_length - 3] + "..."
    
    return summary

def _extract_event_detail(event: Event) -> str:
    """从事件中提取关键详细信息"""
    if event.event_type == EventType.USER_INPUT:
        return f"用户说: {str(event.content)[:50]}..."
    elif event.event_type == EventType.AGENT_ACTION:
        action_type = event.content.get("action_type", "未知")
        return f"代理执行: {action_type}"
    elif event.event_type == EventType.ERROR:
        return f"错误: {event.content.get('message', '未知错误')}"
    else:
        return str(event.content)[:50] + "..." if len(str(event.content)) > 50 else str(event.content)
```

### 事件搜索和过滤

#### search_events()

在事件中搜索特定内容：

```python
def search_events(
    events: List[Event],
    query: str,
    search_content: bool = True,
    search_metadata: bool = False,
    case_sensitive: bool = False
) -> List[Event]:
    """
    在事件中搜索特定查询
    
    参数:
        events: 要搜索的事件列表
        query: 搜索查询字符串
        search_content: 是否搜索事件内容
        search_metadata: 是否搜索事件元数据
        case_sensitive: 是否区分大小写
    
    返回:
        List[Event]: 匹配查询的事件列表
    """
    if not case_sensitive:
        query = query.lower()
    
    matching_events = []
    
    for event in events:
        match_found = False
        
        # 搜索内容
        if search_content:
            content_str = str(event.content)
            if not case_sensitive:
                content_str = content_str.lower()
            
            if query in content_str:
                match_found = True
        
        # 搜索元数据
        if search_metadata and event.metadata:
            metadata_str = str(event.metadata)
            if not case_sensitive:
                metadata_str = metadata_str.lower()
            
            if query in metadata_str:
                match_found = True
        
        if match_found:
            matching_events.append(event)
    
    return matching_events
```

#### filter_events_by_timerange()

按时间范围过滤事件：

```python
def filter_events_by_timerange(
    events: List[Event],
    start_time: datetime = None,
    end_time: datetime = None
) -> List[Event]:
    """
    按时间范围过滤事件
    
    参数:
        events: 要过滤的事件列表
        start_time: 开始时间（包含）
        end_time: 结束时间（包含）
    
    返回:
        List[Event]: 过滤后的事件列表
    """
    filtered_events = events
    
    if start_time:
        filtered_events = [
            event for event in filtered_events
            if event.timestamp >= start_time
        ]
    
    if end_time:
        filtered_events = [
            event for event in filtered_events
            if event.timestamp <= end_time
        ]
    
    return filtered_events
```

### 事件序列化

#### 导出功能

将事件导出为各种格式：

```python
import json
import yaml
from typing import Union

def export_events_to_json(
    events: List[Event],
    filepath: str = None,
    pretty: bool = True
) -> Union[str, None]:
    """
    将事件导出为 JSON 格式
    
    参数:
        events: 要导出的事件列表
        filepath: 可选的文件路径进行保存
        pretty: 是否使用美化格式
    
    返回:
        str: JSON 字符串（如果未提供 filepath）
    """
    events_data = []
    
    for event in events:
        event_dict = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "content": event.content,
            "metadata": event.metadata
        }
        events_data.append(event_dict)
    
    json_str = json.dumps(
        events_data,
        indent=2 if pretty else None,
        ensure_ascii=False
    )
    
    if filepath:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_str)
        return None
    
    return json_str

def export_events_to_yaml(
    events: List[Event],
    filepath: str = None
) -> Union[str, None]:
    """
    将事件导出为 YAML 格式
    
    参数:
        events: 要导出的事件列表
        filepath: 可选的文件路径进行保存
    
    返回:
        str: YAML 字符串（如果未提供 filepath）
    """
    events_data = []
    
    for event in events:
        event_dict = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "content": event.content,
            "metadata": event.metadata
        }
        events_data.append(event_dict)
    
    yaml_str = yaml.dump(
        events_data,
        default_flow_style=False,
        allow_unicode=True
    )
    
    if filepath:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(yaml_str)
        return None
    
    return yaml_str
```

#### 导入功能

从文件导入事件：

```python
def import_events_from_json(filepath: str) -> List[Event]:
    """
    从 JSON 文件导入事件
    
    参数:
        filepath: JSON 文件路径
    
    返回:
        List[Event]: 导入的事件列表
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        events_data = json.load(f)
    
    events = []
    for event_dict in events_data:
        event = Event(
            event_type=event_dict["event_type"],
            timestamp=datetime.fromisoformat(event_dict["timestamp"]),
            content=event_dict["content"],
            metadata=event_dict.get("metadata"),
            event_id=event_dict.get("event_id")
        )
        events.append(event)
    
    return events
```

### 事件验证

#### validate_event()

验证事件对象的完整性：

```python
def validate_event(event: Event) -> bool:
    """
    验证事件对象是否有效
    
    参数:
        event: 要验证的事件对象
    
    返回:
        bool: 如果事件有效则为 True
    
    引发:
        ValueError: 如果事件无效
    """
    if not isinstance(event, Event):
        raise ValueError("对象必须是 Event 类的实例")
    
    if not event.event_type:
        raise ValueError("event_type 不能为空")
    
    if not isinstance(event.timestamp, datetime):
        raise ValueError("timestamp 必须是 datetime 对象")
    
    if event.content is None:
        raise ValueError("content 不能为 None")
    
    return True

def validate_event_stream(events: List[Event]) -> bool:
    """
    验证事件流中的所有事件
    
    参数:
        events: 要验证的事件列表
    
    返回:
        bool: 如果所有事件都有效则为 True
    """
    for i, event in enumerate(events):
        try:
            validate_event(event)
        except ValueError as e:
            raise ValueError(f"事件 {i} 无效: {e}")
    
    return True
```

## 文件处理实用工具

### 文件操作函数

#### safe_file_read()

安全地读取文件内容：

```python
def safe_file_read(
    filepath: str,
    encoding: str = 'utf-8',
    max_size: int = 10 * 1024 * 1024  # 10MB
) -> str:
    """
    安全地读取文件内容
    
    参数:
        filepath: 要读取的文件路径
        encoding: 文件编码
        max_size: 最大文件大小（字节）
    
    返回:
        str: 文件内容
    
    引发:
        FileNotFoundError: 如果文件不存在
        ValueError: 如果文件太大
    """
    import os
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件未找到: {filepath}")
    
    file_size = os.path.getsize(filepath)
    if file_size > max_size:
        raise ValueError(f"文件太大: {file_size} 字节（最大 {max_size} 字节）")
    
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError as e:
        raise ValueError(f"无法使用编码 {encoding} 解码文件: {e}")
```

#### safe_file_write()

安全地写入文件内容：

```python
def safe_file_write(
    filepath: str,
    content: str,
    encoding: str = 'utf-8',
    backup: bool = True
) -> bool:
    """
    安全地写入文件内容
    
    参数:
        filepath: 要写入的文件路径
        content: 要写入的内容
        encoding: 文件编码
        backup: 是否创建备份（如果文件存在）
    
    返回:
        bool: 如果写入成功则为 True
    """
    import os
    import shutil
    
    # 如果需要，创建备份
    if backup and os.path.exists(filepath):
        backup_path = f"{filepath}.backup"
        shutil.copy2(filepath, backup_path)
    
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
        
        return True
    except Exception as e:
        # 如果写入失败且存在备份，恢复备份
        if backup and os.path.exists(f"{filepath}.backup"):
            shutil.move(f"{filepath}.backup", filepath)
        raise e
```

## 字符串处理实用工具

### 文本格式化函数

#### truncate_text()

截断长文本：

```python
def truncate_text(
    text: str,
    max_length: int = 100,
    suffix: str = "..."
) -> str:
    """
    截断文本到指定长度
    
    参数:
        text: 要截断的文本
        max_length: 最大长度
        suffix: 截断后缀
    
    返回:
        str: 截断后的文本
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
```

#### format_duration()

格式化持续时间：

```python
def format_duration(seconds: float) -> str:
    """
    将秒数格式化为人类可读的持续时间
    
    参数:
        seconds: 持续时间（秒）
    
    返回:
        str: 格式化的持续时间字符串
    """
    if seconds < 60:
        return f"{seconds:.1f} 秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} 分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} 小时"
```

## 系统实用工具

### 环境检查函数

#### check_system_requirements()

检查系统要求：

```python
def check_system_requirements() -> Dict[str, bool]:
    """
    检查系统要求
    
    返回:
        Dict[str, bool]: 要求检查结果
    """
    import sys
    import shutil
    
    requirements = {
        "python_version": sys.version_info >= (3, 8),
        "git_available": shutil.which("git") is not None,
        "curl_available": shutil.which("curl") is not None,
    }
    
    return requirements
```

### 路径实用工具

#### get_project_root()

获取项目根目录：

```python
def get_project_root() -> str:
    """
    获取项目根目录路径
    
    返回:
        str: 项目根目录路径
    """
    import os
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 向上查找，直到找到包含 setup.py 或 pyproject.toml 的目录
    while current_dir != os.path.dirname(current_dir):
        if (os.path.exists(os.path.join(current_dir, "setup.py")) or
            os.path.exists(os.path.join(current_dir, "pyproject.toml"))):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    
    # 如果找不到，返回当前目录
    return os.getcwd()
```

## 使用示例

### 基本事件处理

```python
from anges.utils.event_methods import (
    create_event, create_user_input_event,
    EventStream, summarize_events
)

# 创建事件流
stream = EventStream()

# 添加事件
user_event = create_user_input_event("请帮我分析这个数据文件")
stream.add_event(user_event)

# 创建代理操作事件
action_event = create_agent_action_event(
    "file_analysis",
    {"file_path": "/data/analysis.csv"},
    {"rows": 1000, "columns": 5}
)
stream.add_event(action_event)

# 生成摘要
summary = summarize_events(stream.events)
print(f"事件摘要: {summary}")
```

### 事件搜索和过滤

```python
from anges.utils.event_methods import search_events, filter_events_by_timerange
from datetime import datetime, timedelta

# 搜索包含特定文本的事件
matching_events = search_events(
    stream.events,
    "数据文件",
    search_content=True
)

# 过滤最近一小时的事件
recent_events = filter_events_by_timerange(
    stream.events,
    start_time=datetime.now() - timedelta(hours=1)
)
```

### 事件导出和导入

```python
from anges.utils.event_methods import (
    export_events_to_json,
    import_events_from_json
)

# 导出事件到 JSON 文件
export_events_to_json(stream.events, "events_backup.json")

# 从文件导入事件
imported_events = import_events_from_json("events_backup.json")
```

## 最佳实践

### 1. 事件管理

- 为不同类型的事件使用一致的命名约定
- 在事件元数据中包含相关的上下文信息
- 定期清理旧事件以防止内存泄漏
- 使用事件 ID 进行事件跟踪和关联

### 2. 性能优化

- 对大型事件流使用分页
- 实现事件索引以加快搜索速度
- 考虑将事件持久化到数据库以供长期存储
- 使用异步处理进行事件处理

### 3. 错误处理

- 始终验证事件数据
- 实现适当的错误恢复机制
- 记录事件处理错误以进行调试
- 使用事务性操作进行关键事件更新

### 4. 安全性

- 清理事件内容中的敏感信息
- 实现事件访问控制
- 加密持久化的事件数据
- 审计事件访问和修改

这些实用工具函数为 Anges 代理系统提供了强大的基础功能，使开发人员能够有效地管理事件、处理文件和执行常见的系统操作。