#!/usr/bin/env python3
"""
Orchestrator Demo Example for Anges Framework

This example demonstrates how to use the Orchestrator to coordinate multiple agents,
handle complex multi-step tasks, and manage agent delegation patterns.
"""

import logging
import time
from anges.agents.orchestrator import Orchestrator
from anges.agents.default_agent import DefaultAgent
from anges.agents.task_analyzer import TaskAnalyzer
from anges.agents.task_executor import TaskExecutor
from anges.agents.agent_utils.events import Event, EventStream
from anges.config import config
from anges.utils.data_handler import save_event_stream, read_event_stream


def basic_orchestrator_example():
    """
    Demonstrates basic orchestrator usage for coordinating tasks.
    演示协调任务的基本编排器用法。
    """
    print("=== Basic Orchestrator Example ===")
    
    # Create an orchestrator instance | 创建编排器实例
    orchestrator = Orchestrator(
        cmd_init_dir="./",
        logging_level=logging.INFO,
    )
    
    print(f"Created orchestrator with ID: {orchestrator.uid}")
    print(f"Available child agents: TaskAnalyzer, TaskExecutor")
    # Example task that benefits from orchestration
    # 受益于编排的示例任务
    complex_task = """
    I need to create a Python project structure for a web API. Please:
    1. Analyze what components are needed for a REST API project
    2. Create the directory structure
    3. Set up basic configuration files
    4. Create sample endpoint files
    """
    
    try:
        # Execute the complex task using orchestrator
        # 使用编排器执行复杂任务
        print(f"\nExecuting complex task: {complex_task[:50]}...")
        result_stream = orchestrator.run_with_new_request(complex_task)
        
        # Display orchestration results
        # 显示编排结果
        print(f"\nTask completed with {len(result_stream.events_list)} events.")
        print("\n--- Task Delegation Summary ---")
        for i, event in enumerate(result_stream.events_list):
            if hasattr(event, 'type') and 'agent' in event.type.lower():
                print(f"Step {i+1}: {event.type} - {event.reasoning[:100]}...")
                
    except Exception as e:
        print(f"Error in orchestrator example: {e}")


def orchestrator_with_custom_agents_example():
    """
    Demonstrates using orchestrator with custom specialized agents.
    """
    print("\n=== Orchestrator with Custom Agents Example ===")
    
    # Create specialized agents for different tasks
    file_manager_agent = DefaultAgent(
        cmd_init_dir="./",
        logging_level=logging.WARNING,
        auto_entitle=False
    )
    
    code_generator_agent = DefaultAgent(
        cmd_init_dir="./",
        logging_level=logging.WARNING,
        auto_entitle=False
    )
    
    # Create orchestrator
    orchestrator = Orchestrator(
        cmd_init_dir="./",
        logging_level=logging.INFO
    )
    
    print(f"Created orchestrator with specialized agents")
    print(f"File Manager Agent ID: {file_manager_agent.uid}")
    print(f"Code Generator Agent ID: {code_generator_agent.uid}")
    
    # Task that requires coordination between different types of work
    coordination_task = """
    Create a simple calculator project:
    1. Set up the project directory structure
    2. Write a calculator.py module with basic math operations
    3. Create a test file for the calculator
    4. Generate documentation
    """
    
    try:
        print("\nExecuting coordination task...")
        result_stream = orchestrator.run_with_new_request(coordination_task)
        
        print(f"Coordination task completed with {len(result_stream.events_list)} events.")
        
        # Analyze the orchestration pattern
        print("\n--- Orchestration Analysis ---")
        task_analysis_events = [e for e in result_stream.events_list if 'analysis' in e.type.lower()]
        execution_events = [e for e in result_stream.events_list if 'action' in e.type.lower()]
        
        print(f"Task analysis events: {len(task_analysis_events)}")
        print(f"Execution events: {len(execution_events)}")
        
    except Exception as e:
        print(f"Error in coordination example: {e}")


