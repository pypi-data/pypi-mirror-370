**Language**: [English](architecture.md) | [中文](zh/architecture.md)

---
# Anges Architecture Documentation

## Overview

This document provides detailed technical documentation for the core architectural components of the Anges project, an AI agent framework designed for multi-step task execution in Linux environments.

## Table of Contents

- [Event Loop System](#event-loop-system)
- [Action System Architecture](#action-system-architecture)
- [Prompt Construction](#prompt-construction)
- [System Integration](#system-integration)
- [Design Patterns](#design-patterns)
- [Extension Points](#extension-points)

## Event Loop System

The Event Loop System is the core orchestration mechanism that manages the lifecycle of agent interactions, from user input to task completion.

### Event Architecture

#### Event Class Structure

The `Event` class (defined in `anges/agents/agent_utils/events.py`) serves as the fundamental unit of interaction tracking:

```python
class Event:
    def __init__(self, type, reasoning="", content="", analysis="", message="", 
                 est_input_token=0, est_output_token=0):
        self.id = generate_random_id()
        self.type = type  # Event type identifier
        self.reasoning = reasoning  # Agent's reasoning for the action
        self.content = content  # Action output or user input
        self.analysis = analysis  # Internal analysis (not shown to user)
        self.message = message  # User-visible message
        self.timestamp = datetime.now().isoformat()
        self.est_input_token = est_input_token
        self.est_output_token = est_output_token
```

#### Event Types

The system defines several critical event types that control agent behavior:

- **`new_request`**: Initial user input that starts a new task
- **`action`**: Agent-executed shell commands and their results
- **`edit_file`**: File modification operations
- **`task_completion`**: Successful task completion with summary
- **`agent_requested_help`**: Agent requests human intervention
## BaseAgent Class Architecture

The `BaseAgent` class serves as the foundation for all agent implementations in the Anges framework. It provides core functionality for event handling, action execution, and task management.

### Class Definition

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

### Key Properties

- **parent_ids**: List of parent event stream UIDs for hierarchical agent relationships
- **event_stream**: EventStream instance for managing execution history
- **inference_func**: Function used for LLM inference calls
- **cmd_init_dir**: Initial directory for command execution
- **prefix_cmd**: Command prefix for shell operations
- **interrupt_check**: Function to check for user interruption requests
- **status**: Current agent status ("new", "running", "completed", etc.)
- **uid**: Unique identifier (inherited from event_stream.uid)
- **max_consecutive_actions_to_summarize**: Threshold for event summarization
- **message_handlers**: List of functions for handling user-visible messages
- **agent_prompt_template**: Template for constructing agent prompts
- **auto_entitle**: Whether to automatically generate conversation titles
- **agent_config**: Configuration object for agent behavior
- **registered_actions**: List of available action types

### Core Methods

#### `handle_user_visible_messages(message: str)`
Handles user-visible messages by calling all registered message handlers. Provides direct messaging to frontend interfaces.

#### `run_with_new_request(task_description, event_stream=None)`
Main execution method that:
1. Adds a new request event to the event stream
2. Enters the main execution loop
3. Checks for interruptions and exhaustion conditions
4. Predicts and handles next actions
5. Returns the final event stream

#### `_build_run_config(task_description, event_stream)`
Constructs the runtime configuration dictionary containing all necessary context for action execution.

#### `_handle_received_new_request(run_config)`
Processes new task requests and adds appropriate events to the stream. Handles auto-titling if enabled.

#### `_check_interruption(run_config)`
Checks for user interruption requests and handles graceful task termination.

#### `_check_exhausted(run_config)`
Monitors event count limits and prevents infinite execution loops.

#### `_prompt_and_get_action_from_response(event_stream)`
Constructs prompts from event history and parses LLM responses into actionable commands.

#### `_prefict_next_event_and_handle_actions(event_stream, run_config)`
Executes predicted actions and manages the action execution flow.

### Agent Lifecycle

1. **Initialization**: Agent is created with configuration parameters
2. **Request Handling**: New task request is received and processed
3. **Execution Loop**: Agent continuously predicts and executes actions
4. **Interruption Checking**: Regular checks for user interruption or exhaustion
5. **Action Execution**: Individual actions are executed based on LLM predictions
6. **Completion**: Task completes with final event stream state

### Event Stream Integration

The BaseAgent is tightly integrated with the EventStream system:
- All actions generate events that are added to the stream
- Event summaries are created when consecutive action limits are reached
- Parent-child relationships are maintained through event stream UIDs
- Event persistence is handled automatically through save operations

All actions inherit from the base `Action` class (defined in `anges/agents/agent_utils/agent_actions.py`):

```python
class Action:
    def __init__(self):
        self.type = ""  # Unique action identifier
        self.guide_prompt = ""  # Documentation for the agent
        self.user_visible = False  # Whether action results are shown to user
        self.unique_action = False  # Whether action must be used alone
        self.returning_action = False  # Whether action terminates the loop

    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        raise NotImplementedError("Subclasses must implement this method")
```
### Action System Architecture

The Action System provides a modular, extensible framework for agent capabilities through a class-based architecture.

### Action Base Class

All actions inherit from the base `Action` class (defined in `anges/agents/agent_utils/agent_actions.py`):

```python
class Action:
    def __init__(self):
        self.type = ""  # Unique action identifier
        self.guide_prompt = ""  # Documentation for the agent
        self.user_visible = False  # Whether action results are shown to user
        self.unique_action = False  # Whether action must be used alone
        self.returning_action = False  # Whether action terminates execution

    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        raise NotImplementedError("Subclasses must implement this method")
```

### Available Actions

#### TASK_COMPLETE
- **Type**: `TASK_COMPLETE`
- **User Visible**: Yes
- **Unique Action**: Yes (must be used alone)
- **Returning Action**: Yes (terminates execution)
- **Purpose**: Signals successful task completion with summary
- **Event Type Created**: `task_completion`

#### RUN_SHELL_CMD
- **Type**: `RUN_SHELL_CMD`
- **User Visible**: No
- **Unique Action**: No
- **Returning Action**: No
- **Purpose**: Executes shell commands in the system
- **Event Type Created**: `action`
- **Special Features**: Supports background execution and timeout configuration

#### HELP_NEEDED
- **Type**: `HELP_NEEDED`
- **User Visible**: Yes
- **Unique Action**: Yes (must be used alone)
- **Returning Action**: Yes (terminates execution)
- **Purpose**: Requests human intervention when agent is stuck
- **Event Type Created**: `agent_requested_help`

#### AGENT_TEXT_RESPONSE
- **Type**: `AGENT_TEXT_RESPONSE`
- **User Visible**: Yes
- **Unique Action**: Yes (must be used alone)
- **Returning Action**: Yes (terminates execution)
- **Purpose**: Provides informational responses to user questions
- **Event Type Created**: `agent_text_response`

#### EDIT_FILE
- **Type**: `EDIT_FILE`
- **User Visible**: No
- **Unique Action**: No
- **Returning Action**: No
- **Purpose**: Creates, modifies, or deletes file content
- **Event Type Created**: `edit_file`
- **Operations**: NEW_FILE, INSERT_LINES, REMOVE_LINES, REPLACE_LINES

#### READ_MIME_FILES
- **Type**: `READ_MIME_FILES`
- **User Visible**: No
- **Unique Action**: No
- **Returning Action**: No
- **Purpose**: Analyzes content of files (images, PDFs) and YouTube links using multimodal AI
- **Event Type Created**: `READ_MIME_FILES`
- **Supported Formats**: Images, PDFs, YouTube videos
- **Features**: Optional output file saving, multimodal content analysis

### Action Execution Flow

1. **Action Prediction**: Agent LLM predicts next actions based on event history
2. **Action Validation**: Response is parsed and validated against available actions
3. **Action Execution**: Each action's `handle_action_in_parsed_response` method is called
4. **Event Creation**: Actions create appropriate events and add them to the event stream
5. **Stream Persistence**: Event stream is saved after action execution
6. **Termination Check**: Returning actions cause the execution loop to exit

### Action Registration

Actions are registered with agents through the `registered_actions` property. Each agent maintains a list of available actions that can be dynamically configured.

### Event System Documentation

#### Complete Event Types

The system supports the following event types:

- **`new_request`**: Initial user input that starts a new task
- **`follow_up_request`**: Additional user input in an existing conversation
- **`action`**: Agent-executed shell commands and their results
- **`edit_file`**: File modification operations
- **`READ_MIME_FILES`**: Multimodal file analysis operations
- **`task_completion`**: Successful task completion with summary
- **`agent_requested_help`**: Agent requests human intervention
- **`agent_text_response`**: Agent provides informational responses
- **`task_interrupted`**: Task termination due to errors, interruption, or exhaustion
- **`child_agent_running`**: Child agent execution tracking
- **`new_request_from_parent`**: Request received from parent agent
- **`follow_up_request_from_parent`**: Follow-up request from parent agent

#### Event Class Structure

```python
class Event:
    def __init__(self, type, reasoning="", content="", title=None, message="", analysis="", est_input_token=0, est_output_token=0):
        self.type = type  # Required: Event type identifier
        self.reasoning = reasoning  # Required: Agent's reasoning for this action
        self.content = content  # Action-specific content
        self.title = title  # Optional event title
        self.message = message  # Required: User-visible message
        self.analysis = analysis  # Internal analysis (not shown to user)
        self.est_input_token = est_input_token  # Token usage tracking
        self.est_output_token = est_output_token  # Token usage tracking
        self.created_at = datetime.now()  # Timestamp
```

#### EventStream Class Structure

```python
class EventStream:
    def __init__(self, title=None, uid=None, parent_event_stream_uids=None, agent_type=""):
        self.events_list = []  # Chronological list of events
        self.event_summaries_list = []  # Summarized event groups
        self.created_at = datetime.now()
        self.uid = uid or generate_random_id()  # Unique identifier
        self.title = title or self.uid  # Human-readable title
        self.parent_event_stream_uids = parent_event_stream_uids or []  # Parent relationships
        self.agent_type = agent_type  # Type of agent that created this stream
        self.agent_settings = {}  # Agent configuration settings
```

#### Key EventStream Methods

- **`add_event(event)`**: Adds a new event to the stream
- **`get_event_list_including_children_events(starting_from=0)`**: Retrieves flattened event list including child agent events
- **`update_settings(settings)`**: Updates agent configuration settings
- **`get_settings()`**: Returns current agent settings
- **`to_dict()`** / **`from_dict()`**: Serialization methods for persistence

#### Return-to-Parent Event Types

Certain event types cause child agents to return control to their parent:

```python
RETURN_TO_PARENT_EVENT_TYPES = [
    "task_interrupted", 
    "task_completion", 
    "agent_requested_help", 
    "agent_text_response"
]
```

These events signal that a child agent has completed its execution and control should return to the parent agent.
#### Returning Actions
Actions marked as `returning_action=True` terminate the agent loop:
- All unique actions are returning actions
- These actions represent completion states or user interaction points

## Prompt Construction

The Prompt Construction system dynamically builds context-aware prompts that guide agent behavior and provide necessary information for decision-making.

### Prompt Template Architecture

#### Base Template Structure

The core prompt template is defined in `anges/prompt_templates/common_prompts.py`:

```python
DEFAULT_AGENT_PROMPT_TEMPLATE = r"""
# INSTRUCTION
You are the best AI agent. You are running in a Linux environment with some options of actions.

You will be given a list of Events, which contains the previous interaction between you and the user.

Your overall goal is to do multi step actions and help the user to fulfill their requests or answer their questions.

## Response Format Rules
You need to respond in a *JSON* format with the following keys:
- `analysis`: Internal chain-of-thought thinking
- `action`: List of actions to take as the next step
- `reasoning`: User-visible explanation of actions

## Available Action Tags
PLACEHOLDER_ACTION_INSTRUCTIONS

######### FOLLOWING IS THE ACTUAL REQUEST #########
# EVENT STREAM
PLACEHOLDER_EVENT_STREAM

# Next Step
<Now output the next step action in JSON. Do not include ``` quotes. Your whole response needs to be JSON parsable.>
"""
```

#### Template Placeholders

The system uses two key placeholders that are dynamically replaced:

1. **`PLACEHOLDER_ACTION_INSTRUCTIONS`**: Replaced with concatenated `guide_prompt` content from all available actions
2. **`PLACEHOLDER_EVENT_STREAM`**: Replaced with the formatted event stream providing context

### Dynamic Content Injection

#### Action Instructions Generation

Action instructions are dynamically generated by concatenating the `guide_prompt` field from each registered action:

```python
def generate_action_instructions(action_registry):
    instructions = []
    for action_name, action_obj in action_registry.items():
        instructions.append(action_obj.guide_prompt)
    return "\n\n".join(instructions)
```

This provides the agent with:
- Complete action documentation
- Usage examples
- Parameter specifications
- Constraint information

#### Event Stream Formatting

The event stream is formatted using `construct_event_stream_for_agent()` which:

1. **Processes Event History**: Converts events into human-readable format
2. **Applies Summarization**: Condenses long event sequences
3. **Maintains Context**: Preserves critical information for decision-making
4. **Formats Output**: Creates structured text representation

Example formatted event stream:
```
## Event 1 TYPE: NEW_REQUEST
CONTENT:
User wants to analyze a log file and create a summary report.

## Event 2 TYPE: ACTION
REASONING:
I need to first examine the log file to understand its structure.
CONTENT:
******
- COMMAND_EXECUTED: ls -la /var/log/
- EXIT_CODE: 0
- STDOUT: [log file listing]
******
```

### Prompt Assembly Process

#### 1. Template Loading
The base template is loaded from the prompt templates module.

#### 2. Action Instructions Injection
All available actions' guide prompts are concatenated and injected into the `PLACEHOLDER_ACTION_INSTRUCTIONS` location.

#### 3. Event Stream Construction
The current event stream is processed and formatted, then injected into the `PLACEHOLDER_EVENT_STREAM` location.

#### 4. Final Prompt Generation
The complete prompt is assembled with:
- System instructions
- Response format requirements
- Available actions documentation
- Current context (event stream)
- Execution directive

### Context Management

#### Token Optimization
The system manages prompt length through:
- **Event Summarization**: Older events are summarized to reduce token count
- **Content Truncation**: Long command outputs are truncated with "..." indicators
- **Selective Inclusion**: Only relevant events are included in the context

#### Context Continuity
Despite summarization, the system maintains:
- **Task Continuity**: Current task objectives remain clear
- **State Awareness**: Agent understands current system state
- **Error Context**: Recent errors and their resolution attempts
- **Progress Tracking**: Understanding of completed vs. remaining work

### Specialized Prompt Templates

The system includes specialized templates for different scenarios:

#### Orchestrator Prompts
(`anges/prompt_templates/orchestrator_prompts.py`)
- Multi-agent coordination
- Task delegation
- Resource management

#### Task Analyzer Prompts
(`anges/prompt_templates/task_analyzer_prompts.py`)
- Task decomposition
- Complexity assessment
- Approach planning

## System Integration

The three core systems work together to create a cohesive agent framework:

### Integration Flow

1. **Prompt Construction** creates context-aware prompts using current event stream
2. **Agent Processing** generates responses with actions based on the prompt
3. **Action System** executes the specified actions and creates new events
4. **Event Loop** manages the cycle and determines continuation or termination

### Configuration Management

The `run_config` dictionary provides system-wide configuration:

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

## Design Patterns

### Strategy Pattern
The Action System uses the Strategy pattern, allowing different action implementations while maintaining a consistent interface.

### Observer Pattern
Event generation follows the Observer pattern, with multiple components reacting to event creation.

### Template Method Pattern
Prompt construction uses the Template Method pattern, with fixed structure and variable content injection.

### Factory Pattern
Action registration and discovery follows the Factory pattern for extensible action management.

## Extension Points

### Adding New Actions

1. **Create Action Class**: Inherit from `Action` base class
2. **Implement Handler**: Define `handle_action_in_parsed_response()` method
3. **Set Properties**: Configure `user_visible`, `unique_action`, `returning_action`
4. **Write Guide Prompt**: Provide comprehensive documentation
5. **Register Action**: Add to action registry

### Custom Event Types

1. **Define Event Type**: Add new type to event type constants
2. **Update Processing**: Modify event stream construction if needed
3. **Handle Termination**: Add to `RETURN_TO_PARENT_EVENT_TYPES` if terminal

### Prompt Template Customization

1. **Create Template**: Define new template with placeholders
2. **Implement Injection**: Create content injection logic
3. **Register Template**: Make available to agent configuration

This architecture provides a robust, extensible foundation for AI agent development with clear separation of concerns and well-defined integration points.
