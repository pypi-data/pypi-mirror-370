#!/usr/bin/env python3
"""
Basic Usage Example for Anges Framework

This example demonstrates the fundamental usage of the Anges framework,
including creating a default agent and running simple tasks.
"""

import logging
from anges.agents.default_agent import DefaultAgent
from anges.config import config
from anges.utils.inference_api import INFERENCE_FUNC_DICT


def basic_agent_example():
    """
    Demonstrates basic agent creation and task execution.
    """
    print("=== Basic Anges Agent Usage Example ===")
    
    # Create a default agent with basic configuration
    # 创建一个具有基本配置的默认代理
    agent = DefaultAgent(
        cmd_init_dir="./",  # Working directory for shell commands | Shell命令的工作目录
        logging_level=logging.INFO,
        auto_entitle=True  # Automatically generate titles for conversations | 自动为对话生成标题
    )
    
    print(f"Created agent with ID: {agent.uid}")
    print(f"Agent type: DefaultAgent")
    print(f"Available actions: {[action.type for action in agent.registered_actions]}")
    
    # Example 1: Simple file operations task
    print("\n--- Example 1: File Operations Task ---")
    task1 = """
    Create a simple text file called 'hello.txt' with the content 'Hello, Anges Framework!' 
    and then display its contents.
    """
    
    try:
        result_stream = agent.run_with_new_request(task1)
        print(f"Task completed. Event stream has {len(result_stream.events_list)} events.")
        print(f"Final status: {result_stream.events_list[-1].type}")
    except Exception as e:
        print(f"Error running task: {e}")
    
    # Example 2: System information task
    print("\n--- Example 2: System Information Task ---")
    task2 = """
    Check the current working directory, list the files in it, 
    and show the current date and time.
    """
    
    try:
        result_stream = agent.run_with_new_request(task2)
        print(f"Task completed. Event stream has {len(result_stream.events_list)} events.")
        print(f"Final status: {result_stream.events_list[-1].type}")
    except Exception as e:
        print(f"Error running task: {e}")


def agent_with_custom_config_example():
    """
    Demonstrates creating an agent with custom configuration.
    """
    print("\n=== Agent with Custom Configuration Example ===")
    # Create agent with custom settings
    # 创建具有自定义设置的代理
    custom_agent = DefaultAgent(
        cmd_init_dir="/tmp",  # Different working directory | 不同的工作目录
        prefix_cmd="echo 'Starting command:' && ",  # Prefix for shell commands | Shell命令的前缀
        logging_level=logging.DEBUG,
    )
    
    print(f"Created custom agent with ID: {custom_agent.uid}")
    
    # Run a task that will use the custom configuration
    task = """
    Create a temporary file in the current directory with today's date,
    then verify it was created successfully.
    """
    
    try:
        result_stream = custom_agent.run_with_new_request(task)
        print(f"Task completed with {len(result_stream.events_list)} events.")
    except Exception as e:
        print(f"Error running custom agent task: {e}")


def event_stream_inspection_example():
    """
    Demonstrates how to inspect the event stream from agent execution.
    演示如何检查代理执行的事件流。
    """
    print("\n=== Event Stream Inspection Example ===")
    
    agent = DefaultAgent()
    task = "List the files in the current directory and count them."
    
    # Execute task and get event stream
    # 执行任务并获取事件流
    try:
        result_stream = agent.run_with_new_request(task)
        
        print(f"\nTotal events in stream: {len(result_stream.events_list)}")
        print("Event breakdown by type:")
        
        # Analyze event types and their frequency
        # 分析事件类型及其频率
        event_types = {}
        for event in result_stream.events_list:
            event_type = event.type
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        for event_type, count in event_types.items():
            print(f"  {event_type}: {count}")
        
        print("\n--- Event Details ---")
        for i, event in enumerate(result_stream.events_list):
            print(f"Event {i+1}: {event.type} at {event.timestamp}")
            if hasattr(event, 'content') and event.content:
                content_preview = str(event.content)[:100]
                print(f"  Content preview: {content_preview}...")
    
    except Exception as e:
        print(f"Error in event stream inspection: {e}")


def message_handler_example():
    """
    Demonstrates how to use custom message handlers to capture agent output.
    """
    print("\n=== Message Handler Example ===")
    
    # List to capture messages
    captured_messages = []
    
    def custom_message_handler(message: str):
        """Custom handler that captures messages."""
        captured_messages.append(message)
        print(f"[CAPTURED]: {message}")
    
    # Create agent and register the message handler
    agent = DefaultAgent(logging_level=logging.WARNING)
    agent.message_handlers.append(custom_message_handler)
    
    task = "Echo 'Hello from Anges!' and create a small test file."
    
    try:
        result_stream = agent.run_with_new_request(task)
        
        print(f"\nCaptured {len(captured_messages)} messages:")
        for i, msg in enumerate(captured_messages):
            print(f"  {i+1}. {msg[:100]}..." if len(msg) > 100 else f"  {i+1}. {msg}")
            
    except Exception as e:
        print(f"Error in message handler example: {e}")


if __name__ == "__main__":
    print("Anges Framework Basic Usage Examples")
    print("====================================\n")
    
    try:
        # Run all examples
        basic_agent_example()
        agent_with_custom_config_example()
        event_stream_inspection_example()
        message_handler_example()
        
        print("\n=== All Examples Completed ===")
        print("These examples demonstrate the core functionality of the Anges framework.")
        print("For more advanced usage, see the other example files in this directory.")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have the Anges framework properly installed and configured.")