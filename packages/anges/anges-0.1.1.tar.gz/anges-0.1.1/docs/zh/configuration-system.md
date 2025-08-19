**语言**: [English](../configuration-system.md) | [中文](configuration-system.md)

---
# 配置系统文档

Anges 配置系统通过 YAML 文件和环境变量提供了灵活且结构化的应用程序设置管理方式。本文档涵盖配置架构、可用选项和使用模式。

## 概述

配置系统围绕数据类构建，定义了强类型的配置模式。它支持：

- **基于 YAML 的配置文件**，用于默认和覆盖设置
- **环境变量覆盖**，提供部署灵活性
- **嵌套配置结构**，用于组织复杂设置
- **类型验证和转换**，确保配置正确性
- **配置继承和合并**，实现模块化配置管理

## 配置架构

### 核心配置类

配置系统使用 Python 数据类来定义配置结构：

```python
from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass
class AgentConfig:
    """代理配置设置"""
    model_name: str = "claude-3-sonnet-20240229"
    max_tokens: int = 4000
    temperature: float = 0.0
    timeout: int = 300
    max_retries: int = 3

@dataclass
class WebInterfaceConfig:
    """Web 界面配置设置"""
    host: str = "0.0.0.0"
    port: int = 5000
    enable_authentication: bool = True
    session_timeout: int = 3600
    secret_key: str = "dev-secret-key"
    max_concurrent_sessions: int = 100

@dataclass
class Config:
    """主配置类"""
    agent: AgentConfig
    web_interface: WebInterfaceConfig
    debug: bool = False
    log_level: str = "INFO"
```

### 配置文件结构

配置文件使用 YAML 格式组织：

```yaml
# config/default.yaml
agent:
  model_name: "claude-3-sonnet-20240229"
  max_tokens: 4000
  temperature: 0.0
  timeout: 300
  max_retries: 3

web_interface:
  host: "0.0.0.0"
  port: 5000
  enable_authentication: true
  session_timeout: 3600
  secret_key: "dev-secret-key"
  max_concurrent_sessions: 100

debug: false
log_level: "INFO"
```

## 配置加载

### 配置加载器

配置系统使用分层加载方法：

```python
from anges.config import ConfigLoader, Config

# 创建配置加载器
loader = ConfigLoader()

# 加载配置
config = loader.load_config()

# 访问配置值
print(f"代理模型: {config.agent.model_name}")
print(f"Web 端口: {config.web_interface.port}")
```

### 加载顺序

配置按以下优先级顺序加载：

1. **默认值**：数据类中定义的默认值
2. **默认配置文件**：`config/default.yaml`
3. **环境特定配置**：`config/{environment}.yaml`
4. **本地覆盖**：`config/local.yaml`（被 git 忽略）
5. **环境变量**：运行时环境变量

### 环境变量覆盖

任何配置值都可以通过环境变量覆盖：

```bash
# 覆盖代理模型
export ANGES_AGENT_MODEL_NAME="gpt-4"

# 覆盖 Web 端口
export ANGES_WEB_INTERFACE_PORT=8080

# 覆盖调试模式
export ANGES_DEBUG=true
```

环境变量命名约定：
- 前缀：`ANGES_`
- 嵌套结构：使用下划线分隔（例如 `AGENT_MODEL_NAME`）
- 大写：所有环境变量名都是大写

## 配置部分

### 代理配置

代理配置控制 AI 代理的行为：

```yaml
agent:
  # 模型设置
  model_name: "claude-3-sonnet-20240229"  # AI 模型标识符
  max_tokens: 4000                        # 最大响应令牌数
  temperature: 0.0                        # 响应随机性（0.0-1.0）
  
  # 执行设置
  timeout: 300                           # 任务超时（秒）
  max_retries: 3                         # 失败时的最大重试次数
  
  # 行为设置
  enable_thinking: true                  # 启用内部思考过程
  max_consecutive_actions: 30            # 连续操作限制
  
  # 安全设置
  allowed_commands: []                   # 允许的 shell 命令（空表示全部）
  blocked_commands: ["rm -rf", "sudo"]   # 被阻止的危险命令
  working_directory: "/tmp/anges"         # 代理工作目录
```

#### 代理配置参数

