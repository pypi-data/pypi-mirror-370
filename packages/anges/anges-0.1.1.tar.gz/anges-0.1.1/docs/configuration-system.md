**Languages**: [English](configuration-system.md) | [中文](zh/configuration-system.md)

---
# Configuration System Documentation

The Anges configuration system provides a flexible and structured way to manage application settings through YAML files and environment variables. This document covers the configuration architecture, available options, and usage patterns.

## Overview

The configuration system is built around dataclasses that define strongly-typed configuration schemas. It supports:

- **YAML-based configuration files** for default and override settings
- **Environment variable overrides** for deployment flexibility
- **Hierarchical configuration structure** for organized settings
- **Type safety** through dataclass definitions
- **Validation** of required configuration values

## Configuration Architecture

The configuration system is organized into several main categories:

### Model API Configuration

Supports multiple AI model providers with their specific settings:

#### OpenAI Configuration
```yaml
model_api:
  openai:
    model: "gpt-4"
    api_key: "your-openai-api-key"
```

#### Anthropic Configuration
```yaml
model_api:
  anthropic:
    model: "claude-3-sonnet-20240229"
    api_key: "your-anthropic-api-key"
```

#### Google Vertex AI (Gemini)
```yaml
model_api:
  gemini:
    model: "gemini-pro"
    gcp_project: "your-gcp-project"
    gcp_region: "us-central1"
```

#### Google GenAI (Gemini)
```yaml
model_api:
  genai_gemini:
    model: "gemini-pro"
    api_key: "your-genai-api-key"
```

#### Vertex Claude
```yaml
model_api:
  vertex_claude:
    model: "claude-3-sonnet@20240229"
    gcp_project: "your-gcp-project"
    gcp_region: "us-central1"
```

#### Deepseek Configuration
```yaml
model_api:
  deepseek:
    model: "deepseek-chat"
    api_key: "your-deepseek-api-key"
```

### Agent Configuration

Each agent type has its own configuration section with common parameters:

```yaml
agents:
  default_agent:
    shell_cmd_timeout: 300
    max_number_of_events_to_exhaust: 100
    max_consecutive_actions_to_summarize: 30
    default_agent_path: "anges/agents/default_agent.py"
    recent_content_not_truncating: 5
    max_consecutive_content_lines: 50
    model_name: "gpt-4"
    cmd_init_dir: "./"
  
  task_analyzer:
    # Same structure as default_agent
    
  task_executor:
    # Same structure as default_agent
    
  orchestrator:
    # Same structure as default_agent
```

#### Agent Configuration Parameters

- **shell_cmd_timeout**: Maximum time (seconds) for shell command execution
- **max_number_of_events_to_exhaust**: Maximum events to process since the last user input before stopping
- **max_consecutive_actions_to_summarize**: Number of actions before summarization
- **default_agent_path**: Path to the agent implementation file
- **recent_content_not_truncating**: Number of recent content items to keep full
- **max_consecutive_content_lines**: Maximum lines in consecutive content blocks
- **model_name**: AI model to use for this agent
- **cmd_init_dir**: Initial directory for command execution

### Web Interface Configuration

```yaml
web_interface:
  host: "0.0.0.0"
  port: 5000
  enable_authentication: true
  session_timeout: 3600
  secret_key: "your-secret-key-for-sessions"
```

#### Web Interface Parameters

- **host**: Host address to bind the web server
- **port**: Port number for the web interface
- **enable_authentication**: Whether to require authentication
- **session_timeout**: Session timeout in seconds
- **secret_key**: Secret key for Flask session encryption

### General Configuration

```yaml
general_config:
  recent_content_not_truncating: 5
  max_consecutive_content_lines: 50
  max_char_in_single_content_to_truncate: 10000
```

### Action Defaults Configuration

```yaml
action_defaults:
  shell_cmd_timeout: 300
  cmd_init_dir: "./"
  default_agent_path: "anges/agents/default_agent.py"
  mime_reader_model: "gpt-4-vision-preview"
```

## Configuration Loading

### Basic Usage

```python
from anges.config import load_application_config, config

# Load configuration with defaults
app_config = load_application_config()

# Access configuration values
model_name = app_config.model_api.openai.model
debug_mode = app_config.app.debug_mode

# Use the global config instance
api_key = config.model_api.openai.api_key
```

### Configuration File Locations

