#!/usr/bin/env python3
"""
Custom Action Example for Anges Framework

This example demonstrates how to create custom actions that can be used
with any agent in the Anges framework. Custom actions extend the framework's
capabilities with specialized functionality.
"""

import json
import os
import time
import subprocess
from anges.agents.agent_utils.agent_actions import Action
from anges.agents.agent_utils.events import Event
from anges.agents.default_agent import DefaultAgent
from anges.utils.shell_wrapper import run_command


class GitOperationAction(Action):
    """
    Custom action for performing Git operations.
    Demonstrates a practical custom action that extends agent capabilities.
    
    用于执行Git操作的自定义动作。
    演示扩展代理功能的实用自定义动作。
    """
    
    def __init__(self):
        # Action type identifier | 动作类型标识符
        self.type = "GIT_OPERATION"
        # Whether action output is shown to user | 动作输出是否显示给用户
        self.user_visible = False
        # Whether this action can be combined with others | 此动作是否可以与其他动作组合
        self.unique_action = False
        # Whether this action returns results | 此动作是否返回结果
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
        处理Git操作动作。
        """
        # Extract operation parameters | 提取操作参数
        operation = action_json.get("operation", "status")
        files = action_json.get("files", [])
        message = action_json.get("message", "Automated commit")
        
        event_stream = run_config["event_stream"]
        
        try:
            # Build Git command based on operation | 根据操作构建Git命令
            cmd = self._build_git_command(operation, files, message)
            
            # Execute the Git command | 执行Git命令
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
            
            run_config["message_handler_func"](message_text)
            
        except Exception as e:
            error_message = f"Error executing git {operation}: {str(e)}"
            event_stream.events_list.append(
                Event(
                    type="error",
                    reasoning=parsed_response_dict.get("reasoning", ""),
                    content=error_message,
                    message=f"{run_config['agent_message_base']} {error_message}",
                )
            )
        
        return event_stream
    
    def _build_git_command(self, operation, files, message):
        """
        Build the appropriate Git command based on the operation and parameters.
        """
        if operation == "add":
            if files:
                return f"git add {' '.join(files)}"
            else:
                return "git add ."
        elif operation == "commit":
            return f"git commit -m '{message}'"
        elif operation == "status":
            return "git status"
        elif operation == "log":
            return "git log --oneline -10"
        elif operation == "push":
            return "git push origin main"
        elif operation == "pull":
            return "git pull origin main"
        else:
            return f"git {operation}"


class APICallAction(Action):
    """
    Custom action for making HTTP API calls.
    Demonstrates an action that interacts with external services.
    """
    
    def __init__(self):
        self.type = "API_CALL"
        self.user_visible = False
        self.unique_action = False
        self.returning_action = False
        self.guide_prompt = """
### API_CALL:
**non-visible action**
Use this action to make HTTP API calls to external services.

Required fields:
- `action_type`: Must be "API_CALL".
- `url`: The API endpoint URL.
- `method`: HTTP method ("GET", "POST", "PUT", "DELETE").

Optional fields:
- `headers`: Dictionary of HTTP headers.
- `data`: Request body data (for POST/PUT requests).
- `timeout`: Request timeout in seconds (default: 30).

Examples:
{
  "action_type": "API_CALL",
  "url": "https://httpbin.org/get",
  "method": "GET"
}