def multi_step_workflow_example():
    """
    Demonstrates orchestrator handling a complex multi-step workflow.
    """
    print("\n=== Multi-Step Workflow Example ===")
    
    orchestrator = Orchestrator(
        cmd_init_dir="./",
        logging_level=logging.INFO,
        auto_entitle=True
    )
    
    # Complex workflow that requires multiple phases
    workflow_task = """
    Create a data processing pipeline:
    
    Phase 1 - Setup:
    - Create a data/ directory
    - Generate sample CSV data with 100 rows of user information
    
    Phase 2 - Processing:
    - Write a Python script to read and analyze the CSV data
    - Calculate basic statistics (mean, median, count)
    - Identify any data quality issues
    
    Phase 3 - Output:
    - Generate a summary report
    - Create visualizations if possible
    - Package everything into a results/ directory
    """
    
    try:
        print("\nExecuting multi-step workflow...")
        start_time = time.time()
        
        result_stream = orchestrator.run_with_new_request(workflow_task)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"Workflow completed in {execution_time:.2f} seconds")
        print(f"Total events: {len(result_stream.events_list)}")
        
        # Analyze workflow phases
        print("\n--- Workflow Phase Analysis ---")
        phases = {}
        for event in result_stream.events_list:
            event_type = getattr(event, 'type', 'unknown')
            if event_type not in phases:
                phases[event_type] = 0
            phases[event_type] += 1
        
        for phase, count in phases.items():
            print(f"{phase}: {count} events")
            
    except Exception as e:
        print(f"Error in workflow example: {e}")


def orchestrator_error_handling_example():
    """
    Demonstrates how orchestrator handles errors and recovery.
    """
    print("\n=== Orchestrator Error Handling Example ===")
    
    orchestrator = Orchestrator(
        cmd_init_dir="./",
        logging_level=logging.INFO
    )
    
    # Task with potential failure points
    error_prone_task = """
    Perform these operations and handle any errors gracefully:
    1. Try to read a file that doesn't exist
    2. Attempt to create a directory with invalid characters
    3. Run a command that might fail
    4. If any step fails, provide alternatives and continue
    """
    
    try:
        print("\nExecuting error-prone task...")
        result_stream = orchestrator.run_with_new_request(error_prone_task)
        
        print(f"Error handling task completed with {len(result_stream.events_list)} events.")
        
        # Analyze error handling
        print("\n--- Error Handling Analysis ---")
        error_events = [e for e in result_stream.events_list if hasattr(e, 'type') and 'error' in e.type.lower()]
        recovery_events = [e for e in result_stream.events_list if hasattr(e, 'reasoning') and 'alternative' in e.reasoning.lower()]
        
        print(f"Error events: {len(error_events)}")
        print(f"Recovery attempts: {len(recovery_events)}")
        
        if error_events:
            print("\nError details:")
            for i, error_event in enumerate(error_events[:3]):  # Show first 3 errors
                print(f"  {i+1}. {getattr(error_event, 'content', 'No content')[:100]}...")
                
    except Exception as e:
        print(f"Error in error handling example: {e}")


def event_stream_persistence_example():
    """
    Demonstrates saving and loading orchestrator event streams.
    """
    print("\n=== Event Stream Persistence Example ===")
    
    orchestrator = Orchestrator(
        cmd_init_dir="./",
        logging_level=logging.WARNING  # Reduce noise
    )
    
    # Simple task for demonstration
    simple_task = "Create a text file with the current date and time, then display its contents."
    
    try:
        print("\nExecuting task and saving event stream...")
        result_stream = orchestrator.run_with_new_request(simple_task)
        
        # Save the event stream
        save_event_stream(result_stream)
        print(f"Event stream saved with ID: {result_stream.uid}")
        
        # Load the event stream back
        loaded_stream = read_event_stream(result_stream.uid)
        print(f"Event stream loaded successfully")
        print(f"Original events: {len(result_stream.events_list)}")
        print(f"Loaded events: {len(loaded_stream.events_list)}")
        
        # Verify data integrity
        if len(result_stream.events_list) == len(loaded_stream.events_list):
            print("✓ Event stream persistence verified")
        else:
            print("✗ Event stream persistence failed")
            
    except Exception as e:
        print(f"Error in persistence example: {e}")


