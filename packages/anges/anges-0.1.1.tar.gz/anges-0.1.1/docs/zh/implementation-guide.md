**语言**: [English](../implementation-guide.md) | [中文](implementation-guide.md)

---

# Anges 实现指南

## 概述

本指南提供了使用自定义功能扩展 Anges 框架的分步说明。您将学习如何创建自定义代理和动作以满足您的特定需求。

## 目录

- [创建自定义代理](#创建自定义代理)
- [创建自定义动作](#创建自定义动作)
- [配置管理](#配置管理)
- [事件处理](#事件处理)
- [集成外部服务](#集成外部服务)
- [调试和故障排除](#调试和故障排除)
- [部署考虑](#部署考虑)
- [高级模式](#高级模式)

## 创建自定义代理

### 基本代理结构

要创建自定义代理，请从 `BaseAgent` 类继承并根据需要覆盖方法：

```python
from anges.agents.agent_utils.base_agent import BaseAgent
from anges.agents.agent_utils.events import Event
import logging

class CustomAgent(BaseAgent):
    def __init__(self, **kwargs):
        # 调用父类构造函数
        super().__init__(**kwargs)
        
        # 设置自定义属性
        self.agent_type = "custom_agent"
        self.custom_config = {
            "specialized_mode": True,
            "domain_knowledge": "data_analysis"
        }
        
        # 自定义日志记录
        self.logger = logging.getLogger(f"CustomAgent-{self.uid}")
```

### 专用代理示例

以下是一个专门用于数据分析任务的代理示例：

```python
class DataAnalysisAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 专用配置
        self.agent_type = "data_analysis_agent"
        self.supported_formats = ['.csv', '.json', '.xlsx', '.parquet']
        self.analysis_tools = ['pandas', 'numpy', 'matplotlib']
        
        # 自定义提示模板
        self.agent_prompt_template = self._load_specialized_prompt()
        
        # 注册专用动作
        self._register_analysis_actions()
    
    def _load_specialized_prompt(self):
        return """
        您是一个专门的数据分析 AI 代理。您擅长：
        - 数据清理和预处理
        - 统计分析和可视化
        - 机器学习模型开发
        - 报告生成
        
        使用您的专业知识提供准确、可操作的数据洞察。
        """
    
    def _register_analysis_actions(self):
        # 添加专用分析动作
        from .custom_actions import DataVisualizationAction, StatisticalAnalysisAction
        
        self.registered_actions.extend([
            DataVisualizationAction(),
            StatisticalAnalysisAction()
        ])
    
    def preprocess_task(self, task_description):
        """在执行前预处理任务描述"""
        # 检测数据分析关键词
        analysis_keywords = ['分析', '可视化', '统计', '趋势', '相关性']
        
        if any(keyword in task_description for keyword in analysis_keywords):
            self.logger.info("检测到数据分析任务")
            # 添加上下文信息
            enhanced_task = f"""
            数据分析任务: {task_description}
            
            请确保：
            1. 验证数据质量和完整性
            2. 执行探索性数据分析
            3. 应用适当的统计方法
            4. 生成清晰的可视化
            5. 提供可操作的洞察
            """
            return enhanced_task
        
        return task_description
    
    def run_with_new_request(self, task_description, event_stream=None):
        # 预处理任务
        enhanced_task = self.preprocess_task(task_description)
        
        # 调用父类方法
        return super().run_with_new_request(enhanced_task, event_stream)
```

## 创建自定义动作

### 基本动作结构

所有自定义动作都必须继承自 `Action` 基类：

```python
from anges.agents.agent_utils.agent_actions import Action
from anges.agents.agent_utils.events import Event
import json

class CustomAction(Action):
    def __init__(self):
        super().__init__()
        
        # 必需属性
        self.type = "CUSTOM_ACTION"
        self.guide_prompt = self._generate_guide_prompt()
        
        # 行为配置
        self.user_visible = True  # 结果对用户可见
        self.unique_action = False  # 可与其他动作组合
        self.returning_action = False  # 不终止执行循环
    
    def _generate_guide_prompt(self):
        return """
### CUSTOM_ACTION:
使用此动作执行自定义操作。

必需字段：
- action_type: 必须为 "CUSTOM_ACTION"
- parameters: 包含操作参数的字典
- description: 操作描述

示例：
{
    "action_type": "CUSTOM_ACTION",
    "parameters": {
        "input_file": "data.csv",
        "output_format": "json"
    },
    "description": "转换数据格式"
}
        """
    
    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        """处理动作执行的主要方法"""
        try:
            # 提取参数
            parameters = action_json.get('parameters', {})
            description = action_json.get('description', '执行自定义操作')
            
            # 执行自定义逻辑
            result = self._execute_custom_logic(parameters)
            
            # 创建成功事件
            event = Event(
                type="custom_action",
                reasoning=f"执行自定义动作: {description}",
                content=result,
                message=f"自定义动作完成: {description}"
            )
            
            # 添加到事件流
            run_config["event_stream"].add_event(event)
            
            # 处理用户可见消息
            if self.user_visible:
                run_config["message_handler_func"](f"✅ {description} - 完成")
                
        except Exception as e:
            # 创建错误事件
            error_event = Event(
                type="custom_action_error",
                reasoning=f"自定义动作失败: {str(e)}",
                content=f"错误: {str(e)}",
                message=f"❌ 自定义动作失败: {str(e)}"
            )
            
            run_config["event_stream"].add_event(error_event)
    
    def _execute_custom_logic(self, parameters):
        """实现您的自定义逻辑"""
        # 这里实现您的具体逻辑
        result = {
            'status': 'success',
            'message': '操作完成'
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
```

## 配置管理

### 基本配置结构

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
import yaml

@dataclass
class AgentConfig:
    # 基本配置
    agent_type: str = "base_agent"
    max_iterations: int = 50
    timeout: int = 300
    
    # 执行配置
    cmd_init_dir: str = "/tmp"
    auto_entitle: bool = False
    
    # 日志配置
    logging_level: str = "INFO"
    enable_file_logging: bool = True
    
    # 推理配置
    model_name: str = "claude-3-sonnet"
    max_tokens: int = 4000
    temperature: float = 0.1
    
    @classmethod
    def from_file(cls, config_path: str):
        """从 YAML 文件加载配置"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)
    
    def to_file(self, config_path: str):
        """保存配置到 YAML 文件"""
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.__dict__, f, default_flow_style=False, allow_unicode=True)
```

## 事件处理

### 自定义事件处理器

```python
class CustomEventHandler:
    def __init__(self):
        self.event_processors = {}
    
    def register_processor(self, event_type, processor_func):
        """注册事件处理器"""
        if event_type not in self.event_processors:
            self.event_processors[event_type] = []
        self.event_processors[event_type].append(processor_func)
    
    def process_event(self, event):
        """处理事件"""
        processors = self.event_processors.get(event.type, [])
        for processor in processors:
            try:
                processor(event)
            except Exception as e:
                print(f"事件处理器错误: {e}")

# 使用示例
event_handler = CustomEventHandler()

def log_action_events(event):
    if event.type == "action":
        print(f"执行命令: {event.content}")

event_handler.register_processor("action", log_action_events)
```

## 集成外部服务

### 数据库集成

```python
class DatabaseAction(Action):
    def __init__(self, db_config):
        super().__init__()
        self.type = "DATABASE_QUERY"
        self.db_config = db_config
        self.guide_prompt = "执行数据库查询操作"
    
    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        import sqlite3
        
        query = action_json.get('query')
        
        try:
            conn = sqlite3.connect(self.db_config['database'])
            cursor = conn.cursor()
            cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                content = f"查询结果: {results}"
            else:
                conn.commit()
                content = "查询执行成功"
            
            event = Event(
                type="database_query",
                reasoning=f"执行数据库查询: {query}",
                content=content,
                message="数据库操作完成"
            )
            
            run_config["event_stream"].add_event(event)
            
        except Exception as e:
            error_event = Event(
                type="database_error",
                reasoning=f"数据库操作失败: {str(e)}",
                content=f"错误: {str(e)}",
                message=f"数据库操作失败: {str(e)}"
            )
            
            run_config["event_stream"].add_event(error_event)
        
        finally:
            if 'conn' in locals():
                conn.close()
```

## 调试和故障排除

### 调试工具

```python
class DebugAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.debug_mode = True
        self.execution_trace = []
    
    def _prompt_and_get_action_from_response(self, event_stream):
        # 记录提示构建过程
        if self.debug_mode:
            print("=== 提示构建开始 ===")
            print(f"事件数量: {len(event_stream.events_list)}")
        
        # 调用父类方法
        result = super()._prompt_and_get_action_from_response(event_stream)
        
        if self.debug_mode:
            print("=== 提示构建完成 ===")
            print(f"响应: {result}")
        
        return result
    
    def add_execution_trace(self, action_type, details):
        """添加执行跟踪"""
        trace_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'details': details
        }
        self.execution_trace.append(trace_entry)
    
    def print_execution_summary(self):
        """打印执行摘要"""
        print("\n=== 执行摘要 ===")
        for trace in self.execution_trace:
            print(f"{trace['timestamp']}: {trace['action_type']} - {trace['details']}")
```

### 日志配置

```python
import logging
from datetime import datetime

def setup_logging(log_level=logging.INFO, log_file=None):
    """设置日志配置"""
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 设置根日志记录器
    logger = logging.getLogger('anges')
    logger.setLevel(log_level)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# 使用示例
logger = setup_logging(logging.DEBUG, 'agent_debug.log')
```

## 部署考虑

### 生产环境配置

```python
class ProductionAgent(BaseAgent):
    def __init__(self, **kwargs):
        # 生产环境特定配置
        production_config = {
            'max_iterations': 30,  # 限制迭代次数
            'timeout': 600,  # 10分钟超时
            'logging_level': logging.WARNING,  # 减少日志输出
            'auto_entitle': False,  # 禁用自动标题
        }
        
        # 合并配置
        kwargs.update(production_config)
        super().__init__(**kwargs)
        
        # 生产环境安全措施
        self.setup_security_measures()
    
    def setup_security_measures(self):
        """设置安全措施"""
        # 限制可执行命令
        self.allowed_commands = [
            'ls', 'cat', 'grep', 'find', 'python', 'pip'
        ]
        
        # 禁止危险命令
        self.blocked_commands = [
            'rm -rf', 'sudo', 'chmod 777', 'dd'
        ]
```

### 监控和指标

```python
class MonitoredAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.metrics = {
            'total_requests': 0,
            'successful_completions': 0,
            'failed_executions': 0,
            'average_execution_time': 0,
            'total_events': 0
        }
        self.start_time = None
    
    def run_with_new_request(self, task_description, event_stream=None):
        self.start_time = datetime.now()
        self.metrics['total_requests'] += 1
        
        try:
            result = super().run_with_new_request(task_description, event_stream)
            
            # 更新成功指标
            self.metrics['successful_completions'] += 1
            self.update_execution_time()
            
            return result
            
        except Exception as e:
            self.metrics['failed_executions'] += 1
            raise
    
    def update_execution_time(self):
        """更新执行时间指标"""
        if self.start_time:
            execution_time = (datetime.now() - self.start_time).total_seconds()
            current_avg = self.metrics['average_execution_time']
            total_successful = self.metrics['successful_completions']
            
            # 计算新的平均值
            new_avg = ((current_avg * (total_successful - 1)) + execution_time) / total_successful
            self.metrics['average_execution_time'] = new_avg
    
    def get_metrics(self):
        """获取性能指标"""
        return self.metrics.copy()
```

## 高级模式

### 多代理协作

```python
class OrchestratorAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.child_agents = {}
        self.task_queue = []
    
    def register_child_agent(self, name, agent_class, config):
        """注册子代理"""
        self.child_agents[name] = {
            'class': agent_class,
            'config': config,
            'instance': None
        }
    
    def delegate_task(self, task_description, agent_name):
        """将任务委托给子代理"""
        if agent_name not in self.child_agents:
            raise ValueError(f"未知的代理: {agent_name}")
        
        agent_info = self.child_agents[agent_name]
        
        # 创建代理实例（如果不存在）
        if agent_info['instance'] is None:
            agent_info['instance'] = agent_info['class'](**agent_info['config'])
        
        # 执行任务
        child_agent = agent_info['instance']
        result = child_agent.run_with_new_request(task_description)
        
        return result
```

### 插件系统

```python
class PluginManager:
    def __init__(self):
        self.plugins = {}
        self.hooks = {}
    
    def register_plugin(self, name, plugin_class):
        """注册插件"""
        self.plugins[name] = plugin_class()
    
    def register_hook(self, event_name, callback):
        """注册钩子"""
        if event_name not in self.hooks:
            self.hooks[event_name] = []
        self.hooks[event_name].append(callback)
    
    def trigger_hook(self, event_name, *args, **kwargs):
        """触发钩子"""
        hooks = self.hooks.get(event_name, [])
        for hook in hooks:
            try:
                hook(*args, **kwargs)
            except Exception as e:
                print(f"钩子执行错误: {e}")

class PluginEnabledAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plugin_manager = PluginManager()
    
    def run_with_new_request(self, task_description, event_stream=None):
        # 触发开始钩子
        self.plugin_manager.trigger_hook('task_start', task_description)
        
        try:
            result = super().run_with_new_request(task_description, event_stream)
            
            # 触发成功钩子
            self.plugin_manager.trigger_hook('task_success', result)
            
            return result
            
        except Exception as e:
            # 触发错误钩子
            self.plugin_manager.trigger_hook('task_error', e)
            raise
```

此实现指南提供了扩展 Anges 框架的全面方法。通过遵循这些模式和最佳实践，您可以创建强大、可维护且可扩展的 AI 代理解决方案。
