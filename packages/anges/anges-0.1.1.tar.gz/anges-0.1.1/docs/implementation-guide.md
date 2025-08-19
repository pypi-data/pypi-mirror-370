**Language**: [English](implementation-guide.md) | [中文](zh/implementation-guide.md)

---
# Anges Implementation Guide

## Overview

This guide provides step-by-step instructions for extending the Anges framework with custom functionality. You'll learn how to create custom agents and actions to meet your specific requirements.

## Table of Contents

- [Creating Custom Agents](#creating-custom-agents)
- [Creating Custom Actions](#creating-custom-actions)
- [Best Practices](#best-practices)
- [Common Pitfalls](#common-pitfalls)
- [Advanced Patterns](#advanced-patterns)

## Creating Custom Agents

### Overview

Custom agents in Anges extend the `BaseAgent` class to provide specialized functionality for specific domains or use cases. This section will guide you through creating a custom agent step by step.

### Step 1: Understanding BaseAgent

Before creating a custom agent, it's important to understand the `BaseAgent` class structure and the correct import statements:

```python
from anges.agents.agent_utils.base_agent import BaseAgent
from anges.agents.agent_utils.agent_actions import Action
from anges.agents.agent_utils.events import Event, EventStream
from anges.config import config
import logging
```

The `BaseAgent` provides:
- Core agent lifecycle management
- Event handling and processing
- Action registration and execution
- Prompt template management
- Communication with the inference API

### Step 2: Basic Custom Agent Structure

Here's the minimal structure for a custom agent:

```python
#!/usr/bin/env python3
"""
Custom Agent Implementation
"""

import logging
from anges.agents.agent_utils.base_agent import BaseAgent
from anges.agents.agent_utils.agent_actions import Action
from anges.agents.agent_utils.events import Event, EventStream

class MyCustomAgent(BaseAgent):
    """
    A custom agent for specific domain tasks.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set custom agent prompt template
        self.agent_prompt_template = """
You are a specialized custom agent. Your role is to help users with specific domain tasks.

# Available Actions
{available_actions}

# Instructions
- Analyze the user's request carefully
- Use appropriate actions to fulfill the request
- Provide clear reasoning for your actions
"""
        
        # Initialize any custom attributes
        self.domain_specific_data = {}
        
    def get_custom_actions(self):
        """
        Override this method to add custom actions to your agent.
        """
        return []  # Return list of custom Action instances
```

### Step 3: Implementing Custom Functionality

Let's create a practical example - a `CodeAnalyzerAgent` that specializes in code analysis:

```python
class CodeAnalyzerAgent(BaseAgent):
    """
    A custom agent specialized for code analysis tasks.
    This agent has enhanced capabilities for analyzing Python code,
    detecting patterns, and providing code quality feedback.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set specialized prompt template for code analysis
        self.agent_prompt_template = """
You are a specialized code analysis agent. Your expertise includes:
- Python code quality assessment
- Security vulnerability detection
- Performance optimization suggestions
- Code structure analysis

# Available Actions
{available_actions}

# Code Analysis Guidelines
- Always read files before analyzing
- Provide specific, actionable feedback
- Consider security, performance, and maintainability
- Use shell commands for additional analysis tools when needed
"""
        
        # Initialize code analysis specific attributes
        self.analysis_results = []
        self.code_metrics = {}
        
    def get_custom_actions(self):
        """
        Add custom actions specific to code analysis.
        """
        return [
            CodeQualityCheckAction(),
            SecurityScanAction(),
            PerformanceAnalysisAction()
        ]
```

### Step 4: Custom Agent Usage

Once you've created your custom agent, you can use it in your applications:

```python
# Initialize your custom agent
code_analyzer = CodeAnalyzerAgent(
    model_name="gpt-4",
    temperature=0.1,
    max_tokens=2000
)

# Use the agent to analyze code
result = code_analyzer.run(
    user_input="Please analyze the Python files in the ./src directory for code quality issues"
)
```

## Creating Custom Actions

Custom actions extend the capabilities of your agents by providing new functionalities. The Anges framework uses a base `Action` class that you can inherit from to create specialized actions.

### Step 1: Understanding the Action Base Class

All actions in Anges inherit from the base `Action` class:

```python
from anges.agents.agent_utils.agent_actions import Action
from anges.agents.agent_utils.events import Event

class CustomAction(Action):
    def __init__(self):
        super().__init__()
        self.type = "CUSTOM_ACTION"
        self.description = "Description of what this action does"
        
    def execute(self, action_data, event_stream, agent_instance):
        """
        Execute the custom action.
        
        Args:
            action_data: Dictionary containing action parameters
            event_stream: Current event stream
            agent_instance: Reference to the agent instance
            
        Returns:
            Event: Result event to be added to the stream
        """
        # Implement your custom logic here
        result = self._perform_custom_operation(action_data)
        
        # Create and return an event with the result
        return Event(
            event_type="ACTION_RESULT",
            content=result,
            metadata={"action_type": self.type}
        )
        
    def _perform_custom_operation(self, action_data):
        """
        Implement the core functionality of your action.
        """
        # Your custom logic here
        return "Action completed successfully"
```

### Step 4: Advanced Agent Customization

#### Custom Event Processing

You can override event processing methods to add specialized behavior:

```python
def process_events(self, event_stream):
    """
    Custom event processing for code analysis tasks.
    """
    # Pre-process events to extract code-related information
    code_files = self._extract_code_files(event_stream)
    
    # Add code analysis context
    if code_files:
        self._add_code_analysis_context(event_stream, code_files)
    
    # Call parent processing
    return super().process_events(event_stream)

def _extract_code_files(self, event_stream):
    """
    Extract code files mentioned in the event stream.
    """
    code_files = []
    for event in event_stream.events_list:
        # Logic to identify code files in events
        pass
    return code_files
```

### Step 5: Testing Your Custom Agent

Create a test script to verify your custom agent works correctly:

```python
#!/usr/bin/env python3
"""
Test script for CodeAnalyzerAgent
"""

from your_module import CodeAnalyzerAgent
from anges.agents.agent_utils.events import EventStream, Event

def test_code_analyzer_agent():
    # Create agent instance
    agent = CodeAnalyzerAgent()
    
    # Create test event stream
    event_stream = EventStream()
    event_stream.events_list.append(
        Event(
            type="new_request",
            content="Analyze the code quality of main.py"
        )
    )
    
    # Test agent processing
    response = agent.process_events(event_stream)
    
    print(f"Agent response: {response}")
    print(f"Agent type: {type(agent).__name__}")
    print(f"Registered actions: {[action.type for action in agent.registered_actions]}")

if __name__ == "__main__":
    test_code_analyzer_agent()
```

### Step 2: Basic Custom Action Structure

Here's the minimal structure for a custom action:

```python
from anges.agents.agent_utils.agent_actions import Action
from anges.agents.agent_utils.events import Event

class MyCustomAction(Action):
    """
    A custom action that performs specific functionality.
    """
    
    def __init__(self):
        super().__init__()
        self.type = "MY_CUSTOM_ACTION"
        self.user_visible = True
        self.unique_action = False
        self.returning_action = True
        self.guide_prompt = """
Use this action to perform custom functionality.
Required fields:
- action_type: Must be "MY_CUSTOM_ACTION"
- parameter1: Description of parameter
- parameter2: Description of parameter
"""
    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        """
        Handle the action execution.
        
        Args:
            run_config: Configuration dictionary containing execution context
            parsed_response_dict: The full parsed response from the agent
            action_json: The specific action JSON object
        """
        # Extract parameters from action_json
        parameter1 = action_json.get("parameter1")
        parameter2 = action_json.get("parameter2", "default_value")
        
        # Perform the action logic
        result = self._perform_action(parameter1, parameter2)
        
        # Create event to record the action
        event_stream = run_config["event_stream"]
        
        content = f"Custom Action Result: {result}"
        message_text = f"{run_config['agent_message_base']} executed custom action"
        
        event_stream.events_list.append(
            Event(
                type="action",
                reasoning=parsed_response_dict.get("reasoning", ""),
                content=content,
                message=message_text,
                analysis=parsed_response_dict.get("analysis", ""),
                est_input_token=parsed_response_dict.get("est_input_token", 0),
                est_output_token=parsed_response_dict.get("est_output_token", 0)
            )
        )
    
    def _perform_action(self, parameter1, parameter2):
        """
        Implement the actual action logic here.
        """
        # Your custom logic here
        return f"Processed {parameter1} with {parameter2}"
```

### Step 3: Practical Custom Action Example

Let's create a practical example - a `GitOperationAction` that handles Git operations:

```python
import subprocess
from anges.utils.shell_wrapper import run_command

class GitOperationAction(Action):
    """
    Custom action for performing Git operations.
    Demonstrates a practical custom action that extends agent capabilities.
    """
    
    def __init__(self):
        self.type = "GIT_OPERATION"
        self.user_visible = False
        self.unique_action = False
        self.returning_action = False
        self.guide_prompt = """
### GIT_OPERATION:
**non-visible action**
Use this action to perform Git operations like status, add, commit, push, pull, etc.

Required fields:
- `action_type`: Must be "GIT_OPERATION".
- `operation`: Git operation to perform ("status", "add", "commit", "push", "pull", "log").

Optional fields:
- `files`: List of files for operations like add (default: all files).
- `message`: Commit message for commit operations.
- `branch`: Branch name for branch operations.

Examples:
{
  "action_type": "GIT_OPERATION",
  "operation": "status"
}

{
  "action_type": "GIT_OPERATION",
  "operation": "commit",
  "files": ["src/main.py"],
  "message": "Update main functionality"
}
"""
    
    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        """
        Handle the Git operation action.
        """
        operation = action_json.get("operation", "status")
        files = action_json.get("files", [])
        message = action_json.get("message", "Automated commit")
        
        event_stream = run_config["event_stream"]
        
        try:
            # Build Git command based on operation
            cmd = self._build_git_command(operation, files, message)
            
            # Execute the Git command
            result = run_command(
                cmd,
                cwd=run_config.get("cmd_init_dir", "./"),
                timeout=30
            )
            
            # Format the result
            content = f"Git Operation: {operation}\n"
            content += f"Command: {cmd}\n"
            content += f"Exit Code: {result['exit_code']}\n"
            content += f"Output:\n{result['stdout']}\n"
            if result['stderr']:
                content += f"Errors:\n{result['stderr']}\n"
            
            message_text = f"{run_config['agent_message_base']} executed git {operation}"
            
            event_stream.events_list.append(
                Event(
                    type="action",
                    reasoning=parsed_response_dict.get("reasoning", ""),
                    content=content,
                    analysis=parsed_response_dict.get("analysis", ""),
                    message=message_text,
                    est_input_token=parsed_response_dict.get("est_input_token", 0),
                    est_output_token=parsed_response_dict.get("est_output_token", 0),
                )
            )
            
        except Exception as e:
            # Handle errors gracefully
            error_content = f"Git operation failed: {str(e)}"
            event_stream.events_list.append(
                Event(
                    type="action",
                    reasoning=parsed_response_dict.get("reasoning", ""),
                    content=error_content,
                    analysis=parsed_response_dict.get("analysis", ""),
                    message=f"{run_config['agent_message_base']} git operation failed",
                    est_input_token=parsed_response_dict.get("est_input_token", 0),
                    est_output_token=parsed_response_dict.get("est_output_token", 0),
                )
            )
    
    def _build_git_command(self, operation, files, message):
        """
        Build the appropriate Git command based on the operation.
        """
        if operation == "status":
            return "git status"
        elif operation == "add":
            if files:
                return f"git add {' '.join(files)}"
            else:
                return "git add ."
        elif operation == "commit":
            return f'git commit -m "{message}"'
        elif operation == "push":
            return "git push"
        elif operation == "pull":
            return "git pull"
        elif operation == "log":
            return "git log --oneline -10"
        else:
            raise ValueError(f"Unsupported git operation: {operation}")
```

### Step 4: Testing Custom Actions

Create a test script to verify your custom action works correctly:

```python
#!/usr/bin/env python3
"""
Test script for GitOperationAction
"""

from your_module import GitOperationAction
from anges.agents.agent_utils.events import EventStream, Event

def test_git_operation_action():
    # Create action instance
    action = GitOperationAction()
    
    # Create test run config
    run_config = {
        "event_stream": EventStream(),
        "agent_message_base": "TestAgent",
        "cmd_init_dir": "./"
    }
    
    # Create test parsed response
    parsed_response = {
        "reasoning": "Testing git status operation",
        "analysis": "Checking repository status"
    }
    
    # Create test action JSON
    action_json = {
        "action_type": "GIT_OPERATION",
        "operation": "status"
    }
    
    # Test action execution
    action.handle_action_in_parsed_response(run_config, parsed_response, action_json)
    
    # Check results
    events = run_config["event_stream"].events_list
    print(f"Action executed. Events created: {len(events)}")
    if events:
        print(f"Last event content: {events[-1].content}")

if __name__ == "__main__":
    test_git_operation_action()
```

### Step 5: Registering Custom Actions with Agents

To use your custom action with an agent, register it in the agent's `__init__` method:

```python
class MyAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Register custom actions by adding them to the agent
        # Custom actions are automatically discovered and registered
        # when they inherit from the Action class and implement required methods
        self.custom_actions = [
            GitOperationAction(),  # Your custom action
            MyCustomAction(),      # Another custom action
        ]
        
        # Add custom actions to the agent's action registry
        for action in self.custom_actions:
            self.register_action(action)
```

## Best Practices

### For Custom Agents

1. **Clear Naming Convention**: Use descriptive names that indicate the agent's purpose (e.g., `CodeAnalyzerAgent`, `DataProcessingAgent`).

2. **Proper Inheritance**: Always extend `BaseAgent` and call `super().__init__()` in your constructor.

3. **Custom Prompt Templates**: Create domain-specific prompt templates that guide the agent's behavior effectively.

4. **Action Registration**: Only register actions that are relevant to your agent's purpose.

5. **Error Handling**: Implement robust error handling in custom methods.

```python
def custom_method(self, data):
    try:
        # Your logic here
        result = self._process_data(data)
        return result
    except Exception as e:
        self.logger.error(f"Error in custom_method: {str(e)}")
        raise
```

6. **Logging**: Use the built-in logger for debugging and monitoring:

```python
self.logger.info("Starting custom processing")
self.logger.debug(f"Processing data: {data}")
self.logger.warning("Potential issue detected")
self.logger.error(f"Error occurred: {error}")
```

### For Custom Actions

1. **Unique Action Types**: Ensure your action type is unique and descriptive.

2. **Comprehensive Guide Prompts**: Provide clear documentation in the `guide_prompt` with examples.

3. **Parameter Validation**: Validate input parameters and provide meaningful error messages.

```python
def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
    # Validate required parameters
    required_param = action_json.get("required_param")
    if not required_param:
        raise ValueError("required_param is missing from action JSON")
    
    # Validate parameter types
    if not isinstance(required_param, str):
        raise TypeError("required_param must be a string")
```

4. **Proper Event Creation**: Always create events to record action execution.

5. **Resource Cleanup**: Clean up any resources (files, connections, etc.) in case of errors.

6. **Timeout Handling**: Implement timeouts for long-running operations.

```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
    timeout = action_json.get("timeout", 30)
    
    # Set timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        # Your action logic here
        result = self._perform_operation()
    finally:
        # Clear timeout
        signal.alarm(0)
```

## Common Pitfalls

### For Custom Agents

1. **Forgetting to Call Super Constructor**
   ```python
   # Wrong
   def __init__(self, *args, **kwargs):
       self.custom_property = "value"
   
   # Correct
   def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.custom_property = "value"
   ```

2. **Incorrect Agent Message Base**
   ```python
   # Wrong - doesn't handle parent_ids
   self.agent_message_base = f"Agent (Type: MyAgent, ID: {self.uid}) "
   
   # Correct - handles both cases
   if self.parent_ids:
       self.agent_message_base = f"Agent (Type: MyAgent, ID: {self.uid}, Parent_Ids: {'-'.join(self.parent_ids)}) "
   else:
       self.agent_message_base = f"Agent (Type: MyAgent, ID: {self.uid}) "
   ```

3. **Not Properly Implementing Custom Actions**
   ```python
   # Wrong - missing required methods
   class MyAction(Action):
       def __init__(self):
           self.type = "MY_ACTION"
   
   # Correct - implements all required methods
   class MyAction(Action):
       def __init__(self):
           super().__init__()
           self.type = "MY_ACTION"
           self.user_visible = True
           self.unique_action = False
           self.returning_action = True
           self.guide_prompt = "Action guide here"
       
       def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
           # Implementation here
           pass
   ```

4. **Improper Prompt Template Formatting**
   ```python
   # Wrong - missing required placeholders
   self.agent_prompt_template = "You are a custom agent."
   
   # Correct - includes all required placeholders
   self.agent_prompt_template = """
   You are a custom agent.
   
   {base_instructions}
   
   ## Available Action Tags
   {action_tags}
   
   {action_guides}
   
   ######### FOLLOWING IS THE ACTUAL REQUEST #########
   # EVENT STREAM
   
   {event_stream}
   """
   ```

### For Custom Actions

1. **Missing Event Creation**
   ```python
   # Wrong - no event created
   def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
       result = self._do_something()
       return result
   
   # Correct - creates proper event
   def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
       result = self._do_something()
       
       event_stream = run_config["event_stream"]
       event_stream.events_list.append(
           Event(
               type="action",
               reasoning=parsed_response_dict.get("reasoning", ""),
               content=f"Action result: {result}",
               message=f"{run_config['agent_message_base']} executed action"
           )
       )
   ```

2. **Inadequate Error Handling**
   ```python
   # Wrong - no error handling
   def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
       result = risky_operation()
   
   # Correct - proper error handling
   def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
       try:
           result = risky_operation()
           # Create success event
       except Exception as e:
           # Create error event
           event_stream = run_config["event_stream"]
           event_stream.events_list.append(
               Event(
                   type="action",
                   content=f"Action failed: {str(e)}",
                   message=f"{run_config['agent_message_base']} action failed"
               )
           )
   ```

3. **Incomplete Guide Prompts**
   ```python
   # Wrong - minimal documentation
   self.guide_prompt = "Use this action to do something."
   
   # Correct - comprehensive documentation
   self.guide_prompt = """
   ### MY_ACTION:
   **non-visible action**
   Detailed description of what this action does.
   
   Required fields:
   - `action_type`: Must be "MY_ACTION".
   - `param1`: Description and type information.
   
   Optional fields:
   - `param2`: Description and default value.
   
   Examples:
   {
     "action_type": "MY_ACTION",
     "param1": "example_value"
   }
   """
   ```

## Advanced Patterns

### Stateful Custom Agents

For agents that need to maintain state across multiple interactions:

```python
class StatefulAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = {
            "processed_files": [],
            "analysis_results": {},
            "current_context": None
        }
    
    def update_state(self, key, value):
        """Update agent state safely."""
        self.state[key] = value
        self.logger.debug(f"State updated: {key} = {value}")
    
    def get_state(self, key, default=None):
        """Get state value safely."""
        return self.state.get(key, default)
    
    def reset_state(self):
        """Reset agent state."""
        self.state = {
            "processed_files": [],
            "analysis_results": {},
            "current_context": None
        }
```

### Conditional Action Registration

Register actions based on environment or configuration:

```python
class ConditionalAgent(BaseAgent):
    def __init__(self, enable_git=True, enable_docker=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Base actions are handled by the framework automatically
        # Custom actions can be registered conditionally
        self.registered_actions = []
        
        # Conditional actions
        if enable_git:
            self.registered_actions.append(GitOperationAction())
        
        if enable_docker:
            self.registered_actions.append(DockerOperationAction())
        
        # Environment-based actions
        if os.getenv("ENABLE_CLOUD_ACTIONS") == "true":
            self.registered_actions.append(CloudOperationAction())
        
        # Note: Core framework actions (RUN_SHELL_CMD, EDIT_FILE, etc.) 
        # are handled automatically by the base agent implementation

### Action Chaining

Create actions that can trigger other actions:

```python
class ChainedAction(Action):
    def __init__(self):
        self.type = "CHAINED_ACTION"
        self.user_visible = False
        self.unique_action = False
        self.returning_action = True  # This action returns data
    
    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        # Perform initial action
        initial_result = self._perform_initial_action(action_json)
        
        # Trigger follow-up actions based on result
        if initial_result.get("needs_followup"):
            self._trigger_followup_action(run_config, initial_result)
        
        # Return data for agent to use
        return {
            "success": True,
            "result": initial_result,
            "followup_triggered": initial_result.get("needs_followup", False)
        }
```

### Dynamic Prompt Templates

Create prompt templates that adapt based on context:

```python
class DynamicAgent(BaseAgent):
    def __init__(self, domain="general", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain = domain
        self.agent_prompt_template = self._build_dynamic_prompt()
    
    def _build_dynamic_prompt(self):
        base_prompt = """
# INSTRUCTION
You are a specialized AI agent.
"""
        
        domain_prompts = {
            "code": "You excel at code analysis, debugging, and software development tasks.",
            "data": "You specialize in data analysis, visualization, and statistical operations.",
            "devops": "You focus on deployment, infrastructure, and system administration."
        }
        
        domain_specific = domain_prompts.get(self.domain, "You are a general-purpose assistant.")
        
        return base_prompt + domain_specific + """

{base_instructions}

## Available Action Tags
{action_tags}

{action_guides}

######### FOLLOWING IS THE ACTUAL REQUEST #########
# EVENT STREAM

{event_stream}
"""
```

## Integration Examples

### Complete Custom Agent with Multiple Actions

Here's a complete example showing how to create a specialized agent with multiple custom actions:

```python
#!/usr/bin/env python3
"""
Complete example: DevOps Agent with custom actions
"""
import os
import json
from anges.agents.agent_utils.base_agent import BaseAgent
from anges.agents.agent_utils.agent_actions import Action
from anges.agents.agent_utils.events import Event
from anges.utils.shell_wrapper import run_command

class DockerOperationAction(Action):
    """Custom action for Docker operations."""
    
    def __init__(self):
        self.type = "DOCKER_OPERATION"
        self.user_visible = False
        self.unique_action = False
        self.returning_action = False
        self.guide_prompt = """
### DOCKER_OPERATION:
**non-visible action**
Use this action to perform Docker operations like build, run, stop, etc.

Required fields:
- `action_type`: Must be "DOCKER_OPERATION".
- `operation`: Docker operation ("build", "run", "stop", "ps", "logs").

Optional fields:
- `image`: Docker image name for build/run operations.
- `container`: Container name/ID for stop/logs operations.
- `dockerfile`: Path to Dockerfile for build operations.
- `ports`: Port mapping for run operations (e.g., "8080:80").

Example:
{
  "action_type": "DOCKER_OPERATION",
  "operation": "build",
  "image": "my-app:latest",
  "dockerfile": "./Dockerfile"
}
"""
    
    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        operation = action_json.get("operation")
        image = action_json.get("image", "")
        container = action_json.get("container", "")
        dockerfile = action_json.get("dockerfile", "Dockerfile")
        ports = action_json.get("ports", "")
        
        event_stream = run_config["event_stream"]
        
        try:
            cmd = self._build_docker_command(operation, image, container, dockerfile, ports)
            
            result = run_command(
                cmd,
                cwd=run_config.get("cmd_init_dir", "./"),
                timeout=300  # 5 minutes for Docker operations
            )
            
            content = f"Docker Operation: {operation}\n"
            content += f"Command: {cmd}\n"
            content += f"Exit Code: {result['exit_code']}\n"
            content += f"Output:\n{result['stdout']}\n"
            if result['stderr']:
                content += f"Errors:\n{result['stderr']}\n"
            
            event_stream.events_list.append(
                Event(
                    type="action",
                    reasoning=parsed_response_dict.get("reasoning", ""),
                    content=content,
                    message=f"{run_config['agent_message_base']} executed docker {operation}"
                )
            )
            
        except Exception as e:
            error_content = f"Docker operation failed: {str(e)}"
            event_stream.events_list.append(
                Event(
                    type="action",
                    content=error_content,
                    message=f"{run_config['agent_message_base']} docker operation failed"
                )
            )
    
    def _build_docker_command(self, operation, image, container, dockerfile, ports):
        if operation == "build":
            return f"docker build -t {image} -f {dockerfile} ."
        elif operation == "run":
            port_arg = f"-p {ports}" if ports else ""
            return f"docker run -d {port_arg} --name {container} {image}"
        elif operation == "stop":
            return f"docker stop {container}"
        elif operation == "ps":
            return "docker ps -a"
        elif operation == "logs":
            return f"docker logs {container}"
        else:
            raise ValueError(f"Unsupported docker operation: {operation}")

class SystemMonitorAction(Action):
    """Custom action for system monitoring."""
    
    def __init__(self):
        self.type = "SYSTEM_MONITOR"
        self.user_visible = False
        self.unique_action = False
        self.returning_action = True
        self.guide_prompt = """
### SYSTEM_MONITOR:
**non-visible action**
**returning action**
Use this action to monitor system resources and health.

Required fields:
- `action_type`: Must be "SYSTEM_MONITOR".
- `metric`: Metric to monitor ("cpu", "memory", "disk", "network", "all").

Example:
{
  "action_type": "SYSTEM_MONITOR",
  "metric": "all"
}
"""
    
    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        metric = action_json.get("metric", "all")
        event_stream = run_config["event_stream"]
        
        try:
            metrics_data = self._collect_metrics(metric)
            
            content = f"System Monitoring Results:\n"
            content += json.dumps(metrics_data, indent=2)
            
            event_stream.events_list.append(
                Event(
                    type="action",
                    reasoning=parsed_response_dict.get("reasoning", ""),
                    content=content,
                    message=f"{run_config['agent_message_base']} collected system metrics"
                )
            )
            
            return metrics_data
            
        except Exception as e:
            error_content = f"System monitoring failed: {str(e)}"
            event_stream.events_list.append(
                Event(
                    type="action",
                    content=error_content,
                    message=f"{run_config['agent_message_base']} monitoring failed"
                )
            )
            return {"error": str(e)}
    
    def _collect_metrics(self, metric):
        import psutil
        
        metrics = {}
        
        if metric in ["cpu", "all"]:
            metrics["cpu"] = {
                "usage_percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "load_avg": os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
        
        if metric in ["memory", "all"]:
            memory = psutil.virtual_memory()
            metrics["memory"] = {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            }
        
        if metric in ["disk", "all"]:
            disk = psutil.disk_usage('/')
            metrics["disk"] = {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        
        return metrics

class DevOpsAgent(BaseAgent):
    """
    Specialized agent for DevOps tasks including Docker operations,
    system monitoring, and infrastructure management.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set custom agent identification
        if self.parent_ids:
            self.agent_message_base = f"Agent (Type: DevOpsAgent, ID: {self.uid}, Parent_Ids: {'-'.join(self.parent_ids)}) "
        else:
            self.agent_message_base = f"Agent (Type: DevOpsAgent, ID: {self.uid}) "
        
        # Custom prompt template for DevOps tasks
        self.agent_prompt_template = """
# INSTRUCTION
You are a specialized DevOps AI agent. You excel at:
- Container orchestration and Docker operations
- System monitoring and performance analysis
- Infrastructure automation and deployment
- CI/CD pipeline management
- System administration and troubleshooting

Your responses should be technical, focused on reliability, scalability, and best practices.

{base_instructions}

## Available Action Tags
Here are the actionable tags that you can use: {action_tags}

{action_guides}

######### FOLLOWING IS THE ACTUAL REQUEST #########
# EVENT STREAM

{event_stream}

# Next Step

<Now output the next step action in JSON. Do not include ``` quotes. Your whole response needs to be JSON parsable.>
"""
        
        # Register actions including custom ones
        self.registered_actions = [
            TaskCompleteAction(),
            RunShellCMDAction(),
            EditFileAction(),
            AgentTextResponseAction(),
            AgentHelpNeededAction(),
            DockerOperationAction(),
            SystemMonitorAction(),
            GitOperationAction(),  # From previous example
        ]
    
    def analyze_system_health(self, event_stream):
        """
        Custom method to analyze overall system health.
        """
        try:
            # This would typically be called as part of event processing
            self.logger.info("Analyzing system health")
            
            # Custom logic for health analysis
            health_metrics = {
                "timestamp": time.time(),
                "status": "healthy",
                "checks_performed": [
                    "cpu_usage",
                    "memory_usage",
                    "disk_space",
                    "docker_status"
                ]
            }
            
            return health_metrics
            
        except Exception as e:
            self.logger.error(f"Health analysis failed: {str(e)}")
            raise

# Usage example
if __name__ == "__main__":
    # Create DevOps agent
    agent = DevOpsAgent()
    
    # Create test event stream
    from anges.agents.agent_utils.events import EventStream, Event
    
    event_stream = EventStream()
    event_stream.events_list.append(
        Event(
            type="new_request",
            content="Monitor system resources and deploy the application using Docker"
        )
    )
    
    # Process events
    response = agent.process_events(event_stream)
    print(f"Agent response: {response}")
```

### Testing and Validation

Create comprehensive tests for your custom implementations:

```python
#!/usr/bin/env python3
"""
Comprehensive test suite for custom agents and actions
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch

from your_module import DevOpsAgent, DockerOperationAction, SystemMonitorAction
from anges.agents.agent_utils.events import EventStream, Event

class TestCustomImplementations(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = DevOpsAgent()
        self.docker_action = DockerOperationAction()
        self.monitor_action = SystemMonitorAction()
        
        self.run_config = {
            "event_stream": EventStream(),
            "agent_message_base": "TestAgent",
            "cmd_init_dir": "./"
        }
        
        self.parsed_response = {
            "reasoning": "Test reasoning",
            "analysis": "Test analysis"
        }
    
    def test_agent_initialization(self):
        """Test that the custom agent initializes correctly."""
        self.assertIsInstance(self.agent, DevOpsAgent)
        self.assertIn("DevOpsAgent", self.agent.agent_message_base)
        self.assertTrue(len(self.agent.registered_actions) > 5)
    
    def test_docker_action_properties(self):
        """Test Docker action properties."""
        self.assertEqual(self.docker_action.type, "DOCKER_OPERATION")
        self.assertFalse(self.docker_action.user_visible)
        self.assertIn("DOCKER_OPERATION", self.docker_action.guide_prompt)
    
    @patch('anges.utils.shell_wrapper.run_command')
    def test_docker_build_operation(self, mock_run_command):
        """Test Docker build operation."""
        mock_run_command.return_value = {
            'exit_code': 0,
            'stdout': 'Successfully built image',
            'stderr': ''
        }
        
        action_json = {
            "action_type": "DOCKER_OPERATION",
            "operation": "build",
            "image": "test-app:latest"
        }
        
        self.docker_action.handle_action_in_parsed_response(
            self.run_config, self.parsed_response, action_json
        )
        
        # Verify command was called
        mock_run_command.assert_called_once()
        args, kwargs = mock_run_command.call_args
        self.assertIn("docker build", args[0])
        
        # Verify event was created
        events = self.run_config["event_stream"].events_list
        self.assertEqual(len(events), 1)
        self.assertIn("Docker Operation: build", events[0].content)
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_system_monitor_action(self, mock_memory, mock_cpu):
        """Test system monitoring action."""
        # Mock system metrics
        mock_cpu.return_value = 25.5
        mock_memory.return_value = Mock(
            total=8000000000,
            available=4000000000,
            percent=50.0,
            used=4000000000
        )
        
        action_json = {
            "action_type": "SYSTEM_MONITOR",
            "metric": "cpu"
        }
        
        result = self.monitor_action.handle_action_in_parsed_response(
            self.run_config, self.parsed_response, action_json
        )
        
        # Verify metrics were collected
        self.assertIn("cpu", result)
        self.assertEqual(result["cpu"]["usage_percent"], 25.5)
        
        # Verify event was created
        events = self.run_config["event_stream"].events_list
        self.assertEqual(len(events), 1)
        self.assertIn("System Monitoring Results", events[0].content)
    
    def test_agent_action_registration(self):
        """Test that all actions are properly registered."""
        action_types = [action.type for action in self.agent.registered_actions]
        
        # Check for required actions
        required_actions = [
            "TASK_COMPLETE",
            "RUN_SHELL_CMD",
            "EDIT_FILE",
            "AGENT_TEXT_RESPONSE",
            "HELP_NEEDED"
        ]
        
        for required_action in required_actions:
            self.assertIn(required_action, action_types)
        
        # Check for custom actions
        self.assertIn("DOCKER_OPERATION", action_types)
        self.assertIn("SYSTEM_MONITOR", action_types)
    
    def test_error_handling(self):
        """Test error handling in custom actions."""
        action_json = {
            "action_type": "DOCKER_OPERATION",
            "operation": "invalid_operation"
        }
        
        # This should handle the error gracefully
        self.docker_action.handle_action_in_parsed_response(
            self.run_config, self.parsed_response, action_json
        )
        
        # Verify error event was created
        events = self.run_config["event_stream"].events_list
        self.assertEqual(len(events), 1)
        self.assertIn("failed", events[0].content.lower())

if __name__ == '__main__':
    unittest.main()
```

## Conclusion

This implementation guide provides comprehensive instructions for extending the Anges framework with custom agents and actions. Key takeaways:

### For Custom Agents:
- Always extend `BaseAgent` and call the parent constructor
- Create domain-specific prompt templates
- Register only relevant actions
- Implement proper error handling and logging
- Test thoroughly with realistic scenarios

### For Custom Actions:
- Use unique, descriptive action types
- Provide comprehensive guide prompts with examples
- Validate input parameters
- Create proper events for all outcomes
- Handle errors gracefully
- Include timeout handling for long operations

### Development Workflow:
1. **Plan**: Define the specific functionality your agent/action will provide
2. **Implement**: Follow the patterns and best practices outlined in this guide
3. **Test**: Create comprehensive unit tests and integration tests
4. **Document**: Provide clear documentation and examples
5. **Iterate**: Refine based on usage and feedback

### Next Steps:
- Review the example files in `examples/custom_agent.py` and `examples/custom_action.py`
- Start with simple implementations and gradually add complexity
- Consider contributing useful custom implementations back to the project
- Join the community discussions for tips and best practices

By following this guide, you'll be able to create robust, maintainable extensions to the Anges framework that integrate seamlessly with the existing architecture while providing powerful new capabilities for your specific use cases.