- **model_name**: 要使用的 AI 模型（Claude、GPT、Gemini 等）
- **max_tokens**: 单个响应的最大令牌数
- **temperature**: 控制响应创造性（0.0 = 确定性，1.0 = 创造性）
- **timeout**: 单个任务的最大执行时间
- **max_retries**: 失败操作的重试次数
- **enable_thinking**: 是否启用代理的内部推理过程
- **max_consecutive_actions**: 防止无限循环的操作限制
- **allowed_commands**: 代理可执行的命令白名单
- **blocked_commands**: 出于安全考虑被禁止的命令
- **working_directory**: 代理操作的基础目录

### Web 界面配置

Web 界面配置控制 Web 服务器和用户界面：

```yaml
web_interface:
  # 服务器设置
  host: "0.0.0.0"                       # 绑定主机地址
  port: 5000                            # 服务器端口
  
  # 身份验证
  enable_authentication: true           # 启用用户身份验证
  secret_key: "your-secret-key"          # 会话加密密钥
  session_timeout: 3600                 # 会话超时（秒）
  
  # 性能设置
  max_concurrent_sessions: 100          # 最大并发会话数
  request_timeout: 30                   # HTTP 请求超时
  
  # CORS 设置
  cors_origins: ["*"]                   # 允许的 CORS 源
  cors_methods: ["GET", "POST", "PUT", "DELETE"]
  
  # 静态文件
  static_folder: "static"               # 静态文件目录
  template_folder: "templates"          # 模板目录
```

### 日志配置

日志配置控制应用程序日志记录：

```yaml
logging:
  # 基本设置
  level: "INFO"                         # 日志级别（DEBUG、INFO、WARNING、ERROR）
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  # 文件日志
  file_logging:
    enabled: true
    filename: "logs/anges.log"
    max_bytes: 10485760                 # 10MB
    backup_count: 5
  
  # 控制台日志
  console_logging:
    enabled: true
    colorize: true
  
  # 特定记录器
  loggers:
    "anges.agents": "DEBUG"
    "anges.web_interface": "INFO"
    "werkzeug": "WARNING"
```

### 数据库配置

数据库配置（如果使用持久化存储）：

```yaml
database:
  # 连接设置
  url: "sqlite:///anges.db"             # 数据库连接 URL
  echo: false                           # 启用 SQL 查询日志
  
  # 连接池设置
  pool_size: 5                          # 连接池大小
  max_overflow: 10                      # 最大溢出连接
  pool_timeout: 30                      # 连接超时
  
  # 迁移设置
  auto_migrate: true                    # 自动运行数据库迁移
  migration_directory: "migrations"     # 迁移脚本目录
```

## 环境特定配置

### 开发环境

```yaml
# config/development.yaml
debug: true
log_level: "DEBUG"

agent:
  timeout: 600                          # 开发时更长的超时
  
web_interface:
  enable_authentication: false         # 开发时禁用身份验证
  
logging:
  console_logging:
    colorize: true
```

### 生产环境

```yaml
# config/production.yaml
debug: false
log_level: "WARNING"

agent:
  timeout: 300
  max_retries: 5                        # 生产环境更多重试
  
web_interface:
  enable_authentication: true
  session_timeout: 1800                 # 更短的会话超时
  
logging:
  file_logging:
    enabled: true
    filename: "/var/log/anges/anges.log"
```

### 测试环境

```yaml
# config/testing.yaml
debug: true
log_level: "ERROR"                      # 测试时减少日志噪音

agent:
  timeout: 60                           # 测试时快速超时
  
database:
  url: "sqlite:///:memory:"              # 内存数据库用于测试
```

## 配置验证

### 内置验证

配置系统包括内置验证：

```python
from anges.config import validate_config, ConfigValidationError

try:
    config = load_config()
    validate_config(config)
except ConfigValidationError as e:
    print(f"配置验证失败: {e}")
```

### 自定义验证

添加自定义验证规则：

```python
from anges.config import ConfigValidator

class CustomValidator(ConfigValidator):
    def validate_agent_config(self, agent_config):
        if agent_config.max_tokens < 100:
            raise ConfigValidationError("max_tokens 必须至少为 100")
        
        if agent_config.temperature < 0 or agent_config.temperature > 1:
            raise ConfigValidationError("temperature 必须在 0.0 和 1.0 之间")

# 使用自定义验证器
validator = CustomValidator()
validator.validate(config)
```