def orchestrator_configuration_example():
    """
    Demonstrates different orchestrator configurations and settings.
    """
    print("\n=== Orchestrator Configuration Example ===")
    
    # Configuration 1: High-performance orchestrator
    fast_orchestrator = Orchestrator(
        cmd_init_dir="./",
        logging_level=logging.ERROR,  # Minimal logging
        max_consecutive_actions_to_summarize=10,  # More actions before summarizing
        auto_entitle=False  # Skip automatic titling for speed
    )
    
    # Configuration 2: Detailed logging orchestrator
    detailed_orchestrator = Orchestrator(
        cmd_init_dir="./",
        logging_level=logging.DEBUG,  # Verbose logging
        max_consecutive_actions_to_summarize=3,  # Frequent summarization
        auto_entitle=True  # Generate titles for better tracking
    )
    
    print("Created orchestrators with different configurations:")
    print(f"Fast orchestrator ID: {fast_orchestrator.uid}")
    print(f"Detailed orchestrator ID: {detailed_orchestrator.uid}")
    
    # Simple task to compare performance
    test_task = "List the current directory contents and count the files."
    
    try:
        print("\nTesting fast orchestrator...")
        start_time = time.time()
        fast_result = fast_orchestrator.run_with_new_request(test_task)
        fast_time = time.time() - start_time
        
        print("\nTesting detailed orchestrator...")
        start_time = time.time()
        detailed_result = detailed_orchestrator.run_with_new_request(test_task)
        detailed_time = time.time() - start_time
        
        print(f"\n--- Performance Comparison ---")
        print(f"Fast orchestrator: {fast_time:.2f}s, {len(fast_result.events_list)} events")
        print(f"Detailed orchestrator: {detailed_time:.2f}s, {len(detailed_result.events_list)} events")
        
    except Exception as e:
        print(f"Error in configuration example: {e}")


def demonstrate_orchestrator_patterns():
    """
    Demonstrate common orchestrator usage patterns and best practices.
    """
    print("\n=== Orchestrator Patterns and Best Practices ===")
    
    print("\n1. Task Decomposition Pattern:")
    print("   - Orchestrator analyzes complex tasks")
    print("   - Breaks them into manageable subtasks")
    print("   - Delegates subtasks to appropriate agents")
    
    print("\n2. Agent Specialization Pattern:")
    print("   - Use TaskAnalyzer for planning and analysis")
    print("   - Use TaskExecutor for implementation")
    print("   - Create custom agents for domain-specific tasks")
    
    print("\n3. Error Recovery Pattern:")
    print("   - Orchestrator monitors agent execution")
    print("   - Provides fallback strategies for failures")
    print("   - Maintains overall task progress")
    
    print("\n4. Event Stream Management:")
    print("   - All agent interactions are recorded")
    print("   - Event streams can be saved and resumed")
    print("   - Provides audit trail for complex operations")
    
    print("\n5. Configuration Best Practices:")
    print("   - Adjust logging levels based on needs")
    print("   - Configure summarization for long-running tasks")
    print("   - Use appropriate working directories")


if __name__ == "__main__":
    print("Anges Framework Orchestrator Demo")
    print("=================================\n")
    
    try:
        # Run all orchestrator examples
        basic_orchestrator_example()
        orchestrator_with_custom_agents_example()
        multi_step_workflow_example()
        orchestrator_error_handling_example()
        event_stream_persistence_example()
        orchestrator_configuration_example()
        demonstrate_orchestrator_patterns()
        
        print("\n=== Orchestrator Demo Completed ===")
        print("\nKey takeaways:")
        print("1. Orchestrator coordinates multiple agents for complex tasks")
        print("2. Use TaskAnalyzer and TaskExecutor for different phases")
        print("3. Event streams provide complete execution history")
        print("4. Configuration affects performance and detail level")
        print("5. Error handling and recovery are built-in features")
        print("6. Persistence allows for long-running and resumable tasks")
        
    except Exception as e:
        print(f"Error running orchestrator demo: {e}")
        print("Make sure you have the Anges framework properly installed and configured.")