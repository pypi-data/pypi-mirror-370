<!-- Language switcher - place at top of every documentation file -->
**语言**: [English](README.md) | [中文](README.zh.md)

---

# Anges: 开源自主工程助手

Anges 是一个由大语言模型驱动的工程代理系统，设计理念是易于使用，同时具有高度可定制性和简约性。

## 快速开始

### 安装和首次运行

```bash
# 从 PyPI 安装
pip install anges

# 设置您的 API 密钥。Anges 默认使用 Anthropic 的 Claude。
# （请参阅下面的配置部分以使用其他模型，如 Gemini 或 OpenAI）
export ANTHROPIC_API_KEY=<您的API密钥>

# 运行您的第一个任务
anges -q "操作系统版本是什么？"
```

### 基本用法

```bash
# 交互模式（用于对话式任务）
anges -i

# 从命令行直接执行任务
anges -q "列出当前目录中的所有 Python 文件。"

# 执行文件中描述的任务
anges -f task_description.txt

# 启动 Web 界面
anges ui --port 5000 --password 您的密码

# 帮助菜单
anges -h
```

*Anges 检查操作系统和列出文件的快速演示。*
![demo](docs/assets/simple_linux_operation.gif)

*Anges UI 的快速预览。*
![demo](docs/assets/anges_ui.jpg)

### 配置

默认配置位于 `anges/configs/default_config.yaml`。

您可以通过在 `~/.anges/config.yaml` 创建 `config.yaml` 文件来覆盖这些设置。

例如，配置默认代理使用 Google 的 Gemini Pro：

```bash
# 创建配置文件以切换默认模型
cat > ~/.anges/config.yaml <<EOF
agents:
  default_agent:
    model_name: "gemini"
EOF

# 导出相应的 API 密钥
export GOOGLE_API_KEY=<您的GEMINI_API密钥>
```

#### MCP 配置

Anges 支持模型上下文协议（MCP）来集成外部工具和服务。您可以使用 JSON 配置文件配置 MCP 服务器：

```bash
# 创建 MCP 配置文件
cat > mcp_config.json <<EOF
{
  "filesystem": {
    "command": "npx",
    "args": ["-g", "@modelcontextprotocol/server-filesystem", "/path/to/directory"]
  },
  "sqlite": {
    "command": "npx", 
    "args": ["-g", "@modelcontextprotocol/server-sqlite", "/path/to/database.db"]
  }
}
EOF

# 在 CLI 中使用 MCP 配置
anges -q "使用 MCP 列出文件" --mcp_config mcp_config.json

# 或通过 Web 界面的设置面板配置
anges ui --port 5000 --password 您的密码
```

### 高级用法

  * **工作目录：** 您可以从 UI 或 CLI 设置代理的工作目录。这设置了操作的默认位置，但不强制执行严格的权限边界。

  * **前缀命令：** 您可以配置前缀命令（例如，`export MY_VAR=... &&`），该命令将在代理运行的每个命令之前执行。这对于设置一致的环境很有用。

  * **MCP 集成：** Anges 支持模型上下文协议（MCP），用于连接外部工具和服务。您可以通过配置文件或 Web 界面配置 MCP 服务器。

  * **默认代理 vs. 编排器：**

      * **默认代理：** 适用于人类可以在几分钟内完成的简单、单步任务。它快速而直接。
      * **编排器：** 适用于需要研究、规划和代码迭代的复杂、多步骤问题。编排器代理可以分解任务并委托给其他代理。

  * **事件流：** 每个动作、思考过程和命令都记录为 `~/.anges/data/event_streams` 中的 JSON 文件。这提供了完全的透明度，并为微调或分析创建了有价值的数据集。

