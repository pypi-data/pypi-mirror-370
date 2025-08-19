"""
Configuration module for Anges.

This module provides application-specific configuration classes and functions
to load configurations from YAML files and environment variables.

Example usage:
    from anges.config import load_application_config, AppConfig
    
    # Load configuration. Requires default_config.yaml or env vars to define ALL values.
    config = load_application_config() 
    
    # Access configuration values
    model_name = config.model_api.openai.model
    debug_mode = config.app.debug_mode # Assuming AppConfig still has debug_mode, or add it if needed.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

from anges.utils.load_configs import Config, load_config


# Define application-specific configuration classes without default values
@dataclass
class OpenAIConfig(Config):
    """Configuration for OpenAI API."""
    model: str
    api_key: str

@dataclass
class AnthropicConfig(Config):
    """Configuration for Anthropic API."""
    model: str
    api_key: str

@dataclass
class VertexGeminiConfig(Config):
    """Configuration for using Gemini from Vertex API. No API key needed, because auth should be handled by `gcloud auth application-default login`."""
    model: str
    gcp_project: str
    gcp_region: str

@dataclass
class VertexClaudeConfig(Config):
    """Claude model served by Vertex AI."""
    model: str
    gcp_project: str
    gcp_region: str

@dataclass
class GenAIGeminiConfig(Config):
    """Google's Gemini API using GenAI."""
    model: str
    api_key: str

@dataclass
class DeepseekConfig(Config):
    """Configuration for Deepseek API."""
    model: str
    api_key: str

@dataclass
class ModelAPIConfig(Config):
    """Model API configuration."""
    openai: OpenAIConfig
    anthropic: AnthropicConfig
    gemini: VertexGeminiConfig
    genai_gemini: GenAIGeminiConfig
    vertex_claude: VertexClaudeConfig
    deepseek: DeepseekConfig

@dataclass
class DefaultAgentConfig(Config):
    """Configuration for agent execution."""
    shell_cmd_timeout: int
    max_number_of_events_to_exhaust: int
    max_consecutive_actions_to_summarize: int
    default_agent_path: str
    recent_content_not_truncating: int
    max_consecutive_content_lines: int
    model_name: str
    cmd_init_dir: str

@dataclass
class ActionDefaultsConfig(Config):
    """ActionDefaultsConfiguration for agent execution."""
    shell_cmd_timeout: int
    cmd_init_dir: str
    default_agent_path: str
    mime_reader_model: str

@dataclass
class TaskAnalyzerConfig(Config):
    """Configuration for agent execution."""
    shell_cmd_timeout: int
    max_number_of_events_to_exhaust: int
    max_consecutive_actions_to_summarize: int
    default_agent_path: str
    recent_content_not_truncating: int
    max_consecutive_content_lines: int
    model_name: str
    cmd_init_dir: str

@dataclass
class TaskExecutorConfig(Config):
    """Configuration for agent execution."""
    shell_cmd_timeout: int
    max_number_of_events_to_exhaust: int
    max_consecutive_actions_to_summarize: int
    default_agent_path: str
    recent_content_not_truncating: int
    max_consecutive_content_lines: int
    model_name: str
    cmd_init_dir: str

@dataclass
class OrchestratorConfig(Config):
    """Configuration for agent execution."""
    shell_cmd_timeout: int
    max_number_of_events_to_exhaust: int
    max_consecutive_actions_to_summarize: int
    default_agent_path: str
    recent_content_not_truncating: int
    max_consecutive_content_lines: int
    model_name: str
    cmd_init_dir: str


@dataclass
class AgentsConfig(Config):
    """Configuration for all agents."""
    default_agent: DefaultAgentConfig
    task_analyzer: TaskAnalyzerConfig
    task_executor: TaskExecutorConfig
    orchestrator: OrchestratorConfig

@dataclass
class WebInterfaceConfig(Config):
    """Configuration for the web interface."""
    host: str
    port: int
    enable_authentication: bool
    session_timeout: int
    secret_key: str # Secret key for Flask sessions

@dataclass
class AppConfig(Config):
    """Application configuration."""
    name: str
    version: str
    debug_mode: bool 


@dataclass
class GeneralConfig(Config):
    """General configuration."""
    recent_content_not_truncating: int
    max_consecutive_content_lines: int
    max_char_in_single_content_to_truncate: int

@dataclass
class ApplicationConfig(Config):
    """Main application configuration."""
    model_api: ModelAPIConfig
    agents: AgentsConfig
    web_interface: WebInterfaceConfig
    general_config: GeneralConfig
    action_defaults: ActionDefaultsConfig

def load_application_config(
    override_config_path: Optional[str] = None,
) -> ApplicationConfig:
    """
    Load the application configuration from YAML files and environment variables.

    Args:
        override_config_path: Optional path to an override configuration YAML file
        env_prefix: Prefix for environment variables to override config values

    Returns:
        An ApplicationConfig instance containing the configuration

    Raises:
        TypeError: If any configuration value is missing during instantiation,
                   as all fields are now required.
        FileNotFoundError: If default_config_path does not exist.
        # Other errors depending on the implementation of load_config
    """
    # Determine the default config path
    default_config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "configs",
        "default_config.yaml"
    )

    # Check if the default config file exists, as it's now crucial
    if not os.path.exists(default_config_path):
        # Or handle this more gracefully depending on requirements
        raise FileNotFoundError(f"Default configuration file not found: {default_config_path}. "
                                "It's required as dataclasses have no default values.")

    # Load the configuration - this function MUST provide values for ALL fields.
    # The actual implementation of load_config needs to handle this.
    return load_config(
        default_config_path=default_config_path,
        override_config_path=override_config_path,
        config_class=ApplicationConfig
    )


try:
    config_override = os.environ.get("ANGES_CONFIG_OVERRIDE")
    if config_override:
        config_override = os.path.expanduser(config_override)
    else:
        config_override = os.path.expanduser("~/.anges/config.yaml")
    config = load_application_config(override_config_path=config_override)
except (TypeError, FileNotFoundError) as e:
    print(f"Error loading application configuration: {e}")
    # Decide how to proceed: exit, use hardcoded fallbacks (defeats the purpose), etc.
    config = None # Or some other indicator that loading failed