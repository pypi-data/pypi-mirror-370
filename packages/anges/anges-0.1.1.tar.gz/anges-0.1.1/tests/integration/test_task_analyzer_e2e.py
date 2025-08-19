import pytest
import os
from anges.agents.task_analyzer import TaskAnalyzer
from anges.utils.inference_api import vertex_claude_inference

def test_basic_analysis():
    """Test if agent can analyze a simple task"""
    task = """Show the current directory"""

    analyzer = TaskAnalyzer(inference_func=vertex_claude_inference, cmd_init_dir=os.getcwd())
    output_event_stream = analyzer.run_with_new_request(task_description=task)

    # Verify we have a proper event sequence
    assert len(output_event_stream.events_list) >= 2  # At least request and completion
    assert output_event_stream.events_list[0].type == "new_request"
    assert output_event_stream.events_list[-1].type == "task_completion"
    
    # Verify analysis content
    events_str = str(output_event_stream.events_list)
    assert any(cmd in events_str.lower() for cmd in ["pwd", "getcwd"])

def test_help_request_analysis():
    """Test if agent can properly analyze a situation requiring help"""
    task = """Analyze if we have root access."""

    analyzer = TaskAnalyzer(inference_func=vertex_claude_inference)
    output_event_stream = analyzer.run_with_new_request(task_description=task)

    # Verify event sequence
    assert len(output_event_stream.events_list) >= 2
    assert output_event_stream.events_list[0].type == "new_request"
    
    # Either the agent should request help or complete the task
    final_event = output_event_stream.events_list[-1]
    assert final_event.type in ["agent_requested_help", "task_completion"]
    
    # Verify content
    events_str = str(output_event_stream.events_list)
    assert any(word in events_str.lower() for word in ["permission", "sudo", "root"])