### 演示和示例

  * [Linux 和云运维](https://demo.anges.ai/?chatId=QIVELO41)
  * [创建演示网站](https://demo.anges.ai/?chatId=dCg8a13M)
  * [解决复杂任务（3小时运行）](https://demo.anges.ai/?chatId=atktkEDt)
  * [递归自调用测试](https://demo.anges.ai/?chatId=pyA5pYEm)

在 **[https://demo.anges.ai](https://demo.anges.ai)** 探索更多演示。


## 为什么选择 Anges？

| 功能 | **Anges** | **Gemini CLI** | **Cursor** |
| :--- | :--- | :--- | :--- |
| **开源** | ✅ 是 (MIT) | ✅ 是 (Apache-2.0) | ❌ 否 |
| **CLI 支持** | ✅ 是 | ✅ 是 | ✅ 是 |
| **Web UI** | ✅ 是 | ❌ 否 | ❌ 否 |
| **移动 Web 访问** | ✅ 是 | ❌ 否 | ❌ 否 |
| **可定制和可修改** | ✅ 灵活 (Python) | ⚠️ 可分叉 | ❌ 已压缩 |
| **多代理编排**| ✅ 是 | ❌ 否 | ❌ 否 |
| **模型无关** | ✅ 任何模型 | ❌ 仅 Gemini | ❌ Claude/OpenAI |

### 从顾问到助手

我们习惯于大语言模型作为顾问——它们坐在聊天框后面，等待复制粘贴的上下文并提供您仍然需要自己运行的建议。

但是，如果您给 AI **真正的访问权限** 来访问您的 shell、工具和工作环境会怎样？如果它可以**与您一起工作**，而不仅仅是与您交谈会怎样？

Anges 将这个想法变成了一个实用的、可修改的现实，为大语言模型提供受控的执行能力，同时让工程师完全参与其中。

### 主要优势

  * **真正的自动化，而不仅仅是建议**
    Anges 不仅仅建议命令——它执行命令。它读取输出，处理错误，并规划下一步行动。它是一个执行者，而不是一个空谈者。

  * **模型无关**
    使用您想要的任何模型——Claude、OpenAI、Gemini、Llama、本地模型——所有这些都易于配置。您控制大脑。

  * **灵活的界面**
    从您的终端、容器中或通过手机上的 Web UI 工作。Anges 在您所在的地方与您会面。

  * **设计上可修改**
    用干净、模块化的 Python 编写。一切都是公开的，易于修改。没有隐藏提示或逻辑的重度抽象。

  * **内置编排**
    使用可以分解问题、委托工作和递归执行的多代理系统处理复杂任务——无需样板代码。

  * **透明的事件日志**
    每个命令、决策和观察都保存到本地事件流中。您拥有代理工作的完美、可重放的审计跟踪。

## 核心设计理念

### 1. 简约性胜过复杂性

Anges 专注于核心功能：
  * **执行命令** 使用 `RUN_SHELL_CMD`
  * **编辑文件** 使用 `EDIT_FILE`
  * **读取多媒体内容** 使用 `READ_MIME_FILES`
  * **调用外部工具** 使用 `USE_MCP_TOOL`
  * **任务完成** 使用 `TASK_COMPLETE`
  * **寻求帮助** 使用 `HELP_NEEDED`

没有数百个专门的工具或复杂的插件架构。这六个动作涵盖了大多数工程任务。

### 2. 透明度胜过黑盒

每个决策、命令和观察都记录在本地事件流中。您可以：
  * 查看代理的确切思考过程
  * 重放任何会话以进行调试
  * 将事件流用作微调数据
  * 审计所有操作以确保安全性

### 3. 灵活性胜过固执己见

  * **模型无关：** 轻松切换 LLM 提供商
  * **可修改：** 用干净的 Python 编写，易于定制
  * **可配置：** 通过 YAML 文件调整行为
  * **可扩展：** 添加新动作或代理类型

### 4. 实用性胜过完美

Anges 专为真实世界的工程任务而构建：
  * 处理不完美的环境
  * 从错误中恢复
  * 适应不同的工作流程
  * 在不确定时寻求人类帮助

## 架构概述

### 代理类型

**默认代理**
  * 最适合：简单、直接的任务（5-15分钟）
  * 行为：直接执行，最少规划
  * 示例："列出所有 Python 文件"、"安装依赖项"、"运行测试"

**编排器代理**
  * 最适合：复杂、多步骤项目（30分钟-数小时）
  * 行为：分解任务，委托给其他代理
  * 示例："构建完整的 Web 应用"、"重构代码库"、"设置 CI/CD"

### 动作系统

所有代理通过五个核心动作运行：

```python
# 命令执行
{
    "action_type": "RUN_SHELL_CMD",
    "command": "ls -la",
    "shell_cmd_timeout": 30
}

# 文件操作
{
    "action_type": "EDIT_FILE",
    "directive_line": "NEW_FILE example.py",
    "content": "print('Hello, World!')"
}

# 多媒体分析
{
    "action_type": "READ_MIME_FILES",
    "question": "这张图片显示了什么？",
    "inputs": ["screenshot.png"]
}
```

### 事件流系统

每个代理交互都保存为结构化的 JSON 事件流：

```json
{
    "event_type": "ACTION",
    "timestamp": "2024-01-15T10:30:00Z",
    "agent_id": "default_agent",
    "action": {
        "action_type": "RUN_SHELL_CMD",
        "command": "python test.py",
        "reasoning": "运行测试以验证功能"
    },
    "result": {
        "exit_code": 0,
        "stdout": "所有测试通过",
        "stderr": ""
    }
}
```

## 详细安装指南

### 系统要求

  * **Python：** 3.8 或更高版本
  * **操作系统：** Linux、macOS 或 Windows
  * **内存：** 最少 512MB RAM
  * **磁盘空间：** 100MB 用于安装和日志

### 安装方法

#### 方法 1：从 PyPI 安装（推荐）

```bash
# 安装最新稳定版本
pip install anges

# 或安装特定版本
pip install anges==0.2.0

# 验证安装
anges --version
```

#### 方法 2：从源代码安装

```bash
# 克隆仓库
git clone https://github.com/hailon-anges/anges.git
cd anges

# 安装开发依赖
pip install -e .

# 运行测试以验证安装
python -m pytest tests/
```

#### 方法 3：使用 Docker

```bash
# 拉取官方镜像
docker pull anges/anges:latest

# 运行容器
docker run -it \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -v $(pwd):/workspace \
  anges/anges:latest
```

### API 密钥配置

#### Anthropic Claude（默认）

```bash
# 设置环境变量
export ANTHROPIC_API_KEY="your-api-key-here"

# 或在配置文件中设置
cat > ~/.anges/config.yaml <<EOF
api_keys:
  anthropic: "your-api-key-here"
EOF
```

#### OpenAI GPT

```bash
# 环境变量
export OPENAI_API_KEY="your-openai-key"

# 配置文件
cat > ~/.anges/config.yaml <<EOF
agents:
  default_agent:
    model_name: "openai"
api_keys:
  openai: "your-openai-key"
EOF
```

#### Google Gemini

```bash
# 环境变量
export GOOGLE_API_KEY="your-gemini-key"

# 配置文件
cat > ~/.anges/config.yaml <<EOF
agents:
  default_agent:
    model_name: "gemini"
api_keys:
  google: "your-gemini-key"
EOF
```

## CLI 使用详解

### 基本命令

```bash
# 快速任务执行
anges -q "您的任务描述"

# 交互模式
anges -i

# 从文件执行任务
anges -f task.txt

# 指定工作目录
anges -q "列出文件" --work-dir /path/to/directory

# 使用特定代理
anges -q "复杂任务" --agent orchestrator

# 设置超时
anges -q "长时间任务" --timeout 3600
```

### 高级 CLI 选项

```bash
# 自定义配置文件
anges -q "任务" --config /path/to/config.yaml

# 启用详细日志
anges -q "任务" --verbose

# 禁用颜色输出
anges -q "任务" --no-color

# 设置前缀命令
anges -q "任务" --prefix-cmd "export VAR=value &&"

# 指定 MCP 配置文件
anges -q "任务" --mcp_config /path/to/mcp_config.json

# 指定事件流输出
anges -q "任务" --event-stream-file custom_events.jsonl
```

## Web UI 界面

### 启动 Web 界面

```bash
# 基本启动
anges ui

# 自定义端口和密码
anges ui --port 8080 --password mypassword

# 绑定到特定 IP
anges ui --host 0.0.0.0 --port 5000

# 启用 HTTPS
anges ui --ssl-cert cert.pem --ssl-key key.pem
```

### Web UI 功能

  * **实时聊天界面：** 与代理进行对话式交互
  * **文件浏览器：** 浏览和编辑工作目录中的文件
  * **事件流查看器：** 实时查看代理的操作和思考过程
  * **配置管理：** 通过 Web 界面调整设置
  * **MCP 管理：** 在设置面板中管理 MCP 服务器配置，实时查看连接状态和可用工具
  * **移动友好：** 在手机和平板电脑上完全可用

### 安全注意事项

```bash
# 设置强密码
anges ui --password "$(openssl rand -base64 32)"

# 限制访问 IP
anges ui --allowed-ips 192.168.1.0/24,10.0.0.0/8

# 启用会话超时
anges ui --session-timeout 3600
```

## 配置系统详解

### 配置文件层次结构

1. **默认配置：** `anges/configs/default_config.yaml`
2. **用户配置：** `~/.anges/config.yaml`
3. **项目配置：** `./anges_config.yaml`
4. **环境变量：** `ANGES_*` 前缀
5. **命令行参数：** 最高优先级

### 完整配置示例

```yaml
# ~/.anges/config.yaml
api_keys:
  anthropic: "your-anthropic-key"
  openai: "your-openai-key"
  google: "your-google-key"

agents:
  default_agent:
    model_name: "claude"
    max_tokens: 4096
    temperature: 0.1
    timeout: 300
    
  orchestrator:
    model_name: "claude"
    max_tokens: 8192
    temperature: 0.2
    max_iterations: 50

logging:
  level: "INFO"
  file: "~/.anges/logs/anges.log"
  max_size: "10MB"
  backup_count: 5

ui:
  default_port: 5000
  default_password: null
  session_timeout: 7200
  max_file_size: "10MB"

security:
  allowed_commands: ["ls", "cat", "python", "npm", "git"]
  blocked_commands: ["rm -rf", "sudo", "chmod 777"]
  max_execution_time: 1800
```

## 实用示例

### 系统管理任务

```bash
# 检查系统状态
anges -q "检查系统磁盘使用情况、内存使用情况和运行的进程"

# 日志分析
anges -q "分析 /var/log/nginx/error.log 中的最新错误"

# 性能监控
anges -q "监控系统性能 30 秒并生成报告"
```

### 开发任务

```bash
# 代码审查
anges -q "审查这个 Python 项目的代码质量并提出改进建议"

# 测试自动化
anges -q "为 src/ 目录中的所有 Python 模块创建单元测试"

# 文档生成
anges -q "为这个 API 项目生成 OpenAPI 文档"
```

### 数据处理

```bash
# CSV 分析
anges -q "分析 data.csv 文件并创建数据摘要报告"

# 数据清理
anges -q "清理 users.json 文件中的重复条目和无效数据"

# 可视化
anges -q "从 sales_data.csv 创建销售趋势图表"
```

### Web 开发

```bash
# 快速原型
anges -q "创建一个带有用户认证的简单 Flask Web 应用"

# 前端开发
anges -q "构建一个响应式的产品展示页面，使用 HTML、CSS 和 JavaScript"

# API 开发
anges -q "创建一个 RESTful API 来管理待办事项，包含 CRUD 操作"
```

### MCP 集成示例

```bash
# 使用 MCP 文件系统服务器
anges -q "使用 MCP 文件系统列出项目中的所有 Python 文件" --mcp_config mcp_config.json

# 使用 MCP 数据库服务器
anges -q "使用 MCP 查询数据库获取用户信息" --mcp_config mcp_config.json

# 使用多个 MCP 服务器
anges -q "使用 MCP 工具从数据库分析数据并保存到文件系统" --mcp_config mcp_config.json
```

## 故障排除

### 常见问题

**问题：API 密钥错误**
```bash
# 检查环境变量
echo $ANTHROPIC_API_KEY

# 验证配置文件
cat ~/.anges/config.yaml

# 测试 API 连接
anges -q "简单测试" --verbose
```

**问题：权限被拒绝**
```bash
# 检查文件权限
ls -la ~/.anges/

# 修复权限
chmod 755 ~/.anges/
chmod 644 ~/.anges/config.yaml
```

**问题：命令超时**
```bash
# 增加超时时间
anges -q "长时间任务" --timeout 3600

# 或在配置中设置
echo "default_timeout: 1800" >> ~/.anges/config.yaml
```

### 调试技巧

```bash
# 启用详细日志
anges -q "任务" --verbose

# 查看事件流
tail -f ~/.anges/data/event_streams/latest.jsonl

# 检查系统日志
tail -f ~/.anges/logs/anges.log
```

## API 参考

### 核心动作类型

#### RUN_SHELL_CMD
执行 shell 命令并返回结果。

```python
{
    "action_type": "RUN_SHELL_CMD",
    "command": "ls -la",
    "shell_cmd_timeout": 30,
    "run_in_background": false
}
```

#### EDIT_FILE
创建、修改或删除文件内容。

```python
{
    "action_type": "EDIT_FILE",
    "directive_line": "NEW_FILE example.py",
    "content": "print('Hello, World!')"
}
```

#### READ_MIME_FILES
分析图像、PDF、视频等多媒体文件。

```python
{
    "action_type": "READ_MIME_FILES",
    "question": "这张图片显示了什么？",
    "inputs": ["screenshot.png"],
    "output": "analysis.txt"
}
```

#### USE_MCP_TOOL
通过模型上下文协议调用外部工具。

```python
{
    "action_type": "USE_MCP_TOOL",
    "mcp_server_name": "filesystem",
    "tool_name": "list_directory",
    "tool_args": {
        "path": "/data"
    }
}
```

### 事件流格式

```json
{
    "event_id": "evt_123456789",
    "event_type": "ACTION",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "agent_id": "default_agent",
    "session_id": "sess_abcdef123",
    "action": {
        "action_type": "RUN_SHELL_CMD",
        "command": "python test.py",
        "reasoning": "运行测试以验证功能"
    },
    "result": {
        "exit_code": 0,
        "stdout": "所有测试通过\n",
        "stderr": "",
        "execution_time": 2.34
    }
}
```

## 开发和贡献

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/hailon-anges/anges.git
cd anges

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -e ".[dev]"

# 安装预提交钩子
pre-commit install

# 运行测试
python -m pytest tests/ -v

# 运行代码检查
flake8 anges/
black anges/
mypy anges/
```

### 项目结构

```
anges/
├── anges/                 # 主包
│   ├── core/             # 核心功能
│   ├── agents/           # 代理实现
│   ├── actions/          # 动作处理器
│   ├── ui/               # Web 界面
│   └── utils/            # 实用工具
├── tests/                # 测试套件
├── docs/                 # 文档
├── examples/             # 示例代码
└── configs/              # 配置文件
```

### 贡献指南

我们欢迎各种形式的贡献！

#### 报告问题
1. 检查现有的 [GitHub Issues](https://github.com/hailon-anges/anges/issues)
2. 创建新的 issue，包含：
   - 清晰的问题描述
   - 重现步骤
   - 预期行为 vs 实际行为
   - 系统信息（OS、Python 版本等）

#### 提交代码
1. Fork 仓库
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

#### 代码规范
- 遵循 PEP 8 风格指南
- 使用 Black 进行代码格式化
- 添加类型注解
- 编写测试用例
- 更新相关文档

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_agents.py

# 运行带覆盖率的测试
pytest --cov=anges tests/

# 运行集成测试
pytest tests/integration/ -v
```

## 性能优化

### 系统性能调优

```python
#!/usr/bin/env python3
"""
系统性能优化脚本
优化 Anges 在生产环境中的性能
"""

import os
import sys
import yaml
from pathlib import Path

def optimize_system_performance():
    """优化系统性能设置"""
    config_path = Path.home() / ".anges" / "config.yaml"
    
    # 性能优化配置
    performance_config = {
        "agents": {
            "default_agent": {
                "model_name": "claude",
                "max_tokens": 4096,
                "temperature": 0.1,
                "timeout": 300,
                "max_retries": 3
            }
        },
        "logging": {
            "level": "WARNING",  # 减少日志输出
            "async_logging": True
        },
        "performance": {
            "enable_caching": True,
            "cache_size": 1000,
            "parallel_execution": True,
            "max_workers": 4
        }
    }
    
    try:
        # 创建配置目录
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入优化配置
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(performance_config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"✅ 性能配置已保存到 {config_path}")
        return True
        
    except Exception as e:
        print(f"❌ 配置保存失败: {e}")
        return False

if __name__ == "__main__":
    success = optimize_system_performance()
    if success:
        print("✅ 性能优化完成！")
    else:
        print("❌ 优化工作流程失败。")
```

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 致谢

- 感谢所有贡献者和社区成员
- 特别感谢开源社区提供的优秀工具和库
- 感谢所有提供反馈和建议的用户

## 联系方式

- **GitHub Issues**: [https://github.com/hailon-anges/anges/issues](https://github.com/hailon-anges/anges/issues)
- **文档**: [https://docs.anges.ai](https://docs.anges.ai)
- **演示**: [https://demo.anges.ai](https://demo.anges.ai)
- **社区**: [Discord](https://discord.gg/anges)

---

*本文档是持续改进计划的一部分。后续更新将添加更多技术细节、架构图和全面的示例。*

---

<!-- Language switcher - place at bottom of every documentation file -->
**语言**: [English](README.md) | [中文](README.zh.md)
