#!/usr/bin/env python3
"""Agent Factory for creating different types of agents.

This module provides a centralized factory for creating agents, supporting both
native agent types and bring-your-own (BYO) agents. It's designed to be used
by both CLI and web interface components.
"""

import logging
import importlib
from enum import Enum
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field

from anges.agents.task_executor import TaskExecutor
from anges.agents.task_analyzer import TaskAnalyzer
from anges.agents.orchestrator import Orchestrator
from anges.agents.default_agent import DefaultAgent
from anges.config import config

class AgentType(Enum):
    """Enum for native agent types available in the system."""
    DEFAULT = "default"
    TASK_EXECUTOR = "task_executor"
    TASK_ANALYZER = "task_analyzer"
    ORCHESTRATOR = "orchestrator"
    
    @classmethod
    def list(cls):
        """Returns list of agent type values for argparse choices."""
        return [e.value for e in cls]

# Alias for backward compatibility
NativeAgentType = AgentType


@dataclass
class AgentConfig:
    """Configuration class for agent creation."""
    # Agent identification
    agent_type: str = NativeAgentType.DEFAULT.value
    
    # Common agent parameters
    cmd_init_dir: str = ""
    prefix_cmd: str = ""
    notes: list = field(default_factory=list)
    interrupt_check: Optional[Callable] = None
    logging_level: int = logging.INFO
    auto_entitle: bool = True
    model: str = "agent_default"  # Default model for inference
    mcp_config: Optional[Dict[str, Any]] = None

    # Web interface specific parameters
    event_stream: Optional[Any] = None
    message_queue: Optional[Any] = None


    # Orchestrator specific parameters
    remaining_recursive_depth: Optional[int] = None
    max_consecutive_actions_to_summarize: Optional[int] = None
    message_handlers: list = field(default_factory=list)
    
    # BYO agent parameters
    custom_module: Optional[str] = None
    custom_class: Optional[str] = None
    
    # Agent-specific configurations
    orchestrator_config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization to set default orchestrator config."""
        if not self.orchestrator_config:
            self.orchestrator_config = {
                'remaining_recursive_depth': 3,
                'max_consecutive_actions_to_summarize': getattr(
                    config.agents.orchestrator, 
                    'max_consecutive_actions_to_summarize', 
                    None
                ) if hasattr(config, 'agents') else None
            }


class AgentFactory:
    """Factory class for creating different types of agents."""
    
    @staticmethod
    def create_agent(config: AgentConfig) -> Any:
        """Create an agent based on the provided configuration.
        
        Args:
            config (AgentConfig): Configuration object containing agent parameters
            
        Returns:
            Agent: Instance of the requested agent type
            
        Raises:
            ValueError: If invalid agent type is provided or BYO agent cannot be created
            ImportError: If custom module cannot be imported
            AttributeError: If custom class cannot be found in module
        """
        # Handle BYO (Bring Your Own) agents
        if config.custom_module and config.custom_class:
            return AgentFactory._create_byo_agent(config)
        
        # Handle native agents
        return AgentFactory._create_native_agent(config)
    
    @staticmethod
    def _create_native_agent(config: AgentConfig) -> Any:
        """Create a native agent based on the agent type."""
        # Validate agent type
        try:
            if config.agent_type not in NativeAgentType.list():
                raise ValueError(f"Invalid agent type: {config.agent_type}. Must be one of {NativeAgentType.list()}")
        except ValueError as e:
            raise e
        
        # Common parameters for all agents
        common_params = {
            'cmd_init_dir': config.cmd_init_dir,
            'prefix_cmd': config.prefix_cmd,
            'interrupt_check': config.interrupt_check,
            'model': config.model,
            'auto_entitle': config.auto_entitle,
            'notes': config.notes,
            'mcp_config': config.mcp_config,
        }
        
        # Add event_stream if provided (for web interface)
        if config.event_stream is not None:
            common_params['event_stream'] = config.event_stream

        common_params['logging_level'] = config.logging_level
        
        # Create the appropriate agent
        if config.agent_type == NativeAgentType.TASK_EXECUTOR.value:
            agent = TaskExecutor(**common_params)
            
        elif config.agent_type == NativeAgentType.TASK_ANALYZER.value:
            agent = TaskAnalyzer(**common_params)
            
        elif config.agent_type == NativeAgentType.ORCHESTRATOR.value:
            # Add orchestrator-specific parameters
            orchestrator_params = common_params.copy()
            if config.orchestrator_config.get('max_consecutive_actions_to_summarize'):
                orchestrator_params['max_consecutive_actions_to_summarize'] = config.orchestrator_config['max_consecutive_actions_to_summarize']
            
            agent = Orchestrator(**orchestrator_params)
            
            # Set orchestrator-specific attributes
            if config.orchestrator_config.get('remaining_recursive_depth'):
                agent.remaining_recursive_depth = config.orchestrator_config['remaining_recursive_depth']
                
        else:  # Default agent
            agent = DefaultAgent(**common_params)
        
        # Add message handlers if provided (for web interface)
        if config.message_handlers and hasattr(agent, 'message_handlers'):
            agent.message_handlers.extend(config.message_handlers)
        
        return agent
    
    @staticmethod
    def _create_byo_agent(config: AgentConfig) -> Any:
        """Create a bring-your-own (BYO) agent from custom module and class."""
        try:
            # Import the custom module
            module = importlib.import_module(config.custom_module)
            
            # Get the custom class
            if not hasattr(module, config.custom_class):
                raise AttributeError(f"Class '{config.custom_class}' not found in module '{config.custom_module}'")
            
            agent_class = getattr(module, config.custom_class)
            
            # Prepare parameters for custom agent
            custom_params = {
                'cmd_init_dir': config.cmd_init_dir,
                'prefix_cmd': config.prefix_cmd,
                'model': config.model,
                'interrupt_check': config.interrupt_check,
                'auto_entitle': config.auto_entitle,
                'notes': config.notes,
                'mcp_config': config.mcp_config,
            }
            
            # Add event_stream if provided
            if config.event_stream is not None:
                custom_params['event_stream'] = config.event_stream
            else:
                custom_params['logging_level'] = config.logging_level
            
            # Create the custom agent
            agent = agent_class(**custom_params)
            
            # Add message handlers if provided and supported
            if config.message_handlers and hasattr(agent, 'message_handlers'):
                agent.message_handlers.extend(config.message_handlers)
            
            return agent
            
        except ImportError as e:
            raise ImportError(f"Failed to import custom module '{config.custom_module}': {e}")
        except Exception as e:
            raise ValueError(f"Failed to create BYO agent: {e}")


# Convenience functions for backward compatibility and ease of use
def create_agent_from_string(agent_type: str, **kwargs) -> Any:
    """Create an agent from a string type with keyword arguments.
    
    This is a convenience function for simple agent creation.
    """
    config = AgentConfig(agent_type=agent_type, **kwargs)
    return AgentFactory.create_agent(config)


def create_byo_agent(module_name: str, class_name: str, **kwargs) -> Any:
    """Create a bring-your-own agent from module and class names.
    
    This is a convenience function for BYO agent creation.
    """
    config = AgentConfig(
        agent_type="custom",
        custom_module=module_name,
        custom_class=class_name,
        **kwargs
    )
    return AgentFactory.create_agent(config)