{
  "action_type": "API_CALL",
  "url": "https://httpbin.org/post",
  "method": "POST",
  "data": {"key": "value"}
}
"""
    
    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        """
        Handle the API call action.
        """
        url = action_json.get("url", "")
        method = action_json.get("method", "GET").upper()
        headers = action_json.get("headers", {})
        data = action_json.get("data", None)
        timeout = action_json.get("timeout", 30)
        
        event_stream = run_config["event_stream"]
        
        try:
            # Use curl for HTTP requests
            result = self._make_curl_request(url, method, headers, data, timeout)
            
            content = f"API Call Results:\n"
            content += f"URL: {url}\n"
            content += f"Method: {method}\n"
            content += f"Status: {result['status']}\n"
            content += f"Response:\n{result['response']}\n"
            
            if result['error']:
                content += f"Error: {result['error']}\n"
            
            message_text = f"{run_config['agent_message_base']} made {method} request to {url}"
            
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
            
            run_config["message_handler_func"](message_text)
            
        except Exception as e:
            error_message = f"Error making API call: {str(e)}"
            event_stream.events_list.append(
                Event(
                    type="error",
                    reasoning=parsed_response_dict.get("reasoning", ""),
                    content=error_message,
                    message=f"{run_config['agent_message_base']} {error_message}",
                )
            )
        
        return event_stream
    
    def _make_curl_request(self, url, method, headers, data, timeout):
        """
        Make HTTP request using curl command.
        """
        cmd = ["curl", "-s", "-w", "\n%{http_code}", "-X", method]
        
        # Add headers
        for key, value in headers.items():
            cmd.extend(["-H", f"{key}: {value}"])
        
        # Add data for POST/PUT requests
        if data and method in ["POST", "PUT", "PATCH"]:
            if isinstance(data, dict):
                cmd.extend(["-d", json.dumps(data)])
                cmd.extend(["-H", "Content-Type: application/json"])
            else:
                cmd.extend(["-d", str(data)])
        
        cmd.append(url)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output_lines = result.stdout.strip().split('\n')
            status_code = output_lines[-1] if output_lines else "000"
            response_body = '\n'.join(output_lines[:-1]) if len(output_lines) > 1 else ""
            
            return {
                "status": status_code,
                "response": response_body,
                "error": result.stderr if result.stderr else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "response": "",
                "error": f"Request timed out after {timeout} seconds"
            }
        except Exception as e:
            return {
                "status": "error",
                "response": "",
                "error": str(e)
            }


class SimpleLogAction(Action):
    """
    A simple custom action that demonstrates the basic pattern.
    This action just logs a message to the event stream.
    """
    
    def __init__(self):
        self.type = "SIMPLE_LOG"
        self.user_visible = False
        self.unique_action = False
        self.returning_action = False
        self.guide_prompt = """
### SIMPLE_LOG:
**non-visible action**
Use this action to log a simple message.

Required fields:
- `action_type`: Must be "SIMPLE_LOG".
- `message`: The message to log.

Optional fields:
- `level`: Log level ("info", "warning", "error").

Example:
{
  "action_type": "SIMPLE_LOG",
  "message": "This is a test message",
  "level": "info"
}
"""
    
    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        """
        Handle the simple log action.
        """
        message = action_json.get("message", "No message provided")
        level = action_json.get("level", "info")
        
        event_stream = run_config["event_stream"]
        
        content = f"[{level.upper()}] {message}"
        message_text = f"{run_config['agent_message_base']} logged: {message}"
        
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
        
        run_config["message_handler_func"](message_text)
        return event_stream


class FileHashAction(Action):
    """
    Custom action for computing file hashes.
    Demonstrates an action that performs file operations.
    """
    
    def __init__(self):
        self.type = "FILE_HASH"
        self.user_visible = False
        self.unique_action = False
        self.returning_action = False
        self.guide_prompt = """
### FILE_HASH:
**non-visible action**
Use this action to compute hash values of files.

Required fields:
- `action_type`: Must be "FILE_HASH".
- `file_path`: Path to the file to hash.

Optional fields:
- `algorithm`: Hash algorithm ("md5", "sha1", "sha256") (default: "sha256").