## 配置实用工具

### 配置检查器

检查当前配置：

```python
from anges.config import ConfigInspector

inspector = ConfigInspector(config)

# 显示所有配置值
inspector.print_config()

# 检查特定部分
inspector.print_section("agent")

# 查找配置源
source = inspector.get_config_source("agent.model_name")
print(f"model_name 来源: {source}")  # 例如："environment" 或 "config/local.yaml"
```

### 配置导出

导出当前配置：

```python
from anges.config import export_config

# 导出为 YAML
export_config(config, "current_config.yaml", format="yaml")

# 导出为 JSON
export_config(config, "current_config.json", format="json")

# 导出环境变量
export_config(config, "config.env", format="env")
```

## 高级用法

### 动态配置更新

运行时更新配置：

```python
from anges.config import ConfigManager

config_manager = ConfigManager()

# 更新配置值
config_manager.update_config("agent.max_tokens", 8000)

# 重新加载配置
config_manager.reload_config()

# 监听配置变化
config_manager.watch_config_files()
```

### 配置模板

使用模板进行配置生成：

```yaml
# config/template.yaml
agent:
  model_name: "${MODEL_NAME:-claude-3-sonnet-20240229}"
  max_tokens: ${MAX_TOKENS:-4000}
  timeout: ${TIMEOUT:-300}

web_interface:
  host: "${WEB_HOST:-0.0.0.0}"
  port: ${WEB_PORT:-5000}
```

### 配置继承

配置文件可以继承其他配置：

```yaml
# config/base.yaml
agent:
  model_name: "claude-3-sonnet-20240229"
  max_tokens: 4000

# config/custom.yaml
_inherit: "base.yaml"
agent:
  max_tokens: 8000  # 覆盖基础配置
  temperature: 0.2  # 添加新设置
```

## 最佳实践

### 1. 配置组织

- 将相关设置分组到逻辑部分
- 使用描述性的配置键名
- 为所有配置选项提供合理的默认值
- 记录配置选项的用途和有效值

### 2. 安全性

- 永远不要在配置文件中硬编码敏感信息
- 对敏感值使用环境变量
- 使用 `.gitignore` 排除本地配置文件
- 定期轮换密钥和令牌

```yaml
# 好的做法
web_interface:
  secret_key: "${SECRET_KEY}"  # 从环境变量读取

# 不好的做法
web_interface:
  secret_key: "hardcoded-secret"  # 永远不要这样做
```

### 3. 环境管理

- 为每个部署环境使用单独的配置文件
- 使用环境变量进行特定于部署的设置
- 在部署前验证配置
- 保持开发和生产配置同步

### 4. 文档

- 记录所有配置选项
- 提供配置示例
- 解释配置值之间的依赖关系
- 保持配置文档最新

### 5. 测试

- 为不同配置场景编写测试
- 验证配置加载和验证
- 测试环境变量覆盖
- 验证默认配置的工作

```python
# 配置测试示例
def test_config_loading():
    config = load_config()
    assert config.agent.model_name is not None
    assert config.web_interface.port > 0

def test_environment_override():
    os.environ["ANGES_AGENT_MAX_TOKENS"] = "8000"
    config = load_config()
    assert config.agent.max_tokens == 8000
```

## 故障排除

### 常见问题

#### 1. 配置文件未找到

**错误**: `FileNotFoundError: config/default.yaml`

**解决方案**:
- 确认配置文件存在于正确位置
- 检查工作目录
- 验证文件权限

#### 2. 环境变量未被识别

**错误**: 环境变量覆盖不起作用

**解决方案**:
- 检查环境变量命名约定
- 确认变量在应用程序启动前设置
- 验证变量类型转换

#### 3. 配置验证失败

**错误**: `ConfigValidationError`

**解决方案**:
- 检查配置值类型
- 验证必需字段
- 确认值在有效范围内

### 调试配置

启用配置调试：

```python
import logging
logging.getLogger("anges.config").setLevel(logging.DEBUG)

# 这将显示：
# - 配置文件加载顺序
# - 环境变量覆盖
# - 最终配置值
```

配置系统为 Anges 应用程序提供了强大而灵活的设置管理，支持从简单的开发设置到复杂的生产部署的各种用例。