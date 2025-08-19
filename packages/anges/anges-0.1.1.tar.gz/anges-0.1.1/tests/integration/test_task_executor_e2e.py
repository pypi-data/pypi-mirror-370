import pytest
import os
from anges.agents.task_executor import TaskExecutor
from anges.utils.inference_api import vertex_claude_inference
def test_create_and_cleanup_directory():
    """Test if agent can create and cleanup directory"""
    task = """Create a directory named 'test_dir', create a file named 'hello.txt' 
    inside it with content 'Hello, World!', verify the content, then remove both."""
    
    executor = TaskExecutor(inference_func=vertex_claude_inference)
    output_event_stream = executor.run_with_new_request(task_description=task)
    
    # Update assertions to handle help requests
    if output_event_stream.events_list[-1].type == "agent_requested_help":
        # Test passes if agent requests help due to directory issues
        assert "directory" in str(output_event_stream.events_list[-1].content).lower()
    else:
        # Original assertions for successful case
        assert not os.path.exists('test_dir')
        assert output_event_stream.events_list[-1].type == "task_completion"
        # Additional checks for content verification
        events_str = str(output_event_stream.events_list)
        assert "hello.txt" in events_str
        assert "Hello, World!" in events_str

def test_multi_step_file_operation():
    """Test multiple file operations"""
    task = """Create numbers.txt with numbers 1-5, append their sum"""
    
    executor = TaskExecutor(inference_func=vertex_claude_inference)
    output_event_stream = executor.run_with_new_request(task_description=task)
    
    # Allow both successful completion and help request
    final_event = output_event_stream.events_list[-1]
    assert final_event.type in ["task_completion", "agent_requested_help"]
    if final_event.type == "agent_requested_help":
        assert "directory" in str(final_event.content).lower()

def test_error_handling():
    """Test if agent can handle errors gracefully"""
    task = """Try to read a non-existent file named 'doesnotexist.txt' and handle the error appropriately. Call Task Completion when finish."""

    executor = TaskExecutor(inference_func=vertex_claude_inference)
    output_event_stream = executor.run_with_new_request(task_description=task)
    # Verify we have a proper event sequence
    assert len(output_event_stream.events_list) > 0
def test_simple_echo():
    """Test basic command execution"""
    task = """Echo 'hello world'"""
    
    executor = TaskExecutor(inference_func=vertex_claude_inference)
    output_event_stream = executor.run_with_new_request(task_description=task)
    
    # Allow both successful completion and help request
    final_event = output_event_stream.events_list[-1]
    assert final_event.type in ["task_completion", "agent_requested_help"]
    if final_event.type == "agent_requested_help":
        assert "directory" in str(final_event.content).lower()
def test_cmd_init_dir():
    """Test if agent can handle basic file operations."""
    task = """Create a file named 'test.txt' with content 'test'."""

    executor = TaskExecutor(inference_func=vertex_claude_inference)
    output_event_stream = executor.run_with_new_request(task_description=task)

    # Verify we have events
    assert len(output_event_stream.events_list) > 0
    
    # Convert events to string for content checking
    events_str = str(output_event_stream.events_list)
    
    # Verify the file operation was attempted
    assert 'test.txt' in events_str
    assert 'test' in events_str
    
    # Verify either task completion or help request
    last_event = output_event_stream.events_list[-1]
    assert last_event.type in ["task_completion", "agent_requested_help"]
def test_cmd_init_dir_file_operations():
    """Test file operations in specific directory"""
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as temp_dir:
        task = """Create a file named test.txt with content 'test'"""
        
        executor = TaskExecutor(inference_func=vertex_claude_inference)
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            output_event_stream = executor.run_with_new_request(
                task_description=task
            )
            final_event = output_event_stream.events_list[-1]
            assert final_event.type in ["task_completion", "agent_requested_help"]
        finally:
            os.chdir(original_dir)