Example:
{
  "action_type": "FILE_HASH",
  "file_path": "./data.txt",
  "algorithm": "sha256"
}
"""
    
    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        """
        Handle the file hash action.
        """
        file_path = action_json.get("file_path", "")
        algorithm = action_json.get("algorithm", "sha256")
        
        event_stream = run_config["event_stream"]
        
        try:
            # Use system commands to compute hash
            if algorithm == "md5":
                cmd = f"md5sum '{file_path}'"
            elif algorithm == "sha1":
                cmd = f"sha1sum '{file_path}'"
            elif algorithm == "sha256":
                cmd = f"sha256sum '{file_path}'"
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
            result = run_command(
                cmd,
                cwd=run_config.get("cmd_init_dir", "./"),
                timeout=30
            )
            
            if result['exit_code'] == 0:
                hash_value = result['stdout'].split()[0]
                content = f"File Hash Results:\n"
                content += f"File: {file_path}\n"
                content += f"Algorithm: {algorithm}\n"
                content += f"Hash: {hash_value}\n"
            else:
                content = f"Error computing hash: {result['stderr']}"
            
            message_text = f"{run_config['agent_message_base']} computed {algorithm} hash for {file_path}"
            
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
            
            run_config["message_handler_func"](message_text)
            
        except Exception as e:
            error_message = f"Error computing file hash: {str(e)}"
            event_stream.events_list.append(
                Event(
                    type="error",
                    reasoning=parsed_response_dict.get("reasoning", ""),
                    content=error_message,
                    message=f"{run_config['agent_message_base']} {error_message}",
                )
            )
        
        return event_stream


def demonstrate_custom_actions():
    """
    Demonstrate the usage of custom actions with agents.
    """
    print("=== Custom Action Examples ===\n")
    
    # Create an agent and register custom actions
    agent = DefaultAgent(
        cmd_init_dir="./",
        logging_level=30,  # WARNING level to reduce noise
        auto_entitle=True
    )
    
    # Add custom actions to the agent
    custom_actions = [
        GitOperationAction(),
        APICallAction(),
        SimpleLogAction(),
        FileHashAction()
    ]
    
    agent.registered_actions.extend(custom_actions)
    
    print(f"Agent now has {len(agent.registered_actions)} actions available:")
    for action in agent.registered_actions:
        print(f"  - {action.type}")
    
    # Example 1: Simple Log Action
    print("\n--- Example 1: Simple Log Action ---")
    try:
        task1 = """
        Use the SIMPLE_LOG action to log a test message with info level.
        """
        
        result = agent.run_with_new_request(task1)
        print(f"Simple log completed with {len(result.events_list)} events.")
        
    except Exception as e:
        print(f"Error in simple log example: {e}")
    
    # Example 2: File Hash Action
    print("\n--- Example 2: File Hash Action ---")
    try:
        # Create a test file
        with open("test_hash_file.txt", "w") as f:
            f.write("Hello, this is a test file for hashing!")
        
        task2 = """
        Use the FILE_HASH action to compute the SHA256 hash of 'test_hash_file.txt'.
        """
        
        result = agent.run_with_new_request(task2)
        print(f"File hash completed with {len(result.events_list)} events.")
        
        # Clean up
        os.remove("test_hash_file.txt")
        
    except Exception as e:
        print(f"Error in file hash example: {e}")
    
    # Example 3: API Call Action
    print("\n--- Example 3: API Call Action ---")
    try:
        task3 = """
        Use the API_CALL action to make a GET request to https://httpbin.org/get
        to test the API functionality.
        """
        
        result = agent.run_with_new_request(task3)
        print(f"API call completed with {len(result.events_list)} events.")
        
    except Exception as e:
        print(f"Error in API call example: {e}")


def demonstrate_action_patterns():
    """
    Demonstrate different patterns for creating custom actions.
    """
    print("\n=== Custom Action Design Patterns ===\n")
    
    print("1. Basic Action Pattern:")
    print("   - Extend the Action class")
    print("   - Set type, visibility, and uniqueness properties")
    print("   - Implement handle_action_in_parsed_response method")
    print("   - Create appropriate guide_prompt")
    
    print("\n2. Action Properties:")
    print("   - user_visible: Whether action results are shown to user")
    print("   - unique_action: Whether action can be used alone in response")
    print("   - returning_action: Whether action terminates agent execution")
    
    print("\n3. Error Handling:")
    print("   - Always wrap action logic in try-catch blocks")
    print("   - Create error events for failures")
    print("   - Provide meaningful error messages")
    
    print("\n4. Integration with Agents:")
    print("   - Add actions to agent.registered_actions list")
    print("   - Actions automatically become available in agent prompts")
    print("   - Use existing infrastructure (run_command, Event, etc.)")


if __name__ == "__main__":
    print("Anges Framework Custom Action Examples")
    print("=====================================\n")
    
    try:
        demonstrate_custom_actions()
        demonstrate_action_patterns()
        
        print("\n=== Custom Action Examples Completed ===\n")
        print("Key takeaways:")
        print("1. Extend the Action class to create custom actions")
        print("2. Implement handle_action_in_parsed_response method")
        print("3. Set appropriate action properties (type, visibility, etc.)")
        print("4. Use existing framework infrastructure for consistency")
        print("5. Always include proper error handling")
        print("6. Add actions to agent.registered_actions to make them available")
        
    except Exception as e:
        print(f"Error running custom action examples: {e}")
        print("Make sure you have the Anges framework properly installed and configured.")