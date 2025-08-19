**Language**: [English](api-reference.md) | [中文](zh/api-reference.md)

---
# Anges API Reference

## Overview

This document provides comprehensive API reference documentation for the Anges project core classes and their usage patterns. Anges is an AI agent framework that enables autonomous task execution through event-driven architecture.

## Table of Contents

- [Core Classes](#core-classes)
  - [BaseAgent](#baseagent)
  - [Action](#action)
  - [Event](#event)
  - [EventStream](#eventstream)
  - [Configuration](#configuration)
- [Usage Examples](#usage-examples)
  - [Basic Agent Setup](#basic-agent-setup)
  - [Event Handling](#event-handling)
  - [Custom Action Creation](#custom-action-creation)

## Core Classes

### BaseAgent

The `BaseAgent` class is the foundation for all AI agents in the Anges framework. It provides the core functionality for processing events, executing actions, and managing agent lifecycle.

#### Class Definition

```python
from anges.agents.agent_utils.base_agent import BaseAgent
```

#### Key Methods

- **`__init__(self, agent_config, logger=None)`**: Initialize the agent with configuration and optional logger
- **`run_agent_iteration(self, event_stream, inference_func, message_handler_func, **kwargs)`**: Execute a single agent iteration
- **`process_events(self, event_stream)`**: Process events in the event stream
- **`execute_actions(self, actions, run_config)`**: Execute a list of actions with the given configuration

#### Properties

- **`agent_config`**: Configuration object for the agent
- **`logger`**: Logger instance for debugging and monitoring
- **`available_actions`**: Dictionary of available action types

#### Usage Example

```python
from anges.agents.agent_utils.base_agent import BaseAgent
from anges.config import load_application_config
import logging

# Load configuration
config = load_application_config()

# Create logger
logger = logging.getLogger(__name__)

# Initialize agent
agent = BaseAgent(agent_config=config.agent, logger=logger)

# Run agent iteration
result = agent.run_agent_iteration(
    event_stream=event_stream,
    inference_func=inference_function,
    message_handler_func=message_handler
)
```

### Action

The `Action` class is the base class for all actions that agents can execute. Actions represent atomic operations like running shell commands, editing files, or completing tasks.

#### Class Definition

```python
from anges.agents.agent_utils.agent_actions import Action
```

#### Base Properties

- **`type`**: String identifier for the action type
- **`guide_prompt`**: Instruction text for the AI model
- **`user_visible`**: Boolean indicating if action results are shown to users
- **`unique_action`**: Boolean indicating if action must be used alone
- **`returning_action`**: Boolean indicating if action terminates the agent turn

#### Base Methods

- **`handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json)`**: Process and execute the action

#### Available Action Types

1. **TaskCompleteAction** (`TASK_COMPLETE`)
   - User visible, unique action
   - Used to signal task completion
   
2. **RunShellCMDAction** (`RUN_SHELL_CMD`)
   - Non-visible action
   - Execute shell commands
   
3. **EditFileAction** (`EDIT_FILE`)
   - Non-visible action
   - Create, modify, or delete files
   
4. **AgentHelpNeededAction** (`HELP_NEEDED`)
   - User visible, unique action
   - Request human assistance
   
5. **AgentTextResponseAction** (`AGENT_TEXT_RESPONSE`)
   - User visible, unique action
   - Provide formatted text responses
   
6. **ReadMIMEFilesAction** (`READ_MIME_FILES`)
   - Non-visible action
   - Analyze multimedia files and content

#### Usage Example

```python
from anges.agents.agent_utils.agent_actions import RunShellCMDAction

# Create action instance
shell_action = RunShellCMDAction()

# Action configuration
action_json = {
    "action_type": "RUN_SHELL_CMD",
    "command": "ls -la",
    "shell_cmd_timeout": 30
}

# Execute action
result = shell_action.handle_action_in_parsed_response(
    run_config=run_config,
    parsed_response_dict=response_dict,
    action_json=action_json
)
```

### Event

The `Event` class represents individual occurrences in the agent's execution timeline. Events capture actions, responses, and state changes.

#### Class Definition

```python
from anges.agents.agent_utils.events import Event
```

#### Constructor

```python
Event(
    type: str,
    reasoning: str = "",
    content: str = "",
    analysis: str = "",
    message: str = "",
    est_input_token: int = 0,
    est_output_token: int = 0,
    timestamp: str = None,
    event_id: str = None
)
```

#### Properties

- **`type`**: Event type (e.g., "action", "task_completion", "user_input")
- **`reasoning`**: Explanation of why the event occurred
- **`content`**: Main content or result of the event
- **`analysis`**: Additional analysis or context
- **`message`**: Human-readable message
- **`est_input_token`**: Estimated input tokens used
- **`est_output_token`**: Estimated output tokens generated
- **`timestamp`**: ISO format timestamp
- **`event_id`**: Unique identifier for the event

#### Methods

- **`to_dict(self)`**: Convert event to dictionary representation
- **`from_dict(cls, data)`**: Create event from dictionary (class method)

#### Usage Example

```python
from anges.agents.agent_utils.events import Event
from datetime import datetime

# Create a new event
event = Event(
    type="action",
    reasoning="Need to check current directory contents",
    content="Command executed: ls -la\nOutput: total 24\n...",
    message="Agent executed shell command",
    est_input_token=50,
    est_output_token=20
)

# Convert to dictionary
event_dict = event.to_dict()

# Create from dictionary
new_event = Event.from_dict(event_dict)
```

### EventStream

The `EventStream` class manages a sequence of events, providing methods for event manipulation, persistence, and analysis.

#### Class Definition

```python
from anges.agents.agent_utils.events import EventStream
```

#### Constructor

```python
EventStream(
    events_list: List[Event] = None,
    stream_id: str = None,
    metadata: dict = None
)
```

#### Properties

- **`events_list`**: List of Event objects
- **`stream_id`**: Unique identifier for the stream
- **`metadata`**: Additional metadata dictionary

#### Methods

- **`add_event(self, event)`**: Add an event to the stream
- **`get_events_by_type(self, event_type)`**: Filter events by type
- **`get_latest_event(self)`**: Get the most recent event
- **`to_dict(self)`**: Convert stream to dictionary
- **`from_dict(cls, data)`**: Create stream from dictionary (class method)
- **`save_to_file(self, filepath)`**: Save stream to file
- **`load_from_file(cls, filepath)`**: Load stream from file (class method)

#### Usage Example

```python
from anges.agents.agent_utils.events import EventStream, Event

# Create event stream
stream = EventStream()

# Add events
user_event = Event(
    type="user_input",
    content="Please list the files in the current directory",
    message="User requested file listing"
)
stream.add_event(user_event)

action_event = Event(
    type="action",
    reasoning="Executing ls command to list files",
    content="ls -la executed successfully"
)
stream.add_event(action_event)

# Get events by type
user_events = stream.get_events_by_type("user_input")

# Get latest event
latest = stream.get_latest_event()

# Save to file
stream.save_to_file("agent_session.json")

# Load from file
loaded_stream = EventStream.load_from_file("agent_session.json")
```

### Configuration

The configuration system provides structured access to application settings, API keys, and agent parameters.

#### Class Definition

```python
from anges.config import load_application_config, AppConfig
```

#### Configuration Classes

1. **OpenAIConfig**: OpenAI API configuration
   - `model`: Model name (e.g., "gpt-4")
   - `api_key`: API key for authentication

2. **AnthropicConfig**: Anthropic API configuration
   - `model`: Model name (e.g., "claude-3-sonnet")
   - `api_key`: API key for authentication

3. **VertexGeminiConfig**: Google Vertex AI Gemini configuration
   - `model`: Model name
   - `gcp_project`: GCP project ID
   - `gcp_region`: GCP region

4. **AgentConfig**: Agent-specific configuration
   - `shell_cmd_timeout`: Default timeout for shell commands
   - `max_iterations`: Maximum agent iterations
   - `debug_mode`: Enable debug logging

#### Usage Example

```python
from anges.config import load_application_config
import os

# Set environment variables (or use config file)
os.environ['OPENAI_API_KEY'] = 'your-api-key'
os.environ['OPENAI_MODEL'] = 'gpt-4'

# Load configuration
config = load_application_config()

# Access configuration values
model_name = config.model_api.openai.model
api_key = config.model_api.openai.api_key
agent_timeout = config.agent.shell_cmd_timeout

# Use in agent initialization
from anges.agents.agent_utils.base_agent import BaseAgent
agent = BaseAgent(agent_config=config.agent)
```

## Usage Examples

### Basic Agent Setup

```python
from anges.agents.agent_utils.base_agent import BaseAgent
from anges.agents.agent_utils.events import EventStream, Event
from anges.config import load_application_config
from anges.utils.inference_api import get_inference_function
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = load_application_config()

# Create inference function
inference_func = get_inference_function(config.model_api)

# Initialize agent
agent = BaseAgent(agent_config=config.agent, logger=logger)

# Create event stream with initial user input
event_stream = EventStream()
user_event = Event(
    type="user_input",
    content="Please create a simple Python script that prints 'Hello, World!'",
    message="User requested script creation"
)
event_stream.add_event(user_event)

# Define message handler
def message_handler(message):
    print(f"Agent: {message}")

# Run agent iteration
result = agent.run_agent_iteration(
    event_stream=event_stream,
    inference_func=inference_func,
    message_handler_func=message_handler,
    cmd_init_dir="./workspace",
    prefix_cmd=""
)
```

### Event Handling

```python
from anges.agents.agent_utils.events import EventStream, Event

# Create event stream
stream = EventStream()

# Add various event types
events = [
    Event(type="user_input", content="Start the web server"),
    Event(type="action", content="python -m http.server 8000", reasoning="Starting HTTP server"),
    Event(type="task_completion", content="Web server started successfully")
]

for event in events:
    stream.add_event(event)

# Process events by type
user_inputs = stream.get_events_by_type("user_input")
actions = stream.get_events_by_type("action")
completions = stream.get_events_by_type("task_completion")

print(f"Found {len(user_inputs)} user inputs")
print(f"Found {len(actions)} actions")
print(f"Found {len(completions)} completions")

# Get execution summary
latest_event = stream.get_latest_event()
print(f"Latest event: {latest_event.type} - {latest_event.content}")
```

### Custom Action Creation

```python
from anges.agents.agent_utils.agent_actions import Action
from anges.agents.agent_utils.events import Event

class CustomDatabaseAction(Action):
    def __init__(self):
        super().__init__()
        self.type = "QUERY_DATABASE"
        self.user_visible = False
        self.unique_action = False
        self.returning_action = False
        self.guide_prompt = """
### QUERY_DATABASE:
**non-visible action**
Execute a database query and return results.

Required fields:
- `action_type`: Must be "QUERY_DATABASE"
- `query`: SQL query to execute
- `database`: Database name

Example:
{
    "action_type": "QUERY_DATABASE",
    "query": "SELECT * FROM users WHERE active = 1",
    "database": "production"
}
"""
    
    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        query = action_json.get("query", "")
        database = action_json.get("database", "default")
        reasoning = parsed_response_dict.get("reasoning", "")
        
        # Simulate database execution
        try:
            # Your database logic here
            result = f"Query executed on {database}: {query}"
            
            # Create event
            event = Event(
                type="database_query",
                reasoning=reasoning,
                content=result,
                message=f"Database query executed: {query[:50]}..."
            )
            
            # Add to event stream
            event_stream = run_config["event_stream"]
            event_stream.add_event(event)
            
            return result
            
        except Exception as e:
            error_event = Event(
                type="error",
                reasoning=reasoning,
                content=f"Database error: {str(e)}",
                message="Database query failed"
            )
            event_stream = run_config["event_stream"]
            event_stream.add_event(error_event)
            return None

# Register custom action with agent
custom_action = CustomDatabaseAction()
# Add to agent's available actions dictionary
```

This API reference provides the foundation for building and extending Anges agents. Each class is designed to work together in the event-driven architecture, enabling powerful autonomous agent capabilities.
*Note: This is a framework document. Detailed API documentation will be generated and added in subsequent documentation phases. For complete examples, see the `/docs/examples/` directory.*