1. **Default Configuration**: `anges/configs/default_config.yaml`
2. **Override Configuration**: Specified via `override_config_path` parameter
3. **Environment Override**: Set via `ANGES_CONFIG_OVERRIDE` environment variable

### Environment Variable Overrides

Configuration values can be overridden using environment variables with the `ANGES_` prefix:

```bash
# Override OpenAI API key
export ANGES_MODEL_API_OPENAI_API_KEY="new-api-key"

# Override web interface port
export ANGES_WEB_INTERFACE_PORT=8080

# Override agent timeout
export ANGES_AGENTS_DEFAULT_AGENT_SHELL_CMD_TIMEOUT=600
```

The environment variable naming follows the configuration hierarchy with underscores separating levels.

### Custom Configuration Loading

```python
from anges.config import load_application_config

# Load with custom override file
config = load_application_config(
    override_config_path="/path/to/custom-config.yaml",
    env_prefix="MYAPP_"  # Custom environment prefix
)
```

## Configuration Classes Reference

### Core Configuration Classes

- **ApplicationConfig**: Root configuration class containing all other configs
- **ModelAPIConfig**: Container for all model provider configurations
- **AgentsConfig**: Container for all agent configurations
- **WebInterfaceConfig**: Web interface settings
- **GeneralConfig**: General application settings
- **ActionDefaultsConfig**: Default values for agent actions

### Model Provider Classes

- **OpenAIConfig**: OpenAI API configuration
- **AnthropicConfig**: Anthropic API configuration
- **VertexGeminiConfig**: Google Vertex AI Gemini configuration
- **GenAIGeminiConfig**: Google GenAI Gemini configuration
- **VertexClaudeConfig**: Vertex AI Claude configuration
- **DeepseekConfig**: Deepseek API configuration

### Agent Configuration Classes

- **DefaultAgentConfig**: Default agent settings
- **TaskAnalyzerConfig**: Task analyzer agent settings
- **TaskExecutorConfig**: Task executor agent settings
- **OrchestratorConfig**: Orchestrator agent settings

## Error Handling

The configuration system provides clear error messages for common issues:

### Missing Configuration File
```python
# Raises FileNotFoundError if default_config.yaml is missing
config = load_application_config()
```

### Missing Required Values
```python
# Raises TypeError if required configuration values are missing
config = load_application_config()
```

### Configuration Validation

All configuration classes use dataclasses without default values, ensuring that:
- All required configuration values must be provided
- Type checking is enforced at runtime
- Missing values are caught early during application startup

## Best Practices

### 1. Environment-Specific Configurations

```yaml
# development.yaml
web_interface:
  host: "localhost"
  port: 5000
  enable_authentication: false

# production.yaml
web_interface:
  host: "0.0.0.0"
  port: 80
  enable_authentication: true
```

### 2. Secure API Key Management

```bash
# Use environment variables for sensitive data
export ANGES_MODEL_API_OPENAI_API_KEY="$(cat /secrets/openai-key)"
export ANGES_WEB_INTERFACE_SECRET_KEY="$(openssl rand -hex 32)"
```

### 3. Configuration Validation

```python
# Always handle configuration loading errors
try:
    config = load_application_config()
except (TypeError, FileNotFoundError) as e:
    logger.error(f"Configuration error: {e}")
    sys.exit(1)
```

### 4. Modular Configuration

Organize configuration files by environment or component:

```
configs/
├── default_config.yaml
├── environments/
│   ├── development.yaml
│   ├── staging.yaml
│   └── production.yaml
└── components/
    ├── agents.yaml
    └── models.yaml
```

## Migration and Compatibility

When updating configuration schemas:

1. **Add new fields with defaults** when possible
2. **Provide migration scripts** for breaking changes
3. **Document version compatibility** in changelog
4. **Validate configurations** during application startup

## Troubleshooting

### Common Issues

1. **Configuration file not found**
   - Ensure `default_config.yaml` exists in `anges/configs/`
   - Check file permissions and paths

2. **Missing required values**
   - Review the configuration schema
   - Check environment variable names and values
   - Validate YAML syntax

3. **Type errors**
   - Ensure numeric values are not quoted in YAML
   - Check boolean values use `true`/`false` (lowercase)
   - Validate string values are properly quoted when needed

### Debug Configuration Loading

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug logging for configuration loading
config = load_application_config()
```

This will provide detailed information about configuration loading, including which files are read and which environment variables are applied.